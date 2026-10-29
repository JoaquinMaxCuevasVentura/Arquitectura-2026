"""Láminas de planta: dos jardines a la misma escala y lo que se ve desde el comedor.

Uso: python3 planta.py carpeta_fuentes wissous_trazado.json carpeta_salida

Son borradores hechos por la máquina para que el autor los confronte y los
redibuje a mano. Lo supuesto va en rojo y discontinuo (referencias graficas.md §3).
"""
import json
import math
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import chavignolles as ch  # noqa: E402
from svg import (AMARILLO, B, F, GRIS, HALO, I, MACIZO, NUMERO, PAPEL, Hoja, Vista,  # noqa: E402
                 barra_escala, esc, numero, texto, texto_lineas, trazo)
from trazar_wissous import enlazar, marching_squares, simplificar_lazo  # noqa: E402

# --- Wissous: de píxeles de la lámina a metros -----------------------------
# El recuadro de la planta (360–2850 × 290–1576 px) se dibuja como un arpent
# de París (3.419 m²): la lámina no trae escala (I).
ARPENT = 3419.0
WX0, WY0, WX1, WY1 = 360, 290, 2850, 1576
SW = math.sqrt(ARPENT / ((WX1 - WX0) * (WY1 - WY0)))   # metros por píxel


def wm(X, Y):
    return ((X - WX0) * SW, (WY1 - Y) * SW)


W_ANCHO, W_ALTO = wm(WX1, WY0)

# Lo que se dibuja a mano sobre el trazado (píxeles de la lámina, medidos en ella)
W_RECT = {  # número: (X0, Y0, X1, Y1)
    3: (360, 290, 500, 550), 1: (360, 550, 500, 1240), 2: (360, 1240, 600, 1576),
    7: (600, 1320, 856, 1576), 6: (600, 1240, 856, 1320), 5: (510, 950, 856, 1140),
    4: (510, 300, 856, 836), 10: (880, 310, 950, 370), 15: (1690, 290, 1950, 325),
    16: (2780, 794, 2850, 1074), 13: (2740, 1480, 2850, 1576),
}
W_SERRE_PANELES = (590, 1156, 790, 1240)
W_ETIQ = {  # número: posición del rótulo en la lámina
    1: (436, 910), 2: (450, 1430), 3: (436, 426), 4: (640, 630), 5: (696, 1060),
    6: (696, 1290), 7: (716, 1460), 8: (1190, 1280), 9: (1380, 1068), 10: (915, 405),
    11: (1556, 1026), 12: [(2070, 340), (1750, 826), (2090, 936), (2166, 1500)],
    13: (2790, 1530), 14: (2414, 900), 15: (1820, 392), 16: (2754, 930),
    17: (2666, 930), 18: (1690, 1296), 19: (1360, 470),
}
W_LEYENDA = [
    (1, "patio, separado del jardín por una reja"), (2, "casa"), (3, "cuadras y cocheras"),
    (4, "paseo de álamos y tilos"), (5, "parterre de bulbos"), (6, "invernadero"),
    (7, "salón que da al jardín"), (8, "césped delante del salón, «pour donner de l'air et de la vue»"),
    (9, "gabinete de verdor con mesa de piedra"), (10, "otro, de enrejado"),
    (11, "pozo, escondido en un macizo de arbustos"), (12, "cenadores de verdor"),
    (13, "emparrado de vid"), (14, "gran salón de verdor"), (15, "gradería de flores"),
    (16, "colmenar"), (17, "plantas para las abejas"),
    (18, "huerta de primavera y otoño, «masqué de manière à n'être pas aperçu»"),
    (19, "huerta de verano, escondida como la anterior"),
]

# --- Chavignolles: números y rótulos ---------------------------------------
# Mismo número que en Wissous si hay equivalente; si no, del 20 en adelante,
# en el orden en que los invitados los ven al abrirse la cortina (F 61).
C_LEYENDA = [
    (2, "casa", "28"), (4, "charmille, con tilos", "26, 56"),
    (5, "dos canteros de geranios al pie de la escalinata", "38"),
    (7, "comedor («la salle»): dos lugares posibles", "28, 59"),
    (8, "césped", "29, 61"), (13, "tonnelle (emparrado)", "26, 65"),
    (18, "huerta en cuatro cuadros", "26"),
    (20, "roca de granitos pegados", "56, 61"), (21, "tumba etrusca, seis pies", "55, 61, 64"),
    (22, "«Rialto» sobre un estanque sin agua", "55, 61–62"),
    (23, "cabaña con el techo quemado", "38, 55, 61"),
    (24, "tejos podados: pavos reales, ciervos, sillones", "57, 61"),
    (25, "tilo tumbado «de la charmille à la tonnelle»", "56, 61, 65"),
    (26, "pagoda sobre el vigneau", "56, 61"), (27, "brecha en el muro, ruinas por tierra", "55, 61"),
    (28, "laberinto en el bosquete", "55, 57, 62"), (29, "puerta de las pipas", "57, 62"),
]


def contornos(mascara, xs, ys, paso, tol=0.6):
    """Polígonos (en metros) del borde de una máscara booleana de la malla."""
    lazos = enlazar(marching_squares(mascara.astype(np.uint8)))
    polis = []
    for l in lazos:
        s = simplificar_lazo(l, tol)
        polis.append([(xs[0] + (x - 1) * paso, ys[0] + (y - 1) * paso) for x, y in s])
    return polis


