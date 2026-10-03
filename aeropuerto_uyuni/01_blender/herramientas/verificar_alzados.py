"""Alzados y cortes ortogonales del modelo con el mismo encuadre que las vistas del CAD (00_auditoria/vistas).

Cada render cubre exactamente el bbox de su vista del DXF y tiene su mismo tamaño en píxeles, así que se puede
superponer con el PNG del CAD (ver superponer_cad.py). Usa luz neutra (cielo blanco uniforme, sin sol) para
que todas las fachadas se lean igual. No modifica el .blend.

Uso:
  python render: blender -b -P verificar_alzados.py -- ../uyuni_v2.blend ../../00_auditoria/vistas <carpeta_salida> [muestras]
  (o python verificar_alzados.py -- ... con el módulo bpy)
"""
import json
import os
import struct
import sys
import time

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
blend, vistas_dir, salida = args[0], args[1], args[2]
muestras = int(args[3]) if len(args) > 3 else 16

# Transformaciones DXF -> modelo (ver vistas_index.json). "h" lleva la x del DXF a la coordenada horizontal del
# modelo (X en NE/SO, Y en laterales y cortes); la altura es siempre z = y_dxf - npt_y.
VISTAS = {
    "FACHADA_NORESTE_ACTUAL": dict(mira=(0, 1, 0), h=lambda x: x),                         # Lado Tierra, desde -Y
    "FACHADA_SUROESTE": dict(mira=(0, -1, 0), h=lambda x: 187.84 - x),                     # Lado Aire, desde +Y
    "FACHADA_ESTE": dict(mira=(-1, 0, 0), h=lambda x: -0.308 + (x - 249.787)),             # testero eje 20, desde +X
    "FACHADA_OESTE": dict(mira=(1, 0, 0), h=lambda x: -0.308 + (384.834 - x)),             # testero eje 1, desde -X
    "CORTE_ACTUAL_POR_M1": dict(mira=(1, 0, 0), h=lambda x: -41.147 - x, corte_x=11.5),    # por la ME-1 del vano 3-4
    "CORTE_ACTUAL_MURO_CIEGO": dict(mira=(1, 0, 0), h=lambda x: -24.125 - x, corte_x=10.3),  # por el paño ciego, vano 3-4
}


def tam_png(ruta):
    with open(ruta, "rb") as f:
        f.read(16)
        return struct.unpack(">II", f.read(8))


bpy.ops.wm.open_mainfile(filepath=blend)
indice = json.load(open(os.path.join(vistas_dir, "vistas_index.json"), encoding="utf-8"))
sc = bpy.data.scenes["UYUNI_DIA"]
if bpy.context.window:
    bpy.context.window.scene = sc

# luz neutra: sin sol, cielo blanco uniforme y transformación de color estándar
for ob in sc.objects:
    if ob.type == "LIGHT":
        ob.hide_render = True
w = bpy.data.worlds.new("VERIF_NEUTRO")
w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
bg.inputs["Strength"].default_value = 1.0
sc.world = w
sc.view_settings.view_transform = "Standard"
sc.view_settings.exposure = 0.0
sc.cycles.samples = muestras
sc.cycles.device = "CPU"
try:
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
except Exception:
    sc.cycles.use_denoising = False

os.makedirs(salida, exist_ok=True)
for nombre, v in VISTAS.items():
    b = indice[nombre]["bbox_dxf"]
    npt = indice[nombre].get("npt_y", 0.0) or 0.0
    ancho_m, alto_m = b["xmax"] - b["xmin"], b["ymax"] - b["ymin"]
    hc = v["h"]((b["xmin"] + b["xmax"]) / 2)
    zc = (b["ymin"] + b["ymax"]) / 2 - npt
    mira = Vector(v["mira"])
    if "corte_x" in v:                       # corte: el plano de recorte cercano de la cámara hace de plano de corte
        dist = 60.0
        pos = Vector((v["corte_x"] - dist, hc, zc))
    else:                                    # alzado: cámara a 300 m delante de la fachada
        dist = 0.1
        pos = (Vector((hc, 0, zc)) if mira.y else Vector((0, hc, zc))) - mira * 300.0
    cd = bpy.data.cameras.new("VERIF_" + nombre)
    cd.type = "ORTHO"
    cd.ortho_scale = ancho_m
    cd.sensor_fit = "HORIZONTAL"
    cd.clip_start, cd.clip_end = dist, 6000.0
    cam = bpy.data.objects.new("VERIF_" + nombre, cd)
    cam.location = pos
    cam.rotation_euler = mira.to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(cam)
    sc.camera = cam
    px, py = tam_png(os.path.join(vistas_dir, indice[nombre]["png"]))
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = px, py, 100
    sc.render.filepath = os.path.join(salida, f"MODELO_{nombre}.png")
    t = time.time()
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print(f"[VERIF] {nombre} {px}x{py} -> {time.time() - t:.1f} s")
