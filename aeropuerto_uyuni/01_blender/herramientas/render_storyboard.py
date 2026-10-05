"""Render por planos del programa de 120 s, con reanudación verificable.

blender -b uyuni_v2_lateral_zigzag.blend -P herramientas/render_storyboard.py --
  --out renders_video/revision --proposal P1 --shot 2 --keyframes --draft --width 1280
  --out renders_video/master --proposal P1 --shot 2 --width 3840 --encode
Sin --draft: 512 muestras / ruido .01 / OIDN / motion blur .5 / 4K 24 fps.
El master VSE permite revisar los cortes; este script renderiza cada escena
directamente para no interpolar cámaras ni duplicar gestión de color.
Cada toma tiene carpeta, manifiesto PNG16 y MP4 propio. --check escribe el plan
sin renderizar. --keyframes revisa inicio/mitad/final. --pause-file pausa antes
del siguiente fotograma; el que está en proceso termina y queda registrado.
"""
import argparse
import hashlib
from pathlib import Path
import sys

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from continuacion import materiales
from herramientas import render_plan


def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument("--out",required=True)
    p.add_argument("--proposal",choices=["P1","P2"],default="P1")
    p.add_argument("--start",type=int,default=1);p.add_argument("--end",type=int,default=2880)
    p.add_argument("--width",type=int,default=3840);p.add_argument("--draft",action="store_true")
    p.add_argument("--samples",type=int);p.add_argument("--raw",action="store_true")
    p.add_argument("--exr",action="store_true");p.add_argument("--check",action="store_true")
    p.add_argument("--shot",help="Tomas separadas por coma, p. ej. 2,3,9")
    p.add_argument("--keyframes",action="store_true")
    p.add_argument("--pause-file");p.add_argument("--encode",action="store_true")
    p.add_argument("--ffmpeg");p.add_argument("--force",action="store_true")
    p.add_argument("--persistent-data",action="store_true",help="Reutilizar datos de escena entre fotogramas")
    p.add_argument("--compositor-device",choices=["CPU","GPU"],default="CPU")
    p.add_argument("--denoise-gpu",action="store_true",help="OpenImageDenoise en GPU, misma calidad High/Accurate")
    a=p.parse_args(argv)
    if not 1<=a.start<=a.end<=2880:raise ValueError("Cuadros fuera del programa 1..2880")
    if a.width<320 or a.width%32:raise ValueError("Ancho >= 320, múltiplo de 32")
    if a.samples is not None and a.samples<1:raise ValueError("Muestras >= 1")
    if a.keyframes and a.encode:raise ValueError("MP4 requiere fotogramas consecutivos")
    selected={int(n) for n in a.shot.split(',')} if a.shot else set(range(1,11))
    if not selected or not selected<=set(range(1,11)):raise ValueError("Tomas válidas: 1..10")
    out=Path(a.out).resolve()/a.proposal;out.mkdir(parents=True,exist_ok=True)
    master=bpy.data.scenes["UYUNI_VIDEO_MASTER_120S"]
    strips=sorted(master.sequence_editor.strips,key=lambda s:s.frame_final_start)
    source_hash=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
    code_hash=render_plan.digest({str(q):hashlib.sha256(Path(q).read_bytes()).hexdigest()
        for q in (__file__,render_plan.__file__,materiales.__file__)})
    jobs=[];previous_end=0
    for strip in strips:
        sc=strip.scene;sid=int(sc["UY_PLANO"])
        if (strip.frame_final_start!=previous_end+1 or strip.frame_final_start!=sc.frame_start
            or strip.frame_final_end-1!=sc.frame_end or not sc.camera):
            raise RuntimeError("Montaje con huecos/solapes, rango distinto o sin cámara")
        previous_end=sc.frame_end
        start=max(a.start,sc.frame_start);end=min(a.end,sc.frame_end)
        if sid not in selected or end<start:continue
        frames=(sorted({sc.frame_start,(sc.frame_start+sc.frame_end)//2,sc.frame_end})
                if a.keyframes else range(start,end+1))
        frames=[f for f in frames if start<=f<=end]
        if not frames:continue
        jobs.append(dict(shot=sid,name=strip.name,scene=sc.name,camera=sc.camera.name,
            program_range=[sc.frame_start,sc.frame_end],render_range=[start,end],frames=frames,
            frame_count=len(frames),seconds=len(frames)/24,lighting=sc.get("UY_ESTADO_LUZ"),
            directory=str(out/f"toma_{sid:02d}")))
    if len(strips)!=10 or previous_end!=2880 or not jobs or master.render.fps!=24:
        raise RuntimeError("Se requiere montaje de 10 tomas, 2880 cuadros y 24 fps")
    plan=dict(source=bpy.data.filepath,blend_sha256=source_hash,code_sha256=code_hash,
        proposal=a.proposal,resolution=[a.width,a.width*9//16],fps=24,keyframes=a.keyframes,
        profile="drone_draft" if a.draft else "drone",samples=a.samples or (128 if a.draft else 512),
        denoising_device="GPU" if a.denoise_gpu else "CPU",jobs=jobs)
    render_plan.atomic_json(out/"plan.json",plan)
    print("[STORYBOARD]",[(j["name"],j["frame_count"]) for j in jobs],flush=True)
    if a.check:
        return plan
    baseline=render_plan.audit_signature()
    device,info=render_plan.select_device()
    materiales.aplicar({"profile":"DRON"})
    status=dict(status="running",hardware=info,frames_done=0,videos=[],
                denoising_device="GPU" if a.denoise_gpu else "CPU",samples=plan["samples"])
    render_plan.atomic_json(out/"estado.json",status)
    for job in jobs:
        sc=bpy.data.scenes[job["scene"]]
        if sc.get("UY_PLANO") not in (1,10):
            sc["propuesta"]=int(a.proposal=="P2")
            sc["letras_corten"]=int(a.proposal=="P1");sc["letras_gris"]=int(a.proposal=="P2")
        if bpy.context.window:bpy.context.window.scene=sc
        cfg=render_plan.apply_profile(sc,"drone_draft" if a.draft else "drone",device=device,
                                      transparent_bounces=16,animated=True,denoise=not a.raw,motion_blur=True)
        sc.cycles.samples=plan["samples"];cfg.update(samples=sc.cycles.samples,percent=100)
        render_plan.required_set(sc.cycles,"denoising_use_gpu",a.denoise_gpu)
        cfg["denoising_use_gpu"]=sc.cycles.denoising_use_gpu
        sc.render.resolution_x=a.width;sc.render.resolution_y=round(a.width*9/16)
        sc.render.resolution_percentage=100
        sc.render.fps,sc.render.fps_base=24,1.0;sc.render.use_sequencer=False
        render_plan.required_set(sc.render,"use_persistent_data",a.persistent_data)
        render_plan.enum_set(sc.render,"compositor_device",a.compositor_device)
        sc.compositing_node_group=None if sc.get("UY_PLANO")==10 else render_plan.make_optics(
            sc,night="CREPUSCULO" in sc.name,width=a.width,animated=True)
        render_plan.pass_settings(sc,enabled=a.exr)
        directory=Path(job["directory"]);manifest_path=directory/"manifest.json"
        manifest=render_plan.read_manifest(manifest_path)
        for f in job["frames"]:
            if a.pause_file and Path(a.pause_file).exists():
                if render_plan.audit_signature()!=baseline:raise RuntimeError("Cambió geometría CAD")
                status["status"]="paused";render_plan.atomic_json(out/"estado.json",status);return status
            sc.frame_set(f)
            spec={"blend_sha256":source_hash,"code_sha256":code_hash,"proposal":a.proposal,
                  "shot":job["shot"],"frame":f,"scene":sc.name,"cfg":cfg,"width":a.width,
                  "raw":a.raw,"exr":a.exr,"gpu":info,"optics_version":render_plan.OPTICS_VERSION,
                  "persistent_data":a.persistent_data,
                  "compositor_device":a.compositor_device,
                  "camera_matrix":[list(row) for row in sc.camera.matrix_world],
                  "lens":sc.camera.data.lens,"exposure":sc.view_settings.exposure}
            row=render_plan.measured_render(sc,directory/f"VIDEO_{f:04d}",spec,manifest,
                manifest_path,exr=a.exr,jpeg=False,resume=not a.force)
            status.update(shot=job["shot"],frame=f,last_seconds=row["seconds"])
            status["frames_done"]+=1;render_plan.atomic_json(out/"estado.json",status)
        if a.encode:
            status["videos"].append(render_plan.encode_sequence(directory,*job["render_range"],
                a.ffmpeg,a.force,prefix="VIDEO_",video_name=f"UYUNI_{a.proposal}_toma_{job['shot']:02d}.mp4",
                input_fingerprint=render_plan.digest(manifest)))
    if render_plan.audit_signature()!=baseline:raise RuntimeError("La geometría CAD auditada cambió")
    status["status"]="complete";render_plan.atomic_json(out/"estado.json",status)
    return status


if __name__=="__main__":main(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else sys.argv[1:])
