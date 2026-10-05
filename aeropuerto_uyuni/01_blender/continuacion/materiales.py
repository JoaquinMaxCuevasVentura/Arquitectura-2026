"""Refinamiento v031; importar y llamar aplicar(), nunca abre, guarda ni renderiza.

Aplicar después de aplicar_cambios_4oct.py. La geometría y PALETA se conservan.
Controles independientes permiten comparar física, máscaras y sombra del vidrio.
Los materiales aprobados se copian con fake user; sólo se cambian slots de objetos.
No se remapean globalmente los materiales de meshes de respaldo.
"""
import contextlib
import json
import math
from pathlib import Path

import bpy

OWNER = "uyuni_v031_materiales_20261004"
DEFAULTS = {
    "profile": "ESTUDIO",              # DRON omite todos los nodos AO y Bevel
    "smart_masks": True,
    "albedo_luminance_bounds": (0.03, 0.85),
    "roof_p2_finish": "conservar",     # conservar / pintada / aluzinc; decisión del cliente
    "glass_shadow_transparent": False,  # comparación separada; override de rayos, no física DVH
    "glass_tint_comparison": True,      # crea #A9BCCB sin asignarlo
    "dust_day": 1.0,
    "dust_night": 0.6,
    "preserve_luxalon": True,
}
ROLES = {
    "UY_CHAPA_CUBIERTA": "roof",
    "UY_CHAPA_ANTEPECHO_REMATES": "sheet",
    "UY_BASTIDOR_CELOSIAS": "frame",
    "UY_CELOSIA_CORTEN_O_BLANCA": "corten",
    "UY_LETRERO_BLANCO_O_CORTEN": "letters",
    "UY_ALUMINIO_ANTRACITA_MATE": "profile",
    "UY_ALUMINIO_NEGRO_MATE": "profile",
    "UY_PUERTA_ACERO_NEGRO_MATE": "profile",
    "UY_ACERO_GALVANIZADO": "galvanized",
    "UY_REVOQUE_CONTINUO": "wall",
    "UY_REVOQUE_FACHADA_BUNAS": "wall",
    "UY_HORMIGON_VISTO": "concrete",
    "UY_HORMIGON": "concrete",
    "UY_HORMIGON_BLANCO_PREFABRICADO": "concrete",     # anillos y hexágonos del frente
    "UY_CORDON_PINTADO_AMARILLO": "pavement",          # separador, espiga y columnas del frente
    "UY_ACERA_HORMIGON": "pavement",
    "UY_ACERA": "pavement",
    "UY_HORMIGON_FRATASADO": "pavement",
    "UY_ASFALTO": "asphalt",
    "UY_CIELO_LISTONES": "wood",
    "UY_CIELO_LISTONADO": "wood",
    "UY_VIDRIO_CONTROL_SOLAR": "glass",
    "UY_PLENUM_NEGRO_MATE": "dark",
    "UY_SELLO_ESTRUCTURAL_NEGRO": "dark",
    "UY_NIEVE": "snow",
}


