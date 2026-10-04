"""Cámaras, luz y óptica v031. Importar y llamar aplicar(); no abre/guarda/renderiza.

La animación CAM_DRON y las cámaras inclinadas de detalle conservan sus datos.
Todos los ajustes parten de baselines guardadas o de valores absolutos.
El método del letrero nocturno empieza en legacy; halo/bañadores son alternativas
de luces independientes, desactivadas por defecto. Nunca cambia su material.
"""
import contextlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

OWNER = "uyuni_v031_camaras_20261004"
DEFAULTS = {
    "straighten": True,
    "camera_night_height": None,          # conservar 1,70 m actual; opcional 1,50 m
    "create_air_camera": False,         # CAM_08, CAM_09 y CAM_10 ya están en la fuente actual
    "air_camera_position": (92.0, 99.0, 6.0),
    "air_camera_target": (42.0, 45.0, 5.0),
    "air_camera_lens": 28.0,
    "day_calibration": True,
    "day_sun_energy": 2.7,               # guía: original 4,5 × 0,6; orientación intacta
    "day_world_strength": .108,         # guía: original 0,18 × 0,6
    "night_practical_kelvin": True,
    "night_spot_factor": 1.6,            # siempre sobre energía base capturada
    "night_interior_attribute": .25,
    "night_exposure": 1.1,               # candidato de prueba; falta validar False Color
    "interior_area_lights": True,
    "interior_area_energy": 1000.0,
    "interior_rows_y": (3.2, 6.8),
    "interior_light_z": 6.5,
    "interior_kelvin": 3500.0,
    "night_sign_method": "legacy",       # legacy / halo / wash; nunca cambia el color
    "night_sign_kelvin": 4000.0,
    "night_sign_energy": 18.0,
    "lightgroups": True,
    "compositor": False,               # la óptica se configura con render_plan.make_optics
    "day_optics": True,
    "render_quality": "DRAFT",          # DRAFT / FINAL; no cambio de CPU/GPU
    "grain_day": .006,
    "grain_night": .002,
    "lens_distortion": -.008,
    "lens_dispersion": .006,
}
STRAIGHTEN = ("CAM_01_HERO_LADO_TIERRA", "CAM_03_CREPUSCULAR_NIEVE",
              "CAM_05_LETRERO_HORIZONTE", "CAM_06_DETALLE_CELOSIA")
AXES = (0.0, 4.8, 9.6, 14.4, 19.2, 24.0, 28.8, 33.6, 38.4, 43.2,
        48.0, 48.5, 53.23, 58.03, 62.83, 67.63, 72.36, 72.81, 77.66, 82.51)
GROUPS = ("CIELO", "INTERIOR", "ALERO", "LETRERO", "UPLIGHTS")


def enum_set(ob, prop, value):
    p = ob.bl_rna.properties.get(prop)
    if p is None:
        raise RuntimeError(f"RNA ausente: {type(ob).__name__}.{prop}")
    # Los enums dinámicos (Cycles/OIDN) no aparecen en enum_items estático.
    # La asignación de RNA valida la opción realmente disponible.
    setattr(ob, prop, value)


def plain(value):
    try: return list(value)
    except TypeError: return value


def baseline(ob, key, value):
    prop = "UY_V031_BASE_" + key
    if prop not in ob: ob[prop] = json.dumps(value)
    return json.loads(ob[prop])


def snapshot(scene):
    world = scene.world
    return {
        "camera": scene.camera.name if scene.camera else None,
        "exposure": scene.view_settings.exposure,
        "view_transform": scene.view_settings.view_transform,
        "look": scene.view_settings.look,
        "props": {k: scene.get(k) for k in ("propuesta", "letras_corten", "letras_gris", "luz_interior", "luz_alero", "luz_letrero")},
        "world": world.name if world else None,
        "world_backgrounds": {n.name: n.inputs["Strength"].default_value for n in world.node_tree.nodes if n.type == "BACKGROUND"} if world and world.use_nodes else {},
        "compositor": scene.compositing_node_group.name if hasattr(scene, "compositing_node_group") and scene.compositing_node_group else None,
        "lights": {ob.name: {"energy": ob.data.energy, "color": list(ob.data.color), "temperature": getattr(ob.data, "temperature", None),
                              "use_temperature": getattr(ob.data, "use_temperature", None)} for ob in scene.objects if ob.type == "LIGHT"},
        "cycles": {key: getattr(scene.cycles, key, None) for key in ("samples", "adaptive_threshold", "sample_clamp_indirect", "use_light_tree", "denoiser")},
    }


