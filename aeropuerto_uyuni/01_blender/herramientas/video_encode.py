"""Convierte un bloque PNG16 en MP4 y lo entrega en la salida configurada.

blender --factory-startup -b -P video_encode.py -- trabajo.json
Solo trabaja con el bloque recién renderizado; nunca guarda el modelo.
"""
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from herramientas import render_plan


def main(spec):
    directory = Path(spec['directory']).resolve()
    target = Path(spec['output']).resolve()
    encoded = Path(render_plan.encode_sequence(directory, spec['start'], spec['end'],
        overwrite=True, prefix='VIDEO_', video_name=target.name,
        input_fingerprint=spec['fingerprint']))
    target.parent.mkdir(parents=True, exist_ok=True)
    if encoded != target:
        shutil.copy2(encoded, target)
        metadata = json.loads(encoded.with_suffix('.json').read_text(encoding='utf-8'))
        metadata['output'] = str(target)
        render_plan.atomic_json(target.with_suffix('.json'), metadata)
        encoded.unlink()
        encoded.with_suffix('.json').unlink()
    print(json.dumps(dict(output=str(target), bytes=target.stat().st_size)), flush=True)


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--')+1:]
    main(json.loads(Path(args[0]).read_text(encoding='utf-8')))