def patrones(hoja):
    hoja.defs.append(f"""
<pattern id="macizo" width="1.6" height="1.6" patternUnits="userSpaceOnUse">
  <rect width="1.6" height="1.6" fill="{MACIZO}"/>
  <circle cx="0.4" cy="0.5" r="0.13" fill="{B}" fill-opacity="0.55"/>
  <circle cx="1.2" cy="1.25" r="0.11" fill="{B}" fill-opacity="0.45"/>
</pattern>
<pattern id="huerta" width="0.9" height="0.9" patternUnits="userSpaceOnUse">
  <line x1="0" y1="0.45" x2="0.9" y2="0.45" stroke="{F}" stroke-width="0.07" stroke-opacity="0.55"/>
</pattern>
<pattern id="huerta_v" width="0.9" height="0.9" patternUnits="userSpaceOnUse">
  <line x1="0.45" y1="0" x2="0.45" y2="0.9" stroke="{F}" stroke-width="0.07" stroke-opacity="0.55"/>
</pattern>
<pattern id="huerta_gris" width="0.8" height="0.8" patternUnits="userSpaceOnUse">
  <rect width="0.8" height="0.8" fill="#e4e4e4"/>
  <line x1="0.4" y1="0" x2="0.4" y2="0.8" stroke="{GRIS}" stroke-width="0.1"/>
</pattern>
<pattern id="bosque" width="2.2" height="2.2" patternUnits="userSpaceOnUse">
  <circle cx="0.6" cy="0.7" r="0.42" fill="none" stroke="{F}" stroke-width="0.08" stroke-opacity="0.7"/>
  <circle cx="1.7" cy="1.6" r="0.36" fill="none" stroke="{F}" stroke-width="0.08" stroke-opacity="0.7"/>
</pattern>
<pattern id="cesped" width="1.2" height="1.2" patternUnits="userSpaceOnUse">
  <path d="M0.3,0.8 l0.12,-0.3 M0.9,0.4 l0.1,-0.28" stroke="{F}" stroke-width="0.07" stroke-opacity="0.6"/>
</pattern>
<pattern id="rayado_rojo" width="1.1" height="1.1" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <line x1="0" y1="0" x2="0" y2="1.1" stroke="{I}" stroke-width="0.14" stroke-opacity="0.7"/>
</pattern>
<marker id="flecha_roja" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="4" markerHeight="4" orient="auto">
  <path d="M0,0 L6,3 L0,6 z" fill="{I}"/>
</marker>
<marker id="flecha" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="3.5" markerHeight="3.5" orient="auto">
  <path d="M0,0 L6,3 L0,6 z" fill="{F}"/>
</marker>""")


# ============================================================================
# Wissous
# ============================================================================
def dibujar_wissous(h, v, traza, numeros=True):
    caja = [wm(WX0, WY0), wm(WX1, WY0), wm(WX1, WY1), wm(WX0, WY1)]
    h.add(f'<path d="{v.d(caja)}" fill="url(#macizo)" stroke="none"/>')
    # caminos y céspedes trazados de la lámina (B)
    d = " ".join(v.d([wm(x, y) for x, y in p]) for p in traza["poligonos"])
    h.add(f'<path d="{d}" fill-rule="evenodd" {trazo(B, 0.16, relleno=PAPEL)}/>')
    # huertas: en gris, porque están escondidas
    for cx, cy, rx, ry, arriba in ((1345, 290, 205, 190, True), (1705, 1576, 375, 296, False)):
        pts = []
        for k in range(41):
            a = math.pi * k / 40
            pts.append(wm(cx - rx * math.cos(a), cy + (ry * math.sin(a) if arriba else -ry * math.sin(a))))
        h.add(f'<path d="{v.d(pts)}" fill="url(#huerta_gris)" {trazo(GRIS, 0.22)}/>')
    # construcciones y piezas dibujadas a mano sobre la lámina
    for n, (x0, y0, x1, y1) in W_RECT.items():
        relleno = PAPEL
        if n in (2, 3):
            relleno = "#f3ece0"
        h.add(f'<path d="{v.d([wm(x0, y0), wm(x1, y0), wm(x1, y1), wm(x0, y1)])}" {trazo(B, 0.22, relleno=relleno)}/>')
    x0, y0, x1, y1 = W_SERRE_PANELES
    h.add(f'<path d="{v.d([wm(x0, y0), wm(x1, y0), wm(x1, y1), wm(x0, y1)])}" fill="url(#huerta_v)" {trazo(B, 0.2)}/>')
    # paseo 4: tres filas de árboles; 5: canteros
    for fila in (420, 560, 700):
        for col in (590, 690, 790):
            X, Y = v.p(*wm(col, fila))
            h.add(f'<circle cx="{X}" cy="{Y}" r="0.75" {trazo(B, 0.16, relleno="#f6efe2")}/>')
    for col in range(560, 860, 70):
        X, Y = v.p(*wm(col, 340))
        h.add(f'<circle cx="{X}" cy="{Y}" r="0.45" {trazo(B, 0.14, relleno="#f6efe2")}/>')
    # 9 gabinete, 11 pozo, 17 macizo para las abejas
    X, Y = v.p(*wm(1380, 1056))
    h.add(f'<ellipse cx="{X}" cy="{Y}" rx="{40 * SW * v.k}" ry="{34 * SW * v.k}" {trazo(B, 0.2, relleno=PAPEL)}/>')
    X, Y = v.p(*wm(1596, 1072))
    h.add(f'<circle cx="{X}" cy="{Y}" r="{24 * SW * v.k}" {trazo(B, 0.25, relleno=PAPEL)}/>')
    h.add(f'<circle cx="{X}" cy="{Y}" r="{12 * SW * v.k}" {trazo(B, 0.2, relleno="#d9e6ee")}/>')
    pts = [wm(2730 - 120 * math.sin(math.pi * k / 30), 933 + 97 * math.cos(math.pi * k / 30)) for k in range(31)]
    h.add(f'<path d="{v.d(pts)}" fill="url(#macizo)" {trazo(B, 0.2)}/>')
    # borde de la planta
    h.add(f'<path d="{v.d(caja)}" {trazo(B, 0.35)}/>')
    if numeros:
        for n, pos in W_ETIQ.items():
            for (X, Y) in (pos if isinstance(pos, list) else [pos]):
                x, y = v.p(*wm(X, Y))
                h.add(texto(x, round(y + 0.9, 2), n, 2.5, B, clase="gi", ancla="middle"))


# ============================================================================
# Chavignolles
# ============================================================================
def poli(h, v, pts, **kw):
    h.add(f'<path d="{v.d(pts)}" {trazo(**kw)}/>')


