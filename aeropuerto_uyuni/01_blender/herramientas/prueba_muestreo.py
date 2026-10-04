"""Prueba de muestreo y caminos de luz de Cycles en la escena del aeropuerto: qué ajustes pagan y cuáles no.

Pone a prueba en nuestra escena un análisis de Cycles que recomienda:
  - umbral de ruido 0,03 con tope de 2048 muestras y mínimo de 16;
  - rebotes cortos (4/2/2/4);
  - cáusticas reflectivas apagadas;
  - clamp indirecto 10.
Y que sostiene que el poligonaje casi no pesa en el tiempo de render.

Vista CAM_07_PROPUESTAS con P2, la más exigente en rebotes por el blanco integral, letrero A, a 1280 × 720. Todas las
variantes usan OIDN con albedo y normal y prefiltro ACCURATE:
  R      referencia: los ajustes de los renders finales:
           - umbral 0,008, tope 384 y mínimo automático;
           - rebotes 12/6/6/12 y transparentes 8;
           - clamp indirecto 8;
           - las dos cáusticas encendidas, como vienen.
  R2     R con otra semilla: lo que cambia entre R y R2 es el ruido que le queda a R (el piso de la comparación)
  U3     la receta de muestreo del análisis: umbral 0,03, tope 2048, mínimo 16
  U3B    umbral 0,03 con nuestro tope de 384 y el mínimo automático
  U3SD   U3 sin eliminar el ruido: la receta del análisis para animación (dice que el ruido queda como grano)
  RB     los rebotes del análisis: total 4, difusos 2, especulares 2, transmisión 4
  SC     sin cáusticas reflectivas
  PG     path guiding (solo en CPU)
  R1K    R con tope de 1024: dice si el tope de 384 limita
  POLI0 / POLI1  poligonaje:
           - CAM_05 a 960 px y 128 muestras;
           - letras tal cual y subdivididas con Simple (misma forma, millones de triángulos).
  N10 / N4 / N0  noche:
           - CAM_03 de la escena que guarda prueba_noche.py (prueba_noche.blend);
           - con su muestreo (128, umbral 0,01) y clamp indirecto 10, 4 y sin clamp.
  VC1 / VC0 / VC1N / VST0 / VST1  vidrio y sol, en una escena aparte:
           - un muro gris con una ventana de 2 × 2 m: la mitad con el vidrio del modelo y la otra mitad abierta;
           - el sol de la mañana entra al piso de adentro;
           - mide cuánto sol pasa por el vidrio (la mancha del piso, contra la mitad abierta);
           - VC1: cáusticas refractivas encendidas (como vienen); VC0: apagadas; VC1N: encendidas y sin clamp;
           - VST0 y VST1: vidrio transparente para los rayos de sombra (Light Path > Is Shadow Ray con Transparent
             BSDF del color del tinte), con las cáusticas refractivas apagadas y encendidas.
  VT     transmitancia del vidrio, medida limpia: sin sol y con el cielo negro, un panel emisivo uniforme afuera; la
         cámara lo ve por las dos mitades de la ventana y el cociente es la luz que deja pasar el vidrio.

Cada variante guarda:
  - un PNG de 16 bits con la transformación de vista de la escena;
  - un EXR multicapa con la imagen sin ruido, la imagen con ruido y el pase de conteo de muestras;
  - su línea en registro.json: tiempo total, preparación (sincronizar y BVH), memoria pico y triángulos.
Conviene correr cada variante en su propio proceso, para que la memoria pico sea la de esa variante. Se puede retomar:
lo que ya está no se repite. Los números y la hoja los saca hoja_muestreo.py.

Uso: python prueba_muestreo.py -- archivo.blend carpeta [variantes] [prueba_noche.blend]
     variantes separadas por comas; por defecto, todas
"""
import json
import math
import os
import re
import resource
import sys
import time

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
blend, salida = os.path.abspath(args[0]), os.path.abspath(args[1])
TODAS = ["R", "R2", "U3", "U3B", "U3SD", "RB", "SC", "PG", "POLI0", "POLI1", "N10", "N4", "N0", "R1K",
         "VC1", "VC0", "VC1N", "VST0", "VST1", "VT"]
