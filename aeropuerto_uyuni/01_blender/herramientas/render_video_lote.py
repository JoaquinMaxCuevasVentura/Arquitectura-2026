"""Lote local por tomas, con bloques verificados y limpieza de PNG temporales.

Python externo a Blender: python render_video_lote.py configuracion.json
La configuración apunta a una fuente y código congelados, trabajo temporal,
salidas MP4 y lista de tomas. No altera el .blend ni los archivos del cliente.
"""
from datetime import datetime
import ctypes
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import time

import numpy as np
from PIL import Image


def now():
    return datetime.now().astimezone().isoformat()


def atomic(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name+'.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temp, path)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path, default=None):
    return json.loads(Path(path).read_text(encoding='utf-8')) if Path(path).is_file() else default


class Paused(Exception):
    pass


class Batch:
    def __init__(self, config):
        self.cfg = config
        self.root = Path(config['work_root']).resolve()
        self.output = Path(config['output_root']).resolve()
        self.temp = Path(config.get('temporary_root', self.root/'temporales')).resolve()
        if not (self.temp.is_relative_to(self.root) or self.temp.is_relative_to(self.output)):
            raise RuntimeError('Temporales fuera de las carpetas de producción')
        self.logs = self.root/'logs'; self.logs.mkdir(parents=True, exist_ok=True)
        self.output.mkdir(parents=True, exist_ok=True); self.temp.mkdir(parents=True, exist_ok=True)
        self.state_path = self.root/'estado.json'
        self.state = read(self.state_path, dict(status='ready', started=now(), jobs={}, chunks={}))
        fingerprint = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
        if self.state.get('config_sha256', fingerprint) != fingerprint:
            raise RuntimeError('La configuración cambió: use otra carpeta de producción')
        self.state.update(config_sha256=fingerprint, total_jobs=len(config['jobs']), pid=os.getpid())
        self.lock = (self.root/'lote.lock').open('a+b')
        if os.name == 'nt':
            import msvcrt
            if not self.lock.tell(): self.lock.write(b'0'); self.lock.flush()
            self.lock.seek(0); msvcrt.locking(self.lock.fileno(), msvcrt.LK_NBLCK, 1)
        for job in config['jobs']:
            self.state['jobs'].setdefault(job['id'], dict(status='pending', name=job['name'], frames=job['frames']))

    def save(self):
        self.state['updated'] = now()
        self.state['completed_jobs'] = sum(v['status']=='complete' for v in self.state['jobs'].values())
        self.state['denoising_device'] = 'GPU' if self.cfg.get('denoise_gpu') else 'CPU'
        self.state['samples'] = self.cfg['samples']
        atomic(self.state_path, self.state)
        rows = []
        for job in self.cfg['jobs']:
            item = self.state['jobs'][job['id']]
            link = f'<a href="{html.escape(Path(item["output"]).as_uri())}">MP4</a>' if item.get('output') else ''
            rows.append(f'<tr><td>{job["palette"]}</td><td>{html.escape(job["name"])}</td>'
                        f'<td>{job["frames"]/self.cfg["fps"]:g} s</td><td>{item["status"]}</td><td>{link}</td></tr>')
        current = html.escape(json.dumps(self.state.get('current', {}), ensure_ascii=False))
        document = ('<!doctype html><html lang=es><meta charset=utf-8><meta http-equiv=refresh content=30>'
            '<title>UYUNI · videos para Flow</title><style>body{font:16px system-ui;background:#f5f4ef;color:#24333b;'
            'max-width:1100px;margin:40px auto;padding:20px}td,th{text-align:left;padding:10px;border-bottom:1px solid #ccc}'
            'table{width:100%}pre{white-space:pre-wrap}</style><h1>UYUNI · videos por tomas para Flow</h1>'
            f'<p>{self.cfg["width"]} × {self.cfg["height"]} · {self.cfg["fps"]} fps · {self.cfg["samples"]} muestras · '
            f'reducción de ruido en {self.state["denoising_device"]} · '
            'sin acciones de personas ni vehículos. Toma 09 en hora azul.</p>'
            f'<p>Estado: {self.state["status"]}. Terminadas: {self.state["completed_jobs"]} / {self.state["total_jobs"]}.</p>'
            f'<pre>{current}</pre><table><tr><th>Propuesta</th><th>Toma</th><th>Duración</th><th>Estado</th><th>Archivo</th></tr>'
            + ''.join(rows) + '</table><p>Los bloques de hasta seis segundos están en la carpeta tramos. '
            'Los PNG son temporales y se liberan solo después de verificar el video.</p></html>')
        (self.root/'index.html').write_text(document, encoding='utf-8')

    def child(self, args, label, progress=None):
        if Path(self.cfg['pause_file']).exists(): raise Paused()
        self.state['current'] = dict(stage=label); self.save()
        with (self.logs/f'{label}.stdout.log').open('w', encoding='utf-8') as stdout, \
             (self.logs/f'{label}.stderr.log').open('w', encoding='utf-8') as stderr:
            process = subprocess.Popen([self.cfg['blender'], '--factory-startup', '-b', *args],
                stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL, shell=False,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            self.state['child_pid'] = process.pid
            while process.poll() is None:
                if progress:
                    try:
                        value = read(progress)
                        if value:
                            self.state['current'].update(frame=value.get('frame'),
                                frames_done=value.get('frames_done'), last_seconds=value.get('last_seconds'))
                    except (OSError, ValueError): pass
                self.save(); time.sleep(10)
            self.state.pop('child_pid', None)
            if process.returncode:
                raise RuntimeError(f'Blender falló en {label}, código {process.returncode}; ver logs')
        if progress and read(progress, {}).get('status') == 'paused': raise Paused()

    def media(self, spec, label):
        request = self.root/'control'/f'{label}.json'; atomic(request, spec)
        self.child(['--disable-autoexec', '--python-exit-code', '1', '-P', self.cfg['media_script'], '--', str(request)], label)
        result = read(spec['report'])
        if not result or not result['verified']: raise RuntimeError('Media no verificada')
        return result

    def verify(self, file, count, label, sources=()):
        samples = [dict(source=str(p), video_frame=f, decoded=str(self.temp/'decodificados'/f'{label}_{f:03d}.png'))
                   for f,p in dict(sources).items()]
        spec = dict(action='verify', files=[dict(path=str(file),frames=count)], width=self.cfg['width'],
            height=self.cfg['height'], fps=self.cfg['fps'], report=str(self.root/'control'/f'{label}_report.json'),
            source_pngs=samples)
        result = self.media(spec, label)
        comparisons = []
        for sample in samples:
            with Image.open(sample['source']) as source, Image.open(sample['decoded']) as decoded:
                a=np.asarray(source.convert('RGB').resize((512,288)),dtype=float)
                b=np.asarray(decoded.convert('RGB').resize((512,288)),dtype=float)
            error = float(np.abs(a-b).mean())
            if error > 5.0: raise RuntimeError(f'Video distinto del PNG en {label}: {error}')
            comparisons.append(dict(frame=sample['video_frame'], rgb_difference=error))
            Path(sample['decoded']).unlink()
        result['decoded_comparisons'] = comparisons
        atomic(spec['report'], result)
        return result

    def cleanup(self, directory, start, end):
        directory = Path(directory).resolve()
        if not directory.is_relative_to(self.temp): raise RuntimeError('Limpieza fuera de temporales')
        for frame in range(start,end+1):
            path=(directory/f'VIDEO_{frame:04d}.png').resolve()
            if not path.is_relative_to(self.temp): raise RuntimeError('PNG fuera de temporales')
            if path.is_file(): path.unlink()

    def assemble(self, files, target, label):
        if len(files)==1:
            shutil.copy2(files[0]['path'], target)
        else:
            self.media(dict(action='assemble',files=files,width=self.cfg['width'],height=self.cfg['height'],
                fps=self.cfg['fps'],output=str(target),report=str(self.root/'control'/f'{label}_assemble.json')),label)
        return self.verify(target, sum(f['frames'] for f in files), label+'_verify')

    def job(self, job):
        record = self.state['jobs'][job['id']]
        if record['status']=='complete':
            if sha(record['output']) != record['sha256']: raise RuntimeError('Entrega existente cambió')
            return
        target_dir=self.output/job['palette']; target_dir.mkdir(parents=True,exist_ok=True)
        target=target_dir/f'UYUNI_{job["palette"]}_Toma_{job["shot"]:02d}.mp4'
        if job.get('reuse'):
            first=self.state['jobs'][job['reuse']]
            if first['status']!='complete': raise RuntimeError('Toma común no terminada')
            shutil.copy2(first['output'],target)
            chunks=[]
            for item in first['chunks']:
                new_path=self.output/job['palette']/'tramos'/f'toma_{job["shot"]:02d}'/Path(item['path']).name.replace('P1','P2')
                new_path.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(item['path'],new_path)
                chunks.append(dict(path=str(new_path),frames=item['frames']))
            record.update(status='complete',output=str(target),sha256=sha(target),chunks=chunks,shared_scene=True)
            self.save(); return
        record['status']='running'; self.save(); chunks=[]
        for block,start in enumerate(range(job['start'],job['end']+1,self.cfg['chunk_frames']),1):
            end=min(job['end'],start+self.cfg['chunk_frames']-1); count=end-start+1
            label=f'{job["id"]}_bloque_{block:02d}'
            temp_out=self.temp/label; frames_dir=temp_out/job['palette']/f'toma_{job["shot"]:02d}'
            destination=target_dir/'tramos'/f'toma_{job["shot"]:02d}'/f'{label}.mp4'
            previous=self.state['chunks'].get(label)
            if previous and previous['status']=='complete':
                if sha(destination)!=previous['sha256']: raise RuntimeError('Bloque existente cambió')
                self.cleanup(frames_dir,start,end)
                chunks.append(dict(path=str(destination),frames=count)); continue
            if shutil.disk_usage(self.temp).free < self.cfg['min_free_bytes']:
                raise RuntimeError('Espacio insuficiente para el siguiente bloque temporal')
            args=[self.cfg['source'],'--disable-autoexec','--python-exit-code','1','-P',self.cfg['render_script'],
                '--','--out',str(temp_out),'--proposal',job['palette'],'--shot',str(job['shot']),
                '--start',str(start),'--end',str(end),'--width',str(self.cfg['width']),
                '--samples',str(self.cfg['samples']),'--persistent-data','--pause-file',self.cfg['pause_file']]
            if self.cfg.get('denoise_gpu'): args.append('--denoise-gpu')
            for attempt in range(1,self.cfg.get('gpu_retries',0)+2):
                attempt_label=label if attempt==1 else f'{label}_reintento_{attempt-1}'
                try:
                    self.child(args,attempt_label,temp_out/job['palette']/'estado.json')
                    break
                except RuntimeError as exc:
                    log='\n'.join((self.logs/f'{attempt_label}.{suffix}.log').read_text(encoding='utf-8',errors='replace')
                        for suffix in ('stdout','stderr'))
                    if attempt>self.cfg.get('gpu_retries',0) or not any(token in log for token in
                            ('CUDA','OPTIX','OptiX','Launch failed','Out of memory')): raise
                    self.state.setdefault('gpu_retries',[]).append(dict(stage=attempt_label,error=str(exc),time=now()))
                    self.save(); time.sleep(10)
            manifest=read(frames_dir/'manifest.json'); expected=[]
            for frame in range(start,end+1):
                png=frames_dir/f'VIDEO_{frame:04d}.png'
                with png.open('rb') as stream: header=stream.read(29)
                if header[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack('>II',header[16:24])!=(self.cfg['width'],self.cfg['height']) or header[24]!=16:
                    raise RuntimeError('PNG fuera del plan')
                key=str(png.with_suffix(''))
                if key not in manifest['jobs']: raise RuntimeError('PNG sin registro de render')
                expected.append(manifest['jobs'][key])
            destination.parent.mkdir(parents=True,exist_ok=True)
            # En el ensamblado las imágenes usan los números globales del guion.
            encode_spec=dict(directory=str(frames_dir),start=start,end=end,output=str(destination),
                fingerprint=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest())
            encode_request=self.root/'control'/f'{label}_encode.json'; atomic(encode_request,encode_spec)
            self.child(['--disable-autoexec','--python-exit-code','1','-P',self.cfg['encode_script'],'--',str(encode_request)],label+'_encode')
            samples=[(1,frames_dir/f'VIDEO_{start:04d}.png'),((count+1)//2,frames_dir/f'VIDEO_{start+(count-1)//2:04d}.png'),
                     (count,frames_dir/f'VIDEO_{end:04d}.png')]
            verification=self.verify(destination,count,label+'_verify',samples)
            self.state['chunks'][label]=dict(status='complete',path=str(destination),sha256=sha(destination),
                frames=count,render_seconds=sum(i['seconds'] for i in expected),verified=True)
            self.save()
            previews=self.output/'previews'; previews.mkdir(exist_ok=True)
            with Image.open(samples[1][1]) as image:
                image.convert('RGB').resize((1280,720)).save(previews/f'{label}.jpg',quality=92)
            self.cleanup(frames_dir,start,end)
            chunks.append(dict(path=str(destination),frames=count))
        self.assemble(chunks,target,job['id']+'_toma')
        record.update(status='complete',output=str(target),sha256=sha(target),chunks=chunks,finished=now())
        self.save()

    def run(self):
        if sha(self.cfg['source']) != self.cfg['source_sha256']: raise RuntimeError('La fuente congelada cambió')
        for path, fingerprint in self.cfg.get('code_sha256', {}).items():
            if sha(path) != fingerprint: raise RuntimeError(f'El código congelado cambió: {path}')
        self.state.pop('error', None)
        self.state['status']='running'; self.save()
        if os.name=='nt': ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
        try:
            for job in self.cfg['jobs']: self.job(job)
            for palette in ('P1','P2'):
                chunks=[c for j in self.cfg['jobs'] if j['palette']==palette for c in self.state['jobs'][j['id']]['chunks']]
                if not chunks: continue
                count=sum(c['frames'] for c in chunks)
                seconds=count/self.cfg['fps']
                target=self.output/palette/f'UYUNI_{palette}_{seconds:g}s.mp4'
                if palette not in self.state.get('masters',{}):
                    self.assemble(chunks,target,f'master_{palette}')
                    self.state.setdefault('masters',{})[palette]=dict(path=str(target),sha256=sha(target),frames=count,seconds=seconds)
                    self.save()
            self.state.update(status='complete',finished=now()); self.save()
        except Paused:
            self.state['status']='paused'; self.save()
        except Exception as exc:
            self.state.update(status='error',error=str(exc)); self.save(); raise
        finally:
            if os.name=='nt': ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
            self.lock.close()


if __name__=='__main__':
    Batch(read(sys.argv[1])).run()
