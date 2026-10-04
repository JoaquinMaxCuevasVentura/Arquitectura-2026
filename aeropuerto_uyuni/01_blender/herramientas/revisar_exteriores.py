"""Planta y vistas comparativas del trazado de llegada, sin guardar la escena."""
import argparse
from pathlib import Path
import sys

import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from continuacion import materiales
from herramientas import render_plan


def main():
    argv=sys.argv[sys.argv.index("--")+1:]
    p=argparse.ArgumentParser();p.add_argument("archivo");p.add_argument("--baseline",required=True)
    p.add_argument("--out",required=True);a=p.parse_args(argv)
    current=Path(a.archivo).resolve();base=Path(a.baseline).resolve();out=Path(a.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    for stage,file in (("antes",base),("actual",current)):
        bpy.ops.wm.open_mainfile(filepath=str(file));render_plan.select_device()
        materiales.aplicar({"profile":"DRON"})
        bpy.data.objects["UY_SOL_MANANA"].data.energy=2.7
        for sc in bpy.data.scenes:
            if sc.world and "CREPUSCULO" not in sc.name:
                for n in sc.world.node_tree.nodes:
                    if n.type=="BACKGROUND":n.inputs["Strength"].default_value=.108
        for proposal,name in (("P1","UYUNI_DIA"),("P2","UYUNI_DIA_P2_SALAR_LITIO")):
            sc=bpy.data.scenes[name];bpy.context.window.scene=sc
            data=bpy.data.cameras.new("REVISION_EXTERIORES");cam=bpy.data.objects.new(data.name,data);sc.collection.objects.link(cam)
            cam.location=(110,-68,55);target=Vector((41,0,2.5))
            cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
            data.lens=30;data.clip_end=60000;sc.camera=cam
            render_plan.apply_profile(sc,"draft",device="GPU",transparent_bounces=16)
            sc.cycles.samples=96;sc.cycles.adaptive_threshold=.03
            sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage=1600,900,100
            render_plan.set_image(sc)
            sc.compositing_node_group=render_plan.make_optics(sc,width=1600)
            sc.render.filepath=str(out/f"exteriores_{proposal}_{stage}.png")
            bpy.ops.render.render(write_still=True,scene=sc.name)
            if stage=="actual" and proposal=="P1":
                data.type="ORTHO";data.ortho_scale=123
                cam.location=(41,-5,130);cam.rotation_euler=(0,0,0)
                sc.render.resolution_x,sc.render.resolution_y=1600,1200
                sc.compositing_node_group=None
                sc.render.filepath=str(out/"planta_exteriores_actual.png")
                bpy.ops.render.render(write_still=True,scene=sc.name)


if __name__=="__main__":main()