def straighten_camera(cam, height=None):
    if cam.type != "CAMERA" or cam.data.type != "PERSP":
        raise RuntimeError(f"Cámara incompatible: {cam.name}")
    if cam.animation_data and cam.animation_data.action:
        raise RuntimeError(f"No modificar cámara animada: {cam.name}")
    base = baseline(cam, "CAMERA", {"matrix": [list(row) for row in cam.matrix_world],
                                    "lens": cam.data.lens, "sensor_width": cam.data.sensor_width,
                                    "shift_x": cam.data.shift_x, "shift_y": cam.data.shift_y,
                                    "sensor_fit": cam.data.sensor_fit})
    old = Matrix(base["matrix"])
    forward = old.to_quaternion() @ Vector((0, 0, -1))
    horizontal = Vector((forward.x, forward.y, 0))
    if horizontal.length < 1e-6: raise RuntimeError("Cámara casi cenital: no enderezar")
    pitch = math.asin(max(-1, min(1, forward.z)))
    cam.matrix_world = old
    cam.rotation_euler = horizontal.normalized().to_track_quat("-Z", "Y").to_euler()
    if height is not None: cam.location.z = height
    # Regla probada en las herramientas aportadas para sensor horizontal 36 mm.
    cam.data.shift_x = base["shift_x"]
    cam.data.shift_y = base["shift_y"] + math.tan(pitch) * base["lens"] / base["sensor_width"]
    cam["UY_V031_PITCH_BASE_DEG"] = math.degrees(pitch)
    cam["UY_V031_VERTICALS"] = True
    return {"before": base, "after": {"matrix": [list(row) for row in cam.matrix_world],
            "shift_y": cam.data.shift_y, "height": cam.location.z}, "pitch_degrees": math.degrees(pitch)}


def owned_collection(name, parent):
    col = bpy.data.collections.get(name)
    if col:
        if col.get("UY_OWNER") != OWNER: raise RuntimeError(f"Colección ajena: {name}")
    else:
        col = bpy.data.collections.new(name); col["UY_OWNER"] = OWNER
    if col.name not in parent.children: parent.children.link(col)
    return col


def owned_object(name, datatype, col):
    ob = bpy.data.objects.get(name)
    if ob:
        if ob.get("UY_OWNER") != OWNER or ob.type != datatype:
            raise RuntimeError(f"Objeto ajeno o incompatible: {name}")
    else:
        data = bpy.data.cameras.new(name) if datatype == "CAMERA" else bpy.data.lights.new(name, "AREA")
        ob = bpy.data.objects.new(name, data); ob["UY_OWNER"] = OWNER
    if ob.name not in col.objects: col.objects.link(ob)
    return ob


def build_air_camera(cfg, scenes):
    col = owned_collection("08_V031_CAMARAS", scenes[0].collection)
    for scene in scenes[1:]:
        if col.name not in scene.collection.children: scene.collection.children.link(col)
    cam = owned_object("CAM_V031_LADO_AIRE_GENERAL", "CAMERA", col)
    cam.location = cfg["air_camera_position"]
    cam.data.lens = cfg["air_camera_lens"]; cam.data.sensor_width = 36
    direction = Vector(cfg["air_camera_target"]) - cam.location
    cam.rotation_euler = Vector((direction.x, direction.y, 0)).normalized().to_track_quat("-Z", "Y").to_euler()
    cam.data.shift_y = direction.z / math.hypot(direction.x, direction.y) * cam.data.lens / cam.data.sensor_width
    cam.data.clip_start = .1; cam.data.clip_end = 60000
    cam.data.dof.use_dof = False
    return cam.name


def kelvin_light(data, kelvin):
    if not hasattr(data, "use_temperature") or not hasattr(data, "temperature"):
        raise RuntimeError("La versión no ofrece temperatura de luces; no se usa una aproximación RGB")
    data.use_temperature = True; data.temperature = kelvin; data.color = (1, 1, 1)


