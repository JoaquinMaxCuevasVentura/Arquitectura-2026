"""Láminas con grabados de Boitard: Fig. 1 (puentes) y Fig. 5 (escena exótica).

Uso: python3 boitard.py carpeta_fuentes carpeta_atlas carpeta_salida

carpeta_atlas tiene las hojas del atlas bajadas de Internet Archive (A039a019):
n88.jpg, n90.jpg, n92.jpg, n94.jpg, n96.jpg y n98.jpg (láminas 27–32), y
n34_full.jpg (Pl. 1ère, a resolución completa). Los grabados van como están:
recortados y reducidos, sin retoque ni color.

Son borradores hechos por la máquina para que el autor los confronte.
"""
import base64
import io
import os
import sys

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

from svg import (AMARILLO, B, F, GRIS, Hoja, ancho, esc, numero, partir,  # noqa: E402
                 texto, texto_lineas)

GRIS_TX = "#6e6e6e"


def grabado(ruta, caja, ancho_px, calidad=80):
    """Recorta y reduce una hoja del atlas; devuelve (ancho, alto, base64 JPEG)."""
    im = Image.open(ruta).convert("RGB").crop(caja)
    if im.width > ancho_px:
        im = im.resize((ancho_px, round(im.height * ancho_px / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=calidad, optimize=True, progressive=True)
    return im.width, im.height, base64.b64encode(buf.getvalue()).decode()


def imagen(h, x, y, w, alto, b64):
    h.add(f'<image x="{x}" y="{y}" width="{w}" height="{alto}" preserveAspectRatio="xMidYMid meet" '
          f'xlink:href="data:image/jpeg;base64,{b64}"/>')


def parrafo(h, x, y, t, ancho_mm, tam=2.2, fuente="g400", color=F, inter=1.32):
    """Párrafo cortado a ancho_mm; devuelve la y de la línea siguiente."""
    clase = {"g400": "g", "gi400": "gi", "g600": "g", "p400": "", "p500": "b"}[fuente]
    lineas = partir(t, ancho_mm, fuente, tam)
    h.add(texto_lineas(x, y, lineas, tam, inter, color=color, clase=clase))
    return y + len(lineas) * tam * inter


def resaltar(h, x, y, linea, frase, tam=2.2, fuente="g400"):
    """Banda amarilla detrás de una frase dentro de una línea ya escrita en (x, y)."""
    i = linea.find(frase)
    if i < 0:
        raise ValueError(f"no está: {frase!r}")
    x0 = x + ancho(linea[:i], fuente, tam)
    w = ancho(frase, fuente, tam)
    h.add(f'<rect x="{x0 - 0.3:.2f}" y="{y - tam * 0.78:.2f}" width="{w + 0.6:.2f}" '
          f'height="{tam * 1.02:.2f}" fill="{AMARILLO}" fill-opacity="0.75"/>')


def encabezado(h, n, titulo, sub):
    h.add(texto(14, 16.0, titulo, 4.4, F, clase="g", peso=600))
    y = 21.6
    for ln in sub:
        h.add(texto(14, y, ln, 2.4, F, clase="g"))
        y += 3.2
    h.add(texto(287, 14.0, f"Fig. {n}", 3.4, F, clase="g", ancla="end", peso=600))


# ============================================================================
# Fig. 1: los puentes del atlas
# ============================================================================
# Hoja del atlas, lámina, título, figuras (todas sobre agua dibujada) y recorte
# en píxeles de la hoja (el grabado con su número y su título, más un margen).
PUENTES = [
    ("n88.jpg", 27, "Passerelles et ponts", 6, (275, 66, 1576, 997)),
    ("n90.jpg", 28, "Ponts pittoresques et rustiques", 6, (207, 80, 1494, 980)),
    ("n92.jpg", 29, "Ponts pittoresques", 6, (298, 74, 1592, 995)),
    ("n94.jpg", 30, "Ponts pittoresques", 6, (222, 73, 1492, 966)),
    ("n96.jpg", 31, "Ponts pittoresques", 6, (257, 74, 1532, 986)),
    ("n98.jpg", 32, "Ponts de fil de fer", 2, (190, 79, 1477, 973)),
]


def fig1(carpeta_fuentes, atlas, salida):
    h = Hoja(297, 210, carpeta_fuentes)
    encabezado(h, 1, "Treinta y dos puentes, todos sobre agua", [
        "Las seis láminas de puentes del atlas de Boitard (27–32). En cada figura, el puente cruza "
        "agua dibujada: un río, un canal, un torrente o una cascada."])

    cw, ch_ = 82.0, 57.0
    xs = (14.0, 107.5, 201.0)
    ys = (29.0, 96.0)
    total = 0
    for i, (hoja, lam, titulo, n, caja) in enumerate(PUENTES):
        x, y = xs[i % 3], ys[i // 3]
        w_px, h_px, b64 = grabado(os.path.join(atlas, hoja), caja, 900)
        k = min(cw / w_px, ch_ / h_px)
        w, alto = w_px * k, h_px * k
        imagen(h, round(x + (cw - w) / 2, 2), round(y + (ch_ - alto) / 2, 2), round(w, 2), round(alto, 2), b64)
        h.add(texto_lineas(x, y + ch_ + 4.2, [[
            (f"lám. {lam}, ", "", B), (titulo, "gi", B),
            (f"  ·  {n} figuras, {n} sobre agua", "", B)]], 2.0, color=B))
        total += n
    assert total == 32

    # --- la regla (Boitard), con lo que la copia no hizo en amarillo
    x, y = 14.0, 168.0
    h.add(texto(x, y, "La regla  (Boitard s. f.)", 2.3, B, peso=500))
    regla = [
        "«Dans tous les cas, quel que soit le parti agréable que l'on puisse tirer d'un pont,",
        "il faudra qu'il soit rigoureusement motivé, car rien n'est plus ridicule qu'un pont sans eau",
        "ou au moins sans une nécessité indispensable, comme celle par exemple de passer sur un",
        "précipice, ou sur un ravin très-escarpé» (238).",
    ]
    y += 4.4
    for j, ln in enumerate(regla):
        if "rien n'est plus" in ln:
            resaltar(h, x, y + j * 2.2 * 1.32, ln, "rien n'est plus ridicule qu'un pont sans eau")
    h.add(texto_lineas(x, y, regla, 2.2, 1.32, color=B, clase="g"))
    y += len(regla) * 2.2 * 1.32 + 1.2
    parrafo(h, x, y, "Y es la fábrica más fácil de justificar: «rien qui soit plus facile à motiver, "
            "car il ne s'agit que de conduire un chemin, un simple sentier, sur le bord d'un ruisseau "
            "ou d'une rivière» (233).", 112, 2.2, "g400", B)

    # --- la copia (Flaubert)
    x, y = 136.0, 168.0
    h.add(texto(x, y, "La copia  (Flaubert 1910)", 2.3, F, peso=500))
    y = parrafo(h, x, y + 4.4, "«Dans l'autre partie du potager, une espèce de Rialto enjambait un bassin […]. "
                "La terre buvait l'eau, n'importe ! Il se formerait un fond de glaise qui la retiendrait» (55).",
                88, 2.2)
    y = parrafo(h, x, y + 1.0, "El día de la cena, «Pour emplir le bassin, Bouvard et Pécuchet avaient "
                "charrié de l'eau pendant toute la matinée. Elle avait fui entre les pierres du fond, "
                "mal jointes» (61–62).", 88, 2.2)
    parrafo(h, x, y + 1.0, "Desde el comedor, «le pont vénitien un accent circonflexe par-dessus "
            "les haricots» (61).", 88, 2.2)

    # --- convención y créditos
    x = 232.0
    h.add(f'<rect x="{x}" y="166.0" width="7" height="2.4" fill="{AMARILLO}" fill-opacity="0.75"/>')
    h.add(texto_lineas(x + 9, 167.8, ["lo que la regla pedía", "y la copia no hizo"], 1.9, 1.3))
    h.add(texto_lineas(x, 176.0, partir(
        "Hojas 88 a 98 del atlas: Boitard (s. f.), Internet Archive A039a019, ejemplar de la "
        "Biblioteca de la Universidad de Sevilla, Public Domain Mark 1.0. Recortadas y reducidas, "
        "sin retoque. Conteo y montaje: borrador de la máquina (Claude, Anthropic), a pedido del "
        "autor, para verificar.", 54, "g400", 1.8), 1.8, 1.3, clase="g"))
    h.guardar(salida)


# ============================================================================
# Fig. 5: la escena exótica (Pl. 1ère)
# ============================================================================
EXO_HOJA = "n34_full.jpg"
EXO_CAJA = (500, 160, 3045, 1945)     # píxeles de la hoja a resolución completa
EXO_ESC = 3539 / 1770                 # las posiciones se midieron en la copia de 1770 px

# En el orden en que Boitard describe la lámina (63–65): número, nombre, lo que
# dice de ella, página, posición en la copia de 1770 px y color: B (solo
# Boitard), F (aparece en Flaubert), Y (lo que la escena pedía).
EXO = [
    (1, "cierge du Pérou", "«Tout-à-fait sur le bord du tableau»", "63", (1478, 560), "F"),
    (2, "agavé d'Amérique", "", "63", (1400, 795), "B"),
    (3, "chamérope nain", "«son pays natal, la Barbarie»", "63", (1300, 270), "B"),
    (4, "cycas des Indes", "", "63", (1205, 470), "B"),
    (5, "nopal à cochenille", "", "63", (1262, 712), "B"),
    (6, "mélocacte commun", "", "63–64", (1222, 848), "B"),
    (7, "dionée attrape-mouche", "«que nous avons un peu grandie»", "64", (1125, 865), "B"),
    (8, "dragonier à feuilles rouges", "«originaire de la Chine»", "64", (1095, 615), "B"),
    (9, "ananas", "", "64", (842, 718), "B"),
    (10, "chaumière indienne", "«construite en chaume et en bambous»", "64", (640, 520), "B"),
    (11, "papayer de l'Inde", "", "64", (515, 262), "B"),
    (12, "bananier", "el árbol del tahitiano (62)", "64", (452, 600), "B"),
    (13, "filao de l'Inde", "", "64", (740, 360), "B"),
    (14, "soleil, ou hélianthe", "«apporté du Pérou»", "64", (345, 662), "F"),
    (15, "serre chaude", "«l'aspect d'une pagode ou autre monument indien»", "65", (985, 420), "Y"),
]


def marca(h, x, y, n, tipo, r=1.55):
    col = F if tipo == "F" else B
    fondo = AMARILLO if tipo == "Y" else "#ffffff"
    h.add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{fondo}" stroke="{col}" stroke-width="0.25"/>')
    h.add(texto(round(x, 2), round(y + 0.68, 2), n, 1.9, col, clase="gi", ancla="middle", peso=600))


def fig5(carpeta_fuentes, atlas, salida):
    h = Hoja(297, 210, carpeta_fuentes)
    encabezado(h, 5, "La escena exótica de Boitard", [
        "Pl. 1ère del atlas, «Jardin exotique», firmada por Boitard. Los números siguen el orden "
        "en que él la describe, desde «A la droite du lecteur» (s. f., 63–65)."])

    # --- el grabado
    x0, y0, w = 14.0, 28.0, 186.0
    w_px, h_px, b64 = grabado(os.path.join(atlas, EXO_HOJA), EXO_CAJA, 1800, 82)
    alto = w * h_px / w_px
    imagen(h, x0, y0, w, round(alto, 2), b64)
    cx0, cy0, cx1, cy1 = EXO_CAJA

    def p(px, py):
        X = x0 + (px * EXO_ESC - cx0) / (cx1 - cx0) * w
        Y = y0 + (py * EXO_ESC - cy0) / (cy1 - cy0) * alto
        return X, Y

    for n, _, _, _, (px, py), tipo in EXO:
        marca(h, *p(px, py), n, tipo)

    # --- columna derecha: lo que dice Boitard y la lista
    x, y = 208.0, 31.0
    h.add(texto(x, y, "Plantas de muchas partes, una fisonomía", 2.4, B, peso=500))
    y = parrafo(h, x, y + 4.4, "«quelques arbres et quelques plantes des pays chauds, mais que j'ai pris "
                "sans distinction dans plusieurs parties de la terre, en donnant néanmoins à la composition "
                "une physionomie indienne» (63).", 78, 2.2, "g400", B)
    y += 2.4
    for n, nombre, dice, pag, _, tipo in EXO:
        col = F if tipo == "F" else B
        marca(h, x + 1.6, y - 0.7, n, tipo, r=1.4)
        h.add(texto(x + 4.2, y, nombre, 2.15, col, clase="gi"))
        resto = f"{dice}  ({pag})" if dice else f"({pag})"
        xr = x + 4.2 + ancho(nombre, "gi400", 2.15) + 1.6
        if xr + ancho(resto, "p400", 1.85) > 287:
            y += 2.9
            xr = x + 4.2
        h.add(texto(round(xr, 2), y, resto, 1.85, col))
        y += 3.55
    y = parrafo(h, x, y + 0.6, "Da el origen de ocho de las trece plantas, en el nombre o al lado: "
                "Pérou (1, 14), Amérique (2), la Barbarie (3), Indes o Inde (4, 11, 13) y Chine (8).",
                78, 1.95, "p400", B)

    h.add(texto(x, y + 5.0, "Dos frontispicios", 2.3, GRIS_TX, peso=500))
    parrafo(h, x, y + 9.4, "El texto llama a esta lámina «la planche 1re servant de frontispice» "
            "(63). El mismo libro da como frontispicio otra, también numerada I: la «Nouvelle Serre "
            "du jardin des plantes, à Paris», de Ch. Rohaut fils, «le dessin qui forme le frontispice "
            "de cet ouvrage» (xiv). En este ejemplar, el frontispicio es la serre (hoja 10 del atlas) "
            "y esta escena va en la hoja 34. Por qué hay dos, no se sabe.", 78, 1.9, "p400", GRIS_TX, 1.3)

    # --- abajo: lo que pasó a la novela y lo que la escena pedía
    yb = 166.0
    x = 14.0
    h.add(f'<circle cx="{x + 1.4}" cy="{yb - 0.75}" r="1.2" fill="#ffffff" stroke="{F}" stroke-width="0.25"/>')
    h.add(texto(x + 4.0, yb, "Lo que pasó a la novela  (Flaubert 1910)", 2.3, F, peso=500))
    y = parrafo(h, x, yb + 4.4, "El género exótico se hace «en plantant des cierges du Pérou» (54): "
                "la planta que Boitard puso «tout-à-fait sur le bord du tableau» (63) pasa al plural "
                "y se vuelve receta (1).", 86, 2.15)
    y = parrafo(h, x, y + 0.8, "Los girasoles (14) no llegan por aquí: Pécuchet los plantó «entre "
                "les cyprès et les quenouilles» (38), antes de encontrar el libro (54).", 86, 2.15)
    parrafo(h, x, y + 0.8, "Y la escena se descarta: «tant pis pour les colons et les voyageurs, "
            "les plantes américaines coûtaient trop cher» (55).", 86, 2.15)

    x = 108.0
    h.add(f'<rect x="{x}" y="{yb - 2.0}" width="7" height="2.4" fill="{AMARILLO}" fill-opacity="0.75"/>')
    h.add(texto(x + 9.0, yb, "Lo que la escena pedía y la copia dejó  (Boitard s. f., 65)", 2.3, B, peso=500))
    y = yb + 4.4
    for t in ("«une serre chaude à laquelle vous donnerez l'aspect d'une pagode ou autre monument "
              "indien» (15).",
              "«ce genre de tableau ne peut exister chez nous que pendant quatre ou cinq mois de "
              "l'année au plus».",
              "«une exposition chaude, ou au moins abritée des vents»."):
        y = parrafo(h, x, y, t, 90, 2.15, "g400", B) + 0.8

    h.add(texto_lineas(208.0, 166.0, partir(
        "Hoja 34 del atlas: Boitard (s. f.), Internet Archive A039a019, ejemplar de la Biblioteca de "
        "la Universidad de Sevilla, Public Domain Mark 1.0; sin retoque. Números y notas: borrador "
        "de la máquina (Claude, Anthropic), a pedido del autor, para verificar. Las posiciones salen "
        "de la descripción de Boitard; algunas son aproximadas (I).", 79, "g400", 1.8), 1.8, 1.3, clase="g"))
    h.guardar(salida)


if __name__ == "__main__":
    carpeta_fuentes, atlas, salida = sys.argv[1:4]
    os.makedirs(salida, exist_ok=True)
    fig1(carpeta_fuentes, atlas, os.path.join(salida, "fig1-puentes.svg"))
    fig5(carpeta_fuentes, atlas, os.path.join(salida, "fig5-escena-exotica.svg"))
