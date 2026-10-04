"""Verificación sin render: cortes y proyecciones ortogonales del modelo superpuestos con los DXF del cliente.

Dibuja con matplotlib la geometría que exporta exportar_geometria.py (no usa Cycles ni EEVEE). Láminas:
  LADO_AIRE_PLANTA_*            corte a +1,00 y veredas sobre la planta baja A111
  SUPERPOSICION_FACHADA_*       alzados SO, ESTE y OESTE (proyección con orden de profundidad) y su DXF en rojo
  LADO_AIRE_ALZADO_SO_*         tramos del alzado SO
  LADO_TIERRA_NICHOS_CORTE      corte a +1,50 de la fachada NE (paños al ras o en nicho)
  ME2_CORTE_*                   cortes de la puerta ME-2 sobre su detalle
  RETENEDOR_NIEVE_CORTE         corte por el plano de una abrazadera
  LADO_AIRE_PLANTA_GENERAL / _PISO, AVION_737_800_VISTAS
Los DXF son los del cliente (no van en el repositorio, están en UYUNI_insumos_cliente.zip); se buscan por nombre.

Uso (Python con numpy, matplotlib y ezdxf):
  python superponer_cad_2d.py /tmp/geometria.npz carpeta_con_los_dxf ../verificacion
"""
import glob
import math
import os
import sys

import ezdxf
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection

# transformaciones DXF -> modelo (ver TRASPASO.md, sección 3): el alzado SO va corrido 2,6 cm respecto de la planta
TF_SO = lambda x, y: (187.866 - x, y)           # alzado SO: X = 187,866 - x
TF_ESTE = lambda x, y: (x - 250.095, y)         # alzado ESTE (desde +X): Y = x - 250,095
TF_OESTE = lambda x, y: (384.526 - x, y)        # alzado OESTE (desde -X): Y = 384,526 - x
COLOR_COL = {"01": (0.80, 0.78, 0.74), "02": (0.86, 0.84, 0.80), "03": (0.32, 0.38, 0.45), "04": (0.62, 0.64, 0.66),
             "05": (0.62, 0.36, 0.22), "06": (0.78, 0.76, 0.70), "10": (0.90, 0.91, 0.93)}
COLOR_NOMBRE = [("CAMINO_SERVICIO_AIRE_MARCAS", (0.95, 0.95, 0.93)), ("CAMINO_SERVICIO", (0.22, 0.22, 0.22)),
                ("MARCAS_AMARILLAS", (0.88, 0.68, 0.10)), ("PLATAFORMA_AIRE", (0.70, 0.68, 0.64)),
                ("VEREDA", (0.86, 0.83, 0.76)), ("CORDON", (0.55, 0.55, 0.53)), ("CALZADA", (0.25, 0.25, 0.25)),
                ("ACERA", (0.86, 0.83, 0.76)), ("SUELO", (0.76, 0.70, 0.56)), ("VIDRIO", (0.25, 0.42, 0.55)),
                ("GLASS", (0.25, 0.42, 0.55)), ("FUELLE", (0.15, 0.15, 0.15))]


