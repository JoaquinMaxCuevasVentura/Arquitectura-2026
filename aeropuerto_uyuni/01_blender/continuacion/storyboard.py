"""Montaje de 120 s reproducible desde el storyboard entregado por el cliente."""
import json
import math

import bpy
from mathutils import Vector

OWNER = "uyuni_storyboard_120s"


def curva(ob, ruta):
    # Compatibilidad con Actions por slots de Blender 5; sin curvas automáticas.
    action = ob.animation_data.action
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    if fc.data_path == ruta:
                        for key in fc.keyframe_points:
                            key.interpolation = "LINEAR"


def camara(sc, shot):
    data = bpy.data.cameras.new(f"VIDEO_CAM_{shot['id']:02d}")
    ob = bpy.data.objects.new(data.name, data); sc.collection.objects.link(ob)
    data.lens = shot["lens_mm"]; data.sensor_width = shot["sensor_width_mm"]
    data.clip_start = .05; data.clip_end = 60000
    focus = bpy.data.objects.new(f"VIDEO_FOCO_{shot['id']:02d}", None)
    sc.collection.objects.link(focus); focus.empty_display_size = .3
    data.dof.focus_object = focus; data.dof.use_dof = shot["use_dof"]
    data.dof.aperture_fstop = shot["fstop"]
    ob.rotation_mode = "QUATERNION"
    p0, p1 = Vector(shot["camera_start_m"]), Vector(shot["camera_end_m"])
    q0, q1 = Vector(shot["target_start_m"]), Vector(shot["target_end_m"])
    start, end = shot["start_frame"], shot["end_frame"]
    for f in range(start, end + 1):
        t = (f-start)/(end-start); s = 6*t**5 - 15*t**4 + 10*t**3
        ob.location = p0.lerp(p1, s); focus.location = q0.lerp(q1, s)
        ob.rotation_quaternion = (focus.location-ob.location).to_track_quat("-Z", "Y")
        ob.keyframe_insert("location", frame=f); ob.keyframe_insert("rotation_quaternion", frame=f)
        focus.keyframe_insert("location", frame=f)
    curva(ob, "location"); curva(ob, "rotation_quaternion"); curva(focus, "location")
    ob["UY_OWNER"] = OWNER; ob["UY_GUION"] = json.dumps(shot, ensure_ascii=False)
    sc.camera = ob
    return ob


def escena_base(nombre, base):
    sc = bpy.data.scenes.new(nombre)
    for col in base.collection.children:
        sc.collection.children.link(col)
    for key in base.keys():
        sc[key] = base[key]
    sc.world = base.world
    sc.view_settings.exposure = base.view_settings.exposure
    sc.unit_settings.system = "METRIC"; sc.unit_settings.scale_length = 1
    return sc


def material_emision(nombre, color):
    mat = bpy.data.materials.new(nombre); mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*color, 1)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], out.inputs[0])
    return mat


