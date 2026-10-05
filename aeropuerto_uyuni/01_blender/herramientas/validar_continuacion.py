"""Reabre el blend, compara geometría con la base y renderiza previs del guion.

blender -b --python-exit-code 1 -P validar_continuacion.py -- ARCHIVO --out DIR
Opcionales: --baseline BASE.blend --render --width 960 --samples 64 --only 1,9,10
"""
import argparse
import array
import hashlib
import json
from pathlib import Path
import sys
import time

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from herramientas import render_plan


def geometria():
    result={}
    for ob in bpy.data.objects:
        if ob.type!="MESH": continue
        coords=array.array('f',[0])*(len(ob.data.vertices)*3)
        ob.data.vertices.foreach_get("co",coords)
        edges=array.array('i',[0])*(len(ob.data.loops))
        ob.data.loops.foreach_get("vertex_index",edges)
        digest=hashlib.sha256(coords.tobytes()+edges.tobytes()+str(tuple(map(tuple,ob.matrix_world))).encode()).hexdigest()
        result[ob.name]=digest
    return result


def validar(baseline=None):
    report={"version":bpy.app.version_string,"objetos":len(bpy.data.objects),
            "camaras":sum(o.type=="CAMERA" for o in bpy.data.objects),
            "escenas":[s.name for s in bpy.data.scenes],"geometria":{},"planos":[]}
    if baseline:
        actual=geometria()
        rear={"UY_FACHADA_AIRE_EJE_I","UY_CARPINTERIAS_AIRE_PERFILES","UY_CARPINTERIAS_AIRE_VIDRIOS",
              "UY_PUERTAS_AIRE_ACERO","UY_ENROLLABLES_AIRE_CORTINAS","UY_ENROLLABLES_AIRE_GUIAS",
              "UY_NICHO_AIRE","UY_NICHO_AIRE_COSTADO_ESTE","UY_INTERIOR_AIRE_PISOS","UY_INTERIOR_AIRE_LUZ"}
        allowed={"UY_PAJA_BRAVA_DISPERSION"} | rear
        allowed.update(name for name in baseline if name.startswith(("UY_4x4_04_ESTAC","UY_4x4_05_ESTAC")))
        # Frente del Lado Tierra restituido de las capturas del cliente (5 de octubre): asfalto, pintura, jardineras
        # y plaza; el proxy 4x4_03 pasa al segundo carril. Fachada, vereda A111 y calles laterales no cambian.
        allowed.update(name for name in baseline if name.startswith(("UY_FRENTE_","UY_ISLAS_","UY_CALZADA_ASFALTO",
                                                                     "UY_SENALIZACION_VIAL","UY_4x4_03")))
        changed=[name for name,h in baseline.items() if actual.get(name)!=h and name not in allowed]
        report["geometria"]={"mallas_base":len(baseline),"modificadas_o_faltantes":changed,
                             "cambios_exteriores_autorizados":[name for name in allowed-rear if actual.get(name)!=baseline.get(name)],
                             "cambios_fachada_trasera_autorizados":[name for name in sorted(rear) if actual.get(name)!=baseline.get(name)]}
        if changed: raise RuntimeError("Cambió geometría base: "+str(changed))
    master=bpy.data.scenes["UYUNI_VIDEO_MASTER_120S"]
    assert (master.frame_start,master.frame_end,master.render.fps)==(1,2880,24)
    strips=sorted(master.sequence_editor.strips,key=lambda s:s.frame_final_start)
    assert len(strips)==10
    assert [(s.frame_final_start,s.frame_final_end) for s in strips]==[(1,289),(289,625),(625,961),(961,1249),(1249,1537),(1537,1873),(1873,2209),(2209,2545),(2545,2737),(2737,2881)]
    for strip in strips:
        sc=strip.scene; cam=sc.camera; positions=[]
        # Prueba todos los cuadros, no solo los keyframes extremos.
        # El envolvente principal se verifica como zona de exclusión conservadora.
        inside=[]
        for f in range(sc.frame_start,sc.frame_end+1):
            sc.frame_set(f); p=cam.location
            if 0<p.x<82.51 and 0<p.y<48.32 and 0<p.z<13.024 and sc.get("UY_PLANO") not in (1,10):
                inside.append(f)
            if f in (sc.frame_start,(sc.frame_start+sc.frame_end)//2,sc.frame_end):
                positions.append({"frame":f,"camera_m":list(p)})
        assert not inside, f"Cámara dentro del volumen: {sc.name} {inside}"
        report["planos"].append({"escena":sc.name,"cuadros":[sc.frame_start,sc.frame_end],
                                 "lente_mm":cam.data.lens,"dof":cam.data.dof.use_dof,
                                 "muestras":positions,"camara_dentro_volumen":inside})
        sc.frame_set(sc.frame_start)
        if sc.compositing_node_group:
            layers=[n for n in sc.compositing_node_group.nodes if n.type=="R_LAYERS"]
            assert all(n.scene==sc for n in layers), "Compositor apunta a otra escena"
    for name in ("CAM_01_HERO_LADO_TIERRA","CAM_03_CREPUSCULAR_NIEVE","CAM_05_LETRERO_HORIZONTE","CAM_06_DETALLE_CELOSIA"):
        forward=bpy.data.objects[name].rotation_euler.to_matrix()@Vector((0,0,-1))
        assert abs(forward.z)<1e-5, "Verticales inclinadas "+name
    report["texturas_no_empaquetadas"]=[i.name for i in bpy.data.images if i.source=="FILE" and not i.packed_file and i.size[0]>0]
    report["assets"]=json.loads(bpy.data.collections["11_VEHICULOS_PERSONAS"]["UY_REPORTE"])
    assert len(report["assets"]["vehiculos"])==6
    grass=bpy.data.objects["UY_PAJA_BRAVA_DISPERSION"]
    assert grass.modifiers["DISPERSION_PAJA_BRAVA"].node_group.name=="UY_GN_VEGETACION_POLYHAVEN_LOD"
    report["vegetacion_polyhaven"]={"matas":len(grass.data.vertices),"variantes":3,"LOD":[0,2]}
    aligned=[ob for ob in bpy.data.objects if ob.name.startswith("UY_FACHADA_AIRE_RAS_")]
    niches=[ob for ob in bpy.data.objects if ob.name.startswith("UY_FACHADA_AIRE_NICHO_VENTANAL_")]
    assert len(aligned)==8 and len(niches)==2
    for group,y in ((aligned,44.572),(niches,43.872)):
        assert all(abs(max((ob.matrix_world@Vector(v)).y for v in ob.bound_box)-y)<1e-4 for ob in group)
    assert not bpy.data.objects.get("UY_NICHO_AIRE") and not bpy.data.objects.get("UY_NICHO_AIRE_COSTADO_ESTE")
    # Las cuatro ME-4 acompañan al muro; las grandes ME-5 conservan su plano.
    glass=bpy.data.objects["UY_CARPINTERIAS_AIRE_VIDRIOS"]
    windows=[(a,b,4.82,6.51,44.492) for a,b in ((53.46,55.955),(58.26,60.755),(63.062,65.557),(67.86,70.355))]
    windows += [(33.83,38.17,3.76,6.51,43.792),(38.63,42.97,3.76,6.51,43.792)]
    for a,b,z0,z1,y in windows:
        pts=[glass.matrix_world@v.co for v in glass.data.vertices if a+.07<v.co.x<b-.07 and z0+.02<v.co.z<z1-.02]
        assert pts and all(abs(p.y-y)<.09 for p in pts)
    doors=bpy.data.objects["UY_PUERTAS_AIRE_ACERO"]
    entry=[doors.matrix_world@v.co for v in doors.data.vertices if 29.129<v.co.x<30.131]
    assert entry and all(abs(p.y-44.492)<.25 for p in entry)
    report["fachada_trasera"]={"panos_enrasados":len(aligned),"cara_muros_m":44.572,
                                "nichos_ventanales":len(niches),"fondo_nichos_m":43.872,
                                "avance_m":.700,"puerta_entrada":"Frontal alineada, 1,00 x 2,10 m"}
    return report


def render(sc,path,width,samples,animated=False,false_color=False):
    bpy.context.window.scene=sc
    render_plan.apply_profile(sc,"drone_draft" if animated else "draft",transparent_bounces=16,
                              device="GPU",animated=animated,motion_blur=animated)
    sc.cycles.samples=samples; sc.cycles.adaptive_threshold=.04
    sc.render.resolution_x=width; sc.render.resolution_y=round(width*9/16)
    sc.render.resolution_percentage=100; render_plan.set_image(sc)
    sc.compositing_node_group=None if false_color else render_plan.make_optics(sc,night="CREPUSCULO" in sc.name,width=width,animated=animated)
    if sc.get("UY_PLANO")==10: sc.compositing_node_group=None
    if false_color: sc.view_settings.view_transform="False Color"
    sc.render.filepath=str(path); started=time.perf_counter()
    bpy.ops.render.render(write_still=True,scene=sc.name)
    duration=time.perf_counter()-started
    if false_color: sc.view_settings.view_transform="AgX"
    print("[PREVIS]",path.name,round(duration,2),flush=True)
    return round(duration,2)


def main():
    argv=sys.argv[sys.argv.index("--")+1:]
    p=argparse.ArgumentParser(); p.add_argument("archivo");p.add_argument("--out",required=True)
    p.add_argument("--baseline"); p.add_argument("--render",action="store_true")
    p.add_argument("--width",type=int,default=960);p.add_argument("--samples",type=int,default=64)
    p.add_argument("--only",default="")
    args=p.parse_args(argv);out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    baseline=None
    if args.baseline:
        bpy.ops.wm.open_mainfile(filepath=str(Path(args.baseline).resolve()));baseline=geometria()
    bpy.ops.wm.open_mainfile(filepath=str(Path(args.archivo).resolve()))
    report=validar(baseline);(out/"validacion.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    if not args.render:return
    from continuacion import materiales
    materiales.aplicar({"profile":"DRON"})
    _,gpu=render_plan.select_device();report["gpu"]=gpu;report["renders"]={}
    only=set(map(int,args.only.split(','))) if args.only else None
    for sc in bpy.data.scenes:
        sid=sc.get("UY_PLANO")
        if not sid or (only and sid not in only):continue
        for label,f in (("inicio",sc.frame_start),("medio",(sc.frame_start+sc.frame_end)//2),("final",sc.frame_end)):
            sc.frame_set(f);name=f"plano_{sid:02d}_{label}.png"
            if (out/name).is_file(): continue
            report["renders"][name]=render(sc,out/name,args.width,args.samples,animated=True)
            (out/"validacion.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"validacion.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")


if __name__=="__main__":main()