def emission_kelvin_preserve(mat, kelvin):
    """No vuelve a compensar un Blackbody ya instalado por el integrador del 4/10."""
    nt = mat.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    color, strength = b.inputs["Emission Color"], b.inputs["Emission Strength"]
    if color.is_linked and color.links[0].from_node.type == "BLACKBODY":
        color.links[0].from_node.inputs["Temperature"].default_value = kelvin
        return {"existing_blackbody": True, "kelvin": kelvin, "strength_compensation_added": False}
    if color.is_linked:
        raise RuntimeError(f"Emisión de color procedural desconocida: {mat.name}")
    old = tuple(color.default_value)
    luminance = .2126 * old[0] + .7152 * old[1] + .0722 * old[2]
    bb = nt.nodes.new("ShaderNodeBlackbody"); bb.name = "UY_V031_BLACKBODY"
    bb.inputs["Temperature"].default_value = kelvin
    nt.links.new(bb.outputs["Color"], color)
    if strength.is_linked:
        source = strength.links[0].from_socket
        mult = nt.nodes.new("ShaderNodeMath"); enum_set(mult, "operation", "MULTIPLY")
        nt.links.new(source, mult.inputs[0]); mult.inputs[1].default_value = luminance
        nt.links.new(mult.outputs[0], strength)
    else:
        strength.default_value *= luminance
    mat["UY_V031_KELVIN_BASE_COLOR"] = json.dumps(old)
    return {"existing_blackbody": False, "kelvin": kelvin, "strength_factor": luminance}


def area_grid(scene, cfg):
    col = owned_collection("08_V031_INTERIOR_NOCHE", scene.collection)
    # Se iluminan los vanos bajo el bloque principal; intervalos de 0,5 m son juntas.
    centers = [(a + b) / 2 for a, b in zip(AXES, AXES[1:]) if b - a > 1.0 and (a + b) / 2 < 72.36]
    desired = set()
    for row, y in enumerate(cfg["interior_rows_y"], 1):
        for index, x in enumerate(centers, 1):
            name = f"UY_V031_AREA_INTERIOR_{row}_{index:02d}"; desired.add(name)
            ob = owned_object(name, "LIGHT", col)
            enum_set(ob.data, "type", "AREA"); enum_set(ob.data, "shape", "RECTANGLE")
            ob.data.size, ob.data.size_y = 1.2, .6
            ob.data.energy = cfg["interior_area_energy"]; ob.data.spread = math.radians(110)
            kelvin_light(ob.data, cfg["interior_kelvin"])
            ob.location = (x, y, cfg["interior_light_z"]); ob.rotation_euler = (0, 0, 0)
            ob.lightgroup = "INTERIOR"
            ob.hide_render = False
    for ob in list(col.objects):
        if ob.get("UY_OWNER") == OWNER and ob.name not in desired:
            ob.hide_render = True
    return sorted(desired)


def sign_candidates(scene, cfg):
    method = cfg["night_sign_method"]
    if method not in {"legacy", "halo", "wash"}: raise ValueError("night_sign_method: legacy/halo/wash")
    col = owned_collection("08_V031_LETRERO_NOCHE", scene.collection)
    # Se trabaja con luces invisibles al render; no se añaden meshes ni se cambian letras.
    # Esquemas provisionales para comparar. La retirada actual se consulta del bounds.
    signs = [ob for ob in scene.objects if ob.type == "MESH" and "LETRAS" in ob.name.upper()
             and "LETRERO" in " ".join(c.name.upper() for c in ob.users_collection)]
    if signs:
        pts = [ob.matrix_world @ Vector(corner) for ob in signs for corner in ob.bound_box]
        x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
        y_front, y_back = min(p.y for p in pts), max(p.y for p in pts)
        z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
    else:
        x0, x1, y_front, y_back, z0, z1 = 52.0, 58.0, -1.9, -1.752, 7.764, 9.264
    desired = set()
    if method == "halo":
        centers = [x0 + (i + .5) * (x1 - x0) / 5 for i in range(5)]
        for index, x in enumerate(centers, 1):
            name = f"UY_V031_LETRERO_HALO_{index:02d}"; desired.add(name)
            ob = owned_object(name, "LIGHT", col); enum_set(ob.data, "type", "AREA")
            ob.data.size = .5; ob.data.energy = cfg["night_sign_energy"]
            ob.location = (x, y_back + .025, (z0 + z1) / 2)
            direction = Vector((x, y_back + .14, (z0 + z1) / 2)) - ob.location
            ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
            kelvin_light(ob.data, cfg["night_sign_kelvin"]); ob.lightgroup = "LETRERO"; ob.hide_render = False
    if method == "wash":
        for index, fac in enumerate((.15, .5, .85), 1):
            name = f"UY_V031_LETRERO_BANADOR_{index:02d}"; desired.add(name)
            ob = owned_object(name, "LIGHT", col); enum_set(ob.data, "type", "SPOT")
            x = x0 + fac * (x1 - x0)
            ob.location = (x, y_front - .8, z1 + .25)
            ob.rotation_euler = (Vector((x, y_front, (z0 + z1) / 2)) - ob.location).to_track_quat("-Z", "Y").to_euler()
            ob.data.energy = cfg["night_sign_energy"] * 3
            ob.data.spot_size = math.radians(70); ob.data.spot_blend = .65; ob.data.shadow_soft_size = .035
            kelvin_light(ob.data, cfg["night_sign_kelvin"]); ob.lightgroup = "LETRERO"; ob.hide_render = False
    for ob in col.objects:
        if ob.get("UY_OWNER") == OWNER and ob.name not in desired: ob.hide_render = True
    return {"method": method, "lights": sorted(desired), "letter_material_unchanged": True,
            "provisional_scheme": method != "legacy", "bounds": [x0, x1, y_front, y_back, z0, z1]}


