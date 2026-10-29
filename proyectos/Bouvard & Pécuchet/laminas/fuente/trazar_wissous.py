"""Traza las zonas claras (caminos, céspedes) de la lámina 18 de Boitard.

Entrada: la imagen de la hoja 68 del atlas (Internet Archive, A039a019),
a resolución completa. Salida: wissous_trazado.json, con polígonos en
píxeles de la imagen. Las construcciones y los números se dibujan aparte,
a mano, en planta.py.

Uso: python3 trazar_wissous.py hoja68.jpg wissous_trazado.json
"""
import json
import sys

import numpy as np
from PIL import Image, ImageFilter

# Recuadro de la planta en la imagen completa (3539 x 2223 px), medido
# sobre la lámina: borde izquierdo, superior, derecho e inferior.
PLANTA = (360, 290, 2850, 1576)
PASO = 4          # se trabaja a 1/4 de la resolución
UMBRAL = 168      # gris por encima del cual la zona se lee como clara


def mascara(ruta):
    im = Image.open(ruta).convert("L").crop(PLANTA)
    im = im.filter(ImageFilter.GaussianBlur(5))
    w, h = im.size
    im = im.resize((w // PASO, h // PASO), Image.LANCZOS)
    clara = im.point(lambda v: 255 if v > UMBRAL else 0)
    # limpieza: quita motas claras en los macizos y motas oscuras en los caminos
    clara = clara.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    clara = clara.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    return (np.array(clara) > 127).astype(np.uint8)


def marching_squares(m):
    """Contornos de nivel 0,5 de una matriz binaria, como segmentos."""
    m = np.pad(m, 1)
    h, w = m.shape
    segs = []
    for y in range(h - 1):
        for x in range(w - 1):
            a, b, c, d = m[y, x], m[y, x + 1], m[y + 1, x + 1], m[y + 1, x]
            k = a * 8 + b * 4 + c * 2 + d
            if k in (0, 15):
                continue
            top, right = (x + 0.5, y), (x + 1, y + 0.5)
            bottom, left = (x + 0.5, y + 1), (x, y + 0.5)
            tabla = {
                1: [(left, bottom)], 2: [(bottom, right)], 3: [(left, right)],
                4: [(top, right)], 5: [(left, top), (bottom, right)],
                6: [(top, bottom)], 7: [(left, top)], 8: [(top, left)],
                9: [(top, bottom)], 10: [(top, right), (left, bottom)],
                11: [(top, right)], 12: [(left, right)], 13: [(bottom, right)],
                14: [(left, bottom)],
            }
            segs.extend(tabla[k])
    return segs


def enlazar(segs):
    """Une los segmentos en polilíneas cerradas."""
    vecinos = {}
    for p, q in segs:
        vecinos.setdefault(p, []).append(q)
        vecinos.setdefault(q, []).append(p)
    vistos, lazos = set(), []
    for inicio in list(vecinos):
        if inicio in vistos:
            continue
        lazo, prev, cur = [inicio], None, inicio
        vistos.add(inicio)
        while True:
            sig = [n for n in vecinos[cur] if n != prev and n not in vistos]
            if not sig:
                break
            prev, cur = cur, sig[0]
            vistos.add(cur)
            lazo.append(cur)
        if len(lazo) > 8:
            lazos.append(lazo)
    return lazos


def simplificar(pts, tol):
    """Douglas-Peucker."""
    if len(pts) < 3:
        return pts
    a, b = np.array(pts[0]), np.array(pts[-1])
    ab = b - a
    n = np.hypot(*ab) or 1.0
    dist = [abs(ab[0] * (p[1] - a[1]) - ab[1] * (p[0] - a[0])) / n for p in pts[1:-1]]
    i = int(np.argmax(dist)) + 1
    if dist[i - 1] > tol:
        return simplificar(pts[: i + 1], tol)[:-1] + simplificar(pts[i:], tol)
    return [pts[0], pts[-1]]


def simplificar_lazo(lazo, tol):
    """Douglas-Peucker para un lazo cerrado: se parte en el punto más lejano."""
    a = np.array(lazo[0])
    k = int(np.argmax([np.hypot(*(np.array(p) - a)) for p in lazo]))
    ida = simplificar(lazo[: k + 1], tol)
    vuelta = simplificar(lazo[k:] + [lazo[0]], tol)
    return ida[:-1] + vuelta[:-1]


def area(pts):
    x, y = np.array(pts).T
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def dentro(pt, poli):
    """Punto en polígono (par-impar)."""
    x, y = pt
    res = False
    n = len(poli)
    for i in range(n):
        (x1, y1), (x2, y2) = poli[i], poli[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            res = not res
    return res


def profundidad(lazos):
    """Cuántos lazos contienen a cada uno (0: borde exterior, 1: macizo, 2: isla)."""
    areas = [area(l) for l in lazos]
    prof = []
    for i, l in enumerate(lazos):
        pt = l[0]
        prof.append(sum(1 for j, o in enumerate(lazos)
                        if j != i and areas[j] > areas[i] and dentro(pt, o)))
    return prof


# Zonas claras sueltas dentro de un macizo (profundidad par, fuera de la red de
# caminos): son la textura del grabado, no caminos. Se quitan las menores que
# esto, en px² a 1/4 de resolución (3000 px² son unos 50 m² del jardín).
ISLA_MINIMA = 3000


def main(ruta, salida):
    m = mascara(ruta)
    lazos = [l for l in enlazar(marching_squares(m)) if area(l) >= 30]
    prof = profundidad(lazos)
    areas = [area(l) for l in lazos]
    red = int(np.argmax(areas))
    quitar = {i for i in range(len(lazos))
              if i != red and prof[i] % 2 == 0 and areas[i] < ISLA_MINIMA}
    # lo que está dentro de una isla quitada también se quita
    for i in range(len(lazos)):
        if any(areas[j] > areas[i] and dentro(lazos[i][0], lazos[j]) for j in quitar):
            quitar.add(i)
    poligonos = []
    for i, lazo in enumerate(lazos):
        if i in quitar:
            continue
        s = simplificar_lazo(lazo, 0.7)
        # vuelta a píxeles de la imagen completa (se descuenta el borde de 1)
        s = [((x - 1) * PASO + PLANTA[0], (y - 1) * PASO + PLANTA[1]) for x, y in s]
        poligonos.append([[round(x, 1), round(y, 1)] for x, y in s])
    json.dump({"recuadro": PLANTA, "poligonos": poligonos}, open(salida, "w"))
    print(len(poligonos), "polígonos;", len(quitar), "islas de textura quitadas")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
