"""Frente de llegada revisado con las capturas aportadas el 4 de octubre.

Las siluetas oscuras son circulación; solo los óvalos interiores son jardineras.
Las cotas del nuevo trazado son de propuesta, no mediciones de las capturas.
Se conserva la vereda, las dársenas y el drenaje A111 junto a la fachada.
"""
import math
import random

import bpy
from mathutils import Vector


def aplicar(g):
    scenes=list(bpy.data.scenes)
    col=bpy.data.collections.new("06_EXTERIORES_FRENTE_4OCT")
    for sc in scenes:sc.collection.children.link(col)
    hidden=("UY_CALZADA_ASFALTO","UY_ISLAS_CORDON","UY_ISLAS_GRAVA",
            "UY_SENALIZACION_VIAL","UY_SENALIZACION_VIAL_AMARILLA")
    for name in hidden:bpy.data.objects[name].hide_render=True
    # Materiales aprobados compartidos con la propuesta existente.
    src=bpy.data.objects["UY_CALZADA_ASFALTO"].data.materials[0]
    M={"asfalto":src,"hormigon":bpy.data.objects["UY_CORDON_TIERRA"].data.materials[0],
       "grava":bpy.data.objects["UY_ISLAS_GRAVA"].data.materials[0],
       "senal":bpy.data.objects["UY_SENALIZACION_VIAL"].data.materials[0],
       "amarillo":bpy.data.objects["UY_SENALIZACION_VIAL_AMARILLA"].data.materials[0]}
    circulation=src.copy();circulation.name="UY_CIRCULACION_OSCURA_FRENTE"
    principled=next(n for n in circulation.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    for name,value in (("Roughness",.82),("Metallic",0)):
        for link in list(principled.inputs[name].links):circulation.node_tree.links.remove(link)
        principled.inputs[name].default_value=value
    placa=g["placa_con_huecos"];rr=g["rect_redondeado"];inset=g["contraer"];Mesh=g["Malla"]
    x0,x1=g["X_CORDON_LATERAL"];yc=g["Y_CALZADA_TIERRA"]
    crosses=g["CANTERO"]["cruces"];cross_width=4.0
    # Dos carriles de llegada existentes, circulación con jardineras, carril
    # exterior y una fila de estacionamiento en espiga: menos fondo impermeable.
    ycir=(yc-5,yc);outer_lane=(yc-12,yc-5);parking=(yc-17,yc-12)
    new_ring=(yc-25.5,yc-18.5)
    old=g["Y_ANILLO_SUR"]
    try:
        g["Y_ANILLO_SUR"]=new_ring
        road=g["calzada_tierra"](g["cordon_tierra"]())
    finally:g["Y_ANILLO_SUR"]=old
    placa("FRENTE_CALZADA_REVISADA",[road],.10,"XY",-.20,M["asfalto"],col)
    cuts=[x0]
    for cx in crosses:cuts.extend((cx-cross_width/2,cx+cross_width/2))
    cuts.append(x1)
    garden_polys=[];circulation_polys=[]
    for i,(a,b) in enumerate(zip(cuts[::2],cuts[1::2]),1):
        path=rr(a,b,*ycir,2.35,n=16);circulation_polys.append(path)
        cx=(a+b)/2;cy=(ycir[0]+ycir[1])/2
        length=(b-a)*.56;garden=rr(cx-length/2,cx+length/2,cy-.72,cy+.72,.70,n=16)
        garden_polys.append(inset(garden,.18))
        placa(f"FRENTE_CIRCULACION_{i:02d}",[path,garden],.15,"XY",-.075,circulation,col)
        # Los cordones vistos dentro de las siluetas delimitan la tierra vegetal.
        placa(f"FRENTE_JARDINERA_CORDON_{i:02d}",[garden,inset(garden,.18)],.30,"XY",.01,M["hormigon"],col)
        placa(f"FRENTE_JARDINERA_TIERRA_{i:02d}",[inset(garden,.18)],.15,"XY",-.055,M["grava"],col)
        plaque=Mesh()
        # Cordón perimetral oscuro, con borde amarillo del trazado de circulación.
        outer=inset(path,.07)
        placa(f"FRENTE_BORDE_CIRCULACION_{i:02d}",[path,outer],.015,"XY",.009,M["amarillo"],col)
    white,yellow=Mesh(),Mesh()
    def line(m,a,b,c,d,z=-.148):m.caja(a,b,c,d,z,z+.002)
    # Cruces alineados a las dos mamparas de ingreso existentes.
    for cx in crosses:
        y=outer_lane[0]+.4
        while y<g["Y_CORDON_TIERRA"]-.5:
            if not(ycir[0]<y<ycir[1]):line(white,cx-2,cx+2,y,y+.5)
            y+=1
        # Rampa dentro del corte: continuidad entre la isla y la acera del ingreso.
        ramp=rr(cx-2,cx+2,ycir[0],ycir[1],.12,n=3)
        placa(f"FRENTE_PASO_NIVEL_{cx:.2f}",[ramp],.15,"XY",-.075,M["hormigon"],col)
    # Puestos a 60°, como la fila en espiga visible en las referencias.
    bays=[];angle=math.radians(60);depth=4.8;step=2.5/math.sin(angle)
    xx=3.0
    while xx+depth/math.tan(angle)<81.5:
        if all(abs(xx-c)>3.5 for c in crosses):
            a=Vector((xx,parking[1],-.148));b=Vector((xx+depth/math.tan(angle),parking[0]+.2,-.148))
            direction=b-a;normal=Vector((-direction.y,direction.x,0)).normalized()*.045
            white.v += [tuple(a-normal),tuple(a+normal),tuple(b+normal),tuple(b-normal)]
            j=len(white.v)-4;white.f.append((j,j+1,j+2,j+3))
            bays.append((xx,parking[1]))
        xx+=step
    # Ejes amarillos y flechas discretas para la vía de llegada y la exterior.
    for y in ((g["Y_CORDON_TIERRA"]+yc)/2,sum(outer_lane)/2,sum(new_ring)/2):
        for x in range(0,83,8):
            if all(abs(x+1.5-c)>3 for c in crosses):line(yellow,x,x+3,y-.055,y+.055)
    white.crear("FRENTE_SENALIZACION_BLANCA",M["senal"],col)
    yellow.crear("FRENTE_SENALIZACION_AMARILLA",M["amarillo"],col)
    # Franja exterior peatonal y cabecera curva del estacionamiento.
    outer_walk=rr(x0,x1,parking[0]-1.5,parking[0],.7,n=12)
    placa("FRENTE_ACERA_EXTERIOR",[outer_walk],.15,"XY",-.075,M["hormigon"],col)
    # Reubica solo los dos proxies de estacionamiento; el resto conserva dársenas.
    for prefix,cx in (("UY_4x4_04_ESTAC",30.1),("UY_4x4_05_ESTAC",35.9)):
        for ob in bpy.data.objects:
            if ob.name.startswith(prefix):ob.location=(cx,sum(parking)/2,-.15);ob.rotation_euler.z=math.radians(240)
    # Recorta la dispersión antigua: no queda pasto en superficies de circulación.
    pts=bpy.data.objects["UY_PAJA_BRAVA_DISPERSION"]
    locations=[]
    for v in pts.data.vertices:
        p=v.co
        if x0-8<p.x<x1+8 and new_ring[0]<p.y<yc:
            continue
        locations.append(tuple(p))
    rng=random.Random(20261004)
    for garden in garden_polys:
        a=min(x for x,y in garden);b=max(x for x,y in garden);c=min(y for x,y in garden);d=max(y for x,y in garden)
        for _ in range(round((b-a)*(d-c)*1.1)):
            x=rng.uniform(a,b);y=rng.uniform(c,d)
            if g["dentro_poligono"](x,y,garden):locations.append((x,y,.02))
    pts.data.clear_geometry();pts.data.from_pydata(locations,[],[]);pts.data.update()
    col["UY_REFERENCIA"]="Capturas cliente 4 octubre: circulación oscura con jardineras interiores"
    col["UY_COTAS_ESTADO"]="Propuesta aproximada para revisión visual; no replanteo CAD"
    col["UY_ANCHO_CIRCULACION_M"]=5.0;col["UY_ANCHO_JARDINERA_M"]=1.44
    return {"franjas_circulacion":3,"jardineras":3,"cruces":list(crosses),"fila_espiga":1,
            "puesto_nominal_m":2.5,"anillo_y_m":list(new_ring),"cotas":"propuesta por imágenes",
            "originales_ocultos":list(hidden),"dispersión_paja_actualizada":True}