def lightgroups(scene):
    for vl in scene.view_layers:
        for name in GROUPS:
            if name not in vl.lightgroups: vl.lightgroups.add(name=name)
    if scene.world: scene.world.lightgroup = "CIELO"
    for ob in scene.objects:
        if ob.type != "LIGHT": continue
        upper = ob.name.upper()
        if "INTERIOR" in upper: ob.lightgroup = "INTERIOR"
        elif "LETRERO" in upper: ob.lightgroup = "LETRERO"
        elif "UPLIGHT" in upper: ob.lightgroup = "UPLIGHTS"
        elif "ALERO" in upper: ob.lightgroup = "ALERO"
        else: ob.lightgroup = "CIELO"


def comp_node(nt, kind, label=""):
    n = nt.nodes.new(kind); n.label = label; return n


def comp_socket(n, key, value):
    socket = n.inputs.get(key)
    if socket is None: raise RuntimeError(f"Socket compositor ausente: {n.bl_idname}.{key}")
    socket.default_value = value


def mix_rgba(nt, fac, a, b, blend):
    n = comp_node(nt, "ShaderNodeMix"); enum_set(n, "data_type", "RGBA"); enum_set(n, "blend_type", blend)
    next(s for s in n.inputs if s.name == "Factor" and s.type == "VALUE").default_value = fac
    for key, value in (("A", a), ("B", b)):
        target = next(s for s in n.inputs if s.name == key and s.type == "RGBA")
        if isinstance(value, bpy.types.NodeSocket): nt.links.new(value, target)
        else: target.default_value = value
    return next(s for s in n.outputs if s.type == "RGBA")


