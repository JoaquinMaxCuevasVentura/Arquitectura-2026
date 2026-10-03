"""Renderiza una cámara con las propuestas de color y las dos geometrías del letrero.

Uso:
  blender -b -P render_propuestas.py -- ../uyuni_v2.blend ../renders [camara] [ancho] [muestras] [variantes]
  python render_propuestas.py -- ...                                    (con el módulo bpy)

variantes: lista separada por comas (por defecto "P1A,P2A"):
  P1 / P2   propuesta: P1 Patrimonio Ferroviario (escena UYUNI_DIA) o P2 Salar & Litio (UYUNI_DIA_P2_SALAR_LITIO)
  A / B     geometría del letrero: A sobresale del antepecho, B contenida en sus 2,40 m
  -blanco / -corten   (opcional) material de las letras; si no se indica, el de la propuesta (P1 corten, P2 blanco)
  Ejemplo: P1A,P1B,P2A,P2B,P1A-blanco

Por defecto: CAM_07_PROPUESTAS, 3840 px de ancho (16:9), 512 muestras con muestreo adaptativo y eliminación de ruido
(OIDN con pases de albedo y normal). Guarda un PNG de 16 bits y un JPG de 8 bits con difuminado. Usa la GPU si hay
una; si no, la CPU. No modifica el .blend.
"""
import sys
import time

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
blend, salida = args[0], args[1]
camara = args[2] if len(args) > 2 else "CAM_07_PROPUESTAS"
ancho = int(args[3]) if len(args) > 3 else 3840
muestras = int(args[4]) if len(args) > 4 else 512
variantes = args[5].split(",") if len(args) > 5 else ["P1A", "P2A"]

ESCENAS = {"P1": ("UYUNI_DIA", "P1_PATRIMONIO_FERROVIARIO"), "P2": ("UYUNI_DIA_P2_SALAR_LITIO", "P2_SALAR_LITIO")}
LETREROS = {"A": "LETRERO_A_SOBRESALE", "B": "LETRERO_B_CONTENIDO"}


def usar_gpu(sc):
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for tipo in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
            try:
                prefs.compute_device_type = tipo
                prefs.get_devices()
                if any(d.type == tipo for d in prefs.devices):
                    for d in prefs.devices:
                        d.use = d.type == tipo
                    sc.cycles.device = "GPU"
                    return tipo
            except TypeError:
                continue
    except Exception as e:
        print("sin GPU:", e)
    sc.cycles.device = "CPU"
    return "CPU"


def geometria_letrero(sc, variante):
    def buscar(lc, nombre):
        if lc.name == nombre:
            return lc
        for h in lc.children:
            r = buscar(h, nombre)
            if r:
                return r
    for vl in sc.view_layers:
        vl.update()
        for clave, nombre in LETREROS.items():
            lc = buscar(vl.layer_collection, nombre)
            if lc:
                lc.exclude = clave != variante


bpy.ops.wm.open_mainfile(filepath=blend)
for v in variantes:
    base, _, letras = v.partition("-")
    prop, geom = base[:2], base[2:] or "A"
    nombre_escena, etiqueta = ESCENAS[prop]
    sc = bpy.data.scenes[nombre_escena]
    if bpy.context.window:
        bpy.context.window.scene = sc
    geometria_letrero(sc, geom)
    if letras:
        sc["letras_corten"] = 1 if letras == "corten" else 0
    sc.camera = bpy.data.objects[camara]
    r, cy = sc.render, sc.cycles
    r.resolution_x, r.resolution_y, r.resolution_percentage = ancho, int(round(ancho * 9 / 16)), 100
    r.filter_size = 1.5
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGB"
    r.image_settings.color_depth = "16"
    r.dither_intensity = 1.0                 # difuminado al pasar a 8 bits: sin bandas en el cielo
    cy.samples = muestras
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.008
    cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 12, 6, 6, 12
    cy.sample_clamp_indirect = 8.0           # evita luciérnagas sin apagar los reflejos
    cy.use_light_tree = True
    try:
        cy.use_denoising = True
        cy.denoiser = "OPENIMAGEDENOISE"
        cy.denoising_input_passes = "RGB_ALBEDO_NORMAL"
        cy.denoising_prefilter = "ACCURATE"
        cy.denoising_quality = "HIGH"
    except (AttributeError, TypeError) as e:
        print("OIDN parcial:", e)
    dispositivo = usar_gpu(sc)
    sufijo = f"_letrero_{geom}" + (f"_letras_{letras}" if letras else "")
    r.filepath = f"{salida}/{camara}_{etiqueta}{sufijo}.png"
    t = time.time()
    bpy.ops.render.render(write_still=True, scene=sc.name)
    # además un JPG de 8 bits (calidad 95) listo para presentar o subir al upscaler
    r.image_settings.file_format = "JPEG"
    r.image_settings.quality = 95
    bpy.data.images["Render Result"].save_render(filepath=r.filepath[:-4] + ".jpg", scene=sc)
    print(f"[RENDER] {etiqueta}{sufijo} {camara} {ancho}px {muestras} muestras ({dispositivo}) -> {time.time() - t:.1f} s")
