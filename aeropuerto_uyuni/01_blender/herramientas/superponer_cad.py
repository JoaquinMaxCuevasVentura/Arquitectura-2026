"""Superpone las líneas del CAD (en rojo) sobre los renders ortogonales que genera verificar_alzados.py.

Uso:
  python superponer_cad.py <carpeta_renders> ../../00_auditoria/vistas <carpeta_salida>
Requiere Pillow (pip install pillow). Genera SUPERPOSICION_<vista>.jpg y dos láminas resumen.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

renders, vistas, salida = sys.argv[1:4]
indice = json.load(open(os.path.join(vistas, "vistas_index.json"), encoding="utf-8"))
ALZADOS = ["FACHADA_NORESTE_ACTUAL", "FACHADA_SUROESTE", "FACHADA_ESTE", "FACHADA_OESTE"]
CORTES = ["CORTE_ACTUAL_POR_M1", "CORTE_ACTUAL_MURO_CIEGO"]
os.makedirs(salida, exist_ok=True)


def fuente_ttf(tam):
    """Fuente con tildes: DejaVu (Linux) o Arial (Windows); si no hay, la de Pillow."""
    for ruta in ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(ruta, tam)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=tam)
    except TypeError:                  # Pillow < 10.1
        return ImageFont.load_default()


fuente = fuente_ttf(26)


def superponer(nombre):
    modelo = Image.open(os.path.join(renders, f"MODELO_{nombre}.png")).convert("RGB")
    cad = Image.open(os.path.join(vistas, indice[nombre]["png"])).convert("L")
    if cad.size != modelo.size:
        cad = cad.resize(modelo.size, Image.LANCZOS)
    lineas = ImageOps.invert(cad)                                            # 255 = línea del CAD
    base = Image.blend(modelo, Image.new("RGB", modelo.size, "white"), 0.15)  # modelo apenas aclarado
    alfa = lineas.point(lambda v: min(200, int(1.6 * v)))                    # trazo rojo semitransparente
    out = Image.composite(Image.new("RGB", modelo.size, (225, 0, 35)), base, alfa)
    barra = 44
    lam = Image.new("RGB", (out.width, out.height + barra), "white")
    lam.paste(out, (0, barra))
    ImageDraw.Draw(lam).text((12, 8), f"{nombre}: modelo + CAD en rojo  |  {indice[nombre].get('a_ifc', '')}",
                             fill=(0, 0, 0), font=fuente)
    lam.save(os.path.join(salida, f"SUPERPOSICION_{nombre}.jpg"), quality=88)
    return lam


def lamina(imagenes, archivo, ancho, columnas):
    celdas = [im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS) for im in imagenes]
    filas = [celdas[i:i + columnas] for i in range(0, len(celdas), columnas)]
    alto = sum(max(c.height for c in f) for f in filas) + 16 * (len(filas) + 1)
    hoja = Image.new("RGB", (columnas * ancho + 16 * (columnas + 1), alto), (235, 235, 235))
    y = 16
    for f in filas:
        for k, c in enumerate(f):
            hoja.paste(c, (16 + k * (ancho + 16), y))
        y += max(c.height for c in f) + 16
    hoja.save(os.path.join(salida, archivo), quality=85)


hechas = {n: superponer(n) for n in ALZADOS + CORTES if os.path.exists(os.path.join(renders, f"MODELO_{n}.png"))}
if any(n in hechas for n in ALZADOS):
    lamina([hechas[n] for n in ALZADOS if n in hechas], "lamina_verificacion_alzados.jpg", 2200, 1)
if any(n in hechas for n in CORTES):
    lamina([hechas[n] for n in CORTES if n in hechas], "lamina_verificacion_cortes.jpg", 1100, 2)
print("superposiciones:", ", ".join(hechas))