def compositor(scene, cfg):
    if not hasattr(scene, "compositing_node_group"):
        raise RuntimeError("Se requiere la API compositing_node_group de Blender 5.2")
    is_night = "CREPUSCULO" in scene.name
    name = "UY_V031_OPTICA_" + scene.name
    old = bpy.data.node_groups.get(name)
    if old and old.get("UY_OWNER") != OWNER: raise RuntimeError("Grupo compositor ajeno")
    current = scene.compositing_node_group
    if "UY_V031_BASE_COMPOSITOR" not in scene:
        scene["UY_V031_BASE_COMPOSITOR"] = current.name if current else ""
        if current: current.use_fake_user = True
    nt = bpy.data.node_groups.new(name + "_CANDIDATE", "CompositorNodeTree")
    nt["UY_OWNER"] = OWNER
    nt.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    rl = comp_node(nt, "CompositorNodeRLayers", "Escena explícita"); rl.scene = scene
    last = rl.outputs["Image"]
    glare = comp_node(nt, "CompositorNodeGlare", "Halo óptico suave")
    for key, value in (("Type", "Fog Glow"), ("Threshold", 1.5 if is_night else 1.2),
                       ("Strength", .08 if is_night else .12), ("Size", .5 if is_night else .55)):
        comp_socket(glare, key, value)
    nt.links.new(last, glare.inputs["Image"]); last = glare.outputs["Image"]
    # Viñeta óptica separada del color de los materiales.
    ellipse = comp_node(nt, "CompositorNodeEllipseMask")
    comp_socket(ellipse, "Size", (1.15, 1.15))
    blur = comp_node(nt, "CompositorNodeBlur"); comp_socket(blur, "Size", (300.0, 300.0))
    nt.links.new(ellipse.outputs["Mask"], blur.inputs["Image"])
    last = mix_rgba(nt, .30, last, blur.outputs["Image"], "MULTIPLY")
    coordinates = comp_node(nt, "CompositorNodeImageCoordinates")
    nt.links.new(rl.outputs["Image"], coordinates.inputs["Image"])
    noise = comp_node(nt, "ShaderNodeTexWhiteNoise"); enum_set(noise, "noise_dimensions", "2D")
    nt.links.new(coordinates.outputs["Pixel"], noise.inputs["Vector"])
    grain = cfg["grain_night"] if is_night else cfg["grain_day"]
    multiply = comp_node(nt, "ShaderNodeMath"); enum_set(multiply, "operation", "MULTIPLY_ADD")
    nt.links.new(noise.outputs["Value"], multiply.inputs[0])
    multiply.inputs[1].default_value = grain * 2; multiply.inputs[2].default_value = -grain
    last = mix_rgba(nt, 1.0, last, multiply.outputs[0], "ADD")
    lens = comp_node(nt, "CompositorNodeLensdist", "Óptica leve")
    nt.links.new(last, lens.inputs["Image"])
    comp_socket(lens, "Distortion", cfg["lens_distortion"])
    comp_socket(lens, "Dispersion", cfg["lens_dispersion"])
    comp_socket(lens, "Fit", True)
    out = comp_node(nt, "NodeGroupOutput"); nt.links.new(lens.outputs["Image"], out.inputs["Image"])
    if old: old.name = name + "_ANTERIOR"
    nt.name = name; scene.compositing_node_group = nt
    if old and not old.users: bpy.data.node_groups.remove(old)
    return name


def render_settings(scene, quality):
    if quality not in {"DRAFT", "FINAL"}: raise ValueError("render_quality: DRAFT/FINAL")
    night = "CREPUSCULO" in scene.name
    cy = scene.cycles
    cy.use_adaptive_sampling = True
    cy.samples = (768 if night else 512) if quality == "FINAL" else (256 if night else 192)
    cy.adaptive_threshold = .005 if night and quality == "FINAL" else (.01 if quality == "FINAL" else .03)
    cy.sample_clamp_indirect = 10.0
    if hasattr(cy, "use_light_tree"): cy.use_light_tree = True
    cy.use_denoising = True; enum_set(cy, "denoiser", "OPENIMAGEDENOISE")
    for key, value in (("denoising_input_passes", "RGB_ALBEDO_NORMAL"), ("denoising_prefilter", "ACCURATE"),
                       ("denoising_quality", "HIGH")):
        if hasattr(cy, key): enum_set(cy, key, value)
    # Dispositivo, rebotes y cáusticas existentes se conservan.


