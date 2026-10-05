"""Render del recorrido CAM_DRON en CPU con el módulo bpy (sin GPU ni Blender instalado), por tandas reanudables.

Abre uyuni_v2.blend y llama a render_plan.py, que espera el archivo ya abierto. Para el borrador de 960 x 540 hecho en
la nube (5 de octubre): el perfil drone_draft pasa al 50 % de la escena de 1920 x 1080 y se activa use_persistent_data
(no cambia la imagen; evita recargar la geometría estática en cada cuadro). Con 4 núcleos, unos 41 s por cuadro.
render_plan reanuda: los cuadros ya hechos con la misma configuración no se repiten.

Uso, desde 01_blender/herramientas:
  uv run --python 3.13 --with bpy==5.2.2 python render_dron_cpu.py -- --mode drone --profile draft --allow-cpu \
      --out ../renders_video --revision a454d3c_frente --frame-start 1 --frame-end 150
"""
import sys
from pathlib import Path

import bpy

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
args = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=str(RAIZ / "uyuni_v2.blend"))
bpy.data.scenes["UYUNI_DIA"].render.use_persistent_data = True
from herramientas import render_plan  # noqa: E402  (necesita el archivo abierto)

render_plan.PROFILES["drone_draft"]["percent"] = 50
render_plan.main(args)
