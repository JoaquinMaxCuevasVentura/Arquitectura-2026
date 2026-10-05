"""Assets locales y CC0/CC-BY a escala real; conserva el sitio del script base."""
import json
import os
import math
import random
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ASSETS = Path(__file__).resolve().parents[1] / "assets"
OWNER = "uyuni_codex_continuacion"


def coleccion(nombre, escenas):
    col = bpy.data.collections.get(nombre)
    if col is None:
        col = bpy.data.collections.new(nombre)
        col["UY_OWNER"] = OWNER
    if col.get("UY_OWNER") != OWNER:
        raise RuntimeError(f"Colección ajena: {nombre}")
    for sc in escenas:
        if col.name not in sc.collection.children:
            sc.collection.children.link(col)
    return col


def imagen(path, noncolor=False):
    im = bpy.data.images.load(str(path), check_existing=True)
    if noncolor:
        im.colorspace_settings.name = "Non-Color"
    im.pack()
    return im


def suelo_pbr():
    """Textura cercana sobre el terreno de 45 km; conserva cerros, Salar y nieve."""
    ob = bpy.data.objects["UY_SUELO_ALTIPLANO"]
    if ob.get("UY_PBR_APLICADO"):
        return
    original = ob.data.materials[0]
    mat = original.copy()
    mat.name = "UY_SUELO_PBR_SAL_ALTIPLANO"
    mat["UY_SOURCE"] = "https://polyhaven.com/a/sandy_gravel_02"
    mat["UY_LICENSE"] = "CC0 1.0"
    mat["UY_TILE_METROS"] = 2.53
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    b = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    old_color = b.inputs["Base Color"].links[0].from_socket
    geo = nodes.new("ShaderNodeNewGeometry")
    scale = nodes.new("ShaderNodeVectorMath"); scale.operation = "SCALE"
    scale.inputs["Scale"].default_value = 1 / 2.53
    links.new(geo.outputs["Position"], scale.inputs[0])
    # Deformación suave y compartida por los tres mapas: rompe las bandas de
    # repetición que se reconocen desde las cámaras aéreas.
    warp = nodes.new("ShaderNodeTexNoise"); warp.inputs["Scale"].default_value = .25
    links.new(geo.outputs["Position"], warp.inputs["Vector"])
    offset = nodes.new("ShaderNodeVectorMath"); offset.operation = "SUBTRACT"
    links.new(warp.outputs["Color"], offset.inputs[0]); offset.inputs[1].default_value = (.5,.5,.5)
    amount = nodes.new("ShaderNodeVectorMath"); amount.operation = "SCALE"
    amount.inputs["Scale"].default_value = .7; links.new(offset.outputs["Vector"], amount.inputs[0])
    mapped = nodes.new("ShaderNodeVectorMath"); mapped.operation = "ADD"
    links.new(scale.outputs["Vector"], mapped.inputs[0]); links.new(amount.outputs["Vector"], mapped.inputs[1])
    tex = {}
    for channel, suffix in (("diff", "diff"), ("rough", "rough"), ("normal", "nor_gl")):
        node = nodes.new("ShaderNodeTexImage")
        node.image = imagen(ASSETS / "polyhaven/sandy_gravel_02" / f"sandy_gravel_02_{suffix}_2k.jpg", channel != "diff")
        links.new(mapped.outputs["Vector"], node.inputs["Vector"])
        tex[channel] = node
    # XY planar en metros: base tangente coherente para el normal map de suelo.
    uv = ob.data.uv_layers.get("UY_PLANO_METROS") or ob.data.uv_layers.new(name="UY_PLANO_METROS")
    for loop in ob.data.loops:
        v = ob.data.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = (v.x / 2.53, v.y / 2.53)
    normal = nodes.new("ShaderNodeNormalMap")
    normal.uv_map = uv.name; normal.inputs["Strength"].default_value = .35
    links.new(tex["normal"].outputs["Color"], normal.inputs["Color"])
    # La costra se limita al material del terreno; no llega a asfalto/plataforma.
    noise = nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = .4
    noise.inputs["Distortion"].default_value = 2
    links.new(geo.outputs["Position"], noise.inputs["Vector"])
    vor = nodes.new("ShaderNodeTexVoronoi"); vor.feature = "DISTANCE_TO_EDGE"
    vor.inputs["Scale"].default_value = 1.6
    links.new(geo.outputs["Position"], vor.inputs["Vector"])
    edge = nodes.new("ShaderNodeMath"); edge.operation = "LESS_THAN"
    links.new(vor.outputs["Distance"], edge.inputs[0]); edge.inputs[1].default_value = .012
    patch = nodes.new("ShaderNodeMath"); patch.operation = "GREATER_THAN"
    links.new(noise.outputs["Fac"], patch.inputs[0]); patch.inputs[1].default_value = .57
    salt = nodes.new("ShaderNodeMath"); salt.operation = "MULTIPLY"
    links.new(edge.outputs[0], salt.inputs[0]); links.new(patch.outputs[0], salt.inputs[1])
    subtle=nodes.new("ShaderNodeMath");subtle.operation="MULTIPLY";subtle.inputs[1].default_value=.18
    links.new(salt.outputs[0],subtle.inputs[0])
    salt_mix = nodes.new("ShaderNodeMixRGB")
    links.new(subtle.outputs[0], salt_mix.inputs[0])
    links.new(tex["diff"].outputs["Color"], salt_mix.inputs[1]); salt_mix.inputs[2].default_value = (.57, .56, .51, 1)
    # Más allá de 400 m conserva el shader procedural, incluido el Salar lejano.
    distance = nodes.new("ShaderNodeVectorMath"); distance.operation = "DISTANCE"
    links.new(geo.outputs["Position"], distance.inputs[0]); distance.inputs[1].default_value = (40, 20, 0)
    near = nodes.new("ShaderNodeMapRange")
    links.new(distance.outputs["Value"], near.inputs["Value"])
    for key, value in (("From Min", 180), ("From Max", 400), ("To Min", 1), ("To Max", 0)):
        near.inputs[key].default_value = value
    near.clamp = True
    # Las propiedades nieve/salar siguen procediendo del material original.
    snow = nodes.new("ShaderNodeAttribute"); snow.attribute_type = "VIEW_LAYER"; snow.attribute_name = "nieve"
    dry = nodes.new("ShaderNodeMath"); dry.operation = "SUBTRACT"; dry.inputs[0].default_value = 1
    links.new(snow.outputs["Fac"], dry.inputs[1])
    weight = nodes.new("ShaderNodeMath"); weight.operation = "MULTIPLY"
    links.new(near.outputs["Result"], weight.inputs[0]); links.new(dry.outputs[0], weight.inputs[1])
    mix = nodes.new("ShaderNodeMixRGB")
    links.new(weight.outputs[0], mix.inputs[0]); links.new(old_color, mix.inputs[1])
    links.new(salt_mix.outputs["Color"], mix.inputs[2]); links.new(mix.outputs[0], b.inputs["Base Color"])
    links.new(tex["rough"].outputs["Color"], b.inputs["Roughness"])
    links.new(normal.outputs["Normal"], b.inputs["Normal"])
    ob.data.materials[0] = mat
    ob["UY_PBR_APLICADO"] = True