def srgb(h):
    rgb = [int(h.lstrip("#")[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb) + (1.0,)


def set_enum(ob, prop, value):
    """Inspección RNA antes de asignar un enum; no adivina valores."""
    p = ob.bl_rna.properties.get(prop)
    if p is None:
        raise RuntimeError(f"RNA ausente: {type(ob).__name__}.{prop}")
    if p.type == "ENUM" and value not in {i.identifier for i in p.enum_items}:
        raise RuntimeError(f"Enum no disponible: {prop}={value}")
    setattr(ob, prop, value)


def principled(mat):
    nodes = [n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"]
    if len(nodes) != 1:
        raise RuntimeError(f"{mat.name}: se esperaba un Principled, hay {len(nodes)}")
    return nodes[0]


class Graph:
    def __init__(self, nt):
        self.nt, self.links = nt, nt.links

    def node(self, kind, label="", **props):
        n = self.nt.nodes.new(kind)
        n.label = label or kind.removeprefix("ShaderNode")
        for key, value in props.items():
            prop = n.bl_rna.properties.get(key)
            if prop and prop.type == "ENUM":
                set_enum(n, key, value)
            else:
                setattr(n, key, value)
        return n

    def put(self, value, socket):
        if isinstance(value, bpy.types.NodeSocket):
            self.links.new(value, socket)
        else:
            for link in list(socket.links):
                self.links.remove(link)
            socket.default_value = value
        return socket

    def source(self, socket):
        if socket.is_linked:
            return socket.links[0].from_socket
        n = self.node("ShaderNodeRGB" if socket.type == "RGBA" else "ShaderNodeValue")
        n.outputs[0].default_value = socket.default_value
        return n.outputs[0]

    def math(self, op, a, b=0.0, clamp=False):
        n = self.node("ShaderNodeMath", operation=op)
        n.use_clamp = clamp
        self.put(a, n.inputs[0]); self.put(b, n.inputs[1])
        return n.outputs[0]

    def ramp(self, value, lo, hi, outlo=0.0, outhi=1.0):
        n = self.node("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP", clamp=True)
        for key, val in (("Value", value), ("From Min", lo), ("From Max", hi),
                         ("To Min", outlo), ("To Max", outhi)):
            self.put(val, n.inputs[key])
        return n.outputs["Result"]

    def noise(self, pos, scale, detail=3.0, roughness=0.5, distortion=0.0):
        n = self.node("ShaderNodeTexNoise", noise_dimensions="3D")
        for key, val in (("Vector", pos), ("Scale", scale), ("Detail", detail),
                         ("Roughness", roughness), ("Distortion", distortion)):
            self.put(val, n.inputs[key])
        return n.outputs["Fac"]

    def mix(self, fac, a, b, datatype="RGBA"):
        n = self.node("ShaderNodeMix", data_type=datatype)
        typ = "VALUE" if datatype == "FLOAT" else "RGBA"
        sockets = {key: next(s for s in n.inputs if s.name == key and s.type == typ)
                   for key in ("A", "B")}
        self.put(fac, next(s for s in n.inputs if s.name == "Factor" and s.type == "VALUE"))
        self.put(a, sockets["A"]); self.put(b, sockets["B"])
        return next(s for s in n.outputs if s.type == typ)

    def scale(self, color, factor):
        n = self.node("ShaderNodeVectorMath", operation="SCALE")
        self.put(color, n.inputs[0]); self.put(factor, n.inputs["Scale"])
        return n.outputs["Vector"]

    def attribute(self, name):
        n = self.node("ShaderNodeAttribute", attribute_type="VIEW_LAYER", attribute_name=name)
        return n.outputs["Fac"]


def mask_group(profile):
    name = "UY_MASCARAS_ALTIPLANO_" + profile
    old = bpy.data.node_groups.get(name)
    if old:
        if old.get("UY_OWNER") != OWNER:
            raise RuntimeError(f"Colisión con grupo ajeno: {name}")
        return old
    nt = bpy.data.node_groups.new(name, "ShaderNodeTree")
    nt["UY_OWNER"] = OWNER
    for name_, default in (("RadioArista", .01), ("DistAO", .30), ("AltSalpicado", .30)):
        nt.interface.new_socket(name=name_, in_out="INPUT", socket_type="NodeSocketFloat").default_value = default
    for name_ in ("Arista", "Cavidad", "Arriba", "Pie", "Ruptura", "Grano"):
        nt.interface.new_socket(name=name_, in_out="OUTPUT", socket_type="NodeSocketFloat")
    g = Graph(nt)
    inp, out = g.node("NodeGroupInput"), g.node("NodeGroupOutput")
    geo = g.node("ShaderNodeNewGeometry")
    pos, normal = geo.outputs["Position"], geo.outputs["Normal"]
    sep_n = g.node("ShaderNodeSeparateXYZ"); g.put(normal, sep_n.inputs[0])
    sep_p = g.node("ShaderNodeSeparateXYZ"); g.put(pos, sep_p.inputs[0])
    rupture = g.noise(pos, .9, 4.0, .5, .4)
    grain = g.noise(pos, 420.0, 2.0)
    up = g.ramp(sep_n.outputs["Z"], .55, .95)
    z = g.math("ADD", sep_p.outputs["Z"], g.math("MULTIPLY", g.noise(pos, 9.0), .18))
    height = g.ramp(z, 0.0, inp.outputs["AltSalpicado"], 1.0, 0.0)
    vertical = g.ramp(g.math("ABSOLUTE", sep_n.outputs["Z"]), .45, .70, 1.0, 0.0)
    foot = g.math("MULTIPLY", height, vertical)
    edge = cavity = 0.0
    if profile == "ESTUDIO":
        bevel = g.node("ShaderNodeBevel", samples=4)
        g.put(inp.outputs["RadioArista"], bevel.inputs["Radius"])
        dot = g.node("ShaderNodeVectorMath", operation="DOT_PRODUCT")
        g.put(normal, dot.inputs[0]); g.put(bevel.outputs["Normal"], dot.inputs[1])
        edge = g.ramp(dot.outputs["Value"], .70, .995, 1.0, 0.0)
        ao = g.node("ShaderNodeAmbientOcclusion", samples=2, only_local=False)
        g.put(inp.outputs["DistAO"], ao.inputs["Distance"])
        cavity = g.ramp(g.math("SUBTRACT", 1.0, ao.outputs["AO"]), .10, .55)
    for key, value in (("Arista", edge), ("Cavidad", cavity), ("Arriba", up),
                       ("Pie", foot), ("Ruptura", rupture), ("Grano", grain)):
        g.put(value, out.inputs[key])
    return nt


def masks(g, profile, ao_distance=.3, radius=.01):
    n = g.node("ShaderNodeGroup", label="Máscaras métricas")
    n.node_tree = mask_group(profile)
    n.inputs["DistAO"].default_value = ao_distance
    n.inputs["RadioArista"].default_value = radius
    return n.outputs


def bound_albedo(g, color, bounds):
    """Limita luminancia lineal preservando la relación de canales y la paleta."""
    bw = g.node("ShaderNodeRGBToBW"); g.put(color, bw.inputs[0])
    lum = bw.outputs[0]
    target = g.math("MINIMUM", g.math("MAXIMUM", lum, bounds[0]), bounds[1])
    factor = g.math("DIVIDE", target, g.math("MAXIMUM", lum, .000001))
    return g.scale(color, factor)


def dust_layer(mat, role, cfg):
    g, b = Graph(mat.node_tree), principled(mat)
    dist = {"sheet": .06, "roof": .06, "profile": .10, "frame": .10, "pavement": .35}.get(role, .30)
    mk = masks(g, cfg["profile"], dist, .001 if role in {"sheet", "corten"} else .008)
    coefficient = .10 if role in {"sheet", "roof", "frame", "profile", "dark"} else .025
    mask = g.math("MULTIPLY", g.math("MAXIMUM", g.math("MULTIPLY", mk["Cavidad"], .35),
                                     g.math("MULTIPLY", mk["Arriba"], .65)), mk["Ruptura"])
    dust = g.math("MULTIPLY", g.math("MULTIPLY", mask, coefficient), g.attribute("polvo"), clamp=True)
    film = g.math("MULTIPLY", coefficient * .45, g.attribute("polvo"), clamp=True)
    dust = g.math("MAXIMUM", dust, film)
    foot = g.math("MULTIPLY", g.math("MULTIPLY", mk["Pie"], mk["Ruptura"]),
                  g.math("MULTIPLY", .18 if role in {"wall", "concrete"} else .06, g.attribute("polvo")), clamp=True)
    color = g.mix(dust, g.source(b.inputs["Base Color"]), srgb("#C2B8A3"))
    color = g.mix(foot, color, srgb("#9A8264"))
    g.put(color, b.inputs["Base Color"])
    rough = g.mix(g.math("MAXIMUM", dust, foot), g.source(b.inputs["Roughness"]), .92, "FLOAT")
    variation = g.math("MULTIPLY", g.math("SUBTRACT", mk["Ruptura"], .5), .10)
    g.put(g.math("ADD", rough, variation, clamp=True), b.inputs["Roughness"])
    # Altura independiente de AO/Bevel: únicamente orientación, altura y ruido.
    height = g.math("MULTIPLY", g.math("MAXIMUM", g.math("MULTIPLY", mk["Arriba"], .04), foot), mk["Grano"])
    bump = g.node("ShaderNodeBump", label="Polvo: relieve sin AO/Bevel")
    bump.inputs["Strength"].default_value = .25; bump.inputs["Distance"].default_value = .0004
    g.put(height, bump.inputs["Height"])
    if b.inputs["Normal"].is_linked:
        g.put(g.source(b.inputs["Normal"]), bump.inputs["Normal"])
    g.put(bump.outputs["Normal"], b.inputs["Normal"])
    return mk


def corten_variation(mat, role, cfg):
    g, b = Graph(mat.node_tree), principled(mat)
    geo = g.node("ShaderNodeNewGeometry")
    island = geo.outputs["Random Per Island"]
    is_corten = g.attribute("letras_corten") if role == "letters" else g.math("SUBTRACT", 1.0, g.attribute("propuesta"))
    amplitude = .10 if role == "letters" else .30
    factor = g.math("ADD", 1.0, g.math("MULTIPLY", g.math("SUBTRACT", island, .5), amplitude))
    base = g.source(b.inputs["Base Color"])
    varied = g.scale(base, factor)
    varied = g.mix(g.math("MULTIPLY", g.math("LESS_THAN", island, .40), .15), varied, srgb("#5E2C1A"))
    mk = masks(g, cfg["profile"], .10, .001 if role == "corten" else .008)
    patina = g.math("MULTIPLY", g.math("MAXIMUM", g.math("MULTIPLY", mk["Arriba"], .65),
                                       g.math("MULTIPLY", mk["Arista"], .40)), mk["Ruptura"])
    varied = g.mix(g.math("MULTIPLY", patina, .18), varied, srgb("#3A1A0E"))
    g.put(g.mix(is_corten, base, varied), b.inputs["Base Color"])
    if "Diffuse Roughness" in b.inputs:
        g.put(g.mix(is_corten, .7, .5, "FLOAT"), b.inputs["Diffuse Roughness"])


def wood_variation(mat):
    g, b = Graph(mat.node_tree), principled(mat)
    island = g.node("ShaderNodeNewGeometry").outputs["Random Per Island"]
    # Sólo el aspecto madera P1; P2 blanco conserva su valor aprobado.
    k = g.math("SUBTRACT", 1.0, g.attribute("propuesta"))
    factor = g.math("ADD", 1.0, g.math("MULTIPLY", k, g.math("MULTIPLY", g.math("SUBTRACT", island, .5), .16)))
    g.put(g.scale(g.source(b.inputs["Base Color"]), factor), b.inputs["Base Color"])
    for n in mat.node_tree.nodes:
        if n.type == "TEX_WAVE" and "Phase Offset" in n.inputs:
            g.put(g.math("MULTIPLY", island, 2 * math.pi), n.inputs["Phase Offset"])


def galvanized_variation(mat):
    g, b = Graph(mat.node_tree), principled(mat)
    geo = g.node("ShaderNodeNewGeometry")
    vor = g.node("ShaderNodeTexVoronoi", feature="F1")
    g.put(geo.outputs["Position"], vor.inputs["Vector"]); vor.inputs["Scale"].default_value = 60
    sep = g.node("ShaderNodeSeparateColor"); g.put(vor.outputs["Color"], sep.inputs[0])
    g.put(g.scale(g.source(b.inputs["Base Color"]), g.math("ADD", .92, g.math("MULTIPLY", sep.outputs[1], .16))), b.inputs["Base Color"])
    g.put(g.math("ADD", .30, g.math("MULTIPLY", sep.outputs[0], .16)), b.inputs["Roughness"])


def asphalt_variation(mat):
    g, b = Graph(mat.node_tree), principled(mat)
    pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
    vor = g.node("ShaderNodeTexVoronoi", feature="F1")
    g.put(pos, vor.inputs["Vector"]); vor.inputs["Scale"].default_value = 160
    sep = g.node("ShaderNodeSeparateColor"); g.put(vor.outputs["Color"], sep.inputs[0])
    grain = g.math("MULTIPLY", g.math("GREATER_THAN", sep.outputs[0], .82), g.math("LESS_THAN", vor.outputs["Distance"], .32))
    g.put(g.mix(g.math("MULTIPLY", grain, .30), g.source(b.inputs["Base Color"]), srgb("#77736C")), b.inputs["Base Color"])
    if "Diffuse Roughness" in b.inputs:
        g.put(.6, b.inputs["Diffuse Roughness"])


def configure_glass(mat, cfg, tint=None):
    g, b = Graph(mat.node_tree), principled(mat)
    for key, value in (("Metallic", 0.0), ("Transmission Weight", 1.0), ("IOR", 1.52),
                       ("Thin Wall", True), ("Thin Film Thickness", 67.0), ("Thin Film IOR", 1.8)):
        if key not in b.inputs:
            raise RuntimeError(f"Socket de vidrio faltante: {key}")
        g.put(value, b.inputs[key])
    if tint is not None:
        g.put(srgb(tint), b.inputs["Base Color"])
    # Las ondas aprobadas de 0,33 m y Bump de 0,003 m se conservan del integrador.
    if cfg["profile"] == "DRON":
        g.put(.02, b.inputs["Roughness"])
        for n in list(mat.node_tree.nodes):
            if n.type in {"AMBIENT_OCCLUSION", "BEVEL"}:
                mat.node_tree.nodes.remove(n)
    if cfg["glass_shadow_transparent"]:
        outputs = [n for n in mat.node_tree.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output]
        if len(outputs) != 1:
            raise RuntimeError("Vidrio: salida activa ambigua")
        out = outputs[0]
        physical = g.source(out.inputs["Surface"])
        light = g.node("ShaderNodeLightPath", label="Override de sombra: comparación")
        trans = g.node("ShaderNodeBsdfTransparent")
        tint_linear = srgb(tint or "#6E808E")
        trans.inputs["Color"].default_value = tuple(c * .82 for c in tint_linear[:3]) + (1.0,)
        mix = g.node("ShaderNodeMixShader")
        g.put(light.outputs["Is Shadow Ray"], mix.inputs[0])
        g.put(physical, mix.inputs[1]); g.put(trans.outputs[0], mix.inputs[2])
        g.put(mix.outputs[0], out.inputs["Surface"])
    mat["UY_GLASS_TINT"] = tint or "APROBADO_6E808E"
    mat["UY_GLASS_SHADOW_OVERRIDE"] = bool(cfg["glass_shadow_transparent"])
    mat["UY_GLASS_SHADOW_OVERRIDE_NOTE"] = "Comparación artística: tinte lineal ×0.82; no representa transmisión física del DVH."


def summary(mat):
    b = principled(mat)
    result = {"name": mat.name, "nodes": len(mat.node_tree.nodes), "users": mat.users}
    for key in ("Base Color", "Metallic", "Roughness", "IOR", "Transmission Weight", "Emission Strength"):
        s = b.inputs.get(key)
        if s:
            result[key] = {"linked": s.is_linked, "value": list(s.default_value) if s.type in {"RGBA", "VECTOR"} else s.default_value,
                           "source": s.links[0].from_node.name if s.is_linked else None}
    result["AO"] = sum(n.type == "AMBIENT_OCCLUSION" for n in mat.node_tree.nodes)
    result["Bevel"] = sum(n.type == "BEVEL" for n in mat.node_tree.nodes)
    return result


def pristine(name):
    baseline_name = "UY_V031_BASE_" + name
    backup = bpy.data.materials.get(baseline_name)
    if backup:
        if backup.get("UY_OWNER") != OWNER:
            raise RuntimeError(f"Respaldo ajeno: {baseline_name}")
        return backup
    original = bpy.data.materials.get(name)
    if original is None:
        return None
    backup = original.copy(); backup.name = baseline_name
    backup.use_fake_user = True; backup["UY_OWNER"] = OWNER; backup["UY_SOURCE"] = name
    return backup


def is_alternative(ob):
    return any("LUXALON" in col.name.upper() or "ALTERNATIVA" in col.name.upper() for col in ob.users_collection)


def assign_candidate(source_name, candidate, cfg):
    changed = []
    for ob in bpy.data.objects:
        if cfg["preserve_luxalon"] and is_alternative(ob):
            continue
        for slot in ob.material_slots:
            mat = slot.material
            if mat and (mat.name == source_name or (mat.get("UY_OWNER") == OWNER and mat.get("UY_SOURCE") == source_name)):
                slot.material = candidate
                changed.append(ob.name)
    return sorted(set(changed))


def aplicar(params=None, log_path=None):
    cfg = dict(DEFAULTS); cfg.update(params or {})
    if cfg["profile"] not in {"ESTUDIO", "DRON"}:
        raise ValueError("profile debe ser ESTUDIO o DRON")
    counts = {"objects": len(bpy.data.objects), "meshes": len(bpy.data.meshes), "scenes": len(bpy.data.scenes)}
    log = {"owner": OWNER, "config": cfg, "before_counts": counts, "materials": {}, "missing_optional": []}
    candidates = []
    # Construir todo antes de cambiar slots: ningún shader parcial llega al modelo si falla RNA.
    try:
        for source_name, role in ROLES.items():
            backup = pristine(source_name)
            if backup is None:
                log["missing_optional"].append(source_name); continue
            mat = backup.copy(); mat.name = "UY_V031_CANDIDATE_" + source_name
            mat.use_fake_user = False; mat["UY_OWNER"] = OWNER; mat["UY_SOURCE"] = source_name
            candidates.append((source_name, mat))
            g, b = Graph(mat.node_tree), principled(mat)
            before = summary(backup)
            if role == "glass":
                configure_glass(mat, cfg)
            else:
                metal = 1.0 if role == "galvanized" else 0.0
                if role == "roof":
                    finish = cfg["roof_p2_finish"]
                    if finish not in {"conservar", "pintada", "aluzinc"}:
                        raise ValueError("roof_p2_finish: conservar/pintada/aluzinc")
                    p2 = g.source(b.inputs["Metallic"]) if finish == "conservar" else float(finish == "aluzinc")
                    g.put(g.mix(g.attribute("propuesta"), 0.0, p2, "FLOAT"), b.inputs["Metallic"])
                else:
                    g.put(metal, b.inputs["Metallic"])
                if cfg["smart_masks"]:
                    if role in {"corten", "letters"}:
                        corten_variation(mat, role, cfg)
                    if role == "wood": wood_variation(mat)
                    if role == "galvanized": galvanized_variation(mat)
                    if role == "asphalt": asphalt_variation(mat)
                    if role not in {"snow", "wood"}: dust_layer(mat, role, cfg)
                diffuse = {"wall": .8, "concrete": .7, "asphalt": .6}.get(role)
                if diffuse is not None and "Diffuse Roughness" in b.inputs:
                    g.put(diffuse, b.inputs["Diffuse Roughness"])
                # Las paletas del edificio y el negro mate #2E2F31 están aprobados.
                # El límite se aplica a auxiliares, sin aclarar los muros negros P2.
                if role in {"dark", "asphalt", "snow"}:
                    g.put(bound_albedo(g, g.source(b.inputs["Base Color"]), cfg["albedo_luminance_bounds"]), b.inputs["Base Color"])
                if cfg["profile"] == "DRON":
                    for n in list(mat.node_tree.nodes):
                        if n.type in {"AMBIENT_OCCLUSION", "BEVEL"}: mat.node_tree.nodes.remove(n)
            log["materials"][source_name] = {"role": role, "before": before, "after": summary(mat)}
    except Exception:
        for _, mat in candidates:
            if not mat.users: bpy.data.materials.remove(mat)
        raise
    for source_name, mat in candidates:
        name = "UY_V031_SMART_" + source_name
        old = bpy.data.materials.get(name)
        if old and old.get("UY_OWNER") != OWNER:
            raise RuntimeError(f"Colisión de material: {name}")
        if old: old.name = name + "_ANTERIOR"
        mat.name = name
        log["materials"][source_name]["objects"] = assign_candidate(source_name, mat, cfg)
        if old and not old.users: bpy.data.materials.remove(old)
    for scene in bpy.data.scenes:
        if scene.name.startswith("UYUNI_"):
            scene["polvo"] = cfg["dust_night"] if "CREPUSCULO" in scene.name else cfg["dust_day"]
            scene["UY_V031_MATERIAL_PARAMS"] = json.dumps(cfg, sort_keys=True)
    if cfg["glass_tint_comparison"]:
        prepare_glass_comparison(cfg)
    log["after_counts"] = {"objects": len(bpy.data.objects), "meshes": len(bpy.data.meshes), "scenes": len(bpy.data.scenes)}
    if log["after_counts"] != counts:
        raise RuntimeError("El parche de materiales cambió objetos, meshes o escenas")
    if log_path:
        Path(log_path).write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    return log


def prepare_glass_comparison(cfg=None):
    cfg = dict(DEFAULTS, **(cfg or {}))
    name = "UY_V031_VIDRIO_COMPARACION_A9BCCB"
    old = bpy.data.materials.get(name)
    if old:
        if old.get("UY_OWNER") != OWNER: raise RuntimeError("Material de comparación ajeno")
        return old
    base = pristine("UY_VIDRIO_CONTROL_SOLAR")
    if base is None: raise RuntimeError("Falta vidrio aprobado")
    mat = base.copy(); mat.name = name; mat.use_fake_user = True
    mat["UY_OWNER"] = OWNER; mat["UY_COMPARACION_NO_APROBADA"] = True
    configure_glass(mat, dict(cfg, glass_shadow_transparent=False), "#A9BCCB")
    return mat


@contextlib.contextmanager
def glass_comparison(tint=False, shadow_transparent=False):
    """Cambio temporal exclusivamente para un render comparativo; restaura todos los slots."""
    cfg = dict(DEFAULTS, glass_shadow_transparent=shadow_transparent)
    base = pristine("UY_VIDRIO_CONTROL_SOLAR")
    if base is None: raise RuntimeError("Falta vidrio aprobado")
    mat = base.copy(); mat.name = "UY_V031_TEMP_GLASS_COMPARISON"
    configure_glass(mat, cfg, "#A9BCCB" if tint else None)
    changed = []
    try:
        for ob in bpy.data.objects:
            for slot in ob.material_slots:
                current = slot.material
                if current and (current.name == "UY_VIDRIO_CONTROL_SOLAR" or current.get("UY_SOURCE") == "UY_VIDRIO_CONTROL_SOLAR"):
                    changed.append((slot, current)); slot.material = mat
        yield {"tint": "#A9BCCB" if tint else "#6E808E", "shadow_override": shadow_transparent, "slots": len(changed)}
    finally:
        for slot, original in changed: slot.material = original
        if not mat.users: bpy.data.materials.remove(mat)


def material_diagnostico(profile="ESTUDIO"):
    name = "UY_V031_DIAGNOSTICO_" + profile
    existing = bpy.data.materials.get(name)
    if existing:
        if existing.get("UY_OWNER") != OWNER: raise RuntimeError("Material diagnóstico ajeno")
        return existing
    mat = bpy.data.materials.new(name); mat.use_nodes = True; mat.use_fake_user = True
    mat["UY_OWNER"] = OWNER; mat.node_tree.nodes.clear()
    g = Graph(mat.node_tree); mk = masks(g, profile)
    rgb = g.node("ShaderNodeCombineColor")
    g.put(mk["Arista"], rgb.inputs[0]); g.put(mk["Cavidad"], rgb.inputs[1])
    g.put(g.math("MAXIMUM", mk["Arriba"], mk["Pie"]), rgb.inputs[2])
    emit = g.node("ShaderNodeEmission"); g.put(rgb.outputs[0], emit.inputs["Color"])
    out = g.node("ShaderNodeOutputMaterial"); g.put(emit.outputs[0], out.inputs["Surface"])
    return mat


@contextlib.contextmanager
def diagnostico(scene, profile="ESTUDIO"):
    previous = [(vl, vl.material_override) for vl in scene.view_layers]
    old_comp = scene.compositing_node_group if hasattr(scene, "compositing_node_group") else None
    try:
        for vl, _ in previous: vl.material_override = material_diagnostico(profile)
        if hasattr(scene, "compositing_node_group"): scene.compositing_node_group = None
        yield
    finally:
        for vl, old in previous: vl.material_override = old
        if hasattr(scene, "compositing_node_group"): scene.compositing_node_group = old_comp


if __name__ == "__main__":
    raise RuntimeError("Importar este complemento y llamar aplicar(); no ejecuta un render ni guarda el proyecto.")