def aplicar(params=None, log_path=None):
    cfg = dict(DEFAULTS); cfg.update(params or {})
    scenes = [sc for sc in bpy.data.scenes if sc.name.startswith("UYUNI_")]
    if not scenes: raise RuntimeError("Faltan escenas UYUNI_")
    night = bpy.data.scenes.get("UYUNI_CREPUSCULO")
    if night is None: raise RuntimeError("Falta escena crepuscular")
    meshes_before = len(bpy.data.meshes)
    log = {"owner": OWNER, "config": cfg, "before": {sc.name: snapshot(sc) for sc in scenes},
           "cameras": {}, "emission": {}, "warnings": ["Exposición y energía son candidatos de la guía; validar False Color sin compositor."]}
    if cfg["straighten"]:
        for name in STRAIGHTEN:
            cam = bpy.data.objects.get(name)
            if cam:
                height = cfg["camera_night_height"] if name == "CAM_03_CREPUSCULAR_NIEVE" else None
                log["cameras"][name] = straighten_camera(cam, height)
    if cfg["create_air_camera"]:
        log["air_camera"] = build_air_camera(cfg, scenes)
    if cfg["day_calibration"]:
        sun = bpy.data.objects.get("UY_SOL_MANANA")
        if sun and sun.type == "LIGHT":
            baseline(sun.data, "ENERGY", sun.data.energy); sun.data.energy = cfg["day_sun_energy"]
        handled = set()
        for sc in scenes:
            if "CREPUSCULO" in sc.name or not sc.world or sc.world.name in handled: continue
            handled.add(sc.world.name)
            for node in sc.world.node_tree.nodes:
                if node.type == "BACKGROUND":
                    if node.inputs["Strength"].is_linked:
                        raise RuntimeError("Cielo con fuerza procedural: no sobrescribir")
                    baseline(sc.world, "STRENGTH_" + node.name, node.inputs["Strength"].default_value)
                    node.inputs["Strength"].default_value = cfg["day_world_strength"]
    if cfg["night_practical_kelvin"]:
        for name, kelvin in (("UY_LUMINARIA_ALERO", 3000), ("UY_INTERIOR_LUZ_CALIDA", 3500)):
            mat = bpy.data.materials.get(name)
            if mat: log["emission"][name] = emission_kelvin_preserve(mat, kelvin)
        lum = bpy.data.materials.get("UY_LUMINARIA_ALERO")
        if lum: enum_set(lum.cycles, "emission_sampling", "NONE")
        ob_lum = bpy.data.objects.get("UY_LUMINARIAS_ALERO")
        if ob_lum: baseline(ob_lum, "VISIBLE_DIFFUSE", ob_lum.visible_diffuse); ob_lum.visible_diffuse = False
        for ob in night.objects:
            if ob.type == "LIGHT" and "SPOT_ALERO" in ob.name:
                ob.data.energy = baseline(ob.data, "ENERGY", ob.data.energy) * cfg["night_spot_factor"]
                kelvin_light(ob.data, 3000)
                ob.data.shadow_soft_size = .05
    baseline(night, "LUZ_INTERIOR", night.get("luz_interior", 7.0))
    baseline(night, "EXPOSURE", night.view_settings.exposure)
    night["luz_interior"] = cfg["night_interior_attribute"]
    night.view_settings.exposure = cfg["night_exposure"]
    if cfg["interior_area_lights"]:
        log["interior_lights"] = area_grid(night, cfg)
    else:
        col = bpy.data.collections.get("08_V031_INTERIOR_NOCHE")
        if col and col.get("UY_OWNER") == OWNER:
            for ob in col.objects: ob.hide_render = True
    log["night_sign"] = sign_candidates(night, cfg)
    for sc in scenes:
        if cfg["lightgroups"]: lightgroups(sc)
        render_settings(sc, cfg["render_quality"])
        if cfg["compositor"] and (cfg["day_optics"] or sc == night):
            compositor(sc, cfg)
        elif hasattr(sc, "compositing_node_group") and sc.compositing_node_group and sc.compositing_node_group.get("UY_OWNER") == OWNER:
            sc.compositing_node_group = None
        sc["UY_V031_CAMERA_LIGHT_PARAMS"] = json.dumps(cfg, sort_keys=True)
    if len(bpy.data.meshes) != meshes_before: raise RuntimeError("El complemento añadió mallas")
    log["after"] = {sc.name: snapshot(sc) for sc in scenes}
    log["mesh_count_unchanged"] = meshes_before
    if log_path: Path(log_path).write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    return log


@contextlib.contextmanager
def false_color(scene):
    view, look, comp = scene.view_settings.view_transform, scene.view_settings.look, scene.compositing_node_group
    try:
        enum_set(scene.view_settings, "view_transform", "False Color")
        enum_set(scene.view_settings, "look", "None")
        scene.compositing_node_group = None
        yield
    finally:
        scene.view_settings.view_transform = view; scene.view_settings.look = look
        scene.compositing_node_group = comp