def vegetacion(escenas, cantidad=None):
    """Sustituye toda la vegetación procedural por tres scans CC0, con dos LOD."""
    col = coleccion("10_CONTEXTO_PAISAJE", escenas)
    if col.get("UY_VEGETACION_APLICADA"):
        return int(col["UY_CANTIDAD"])
    asset = ASSETS / "polyhaven/grass_medium_01/grass_medium_01_1k.blend"
    with bpy.data.libraries.load(str(asset), link=False) as (src, dst):
        names = [f"grass_medium_01_geonodes_large_{letter}_LOD{lod}" for lod in (0,2) for letter in "abc"]
        if not all(name in src.objects for name in names):
            raise RuntimeError("Faltan las tres variantes de mata de Poly Haven")
        dst.objects = names
    templates={0:bpy.data.collections.new("PH_MATAS_PLANTILLAS_LOD0"),
               2:bpy.data.collections.new("PH_MATAS_PLANTILLAS_LOD2")}
    for index,ob in enumerate(dst.objects):
        mesh = ob.data
        mesh.transform(ob.matrix_world)
        low=Vector(tuple(min(v.co[a] for v in mesh.vertices) for a in range(3)))
        high=Vector(tuple(max(v.co[a] for v in mesh.vertices) for a in range(3)))
        center=Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z))
        height=(.40,.55,.65)[index%3];factor=height/max(high.z-low.z,.001)
        mesh.transform(Matrix.Scale(factor,4)@Matrix.Translation(-center))
        ob.matrix_world=Matrix.Identity(4)
        for mat in mesh.materials:
            if not mat or not mat.use_nodes:
                continue
            mat["UY_SOURCE"] = "https://polyhaven.com/a/grass_medium_01"
            mat["UY_LICENSE"] = "CC0 1.0"
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image:
                    name = Path(node.image.filepath).name
                    if "diff" in name:
                        name = "grass_medium_01_dry_diff_1k.png"
                    path = ASSETS / "polyhaven/grass_medium_01/textures" / name
                    if path.is_file():
                        node.image = imagen(path, any(k in name for k in ("rough", "nor", "alpha")))
        lod=0 if index<3 else 2
        templates[lod].objects.link(ob)
        ob.location.z=-1000
        ob["UY_SOURCE"]="https://polyhaven.com/a/grass_medium_01";ob["UY_LICENSE"]="CC0 1.0"
    # Cycles necesita las plantillas en su grafo de render. Se ocultan bajo el
    # terreno; Reset Children elimina esa traslación en las instancias.
    for template_col in templates.values():
        for sc in escenas:sc.collection.children.link(template_col)
    points = bpy.data.objects["UY_PAJA_BRAVA_DISPERSION"]
    ng=bpy.data.node_groups.new("UY_GN_VEGETACION_POLYHAVEN_LOD","GeometryNodeTree")
    ng.interface.new_socket(name="Geometry",in_out="INPUT",socket_type="NodeSocketGeometry")
    ng.interface.new_socket(name="Geometry",in_out="OUTPUT",socket_type="NodeSocketGeometry")
    N,L=ng.nodes,ng.links;gi=N.new("NodeGroupInput");go=N.new("NodeGroupOutput")
    position=N.new("GeometryNodeInputPosition");dist=N.new("ShaderNodeVectorMath");dist.operation="DISTANCE"
    dist.inputs[1].default_value=(41,-10,0);L.new(position.outputs[0],dist.inputs[0])
    far=N.new("ShaderNodeMath");far.operation="GREATER_THAN";far.inputs[1].default_value=110
    L.new(dist.outputs["Value"],far.inputs[0])
    sep=N.new("GeometryNodeSeparateGeometry");sep.domain="POINT"
    L.new(gi.outputs[0],sep.inputs["Geometry"]);L.new(far.outputs[0],sep.inputs["Selection"])
    rotate=N.new("FunctionNodeRandomValue");rotate.data_type="FLOAT_VECTOR"
    rotate.inputs["Min"].default_value=(-.06,-.06,0);rotate.inputs["Max"].default_value=(.06,.06,math.tau)
    scale=N.new("FunctionNodeRandomValue");scale.data_type="FLOAT"
    scale.inputs["Min"].default_value=.75;scale.inputs["Max"].default_value=1.2
    choice=N.new("FunctionNodeRandomValue");choice.data_type="INT"
    next(s for s in choice.inputs if s.name=="Min" and s.type=="INT").default_value=0
    next(s for s in choice.inputs if s.name=="Max" and s.type=="INT").default_value=2
    join=N.new("GeometryNodeJoinGeometry")
    for lod,output in ((0,"Inverted"),(2,"Selection")):
        info=N.new("GeometryNodeCollectionInfo");info.inputs["Collection"].default_value=templates[lod]
        info.inputs["Separate Children"].default_value=True;info.inputs["Reset Children"].default_value=True
        instances=N.new("GeometryNodeInstanceOnPoints");instances.inputs["Pick Instance"].default_value=True
        L.new(sep.outputs[output],instances.inputs["Points"]);L.new(info.outputs["Instances"],instances.inputs["Instance"])
        L.new(next(s for s in choice.outputs if s.type=="INT"),instances.inputs["Instance Index"])
        L.new(rotate.outputs["Value"],instances.inputs["Rotation"]);L.new(scale.outputs["Value"],instances.inputs["Scale"])
        L.new(instances.outputs["Instances"],join.inputs["Geometry"])
    L.new(join.outputs[0],go.inputs[0])
    points.modifiers["DISPERSION_PAJA_BRAVA"].node_group=ng
    col["UY_VEGETACION_APLICADA"] = True; col["UY_CANTIDAD"] = len(points.data.vertices)
    col["UY_ESPECIE"] = "Tres matas escaneadas secas Poly Haven; referencia visual, sin identificación botánica"
    col["UY_LOD"]="LOD0 hasta 110 m del frente; LOD2 en el resto del contexto"
    points["UY_SOURCE"]="https://polyhaven.com/a/grass_medium_01"
    return int(col["UY_CANTIDAD"])


