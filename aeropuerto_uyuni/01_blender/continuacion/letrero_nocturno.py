"""Difusores luminosos sobre el grafismo existente e interior cálido de noche.
Las caras luminosas copian los trazos CAD, incluidos sus agujeros y el reflejo
invertido. Solo se añaden a las escenas nocturnas; el acero original permanece.
"""
import math
import bpy
from mathutils import Vector

OWNER = 'uyuni_letrero_nocturno_20261004'
COLLECTION = '08_LETRERO_ILUMINADO'
DEFAULTS = {'emission_strength': 2.5, 'kelvin': 4000.0,
            'interior_attribute': .25, 'interior_fill_w': 600.0,
            'interior_kelvin': 3500.0, 'variant': 'A'}
TOKENS = ('LETRAS_UYUNI', 'REFLEJO_UYUNI', 'LINEA_HORIZONTE',
          'PIRAMIDES_SAL_3D', 'REFLEJO_MONTICULOS')


def material(cfg):
    name = 'UY_NEON_DIFUSOR_4000K'
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat['UY_OWNER'] = OWNER
    elif mat.get('UY_OWNER') != OWNER:
        raise RuntimeError('Material de neón ajeno')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    blackbody = nodes.new('ShaderNodeBlackbody')
    blackbody.inputs['Temperature'].default_value = cfg['kelvin']
    emission.inputs['Strength'].default_value = cfg['emission_strength']
    mat.node_tree.links.new(blackbody.outputs['Color'], emission.inputs['Color'])
    mat.node_tree.links.new(emission.outputs[0], output.inputs['Surface'])
    mat.diffuse_color = (1.0, .83, .62, 1.0)
    return mat


def diffuser(source, col, mat):
    """Frente luminoso de 4 mm, a 8 mm de las caras metálicas originales.
    Las triangulaciones existentes conservan todos los calados y la tipografía.
    """
    vertices, faces = [], []
    for face in source.data.polygons:
        normal = (source.matrix_world.to_3x3() @ face.normal).normalized()
        if normal.y > -.9:
            continue
        start = len(vertices)
        for index in face.vertices:
            point = source.matrix_world @ source.data.vertices[index].co
            vertices.append(tuple(point + normal * .008))
        faces.append(tuple(range(start, len(vertices))))
    if not faces:
        raise RuntimeError(f'Sin caras frontales en {source.name}')
    name = source.name.replace('UY_LETRERO_', 'UY_NEON_')
    obj = bpy.data.objects.get(name)
    if obj and (obj.type != 'MESH' or obj.get('UY_OWNER') != OWNER):
        raise RuntimeError(f'Objeto de neón ajeno: {name}')
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    if obj is None:
        obj = bpy.data.objects.new(name, mesh)
        obj['UY_OWNER'] = OWNER
        col.objects.link(obj)
    else:
        old = obj.data
        obj.data = mesh
        if old.users == 0:
            bpy.data.meshes.remove(old)
    solidify = next((m for m in obj.modifiers if m.type == 'SOLIDIFY'), None)
    if solidify is None:
        solidify = obj.modifiers.new('Espesor del difusor', 'SOLIDIFY')
    solidify.thickness, solidify.offset = .004, -1.0
    obj.lightgroup = 'LETRERO'
    obj.hide_render = False
    return {'name': name, 'source': source.name, 'faces': len(faces),
            'stand_off_m': .008, 'thickness_m': .004}


def interior_surfaces(col):
    """Acabado mate sobre el fondo/cielo existente, iluminado por las áreas reales.

    Evita que el fondo emisivo básico se lea como un plano blanco tras el vidrio.
    El piso y el recinto mantienen sus cotas; no se inventa mobiliario ni un IFC.
    """
    mat = bpy.data.materials.get('UY_NOCHE_INTERIOR_MATE')
    if mat is None:
        mat = bpy.data.materials.new('UY_NOCHE_INTERIOR_MATE')
        mat['UY_OWNER'] = OWNER
    elif mat.get('UY_OWNER') != OWNER:
        raise RuntimeError('Material interior ajeno')
    mat.use_nodes = True
    mat.node_tree.nodes.clear()
    output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
    shader = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    shader.inputs['Base Color'].default_value = (.62, .55, .44, 1)
    shader.inputs['Roughness'].default_value = .8
    mat.node_tree.links.new(shader.outputs[0], output.inputs['Surface'])
    source = bpy.data.objects['UY_INTERIOR_LUZ']
    vertices, faces = [], []
    for face in source.data.polygons:
        normal = (source.matrix_world.to_3x3() @ face.normal).normalized()
        if normal.y > -.9 and normal.z > -.9:
            continue
        start = len(vertices)
        for index in face.vertices:
            point = source.matrix_world @ source.data.vertices[index].co
            vertices.append(tuple(point + normal * .004))
        faces.append(tuple(range(start, len(vertices))))
    name = 'UY_NOCHE_INTERIOR_ACABADO_MATE'
    obj = bpy.data.objects.get(name)
    if obj and (obj.type != 'MESH' or obj.get('UY_OWNER') != OWNER):
        raise RuntimeError('Acabado interior ajeno')
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    if obj is None:
        obj = bpy.data.objects.new(name, mesh)
        obj['UY_OWNER'] = OWNER
        col.objects.link(obj)
    else:
        old = obj.data
        obj.data = mesh
        if old.users == 0:
            bpy.data.meshes.remove(old)
    obj.lightgroup = 'INTERIOR'
    obj.hide_render = False
    return {'name': name, 'source': source.name, 'faces': len(faces),
            'method': 'acabado_mate_con_luces_area_existentes', 'stand_off_m': .004}