def escena_salar(base):
    sc = bpy.data.scenes.new("UYUNI_VIDEO_01_SALAR")
    sc["UY_CONTEXTO"] = "Escena de contexto independiente: no simula continuidad geográfica"
    sc.world = base.world.copy(); sc.world.name = "UY_VIDEO_AMANECER_SALAR"
    for node in sc.world.node_tree.nodes:
        if node.type == "TEX_SKY":
            node.sun_elevation = math.radians(3)
        elif node.type == "BACKGROUND":
            node.inputs["Strength"].default_value = .25
    mesh = bpy.data.meshes.new("VIDEO_SALAR_SUPERFICIE")
    mesh.from_pydata([(-15000,-15000,0),(15000,-15000,0),(15000,15000,0),(-15000,15000,0)], [], [(0,1,2,3)])
    ob = bpy.data.objects.new(mesh.name, mesh); sc.collection.objects.link(ob)
    mat = bpy.data.materials.new("UY_VIDEO_SALAR_REFLEJO"); mat.use_nodes = True
    nt = mat.node_tree; b = nt.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (.72,.73,.73,1)
    b.inputs["Roughness"].default_value = .08; b.inputs["IOR"].default_value = 1.333
    b.inputs["Coat Weight"].default_value = 1
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 4
    geo = nt.nodes.new("ShaderNodeNewGeometry"); nt.links.new(geo.outputs["Position"], noise.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .12
    bump.inputs["Distance"].default_value = .001; nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"]); mesh.materials.append(mat)
    # Costra salina visible bajo la lámina de agua, en coordenadas métricas.
    cells=nt.nodes.new("ShaderNodeTexVoronoi"); cells.feature="DISTANCE_TO_EDGE"
    cells.inputs["Scale"].default_value=.6; nt.links.new(geo.outputs["Position"],cells.inputs["Vector"])
    edge=nt.nodes.new("ShaderNodeMath"); edge.operation="LESS_THAN"; edge.inputs[1].default_value=.014
    nt.links.new(cells.outputs["Distance"],edge.inputs[0])
    rough=nt.nodes.new("ShaderNodeMath"); rough.operation="MULTIPLY_ADD"
    rough.inputs[1].default_value=.25; rough.inputs[2].default_value=.065
    nt.links.new(edge.outputs[0],rough.inputs[0]); nt.links.new(rough.outputs[0],b.inputs["Roughness"])
    # Montañas del contexto procedural, sin edificios ni pistas en esta escena.
    for mountain in base.objects:
        if mountain.name == "UY_SUELO_ALTIPLANO":
            sc.collection.objects.link(mountain)
    return sc


def cierre_logo(base, start=2737, end=2880):
    sc = bpy.data.scenes.new("UYUNI_VIDEO_10_IDENTIDAD")
    sc.world = bpy.data.worlds.new("UY_VIDEO_GRAPHIC_WORLD")
    sc.world.use_nodes = True
    sc.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (.018,.024,.027,1)
    col = bpy.data.collections.new("VIDEO_LOGO_ORIGINAL"); sc.collection.children.link(col)
    letter = bpy.data.objects["UY_LETRERO_LETRAS_UYUNI_A"]
    vertices = [letter.matrix_world @ v.co for v in letter.data.vertices]
    xmin = min(v.x for v in vertices); xmax = max(v.x for v in vertices)
    # Incluye los montículos del ingreso central; omite la repetición de salida.
    center = (xmin+xmax)/2
    central_range = (center-20, center+20)
    groups = [
        ("UY_LETRERO_LINEA_HORIZONTE_A", "HORIZONTE", 2737,2760),
        ("UY_LETRERO_PIRAMIDES_SAL_3D_A", "MONTICULOS", 2761,2791),
        ("UY_LETRERO_LETRAS_UYUNI_A", "NOMBRE", 2792,2820),
        ("UY_LETRERO_REFLEJO_UYUNI_A", "REFLEJO", 2821,2849),
        ("UY_LETRERO_REFLEJO_MONTICULOS_A", "REFLEJO_MONTICULOS", 2821,2849),
    ]
    all_points = []
    for source, label, reveal_start, reveal_end in groups:
        src = bpy.data.objects[source]
        selected = [p for p in src.data.polygons if all(central_range[0] < (src.matrix_world @ src.data.vertices[i].co).x < central_range[1] for i in p.vertices)]
        ids = sorted({i for p in selected for i in p.vertices}); lookup = {i:j for j,i in enumerate(ids)}
        pts = [src.matrix_world @ src.data.vertices[i].co for i in ids]; all_points += pts
        mesh = bpy.data.meshes.new("VIDEO_ARTE_"+label)
        mesh.from_pydata(pts, [], [[lookup[i] for i in p.vertices] for p in selected]); mesh.update()
        ob = bpy.data.objects.new(mesh.name, mesh); col.objects.link(ob)
        ob["UY_GEOMETRIA_ORIGINAL"] = source
        # Máscara horizontal, sin escalar ni sustituir los contornos originales.
        mat = bpy.data.materials.new("VIDEO_REVEAL_"+label); mat.use_nodes = True
        nt=mat.node_tree; nt.nodes.clear()
        geo=nt.nodes.new("ShaderNodeNewGeometry"); sep=nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo.outputs["Position"],sep.inputs[0])
        value=nt.nodes.new("ShaderNodeValue"); value.outputs[0].default_value=central_range[0]-.1
        value.outputs[0].keyframe_insert("default_value",frame=reveal_start)
        value.outputs[0].default_value=central_range[1]+.1
        value.outputs[0].keyframe_insert("default_value",frame=reveal_end)
        test=nt.nodes.new("ShaderNodeMath"); test.operation="LESS_THAN"
        nt.links.new(sep.outputs["X"],test.inputs[0]); nt.links.new(value.outputs[0],test.inputs[1])
        em=nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value=(.61,.31,.19,1)
        if "MONTICULOS" in label and label == "MONTICULOS":
            # Mantiene caras y añade su relieve a la presentación gráfica.
            geom=nt.nodes.new("ShaderNodeNewGeometry"); dot=nt.nodes.new("ShaderNodeVectorMath"); dot.operation="DOT_PRODUCT"
            nt.links.new(geom.outputs["Normal"],dot.inputs[0]); dot.inputs[1].default_value=(.3,-.85,.4)
            add=nt.nodes.new("ShaderNodeMath"); add.operation="MULTIPLY_ADD"; add.inputs[1].default_value=.35; add.inputs[2].default_value=.75
            nt.links.new(dot.outputs["Value"],add.inputs[0]); nt.links.new(add.outputs[0],em.inputs["Strength"])
        transparent=nt.nodes.new("ShaderNodeBsdfTransparent"); mix=nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(test.outputs[0],mix.inputs[0]); nt.links.new(transparent.outputs[0],mix.inputs[1]); nt.links.new(em.outputs[0],mix.inputs[2])
        out=nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(mix.outputs[0],out.inputs[0]); mesh.materials.append(mat)
    low=Vector(tuple(min(p[a] for p in all_points) for a in range(3)))
    high=Vector(tuple(max(p[a] for p in all_points) for a in range(3)))
    target=(low+high)/2
    data=bpy.data.cameras.new("VIDEO_CAM_10"); data.type="ORTHO"
    data.ortho_scale=(high.x-low.x)*1.25
    cam=bpy.data.objects.new(data.name,data); sc.collection.objects.link(cam)
    cam.location=(target.x,target.y-20,target.z)
    cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler(); sc.camera=cam
    sc["UY_ARTE"]="Contornos y pirámides originales A; máscara por capas, sin rediseño"
    return sc