pedidas = args[2].split(",") if len(args) > 2 and args[2] else TODAS
blend_noche = os.path.abspath(args[3]) if len(args) > 3 else None
os.makedirs(salida, exist_ok=True)
REGISTRO = os.path.join(salida, "registro.json")

# ajustes de los renders finales (render_propuestas.py); cada variante cambia solo lo suyo
BASE = dict(samples=384, adaptive_threshold=0.008, adaptive_min_samples=0, seed=0,
            max_bounces=12, diffuse_bounces=6, glossy_bounces=6, transmission_bounces=12,
            transparent_max_bounces=8, volume_bounces=0, sample_clamp_direct=0.0, sample_clamp_indirect=8.0,
            caustics_reflective=True, caustics_refractive=True, use_guiding=False, use_light_tree=True)
VARIANTES = {
    "R": ("dia", {}),
    "R2": ("dia", dict(seed=1)),
    "U3": ("dia", dict(adaptive_threshold=0.03, samples=2048, adaptive_min_samples=16)),
    "U3B": ("dia", dict(adaptive_threshold=0.03)),
    "U3SD": ("dia", dict(adaptive_threshold=0.03, samples=2048, adaptive_min_samples=16, use_denoising=False)),
    "RB": ("dia", dict(max_bounces=4, diffuse_bounces=2, glossy_bounces=2, transmission_bounces=4)),
    "SC": ("dia", dict(caustics_reflective=False)),
    "PG": ("dia", dict(use_guiding=True)),
    "R1K": ("dia", dict(samples=1024)),
    "POLI0": ("poli", dict(samples=128)),
    "POLI1": ("poli", dict(samples=128)),
    "N10": ("noche", dict(sample_clamp_indirect=10.0)),
    "N4": ("noche", dict(sample_clamp_indirect=4.0)),
    "N0": ("noche", dict(sample_clamp_indirect=0.0)),
    "VC1": ("vidrio", dict(samples=256, adaptive_threshold=0.01)),
    "VC0": ("vidrio", dict(samples=256, adaptive_threshold=0.01, caustics_refractive=False)),
    "VC1N": ("vidrio", dict(samples=256, adaptive_threshold=0.01, sample_clamp_indirect=0.0)),
    "VST0": ("vidrio", dict(samples=256, adaptive_threshold=0.01, caustics_refractive=False)),
    "VST1": ("vidrio", dict(samples=256, adaptive_threshold=0.01)),
    "VT": ("vidrio", dict(samples=256, adaptive_threshold=0.01)),
}
RAPIDA = bool(os.environ.get("PRUEBA_RAPIDA"))       # ensayo del script: un cuarto del ancho y 16 muestras
TRIANGULOS_POLI = 1e6 if RAPIDA else 12e6             # meta de la variante subdividida (el contenedor tiene 15 GB)

try:
    with open(REGISTRO) as f:
        registro = json.load(f)
except (OSError, ValueError):
    registro = {}


def buscar(lc, nombre):
    if lc.name == nombre:
        return lc
    for h in lc.children:
        r = buscar(h, nombre)
        if r:
            return r


def triangulos(sc):
    """Triángulos que ve el render en la escena, con instancias (cuenta del depsgraph de la vista)."""
    vl = sc.view_layers[0]
    vl.update()                       # crea y evalúa el depsgraph de la capa si todavía no existe
    dg = vl.depsgraph
    cache, total = {}, 0
    for inst in dg.object_instances:
        ob = inst.object
        if ob.type != "MESH":
            continue
        if ob.data.name not in cache:
            me = ob.data
            cache[ob.data.name] = len(me.loops) - 2 * len(me.polygons)     # suma de (lados - 2) de cada cara
        total += cache[ob.data.name]
    return total


