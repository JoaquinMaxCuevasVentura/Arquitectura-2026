"""Verifica o une MP4 locales en Blender, sin importar el modelo ni modificarlo.

blender --factory-startup -b -P video_media.py -- trabajo.json
El JSON define action=verify/assemble, files=[{path,frames}], width, height,
fps, report, output (assemble) y source_pngs (verify).
output_width/output_height permiten reducir la resolución sin recortar el encuadre.
"""
import json
from pathlib import Path
import sys
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from herramientas import render_plan


def main(spec):
    scene = bpy.data.scenes.new('UY_VIDEO_MEDIA_LOCAL')
    if bpy.context.window:
        bpy.context.window.scene = scene
    scene.render.resolution_x = spec.get('output_width', spec['width'])
    scene.render.resolution_y = spec.get('output_height', spec['height'])
    scene.render.resolution_percentage = 100
    editor = scene.sequence_editor_create()
    reports = []; cursor = 1
    for item in spec['files']:
        path = Path(item['path']).resolve()
        if not path.is_file() or not path.stat().st_size:
            raise RuntimeError(f'Video ausente: {path}')
        strip = editor.strips.new_movie(path.stem, str(path), channel=1, frame_start=cursor)
        size = [strip.elements[0].orig_width, strip.elements[0].orig_height]
        strip.transform.scale_x = scene.render.resolution_x / size[0]
        strip.transform.scale_y = scene.render.resolution_y / size[1]
        frames = strip.frame_duration
        if size != [spec['width'], spec['height']] or frames != item['frames'] or strip.fps != spec['fps']:
            raise RuntimeError(f'Media fuera del plan: {path}, {size}, {frames}, {strip.fps}')
        reports.append(dict(path=str(path), resolution=size, frames=frames, fps=strip.fps))
        cursor += frames
    render_plan.enum_set(scene.view_settings, 'view_transform', 'Standard')
    render_plan.enum_set(scene.view_settings, 'look', 'None')
    render_plan.enum_set(scene.sequencer_colorspace_settings, 'name', 'sRGB')
    scene.view_settings.exposure, scene.view_settings.gamma = 0.0, 1.0
    render_plan.enum_set(scene.render, 'engine', 'CYCLES')
    render_plan.enum_set(scene.cycles, 'device', 'CPU')
    render_plan.enum_set(scene.render, 'compositor_device', 'CPU')
    scene.render.use_sequencer = True
    scene.render.resolution_x = spec.get('output_width', spec['width'])
    scene.render.resolution_y = spec.get('output_height', spec['height'])
    scene.render.resolution_percentage = 100
    scene.render.fps, scene.render.fps_base = spec['fps'], 1.0
    scene.frame_start, scene.frame_end = 1, cursor-1
    if spec['action'] == 'assemble':
        target = Path(spec['output']).resolve(); target.parent.mkdir(parents=True, exist_ok=True)
        render_plan.enum_set(scene.render.image_settings, 'media_type', 'VIDEO')
        render_plan.enum_set(scene.render.image_settings, 'file_format', 'FFMPEG')
        for key, value in dict(format='MPEG4', codec='H264', constant_rate_factor='HIGH', ffmpeg_preset='GOOD').items():
            render_plan.enum_set(scene.render.ffmpeg, key, value)
        scene.render.filepath = str(target)
        bpy.ops.render.render(animation=True, scene=scene.name)
        if not target.is_file() or not target.stat().st_size:
            raise RuntimeError('No se produjo el montaje')
    elif spec['action'] == 'verify':
        render_plan.set_image(scene)
        previews = []
        for sample in spec.get('source_pngs', []):
            target = Path(sample['decoded']).resolve(); target.parent.mkdir(parents=True, exist_ok=True)
            scene.frame_set(sample['video_frame'])
            scene.render.filepath = str(target)
            bpy.ops.render.render(write_still=True, scene=scene.name)
            previews.append(dict(source=sample['source'], decoded=str(target), video_frame=sample['video_frame']))
    else:
        raise ValueError('Acción de media desconocida')
    result = dict(verified=True, files=reports, frames=cursor-1, fps=spec['fps'],
                  seconds=(cursor-1)/spec['fps'], resolution=[scene.render.resolution_x, scene.render.resolution_y],
                  samples=previews if spec['action']=='verify' else [])
    render_plan.atomic_json(Path(spec['report']), result)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--')+1:]
    main(json.loads(Path(args[0]).read_text(encoding='utf-8')))