def aplicar(data, configurar, letrero_A):
    if bpy.data.scenes.get("UYUNI_VIDEO_MASTER_120S"):
        raise RuntimeError("El storyboard debe construirse una sola vez desde la fuente limpia")
    base=bpy.data.scenes["UYUNI_DIA"]; shots=[]
    for shot in data["shots"]:
        sid=shot["id"]
        if sid==1:
            sc=escena_salar(base)
        elif sid==10:
            sc=cierre_logo(base)
        else:
            sc=escena_base(f"UYUNI_VIDEO_{sid:02d}_{shot['name'].upper().replace(' ','_')}",base)
            letrero_A(sc,"A")
        configurar(sc,animado=True)
        if sid==10:
            # Arte gráfico: conserva contornos, sin distorsión óptica de cámara.
            sc.compositing_node_group=None
        sc.frame_start=shot["start_frame"]; sc.frame_end=shot["end_frame"]
        sc["UY_PLANO"]=sid; sc["UY_ESTADO_LUZ"]=shot["lighting_state"]
        if sid!=10: camara(sc,shot)
        if shot["lighting_state"]=="ATARDECER_LATERAL":
            # Colección exclusiva: el sol de mañana compartido queda excluido aquí.
            from herramientas.render_plan import find_layer
            for vl in sc.view_layers:
                lc=find_layer(vl.layer_collection,"08_LUZ_DIA")
                if lc: lc.exclude=True
            col=bpy.data.collections.new("VIDEO_05_SOL_RASANTE"); sc.collection.children.link(col)
            sun=bpy.data.lights.new("VIDEO_SOL_TARDE","SUN"); sun.energy=2.7; sun.angle=math.radians(.53)
            ob=bpy.data.objects.new(sun.name,sun); col.objects.link(ob)
            # Sol occidental georreferenciado: contraluz en el testero Este.
            north=float(base.get("norte_verdadero_local_deg_CCW_desde_X",301.043))
            az,elev=262.0,12.0
            phi=math.radians(north-az); e=math.radians(elev)
            toward=Vector((math.cos(e)*math.cos(phi),math.cos(e)*math.sin(phi),math.sin(e)))
            ob.rotation_euler=toward.to_track_quat("Z","Y").to_euler()
            sc.world=base.world.copy()
            for node in sc.world.node_tree.nodes:
                if node.type=="TEX_SKY": node.sun_elevation=e; node.sun_rotation=math.radians((90-(north-az))%360)
            sc["UY_SOL_AZIMUT_ELEVACION"]=[az,elev]
        sc.frame_set(sc.frame_start); shots.append((shot,sc))
    master=bpy.data.scenes.new("UYUNI_VIDEO_MASTER_120S")
    master.frame_start=1; master.frame_end=data["frame_end"]
    master.render.fps=data["fps"]; master.render.resolution_x,master.render.resolution_y=data["resolution"]
    master.render.resolution_percentage=100; master.render.use_sequencer=True
    master.view_settings.view_transform="AgX"; master.view_settings.look="AgX - Medium High Contrast"
    editor=master.sequence_editor_create()
    for shot,sc in shots:
        strip=editor.strips.new_scene(f"{shot['id']:02d} · {shot['name']}",sc,channel=1,frame_start=shot["start_frame"])
        strip.scene_input="CAMERA"
        strip.frame_final_duration=shot["end_frame"]-shot["start_frame"]+1
        if strip.frame_final_start!=shot["start_frame"] or strip.frame_final_end!=shot["end_frame"]+1:
            raise RuntimeError("Duración VSE distinta del guion")
        master.timeline_markers.new(shot["name"],frame=shot["start_frame"])
    master["UY_OWNER"]=OWNER; master["UY_STORYBOARD"]=json.dumps(data,ensure_ascii=False)
    master["UY_DURACION_SEGUNDOS"]=120; master["UY_FPS"]=24
    master["UY_PENDIENTE_AUDIO"]="No se incorpora música ni locución sin archivos autorizados"
    master.frame_set(1)
    return {"planos":len(shots),"cuadros":2880,"fps":24,"duracion_s":120,
            "master":master.name,"recorrido_corto_conservado":"CAM_DRON / 600 cuadros",
            "validacion":"Revisar previs de encuadres y colisiones; coordenadas del guion conservadas"}
