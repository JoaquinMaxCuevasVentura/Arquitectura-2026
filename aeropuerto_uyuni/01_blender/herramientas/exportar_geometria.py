"""Exporta la geometría evaluada de una escena (con modificadores e instancias) a un .npz, sin renderizar.

Lo usa superponer_cad_2d.py para dibujar cortes y alzados del modelo sobre los DXF del cliente.
Guarda, por objeto visible en el render: vértices en coordenadas de mundo (float32), triángulos, nombre y colección.

Uso:
  python exportar_geometria.py -- ../uyuni_v2.blend /tmp/geometria.npz [ESCENA]      (módulo bpy 5.2, Python 3.13)
  blender -b -P exportar_geometria.py -- ../uyuni_v2.blend /tmp/geometria.npz
"""
import sys

import bpy
import numpy as np

args = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=args[0])
sc = bpy.data.scenes[args[2] if len(args) > 2 else "UYUNI_DIA"]
if bpy.context.window:
    bpy.context.window.scene = sc
vl = sc.view_layers[0]
vl.update()
dg = vl.depsgraph
datos, nombres, colecciones = {}, [], []
for inst in dg.object_instances:
    ob = inst.object
    if ob.type != "MESH":
        continue
    orig = ob.original
    if orig.hide_render or any(c.hide_render for c in orig.users_collection):
        continue
    me = ob.to_mesh()
    me.calc_loop_triangles()
    n = len(me.vertices)
    if n and len(me.loop_triangles):
        co = np.empty(n * 3, dtype=np.float32)
        me.vertices.foreach_get("co", co)
        m = np.array(inst.matrix_world, dtype=np.float64)
        cw = (np.c_[co.reshape(-1, 3), np.ones(n)] @ m.T)[:, :3].astype(np.float32)
        tri = np.empty(len(me.loop_triangles) * 3, dtype=np.int32)
        me.loop_triangles.foreach_get("vertices", tri)
        k = len(nombres)
        datos[f"v{k}"], datos[f"t{k}"] = cw, tri.reshape(-1, 3)
        nombres.append(orig.name)
        colecciones.append(orig.users_collection[0].name if orig.users_collection else "")
    ob.to_mesh_clear()
datos["nombres"], datos["colecciones"] = np.array(nombres), np.array(colecciones)
np.savez_compressed(args[1], **datos)
print("[OK]", len(nombres), "objetos ->", args[1])