# --- DXF ---------------------------------------------------------------------
def segmentos(e, capa=None):
    capa = capa or e.dxf.layer
    t = e.dxftype()
    if t == "LINE":
        yield capa, [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
    elif t in ("LWPOLYLINE", "POLYLINE"):
        try:
            pts = [(p[0], p[1]) for p in e.flattening(0.01)]
        except Exception:
            pts = [(p[0], p[1]) for p in e.get_points("xy")] if t == "LWPOLYLINE" else []
        if len(pts) > 1:
            yield capa, pts
    elif t in ("ARC", "CIRCLE", "ELLIPSE", "SPLINE"):
        try:
            yield capa, [(p.x, p.y) for p in e.flattening(0.01)]
        except Exception:
            pass
    elif t == "INSERT":
        try:
            for v in e.virtual_entities():
                yield from segmentos(v, capa if capa != "0" else v.dxf.layer)
        except Exception:
            pass


_cache = {}


def lineas_dxf(ruta, tf, filtro_x=None, fuera=("0-COTAS", "0-COTAS REF", "0-COTAS DETALLES", "0-TEXTO", "0-EJES")):
    if ruta not in _cache:
        _cache[ruta] = [(c, p) for e in ezdxf.readfile(ruta).modelspace()
                        if e.dxftype() not in ("HATCH", "MTEXT", "TEXT", "DIMENSION") for c, p in segmentos(e)]
    out = []
    for capa, pts in _cache[ruta]:
        if capa in fuera:
            continue
        xs = [p[0] for p in pts]
        if filtro_x and (max(xs) < filtro_x[0] or min(xs) > filtro_x[1]):
            continue
        out.append([tf(x, y) for x, y in pts])
    return out


# --- geometría del modelo --------------------------------------------------------
def cargar_geom(ruta):
    d = np.load(ruta, allow_pickle=False)
    return [(str(n), str(c), d[f"v{k}"].astype(np.float64), d[f"t{k}"])
            for k, (n, c) in enumerate(zip(d["nombres"], d["colecciones"]))]


def color(nombre, colec):
    for k, c in COLOR_NOMBRE:
        if k in nombre:
            return np.array(c)
    return np.array(COLOR_COL.get(colec[:2], (0.7, 0.7, 0.7)))


def corte(objs, eje, c, filtro=None):
    """Segmentos de la intersección de las mallas con el plano coordenada[eje] = c."""
    out = []
    for nombre, colec, v, t in objs:
        if filtro and not filtro(nombre, colec):
            continue
        p = v[t]
        d = p[:, :, eje] - c
        cruza = (d.max(axis=1) > 0) & (d.min(axis=1) < 0)
        p, d = p[cruza], d[cruza]
        if not len(p):
            continue
        pts, ms = [], []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            m = d[:, a] * d[:, b] < 0
            tt = np.where(m, d[:, a] / np.where(m, d[:, a] - d[:, b], 1.0), 0.0)
            pts.append(p[:, a] + (p[:, b] - p[:, a]) * tt[:, None])
            ms.append(m)
        pts, ms = np.stack(pts, 1), np.stack(ms, 1)
        for i in range(len(p)):
            q = pts[i][ms[i]]
            if len(q) >= 2:
                out.append((q[0], q[1]))
    return out


def proyectar(ax, objs, base, filtro, luz=(0.35, 0.45, 0.8)):
    """Proyección ortogonal en la base (derecha, arriba, hacia el observador), caras de frente, orden de profundidad
    por baricentro (algoritmo del pintor: alguna cara grande puede quedar mal ordenada)."""
    R, U, F = (np.array(b, dtype=float) for b in base)
    L = np.array(luz) / np.linalg.norm(luz)
    polis, cols, prof = [], [], []
    for nombre, colec, v, t in objs:
        if not filtro(nombre, colec):
            continue
        p = v[t]
        n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
        ln = np.linalg.norm(n, axis=1)
        ok = ln > 1e-12
        p, n = p[ok], n[ok] / ln[ok, None]
        vis = n @ F > 1e-4
        p, n = p[vis], n[vis]
        if len(p):
            polis.append(np.stack([p @ R, p @ U], axis=-1))
            cols.append(np.clip(color(nombre, colec)[None] * (0.5 + 0.5 * np.clip(n @ L, 0, 1))[:, None], 0, 1))
            prof.append((p @ F).mean(axis=1))
    if polis:
        polis, cols, prof = np.concatenate(polis), np.concatenate(cols), np.concatenate(prof)
        o = np.argsort(prof)
        ax.add_collection(PolyCollection(polis[o], facecolors=cols[o], edgecolors="none", antialiased=False))


def trazar(ax, segs, color_, lw=0.6, alfa=1.0):
    ls = []
    for s in segs:
        ls += [[s[i], s[i + 1]] for i in range(len(s) - 1)]
    ax.add_collection(LineCollection(ls, colors=color_, linewidths=lw, alpha=alfa))


def lienzo(ventana, tam, titulo, paso, invertir=False):
    u0, u1, v0, v1 = ventana
    fig, ax = plt.subplots(figsize=tam, dpi=100)
    ax.set_xlim((u1, u0) if invertir else (u0, u1))
    ax.set_ylim(v0, v1)
    ax.set_aspect("equal")
    ax.set_xticks(np.arange(math.ceil(u0 / paso) * paso, u1 + 1e-9, paso))
    ax.set_yticks(np.arange(math.ceil(v0 / paso) * paso, v1 + 1e-9, paso))
    ax.tick_params(labelsize=7)
    ax.grid(alpha=0.2)
    ax.set_title(titulo, fontsize=11)
    return fig, ax


def guardar(fig, carpeta, nombre):
    fig.tight_layout()
    fig.savefig(os.path.join(carpeta, nombre + ".jpg"), dpi=100, pil_kwargs={"quality": 88})
    plt.close(fig)
    print("  ", nombre + ".jpg")


def buscar(carpeta, patron):
    r = sorted(glob.glob(os.path.join(carpeta, patron)))
    if not r:
        raise FileNotFoundError(f"no encuentro {patron} en {carpeta}")
    return r[0]


def main(geom, carpeta_dxf, sal):
    os.makedirs(sal, exist_ok=True)
    planta = buscar(carpeta_dxf, "*PLANTA_BAJA*.dxf")
    so = buscar(carpeta_dxf, "*SUROESTE*.dxf")
    eo = buscar(carpeta_dxf, "*ESTE_y_FachadaOESTE*.dxf")
    me2 = buscar(carpeta_dxf, "*ME-2*.dxf")
    objs = cargar_geom(geom)
    edificio = lambda n, c: not c.startswith(("06", "10")) and "INTERIOR" not in n
    # plantas del Lado Aire
    s1 = corte(objs, 2, 1.0, lambda n, c: not c.startswith("10"))
    s0 = corte(objs, 2, -0.10, lambda n, c: c.startswith("06"))
    for nombre, ventana, tam, paso in (("LADO_AIRE_PLANTA_CORTE", (-6, 88, 36, 56), (34, 9.5), 2.0),
                                       ("LADO_AIRE_PLANTA_BLOQUE_MARQUESINA", (-6, 32, 40, 52), (26, 9), 1.0),
                                       ("LADO_AIRE_PLANTA_VESTIBULO_ANEXO", (40, 88, 40, 52), (26, 9), 1.0)):
        fig, ax = lienzo(ventana, tam, "Planta baja: corte del modelo a +1,00 (negro) y veredas y cordón (verde) "
                         "sobre la A111 del cliente (rojo)", paso)
        trazar(ax, lineas_dxf(planta, lambda x, y: (x, y)), "tab:red", 0.5, 0.8)
        trazar(ax, [[a[:2], b[:2]] for a, b in s1], "black", 0.8)
        trazar(ax, [[a[:2], b[:2]] for a, b in s0], "darkgreen", 0.9)
        guardar(fig, sal, nombre)
    # alzados
    vista_so = ((1, 0, 0), (0, 0, 1), (0, 1, 0))
    for nombre, ventana, tam in (("SUPERPOSICION_FACHADA_SUROESTE", (-3, 86, -0.5, 14.5), (34, 7)),
                                 ("LADO_AIRE_ALZADO_SO_OESTE", (-2, 32, -0.5, 9), (30, 9)),
                                 ("LADO_AIRE_ALZADO_SO_CENTRO", (30, 60, -0.5, 9), (30, 9)),
                                 ("LADO_AIRE_ALZADO_SO_ESTE", (56, 86, -0.5, 9), (30, 9))):
        fig, ax = lienzo(ventana, tam, "Alzado SO (Lado Aire): proyección del modelo y alzado del cliente en rojo",
                         1.0, invertir=True)
        proyectar(ax, objs, vista_so, lambda n, c: edificio(n, c) and "LETRERO" not in n)
        trazar(ax, lineas_dxf(so, TF_SO, filtro_x=(100, 192)), "red", 0.6, 0.9)
        guardar(fig, sal, nombre)
    fig, ax = lienzo((-2, 50, -0.5, 14), (32, 9.5), "Alzado ESTE (testero del eje 20): proyección del modelo y CAD en rojo", 1.0)
    proyectar(ax, objs, ((0, 1, 0), (0, 0, 1), (1, 0, 0)), edificio)
    trazar(ax, lineas_dxf(eo, TF_ESTE, filtro_x=(240, 320)), "red", 0.6, 0.9)
    guardar(fig, sal, "SUPERPOSICION_FACHADA_ESTE")
    fig, ax = lienzo((-2, 52, -0.5, 14), (32, 9.5), "Alzado OESTE (testero del eje 1): proyección del modelo y CAD en rojo",
                     1.0, invertir=True)
    proyectar(ax, objs, ((0, 1, 0), (0, 0, 1), (-1, 0, 0)), edificio)
    trazar(ax, lineas_dxf(eo, TF_OESTE, filtro_x=(320, 400)), "red", 0.6, 0.9)
    guardar(fig, sal, "SUPERPOSICION_FACHADA_OESTE")
    # Lado Tierra: paños al ras de las columnas o en nicho
    fig, ax = lienzo((-2, 86, -2.5, 2.5), (36, 3.6), "Fachada NE: corte a +1,50 (nicho solo en los vanos con ME-1/ME-2)", 1.0)
    trazar(ax, [[a[:2], b[:2]] for a, b in corte(objs, 2, 1.5, lambda n, c: c[:2] in ("01", "02", "03", "05"))], "black", 0.7)
    guardar(fig, sal, "LADO_TIERRA_NICHOS_CORTE")
    # ME-2 (eje 4-5, X 14,66): detalle llevado al modelo (vidrio exterior en Y 0,479; interior hacia +Y)
    x0 = 14.66
    sec = lambda n, c: c[:2] in ("01", "02", "03")
    fig, ax = lienzo((14.4, 19.2, 0.4, 0.8), (30, 3.6), "ME-2: corte a +1,00 del modelo (negro) y sección 1 del detalle (rojo)", 0.1)
    trazar(ax, [[a[:2], b[:2]] for a, b in corte(objs, 2, 1.0, sec)], "black", 0.8)
    trazar(ax, lineas_dxf(me2, lambda x, y: (x - 30.148 + x0, 0.479 + (y + 25.45)), filtro_x=(29.9, 34.7)), "red", 0.5, 0.8)
    guardar(fig, sal, "ME2_CORTE_HORIZONTAL")
    fig, ax = lienzo((0.25, 0.95, 1.6, 3.2), (9, 18), "ME-2: corte vertical por el centro (modelo en negro, sección 2 del detalle en rojo)", 0.1)
    trazar(ax, [[(a[1], a[2]), (b[1], b[2])] for a, b in corte(objs, 0, x0 + 2.14, sec)], "black", 0.9)
    trazar(ax, lineas_dxf(me2, lambda x, y: (0.479 + (x - 36.233), y + 24.42), filtro_x=(35.8, 37.4)), "red", 0.5, 0.8)
    guardar(fig, sal, "ME2_CORTE_VERTICAL")
    # retenedor de nieve: corte por el plano del primer nervio con abrazadera
    fig, ax = lienzo((-1.9, 0.2, 8.85, 9.75), (16, 7.5), "Retenedor de nieve: corte por el plano de una abrazadera", 0.05)
    trazar(ax, [[(a[1], a[2]), (b[1], b[2])] for a, b in corte(objs, 0, -0.23 + 0.10 + 0.0125,
                                                            lambda n, c: c[:2] in ("02", "04"))], "black", 0.9)
    guardar(fig, sal, "RETENEDOR_NIEVE_CORTE")
    # Lado Aire en planta: conjunto y piso
    fig, ax = lienzo((-20, 110, -6, 112), (22, 19.5), "Lado Aire en planta (proyección cenital): mangas, 737-800, camino "
                     "y marcas, con la A111 en rojo", 5.0)
    proyectar(ax, objs, ((1, 0, 0), (0, 1, 0), (0, 0, 1)), lambda n, c: "SUELO" not in n and "INTERIOR" not in n)
    trazar(ax, lineas_dxf(planta, lambda x, y: (x, y)), "tab:red", 0.4, 0.7)
    guardar(fig, sal, "LADO_AIRE_PLANTA_GENERAL")
    fig, ax = lienzo((-15, 100, 36, 112), (24, 16), "Piso del Lado Aire (cenital): veredas, cordón, plataforma, camino "
                     "de servicio y marcas", 5.0)
    proyectar(ax, objs, ((1, 0, 0), (0, 1, 0), (0, 0, 1)), lambda n, c: c[:2] in ("01", "02", "06"))
    guardar(fig, sal, "LADO_AIRE_PISO")
    # el 737 número 1, en sus ejes (nariz en el origen)
    av = [(n, c, v, t) for n, c, v, t in objs if n.startswith("UY_AVION_737") and n.endswith("_1")]
    if av:
        todos = np.concatenate([o[2] for o in av])
        fus = next(o for o in av if "FUSELAJE" in o[0])[2]
        mot = next(o for o in av if o[0].startswith("UY_AVION_737_MOTORES_"))[2]
        # rumbo: eje principal del fuselaje en planta, hacia el lado de los motores (están delante del ala)
        c = fus[:, :2].mean(axis=0)
        w, vecs = np.linalg.eigh(np.cov((fus[:, :2] - c).T))
        eje = vecs[:, np.argmax(w)]
        if (mot[:, :2].mean(axis=0) - c) @ eje < 0:
            eje = -eje
        ang = math.atan2(eje[1], eje[0])
        punta = fus[np.argmax(fus[:, :2] @ eje)]
        o0 = np.array([punta[0], punta[1], todos[:, 2].min()])
        loc = []
        for n, c, v, t in av:
            d = v - o0
            x = d[:, 0] * math.cos(ang) + d[:, 1] * math.sin(ang)
            y = -d[:, 0] * math.sin(ang) + d[:, 1] * math.cos(ang)
            loc.append((n, c, np.stack([x, y, d[:, 2]], 1), t))
        fig, axs = plt.subplots(3, 1, figsize=(16, 20), dpi=90)
        for ax, base, tit, lim in ((axs[0], ((-1, 0, 0), (0, 0, 1), (0, -1, 0)), "737-800 genérico: lateral izquierdo", (-2, 41, -1, 14)),
                                   (axs[1], ((-1, 0, 0), (0, -1, 0), (0, 0, 1)), "planta", (-2, 41, -19, 19)),
                                   (axs[2], ((0, -1, 0), (0, 0, 1), (1, 0, 0)), "frente", (-19, 19, -1, 14))):
            proyectar(ax, loc, base, lambda n, c: True)
            ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3]); ax.set_aspect("equal"); ax.grid(alpha=0.2)
            ax.set_title(tit)
        guardar(fig, sal, "AVION_737_800_VISTAS")


if __name__ == "__main__":
    main(*sys.argv[1:4])