def linea(h, v, a, b, **kw):
    (x1, y1), (x2, y2) = v.p(*a), v.p(*b)
    h.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {trazo(**kw)}/>')


def rotulo(h, v, x, y, t, tam=2.0, color=F, ancla="start", clase="", halo=True):
    X, Y = v.p(x, y)
    h.add(texto(X, Y, t, tam, color, clase=clase, ancla=ancla, extra=HALO if halo else ""))


def num(h, v, x, y, n, r=1.45):
    X, Y = v.p(x, y)
    h.add(numero(X, Y, n, r=r, lleno=n >= 20))


GUION_I = "1.1,0.7"        # lugar o medida supuestos
GUION_V = "0.25,0.55"      # visuales


def dibujar_chavignolles(h, v, estado="obras", detalle=True, rotulos=True, r_num=1.45):
    L = ch.LADO
    # propiedad: jardín, huerto y bosquete (medidas I)
    poli(h, v, ch.ZONAS["huerto (verger)"], color=I, ancho=0.2, guion=GUION_I)
    poli(h, v, ch.ZONAS["bosquete"], color=I, ancho=0.2, guion=GUION_I, relleno="url(#bosque)")
    # huerto: frutales en grilla (lugar I)
    for x in np.arange(27.5, 35.0, 3.2):
        for y in np.arange(1.8, 11.0, 3.2):
            X, Y = v.p(x, y)
            h.add(f'<circle cx="{X}" cy="{Y}" r="{0.9 * v.k}" {trazo(F, 0.12, guion="0.5,0.4")}/>')
    # bosquete: el laberinto (I), un camino sinuoso
    lab = [(25.6, 21.6), (28.0, 22.8), (31.0, 21.4), (33.6, 23.2), (34.8, 20.0), (32.2, 18.0),
           (29.0, 19.2), (26.6, 17.0), (28.4, 14.6), (31.8, 15.8), (34.6, 13.6)]
    h.add(f'<path d="{v.d(lab, cerrar=False)}" {trazo(PAPEL, 0.9 * v.k / 3.0)}/>')
    h.add(f'<path d="{v.d(lab, cerrar=False)}" {trazo(F, 0.12, guion="0.6,0.4")}/>')
    # casa (F 28; medidas I) y escalinata (F 38)
    poli(h, v, ch.CASA, color=F, ancho=0.3, guion=GUION_I, relleno="#f1f1f1")
    for x in (6.1, 10.5, 14.5, 18.9):          # tabiques de las cinco piezas (I)
        linea(h, v, (x, -9.0), (x, 0.0), color=GRIS, ancho=0.12, guion="0.6,0.5")
    poli(h, v, ch.rect(11.0, 0.0, 14.0, 1.6), color=F, ancho=0.2, guion=GUION_I, relleno=PAPEL)
    for k in range(1, 4):
        linea(h, v, (11.0, 0.4 * k), (14.0, 0.4 * k), color=F, ancho=0.08)
    # huerta en cuatro cuadros, alamedas en cruz (F 26; medidas I)
    cuadros = [ch.rect(3.4, 2.4, 11.0, 11.2), ch.rect(14.0, 2.4, 23.0, 11.2),
               ch.rect(3.4, 13.8, 11.0, 24.4), ch.rect(14.0, 13.8, 23.0, 24.4)]
    for i, c in enumerate(cuadros):
        patron = "url(#huerta)" if i % 2 == 0 else "url(#huerta_v)"
        poli(h, v, c, color=F, ancho=0.18, guion=GUION_I, relleno=patron)
    # césped en el cruce (I) y la roca (F 56: «au milieu du gazon»)
    X, Y = v.p(*ch.ROCA)
    h.add(f'<circle cx="{X}" cy="{Y}" r="{3.0 * v.k}" {trazo(F, 0.18, guion=GUION_I, relleno="url(#cesped)")}/>')
    # vigneau (F 26) con la pagoda (F 56)
    cx, cy, r = ch.VIGNEAU
    X, Y = v.p(cx, cy)
    h.add(f'<circle cx="{X}" cy="{Y}" r="{r * v.k}" {trazo(F, 0.22, relleno="#f4f4f4")}/>')
    h.add(f'<circle cx="{X}" cy="{Y}" r="{r * 0.62 * v.k}" {trazo(F, 0.1, guion="0.4,0.4")}/>')
    # tonnelle (F 26), muro (F 26) y charmille (F 26, 56)
    poli(h, v, ch.ELEMENTOS_POR_ID["tonnelle"]["forma"], color=F, ancho=0.22, relleno="#f4f4f4")
    for y in np.arange(3.6, 18.4, 1.3):
        linea(h, v, (0.4, y), (2.8, y), color=F, ancho=0.08)
    if estado == "antes":
        partes_muro, partes_ch = ["muro"], ["charmille"]
    else:
        partes_muro, partes_ch = ["muro_a", "muro_b"], ["charmille_1", "charmille_2", "charmille_3", "charmille_4"]
    for pid in partes_muro:
        poli(h, v, ch.ELEMENTOS_POR_ID[pid]["forma"], color=F, ancho=0.2, relleno=F)
    for pid in partes_ch:
        poli(h, v, ch.ELEMENTOS_POR_ID[pid]["forma"], color=F, ancho=0.2, relleno="#e9e9e9")
    for y in np.arange(12.7, 25.0, 1.5):
        if estado == "obras" and (14.4 < y < 15.4 or 18.1 < y < 19.1 or 21.4 < y < 22.4):
            continue
        X, Y = v.p(24.25, y)
        h.add(f'<circle cx="{X}" cy="{Y}" r="{0.62 * v.k}" {trazo(F, 0.12, relleno=PAPEL)}/>')
    # celosía al fondo (F 26) y caminito detrás (F 26)
    linea(h, v, (7.4, L), (23.5, L), color=F, ancho=0.18, guion="0.3,0.3")
    linea(h, v, (0.0, L + 2.4), (36.0, L + 2.4), color=F, ancho=0.12, guion=GUION_I)
    # cahute / cabaña (F 38: «au bout de la charmille»)
    poli(h, v, ch.CABANA, color=F, ancho=0.22, relleno=F if estado == "obras" else "#dddddd")
    # dama de yeso (F 28, 38)
    X, Y = v.p(22.9, 21.0)
    h.add(f'<circle cx="{X}" cy="{Y}" r="0.45" fill="{F}"/>')
    # tejos de la gran alameda (F 57)
    for y in ch.TEJOS_Y:
        for x in (11.0, 14.0):
            X, Y = v.p(x, y)
            h.add(f'<circle cx="{X}" cy="{Y}" r="{0.45 * v.k}" {trazo(F, 0.14, relleno="#cfcfcf")}/>')
    # geranios (F 38)
    for x in (10.6, 14.4):
        X, Y = v.p(x, 1.2)
        h.add(f'<circle cx="{X}" cy="{Y}" r="{0.55 * v.k}" {trazo(F, 0.12, relleno="#f0c9c0")}/>')
    if estado == "obras":
        # roca (lugar I), tumba (lugar I), estanque y puente (lugar I)
        poli(h, v, ch.ELEMENTOS_POR_ID["roca"]["forma"], color=F, ancho=0.25, guion=GUION_I, relleno="#bdbdbd")
        poli(h, v, ch.ELEMENTOS_POR_ID["tumba"]["forma"], color=F, ancho=0.25, guion=GUION_I, relleno=F)
        tx, ty = ch.TUMBA
        for dx, dy in ((-1.2, -1.2), (1.2, -1.2), (1.2, 1.2), (-1.2, 1.2)):
            X, Y = v.p(tx + dx, ty + dy)
            h.add(f'<circle cx="{X}" cy="{Y}" r="{0.35 * v.k}" {trazo(F, 0.1, relleno="#9fb59f")}/>')
        ex, ey = ch.ESTANQUE
        poli(h, v, ch.rect(ex - 1.8, ey - 1.1, ex + 1.8, ey + 1.1), color=F, ancho=0.22, guion=GUION_I, relleno="#f7f7f7")
        poli(h, v, ch.ELEMENTOS_POR_ID["puente"]["forma"], color=F, ancho=0.2, relleno=PAPEL)
        # tilo tumbado (F 56, 61) y su copa seca
        poli(h, v, ch.ELEMENTOS_POR_ID["tilo"]["forma"], color=F, ancho=0.2, relleno="#d6c7b2")
        poli(h, v, ch.ELEMENTOS_POR_ID["tilo_copa"]["forma"], color=F, ancho=0.12, guion="0.5,0.4")
        X, Y = v.p(*ch.TILO_PIE)
        h.add(f'<circle cx="{X}" cy="{Y}" r="{0.55 * v.k}" {trazo(F, 0.18, relleno="#d6c7b2")}/>')
        # brecha y ruinas
        for (x, y) in ((24.4, 5.6), (25.3, 6.1), (24.0, 6.9), (25.6, 7.3), (24.8, 7.6)):
            X, Y = v.p(x, y)
            h.add(f'<rect x="{X - 0.4}" y="{Y - 0.3}" width="0.8" height="0.6" {trazo(F, 0.1, relleno="#cccccc")}/>')
        # pagoda: seis troncos (F 56)
        cx, cy, _ = ch.VIGNEAU
        for k in range(6):
            a = math.pi / 3 * k
            X, Y = v.p(cx + 1.1 * math.cos(a), cy + 1.1 * math.sin(a))
            h.add(f'<rect x="{X - 0.25}" y="{Y - 0.25}" width="0.5" height="0.5" fill="{F}"/>')
        X, Y = v.p(cx, cy)
        h.add(f'<polygon points="{" ".join(f"{X + 1.6 * v.k * math.cos(math.pi / 3 * k + math.pi / 6)},{Y + 1.6 * v.k * math.sin(math.pi / 3 * k + math.pi / 6)}" for k in range(6))}" {trazo("#b23a2a", 0.2, relleno="none")}/>')
        # puerta de las pipas (F 57): en el borde del bosquete hacia el campo (lugar I)
        poli(h, v, ch.rect(30.0, 24.7, 32.4, 25.2), color=F, ancho=0.2, guion=GUION_I, relleno=F)
    if rotulos:
        rotular_chavignolles(h, v, estado, r_num)