def preparar_dron_equilibrado(scene_name="UYUNI_DIA", activate=False, log_path=None):
    """Alternativa de 600 cuadros, 24 fps; original CAM_DRON y su target intactos.

    Claves LINEAR impiden overshoot de Bézier. La clave 345 asciende delante del
    edificio antes de doblar el testero, manteniendo la cámara fuera de la huella.
    Activar la cámara o cambiar el rango de escena es una opción explícita.
    """
    scene = bpy.data.scenes.get(scene_name)
    original = bpy.data.objects.get("CAM_DRON")
    if scene is None or original is None or original.type != "CAMERA":
        raise RuntimeError("Falta escena o cámara original de dron")
    col = owned_collection("08_V031_DRON_EQUILIBRADO", scene.collection)
    cam = bpy.data.objects.get("CAM_DRON_EQUILIBRADO")
    if cam:
        if cam.get("UY_OWNER") != OWNER or cam.type != "CAMERA":
            raise RuntimeError("Cámara de dron equilibrado ajena")
        cam.animation_data_clear()
        cam.data.animation_data_clear()
        for constraint in list(cam.constraints): cam.constraints.remove(constraint)
    else:
        data = original.data.copy(); data.name = "CAM_DRON_EQUILIBRADO"
        data.animation_data_clear()
        cam = bpy.data.objects.new("CAM_DRON_EQUILIBRADO", data); cam["UY_OWNER"] = OWNER
        col.objects.link(cam)
    target = bpy.data.objects.get("UY_V031_DRON_EQUILIBRADO_TARGET")
    if target:
        if target.get("UY_OWNER") != OWNER: raise RuntimeError("Target ajeno")
        target.animation_data_clear()
    else:
        target = bpy.data.objects.new("UY_V031_DRON_EQUILIBRADO_TARGET", None)
        target["UY_OWNER"] = OWNER; col.objects.link(target)
    points = {
        1: ((-40, -120, 55), (36, 10, 5)),
        150: ((-15, -45, 22), (38, -.5, 5)),
        300: ((45, -16, 7), (55.64, -.5, 6)),
        345: ((89, -8, 28), (82, 12, 6)),
        450: ((120, 32, 32), (60, 40, 6)),
        600: ((78, 122, 45), (35, 65, 5)),
    }
    original_matrix = [list(row) for row in original.matrix_world]
    original_action = original.animation_data.action if original.animation_data else None
    for frame, (position, focus) in points.items():
        cam.location = position; target.location = focus
        cam.keyframe_insert(data_path="location", frame=frame)
        target.keyframe_insert(data_path="location", frame=frame)
    def fcurves_of(ob):
        action = ob.animation_data.action
        if hasattr(action, "fcurves"): return list(action.fcurves)
        result = []
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    result.extend(bag.fcurves)
        return result
    for ob in (cam, target):
        ob.animation_data.action.name = "UY_V031_" + ob.name + "_ACTION"
        for curve in fcurves_of(ob):
            for key in curve.keyframe_points: enum_set(key, "interpolation", "LINEAR")
    constraint = cam.constraints.new(type="TRACK_TO")
    constraint.name = "UY_V031_MIRAR_TARGET"; constraint.target = target
    enum_set(constraint, "track_axis", "TRACK_NEGATIVE_Z"); enum_set(constraint, "up_axis", "UP_Y")
    cam.data.lens = 24; cam.data.sensor_width = 36; cam.data.shift_y = 0
    cam.data.dof.use_dof = False
    cam["UY_V031_FPS"] = 24; cam["UY_V031_FRAME_RANGE"] = [1, 600]
    cam["UY_V031_ROUTE"] = json.dumps(points)
    # Comprobar los 600 puntos del recorrido contra una envolvente conservadora
    # de cubierta 13,023854 m +1 m; cámara baja de Tierra queda fuera del edificio.
    frames = sorted(points)
    near_roof = []
    for frame in range(1, 601):
        right = next((i for i, value in enumerate(frames) if value >= frame), len(frames) - 1)
        left = max(0, right - 1)
        a, b = frames[left], frames[right]
        fac = (frame - a) / (b - a) if b > a else 0
        pos = Vector(points[a][0]).lerp(Vector(points[b][0]), fac)
        if -.7 <= pos.x <= 83.4 and -2.6 <= pos.y <= 48.9 and pos.z < 14.023854:
            near_roof.append(frame)
    if near_roof: raise RuntimeError(f"Recorrido demasiado próximo a cubierta: {near_roof}")
    if [list(row) for row in original.matrix_world] != original_matrix or (original.animation_data.action if original.animation_data else None) != original_action:
        raise RuntimeError("Se modificó la cámara original")
    if activate:
        scene.camera = cam; scene.frame_start = 1; scene.frame_end = 600
        scene.render.fps = 24; scene.render.fps_base = 1
    log = {"camera": cam.name, "target": target.name, "original_unchanged": True,
           "points": points, "interpolation": "LINEAR", "conservative_clearance_check": "PASS",
           "activated": activate, "frames": 600, "fps": 24}
    if log_path: Path(log_path).write_text(json.dumps(log, indent=2), encoding="utf-8")
    return log


if __name__ == "__main__":
    raise RuntimeError("Importar este complemento y llamar aplicar(); no ejecuta un render ni guarda el proyecto.")
