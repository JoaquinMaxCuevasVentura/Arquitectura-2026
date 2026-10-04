"""Comparaciones a igual cámara y luz; no guarda las opciones sobre el blend."""
import argparse
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from continuacion import materiales, camaras
from herramientas import render_plan
from herramientas.validar_continuacion import render


def main():
    argv=sys.argv[sys.argv.index("--")+1:]
    p=argparse.ArgumentParser();p.add_argument("archivo");p.add_argument("--baseline",required=True)
    p.add_argument("--out",required=True);p.add_argument("--width",type=int,default=1280)
    p.add_argument("--samples",type=int,default=96)
    a=p.parse_args(argv);out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
    current=str(Path(a.archivo).resolve());old=str(Path(a.baseline).resolve());times={}
    for stage,path in (("antes",old),("despues",current)):
        bpy.ops.wm.open_mainfile(filepath=path);render_plan.select_device()
        sun=bpy.data.objects["UY_SOL_MANANA"];sun.data.energy=2.7
        for sc in bpy.data.scenes:
            if sc.world and "CREPUSCULO" not in sc.name:
                for n in sc.world.node_tree.nodes:
                    if n.type=="BACKGROUND":n.inputs["Strength"].default_value=.108
        if stage=="despues":materiales.aplicar({"profile":"DRON"})
        for proposal,name in (("P1","UYUNI_DIA"),("P2","UYUNI_DIA_P2_SALAR_LITIO")):
            sc=bpy.data.scenes[name];sc.camera=bpy.data.objects["CAM_07_PROPUESTAS"]
            key=f"fachada_{proposal}_{stage}.png"
            times[key]=render(sc,out/key,a.width,a.samples)
    # Se reabre el archivo para que los ensayos no afecten al diseño aprobado.
    bpy.ops.wm.open_mainfile(filepath=current);render_plan.select_device()
    materiales.aplicar({"profile":"DRON"})
    sc=bpy.data.scenes["UYUNI_DIA"]
    for tag,name in (("CAM05","CAM_05_LETRERO_HORIZONTE"),("CAM07","CAM_07_PROPUESTAS")):
        sc.camera=bpy.data.objects[name]
        key=f"vidrio_{tag}_aprobado_6E808E.png";times[key]=render(sc,out/key,a.width,a.samples)
        with materiales.glass_comparison("#A9BCCB",shadow_transparent=False):
            key=f"vidrio_{tag}_alternativa_A9BCCB.png";times[key]=render(sc,out/key,a.width,a.samples)
    sc.camera=bpy.data.objects["CAM_07_PROPUESTAS"]
    times["falsecolor_dia.png"]=render(sc,out/"falsecolor_dia.png",a.width,a.samples,false_color=True)
    night=bpy.data.scenes["UYUNI_CREPUSCULO"]
    for method in ("legacy","halo","wash"):
        # Alternativas con letras Corten aprobadas: se evalúa solo la iluminación.
        night["letras_corten"]=0 if method=="legacy" else 1
        night["letras_gris"]=0;night["luz_letrero"]=2.5 if method=="legacy" else 0
        camaras.sign_candidates(night,dict(camaras.DEFAULTS,night_sign_method=method,night_sign_energy=80))
        key="noche_"+method+".png";times[key]=render(night,out/key,a.width,a.samples)
    night["letras_corten"]=0;night["luz_letrero"]=2.5
    camaras.sign_candidates(night,dict(camaras.DEFAULTS,night_sign_method="legacy"))
    times["falsecolor_noche.png"]=render(night,out/"falsecolor_noche.png",a.width,a.samples,false_color=True)
    (out/"tiempos_comparaciones.json").write_text(json.dumps(times,indent=2),encoding="utf-8")


if __name__=="__main__":main()