def escena_vidrio(sombra_transparente, medir_transmitancia=False):
    """Muro gris con una ventana de 2 × 2 m (mitad con el vidrio del modelo, mitad abierta) y el sol de la mañana. Devuelve
    la escena y los puntos donde se mide: el piso iluminado por cada mitad, el piso a la sombra del muro y el exterior
    visto a través de cada mitad."""
    import bmesh
    from mathutils import Matrix, Vector
    base = bpy.data.scenes["UYUNI_DIA_P2_SALAR_LITIO"]
    sc = bpy.data.scenes.new("PRUEBA_VIDRIO_SOL")
    sc.render.engine, sc.world = "CYCLES", base.world
    for k in ("view_transform", "look", "exposure", "gamma"):
        setattr(sc.view_settings, k, getattr(base.view_settings, k))
    sol = next(o for o in base.objects if o.type == "LIGHT" and o.data.type == "SUN")
    sc.collection.objects.link(sol)
    d = (sol.matrix_world.to_quaternion() @ Vector((0, 0, -1))).normalized()     # hacia donde viaja la luz
    h = Vector((d.x, d.y, 0)).normalized()          # +h: adentro; el sol pega desde -h
    s = Vector((h.y, -h.x, 0))                      # a lo largo del muro (s, h, z es una base derecha)
    z = Vector((0, 0, 1))
    tan_e = -d.z / Vector((d.x, d.y, 0)).length

    def gris(nombre):
        m = bpy.data.materials.new(nombre)
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value, b.inputs["Roughness"].default_value = (0.3, 0.3, 0.3, 1), 1.0
        return m

    def caja(nombre, s0, s1, h0, h1, z0, z1, mat):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        c = (s0 + s1) / 2 * s + (h0 + h1) / 2 * h + (z0 + z1) / 2 * z
        M = Matrix([[s.x * (s1 - s0), h.x * (h1 - h0), 0, c.x], [s.y * (s1 - s0), h.y * (h1 - h0), 0, c.y],
                    [0, 0, z1 - z0, c.z], [0, 0, 0, 1]])
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        me = bpy.data.meshes.new(nombre)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(mat)
        ob = bpy.data.objects.new(nombre, me)
        sc.collection.objects.link(ob)
        return ob

    piso, muro = gris("PRUEBA_PISO"), gris("PRUEBA_MURO")
    caja("PRUEBA_PISO", -20, 20, -20, 20, -0.1, 0.0, piso)
    for i, (s0, s1, z0, z1) in enumerate([(-4, -1, 0, 3.2), (1, 4, 0, 3.2), (-1, 1, 0, 0.8), (-1, 1, 2.8, 3.2)]):
        caja(f"PRUEBA_MURO_{i}", s0, s1, -0.1, 0.1, z0, z1, muro)
    vidrio = bpy.data.materials["UY_VIDRIO_CONTROL_SOLAR"]
    if sombra_transparente:
        # truco de arquitectura: para los rayos de sombra el vidrio es un Transparent BSDF del color del tinte
        vidrio = vidrio.copy()
        nt = vidrio.node_tree
        salida_mat = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
        superficie = salida_mat.inputs["Surface"].links[0].from_socket
        bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        lp, tr, mix = (nt.nodes.new(t) for t in ("ShaderNodeLightPath", "ShaderNodeBsdfTransparent", "ShaderNodeMixShader"))
        tr.inputs["Color"].default_value = bsdf.inputs["Base Color"].default_value
        nt.links.new(lp.outputs["Is Shadow Ray"], mix.inputs["Fac"])
        nt.links.new(superficie, mix.inputs[1])
        nt.links.new(tr.outputs["BSDF"], mix.inputs[2])
        nt.links.new(mix.outputs["Shader"], salida_mat.inputs["Surface"])
    caja("PRUEBA_VIDRIO", -1, 0, -0.0135, 0.0135, 0.8, 2.8, vidrio)       # paño de 27 mm, como en el modelo
    if medir_transmitancia:
        # sin sol y con el mundo negro: lo único que ve la cámara por la ventana es un panel emisivo de fuerza 1
        sc.collection.objects.unlink(sol)
        sc.world = bpy.data.worlds.new("PRUEBA_NEGRO")
        sc.world.use_nodes = True
        sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
        panel = bpy.data.materials.new("PRUEBA_PANEL")
        panel.use_nodes = True
        b = next(n for n in panel.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (0, 0, 0, 1)
        b.inputs["Emission Color"].default_value, b.inputs["Emission Strength"].default_value = (1, 1, 1, 1), 1.0
        caja("PRUEBA_PANEL", -8, 8, -3.2, -3.0, -1.0, 8.0, panel)
    hp = 1.8 / tan_e                                # el centro de la ventana cae en el piso a hp de adentro
    cam_d = bpy.data.cameras.new("PRUEBA_CAM")
    cam_d.lens, cam_d.sensor_width = 18, 36
    cam = bpy.data.objects.new("PRUEBA_CAM", cam_d)
    sc.collection.objects.link(cam)
    pos, mira = (hp + 3.0) * h + 2.2 * z, (hp - 1.0) * h + 0.6 * z
    cam.matrix_world = Matrix.Translation(pos) @ (mira - pos).to_track_quat("-Z", "Y").to_matrix().to_4x4()
    sc.camera = cam
    puntos = {"piso_vidrio": -0.5 * s + hp * h, "piso_abierto": 0.5 * s + hp * h, "piso_sombra": 2.5 * s + hp * h,
              "vista_vidrio": -0.5 * s + 1.2 * z, "vista_abierta": 0.5 * s + 1.2 * z}
    print(f"[VIDRIO] elevación del sol {math.degrees(math.atan(tan_e)):.1f}°, mancha a {hp:.2f} m del muro", flush=True)
    return sc, puntos


def preparar(nombre):
    tipo, cambios = VARIANTES[nombre]
    if tipo == "noche":
        if not blend_noche:
            raise SystemExit(f"{nombre}: falta prueba_noche.blend (cuarto argumento)")
        bpy.ops.wm.open_mainfile(filepath=blend_noche)
        sc = bpy.data.scenes["UYUNI_CREPUSCULO"]
        ajustes = dict(samples=128, adaptive_threshold=0.01, **cambios)        # el muestreo de prueba_noche.py
        ancho = 1280
    elif tipo == "vidrio":
        bpy.ops.wm.open_mainfile(filepath=blend)
        sc, puntos = escena_vidrio(nombre.startswith("VST"), medir_transmitancia=nombre == "VT")
        ajustes = dict(BASE, **cambios)
        ancho = 960
    else:
        bpy.ops.wm.open_mainfile(filepath=blend)
        sc = bpy.data.scenes["UYUNI_DIA_P2_SALAR_LITIO"]
        for vl in sc.view_layers:
            vl.update()
            for clave, coleccion in (("A", "LETRERO_A_SOBRESALE"), ("B", "LETRERO_B_CONTENIDO")):
                lc = buscar(vl.layer_collection, coleccion)
                if lc:
                    lc.exclude = clave != "A"
        sc.camera = bpy.data.objects["CAM_07_PROPUESTAS" if tipo == "dia" else "CAM_05_LETRERO_HORIZONTE"]
        ajustes = dict(BASE, **cambios)
        ancho = 1280 if tipo == "dia" else 960
    if RAPIDA:
        ancho, ajustes["samples"] = ancho // 4, min(ajustes["samples"], 16)
    r, cy = sc.render, sc.cycles
    r.resolution_x, r.resolution_y, r.resolution_percentage = ancho, round(ancho * 9 / 16), 100
    r.filter_size, r.film_transparent = 1.5, False
    cy.device, cy.use_adaptive_sampling = "CPU", True
    cy.use_denoising, cy.denoiser = True, "OPENIMAGEDENOISE"
    cy.denoising_input_passes, cy.denoising_prefilter, cy.denoising_quality = "RGB_ALBEDO_NORMAL", "ACCURATE", "HIGH"
    for k, v in ajustes.items():
        setattr(cy, k, v)
    if hasattr(sc, "compositing_node_group"):
        sc.compositing_node_group = None          # se comparan renders, no la óptica del compositor
    for vl in sc.view_layers:
        vl.cycles.pass_debug_sample_count = True  # pase "Debug Sample Count": muestras de cada píxel / tope
        vl.cycles.denoising_store_passes = True   # guarda también la imagen con ruido
    tri, extra = triangulos(sc), {}
    if tipo == "vidrio":
        from bpy_extras.object_utils import world_to_camera_view
        alto = round(ancho * 9 / 16)
        extra["puntos"] = {k: (world_to_camera_view(sc, sc.camera, p).x * ancho,
                               (1 - world_to_camera_view(sc, sc.camera, p).y) * alto) for k, p in puntos.items()}
    if nombre == "POLI1":
        letras = [o for o in bpy.data.collections["LETRERO_A_SOBRESALE"].all_objects if o.type == "MESH"]
        dg = sc.view_layers[0].depsgraph
        mallas = [o.evaluated_get(dg).data for o in letras]
        esquinas = sum(len(me.loops) for me in mallas)
        antes = sum(len(me.loops) - 2 * len(me.polygons) for me in mallas)
        # Simple: en el nivel 1 cada cara de n lados da n cuadriláteros, y después cada nivel multiplica por 4
        nivel = 1
        while 2 * esquinas * 4 ** nivel <= TRIANGULOS_POLI and nivel < 8:
            nivel += 1
        despues = 2 * esquinas * 4 ** (nivel - 1)
        for o in letras:      # solo en el render (levels 0): la cuenta y la memoria de la vista no cambian
            m = o.modifiers.new("PRUEBA_POLIGONAJE", "SUBSURF")
            m.subdivision_type, m.levels, m.render_levels = "SIMPLE", 0, nivel
        tri += despues - antes
        extra = dict(nivel_subdivision=nivel, triangulos_letras_antes=antes, triangulos_letras=despues)
    return sc, dict(ajustes=ajustes, ancho=ancho, triangulos=tri, **extra)


def render(nombre):
    png, exr = f"{salida}/{nombre}.png", f"{salida}/{nombre}.exr"
    if nombre in registro and os.path.exists(png) and os.path.exists(exr):
        print(f"[MUESTREO] {nombre} ya está ({registro[nombre]['tiempo']:.0f} s)", flush=True)
        return
    sc, datos = preparar(nombre)
    r = sc.render
    r.image_settings.media_type = "MULTI_LAYER_IMAGE"         # Blender 5: el EXR multicapa es un tipo de medio
    r.image_settings.file_format, r.image_settings.color_depth = "OPEN_EXR_MULTILAYER", "16"
    r.image_settings.exr_codec = "ZIP"
    r.filepath = exr
    estados = []

    def estado(texto, *_):
        estados.append((time.time(), str(texto)))
    bpy.app.handlers.render_stats.append(estado)
    t = time.time()
    bpy.ops.render.render(write_still=True, scene=sc.name)
    total = time.time() - t
    bpy.app.handlers.render_stats.remove(estado)
    # preparación: hasta la primera muestra (sincronizar escena, cargar núcleos, construir BVH)
    primera = next((ts for ts, s in estados if re.search(r"Sample \d+/\d+", s)), None)
    cycles_mb = [float(x) for _, s in estados for x in re.findall(r"Mem: ?([\d.]+)M", s)]
    r.image_settings.media_type = "IMAGE"
    r.image_settings.file_format, r.image_settings.color_mode, r.image_settings.color_depth = "PNG", "RGB", "16"
    bpy.data.images["Render Result"].save_render(filepath=png, scene=sc)
    registro[nombre] = dict(datos, tiempo=total, preparacion=(primera - t) if primera else None,
                            memoria_cycles_mb=max(cycles_mb) if cycles_mb else None,
                            memoria_pico_proceso_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
                            estados=[s for _, s in estados[:3] + estados[-2:]])
    try:                                   # otro proceso pudo escribir mientras tanto: se relee antes de guardar
        with open(REGISTRO) as f:
            registro.update({k: v for k, v in json.load(f).items() if k != nombre})
    except (OSError, ValueError):
        pass
    with open(REGISTRO, "w") as f:
        json.dump(registro, f, indent=1)
    prep = f", preparación {registro[nombre]['preparacion']:.0f} s" if primera else ""
    print(f"[MUESTREO] {nombre} -> {total:.0f} s{prep}, {datos['triangulos'] / 1e6:.2f} M triángulos, "
          f"pico {registro[nombre]['memoria_pico_proceso_mb']:.0f} MB", flush=True)


for v in pedidas:
    render(v)
