"""Renderiza una franja horizontal de una cámara: la imagen completa, pero solo con contenido en la franja.

Sirve para renderizar en una CPU que se puede cortar, como un contenedor en la nube. Cada franja se guarda aparte y de
forma atómica, así que se retoma desde la última que terminó. Después, unir_bandas.py las une con un fundido en el
solape, para que no se note la costura del eliminador de ruido.

Usa los ajustes de los renders finales (02_postproduccion/MUESTREO_Y_RENDIMIENTO.md, sección 4):
  - umbral 0,008;
  - rebotes 12/6/6/12;
  - clamp indirecto 8;
  - light tree;
  - OIDN con albedo y normal.

Uso: python render_banda.py -- archivo.blend salida_sin_extension camara ancho muestras variante banda n_bandas solape_px
  variante: P1A, P2A, P1B... como en render_propuestas.py, con "-corten" o "-blanco" opcional para las letras.

Ejemplo, CAM_07 en 4K en cuatro franjas:
  for i in 0 1 2 3; do
    python render_banda.py -- ../uyuni_v2.blend renders/CAM_07_P1A CAM_07_PROPUESTAS 3840 384 P1A $i 4 32
  done
  python unir_bandas.py renders/CAM_07_P1A 4 32
"""
import os
import sys
import time

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
blend, salida, camara = args[0], args[1], args[2]
ancho, muestras, variante = int(args[3]), int(args[4]), args[5]
banda, n, solape = int(args[6]), int(args[7]), int(args[8])
ESCENAS = {"P1": "UYUNI_DIA", "P2": "UYUNI_DIA_P2_SALAR_LITIO"}
LETREROS = {"A": "LETRERO_A_SOBRESALE", "B": "LETRERO_B_CONTENIDO"}


def buscar(lc, nombre):
    if lc.name == nombre:
        return lc
    for h in lc.children:
        r = buscar(h, nombre)
        if r:
            return r


bpy.ops.wm.open_mainfile(filepath=blend)
base, _, letras = variante.partition("-")
sc = bpy.data.scenes[ESCENAS[base[:2]]]
for vl in sc.view_layers:
    vl.update()
    for clave, nombre in LETREROS.items():
        lc = buscar(vl.layer_collection, nombre)
        if lc:
            lc.exclude = clave != (base[2:] or "A")
if letras:
    sc["letras_corten"] = 1 if letras == "corten" else 0
sc.camera = bpy.data.objects[camara]

r, cy = sc.render, sc.cycles
alto = round(ancho * 9 / 16)
r.resolution_x, r.resolution_y, r.resolution_percentage = ancho, alto, 100
r.filter_size = 1.5
r.image_settings.file_format, r.image_settings.color_mode, r.image_settings.color_depth = "PNG", "RGBA", "16"
r.film_transparent = False
cy.device, cy.samples, cy.use_adaptive_sampling, cy.adaptive_threshold = "CPU", muestras, True, 0.008
cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 12, 6, 6, 12
cy.sample_clamp_indirect, cy.use_light_tree = 8.0, True
cy.use_denoising, cy.denoiser = True, "OPENIMAGEDENOISE"
cy.denoising_input_passes, cy.denoising_prefilter, cy.denoising_quality = "RGB_ALBEDO_NORMAL", "ACCURATE", "HIGH"

# la franja, en píxeles desde arriba, con el solape a cada lado
paso = alto / n
arriba = max(0, banda * paso - solape)
abajo = min(alto, (banda + 1) * paso + solape)
r.use_border, r.use_crop_to_border = True, False
r.border_min_x, r.border_max_x = 0.0, 1.0
r.border_max_y, r.border_min_y = 1 - arriba / alto, 1 - abajo / alto
r.filepath = f"{salida}_banda{banda}_tmp.png"
t = time.time()
bpy.ops.render.render(write_still=True, scene=sc.name)
# atómico: una franja a medias nunca cuenta como hecha
os.replace(f"{salida}_banda{banda}_tmp.png", f"{salida}_banda{banda}.png")
print(f"[BANDA] {variante} {banda + 1}/{n} filas {arriba:.0f}-{abajo:.0f} -> {time.time() - t:.0f} s", flush=True)
