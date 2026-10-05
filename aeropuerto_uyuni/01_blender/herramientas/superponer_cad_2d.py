"""Verificación sin render: cortes y proyecciones ortogonales del modelo superpuestos con los DXF del cliente.

Dibuja con matplotlib la geometría que exporta exportar_geometria.py (no usa Cycles ni EEVEE). Láminas:
  LADO_AIRE_PLANTA_*            corte a +1,00 y veredas sobre la planta baja A111
  SUPERPOSICION_FACHADA_*       alzados SO, ESTE y OESTE (proyección con orden de profundidad) y su DXF en rojo
  LADO_AIRE_ALZADO_SO_*         tramos del alzado SO
  LADO_TIERRA_NICHOS_CORTE      corte a +1,50 de la fachada NE (paños al ras o en nicho)
  ME2_CORTE_*                   cortes de la puerta ME-2 sobre su detalle
  RETENEDOR_NIEVE_CORTE         corte por el plano de una abrazadera
  LADO_AIRE_PLANTA_GENERAL / _PISO, AVION_737_800_VISTAS (con la librea de BoA, los dos lados)
  LADO_TIERRA_PLANTA_VEREDAS / _VEREDA_*   corte a -0,10 de veredas, cordones y jardineras sobre la A111
  LADO_TIERRA_PLANTA_SITIO / _FRENTE       sitio y frente del modelo del cliente: calzada, jardineras, plaza (cenital)
  CONTEXTO_PLATAFORMA_RODAJE / _AEROPUERTO_PLANTA / _PISTA_CABECERAS   plataforma, rodaje, pista y marcas
  CONTEXTO_HORIZONTE                       horizonte de cerros visto desde la terminal y hacia dónde mira cada cámara
  ENCUADRE_CAM_10/04/01/07_*               encuadre aproximado de esas cámaras, en perspectiva y sin render
Los DXF son los del cliente (no van en el repositorio, están en UYUNI_insumos_cliente.zip); se buscan por nombre.
Sin ellos (carpeta "-"), las láminas salen igual, con el modelo solo: sirve para revisar sitio, pista y encuadres.

Uso (Python con numpy, matplotlib y ezdxf):
  python superponer_cad_2d.py /tmp/geometria.npz carpeta_con_los_dxf ../verificacion
  python superponer_cad_2d.py /tmp/geometria.npz - /tmp/laminas          (sin los DXF del cliente)
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
             "05": (0.62, 0.36, 0.22), "06": (0.78, 0.76, 0.70), "10": (0.90, 0.91, 0.93), "11": (0.70, 0.70, 0.70)}
AZUL_BOA = (0.11, 0.25, 0.58)
COLOR_NOMBRE = [("LIBREA_DERIVA_ROJO", (0.84, 0.17, 0.12)), ("LIBREA_DERIVA_AMARILLO", (0.96, 0.82, 0.0)),
                ("LIBREA_DERIVA_VERDE", (0.0, 0.47, 0.20)), ("LIBREA", AZUL_BOA), ("AVION_737_DERIVA", AZUL_BOA),
                ("AVION_737_WINGLETS", AZUL_BOA), ("MANGA_VIENTO_FRANJAS_NARANJA", (0.91, 0.38, 0.10)),
                ("CAMINO_SERVICIO_AIRE_MARCAS", (0.95, 0.95, 0.93)), ("CAMINO_SERVICIO", (0.22, 0.22, 0.22)),
                ("MARCAS_AMARILLAS", (0.88, 0.68, 0.10)), ("AMARILLA", (0.88, 0.68, 0.10)),
                ("MARCAS_BLANCAS", (0.97, 0.97, 0.95)), ("SENALIZACION_VIAL", (0.97, 0.97, 0.95)),
                ("PLATAFORMA_AIRE", (0.70, 0.68, 0.64)), ("JARDINERAS_TIERRA", (0.17, 0.14, 0.12)),
                ("ANILLOS_TIERRA", (0.17, 0.14, 0.12)), ("ANILLOS_BLANCOS", (0.93, 0.92, 0.89)),
                ("CORDONES_AMARILLOS", (0.85, 0.65, 0.08)), ("ESPIGA", (0.85, 0.65, 0.08)),
                ("COLUMNAS_AMARILLAS", (0.85, 0.65, 0.08)), ("ANDENES", (0.80, 0.78, 0.73)),
                ("PASOS_ME2", (0.80, 0.78, 0.73)), ("PLAZA_ASFALTO", (0.25, 0.25, 0.25)),
                ("VEREDA", (0.86, 0.83, 0.76)), ("CORDON", (0.55, 0.55, 0.53)), ("CALZADA", (0.25, 0.25, 0.25)),
                ("PISTA", (0.27, 0.27, 0.27)), ("RODAJE_ASFALTO", (0.27, 0.27, 0.27)),
                ("ACERA", (0.86, 0.83, 0.76)), ("SUELO", (0.76, 0.70, 0.56)), ("VIDRIO", (0.25, 0.42, 0.55)),
                ("GLASS", (0.25, 0.42, 0.55)), ("FUELLE", (0.15, 0.15, 0.15))]
NORTE_LOCAL_DEG = 301.043        # norte verdadero en coordenadas locales (antihorario desde +X), como en el modelo


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
    if not ruta:                      # sin el DXF del cliente: la lámina sale solo con el modelo
        return []
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


def cargar_extra(ruta):
    """Puntos de las dispersiones {nombre: (n, 3)} y cámaras {nombre: (posición, dirección, focal, sensor)} del .npz."""
    d = np.load(ruta, allow_pickle=False)
    puntos = {str(n): d[f"puntos{k}"] for k, n in enumerate(d["puntos_nombres"])} if "puntos_nombres" in d else {}
    camaras = ({str(n): (c[:3], c[3:6], c[6], c[7]) for n, c in zip(d["camaras_nombres"], d["camaras"])}
               if "camaras_nombres" in d else {})
    return puntos, camaras


def vista_perspectiva(objs, puntos, cam, titulo, carpeta, nombre, aspecto=16 / 9, cerca=2.0):
    """Encuadre aproximado de una cámara SIN render: proyección en perspectiva con recorte en el plano cercano, orden
    de pintor (puede ordenar mal alguna cara grande), sombreado plano, cielo liso y la paja brava como puntos."""
    pos, d, focal, sensor = cam
    pos, d = np.asarray(pos, float), np.asarray(d, float) / np.linalg.norm(d)
    der = np.cross(d, (0.0, 0.0, 1.0))
    der /= np.linalg.norm(der)
    arr = np.cross(der, d)
    W, H = sensor, sensor / aspecto
    L = np.array((0.35, 0.45, 0.8)) / np.linalg.norm((0.35, 0.45, 0.8))
    polis, cols, prof = [], [], []
    for nom, colec, v, t in objs:
        if "INTERIOR" in nom:
            continue
        tri = v[t] - pos
        zz = tri @ d
        vis = (zz > cerca).any(axis=1)
        tri, zz = tri[vis], zz[vis]
        if not len(tri):
            continue
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.where(np.linalg.norm(n, axis=1) > 0, np.linalg.norm(n, axis=1), 1.0)[:, None]
        c = np.array((0.80, 0.74, 0.60)) if "SUELO" in nom else color(nom, colec)
        luz = 0.55 + 0.45 * np.clip(np.abs(n @ L), 0, 1)
        for k in range(len(tri)):
            pts, zs = tri[k], zz[k]
            if (zs <= cerca).any():                                    # recorte contra el plano cercano
                out = []
                for i in range(3):
                    a, b, za, zb = pts[i], pts[(i + 1) % 3], zs[i], zs[(i + 1) % 3]
                    if za > cerca:
                        out.append(a)
                    if (za > cerca) != (zb > cerca):
                        out.append(a + (b - a) * (cerca - za) / (zb - za))
                pts = np.array(out)
                zs = pts @ d
            x, y = (pts @ der) / zs * focal, (pts @ arr) / zs * focal
            if (np.abs(x) > W).all() or (np.abs(y) > H).all():
                continue
            polis.append(np.stack([x, y], -1))
            cols.append(np.clip(c * luz[k], 0, 1))
            prof.append(zs.mean() + (1e7 if "SUELO" in nom else 0.0) + (0.5 if "LIBREA" in nom else 0.0))
    o = np.argsort(-np.array(prof))
    fig, ax = plt.subplots(figsize=(16, 16 / aspecto), dpi=100)
    ax.set_facecolor((0.62, 0.75, 0.90))
    ax.add_collection(PolyCollection([polis[i] for i in o], facecolors=np.array(cols)[o], edgecolors="none",
                                     antialiased=False))
    for p in puntos.values():
        q = p - pos
        z = q @ d
        m = z > cerca
        ax.scatter((q[m] @ der) / z[m] * focal, (q[m] @ arr) / z[m] * focal, s=np.clip(300.0 / z[m], 0.05, 6.0),
                   c=[(0.62, 0.55, 0.30)], linewidths=0)
    ax.set_xlim(-W / 2, W / 2)
    ax.set_ylim(-H / 2, H / 2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(titulo, fontsize=10)
    guardar(fig, carpeta, nombre)


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
            prof.append((p @ F).mean(axis=1) + (0.5 if "LIBREA" in nombre else 0.0))   # la librea, encima de su piel
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
    """Primer DXF que cumple el patrón; None si no está (o si la carpeta es "-")."""
    r = sorted(glob.glob(os.path.join(carpeta, patron))) if carpeta and carpeta != "-" else []
    if not r:
        print(f"   (sin {patron}: las láminas que lo usan salen solo con el modelo)")
        return None
    return r[0]


def main(geom, carpeta_dxf, sal):
    os.makedirs(sal, exist_ok=True)
    planta = buscar(carpeta_dxf, "*PLANTA_BAJA*.dxf")
    so = buscar(carpeta_dxf, "*SUROESTE*.dxf")
    eo = buscar(carpeta_dxf, "*ESTE_y_FachadaOESTE*.dxf")
    me2 = buscar(carpeta_dxf, "*ME-2*.dxf")
    objs = cargar_geom(geom)
    puntos, camaras = cargar_extra(geom)
    edificio = lambda n, c: not c.startswith(("06", "10", "11")) and "INTERIOR" not in n
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
        fig, axs = plt.subplots(4, 1, figsize=(16, 27), dpi=90)
        # bases (derecha, arriba, hacia el observador) sin espejar: derecha x arriba = hacia el observador
        for ax, base, tit, lim in ((axs[0], ((-1, 0, 0), (0, 0, 1), (0, 1, 0)), "737-800 con la librea de BoA: lado izquierdo (puerta L1, mangas)", (-2, 41, -1, 14)),
                                   (axs[1], ((1, 0, 0), (0, 0, 1), (0, -1, 0)), "lado derecho", (-41, 2, -1, 14)),
                                   (axs[2], ((-1, 0, 0), (0, -1, 0), (0, 0, 1)), "planta", (-2, 41, -19, 19)),
                                   (axs[3], ((0, 1, 0), (0, 0, 1), (1, 0, 0)), "frente", (-19, 19, -1, 14))):
            proyectar(ax, loc, base, lambda n, c: True)
            ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3]); ax.set_aspect("equal"); ax.grid(alpha=0.2)
            ax.set_title(tit)
        guardar(fig, sal, "AVION_737_800_VISTAS")
    laminas_contexto(objs, puntos, camaras, planta, sal)


def laminas_contexto(objs, puntos, camaras, planta, sal):
    """Lado Tierra (veredas de la A111 y sitio), aeropuerto (pista, rodaje, plataforma y paja brava), umbrales de la
    pista y horizonte (cerros vistos desde la terminal)."""
    a111 = lineas_dxf(planta, lambda x, y: (x, y))
    sitio = lambda n, c: c.startswith(("06", "11")) and "SUELO" not in n
    s0 = corte(objs, 2, -0.10, sitio)
    for nombre, ventana, tam, paso in (("LADO_TIERRA_PLANTA_VEREDAS", (-8, 90, -12, 4), (34, 6.6), 2.0),
                                       ("LADO_TIERRA_VEREDA_ESQUINA_OESTE", (-6, 6, -10, 2), (12, 12), 0.5),
                                       ("LADO_TIERRA_VEREDA_DARSENA_1", (18, 37, -11, -3), (20, 9.4), 0.5)):
        fig, ax = lienzo(ventana, tam, "Lado Tierra: corte del modelo a -0,10 (veredas, cordones y jardineras, en verde) y "
                         "la A111 del cliente encima (rojo fino)", paso)
        trazar(ax, [[a[:2], b[:2]] for a, b in s0], "darkgreen", 1.6)
        trazar(ax, a111, "red", 0.5, 1.0)
        guardar(fig, sal, nombre)
    cenital = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    def dibujar_paja(ax, ventana, tam_punto):
        for p in puntos.values():
            u0, u1, v0, v1 = ventana
            m = (p[:, 0] > u0) & (p[:, 0] < u1) & (p[:, 1] > v0) & (p[:, 1] < v1)
            ax.scatter(p[m, 0], p[m, 1], s=tam_punto, c=[(0.62, 0.55, 0.30)], linewidths=0)
    fig, ax = lienzo((-30, 112, -68, 58), (20, 17.8), "Sitio del Lado Tierra (cenital): vereda y dársenas de la A111 y el "
                     "frente del modelo del cliente (calzada, jardineras, separador, plaza y calle del eje 20); A111 en rojo",
                     5.0)
    proyectar(ax, objs, cenital, lambda n, c: "SUELO" not in n and "INTERIOR" not in n)
    dibujar_paja(ax, (-30, 112, -68, 58), 2.0)
    trazar(ax, a111, "tab:red", 0.4, 0.7)
    guardar(fig, sal, "LADO_TIERRA_PLANTA_SITIO")
    fig, ax = lienzo((-30, 100, -62, 2), (26, 12.8), "Frente del Lado Tierra (cenital), restituido de las capturas del "
                     "modelo del cliente: jardineras A y B con sus anillos blancos, separador amarillo L1, plaza con "
                     "hexágonos, espiga y andenes, cebra y columnas de la isla sudeste; A111 en rojo", 2.0)
    proyectar(ax, objs, cenital, lambda n, c: "SUELO" not in n and "INTERIOR" not in n)
    trazar(ax, a111, "tab:red", 0.4, 0.7)
    guardar(fig, sal, "LADO_TIERRA_PLANTA_FRENTE")
    fig, ax = lienzo((-140, 280, -80, 380), (18, 19.5), "Plataforma, calle de rodaje y pista (cenital), con la paja brava "
                     "(puntos ocre)", 20.0)
    proyectar(ax, objs, cenital, lambda n, c: "SUELO" not in n and "INTERIOR" not in n)
    dibujar_paja(ax, (-140, 280, -80, 380), 1.2)
    guardar(fig, sal, "CONTEXTO_PLATAFORMA_RODAJE")
    fig, ax = lienzo((-1250, 3150, -150, 470), (36, 6.2), "Aeropuerto (cenital): pista 13/31 de 4000 x 45 m con las X de "
                     "la georreferencia y la Y supuesta (330 m), rodaje, plataforma, calles y acceso a Uyuni (-X)", 100.0)
    proyectar(ax, objs, cenital, lambda n, c: "SUELO" not in n and "INTERIOR" not in n)
    guardar(fig, sal, "CONTEXTO_AEROPUERTO_PLANTA")
    fig, axs = plt.subplots(2, 1, figsize=(30, 9), dpi=100)
    for ax, (u0, u1), tit in ((axs[0], (-1100, -560), "Cabecera 31 (aterrizaje hacia +X)"),
                              (axs[1], (2490, 3030), "Cabecera 13 (aterrizaje hacia -X)")):
        proyectar(ax, objs, cenital, lambda n, c: "PISTA" in n)
        ax.set_xlim(u0, u1); ax.set_ylim(300, 360); ax.set_aspect("equal"); ax.grid(alpha=0.2)
        ax.set_title(tit + ": umbral, designación, zona de toma de contacto, punto de visada y chevrones", fontsize=11)
    guardar(fig, sal, "CONTEXTO_PISTA_CABECERAS")
    # horizonte desde la terminal: elevación aparente del terreno por azimut verdadero
    suelo = next((o for o in objs if o[0] == "UY_SUELO_ALTIPLANO"), None)
    if suelo is not None:
        v = suelo[2]
        fig, ax = plt.subplots(figsize=(30, 7), dpi=100)
        for h, col_, et in ((1.65, "saddlebrown", "a la altura del ojo (1,65 m)"), (26.0, "tab:blue", "a 26 m (CAM_10)")):
            d = v[:, :2] - np.array([41.0, 22.0])
            r = np.hypot(d[:, 0], d[:, 1])
            ok = r > 1000
            az = (NORTE_LOCAL_DEG - np.degrees(np.arctan2(d[ok, 1], d[ok, 0]))) % 360
            el = np.degrees(np.arctan2(v[ok, 2] - h, r[ok]))
            b = np.floor(az * 2).astype(int) % 720
            maximo = np.full(720, -90.0)
            np.maximum.at(maximo, b, el)
            hay = maximo > -89.0                                       # solo los medios grados con vértices
            ax.plot((np.arange(720) / 2 + 0.25)[hay], maximo[hay], color=col_, lw=1.2, label="horizonte " + et)
        ax.axvspan(238, 332, color="0.85", alpha=0.6, label="Salar de Uyuni (plano, desde 18 km)")
        for nombre, (pos, dirc, _, _) in sorted(camaras.items()):
            if not nombre.startswith("CAM_") or nombre == "CAM_DRON":
                continue
            azc = (NORTE_LOCAL_DEG - math.degrees(math.atan2(dirc[1], dirc[0]))) % 360
            ax.axvline(azc, color="0.4", lw=0.6, ls="--")
            ax.text(azc, 3.2, nombre.replace("CAM_", ""), rotation=90, fontsize=7, ha="right", va="top")
        ax.set_xlim(0, 360); ax.set_ylim(-0.6, 3.4); ax.set_xticks(range(0, 361, 15)); ax.grid(alpha=0.25)
        ax.set_xlabel("azimut verdadero (°): 0 N, 90 E, 180 S, 270 O"); ax.set_ylabel("elevación aparente (°)")
        ax.set_title("Horizonte del terreno visto desde la terminal (cerros de CERROS y curvatura de la Tierra); líneas "
                     "de trazos: hacia dónde mira cada cámara", fontsize=11)
        ax.legend(loc="upper left", fontsize=9)
        guardar(fig, sal, "CONTEXTO_HORIZONTE")
    # encuadres aproximados (sin render) de las vistas que muestran el contexto nuevo
    for nombre in ("CAM_10_PISTA_HORIZONTE", "CAM_04_AEREA_GENERAL", "CAM_01_HERO_LADO_TIERRA", "CAM_07_PROPUESTAS"):
        if nombre in camaras:
            vista_perspectiva(objs, puntos, camaras[nombre], f"{nombre}: encuadre aproximado SIN render (orden de pintor, "
                              "sin sombras, cielo liso; la paja brava como puntos)", sal, "ENCUADRE_" + nombre)


if __name__ == "__main__":
    main(*sys.argv[1:4])