def interior_fill(col, cfg):
    """Bañadores interiores dirigidos al fondo existente, detrás del vidrio."""
    grid = sorted((o for o in bpy.data.objects if o.type == 'LIGHT'
                   and o.name.startswith('UY_V031_AREA_INTERIOR_1_')), key=lambda o: o.location.x)
    if not grid:
        raise RuntimeError('Falta la fila de luminarias interiores de referencia')
    report = []
    for index, reference in enumerate(grid, 1):
        name = f'UY_NOCHE_INTERIOR_REFUERZO_{index:02d}'
        obj = bpy.data.objects.get(name)
        if obj is None:
            data = bpy.data.lights.new(name, 'AREA')
            obj = bpy.data.objects.new(name, data)
            obj['UY_OWNER'] = OWNER
            col.objects.link(obj)
        elif obj.type != 'LIGHT' or obj.get('UY_OWNER') != OWNER:
            raise RuntimeError(f'Luz interior ajena: {name}')
        data = obj.data
        data.shape = 'RECTANGLE'
        data.size, data.size_y = 2.0, .6
        data.energy = cfg['interior_fill_w']
        data.spread = math.radians(110)
        data.use_temperature, data.temperature = True, cfg['interior_kelvin']
        obj.location = (reference.location.x, 7.2, 6.4)
        target = Vector((reference.location.x, 8.896, 3.0))
        obj.rotation_euler = (target - obj.location).to_track_quat('-Z', 'Y').to_euler()
        obj.lightgroup = 'INTERIOR'
        obj.hide_render = False
        report.append({'name': name, 'energy_w': data.energy,
                       'kelvin': data.temperature, 'target': list(target)})
    return report


def aplicar(scenes=None, params=None):
    cfg = dict(DEFAULTS)
    cfg.update(params or {})
    if cfg['variant'] not in ('A', 'B'):
        raise ValueError('Variante de letrero desconocida')
    if scenes is None:
        night = bpy.data.scenes.get('UYUNI_CREPUSCULO')
        if night is None:
            raise RuntimeError('Falta la escena de hora azul')
        second = bpy.data.scenes.get('UYUNI_CREPUSCULO_P2_SALAR_LITIO')
        if second is None:
            second = night.copy()
            second.name = 'UYUNI_CREPUSCULO_P2_SALAR_LITIO'
            if second.compositing_node_group:
                second.compositing_node_group = second.compositing_node_group.copy()
                second.compositing_node_group.name = 'UY_NEON_OPTICA_P2'
        scenes = [night, second]
    else:
        scenes = list(scenes)
    if not scenes or any('CREPUSCULO' not in s.name for s in scenes):
        raise RuntimeError('La iluminación requiere escenas crepusculares')
    col = bpy.data.collections.get(COLLECTION)
    if col is None:
        col = bpy.data.collections.new(COLLECTION)
        col['UY_OWNER'] = OWNER
    elif col.get('UY_OWNER') != OWNER:
        raise RuntimeError('Colección de iluminación ajena')
    # Sustituye solo los bañadores de la prueba anterior de esta misma receta.
    for obj in list(col.objects):
        if obj.get('UY_OWNER') == OWNER and obj.type == 'LIGHT' and obj.name.startswith('UY_LETRERO_LUZ_'):
            data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if data.users == 0:
                bpy.data.lights.remove(data)
    for scene in scenes:
        palette = int(scene.name.endswith('_P2_SALAR_LITIO'))
        scene['propuesta'], scene['letras_corten'], scene['letras_gris'] = palette, 1 - palette, palette
        if col.name not in scene.collection.children:
            scene.collection.children.link(col)
        for layer in scene.view_layers:
            if layer.lightgroups.get('LETRERO') is None:
                layer.lightgroups.add(name='LETRERO')
        scene['luz_letrero'] = 0.0
        scene['luz_interior'] = cfg['interior_attribute']
        scene['UY_LETRERO_ILUMINACION'] = 'neon_difusores_trazos_CAD'
        scene['UY_LETRERO_KELVIN'] = cfg['kelvin']
        scene['UY_NEON_EMISSION_STRENGTH'] = cfg['emission_strength']
        scene['UY_NEON_INTERIOR_ATTRIBUTE'] = cfg['interior_attribute']
        if scene.compositing_node_group:
            for node in scene.compositing_node_group.nodes:
                if node.bl_idname == 'CompositorNodeRLayers':
                    node.scene = scene
    mat = material(cfg)
    report = []
    for token in TOKENS:
        source = bpy.data.objects.get(f'UY_LETRERO_{token}_{cfg["variant"]}')
        if source is None or source.type != 'MESH':
            raise RuntimeError(f'Falta la geometría CAD del letrero: {token}')
        report.append(diffuser(source, col, mat))
    interior = interior_surfaces(col)
    interior_lights = interior_fill(col, cfg)
    desired = {row['name'] for row in report + interior_lights} | {interior['name']}
    for obj in col.objects:
        if obj.get('UY_OWNER') == OWNER and obj.name not in desired:
            obj.hide_render = True
    return {'method': 'neon_difusores_trazos_CAD', 'scenes': [s.name for s in scenes],
            'diffusers': report, 'kelvin': cfg['kelvin'],
            'emission_strength': cfg['emission_strength'],
            'interior_attribute': cfg['interior_attribute'],
            'interior': interior,
            'interior_lights': interior_lights,
            'original_geometry_changed': False, 'metal_material_changed': False}
