"""Genera los tableros de la taxonomía visual a partir de catalogo.json.

Uso (desde la raíz del repositorio):
    python3 "Una arquitectura que se arma y se guarda/taxonomia/generar_tableros.py"      # los tres tableros y el catálogo legible
    python3 "Una arquitectura que se arma y se guarda/taxonomia/generar_tableros.py" 3    # solo el tablero 3

Escribe en taxonomia/:
    tablero_1_arbol.jpg y .pdf   materiales arriba, gestos abajo, en el orden del ciclo (a la manera del «Tree Diagram» de Kuma)
    tablero_2_fechas.jpg y .pdf  las imágenes por año, en una franja por categoría del Cuadro 1 (a la manera del mapa de las vanguardias)
    tablero_3_relato.jpg y .pdf  el argumento del borrador: hilo rojo para el desarrollo, azul para las hipótesis («Doing a Duchamp»)
    catalogo.md                  la ficha de cada imagen, en una tabla

Sigue el sistema gráfico de los tableros de «Cosecha de piedras» (repositorio Altiplano). Necesita Chromium (ruta en la
variable CHROME) y Pillow.
"""

import html
import json
import math
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent
IMG = BASE / "imagenes"
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome")

PAPEL = "#f3eee4"
TINTA = "#2b2620"
GRIS = "#7a7166"
CELDA = "#fbf8f1"
ROJO = "#c0262d"
AZUL = "#1f5fbf"
SERIF = "'Liberation Serif', 'DejaVu Serif', serif"
SANS = "'DejaVu Sans', 'Liberation Sans', sans-serif"

CAT = json.loads((BASE / "catalogo.json").read_text(encoding="utf8"))
MAT = {m["clave"]: m for m in CAT["materiales"]}
GES = {g["clave"]: g for g in CAT["gestos"]}
CATEG = {c["clave"]: c for c in CAT["categorias"]}
IMAGENES = CAT["imagenes"]
POR_ID = {im["id"]: im for im in IMAGENES}


def e(t):
    return html.escape(str(t), quote=True)


def lineas(texto, ancho):
    return textwrap.wrap(texto, ancho, break_long_words=False) or [""]


def texto(x, y, cadena, tam, color=TINTA, fuente=SERIF, peso="normal", estilo="normal", ancla="start", alto=1.25,
          halo=False):
    """Una o varias líneas de texto SVG. Lo que va entre asteriscos sale en cursiva (o en redonda, si la línea ya es
    cursiva). Con halo, un borde del color del papel separa el texto de los hilos que pasan por debajo."""
    borde = f' stroke="{PAPEL}" stroke-width="7" stroke-linejoin="round" paint-order="stroke"' if halo else ""
    filas = cadena if isinstance(cadena, list) else [cadena]
    out = []
    for i, f in enumerate(filas):
        partes = f.split("*")
        otro = "normal" if estilo == "italic" else "italic"
        cuerpo = "".join(e(p) if j % 2 == 0 else f'<tspan font-style="{otro}">{e(p)}</tspan>' for j, p in enumerate(partes))
        out.append(f'<text x="{x:.1f}" y="{y + i * tam * alto:.1f}" font-size="{tam}" fill="{color}" '
                   f'font-family="{fuente}" font-weight="{peso}" font-style="{estilo}" text-anchor="{ancla}"{borde}>{cuerpo}</text>')
    return "\n".join(out)


def tam_imagen(im):
    with Image.open(IMG / im["archivo"]) as x:
        return x.size


def imagen(im, x, y, w, h):
    return (f'<image href="{(IMG / im["archivo"]).as_uri()}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
            f'height="{h:.1f}" preserveAspectRatio="xMidYMid meet"/>')


def ajustada(im, w, h):
    iw, ih = tam_imagen(im)
    k = min(w / iw, h / ih)
    return iw * k, ih * k


def insignia(x, y, n, color, r=15):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" stroke="{PAPEL}" stroke-width="2"/>'
            + texto(x, y + r * 0.36, str(n), int(r * 0.95), "#fff", SANS, "bold", ancla="middle"))


