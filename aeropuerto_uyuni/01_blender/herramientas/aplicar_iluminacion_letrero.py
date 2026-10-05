"""Actualiza solo el letrero nocturno sobre un .blend existente.

Uso: blender --factory-startup -b --python aplicar_iluminacion_letrero.py -- entrada.blend salida.blend
Conserva geometría, cámaras, animación, materiales y ajustes de las escenas existentes.
"""
from array import array
import hashlib
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from continuacion import letrero_nocturno


def geometry():
    result = {}
    for obj in bpy.data.objects:
        if obj.type not in ('MESH', 'CAMERA') or obj.get('UY_OWNER') == letrero_nocturno.OWNER:
            continue
        row = {'matrix': [list(r) for r in obj.matrix_world],
               'action': obj.animation_data.action.name if obj.animation_data and obj.animation_data.action else None,
               'materials': [slot.material.name if slot.material else None for slot in obj.material_slots],
               'modifiers': [(m.name, m.type) for m in obj.modifiers]}
        if obj.type == 'MESH':
            vertices = array('f', [0]) * (len(obj.data.vertices) * 3)
            loops = array('i', [0]) * len(obj.data.loops)
            obj.data.vertices.foreach_get('co', vertices)
            obj.data.loops.foreach_get('vertex_index', loops)
            digest = hashlib.sha256(vertices.tobytes() + loops.tobytes()).hexdigest()
            row.update(mesh_sha256=digest, vertices=len(obj.data.vertices), polygons=len(obj.data.polygons))
        else:
            row.update(lens=obj.data.lens, shift=[obj.data.shift_x, obj.data.shift_y])
        result[obj.name] = row
    return result


args = sys.argv[sys.argv.index('--') + 1:]
source, target = [Path(p).resolve() for p in args[:2]]
if source == target:
    raise RuntimeError('Escribe una copia y revisa la validación antes de reemplazar el original')
bpy.ops.wm.open_mainfile(filepath=str(source))
before = geometry()
lights_before = {o.name: (o.data.energy, list(o.location), list(o.rotation_euler)) for o in bpy.data.objects
                 if o.type == 'LIGHT' and o.get('UY_OWNER') != letrero_nocturno.OWNER}
scene_settings = {s.name: (s.view_settings.exposure, s.camera.name if s.camera else None,
                          s.world.name if s.world else None, s.render.resolution_x, s.render.resolution_y)
                  for s in bpy.data.scenes}
report = letrero_nocturno.aplicar()
counts = (len(bpy.data.objects), len(bpy.data.lights), len(bpy.data.collections), len(bpy.data.scenes))
letrero_nocturno.aplicar()
assert counts == (len(bpy.data.objects), len(bpy.data.lights), len(bpy.data.collections), len(bpy.data.scenes)), 'No es idempotente'
assert geometry() == before, 'Se alteró la geometría, los materiales asignados, la cámara o la animación'
assert lights_before == {n: (bpy.data.objects[n].data.energy, list(bpy.data.objects[n].location),
                            list(bpy.data.objects[n].rotation_euler)) for n in lights_before}, 'Cambió otra iluminación'
assert scene_settings == {n: (bpy.data.scenes[n].view_settings.exposure,
                              bpy.data.scenes[n].camera.name if bpy.data.scenes[n].camera else None,
                              bpy.data.scenes[n].world.name if bpy.data.scenes[n].world else None,
                              bpy.data.scenes[n].render.resolution_x, bpy.data.scenes[n].render.resolution_y)
                          for n in scene_settings}, 'Cambió la cámara, exposición o ajustes del render'
assert all(letrero_nocturno.COLLECTION not in s.collection.children for s in bpy.data.scenes if 'DIA' in s.name), 'Luz nueva en escena diurna'
report.update(source=str(source), output=str(target), geometry_verified=len(before), idempotent=True,
              other_lights_preserved=len(lights_before), existing_scene_settings_preserved=True)
embedded = bpy.data.texts.get('CONTINUACION_CODEX.json')
if embedded:
    record = json.loads(embedded.as_string())
    record['letrero_nocturno'] = report
    record['decisiones_pendientes'] = [item for item in record.get('decisiones_pendientes', [])
                                      if not item.startswith('Letrero nocturno:')]
    embedded.clear()
    embedded.write(json.dumps(record, ensure_ascii=False, indent=2))
target.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(target), compress=True)
target.with_suffix('.iluminacion.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('LETRERO_ACTUALIZADO', json.dumps(report, ensure_ascii=False), flush=True)
