"""Uyuni v3.1: reproducible render/optics pipeline; never regenerates or saves the model.

Run in Blender 5.2, after saving the integrated model to a new .blend:
  blender -b integrated.blend -P render_plan.py -- --mode preflight --out renders
  blender -b integrated.blend -P render_plan.py -- --mode stills --profile draft --out renders
  blender -b integrated.blend -P render_plan.py -- --mode stills --profile final --out renders --compositor optics --exr
  blender -b integrated.blend -P render_plan.py -- --mode drone-test --out renders --compositor optics
  blender -b integrated.blend -P render_plan.py -- --mode drone --out renders --encode --drone-camera CAM_DRON_EQUILIBRADO

Defaults: CAM01..07, CAM02B, plus CAM07 P2; A sign only. Extra approved cameras:
  --extra-camera UYUNI_DIA:CAM_08_LADO_AIRE
Outputs are separated by profile/revision and have a resumable manifest. Change --revision
after any material/light/geometry edit, particularly when running in an unsaved UI session.

The script changes render settings, scene palette properties, Light Group labels and
per-view-layer visibility of the sign. It switches ESTUDIO/DRON shaders in memory;
it preserves palette colors and physical lights,
camera transforms, meshes, assets or keyframes.
It preserves all UY_AUDIT_* objects and checks their coordinates before/after work.
No purge, open_mainfile, save_as_mainfile, remote actions or asset downloads.

Source criteria: TRASPASO 5/8.4/8.5/8.7/10, GUIA_REALISMO_FOTOGRAFICO and
MUESTREO_Y_RENDIMIENTO. Sampling guide supersedes the older 512/.01 still recipe.
RNA/enums were inspected by the parent in work/v031/formal_inventory.json; dynamic enums
are still tested on disposable scene/node data before modifying production scenes.
"""
from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import time


PROFILES = {
    "draft": dict(samples=384, threshold=0.03, clamp=8.0, percent=50),
    "final_day": dict(samples=1024, threshold=0.008, clamp=8.0, percent=100),
    "final_night": dict(samples=1024, threshold=0.005, clamp=10.0, percent=100),
    "drone": dict(samples=512, threshold=0.01, clamp=8.0, percent=100),
    "drone_draft": dict(samples=128, threshold=0.03, clamp=8.0, percent=25),
}
STILLS = [
    ("CAM_01", "UYUNI_DIA", "CAM_01_HERO_LADO_TIERRA"),
    ("CAM_02", "UYUNI_DIA", "CAM_02_DETALLE_ALERO"),
    ("CAM_02B", "UYUNI_DIA", "CAM_02B_DETALLE_CIELO"),
    ("CAM_03", "UYUNI_CREPUSCULO", "CAM_03_CREPUSCULAR_NIEVE"),
    ("CAM_04", "UYUNI_DIA", "CAM_04_AEREA_GENERAL"),
    ("CAM_05", "UYUNI_DIA", "CAM_05_LETRERO_HORIZONTE"),
    ("CAM_06", "UYUNI_DIA", "CAM_06_DETALLE_CELOSIA"),
    ("CAM_07_P1", "UYUNI_DIA", "CAM_07_PROPUESTAS"),
    ("CAM_07_P2", "UYUNI_DIA_P2_SALAR_LITIO", "CAM_07_PROPUESTAS"),
    ("CAM_07B", "UYUNI_DIA", "CAM_07B_CAPTURA_CLIENTE"),
    ("CAM_08", "UYUNI_DIA", "CAM_08_LADO_AIRE"),
    ("CAM_09", "UYUNI_DIA", "CAM_09_MANGA_737"),
    ("CAM_10", "UYUNI_DIA", "CAM_10_PISTA_HORIZONTE"),
]
SEED = 20261004
OPTICS_VERSION = 1


def bpy_module():
    import bpy
    import addon_utils
    if not hasattr(bpy.context.scene, "cycles"):
        addon_utils.enable("cycles", default_set=False, persistent=False)
    return bpy