def pie(y, ancho=210):
    fuentes = ("Imágenes de dominio público: Det Kgl. Bibliotek (Guaman Poma, 1615); Internet Archive (Marcoy, 1875; "
               "Squier, 1877; Wiener, 1880; Semper, 1863; Wright, 1907; Gilbreth, 1911); Public Domain Image Archive; "
               "Cleveland Museum of Art (CC0). Fichas, enlaces y derechos: taxonomia/catalogo.md.")
    return texto(70, y, lineas(fuentes, ancho), 17, GRIS, SANS)


def pagina(W, H, cuerpo):
    return (f"<!doctype html><meta charset='utf-8'><style>@page{{size:{W}px {H}px;margin:0}}"
            f"html,body{{margin:0;background:{PAPEL}}}svg{{display:block}}</style>"
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<rect width="{W}" height="{H}" fill="{PAPEL}"/>{cuerpo}</svg>')


# ---------------------------------------------------------------- tablero 1: el árbol

def tablero_arbol():
    W, M = 2800, 70
    colW = (W - 2 * M) / len(GES)
    gut, celdaW, imgH, capH, sep = 62, 296, 190, 86, 12
    filaH = imgH + capH + sep
    yMat, top = 300, 660
    en_arbol = [im for im in IMAGENES if im["gesto"]]
    filas = max(sum(1 for im in en_arbol if im["gesto"] == g) for g in GES)
    s = [texto(M, 92, CAT["titulo"], 50, peso="bold"),
         texto(M, 140, "Seis materiales arriba y siete gestos abajo, en el orden del ciclo diario: de cargar a guardar. "
               "Cada imagen está en la columna de su gesto; una línea del color de su material la ata a él.", 24, GRIS,
               estilo="italic")]
    claves = list(MAT)
    xs = {k: M + 190 + i * (W - 2 * M - 380) / (len(claves) - 1) for i, k in enumerate(claves)}
    curvas, cajas = [], []
    for c, g in enumerate(GES):
        x0 = M + c * colW
        for r, im in enumerate([im for im in en_arbol if im["gesto"] == g]):
            col = MAT[im["material"]]["color"]
            y = top + r * filaH
            ix = x0 + gut
            cajas.append(f'<rect x="{ix:.1f}" y="{y:.1f}" width="{celdaW}" height="{imgH}" fill="{CELDA}" '
                         f'stroke="#d8d0c2" stroke-width="1.2"/>')
            cajas.append(imagen(im, ix + 6, y + 6, celdaW - 12, imgH - 12))
            cajas.append(insignia(ix + 4, y + 4, im["id"], col))
            ls = lineas(im["titulo"], 38)[:3]
            cajas.append(texto(ix, y + imgH + 21, ls, 16))
            cajas.append(texto(ix, y + imgH + 21 + len(ls) * 20, f'{im["autor_breve"]}, {im["fecha"]}', 14, GRIS, SANS))
            lane = x0 + gut - 12 - r * 8
            ys = y + imgH / 2
            mx = xs[im["material"]]
            curvas.append(f'<path d="M{ix:.1f},{ys:.1f} H{lane:.1f} V{top - 24:.1f} '
                          f'C{lane:.1f},{top - 200:.1f} {mx:.1f},{yMat + 170:.1f} {mx:.1f},{yMat + 40:.1f}" '
                          f'fill="none" stroke="{col}" stroke-width="2.6" stroke-opacity="0.82"/>')
            curvas.append(f'<circle cx="{ix:.1f}" cy="{ys:.1f}" r="4.5" fill="{col}"/>')
        yb = top + filas * filaH + 6
        cajas.append(f'<path d="M{x0 + gut:.1f},{yb:.1f} v14 H{x0 + gut + celdaW:.1f} v-14" fill="none" '
                     f'stroke="{TINTA}" stroke-width="2"/>')
        cajas.append(texto(x0 + gut + celdaW / 2, yb + 62, GES[g]["nombre"], 38, peso="bold", ancla="middle"))
        cajas.append(texto(x0 + gut + celdaW / 2, yb + 94, GES[g]["def"], 18, GRIS, estilo="italic", ancla="middle"))
        if c < len(GES) - 1:   # flecha del ciclo entre un gesto y el siguiente
            xa = x0 + gut + celdaW + 14
            cajas.append(f'<path d="M{xa:.1f},{yb + 50:.1f} h{colW - celdaW - 28:.1f}" stroke="{GRIS}" stroke-width="2"/>'
                         f'<polygon points="0,-7 12,0 0,7" fill="{GRIS}" '
                         f'transform="translate({xa + colW - celdaW - 30:.1f} {yb + 50:.1f})"/>')
    yb = top + filas * filaH + 6
    cajas.append(texto(M + gut, yb + 136, "mañana", 18, GRIS, SANS, estilo="italic"))
    cajas.append(texto(W - M - 20, yb + 136, "noche", 18, GRIS, SANS, estilo="italic", ancla="end"))
    for k in claves:
        m = MAT[k]
        n = sum(1 for im in en_arbol if im["material"] == k)
        cajas.append(texto(xs[k], yMat - 70, m["nombre"], 38, peso="bold", ancla="middle"))
        cajas.append(texto(xs[k], yMat - 40, m["def"], 18, GRIS, estilo="italic", ancla="middle"))
        cajas.append(f'<circle cx="{xs[k]:.1f}" cy="{yMat:.1f}" r="40" fill="{m["color"]}"/>')
        cajas.append(texto(xs[k], yMat + 10, str(n), 30, "#fff", SANS, "bold", ancla="middle"))
    H = int(yb + 300)
    con_ref = sum(1 for im in en_arbol if im["referencia"])
    nota = (f"Las imágenes no ilustran los puestos de La Paz: son analogías. Las {len(en_arbol)} tienen un material y un "
            f"gesto; {con_ref} llevan además la cita que justifica la analogía, y las otras {len(en_arbol) - con_ref} "
            "todavía no (catalogo.md). El número dentro de cada material es cuántas imágenes llegan a él.")
    cuerpo = "\n".join(s + curvas + cajas) + texto(M, H - 98, lineas(nota, 230), 18, TINTA, SANS) + pie(H - 46, 230)
    return W, H, pagina(W, H, cuerpo)


# ---------------------------------------------------------------- tablero 2: las fechas

def tablero_fechas():
    W, M = 3000, 60
    xL, x0, x1 = M + 300, M + 470, W - M - 60
    # Escala partida: los siglos con pocas imágenes ocupan poco; 1850-1920, donde se juntan, se abre.
    tramos = [(1550, 1850, 0.27), (1850, 1920, 0.61), (1920, 2030, 0.12)]
    laneH, top, th = 190, 250, 80

    def X(anio):
        if anio < tramos[0][0]:   # lo anterior a 1550 (Li Song, 1212) va a la izquierda del corte
            return xL + 70
        x = x0
        for a, b, f in tramos:
            ancho = f * (x1 - x0)
            if anio <= b:
                return x + (anio - a) / (b - a) * ancho
            x += ancho
        return x1

    s = [texto(M, 84, "Mapa de fechas: cuándo aparece cada parte del puesto en las imágenes reunidas", 46, peso="bold"),
         texto(M, 128, "Una franja por categoría del Cuadro 1 del borrador. Cada miniatura está en su año; el borde, del "
               "color de su material. La escala está partida: 1850-1920 se abre porque ahí se juntan las imágenes.",
               23, GRIS, estilo="italic")]
    cats = list(CATEG)
    bottom = top + laneH * len(cats)
    for i, c in enumerate(cats):
        y = top + i * laneH
        if i % 2 == 0:
            s.append(f'<rect x="{M}" y="{y}" width="{W - 2 * M}" height="{laneH}" fill="#ece5d8"/>')
        s.append(texto(M + 14, y + 60, CATEG[c]["nombre"], 34, peso="bold"))
        s.append(texto(M + 14, y + 90, lineas(CATEG[c]["def"], 24), 17, GRIS, estilo="italic"))
    for anio in (1550, 1600, 1650, 1700, 1750, 1800, 1850, 1860, 1870, 1880, 1890, 1900, 1910, 1920, 1975, 2026):
        x = X(anio)
        s.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="#d2c9b9" stroke-width="1"/>')
        s.append(texto(x, bottom + 34, str(anio), 19, GRIS, SANS, ancla="middle"))
    for a in (1850, 1920):   # cambios de escala
        s.append(f'<line x1="{X(a):.1f}" y1="{top - 10}" x2="{X(a):.1f}" y2="{bottom + 10}" stroke="{GRIS}" '
                 f'stroke-width="1.6" stroke-dasharray="2 6"/>')
    s.append(f'<line x1="{xL + 140:.1f}" y1="{top}" x2="{xL + 140:.1f}" y2="{bottom}" stroke="{TINTA}" '
             f'stroke-width="2" stroke-dasharray="3 5"/>')
    s.append(texto(xL + 70, bottom + 34, "1212", 19, GRIS, SANS, ancla="middle"))
    # 2026: el puesto a medias y el trabajo de campo
    x26 = X(2026)
    s.append(f'<line x1="{x26:.1f}" y1="{top - 40}" x2="{x26:.1f}" y2="{bottom + 50}" stroke="#9c2a3f" stroke-width="3"/>')
    s.append(texto(x26 - 8, top - 52, "2026: un puesto que «se redujo a un nailon de color azul tendido en el suelo» "
                   "(La Prensa, 8 de junio) y el trabajo de campo de noviembre y diciembre", 19, "#9c2a3f", SANS, "bold",
                   ancla="end"))
    grupos = {}
    for im in IMAGENES:
        grupos.setdefault((im["categoria"], im["anio"], im["autor_breve"]), []).append(im)
    pos = {}
    for i, c in enumerate(cats):
        y = top + i * laneH
        fila = sorted([(k, v) for k, v in grupos.items() if k[0] == c], key=lambda kv: kv[0][1])
        libre = -1e9
        rotulos = []
        for (cc, anio, autor), ims in fila:
            cols = min(len(ims), 3)
            ancho = cols * (th + 4)
            xc = max(X(anio) - ancho / 2, libre + 8)
            libre = xc + ancho
            nfil = (len(ims) + 2) // 3
            yc = y + (laneH - nfil * (th + 4)) / 2 - 8
            s.append(f'<circle cx="{X(anio):.1f}" cy="{y + laneH - 6:.1f}" r="4" fill="{TINTA}"/>')
            if abs(xc + ancho / 2 - X(anio)) > 4:
                s.append(f'<line x1="{X(anio):.1f}" y1="{y + laneH - 6:.1f}" x2="{xc + ancho / 2:.1f}" '
                         f'y2="{yc + nfil * (th + 4):.1f}" stroke="{GRIS}" stroke-width="1"/>')
            for j, im in enumerate(ims):
                xi = xc + (j % 3) * (th + 4)
                yi = yc + (j // 3) * (th + 4)
                col = MAT[im["material"]]["color"]
                s.append(f'<rect x="{xi:.1f}" y="{yi:.1f}" width="{th}" height="{th}" fill="{CELDA}" stroke="{col}" stroke-width="3"/>')
                s.append(f'<image href="{(IMG / im["archivo"]).as_uri()}" x="{xi + 3:.1f}" y="{yi + 3:.1f}" '
                         f'width="{th - 6}" height="{th - 6}" preserveAspectRatio="xMidYMid slice"/>')
                s.append(f'<rect x="{xi + th - 27:.1f}" y="{yi + th - 20:.1f}" width="24" height="17" fill="{TINTA}" fill-opacity="0.75"/>')
                s.append(texto(xi + th - 15, yi + th - 7, str(im["id"]), 13, "#fff", SANS, "bold", ancla="middle"))
            pos.setdefault((anio, autor), []).append((xc + ancho / 2, yc, yc + nfil * (th + 4)))
            rot = f'{autor}, {ims[0]["fecha"]}'
            xm, media = xc + ancho / 2, len(rot) * 3.9
            fila_r = 0
            while any(r == fila_r and xm - media < b2 + 6 and xm + media > a2 - 6 for a2, b2, r in rotulos):
                fila_r += 1
            rotulos.append((xm - media, xm + media, fila_r))
            s.append(texto(xm, yc + nfil * (th + 4) + 16 + fila_r * 15, rot, 13, GRIS, SANS, ancla="middle"))
    # Una misma obra en varias categorías: línea discontinua entre sus grupos.
    for (anio, autor), ps in pos.items():
        if len(ps) > 1:
            ps.sort(key=lambda p: p[1])
            for a, b in zip(ps, ps[1:]):
                s.append(f'<path d="M{a[0]:.1f},{a[2]:.1f} L{b[0]:.1f},{b[1]:.1f}" stroke="{TINTA}" '
                         f'stroke-width="1.6" stroke-dasharray="6 4" fill="none"/>')
    ly = bottom + 90
    s.append(texto(M, ly, "Borde de cada miniatura: su material", 19, TINTA, SANS, "bold"))
    for i, k in enumerate(MAT):
        x = M + 420 + i * 240
        s.append(f'<rect x="{x}" y="{ly - 20}" width="26" height="26" fill="{CELDA}" stroke="{MAT[k]["color"]}" stroke-width="4"/>')
        s.append(texto(x + 38, ly, MAT[k]["nombre"], 20, TINTA, SANS))
    H = ly + 100
    s.append(pie(H - 46, 240))
    return W, H, pagina(W, H, "\n".join(s))


# ---------------------------------------------------------------- tablero 3: el relato

def tablero_relato():
    W, H = 3000, 2160
    R = CAT["relato"]
    sitio = {"1": (360, 450), "2": (1080, 450), "3": (1820, 450), "4": (2560, 450), "5": (2520, 1040),
             "6": (1800, 1400), "7": (1000, 1400), "callado": (1620, 960)}
    giro = {"1": -1.2, "2": 1.0, "3": -0.8, "4": 1.3, "5": -1.0, "6": 1.1, "7": -1.3, "callado": 1.6}
    altoMax, anchoMax = 220, 560
    s = [texto(60, 84, "El relato: el argumento del borrador sobre las imágenes", 46, peso="bold"),
         texto(60, 128, "Hilo rojo: el desarrollo, en el orden de las secciones del borrador. Hilo azul: las cinco "
               "hipótesis que el trabajo de campo debe probar (analisis/02). Las imágenes son analogías.", 23, GRIS,
               estilo="italic")]
    capas_hilo, capas_img, capas_txt = [], [], []
    ancla, pie_grupo = {}, {}

    def grupo(clave, ids, muestra=False):
        cx, cy = sitio[clave]
        ims = [POR_ID[i] for i in ids]
        n = len(ims) + (1 if muestra else 0)
        medidas = [ajustada(im, anchoMax / n - 16, altoMax) for im in ims]
        if muestra:
            medidas = [(170, 120)] + medidas
        total = sum(w for w, h in medidas) + 22 * (len(medidas) - 1)
        x = cx - total / 2
        alto = max(h for w, h in medidas)
        partes = []
        for k, (w, h) in enumerate(medidas):
            y = cy - h / 2
            if muestra and k == 0:   # el nailon de 2026: no hay imagen, solo su color
                partes.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{MAT["tela"]["color"]}"/>')
                partes.append(texto(x + w / 2, y + h / 2 - 4, "nailon azul, 2026", 17, "#fff", SANS, "bold", ancla="middle"))
                partes.append(texto(x + w / 2, y + h / 2 + 18, "sin imagen", 15, "#dfe8f3", SANS, estilo="italic", ancla="middle"))
            else:
                im = ims[k - (1 if muestra else 0)]
                partes.append(f'<rect x="{x - 7:.1f}" y="{y - 7:.1f}" width="{w + 14:.1f}" height="{h + 14:.1f}" '
                              f'fill="#fffdf8" stroke="#cfc6b6" stroke-width="1"/>')
                partes.append(imagen(im, x, y, w, h))
                partes.append(insignia(x - 2, y - 2, im["id"], MAT[im["material"]]["color"], 14))
            x += w + 22
        capas_img.append(f'<g transform="rotate({giro[clave]} {cx:.1f} {cy:.1f})">{"".join(partes)}</g>')
        ancla[clave] = (cx, cy)
        pie_grupo[clave] = cy + alto / 2 + 7
        return cx, cy, alto, total

    nodos = R["nodos"]
    for nd in nodos:
        cx, cy, alto, total = grupo(nd["n"], nd["imagenes"], nd.get("muestra", False))
        y0 = cy + alto / 2 + 44
        x0 = cx - max(total, 340) / 2
        etiqueta = f'{nd["n"]} · {nd["titulo"]}'
        capas_txt.append(f'<rect x="{x0:.1f}" y="{y0 - 27:.1f}" width="{len(etiqueta) * 14 + 26:.1f}" height="38" fill="{ROJO}"/>')
        capas_txt.append(texto(x0 + 13, y0, etiqueta, 25, "#fff", SERIF, "bold"))
        capas_txt.append(texto(x0, y0 + 36, nd["seccion"], 17, GRIS, SANS, halo=True))
        cita = nd["cita"] if nd.get("pregunta") else f'«{nd["cita"]}»'
        ls = lineas(cita, 46)
        capas_txt.append(texto(x0, y0 + 64, ls, 21, TINTA, estilo="italic", halo=True))
        capas_txt.append(texto(x0, y0 + 64 + len(ls) * 26, nd["fuente_cita"], 16, GRIS, SANS, halo=True))
    cl = R["callado"]
    cx, cy, alto, total = grupo("callado", cl["imagenes"])
    capas_img.append(f'<rect x="{cx - total / 2 - 26:.1f}" y="{cy - alto / 2 - 30:.1f}" width="{total + 52:.1f}" '
                     f'height="{alto + 60:.1f}" fill="none" stroke="{AZUL}" stroke-width="2.5" stroke-dasharray="10 7"/>')
    capas_txt.append(texto(cx, cy + alto / 2 + 64, lineas(cl["rotulo"], 36), 22, AZUL, SERIF, "bold", "italic",
                           ancla="middle", halo=True))
    capas_txt.append(texto(cx, cy + alto / 2 + 124, lineas(cl["nota"], 48), 16, GRIS, SANS, ancla="middle", halo=True))

    codos = {("4", "5"): [(2900, 450), (2900, 1040)]}
    for a, b in zip(nodos, nodos[1:]):
        pts = [ancla[a["n"]]] + codos.get((a["n"], b["n"]), []) + [ancla[b["n"]]]
        capas_hilo.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" '
                          f'stroke="{ROJO}" stroke-width="6" stroke-linejoin="round"/>')
        (x1, y1), (x2, y2) = max(zip(pts, pts[1:]), key=lambda sg: math.dist(*sg))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
        capas_txt.append(f'<polygon points="-16,-12 14,0 -16,12" fill="{ROJO}" transform="translate({mx:.1f} {my:.1f}) rotate({ang:.1f})"/>')
    for nd in nodos:
        x, y = ancla[nd["n"]]
        capas_txt.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="{ROJO}" stroke="#fff" stroke-width="3"/>')
    ec = R["eco"]
    (x1, y1), (x2, y2) = ancla[ec["desde"]], ancla[ec["hasta"]]
    capas_hilo.append(f'<path d="M{x1:.1f},{y1:.1f} C{x1 - 120:.1f},{y1 + 700:.1f} {x2 - 600:.1f},{y2 - 40:.1f} {x2:.1f},{y2:.1f}" '
                      f'fill="none" stroke="{ROJO}" stroke-width="3.5" stroke-dasharray="14 9"/>')
    capas_txt.append(texto(110, 1030, lineas(ec["rotulo"], 32), 20, ROJO, SANS, "bold", halo=True))

    hs = R["hipotesis"]
    yC, hC, mC, gap = 1770, 220, 60, 30
    anchoC = (W - 2 * mC - (len(hs) - 1) * gap) / len(hs)
    for i, h in enumerate(hs):
        xC = mC + i * (anchoC + gap)
        n = len(h["nodos"])
        for j, destino in enumerate(h["nodos"]):
            px = xC + anchoC * (j + 1) / (n + 1)
            dx, _ = ancla[destino]
            dy = pie_grupo[destino] - 20
            raya = ' stroke-dasharray="12 8"' if destino == "callado" else ""
            capas_hilo.append(f'<line x1="{px:.1f}" y1="{yC:.1f}" x2="{dx:.1f}" y2="{dy:.1f}" stroke="{AZUL}" '
                              f'stroke-width="3" stroke-opacity="0.8"{raya}/>')
            capas_txt.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="7" fill="{AZUL}" stroke="#fff" stroke-width="2"/>')
            capas_txt.append(f'<circle cx="{px:.1f}" cy="{yC:.1f}" r="7" fill="{AZUL}"/>')
        capas_txt.append(f'<rect x="{xC:.1f}" y="{yC:.1f}" width="{anchoC:.1f}" height="{hC}" fill="#f8fbff" '
                         f'stroke="{AZUL}" stroke-width="3"/>')
        capas_txt.append(texto(xC + 22, yC + 46, h["n"], 30, AZUL, SERIF, "bold"))
        capas_txt.append(texto(xC + 22, yC + 88, lineas(h["texto"], 42), 22, TINTA))
        capas_txt.append(texto(xC + anchoC - 20, yC + hC - 16, "hilos a: " + ", ".join(
            "lo callado" if d == "callado" else d for d in h["nodos"]), 16, GRIS, SANS, ancla="end"))
    ly = 172
    s.append(f'<line x1="1960" y1="{ly}" x2="2040" y2="{ly}" stroke="{ROJO}" stroke-width="6"/>')
    s.append(texto(2055, ly + 7, "desarrollo", 20, TINTA, SANS))
    s.append(f'<line x1="2220" y1="{ly}" x2="2300" y2="{ly}" stroke="{ROJO}" stroke-width="3.5" stroke-dasharray="14 9"/>')
    s.append(texto(2315, ly + 7, "eco", 20, TINTA, SANS))
    s.append(f'<line x1="2420" y1="{ly}" x2="2500" y2="{ly}" stroke="{AZUL}" stroke-width="3"/>')
    s.append(texto(2515, ly + 7, "hipótesis", 20, TINTA, SANS))
    s.append(texto(60, H - 84, lineas("Las hipótesis no son hallazgos: son lo que el campo de noviembre y diciembre puede "
                                      "confirmar o tumbar. Los números de colores son los de catalogo.md; el color es el de su material.",
                                      230), 18, TINTA, SANS))
    s.append(pie(H - 34, 240))
    return W, H, pagina(W, H, "\n".join(s + capas_hilo + capas_img + capas_txt))


# ---------------------------------------------------------------- catálogo legible

def catalogo_md():
    filas = ["# Catálogo de la taxonomía visual", "",
             "Generado por `generar_tableros.py` desde `catalogo.json`; no lo edites a mano. La «referencia» es la cita "
             "que justifica la analogía, comprobada en su fuente; las imágenes sin referencia son candidatas.", "",
             "| N.º | Imagen | Autor y fecha | Material | Gesto | Categoría | Referencia | Fuente y derechos |",
             "|---|---|---|---|---|---|---|---|"]
    for im in IMAGENES:
        ubic = f', {im["ubicacion"]}' if im["ubicacion"] else ""
        obra = f', *{im["obra"]}*' if im["obra"] else ""
        orig = f' (*{im["titulo_original"]}*)' if im["titulo_original"] else ""
        gesto = GES[im["gesto"]]["nombre"] if im["gesto"] else "—"
        filas.append(f'| {im["id"]} | [{im["titulo"]}](imagenes/{im["archivo"]}){orig} | {im["autor"]}, {im["fecha"]}{obra}{ubic} | '
                     f'{MAT[im["material"]]["nombre"]} | {gesto} | {CATEG[im["categoria"]]["nombre"]} | '
                     f'{im["referencia"] or "—"} | [{im["fuente"]}]({im["pagina"]}). {im["derechos"]} |')
    (BASE / "catalogo.md").write_text("\n".join(filas) + "\n", encoding="utf8")
    print("catalogo.md")


def render(nombre, W, H, doc):
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / f"{nombre}.html"
        f.write_text(doc, encoding="utf8")
        png = Path(tmp) / f"{nombre}.png"
        base = [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                "--allow-file-access-from-files", "--virtual-time-budget=8000"]
        subprocess.run(base + ["--force-device-scale-factor=1", f"--window-size={W},{H + 300}", f"--screenshot={png}",
                               f.as_uri()], check=True, capture_output=True)
        Image.open(png).convert("RGB").crop((0, 0, W, H)).save(BASE / f"{nombre}.jpg", quality=86, optimize=True,
                                                                 progressive=True)
        subprocess.run(base + ["--no-pdf-header-footer", f"--print-to-pdf={BASE / (nombre + '.pdf')}", f.as_uri()],
                       check=True, capture_output=True)
    print(f"{nombre}.jpg y .pdf ({W} x {H})")


def main():
    pedidos = {int(a) for a in sys.argv[1:]}
    tableros = [(1, "tablero_1_arbol", tablero_arbol), (2, "tablero_2_fechas", tablero_fechas),
                (3, "tablero_3_relato", tablero_relato)]
    for n, nombre, f in tableros:
        if pedidos and n not in pedidos:
            continue
        render(nombre, *f())
    if not pedidos:
        catalogo_md()


if __name__ == "__main__":
    main()