def rotular_chavignolles(h, v, estado, r=1.45):
    L = ch.LADO
    if estado == "obras":
        for (n, x, y) in ((20, 12.5, 15.6), (21, 19.0, 9.1), (22, 7.2, 12.7), (23, 22.0, 26.6),
                          (24, 15.6, 5.5), (25, 17.5, 20.0), (26, 4.0, 26.2), (27, 22.2, 6.5),
                          (28, 29.8, 20.4), (29, 31.2, 26.8)):
            num(h, v, x, y, n, r)
    for (n, x, y) in ((2, 12.5, -5.0), (4, 25.9, 21.8), (5, 9.2, 1.0), (8, 9.0, 13.6),
                      (13, 1.6, 8.0), (18, 7.2, 5.6)):
        num(h, v, x, y, n, r)
    rotulo(h, v, 12.5, L + 4.2, "los campos [F 26]", 1.9, ancla="middle")
    rotulo(h, v, -0.6, L + 2.0, "caminito [F 26]", 1.6, ancla="end")
    rotulo(h, v, 13.5, L + 0.6, "celosía [F 26]", 1.6)
    rotulo(h, v, 30.6, 6.2, "huerto [F 26]", 1.6, ancla="middle")
    rotulo(h, v, 30.6, 23.2, "bosquete [F 26]", 1.6, ancla="middle")
    rotulo(h, v, -0.6, 12.5, "álamos [F 26]", 1.6, ancla="end")
    rotulo(h, v, 26.0, 1.0, "muro [F 26]", 1.6)
    rotulo(h, v, -0.6, 21.4, "vigneau [F 26]", 1.6, ancla="end")