def enum_set(owner, key, value, report=None):
    """Static RNA lists may omit dynamic engines/OCIO entries. Assignment is authoritative."""
    prop = owner.bl_rna.properties.get(key)
    if prop is None:
        raise RuntimeError(f"Missing RNA property: {owner.bl_rna.identifier}.{key}")
    if prop.type != "ENUM":
        raise RuntimeError(f"Expected ENUM: {owner.bl_rna.identifier}.{key}")
    choices = [e.identifier for e in prop.enum_items]
    try:
        setattr(owner, key, value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Unsupported enum {owner.bl_rna.identifier}.{key}={value!r}; RNA={choices}") from exc
    if getattr(owner, key) != value:
        raise RuntimeError(f"Blender changed requested enum {key}={value!r}")
    if report is not None:
        report[f"{owner.bl_rna.identifier}.{key}"] = dict(requested=value, static_enum=choices, assignment="OK")


def required_set(owner, key, value):
    if owner.bl_rna.properties.get(key) is None:
        raise RuntimeError(f"Missing RNA property: {owner.bl_rna.identifier}.{key}")
    setattr(owner, key, value)


def socket(node, identifier, kind=None, output=False):
    sockets = node.outputs if output else node.inputs
    matches = [s for s in sockets if (s.identifier == identifier or s.name == identifier)
               and (kind is None or s.type == kind)]
    if len(matches) != 1:
        available = [(s.identifier, s.name, s.type) for s in sockets]
        raise RuntimeError(f"Socket {node.bl_idname}/{identifier}/{kind}: {available}")
    return matches[0]


def input_set(node, identifier, value, kind=None):
    s = socket(node, identifier, kind)
    if s.bl_rna.properties.get("default_value") is None:
        raise RuntimeError(f"No default_value on {node.bl_idname}.{identifier}")
    # MENU choices are dynamic in Blender5.2: test on scratch nodes during preflight.
    try:
        s.default_value = value
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Unsupported input {node.bl_idname}.{identifier}={value!r}") from exc
    return s


def make_optics(scene, *, night=False, width=3840, animated=False, probe=False):
    """Own compositor group, with explicit scene reference; preserves previous group by name."""
    bpy = bpy_module()
    name = "UY_RENDERPLAN_RNA_PROBE" if probe else f"UY_RENDERPLAN_OPTICS_{scene.name}"
    existing = bpy.data.node_groups.get(name)
    if existing and not probe:
        if not existing.get("uy_renderplan_owned"):
            raise RuntimeError(f"Compositor name collision: {name}")
        # Reuse only our matching recipe; creating a revised group preserves older groups.
        key = json.dumps([OPTICS_VERSION, night, width, animated])
        if existing.get("recipe") == key:
            for n in existing.nodes:
                if n.bl_idname == "CompositorNodeRLayers":
                    n.scene = scene
            return existing
        name += "_v" + hashlib.sha256(key.encode()).hexdigest()[:8]
        found = bpy.data.node_groups.get(name)
        if found and found.get("uy_renderplan_owned"):
            return found
    ng = bpy.data.node_groups.new(name, "CompositorNodeTree")
    try:
        ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        ng["uy_renderplan_owned"] = True
        ng["recipe"] = json.dumps([OPTICS_VERSION, night, width, animated])
        N, L = ng.nodes, ng.links
        rl = N.new("CompositorNodeRLayers")
        rl.scene = scene                         # Required: avoid rendering the active unrelated scene.
        gl = N.new("CompositorNodeGlare")
        input_set(gl, "Type", "Fog Glow" if night else "Bloom", "MENU")
        for k, v in dict(Threshold=1.5 if night else 1.2, Strength=.08 if night else .12,
                         Size=.5 if night else .55).items():
            input_set(gl, k, v, "VALUE")
        L.new(socket(rl, "Image", "RGBA", True), socket(gl, "Image", "RGBA"))
        ld = N.new("CompositorNodeLensdist")
        input_set(ld, "Distortion", -.008, "VALUE")
        input_set(ld, "Dispersion", .006, "VALUE")
        input_set(ld, "Fit", True, "BOOLEAN")
        L.new(socket(gl, "Image", "RGBA", True), socket(ld, "Image", "RGBA"))
        el = N.new("CompositorNodeEllipseMask")
        input_set(el, "Size", (1.15, 1.15))
        bl = N.new("CompositorNodeBlur")
        px = max(1, round(width / 1280 * 300))
        input_set(bl, "Size", (px, px))
        L.new(socket(el, "Mask", output=True), socket(bl, "Image"))
        vg = N.new("ShaderNodeMix")
        enum_set(vg, "data_type", "RGBA")
        enum_set(vg, "blend_type", "MULTIPLY")
        input_set(vg, "Factor", .30, "VALUE")
        L.new(socket(ld, "Image", output=True), socket(vg, "A", "RGBA"))
        L.new(socket(bl, "Image", output=True), socket(vg, "B", "RGBA"))
        coords = N.new("CompositorNodeImageCoordinates")
        L.new(socket(rl, "Image", output=True), socket(coords, "Image"))
        noise = N.new("ShaderNodeTexWhiteNoise")
        enum_set(noise, "noise_dimensions", "4D" if animated else "2D")
        L.new(socket(coords, "Pixel", output=True), socket(noise, "Vector"))
        if animated:
            driver = socket(noise, "W").driver_add("default_value").driver
            driver.expression = f"frame / 24.0 + {SEED}"
        grain = N.new("ShaderNodeMath")
        enum_set(grain, "operation", "MULTIPLY_ADD")
        L.new(socket(noise, "Value", output=True), grain.inputs[0])
        amp = .002 if night else .006
        grain.inputs[1].default_value, grain.inputs[2].default_value = 2 * amp, -amp
        add = N.new("ShaderNodeMix")
        enum_set(add, "data_type", "RGBA")
        enum_set(add, "blend_type", "ADD")
        input_set(add, "Factor", 1.0, "VALUE")
        L.new(socket(vg, "Result", "RGBA", True), socket(add, "A", "RGBA"))
        L.new(grain.outputs[0], socket(add, "B", "RGBA"))
        L.new(socket(add, "Result", "RGBA", True), N.new("NodeGroupOutput").inputs["Image"])
        return ng
    except Exception:
        bpy.data.node_groups.remove(ng)
        raise


def apply_profile(scene, name, *, device="GPU", denoise=True, animated=False,
                  transparent_bounces=8, motion_blur=False):
    cfg = PROFILES[name]
    r, cy = scene.render, scene.cycles
    enum_set(r, "engine", "CYCLES")
    enum_set(cy, "device", device)
    values = dict(samples=cfg["samples"], use_adaptive_sampling=True,
                  adaptive_threshold=cfg["threshold"], adaptive_min_samples=0,
                  max_bounces=12, diffuse_bounces=6, glossy_bounces=6, transmission_bounces=12,
                  transparent_max_bounces=transparent_bounces, volume_bounces=0,
                  sample_clamp_direct=0.0, sample_clamp_indirect=cfg["clamp"],
                  caustics_reflective=True, caustics_refractive=True, use_light_tree=True,
                  use_guiding=False, use_fast_gi=False, seed=SEED, use_animated_seed=animated,
                  use_denoising=denoise)
    for k, v in values.items():
        required_set(cy, k, v)
    enum_set(cy, "denoiser", "OPENIMAGEDENOISE")
    enum_set(cy, "denoising_input_passes", "RGB_ALBEDO_NORMAL")
    enum_set(cy, "denoising_prefilter", "ACCURATE")
    enum_set(cy, "denoising_quality", "HIGH")
    required_set(r, "filter_size", 1.5)
    required_set(r, "film_transparent", False)
    required_set(r, "dither_intensity", 1.0)
    required_set(r, "use_motion_blur", motion_blur)
    if motion_blur:
        required_set(r, "motion_blur_shutter", .5)
    enum_set(r, "compositor_device", "CPU")  # Avoid headless EGL dependencies; Cycles remains GPU.
    enum_set(r, "compositor_precision", "FULL")
    enum_set(scene.view_settings, "view_transform", "AgX")
    enum_set(scene.view_settings, "look", "AgX - Medium High Contrast")
    for vl in scene.view_layers:
        required_set(vl.cycles, "denoising_store_passes", True)
    return dict(profile=name, **cfg, device=device, denoise=denoise, animated_seed=animated,
                seed=SEED, transparent_bounces=transparent_bounces, motion_blur=motion_blur,
                bounces=[12, 6, 6, 12], denoiser="OPENIMAGEDENOISE", prefilter="ACCURATE",
                denoising_quality="HIGH", filter=1.5)


def set_image(scene, fmt="PNG"):
    settings = scene.render.image_settings
    enum_set(settings, "media_type", "MULTI_LAYER_IMAGE" if fmt == "OPEN_EXR_MULTILAYER" else "IMAGE")
    enum_set(settings, "file_format", fmt)
    enum_set(settings, "color_mode", "RGBA" if fmt == "OPEN_EXR_MULTILAYER" else "RGB")
    if fmt != "JPEG":
        enum_set(settings, "color_depth", "16")
    if fmt == "OPEN_EXR_MULTILAYER":
        enum_set(settings, "exr_codec", "ZIP")
    if fmt == "JPEG":
        required_set(settings, "quality", 95)


def audit_signature():
    bpy = bpy_module()
    out = {}
    for ob in bpy.data.objects:
        if not ob.name.startswith("UY_AUDIT_"):
            continue
        digest = hashlib.sha256()
        for row in ob.matrix_world:
            digest.update(struct.pack("4d", *row))
        if ob.type == "MESH":
            vertices = array("f", [0.0]) * (3 * len(ob.data.vertices))
            ob.data.vertices.foreach_get("co", vertices)
            digest.update(vertices.tobytes())
            connectivity = array("i", [0]) * len(ob.data.loops)
            ob.data.loops.foreach_get("vertex_index", connectivity)
            digest.update(connectivity.tobytes())
            digest.update(str((len(ob.data.polygons), len(ob.data.loops))).encode())
        out[ob.name] = dict(type=ob.type, data=ob.data.name if ob.data else None,
                            hash=digest.hexdigest(), collections=sorted(c.name for c in ob.users_collection))
    return out


def preflight(out=None, expected_audit_count=None):
    bpy = bpy_module()
    report = dict(version=bpy.app.version_string, checked_enums={}, profiles={}, compositor=[],
                  audit_count=len(audit_signature()))
    if expected_audit_count is not None and report["audit_count"] != expected_audit_count:
        raise RuntimeError(f"Expected {expected_audit_count} audited objects, found {report['audit_count']}")
    scratch = bpy.data.scenes.new("UY_RENDERPLAN_RNA_PROBE")
    groups = []
    try:
        # Dynamic engine, OCIO and menu enums are assigned only on disposable datablocks.
        for name in PROFILES:
            report["profiles"][name] = apply_profile(scratch, name, animated=name.startswith("drone"),
                                                    motion_blur=name.startswith("drone"))
        enum_set(scratch.view_settings, "view_transform", "False Color", report["checked_enums"])
        for fmt in ("PNG", "JPEG", "OPEN_EXR_MULTILAYER"):
            set_image(scratch, fmt)
        enum_set(scratch.render.image_settings, "media_type", "VIDEO", report["checked_enums"])
        enum_set(scratch.render.image_settings, "file_format", "FFMPEG", report["checked_enums"])
        for key, value in dict(format="MPEG4", codec="H264", constant_rate_factor="HIGH",
                               ffmpeg_preset="GOOD").items():
            enum_set(scratch.render.ffmpeg, key, value, report["checked_enums"])
        for night, animated in ((False, False), (True, False), (False, True)):
            ng = make_optics(scratch, night=night, animated=animated, probe=True)
            groups.append(ng)
            report["compositor"].append(dict(night=night, animated=animated,
                                            nodes=[n.bl_idname for n in ng.nodes]))
        for vl in scratch.view_layers:
            for prop in ("use_pass_mist", "use_pass_ambient_occlusion", "use_pass_cryptomatte_object",
                         "use_pass_cryptomatte_material"):
                required_set(vl, prop, True)
            vl.lightgroups.add(name="UY_TEST")
        # Sequencer API required only for the no-external-ffmpeg encoding fallback.
        seq = scratch.sequence_editor_create()
        strips = getattr(seq, "strips", None)
        if strips is None:
            strips = getattr(seq, "sequences", None)
        report["sequencer_images_available"] = strips is not None and hasattr(strips, "new_image")
        report["status"] = "RNA assignments OK; no render has been performed"
    finally:
        bpy.data.scenes.remove(scratch)
        for ng in groups:
            if ng.name in bpy.data.node_groups:
                bpy.data.node_groups.remove(ng)
    if out:
        atomic_json(Path(out), report)
    return report


def select_device(allow_cpu=False, preferred="AUTO"):
    bpy = bpy_module()
    prefs = bpy.context.preferences.addons["cycles"].preferences
    candidates = [preferred] if preferred != "AUTO" else ["OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"]
    errors = []
    for backend in candidates:
        try:
            enum_set(prefs, "compute_device_type", backend)
            prefs.get_devices()
            devices = [d for d in prefs.devices if d.type == backend]
            if not devices:
                continue
            for d in prefs.devices:
                d.use = d.type == backend
            return "GPU", dict(backend=backend, devices=[d.name for d in devices])
        except (RuntimeError, TypeError, ValueError) as exc:
            errors.append(str(exc))
    if allow_cpu:
        return "CPU", dict(backend="CPU", devices=[], gpu_errors=errors)
    raise RuntimeError("No GPU backend available; refusing silent CPU render. " + " | ".join(errors))


def find_layer(layer, name):
    if layer.name == name:
        return layer
    return next((found for child in layer.children if (found := find_layer(child, name))), None)


def sign_A(scene):
    for vl in scene.view_layers:
        vl.update()
        for name, excluded in (("LETRERO_A_SOBRESALE", False), ("LETRERO_B_CONTENIDO", True)):
            lc = find_layer(vl.layer_collection, name)
            if lc is None:
                raise RuntimeError(f"Missing sign collection {name} in {scene.name}/{vl.name}")
            lc.exclude = excluded


def pass_settings(scene, enabled=False):
    if not enabled:
        return
    for vl in scene.view_layers:
        for key in ("use_pass_mist", "use_pass_ambient_occlusion", "use_pass_cryptomatte_object",
                    "use_pass_cryptomatte_material"):
            required_set(vl, key, True)
        required_set(vl.cycles, "denoising_store_passes", True)
        if "CREPUSCULO" in scene.name:
            for name in ("CIELO", "INTERIOR", "ALERO", "LETRERO", "CELOSIAS"):
                if vl.lightgroups.get(name) is None:
                    vl.lightgroups.add(name=name)
    if "CREPUSCULO" not in scene.name:
        return
    if scene.world and not scene.world.lightgroup:
        scene.world.lightgroup = "CIELO"
    # Group labels do not change light intensity/color. Preserve explicit client assignments.
    for ob in scene.objects:
        if ob.lightgroup:
            continue
        name = ob.name.upper()
        group = None
        if ob.type == "LIGHT":
            if ob.data.type == "SUN":
                group = "CIELO"
            elif "CELOSIA" in name or "UPLIGHT" in name or "BANADOR" in name:
                group = "CELOSIAS"
            elif "LETRERO" in name:
                group = "LETRERO"
            elif "ALERO" in name:
                group = "ALERO"
            elif "INTERIOR" in name:
                group = "INTERIOR"
        elif ob.type == "MESH":
            if "LETRERO" in name:
                group = "LETRERO"
            elif "LUMINARIA" in name and "ALERO" in name:
                group = "ALERO"
            elif "INTERIOR_LUZ" in name:
                group = "INTERIOR"
        if group:
            ob.lightgroup = group


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def source_info():
    bpy = bpy_module()
    path = Path(bpy.data.filepath) if bpy.data.filepath else None
    return dict(file=str(path) if path else None,
                bytes=path.stat().st_size if path and path.is_file() else None,
                mtime=path.stat().st_mtime_ns if path and path.is_file() else None,
                blender=bpy.app.version_string)


def job_spec(scene, camera, cfg, args, job_id, frame):
    return dict(source=source_info(), revision=args.revision, job_id=job_id, scene=scene.name,
                camera=camera.name, frame=frame, settings=cfg, optics=args.compositor,
                optics_version=OPTICS_VERSION, size=[scene.render.resolution_x, scene.render.resolution_y,
                                                   scene.render.resolution_percentage],
                exposure=scene.view_settings.exposure, sign="A", palette=dict(propuesta=scene.get("propuesta"),
                letras_corten=scene.get("letras_corten"), letras_gris=scene.get("letras_gris")),
                camera_matrix=[list(row) for row in camera.matrix_world], lens=camera.data.lens,
                shift=[camera.data.shift_x, camera.data.shift_y],
                light_groups={vl.name: [g.name for g in vl.lightgroups] for vl in scene.view_layers},
                audit=audit_signature())


def read_manifest(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else dict(version=1, jobs={})


def measured_render(scene, stem, spec, manifest, manifest_path, *, exr=False, jpeg=True, resume=True):
    bpy = bpy_module()
    outputs = [stem.with_suffix(".png")]
    if exr:
        outputs.append(stem.with_suffix(".exr"))
    if jpeg:
        outputs.append(stem.with_suffix(".jpg"))
    key, fingerprint = str(stem), digest(spec)
    prev = manifest["jobs"].get(key)
    if resume and prev and prev.get("fingerprint") == fingerprint and all(p.is_file() and p.stat().st_size for p in outputs):
        print(f"[UY_RENDER] resume: {stem.name}", flush=True)
        return prev
    stem.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(stem.with_suffix(".exr" if exr else ".png"))
    set_image(scene, "OPEN_EXR_MULTILAYER" if exr else "PNG")
    stats = []
    def capture(*parts):
        stats.append((time.perf_counter(), " ".join(str(p) for p in parts)))
    bpy.app.handlers.render_stats.append(capture)
    start = time.perf_counter()
    try:
        bpy.ops.render.render(write_still=True, scene=scene.name)
    finally:
        bpy.app.handlers.render_stats.remove(capture)
    elapsed = time.perf_counter() - start
    result = bpy.data.images.get("Render Result")
    if result is None:
        raise RuntimeError("Render Result missing after render")
    if exr:
        set_image(scene, "PNG")
        result.save_render(filepath=str(stem.with_suffix(".png")), scene=scene)
    if jpeg:
        set_image(scene, "JPEG")
        result.save_render(filepath=str(stem.with_suffix(".jpg")), scene=scene)
    first_sample = next((t for t, line in stats if re.search(r"Sample \d+/\d+", line)), None)
    mem = [float(m) for _, line in stats for m in re.findall(r"Mem:\s*([\d.]+)M", line)]
    row = dict(spec=spec, fingerprint=fingerprint, seconds=elapsed,
               preparation_seconds=first_sample - start if first_sample else None,
               cycles_peak_mb=max(mem) if mem else None, outputs=[str(p) for p in outputs])
    manifest["jobs"][key] = row
    atomic_json(manifest_path, manifest)
    print(f"[UY_RENDER] {stem.name}: {elapsed:.1f}s", flush=True)
    return row


def prepare_scene(scene, camera, cfg_name, args, device, *, animated=False, denoise=True):
    bpy = bpy_module()
    if camera.name not in scene.objects:
        raise RuntimeError(f"Camera {camera.name} is not linked to {scene.name}")
    if bpy.context.window:
        bpy.context.window.scene = scene
    scene.camera = camera
    sign_A(scene)
    if scene.name == "UYUNI_DIA_P2_SALAR_LITIO":
        scene["propuesta"], scene["letras_corten"], scene["letras_gris"] = 1, 0, 1
    elif scene.name == "UYUNI_DIA":
        scene["propuesta"], scene["letras_corten"], scene["letras_gris"] = 0, 1, 0
    cfg = apply_profile(scene, cfg_name, device=device, denoise=denoise, animated=animated,
                        transparent_bounces=args.transparent_bounces, motion_blur=animated)
    scene.render.resolution_x, scene.render.resolution_y = (1920, 1080) if animated else (3840, 2160)
    scene.render.resolution_percentage = cfg["percent"]
    if args.exposure is not None:
        scene.view_settings.exposure = args.exposure
    if args.compositor == "off":
        scene.compositing_node_group = None
    elif args.compositor == "optics":
        if scene.compositing_node_group and not scene.get("UY_RENDERPLAN_previous_compositor"):
            scene["UY_RENDERPLAN_previous_compositor"] = scene.compositing_node_group.name
        width = round(scene.render.resolution_x * scene.render.resolution_percentage / 100)
        scene.compositing_node_group = make_optics(scene, night="CREPUSCULO" in scene.name,
                                                 width=width, animated=animated)
    pass_settings(scene, enabled=args.exr)
    return cfg


def render_stills(args, device, device_info):
    bpy = bpy_module()
    from continuacion import materiales
    materiales.aplicar({"profile":"ESTUDIO" if args.profile=="final" else "DRON"})
    jobs = list(STILLS)
    for extra in args.extra_camera:
        name, camera = extra.split(":", 1)
        jobs.append((camera, name, camera))
    if args.only:
        selected = set(args.only.split(","))
        missing = selected - {j[0] for j in jobs}
        if missing:
            raise RuntimeError(f"Unknown jobs: {sorted(missing)}")
        jobs = [j for j in jobs if j[0] in selected]
    # Validate all jobs before starting an expensive batch.
    for _, scene, camera in jobs:
        if scene not in bpy.data.scenes or camera not in bpy.data.objects:
            raise RuntimeError(f"Missing job input: {scene}/{camera}")
    directory = Path(args.out) / args.revision / args.profile / "stills"
    path = directory / "manifest.json"
    manifest = read_manifest(path)
    for job_id, scene_name, camera_name in jobs:
        scene, camera = bpy.data.scenes[scene_name], bpy.data.objects[camera_name]
        profile = "draft" if args.profile == "draft" else ("final_night" if "CREPUSCULO" in scene_name else "final_day")
        cfg = prepare_scene(scene, camera, profile, args, device)
        if "CREPUSCULO" in scene_name:
            scene.cycles.sample_clamp_indirect = 10.0
            cfg["clamp"] = 10.0
        frame = scene.frame_current
        spec = job_spec(scene, camera, cfg, args, job_id, frame)
        spec["hardware"] = device_info
        measured_render(scene, directory / job_id, spec, manifest, path,
                        exr=args.exr, resume=not args.force)
        if args.diagnostics:
            old_transform, old_group = scene.view_settings.view_transform, scene.compositing_node_group
            old_resolution = (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage)
            try:
                enum_set(scene.view_settings, "view_transform", "False Color")
                scene.compositing_node_group = None
                scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 960, 540, 100
                ds = dict(spec, diagnostic="False Color without compositor", size=[960, 540, 100])
                measured_render(scene, directory / (job_id + "_FALSE_COLOR"), ds, manifest, path,
                                exr=False, resume=not args.force)
            finally:
                enum_set(scene.view_settings, "view_transform", old_transform)
                scene.compositing_node_group = old_group
                scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = old_resolution
    return dict(manifest=str(path), jobs=len(jobs))


def render_drone(args, device, device_info, test=False):
    bpy = bpy_module()
    from continuacion import materiales
    materiales.aplicar({"profile": "DRON"})
    scene, camera = bpy.data.scenes["UYUNI_DIA"], bpy.data.objects[args.drone_camera]
    if camera.animation_data is None and not camera.constraints:
        raise RuntimeError(f"{camera.name} has neither animation nor constraints")
    start = args.frame_start if args.frame_start is not None else (300 if test else 1)
    end = args.frame_end if args.frame_end is not None else (start + 47 if test else 600)
    if start < 1 or end > 600 or end < start:
        raise RuntimeError("Drone range must stay within the existing 1..600 path")
    profile = "drone_draft" if args.profile == "draft" else "drone"
    denoisers = [True, False] if test else [not args.no_denoise]
    outputs = []
    for denoise in denoisers:
        tag = "OIDN" if denoise else "RAW"
        directory = Path(args.out) / args.revision / args.profile / ("drone_test" if test else "drone") / tag
        path = directory / "manifest.json"
        manifest = read_manifest(path)
        cfg = prepare_scene(scene, camera, profile, args, device, animated=True, denoise=denoise)
        scene.frame_start, scene.frame_end = start, end
        scene.render.fps, scene.render.fps_base = 24, 1.0
        for frame in range(start, end + 1):
            scene.frame_set(frame)
            spec = job_spec(scene, camera, cfg, args, f"CAM_DRON_{tag}", frame)
            spec["hardware"] = device_info
            measured_render(scene, directory / f"CAM_DRON_{frame:04d}", spec, manifest, path,
                            exr=False, jpeg=False, resume=not args.force)
        outputs.append(dict(directory=str(directory), manifest=str(path), start=start, end=end,
                            width=round(scene.render.resolution_x * cfg["percent"] / 100),
                            height=round(scene.render.resolution_y * cfg["percent"] / 100), denoise=denoise))
        if args.encode:
            encode_sequence(directory, start, end, args.ffmpeg, overwrite=args.force)
    return outputs


def encode_sequence(directory, start, end, ffmpeg=None, overwrite=False):
    """PNG→H.264. External ffmpeg preferred; Blender VSE is a local dependency-free fallback."""
    directory = Path(directory).resolve()
    images = [directory / f"CAM_DRON_{f:04d}.png" for f in range(start, end + 1)]
    missing = [str(p) for p in images if not p.is_file() or not p.stat().st_size]
    if missing:
        raise RuntimeError(f"Incomplete sequence: {missing[:5]}")
    destination = directory / f"dron_uyuni_{start:04d}_{end:04d}.mp4"
    if destination.exists() and not overwrite:
        raise RuntimeError(f"Video already exists; use --force to replace: {destination}")
    executable = ffmpeg or shutil.which("ffmpeg")
    if executable:
        command = [str(executable), "-y" if overwrite else "-n", "-framerate", "24", "-start_number", str(start),
                   "-i", str(directory / "CAM_DRON_%04d.png"), "-frames:v", str(len(images)),
                   "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-movflags", "+faststart", str(destination)]
        subprocess.run(command, check=True, shell=False,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0)
        method = "ffmpeg/libx264/crf18/yuv420p"
    else:
        bpy = bpy_module()
        scene = bpy.data.scenes.new("UY_RENDERPLAN_ENCODE_ONLY")
        try:
            editor = scene.sequence_editor_create()
            strips = getattr(editor, "strips", None)
            if strips is None:
                strips = getattr(editor, "sequences", None)
            if strips is None or not hasattr(strips, "new_image"):
                raise RuntimeError("No VSE image-strip API. Supply --ffmpeg /absolute/path/ffmpeg.exe")
            strip = strips.new_image("UY_DRONE_PNG_SEQUENCE", filepath=str(images[0]), channel=1, frame_start=1)
            for p in images[1:]:
                strip.elements.append(p.name)
            strip.frame_final_duration = len(images)
            # Input PNGs already contain AgX. Standard/sRGB prevents a second AgX transform.
            enum_set(scene.view_settings, "view_transform", "Standard")
            enum_set(scene.view_settings, "look", "None")
            scene.view_settings.exposure, scene.view_settings.gamma = 0.0, 1.0
            enum_set(scene.sequencer_colorspace_settings, "name", "sRGB")
            size = bpy.data.images.load(str(images[0]), check_existing=False)
            try:
                scene.render.resolution_x, scene.render.resolution_y = size.size[:]
            finally:
                bpy.data.images.remove(size)
            scene.render.resolution_percentage = 100
            scene.render.fps, scene.render.fps_base = 24, 1.0
            scene.frame_start, scene.frame_end = 1, len(images)
            required_set(scene.render, "use_sequencer", True)
            enum_set(scene.render, "compositor_device", "CPU")
            enum_set(scene.render, "engine", "CYCLES")
            enum_set(scene.cycles, "device", "CPU")
            enum_set(scene.render.image_settings, "media_type", "VIDEO")
            enum_set(scene.render.image_settings, "file_format", "FFMPEG")
            for key, value in dict(format="MPEG4", codec="H264", constant_rate_factor="HIGH",
                                   ffmpeg_preset="GOOD").items():
                enum_set(scene.render.ffmpeg, key, value)
            scene.render.filepath = str(destination)
            bpy.ops.render.render(animation=True, scene=scene.name)
            method = "BlenderVSE/MPEG4/H264/HIGH/GOOD"
        finally:
            bpy.data.scenes.remove(scene)
    if not destination.is_file() or not destination.stat().st_size:
        raise RuntimeError(f"Encoder did not produce {destination}")
    atomic_json(destination.with_suffix(".json"), dict(source=str(directory), frames=len(images),
                 start=start, end=end, fps=24, duration_seconds=len(images)/24, method=method,
                 output=str(destination)))
    return str(destination)


def parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mode", choices=["preflight", "configure", "stills", "drone-test", "drone", "encode"], default="preflight")
    p.add_argument("--profile", choices=["draft", "final"], default="final")
    p.add_argument("--out", required=True)
    p.add_argument("--revision", default="codex_acf7f58")
    p.add_argument("--compositor", choices=["keep", "off", "optics"], default="keep")
    p.add_argument("--only", help="Comma-separated job IDs, e.g. CAM_07_P1,CAM_07_P2")
    p.add_argument("--extra-camera", action="append", default=[], metavar="SCENE:CAMERA")
    p.add_argument("--exr", action="store_true", help="Half-float multilayer EXR plus PNG16 and JPG")
    p.add_argument("--diagnostics", action="store_true", help="Additional 960px False Color without optics")
    p.add_argument("--exposure", type=float, help="Explicit override only; default preserves measured exposure")
    p.add_argument("--transparent-bounces", type=int, choices=[8,16,32], default=8)
    p.add_argument("--backend", choices=["AUTO","OPTIX","CUDA","HIP","METAL","ONEAPI"], default="AUTO")
    p.add_argument("--allow-cpu", action="store_true")
    p.add_argument("--expected-audit-count", type=int, help="Use 42 on the integrated continuation model")
    p.add_argument("--frame-start", type=int)
    p.add_argument("--frame-end", type=int)
    p.add_argument("--drone-camera", default="CAM_DRON", help="Alternative camera; original keyframes remain untouched")
    p.add_argument("--no-denoise", action="store_true", help="Drone only; test mode always produces both variants")
    p.add_argument("--encode", action="store_true", help="Encode the completed drone sequence")
    p.add_argument("--ffmpeg", help="Optional ffmpeg executable; otherwise PATH or local BlenderVSE encoder")
    p.add_argument("--force", action="store_true", help="Rerender completed jobs / replace matching MP4")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    args.out = str(Path(args.out).resolve())
    if args.mode == "encode":
        if args.frame_start is None or args.frame_end is None:
            raise RuntimeError("encode needs --out SEQUENCE_DIRECTORY --frame-start N --frame-end N")
        print(encode_sequence(args.out, args.frame_start, args.frame_end, args.ffmpeg, args.force))
        return
    baseline = audit_signature()
    output = Path(args.out) / args.revision
    try:
        report = preflight(output / "rna_preflight.json", args.expected_audit_count)
        if args.mode == "preflight":
            print(json.dumps(report, ensure_ascii=False))
            return
        device, hardware = select_device(args.allow_cpu, args.backend)
        if args.mode == "stills":
            result = render_stills(args, device, hardware)
        elif args.mode in ("drone-test", "drone"):
            result = render_drone(args, device, hardware, test=args.mode == "drone-test")
        else:
            bpy = bpy_module()
            result = {}
            for name in ["UYUNI_DIA", "UYUNI_DIA_P2_SALAR_LITIO", "UYUNI_CREPUSCULO"]:
                scene = bpy.data.scenes[name]
                profile = "draft" if args.profile == "draft" else ("final_night" if "CREPUSCULO" in name else "final_day")
                result[name] = prepare_scene(scene, scene.camera, profile, args, device)
        atomic_json(output / (args.mode + "_summary.json"), dict(mode=args.mode, hardware=hardware, result=result))
        print(json.dumps(dict(mode=args.mode, hardware=hardware, result=result), ensure_ascii=False))
    finally:
        if audit_signature() != baseline:
            raise RuntimeError("Audited CAD geometry/collection membership changed during render pipeline")


if __name__ == "__main__":
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    main(arguments)