def plantilla_glb(path, nombre, largo=None, altura=None, eje="X"):
    """Convierte el asset a un espacio común, con apoyo en z=0 y escala horneada."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    imported = list(set(bpy.data.objects) - before)
    meshes = [ob for ob in imported if ob.type == "MESH"]
    if not meshes:
        raise RuntimeError(f"GLB sin mallas: {path}")
    bpy.context.view_layer.update()
    vertices = [ob.matrix_world @ Vector(c) for ob in meshes for c in ob.bound_box]
    low = Vector(tuple(min(v[a] for v in vertices) for a in range(3)))
    high = Vector(tuple(max(v[a] for v in vertices) for a in range(3)))
    size = high - low
    rotation = Matrix.Identity(4)
    if largo and size.y > size.x:
        rotation = Matrix.Rotation(math.pi / 2, 4, "Z")
    transformed = [rotation @ v for v in vertices]
    low = Vector(tuple(min(v[a] for v in transformed) for a in range(3)))
    high = Vector(tuple(max(v[a] for v in transformed) for a in range(3)))
    factor = largo / (high.x - low.x) if largo else altura / (high.z - low.z)
    center = Vector(((low.x + high.x) / 2, (low.y + high.y) / 2, low.z))
    matrix = Matrix.Scale(factor, 4) @ Matrix.Translation(-center) @ rotation
    templates = []
    for i, ob in enumerate(meshes):
        mesh = ob.data.copy(); mesh.transform(matrix @ ob.matrix_world)
        mesh.name = f"UY_ASSET_{nombre}_{i:02d}"
        templates.append(mesh)
        for mat in mesh.materials:
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == "TEX_IMAGE" and node.image:
                        image = node.image
                        if not image.packed_file:
                            resolved = Path(bpy.path.abspath(image.filepath))
                            if not resolved.is_file():
                                candidate = path.parent / "tex" / Path(image.filepath.replace("\\", "/")).name
                                if not candidate.is_file():
                                    raise FileNotFoundError(f"Textura del asset local: {image.filepath}")
                                image.filepath = str(candidate); image.reload()
                            image.pack()
    for ob in imported:
        bpy.data.objects.remove(ob, do_unlink=True)
    return templates


def plantilla_blend(path, nombre, largo=None, altura=None):
    """Asset local: hornea modificadores y comparte mallas entre instancias."""
    with bpy.data.libraries.load(str(path), link=False) as (src, dst):
        dst.objects = list(src.objects)
    imported = [ob for ob in dst.objects if ob is not None]
    temp = bpy.data.collections.new("UY_IMPORTACION_ASSET_LOCAL")
    bpy.context.scene.collection.children.link(temp)
    for ob in imported:
        temp.objects.link(ob)
        # Un nivel mantiene superficies suaves sin multiplicar innecesariamente
        # la geometría para los cinco vehículos de contexto.
        for modifier in ob.modifiers:
            if modifier.type == "SUBSURF":
                modifier.levels = min(modifier.levels, 1)
                modifier.render_levels = min(modifier.render_levels, 1)
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    meshes = []
    for ob in imported:
        if ob.type not in ("MESH", "CURVE", "FONT", "SURFACE") or ob.hide_render:
            continue
        mesh = bpy.data.meshes.new_from_object(ob.evaluated_get(depsgraph), preserve_all_data_layers=True, depsgraph=depsgraph)
        if not mesh.vertices:
            bpy.data.meshes.remove(mesh)
            continue
        mesh.transform(ob.matrix_world)
        meshes.append(mesh)
    if not meshes:
        raise RuntimeError(f"Asset local sin geometría visible: {path}")
    vertices = [v.co for mesh in meshes for v in mesh.vertices]
    low = Vector(tuple(min(v[a] for v in vertices) for a in range(3)))
    high = Vector(tuple(max(v[a] for v in vertices) for a in range(3)))
    rotation = Matrix.Rotation(math.pi / 2, 4, "Z") if largo and high.y-low.y > high.x-low.x else Matrix.Identity(4)
    corners = [rotation @ Vector((x,y,z)) for x in (low.x,high.x) for y in (low.y,high.y) for z in (low.z,high.z)]
    low = Vector(tuple(min(v[a] for v in corners) for a in range(3)))
    high = Vector(tuple(max(v[a] for v in corners) for a in range(3)))
    factor = largo/(high.x-low.x) if largo else altura/(high.z-low.z)
    center = Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z))
    matrix = Matrix.Scale(factor,4) @ Matrix.Translation(-center) @ rotation
    for i,mesh in enumerate(meshes):
        mesh.transform(matrix)
        mesh.name = f"UY_ASSET_{nombre}_{i:03d}"
        for material in mesh.materials:
            if material and material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == "TEX_IMAGE" and node.image:
                        image = node.image
                        if not image.packed_file:
                            resolved = Path(bpy.path.abspath(image.filepath))
                            if not resolved.is_file():
                                candidate = path.parent / "tex" / Path(image.filepath.replace("\\", "/")).name
                                if not candidate.is_file():
                                    raise FileNotFoundError(f"Textura del asset local: {image.filepath}")
                                image.filepath = str(candidate); image.reload()
                            image.pack()
    for ob in imported:
        bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.collections.remove(temp)
    return meshes


def colocar(templates, proxy, col, nombre, giro=0):
    z = proxy.location.z if "CARROCERIA" in proxy.name else min((proxy.matrix_world @ Vector(c)).z for c in proxy.bound_box)
    for i, mesh in enumerate(templates):
        ob = bpy.data.objects.new(f"UY_ASSET_{nombre}_{i:02d}", mesh)
        col.objects.link(ob)
        ob.location = (proxy.location.x, proxy.location.y, z)
        ob.rotation_euler.z = proxy.rotation_euler.z + giro
        ob["UY_PROXY_ORIGEN"] = proxy.name; ob["UY_OWNER"] = OWNER
    proxy.hide_render = True


def vehiculos_personas(escenas):
    col = coleccion("11_VEHICULOS_PERSONAS", escenas)
    if col.get("UY_ASSETS_APLICADOS"):
        return json.loads(col["UY_REPORTE"])
    local = os.environ.get("UYUNI_ASSETS_LOCALES", os.environ.get("UYUNI_PERSONAS_LOCALES", "0")) == "1"
    land_cruiser = ASSETS / "local/vehicles/land_cruiser_200.blend"
    suv_local = local and land_cruiser.is_file()
    suv = plantilla_blend(land_cruiser, "LAND_CRUISER_LOCAL", largo=4.95) if suv_local else plantilla_glb(ASSETS / "vehicles/Range_Rover_IvOfficial.glb", "SUV", largo=4.9)
    sprinter = ASSETS / "local/vehicles/sprinter_pasajeros.blend"
    van_local = local and sprinter.is_file()
    van = plantilla_blend(sprinter, "TRANSFER_LOCAL", largo=6.4) if van_local else plantilla_glb(ASSETS / "vehicles/Generic_Van_PuKkBuMXDD.glb", "TRANSFER", largo=6.4)
    report = {"vehiculos": [], "personas": [], "personas_locales": False,
              "vehiculos_locales":suv_local, "transfer_local":van_local, "personas_variantes":[],
              "suv": "Toyota Land Cruiser 200 detallado de BlenderKit" if suv_local else "Range Rover provisional; no es Toyota Land Cruiser",
              "transfer": "Mercedes Sprinter de pasajeros detallado de BlenderKit" if van_local else "Van genérico provisional"}
    for proxy in list(bpy.data.objects):
        if proxy.name.startswith("UY_4x4_") and proxy.name.endswith("_CARROCERIA"):
            colocar(suv, proxy, col, proxy.name.removeprefix("UY_"))
            report["vehiculos"].append(proxy.name)
        elif proxy.name == "UY_MINIBUS_TRANSFER_CARROCERIA":
            colocar(van, proxy, col, "MINIBUS_TRANSFER")
            report["vehiculos"].append(proxy.name)
    people = []
    if local:
        person = ASSETS / "local/people/rp_posed_00178_29/rp_posed_00178_29.glb"
        if person.is_file():
            people.append(plantilla_glb(person, "PERSONA_LOCAL_00178", altura=1.70))
            report["personas_variantes"].append("rp_posed_00178_29")
        for name, lod, height in (("rp_mei_posed_001","30k",1.70),
                                 ("rp_dennis_posed_004","30k",1.80),
                                 ("rp_fabienne_percy_posed_001","60k",1.72)):
            path = ASSETS / "local/people" / name / f"{name}_{lod}.blend"
            if path.is_file():
                people.append(plantilla_blend(path, name.upper(), altura=height))
                report["personas_variantes"].append(name)
    if people:
        for i, proxy in enumerate(sorted((o for o in bpy.data.objects if o.name.startswith("UY_TURISTA_")), key=lambda o:o.name)):
            colocar(people[i % len(people)], proxy, col, f"TURISTA_{i:02d}", math.radians((i * 41) % 360))
            report["personas"].append(proxy.name)
        report["personas_locales"] = True
    col["UY_ASSETS_APLICADOS"] = True; col["UY_REPORTE"] = json.dumps(report)
    return report


def limpiar_para_ia():
    """Deja en el render solo lo que la IA no debe inventar: arquitectura, sitio y assets locales de alta calidad.

    Oculta en el render (sin borrarlos) la dispersión de matas del terreno y los vehículos provisionales (GLB públicos
    que no son el modelo real); los assets locales (Land Cruiser, Sprinter, Renderpeople) quedan visibles.
    """
    ocultos = []
    puntos = bpy.data.objects.get("UY_PAJA_BRAVA_DISPERSION")
    if puntos and not puntos.hide_render:
        puntos.hide_render = True
        ocultos.append(puntos.name)
    col = bpy.data.collections.get("11_VEHICULOS_PERSONAS")
    for ob in (col.all_objects if col else []):
        malla = ob.data.name if ob.type == "MESH" else ""
        provisional = malla.startswith(("UY_ASSET_SUV_", "UY_ASSET_TRANSFER_")) and "_LOCAL" not in malla
        if provisional and not ob.hide_render:
            ob.hide_render = True
            ocultos.append(ob.name)
    return {"ocultos_en_render": len(ocultos), "matas": "UY_PAJA_BRAVA_DISPERSION" in ocultos,
            "vehiculos_provisionales": sum(o != "UY_PAJA_BRAVA_DISPERSION" for o in ocultos)}


def cielo_nublado():
    """Una sola escena meteorológica adicional, con P1/P2 como propiedades."""
    existing = bpy.data.scenes.get("UYUNI_DIA_NUBLADO")
    if existing:
        return existing
    base = bpy.data.scenes["UYUNI_DIA"]
    sc = bpy.data.scenes.new("UYUNI_DIA_NUBLADO")
    for col in base.collection.children:
        if col.name == "08_LUZ_DIA":
            continue
        sc.collection.children.link(col)
    for key in base.keys():
        sc[key] = base[key]
    sc.camera = base.camera
    world = bpy.data.worlds.new("UY_CIELO_NUBLADO_PH")
    world.use_nodes = True; nt = world.node_tree; nt.nodes.clear()
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = imagen(ASSETS / "polyhaven/kloofendal_overcast/kloofendal_overcast_2k.hdr")
    bg = nt.nodes.new("ShaderNodeBackground"); bg.inputs["Strength"].default_value = .6
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(env.outputs["Color"], bg.inputs["Color"]); nt.links.new(bg.outputs[0], out.inputs["Surface"])
    sc.world = world; sc.world.lightgroup = "CIELO"
    sc["UY_CLIMA"] = "Nublado invernal; luz difusa HDRI CC0 Poly Haven"
    sc["UY_SOURCE"] = "https://polyhaven.com/a/kloofendal_overcast"
    return sc
