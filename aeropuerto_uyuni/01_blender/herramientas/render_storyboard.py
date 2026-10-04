"""Render por planos del programa de 120 s, con reanudación verificable.

blender -b uyuni_v2.blend -P herramientas/render_storyboard.py -- --out renders_video
  --proposal P1/P2 --draft --start 1 --end 2880 --width 3840 --exr
Sin --draft: 512 muestras / ruido .01 / OIDN / motion blur .5 / 4K 24 fps.
El master VSE permite revisar los cortes; este script renderiza cada escena
directamente para no interpolar cámaras ni duplicar gestión de color.
"""
import argparse
import hashlib
from pathlib import Path
import sys

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from continuacion import materiales
from herramientas import render_plan


def main():
    argv=sys.argv[sys.argv.index("--")+1:]
    p=argparse.ArgumentParser();p.add_argument("--out",required=True)
    p.add_argument("--proposal",choices=["P1","P2"],default="P1")
    p.add_argument("--start",type=int,default=1);p.add_argument("--end",type=int,default=2880)
    p.add_argument("--width",type=int,default=3840);p.add_argument("--draft",action="store_true")
    p.add_argument("--samples",type=int);p.add_argument("--raw",action="store_true")
    p.add_argument("--exr",action="store_true");p.add_argument("--check",action="store_true")
    a=p.parse_args(argv)
    if not 1<=a.start<=a.end<=2880:raise ValueError("Cuadros fuera del programa 1..2880")
    out=Path(a.out).resolve()/a.proposal;out.mkdir(parents=True,exist_ok=True)
    master=bpy.data.scenes["UYUNI_VIDEO_MASTER_120S"]
    strips=sorted(master.sequence_editor.strips,key=lambda s:s.frame_final_start)
    source_hash=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
    if a.check:
        print("[STORYBOARD]",[(s.name,s.frame_final_start,s.frame_final_end-1) for s in strips]);return
    device,info=render_plan.select_device()
    materiales.aplicar({"profile":"DRON"})
    manifest_path=out/"manifest.json";manifest=render_plan.read_manifest(manifest_path)
    for strip in strips:
        sc=strip.scene;start=max(a.start,sc.frame_start);end=min(a.end,sc.frame_end)
        if end<start:continue
        if sc.get("UY_PLANO") not in (1,10):
            sc["propuesta"]=int(a.proposal=="P2")
            sc["letras_corten"]=int(a.proposal=="P1");sc["letras_gris"]=int(a.proposal=="P2")
        bpy.context.window.scene=sc
        cfg=render_plan.apply_profile(sc,"drone_draft" if a.draft else "drone",device=device,
                                      transparent_bounces=16,animated=True,denoise=not a.raw,motion_blur=True)
        if a.samples:sc.cycles.samples=a.samples
        sc.render.resolution_x=a.width;sc.render.resolution_y=round(a.width*9/16)
        sc.render.resolution_percentage=100
        sc.compositing_node_group=None if sc.get("UY_PLANO")==10 else render_plan.make_optics(sc,width=a.width,animated=True)
        render_plan.pass_settings(sc,enabled=a.exr)
        for f in range(start,end+1):
            sc.frame_set(f)
            spec={"blend_sha256":source_hash,"proposal":a.proposal,"frame":f,"scene":sc.name,
                  "cfg":cfg,"samples":sc.cycles.samples,"width":a.width,"raw":a.raw,
                  "gpu":info,"camera":list(sc.camera.location),"rotation":list(sc.camera.rotation_quaternion)}
            render_plan.measured_render(sc,out/f"VIDEO_{f:04d}",spec,manifest,manifest_path,exr=a.exr,jpeg=False)


if __name__=="__main__":main()
