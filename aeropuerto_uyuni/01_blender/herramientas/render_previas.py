"""Renderiza vistas previas rápidas (CPU, pocas muestras) de las cámaras del modelo.

Uso:
  blender -b -P render_previas.py -- ../uyuni_v2.blend ../previews CAM_01_HERO_LADO_TIERRA,CAM_04_AEREA_GENERAL [ancho] [muestras]
  python render_previas.py -- ...                                          (con el módulo bpy)

Las cámaras CAM_03* se renderizan en la escena UYUNI_CREPUSCULO; el resto, en UYUNI_DIA.
Por defecto: 960 px de ancho (16:9) y 24 muestras con eliminación de ruido. No modifica el .blend.
"""
import sys
import time

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
blend, salida, camaras = args[0], args[1], args[2].split(",")
ancho = int(args[3]) if len(args) > 3 else 960
muestras = int(args[4]) if len(args) > 4 else 24

bpy.ops.wm.open_mainfile(filepath=blend)
for cam in camaras:
    sc = bpy.data.scenes["UYUNI_CREPUSCULO" if cam.startswith("CAM_03") else "UYUNI_DIA"]
    if bpy.context.window:
        bpy.context.window.scene = sc
    sc.camera = bpy.data.objects[cam]
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = ancho, int(ancho * 9 / 16), 100
    sc.cycles.samples = muestras
    sc.cycles.device = "CPU"
    try:
        sc.cycles.use_denoising = True
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception as e:
        print("sin OIDN:", e)
        sc.cycles.use_denoising = False
    sc.render.filepath = f"{salida}/{cam}.png"
    t = time.time()
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print(f"[RENDER] {cam} {ancho}px {muestras} muestras -> {time.time() - t:.1f} s")