# ---------------------------------------------------------------------------
def leyenda_numeros(h, x, y, filas, tam=2.05, ancho_col=88, col_n=1, color=F, letra="F", serif=False):
    """Leyenda numerada; filas = [(n, texto, páginas)]."""
    por_col = math.ceil(len(filas) / col_n)
    for i, fila in enumerate(filas):
        n, t = fila[0], fila[1]
        pags = fila[2] if len(fila) > 2 else None
        cx = x + (i // por_col) * ancho_col
        cy = y + (i % por_col) * tam * 1.42
        if serif:
            h.add(texto(cx + 1.4, cy + 0.75, n, tam * 1.05, color, clase="gi", ancla="middle"))
        else:
            h.add(numero(cx + 1.4, cy, n, r=1.25, lleno=n >= 20, color=color, tam=1.7))
        cola = f"  [{letra} {pags}]" if pags else ""
        h.add(f'<text x="{cx + 3.6}" y="{round(cy + 0.75, 2)}" font-size="{tam}" fill="{color}">'
              f'{esc(t)}<tspan fill="{color}" fill-opacity="0.75">{esc(cola)}</tspan></text>')


def leyenda_lineas(h, x, y):
    filas = [
        ("continua", F, None, "lo da Flaubert, también el lugar"),
        ("discontinua", F, GUION_I, "lo da Flaubert; el lugar o la medida es supuesto"),
        ("roja", I, GUION_I, "supuesto (I): medidas, límites, origen del agua"),
        ("visual", F, GUION_V, "línea de vista desde el comedor"),
    ]
    for i, (_, col, g, t) in enumerate(filas):
        yy = y + i * 3.4
        h.add(f'<line x1="{x}" y1="{yy}" x2="{x + 9}" y2="{yy}" {trazo(col, 0.3 if g != GUION_V else 0.25, guion=g)}/>')
        h.add(texto(x + 11, yy + 0.7, t, 2.0))
    yy = y + len(filas) * 3.4
    h.add(f'<rect x="{x}" y="{yy - 1.3}" width="9" height="2.6" fill="{AMARILLO}" fill-opacity="0.55"/>')
    h.add(texto(x + 11, yy + 0.7, "lo que la regla pedía y la copia no hizo", 2.0))
    yy += 3.4
    h.add(numero(x + 2, yy, "", r=1.25))
    h.add(numero(x + 6.5, yy, "", r=1.25, lleno=True))
    h.add(texto(x + 11, yy + 0.7, "abierto: tiene equivalente en Wissous; lleno: vino de otra parte del manual", 2.0))


def pie(h, x, y, lineas, tam=2.0):
    h.add(texto_lineas(x, y, lineas, tam, 1.3, clase="g"))


# ============================================================================
# Dos jardines a la misma escala
# ============================================================================
def convenciones(h, x, y, filas, ancho_col=88, por_col=3, tam=2.0):
    """Leyenda corta de líneas y colores; filas = [(tipo, color, guion, texto)]."""
    for i, (tipo, col, g, t) in enumerate(filas):
        cx = x + (i // por_col) * ancho_col
        cy = y + (i % por_col) * 3.4
        if tipo == "linea":
            h.add(f'<line x1="{cx}" y1="{cy}" x2="{cx + 9}" y2="{cy}" {trazo(col, 0.3, guion=g)}/>')
        elif tipo == "mancha":
            h.add(f'<rect x="{cx}" y="{cy - 1.3}" width="9" height="2.6" fill="{col}" fill-opacity="0.6"/>')
        elif tipo == "numeros":
            h.add(numero(cx + 2, cy, "", r=1.2))
            h.add(numero(cx + 6.5, cy, "", r=1.2, lleno=True))
        elif tipo == "serif":
            h.add(texto(cx + 4.5, cy + 0.9, "12", 2.5, col, clase="gi", ancla="middle"))
        h.add(texto(cx + 11, cy + 0.7, t, tam))


def dos_jardines(carpeta_fuentes, traza, salida):
    h = Hoja(297, 210, carpeta_fuentes)
    patrones(h)
    h.add(texto(14, 16.0, "Dos jardines a la misma escala", 4.4, F, clase="g", peso=600))
    h.add(texto(14, 21.6, "El jardín que Boitard da como ejemplo para una casa modesta, "
                "y el que Bouvard y Pécuchet arman en Chavignolles.", 2.4, F, clase="g"))
    h.add(texto(287, 14.0, NUMERO["dos-jardines"], 3.4, F, clase="g", ancla="end", peso=600))

    # --- Wissous, como la lámina (B); la escala es supuesta (I)
    vw = Vista(x_mm=14.0, y_mm=122.0, escala=500)
    dibujar_wissous(h, vw, traza)
    h.add(texto(14, 31.0, "Wissous, cerca de París (Boitard s. f., lám. 18; 115–116)", 2.6, B, peso=500))
    h.add(texto(14, 35.0, "«pas plus d'un arpent d'étendue» (115). Dibujado como un arpent entero: "
                "unos 81 × 42 m, 3.400 m² (I).", 2.0, B))

    # --- Chavignolles, reconstruido (F, con lugares y medidas I)
    vc = Vista(x_mm=196.0, y_mm=122.0, escala=500, x0=-3.0, y0=-10.0)
    # amarillo: lo que Boitard excluye para un clos de uno o dos arpents (114)
    for (x, y, r) in ((ch.TUMBA[0], ch.TUMBA[1], 2.3), (22.05, 23.55, 2.6), (25.0, 6.5, 2.6)):
        X, Y = vc.p(x, y)
        h.add(f'<circle cx="{X}" cy="{Y}" r="{r * vc.k}" fill="{AMARILLO}" fill-opacity="0.6"/>')
    dibujar_chavignolles(h, vc, estado="obras", r_num=1.2)
    # el comedor: segunda o cuarta pieza (F 28, 59)
    for x0 in (6.1, 14.5):
        poli(h, vc, ch.rect(x0 + 0.25, -8.75, x0 + 4.15, -0.25), color=I, ancho=0.2, guion=GUION_I)
        num(h, vc, x0 + 2.2, -6.6, 7, 1.2)
    h.add(texto(196, 31.0, "Chavignolles (Flaubert 1910, cap. II), reconstruido", 2.6, F, peso=500))
    h.add(texto(196, 35.0, "Jardín de 25 × 25 m, el largo del tilo (I): unos 625 m². "
                "Con huerto y bosquete, unos 900 m² (I).", 2.0, I))

    # --- escala, una para los dos
    h.add(barra_escala(14.0, 127.0, 500, metros=(0, 10, 20, 30, 40, 50)))
    h.add(texto(128.0, 128.2, "La misma escala para los dos, 1:500 en A4. Es supuesta (I): "
                "ninguna fuente da medidas.", 2.0, I))

    # --- leyendas
    h.add(texto(14, 137.0, "Wissous  [B 115–116]", 2.3, B, peso=500))
    leyenda_numeros(h, 14, 141.0, W_LEYENDA, tam=1.95, ancho_col=82, col_n=2, color=B, serif=True)
    h.add(texto(196, 137.0, "Chavignolles", 2.3, F, peso=500))
    leyenda_numeros(h, 196, 141.0, C_LEYENDA, tam=1.8, ancho_col=90, col_n=1)
    h.add(texto_lineas(14, 172.0, [
        "En Wissous las dos huertas están escondidas (18, 19), y lo construido son cenadores y salas de verdor,",
        "lo que Boitard admite en un bosquet chico (114). En Chavignolles la huerta es casi todo el jardín, y la tumba,",
        "la roca y el puente quedan entre las legumbres, a la vista de las ventanas: «le tombeau faisait un cube",
        "au milieu des épinards» (Flaubert 1910, 61). Boitard aclara que juntar «l'utile à l'agréable», como aquí,",
        "no es «une règle à suivre dans tous les cas»; lo «de première considération» es la armonía con la casa",
        "y con «les goûts et la fortune du propriétaire» (116).",
    ], 2.15, 1.3, clase="g"))
    convenciones(h, 14.0, 192.0, [
        ("serif", B, None, "Boitard: la lámina 18 y su leyenda (B)"),
        ("linea", F, None, "lo da Flaubert, también el lugar (F)"),
        ("linea", F, GUION_I, "lo da Flaubert; el lugar o la medida es supuesto"),
        ("linea", I, GUION_I, "supuesto (I): medidas y límites"),
        ("mancha", AMARILLO, None, "lo que Boitard excluye en un clos de uno o dos arpents (114)"),
        ("numeros", F, None, "abierto: tiene equivalente en Wissous; lleno: no"),
    ], ancho_col=86, por_col=3, tam=1.9)
    pie(h, 196.0, 189.0, [
        "Borrador de la máquina (Claude, Anthropic), a pedido del autor,",
        "para verificar y redibujar a mano. Wissous: caminos trazados de la",
        "hoja 68 del atlas (Internet Archive, A039a019) con trazar_wissous.py;",
        "Chavignolles: datos de «Planta: datos del texto». Cada planta va en la",
        "orientación de su fuente; ninguna trae norte que sirva aquí.",
    ], 1.8)
    h.guardar(salida)


# ============================================================================
# Lo que se ve desde el comedor
# ============================================================================
def vistas_comedor(carpeta_fuentes, salida):
    h = Hoja(297, 210, carpeta_fuentes)
    patrones(h)
    h.add(texto(14, 16.0, "Lo que se ve desde el comedor", 4.4, F, clase="g", peso=600))
    h.add(texto(14, 21.6, "Chavignolles la noche de la cena (Flaubert 1910, 59–62), reconstruido. En amarillo, "
                "lo que no se habría visto desde el comedor, con el jardín como lo encontraron (26–38).",
                2.4, F, clase="g"))
    h.add(texto(287, 14.0, NUMERO["vistas-comedor"], 3.4, F, clase="g", ancla="end", peso=600))
    v = Vista(x_mm=16.0, y_mm=170.0, escala=300, x0=-3.0, y0=-10.0)

    # --- prueba: dónde no se ve una tumba de seis pies desde ninguna de las
    # dos posiciones del comedor, con el muro y la charmille enteros («antes»)
    r1 = ch.analisis("antes", "comedor, posición 1")
    r2 = ch.analisis("antes", "comedor, posición 2")
    for p in contornos(r1["escondido"] & r2["escondido"], r1["xs"], r1["ys"], r1["paso"]):
        if len(p) > 2:
            h.add(f'<path d="{v.d(p)}" fill="{AMARILLO}" fill-opacity="0.55" stroke="none"/>')
    dibujar_chavignolles(h, v, estado="obras")

    # visuales del comedor a la tumba, al puente y a la pagoda: se ven (F 61)
    for (wx, n) in ((8.1, 1), (16.9, 2)):
        for (tx, ty) in (ch.TUMBA, (ch.ESTANQUE[0], ch.ESTANQUE[1] - 0.3),
                         (ch.VIGNEAU[0] + 0.6, ch.VIGNEAU[1] - 0.4)):
            linea(h, v, (wx, 0.0), (tx, ty), color=F, ancho=0.22, guion=GUION_V)
        X, Y = v.p(wx, -1.6)
        h.add(f'<rect x="{X - 4.2}" y="{Y - 1.4}" width="8.4" height="2.8" fill="{PAPEL}" '
              f'{trazo(I, 0.2, guion=GUION_I)}/>')
        h.add(texto(X, Y + 0.7, f"comedor {n}", 1.8, I, ancla="middle"))
    num(h, v, 3.6, -4.5, 7)
    rotulo(h, v, 3.6, -6.9, "cocina, petite salle, vestíbulo, deuxième salle, salón [F 28]:", 1.75, "#6e6e6e")
    rotulo(h, v, 3.6, -8.2, "no dice desde qué lado. Por eso, dos lugares para el comedor.", 1.75, "#6e6e6e")

    # el tilo como medida (I)
    linea(h, v, (ch.TILO_COPA[0], 19.9), (ch.TILO_PIE[0], 20.3), color=I, ancho=0.2,
          extra='marker-start="url(#flecha_roja)" marker-end="url(#flecha_roja)"')
    rotulo(h, v, 13.4, 20.6, "largo del tilo ≈ lado del jardín (I)", 1.6, I, ancla="middle")

    # el agua: el texto no dice de dónde la traen (F 61–62)
    pts = [(-2.2, 2.8), (-1.4, 9.0), (4.2, 13.4), (5.6, 14.6)]
    h.add(f'<path d="{v.d(pts, cerrar=False)}" {trazo(I, 0.3, guion=GUION_I)} marker-end="url(#flecha_roja)"/>')
    rotulo(h, v, -2.9, 1.6, "agua: ¿de dónde?", 1.6, I)
    rotulo(h, v, -2.9, 0.5, "«toute la matinée» [F 61–62]", 1.5, I)

    # rótulo del amarillo, al lado de la casa
    X, Y = v.p(25.6, -1.6)
    h.add(texto_lineas(X, Y, [
        "En amarillo, lo que no se ve desde el comedor",
        "en ninguna de sus dos posiciones, con el muro",
        "y la charmille enteros (F 26): ahí cabía la tumba.",
        "Las franjas junto a la tonnelle y al vigneau",
        "son demasiado angostas para ella.",
    ], 1.7, 1.3, color=F))
    linea(h, v, (31.0, -0.6), (31.0, 1.8), color=F, ancho=0.15)

    # escala, orientación
    h.add(barra_escala(16.0, 177.0, 300, metros=(0, 5, 10, 20),
                       etiqueta="escala supuesta (I): el lado del jardín, 25 m, es el largo del tilo"))
    h.add(texto(96.0, 178.2, "Sin norte: el texto no lo da. La casa abajo, como en la vista desde la ventana (F 26).",
                1.9, GRIS))
    convenciones(h, 16.0, 188.0, [
        ("linea", F, None, "lo da Flaubert, también el lugar (F)"),
        ("linea", F, GUION_I, "lo da Flaubert; el lugar o la medida es supuesto"),
        ("linea", I, GUION_I, "supuesto (I): medidas, límites, origen del agua"),
        ("linea", F, GUION_V, "línea de vista desde el comedor"),
        ("mancha", AMARILLO, None, "lo que la regla pedía y la copia no hizo"),
        ("numeros", F, None, "abierto: tiene equivalente en Wissous; lleno: no"),
    ], ancho_col=74, por_col=3, tam=1.9)

    # --- columna derecha
    xr = 162.0
    h.add(texto_lineas(xr, 33.0, [
        "Boitard quería la tumba lejos de la casa, «de manière à ce qu'il ne puisse être aperçu",
        "d'aucune partie du bâtiment, et même des principales poses du jardin» (s. f., 69).",
        "En Chavignolles ese lugar existía: detrás de la charmille y detrás del muro. La tumba",
        "se hizo donde estaban los espárragos (F 55), y al abrirse las cortinas «le tombeau",
        "faisait un cube au milieu des épinards» (61).",
    ], 2.15, 1.32, clase="g"))
    corte(h, xr, 52.0)
    estanque(h, xr, 104.0)
    h.add(texto(xr, 144.5, "Números", 2.4, F, peso=500))
    leyenda_numeros(h, xr, 148.5, C_LEYENDA, tam=1.8, ancho_col=60, col_n=2)
    pie(h, xr, 188.0, [
        "Borrador de la máquina (Claude, Anthropic), a pedido del autor, para verificar y redibujar",
        "a mano. Datos: Flaubert (1910), cap. II, en «Planta: datos del texto». Vistas: chavignolles.py,",
        "en malla de 25 cm. Alturas supuestas (I): ojos a 2,4 m en el comedor y 5,6 m en el piso alto;",
        "muro 2,5 m; charmille 3,5 m; tumba 1,95 m, «six pieds» (F 55).",
    ], 1.8)
    h.guardar(salida)


def corte(h, x, y):
    """Corte esquemático por una ventana del comedor, la charmille y el bosquete (alturas I)."""
    h.add(texto(x, y, "Corte esquemático: de la ventana al bosquete (alturas supuestas, I)", 2.2, F, peso=500))
    k = 2.4                       # mm por metro
    base = y + 26.0               # línea de tierra
    X0 = x + 21.0                 # la fachada
    # distancias sobre la recta de la ventana (9,2; 0) al punto (33; 21) del bosquete
    CH0, CH1, FIN = 19.1, 21.0, 35.7

    def P(d, z):
        return (round(X0 + d * k, 2), round(base - z * k, 2))

    h.add(f'<line x1="{P(-2, 0)[0]}" y1="{base}" x2="{P(FIN + 1, 0)[0]}" y2="{base}" {trazo(F, 0.25)}/>')
    (a, b), (c, d) = P(-1.6, 0), P(0, 8.0)
    h.add(f'<rect x="{a}" y="{d}" width="{c - a}" height="{b - d}" fill="#f1f1f1" {trazo(F, 0.2, guion=GUION_I)}/>')
    for z, rot in ((ch.Z_BAJO, "comedor, ojos a 2,4 m"), (ch.Z_ALTO, "piso alto, 5,6 m")):
        ex, ez = P(0, z)
        h.add(f'<circle cx="{ex}" cy="{ez}" r="0.5" fill="{I}"/>')
        h.add(texto(P(-2.2, 0)[0], ez + 0.6, rot, 1.6, I, ancla="end"))
    # charmille: tres alturas posibles
    for hch, op in ((4.5, 0.18), (3.5, 0.38), (2.5, 0.7)):
        (a, b), (c, d) = P(CH0, 0), P(CH1, hch)
        h.add(f'<rect x="{a}" y="{d}" width="{c - a}" height="{b - d}" fill="#bdbdbd" fill-opacity="{op}" '
              f'{trazo(F, 0.12, guion="0.5,0.4")}/>')
    a, b = P((CH0 + CH1) / 2, 5.0)
    h.add(texto(a, b, "charmille: 2,5, 3,5 o 4,5 m", 1.6, F, ancla="middle"))
    # bosquete escondido desde el comedor, y la tumba
    (a, b), (c, d) = P(CH1, 0), P(FIN, 0.5)
    h.add(f'<rect x="{a}" y="{d}" width="{c - a}" height="{b - d}" fill="{AMARILLO}" fill-opacity="0.7"/>')
    a, b = P(FIN - 2.0, 0)
    h.add(texto(a, b + 3.0, "bosquete", 1.6, F, ancla="middle"))
    (a, b), (c, d) = P(24.5, 0), P(25.9, ch.TUMBA_H)
    h.add(f'<rect x="{a}" y="{d}" width="{c - a}" height="{b - d}" fill="{F}"/>')
    a, b = P(25.2, 0)
    h.add(texto(a, b + 3.0, "tumba, 1,95 m (F 55)", 1.6, F, ancla="middle"))
    # visual del comedor: rasa la charmille más baja y sigue subiendo
    e = (0, ch.Z_BAJO)
    pend = (2.5 - ch.Z_BAJO) / CH0
    f = P(FIN, ch.Z_BAJO + pend * FIN)
    h.add(f'<line x1="{P(*e)[0]}" y1="{P(*e)[1]}" x2="{f[0]}" y2="{f[1]}" {trazo(F, 0.25, guion=GUION_V)}/>')
    # visuales del piso alto: rasan la charmille de 2,5 y de 3,5 m y bajan
    for hch in (2.5, 3.5):
        pend = (hch - ch.Z_ALTO) / CH1
        d_fin = min(FIN, -ch.Z_ALTO / pend)
        f = P(d_fin, ch.Z_ALTO + pend * d_fin)
        h.add(f'<line x1="{P(0, ch.Z_ALTO)[0]}" y1="{P(0, ch.Z_ALTO)[1]}" x2="{f[0]}" y2="{f[1]}" '
              f'{trazo(GRIS, 0.22, guion=GUION_V)}/>')
    h.add(texto_lineas(x, base + 4.6, [
        "Desde el comedor, los ojos (2,4 m) quedan más bajos que cualquier charmille de 2,5 m o más:",
        "detrás no se ve nada, en las dos posiciones. Desde el piso alto (en gris) depende de la altura,",
        "que el texto no da: con 3,5 m o más, y estos supuestos, queda un rincón del bosquete escondido",
        "de las cuatro ventanas, donde cabe la tumba; con 2,5 o 3 m, no.",
    ], 1.8, 1.3))


def estanque(h, x, y):
    """Prueba chica de P10: el estanque como circuito, con su corte."""
    h.add(texto(x, y, "El estanque: de dónde viene el agua y por dónde se va", 2.2, F, peso=500))
    y1 = y + 7.5
    h.add(f'<line x1="{x + 2}" y1="{y1}" x2="{x + 14}" y2="{y1}" {trazo(I, 0.3, guion=GUION_I)} '
          f'marker-end="url(#flecha_roja)"/>')
    h.add(texto(x + 2, y1 - 1.6, "¿de dónde? (I)", 1.7, I))
    h.add(f'<line x1="{x + 16}" y1="{y1}" x2="{x + 56}" y2="{y1}" {trazo(F, 0.3)} marker-end="url(#flecha)"/>')
    h.add(texto(x + 16, y1 - 1.6, "acarreada «toute la matinée» (F 61–62)", 1.7))
    h.add(f'<rect x="{x + 58}" y="{y1 - 2}" width="14" height="4" {trazo(F, 0.25, relleno="#eef4f7")}/>')
    h.add(texto(x + 65, y1 + 0.7, "estanque", 1.7, ancla="middle"))
    h.add(f'<line x1="{x + 65}" y1="{y1 + 2.2}" x2="{x + 65}" y2="{y1 + 7}" {trazo(F, 0.3)} marker-end="url(#flecha)"/>')
    h.add(texto(x + 67, y1 + 6.0, "se va «entre les pierres du fond, mal jointes» (F 62)", 1.7))
    # corte del fondo
    y2 = y + 23.0
    h.add(f'<path d="M{x + 2},{y2 - 6} L{x + 8},{y2 - 6} L{x + 10},{y2} L{x + 40},{y2} L{x + 42},{y2 - 6} '
          f'L{x + 48},{y2 - 6}" {trazo(F, 0.3)}/>')
    for i in range(10):
        cx = x + 11.5 + i * 2.9
        h.add(f'<rect x="{cx}" y="{y2 - 1.6}" width="2.5" height="1.5" {trazo(F, 0.15, relleno="#d9d9d9")}/>')
        h.add(f'<line x1="{cx + 2.7}" y1="{y2 - 1.2}" x2="{cx + 2.7}" y2="{y2 + 2.4}" {trazo("#3b7ea1", 0.25)}/>')
    h.add(f'<rect x="{x + 10}" y="{y2 - 2.3}" width="30" height="0.6" fill="#8b7d6b" fill-opacity="0.6"/>')
    h.add(texto(x + 50, y2 - 3.6, "vase (F 62)", 1.6))
    h.add(f'<path d="M{x + 10},{y2 + 0.8} L{x + 40},{y2 + 0.8}" {trazo(I, 0.25, guion=GUION_I)}/>')
    h.add(texto(x + 50, y2 + 1.4, "el «fond de glaise» que esperaban (F 55)", 1.6, I))
    h.add(texto_lineas(x, y2 + 6.2, [
        "Boitard: solo algunas tierras «très-peu poreuses» guardan el agua sin cimentar el borde ni el",
        "fondo; si no hay agua en el sitio, un pozo con una máquina alcanza para un bassin chico",
        "(s. f., 37). Wissous tiene su pozo, escondido entre arbustos (11).",
    ], 1.8, 1.3))


if __name__ == "__main__":
    carpeta_fuentes, traza_json, salida = sys.argv[1:4]
    traza = json.load(open(traza_json, encoding="utf-8"))
    os.makedirs(salida, exist_ok=True)
    dos_jardines(carpeta_fuentes, traza, os.path.join(salida, "dos-jardines.svg"))
    vistas_comedor(carpeta_fuentes, os.path.join(salida, "vistas-comedor.svg"))
