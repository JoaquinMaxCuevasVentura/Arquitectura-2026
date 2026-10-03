"""Exporta un inventario legible del .blend (escenas, colecciones, objetos, cámaras, luces, materiales y proxies).

Sirve para revisar o continuar el modelo sin abrir Blender: qué existe, dónde está y con qué material.
Uso:
  python inventario_escena.py -- ../uyuni_v2.blend ../inventario_escena.json      (con el módulo bpy)
  blender -b -P inventario_escena.py -- ../uyuni_v2.blend ../inventario_escena.json
"""
import json
import math
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
blend, salida = args[0], args[1]
bpy.ops.wm.open_mainfile(filepath=blend)


def r(v, n=3):
    return [round(float(x), n) for x in v]


def caja_mundo(ob):
    esquinas = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return {"min": r([min(c[i] for c in esquinas) for i in range(3)]),
            "max": r([max(c[i] for c in esquinas) for i in range(3)])}


def colecciones_de(ob):
    return [c.name for c in ob.users_collection]


def valor_prop(v):
    try:
        return float(v) if isinstance(v, (int, float)) else str(v)
    except Exception:
        return str(v)


inv = {"archivo": bpy.path.basename(blend), "blender": bpy.app.version_string, "unidades": "metros",
       "sistema_coordenadas": "X = ejes 1->20 (eje 1 en 0); Y = ejes A->R (Lado Tierra hacia -Y); Z = m sobre NPT ±0,00",
       "escenas": {}, "colecciones": {}, "objetos": [], "camaras": {}, "luces": [], "materiales": [],
       "proxies_a_reemplazar": []}

for sc in bpy.data.scenes:
    vs = sc.view_settings
    inv["escenas"][sc.name] = {
        "camara_activa": sc.camera.name if sc.camera else None,
        "mundo": sc.world.name if sc.world else None,
        "motor": sc.render.engine,
        "resolucion": [sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage],
        "muestras": getattr(sc.cycles, "samples", None),
        "dispositivo": getattr(sc.cycles, "device", None),
        "cuadros": [sc.frame_start, sc.frame_end], "fps": sc.render.fps,
        "color": {"view_transform": vs.view_transform, "look": vs.look, "exposure": round(vs.exposure, 3)},
        "colecciones_enlazadas": [c.name for c in sc.collection.children],
        "propiedades": {k: valor_prop(sc[k]) for k in sc.keys() if not k.startswith("_") and k != "cycles"},
    }


def recorrer(c, padre):
    inv["colecciones"][c.name] = {"padre": padre, "objetos": len(c.objects),
                                  "oculta_en_render": c.hide_render,
                                  "hijas": [h.name for h in c.children]}
    for h in c.children:
        recorrer(h, c.name)


for c in bpy.data.collections:     # colecciones de primer nivel: padre = escenas que las enlazan
    escenas = [sc.name for sc in bpy.data.scenes if c.name in sc.collection.children]
    if escenas:
        recorrer(c, " + ".join(escenas))

for ob in sorted(bpy.data.objects, key=lambda o: o.name):
    d = {"nombre": ob.name, "tipo": ob.type, "colecciones": colecciones_de(ob),
         "ubicacion": r(ob.location), "rotacion_deg": r([math.degrees(a) for a in ob.rotation_euler], 2),
         "oculto_en_render": ob.hide_render}
    if ob.type == "MESH":
        d["caja_mundo"] = caja_mundo(ob)
        d["vertices"], d["caras"] = len(ob.data.vertices), len(ob.data.polygons)
        d["materiales"] = [s.material.name for s in ob.material_slots if s.material]
        d["modificadores"] = [f"{m.type}:{m.name}" for m in ob.modifiers]
    inv["objetos"].append(d)
    if ob.type == "CAMERA":
        cd = ob.data
        inv["camaras"][ob.name] = {"ubicacion": r(ob.matrix_world.translation),
                                   "direccion": r(ob.matrix_world.to_3x3() @ Vector((0, 0, -1))),
                                   "focal_mm": round(cd.lens, 1), "sensor_mm": cd.sensor_width, "tipo": cd.type,
                                   "animada": bool(ob.animation_data and ob.animation_data.action),
                                   "restricciones": [f"{k.type}->{getattr(k, 'target', None) and k.target.name}"
                                                     for k in ob.constraints]}
    if ob.type == "LIGHT":
        ld = ob.data
        inv["luces"].append({"nombre": ob.name, "tipo": ld.type, "energia": round(ld.energy, 3),
                             "temperatura_K": getattr(ld, "temperature", None) if getattr(ld, "use_temperature", False) else None,
                             "ubicacion": r(ob.location), "colecciones": colecciones_de(ob),
                             "direccion": r(ob.matrix_world.to_3x3() @ Vector((0, 0, -1)))})

for m in sorted(bpy.data.materials, key=lambda m: m.name):
    nodos = sorted({n.bl_idname for n in m.node_tree.nodes}) if m.node_tree else []
    atributos = sorted({n.attribute_name for n in m.node_tree.nodes if n.type == "ATTRIBUTE"}) if m.node_tree else []
    inv["materiales"].append({"nombre": m.name, "usuarios": m.users, "color_visor": r(m.diffuse_color),
                              "propiedades_de_escena_que_lee": atributos, "nodos": nodos})

# proxies de colocación: un registro por vehículo o persona, con su posición y tamaño para reemplazarlo
grupos = {}
for ob in bpy.data.objects:
    if "PROXIES_COLOCACION" in colecciones_de(ob):
        base = ob.name.rsplit("_", 1)[0] if ob.name.endswith(("_CARROCERIA", "_VIDRIOS", "_RUEDAS")) else ob.name
        g = grupos.setdefault(base, {"partes": [], "min": [1e9] * 3, "max": [-1e9] * 3,
                                     "rotacion_z_deg": round(math.degrees(ob.matrix_world.to_euler().z), 1)})
        g["partes"].append(ob.name)
        cb = caja_mundo(ob)
        g["min"] = [min(a, b) for a, b in zip(g["min"], cb["min"])]
        g["max"] = [max(a, b) for a, b in zip(g["max"], cb["max"])]
for base, g in sorted(grupos.items()):
    tipo = "minibus" if "MINIBUS" in base else ("vagoneta_4x4" if "4x4" in base else "persona")
    inv["proxies_a_reemplazar"].append({
        "proxy": base, "tipo": tipo, "partes": g["partes"],
        "centro_base": r([(g["min"][0] + g["max"][0]) / 2, (g["min"][1] + g["max"][1]) / 2, g["min"][2]]),
        "tamano": r([g["max"][i] - g["min"][i] for i in range(3)]), "rotacion_z_deg": g["rotacion_z_deg"]})

json.dump(inv, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"[OK] {salida}: {len(inv['objetos'])} objetos, {len(inv['camaras'])} cámaras, {len(inv['luces'])} luces, "
      f"{len(inv['materiales'])} materiales, {len(inv['proxies_a_reemplazar'])} proxies")
