"""Ejecuta un plan validado en procesos separados de Blender, con registro de progreso.

python render_lote.py configuracion.json
Los archivos y opciones se toman de la configuración; nunca guarda el .blend.
Un archivo PAUSAR_DESPUES_ACTUAL.txt en la carpeta de control pausa entre imágenes.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import time


def escribir(path, data):
    temporal = path.with_suffix(path.suffix + ".tmp")
    temporal.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporal, path)


def ahora():
    return datetime.now(timezone.utc).isoformat()


def verificar_png(path):
    with path.open("rb") as stream:
        header = stream.read(29)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise RuntimeError(f"PNG inválido: {path}")
    width, height = struct.unpack(">II", header[16:24])
    if (width, height, header[24]) != (7680, 4320, 16):
        raise RuntimeError(f"Resolución/profundidad inesperada: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    config = json.loads(parser.parse_args().config.read_text(encoding="utf-8"))
    control = Path(config["control"])
    control.mkdir(parents=True, exist_ok=True)
    logs = control / "logs"
    logs.mkdir(exist_ok=True)
    temporal = control / "temporales"
    temporal.mkdir(exist_ok=True)
    plan = json.loads(Path(config["plan"]).read_text(encoding="utf-8"))
    source = Path(config["blend"])
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    state_path = control / "estado.json"
    state = dict(estado="iniciando", pid=os.getpid(), inicio=ahora(), fuente=str(source),
                 fuente_sha256=source_hash, total=plan["count"], terminados=[], actual=None)
    # El bloqueo desaparece al salir el proceso, incluso si Blender falla.
    lock = (control / "lote.lock").open("a+b")
    if os.name == "nt":
        import msvcrt
        lock.seek(0)
        if not lock.read(1):
            lock.write(b"0"); lock.flush()
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    try:
        escribir(state_path, state)
        env = dict(os.environ, PYTHONUNBUFFERED="1", TEMP=str(temporal), TMP=str(temporal))
        for job in plan["jobs"]:
            if (control / "PAUSAR_DESPUES_ACTUAL.txt").exists():
                state.update(estado="pausado", actual=None, actualizado=ahora())
                escribir(state_path, state)
                return
            if shutil.disk_usage(control).free < 2 * 1024 ** 3:
                raise RuntimeError("Quedan menos de 2 GB en el disco de renders")
            if hashlib.sha256(source.read_bytes()).hexdigest() != source_hash:
                raise RuntimeError("La fuente del lote cambió; se detiene para no mezclar revisiones")
            job_id = job["job_id"]
            state.update(estado="renderizando", actual=job_id, actualizado=ahora())
            escribir(state_path, state)
            command = [config["blender"], "--factory-startup", "-b", "--disable-autoexec", str(source),
                       "--python-exit-code", "1", "-P", config["render_script"], "--",
                       "--mode", "stills", *config["opciones"], "--only", job_id]
            print(f"[LOTE] {job_id}: inicio", flush=True)
            start = time.perf_counter()
            with (logs / (job_id + ".log")).open("w", encoding="utf-8") as log:
                result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, env=env,
                                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            if result.returncode != 0:
                raise RuntimeError(f"Blender falló en {job_id}: código {result.returncode}; revisar su log")
            output = Path(job["output"])
            verificar_png(output)
            manifest_path = output.parent / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if str(output.with_suffix("")) not in manifest["jobs"]:
                raise RuntimeError(f"Falta el registro de configuración de {job_id}")
            state["terminados"].append(dict(vista=job_id, archivo=str(output), segundos=round(time.perf_counter()-start, 2)))
            state.update(actual=None, actualizado=ahora())
            escribir(state_path, state)
            print(f"[LOTE] {job_id}: terminado ({len(state['terminados'])}/{state['total']})", flush=True)
        state.update(estado="completo", actual=None, fin=ahora())
        escribir(state_path, state)
    except Exception as exc:
        state.update(estado="error", error=str(exc), actualizado=ahora())
        escribir(state_path, state)
        raise
    finally:
        lock.close()


if __name__ == "__main__":
    main()
