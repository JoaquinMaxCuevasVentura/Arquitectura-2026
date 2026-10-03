"""Genera uyuni_v2.blend desde uyuni_modelo.py sin abrir la interfaz de Blender.

Uso (cualquiera de las dos formas):
  blender -b -P construir_blend.py -- ../uyuni_modelo.py ../uyuni_v2.blend
  python construir_blend.py -- ../uyuni_modelo.py ../uyuni_v2.blend     (con el módulo bpy: pip install bpy==5.2.2, Python 3.13)
"""
import os
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[-2:]
script, salida = (os.path.abspath(a) for a in args[:2])

# parte de una escena vacía (sin el cubo, la luz ni la cámara de inicio)
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# __file__ hace que el script cargue también las vistas del CAD en _REF_CAD
exec(open(script, encoding="utf-8").read(), {"__file__": script, "__name__": "__main__"})

vacia = bpy.data.collections.get("Collection")     # la colección vacía del archivo de inicio
if vacia and not vacia.all_objects:
    bpy.data.collections.remove(vacia)
dia = bpy.data.scenes["UYUNI_DIA"]
if bpy.context.window:
    bpy.context.window.scene = dia
bpy.ops.wm.save_as_mainfile(filepath=salida, compress=True)
print("[OK] guardado", salida)
