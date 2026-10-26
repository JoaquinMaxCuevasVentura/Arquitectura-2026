"""Planos de construcción en SVG, desde el modelo constructivo (construccion.py).

Ortográficas (alzados, plantas, secciones) y axonométricas (montada, despiece y pasos de montaje), con medidas
en mm de papel: el SVG sale con viewBox en mm y se puede poner tal cual en una lámina o en el libro.

Convenciones:
- Línea vista 0,18 mm; corte 0,35; oculta 0,13 a trazos; cotas 0,1; ejes en almagre, a trazo y punto.
- Corte de madera: con la fibra a lo largo, líneas en su dirección; en testa, anillos. Piedra cortada: negro
  lleno (lo único fijo). Fresno, más claro que el nogal.
- Una pieza hecha de varias cajas (el travesaño y sus espigas) se dibuja sin las costuras entre ellas.

Necesita shapely (solo para dibujar; el instrumento de cálculo sigue sin dependencias).
"""
import itertools
import math

from shapely.geometry import LineString, MultiLineString, Polygon, box as sbox
from shapely.ops import unary_union

TINTA, ALMAGRE, PAPEL = "#1d1c1a", "#9a3b22", "#f4f2ec"
TONO = {"nogal": "#e4ddcf", "fresno": "#f5f1e8", "piedra": "#2b2a28"}
EJE = "xyz"
FUENTE = "'IBM Plex Mono', 'DejaVu Sans Mono', monospace"
_IDS = itertools.count(1)

# (eje de u, signo), (eje de v, signo), (eje de profundidad, signo): cerca = profundidad menor
VISTAS = {
    "frente": ((0, 1), (2, 1), (1, 1)),     # desde −y
    "atras": ((0, -1), (2, 1), (1, -1)),    # desde +y
    "lado": ((1, 1), (2, 1), (0, -1)),      # desde +x: u = y
    "planta": ((0, 1), (1, 1), (2, -1)),    # desde arriba: v = y
}


def _rango(c, eje, signo):
    a, b = c[eje][0] * signo, c[eje][1] * signo
    return (a, b) if a <= b else (b, a)


def _mezcla(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


class Dibujo:
    """Un SVG en mm de papel. Las primitivas se dan en mm del modelo (u, v) y se pasan a papel con la escala."""

    def __init__(self, escala):
        self.e = escala
        self.el = []
        self.defs = []
        self.caja = None

    # --- coordenadas
    def P(self, u, v):
        return (u / self.e, -v / self.e)

    def _crecer(self, xs, ys):
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        if self.caja is None:
            self.caja = [x0, y0, x1, y1]
        else:
            self.caja = [min(self.caja[0], x0), min(self.caja[1], y0), max(self.caja[2], x1), max(self.caja[3], y1)]

    def _d(self, geom):
        """Camino SVG de un polígono o una línea de shapely (en mm del modelo)."""
        partes = []
        geoms = getattr(geom, "geoms", [geom])
        for g in geoms:
            if g.is_empty:
                continue
            if g.geom_type == "Polygon":
                for anillo in [g.exterior, *g.interiors]:
                    pts = [self.P(*p) for p in anillo.coords]
                    self._crecer([p[0] for p in pts], [p[1] for p in pts])
                    partes.append("M" + "L".join(f"{x:.3f},{y:.3f}" for x, y in pts) + "Z")
            elif g.geom_type in ("LineString", "LinearRing"):
                pts = [self.P(*p) for p in g.coords]
                self._crecer([p[0] for p in pts], [p[1] for p in pts])
                partes.append("M" + "L".join(f"{x:.3f},{y:.3f}" for x, y in pts))
            elif g.geom_type in ("MultiPolygon", "MultiLineString", "GeometryCollection"):
                partes.append(self._d(g))
        return "".join(partes)

    # --- primitivas
    def area(self, geom, fill="none", stroke="none", sw=0.18, dash=None, opacity=None):
        d = self._d(geom)
        if not d:
            return
        a = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' fill-opacity="{opacity}"' if opacity is not None else ""
        self.el.append(f'<path d="{d}" fill="{fill}"{o} stroke="{stroke}" stroke-width="{sw}"'
                       f' stroke-linejoin="round" stroke-linecap="round" fill-rule="evenodd"{a}/>')

    def trazo(self, geom, stroke=TINTA, sw=0.18, dash=None):
        if geom is None or geom.is_empty:
            return
        self.area(geom, "none", stroke, sw, dash)

    def linea(self, pts, stroke=TINTA, sw=0.1, dash=None):
        self.trazo(LineString(pts), stroke, sw, dash)

    def texto(self, u, v, s, tam=1.8, anchor="middle", color=TINTA, rot=0, dx=0.0, dy=0.0, peso=400, papel=False):
        """Texto en (u, v) del modelo, corrido dx, dy mm de papel; tam en mm de papel (altura de mayúscula ≈ 0,7 tam)."""
        x, y = self.P(u, v) if not papel else (u, v)
        x, y = x + dx, y + dy
        w = len(s) * tam * 0.6
        self._crecer([x - w, x + w], [y - tam, y + tam * 0.4])
        r = f' transform="rotate({rot} {x:.3f} {y:.3f})"' if rot else ""
        s = s.replace("&", "&amp;").replace("<", "&lt;")
        self.el.append(f'<text x="{x:.3f}" y="{y:.3f}" font-family="{FUENTE}" font-size="{tam}" font-weight="{peso}"'
                       f' text-anchor="{anchor}" fill="{color}"{r}>{s}</text>')

    # --- tramas
    def _trama_lineas(self, ang, paso, color, sw):
        pid = f"t{next(_IDS)}"
        self.defs.append(f'<pattern id="{pid}" patternUnits="userSpaceOnUse" width="{paso}" height="{paso}" '
                         f'patternTransform="rotate({ang})"><line x1="0" y1="0" x2="0" y2="{paso}" stroke="{color}" '
                         f'stroke-width="{sw}"/></pattern>')
        return f"url(#{pid})"

    def anillos(self, geom, fondo, color=TINTA, paso=0.7, sw=0.09):
        """Testa: anillos concéntricos con centro bajo la pieza, recortados a su contorno."""
        if geom.is_empty:
            return
        cid = f"c{next(_IDS)}"
        self.defs.append(f'<clipPath id="{cid}"><path d="{self._d(geom)}" clip-rule="evenodd"/></clipPath>')
        x0, y0, x1, y1 = geom.bounds
        cx, cy = self.P((x0 + x1) / 2 + (x1 - x0) * 0.17, y0 - (y1 - y0) * 0.9)
        (px0, py0), (px1, py1) = self.P(x0, y0), self.P(x1, y1)
        rmax = math.hypot(max(abs(px0 - cx), abs(px1 - cx)), max(abs(py0 - cy), abs(py1 - cy))) + paso
        rmin = max(0.0, math.hypot(0, min(abs(py0 - cy), abs(py1 - cy))) - paso)
        circ = "".join(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}"/>'
                       for r in [rmin + paso * k for k in range(int((rmax - rmin) / paso) + 1)])
        self.area(geom, fondo, "none")
        self.el.append(f'<g clip-path="url(#{cid})" fill="none" stroke="{color}" stroke-width="{sw}">{circ}</g>')

    # --- cotas
    def cota_h(self, u1, u2, v, ref=None, txt=None, lado=1, ext=True):
        """Cota horizontal entre u1 y u2 sobre la línea v; ref: nivel del objeto (para las líneas de referencia)."""
        tick = 0.9 * self.e
        if ext and ref is not None:
            for u in (u1, u2):
                a, b = (ref + lado * 0.8 * self.e, v + lado * 1.2 * self.e)
                self.linea([(u, a), (u, b)], sw=0.08)
        self.linea([(u1 - 1.2 * self.e, v), (u2 + 1.2 * self.e, v)], sw=0.09)
        for u in (u1, u2):
            self.linea([(u - tick / 2, v - tick / 2), (u + tick / 2, v + tick / 2)], sw=0.2)
        t = txt if txt is not None else f"{abs(u2 - u1):g}"
        self.texto((u1 + u2) / 2, v, t, 1.75, dy=-0.7 if lado > 0 else 2.3)

    def cota_v(self, v1, v2, u, ref=None, txt=None, lado=-1, ext=True):
        tick = 0.9 * self.e
        if ext and ref is not None:
            for v in (v1, v2):
                self.linea([(ref + lado * 0.8 * self.e, v), (u + lado * 1.2 * self.e, v)], sw=0.08)
        self.linea([(u, v1 - 1.2 * self.e), (u, v2 + 1.2 * self.e)], sw=0.09)
        for v in (v1, v2):
            self.linea([(u - tick / 2, v - tick / 2), (u + tick / 2, v + tick / 2)], sw=0.2)
        t = txt if txt is not None else f"{abs(v2 - v1):g}"
        x, y = self.P(u, (v1 + v2) / 2)
        self.texto(x - 0.7 if lado < 0 else x + 2.3, y, t, 1.75, rot=-90, papel=True)

    def cadena_h(self, us, v, ref=None, lado=1, textos=None):
        for i, (a, b) in enumerate(zip(us, us[1:])):
            self.cota_h(a, b, v, ref, None if textos is None else textos[i], lado)

    def cadena_v(self, vs, u, ref=None, lado=-1, textos=None):
        for i, (a, b) in enumerate(zip(vs, vs[1:])):
            self.cota_v(a, b, u, ref, None if textos is None else textos[i], lado)

    def eje(self, u1, v1, u2, v2):
        self.linea([(u1, v1), (u2, v2)], stroke=ALMAGRE, sw=0.1, dash="3 0.8 0.5 0.8")

    def marca(self, n, u, v, dx, dy, r=1.55):
        """Número de pieza en un círculo, a dx, dy mm de papel del punto (u, v), con su línea de referencia."""
        x, y = self.P(u, v)
        cx, cy = x + dx, y + dy
        L = math.hypot(dx, dy) or 1
        self.el.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="0.28" fill="{TINTA}"/>')
        self.el.append(f'<line x1="{x:.3f}" y1="{y:.3f}" x2="{cx - dx / L * r:.3f}" y2="{cy - dy / L * r:.3f}" '
                       f'stroke="{TINTA}" stroke-width="0.09"/>')
        self.el.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r}" fill="{PAPEL}" stroke="{TINTA}" stroke-width="0.13"/>')
        self.texto(cx, cy + 0.62, str(n), 1.7, papel=True)
        self._crecer([cx - r, cx + r], [cy - r, cy + r])

    def rotulo(self, u, v, s, dx=0.0, dy=0.0, anchor="start", color=TINTA, tam=1.8):
        self.texto(u, v, s, tam, anchor, color, dx=dx, dy=dy)

    def svg(self, margen=2.0, ancho=None, alto=None, clase="plano"):
        x0, y0, x1, y1 = self.caja
        x0, y0, x1, y1 = x0 - margen, y0 - margen, x1 + margen, y1 + margen
        w, h = (ancho or x1 - x0), (alto or y1 - y0)
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" class="{clase}" viewBox="{x0:.3f} {y0:.3f} {x1 - x0:.3f} {y1 - y0:.3f}" '
                f'width="{w:.3f}mm" height="{h:.3f}mm">{defs}{"".join(self.el)}</svg>')


# ------------------------------------------------------------------ ortográficas

def _seams(rects):
    """Segmentos internos: bordes compartidos por dos cajas de la misma pieza con sus caras de adelante en el mismo plano."""
    out = []
    for (a, da), (b, db) in itertools.combinations(rects, 2):
        if abs(da - db) > 1e-6:
            continue
        inter = a.intersection(b)
        if inter.is_empty or inter.length == 0 or inter.area > 1e-6:
            continue
        out.append(inter)
    return unary_union(out) if out else None


def ortografica(dib, solidos, vista, corte=None, ocultos=(), excluir=(), recorte=None, tramas=True, tonos=True,
                resaltar=()):
    """Dibuja una vista en `dib`. corte: profundidad del plano de corte (en la coordenada de profundidad de la vista).
    ocultos: prefijos de piezas (o 'vacios:prefijo') cuyas partes tapadas se dibujan a trazos.
    recorte: (u0, v0, u1, v1) en mm del modelo, para los detalles."""
    (ua, us), (va, vs), (da, ds) = VISTAS[vista]
    clip = sbox(*recorte) if recorte else None
    items = []
    for s in solidos:
        if any(s.nombre.startswith(x) for x in excluir):
            continue
        for c in s.cajas:
            u, v, d = _rango(c, ua, us), _rango(c, va, vs), _rango(c, da, ds)
            if corte is not None and d[1] <= corte + 1e-6:
                continue
            cortada = corte is not None and d[0] < corte - 1e-6
            near = max(d[0], corte) if corte is not None else d[0]
            items.append(dict(s=s, c=c, r=sbox(u[0], v[0], u[1], v[1]), near=near, far=d[1], d=d, cortada=cortada))
    items.sort(key=lambda it: (-it["near"], -it["far"]))
    # costuras por pieza
    por_pieza = {}
    for it in items:
        por_pieza.setdefault(id(it["s"]), []).append((it["r"], it["near"]))
    costuras = {k: _seams(v) for k, v in por_pieza.items()}

    def recortar(g):
        return g.intersection(clip) if clip is not None else g

    pintado = []
    for k, it in enumerate(items):
        s, r = it["s"], it["r"]
        geom = r
        aberturas = []
        for vac in s.vacios:
            vu, vv, vd = _rango(vac, ua, us), _rango(vac, va, vs), _rango(vac, da, ds)
            vr = sbox(vu[0], vv[0], vu[1], vv[1]).intersection(r)
            if vr.is_empty or vr.area < 1e-6:
                continue
            if vd[0] <= it["near"] + 1e-6 and vd[1] >= it["far"] - 1e-6:
                geom = geom.difference(vr)                       # pasante: se ve lo de atrás
            elif abs(vd[0] - it["near"]) < 1e-6:
                aberturas.append(vr)                             # se abre en la cara que se ve
        tono = TONO[s.material] if tonos else PAPEL
        if s.nombre.split()[0] in resaltar or s.nombre in resaltar:
            tono = _mezcla(PAPEL, ALMAGRE, 0.35)
        g = recortar(geom)
        dib.area(g, tono, "none")
        for a in aberturas:
            dib.area(recortar(a), _mezcla(tono, TINTA, 0.55), TINTA, 0.1)
        borde = geom.boundary
        cs = costuras.get(id(s))
        if cs is not None:
            borde = borde.difference(cs.buffer(1e-3))
        dib.trazo(recortar(borde), TINTA, 0.18)
        pintado.append((k, it, geom))
    # partes ocultas
    if ocultos:
        for k, it, geom in pintado:
            s = it["s"]
            quiere = any(s.nombre.startswith(x) for x in ocultos)
            vac_q = any(x.startswith("vacios:") and s.nombre.startswith(x[7:]) for x in ocultos)
            delante = [g for j, it2, g in pintado if j > k and it2["near"] < it["near"] - 1e-6] + \
                      [g for j, it2, g in pintado if j > k and it2["s"] is not s and it2["near"] <= it["near"] + 1e-6]
            tapa = unary_union(delante) if delante else None
            if quiere and tapa is not None:
                dib.trazo(recortar(geom.boundary.intersection(tapa)), TINTA, 0.13, "1.1 0.7")
            if vac_q:
                for vac in s.vacios:
                    vu, vv, vd = _rango(vac, ua, us), _rango(vac, va, vs), _rango(vac, da, ds)
                    if vd[0] <= it["near"] + 1e-6:
                        continue
                    vr = sbox(vu[0], vv[0], vu[1], vv[1]).intersection(it["r"])
                    if not vr.is_empty:
                        dib.trazo(recortar(vr.boundary), TINTA, 0.13, "1.1 0.7")
    # caras cortadas
    if corte is not None:
        cortes = {}
        for it in items:
            if it["cortada"]:
                cortes.setdefault(id(it["s"]), (it["s"], []))[1].append(it["r"])
        for s, rs in cortes.values():
            g = unary_union(rs)
            for vac in s.vacios:
                vd = _rango(vac, da, ds)
                if vd[0] < corte < vd[1]:
                    vu, vv = _rango(vac, ua, us), _rango(vac, va, vs)
                    g = g.difference(sbox(vu[0], vv[0], vu[1], vv[1]))
            g = recortar(g)
            if g.is_empty:
                continue
            _corte(dib, s, g, EJE[da], EJE[ua], tramas)
            dib.trazo(g.boundary, TINTA, 0.35)
    return items


def _corte(dib, s, g, eje_vista, eje_u, tramas):
    if s.material == "piedra":
        dib.area(g, TINTA, "none")
        return
    fondo = TONO[s.material] if s.material == "nogal" else PAPEL
    if not tramas:
        dib.area(g, fondo, "none")
        return
    paso = 0.75 if s.material == "nogal" else 1.25
    if s.veta == eje_vista:
        dib.anillos(g, fondo, paso=paso * 0.95)
    else:
        ang = 90 if s.veta == eje_u else 0
        dib.area(g, fondo, "none")
        dib.area(g, dib._trama_lineas(ang, paso, TINTA, 0.08), "none")


# ------------------------------------------------------------------ axonométricas

def _restar(a, b):
    """Caja a menos caja b, en cajas disjuntas."""
    inter = [(max(a[i][0], b[i][0]), min(a[i][1], b[i][1])) for i in range(3)]
    if any(i1 - i0 <= 1e-6 for i0, i1 in inter):
        return [a]
    out, resto = [], [list(r) for r in a]
    for i in range(3):
        lo, hi = resto[i]
        if lo < inter[i][0] - 1e-6:
            c = [tuple(r) for r in resto]
            c[i] = (lo, inter[i][0])
            out.append(tuple(c))
        if hi > inter[i][1] + 1e-6:
            c = [tuple(r) for r in resto]
            c[i] = (inter[i][1], hi)
            out.append(tuple(c))
        resto[i] = list(inter[i])
    return out


def _mover(c, d):
    return tuple((c[i][0] + d[i], c[i][1] + d[i]) for i in range(3))


def _dentro(c, vacios):
    return any(all(v[i][0] - 0.1 <= c[i][0] and c[i][1] <= v[i][1] + 0.1 for i in range(3)) for v in vacios)


class _Pieza3D:
    def __init__(self, s, cajas, vacios):
        self.s, self.cajas, self.vacios = s, cajas, vacios


def preparar(solidos, desplazar=None, quitar=()):
    """Mueve cada grupo y recorta lo que entra en otra pieza (la espiga dentro de su caja no se ve)."""
    desplazar = desplazar or {}
    ps = []
    for s in solidos:
        if any(s.nombre.startswith(q) for q in quitar):
            continue
        d = desplazar.get(s.grupo, desplazar.get(s.nombre, (0, 0, 0)))
        ps.append(_Pieza3D(s, [_mover(c, d) for c in s.cajas], [_mover(v, d) for v in s.vacios]))
    for a in ps:
        nuevas = []
        for c in a.cajas:
            partes = [c]
            for b in ps:
                if b is a:
                    continue
                for cb in b.cajas:
                    sig = []
                    for p in partes:
                        inter = tuple((max(p[i][0], cb[i][0]), min(p[i][1], cb[i][1])) for i in range(3))
                        if all(i1 - i0 > 0.1 for i0, i1 in inter) and _dentro(inter, b.vacios):
                            sig += _restar(p, inter)
                        else:
                            sig.append(p)
                    partes = sig
            nuevas += partes
        a.cajas = [c for c in nuevas if all(c[i][1] - c[i][0] > 0.05 for i in range(3))]
    return ps


def axonometrica(dib, solidos, p=(1.0, -1.35, 0.95), desplazar=None, quitar=(), resaltar=(), grises=False,
                 aristas=0.16):
    """Axonometría con el observador en la dirección p (x, y, z). Pinta con el algoritmo del pintor: cada par de
    cajas que se tapan se ordena por el plano que las separa."""
    n = math.sqrt(sum(x * x for x in p))
    p = tuple(x / n for x in p)
    r = (-p[1], p[0], 0.0)
    nr = math.hypot(r[0], r[1])
    r = (r[0] / nr, r[1] / nr, 0.0)
    up = (p[1] * r[2] - p[2] * r[1], p[2] * r[0] - p[0] * r[2], p[0] * r[1] - p[1] * r[0])
    if up[2] < 0:
        up = tuple(-x for x in up)

    def proy(x, y, z):
        return (x * r[0] + y * r[1] + z * r[2], x * up[0] + y * up[1] + z * up[2])

    piezas = preparar(solidos, desplazar, quitar)
    cajas = []
    for pz in piezas:
        for c in pz.cajas:
            pts = [proy(c[0][i], c[1][j], c[2][k]) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
            cajas.append(dict(p=pz, c=c, hull=Polygon(pts).convex_hull))
    N = len(cajas)
    antes = [set() for _ in range(N)]      # antes[j]: índices que se pintan antes que j
    for i in range(N):
        for j in range(i + 1, N):
            a, b = cajas[i], cajas[j]
            if not a["hull"].intersects(b["hull"]) or a["hull"].intersection(b["hull"]).area < 1e-4:
                continue
            ca, cb = a["c"], b["c"]
            orden = None
            for k in range(3):
                if abs(p[k]) < 1e-9:
                    continue
                if ca[k][1] <= cb[k][0] + 1e-6:
                    orden = (i, j) if p[k] > 0 else (j, i)
                elif cb[k][1] <= ca[k][0] + 1e-6:
                    orden = (j, i) if p[k] > 0 else (i, j)
                if orden:
                    break
            if orden:
                antes[orden[1]].add(orden[0])
    # orden topológico (si hay ciclos, por profundidad)
    prof = [sum(((c["c"][k][0] + c["c"][k][1]) / 2) * p[k] for k in range(3)) for c in cajas]
    hecho, orden = set(), []
    pend = sorted(range(N), key=lambda i: prof[i])
    while pend:
        listo = [i for i in pend if antes[i] <= hecho]
        if not listo:
            listo = [pend[0]]
        for i in listo:
            orden.append(i)
            hecho.add(i)
        pend = [i for i in pend if i not in hecho]
    caras_vistas = [(0, 1 if p[0] > 0 else 0), (1, 1 if p[1] > 0 else 0), (2, 1 if p[2] > 0 else 0)]
    sombra = {0: 0.10, 1: 0.04, 2: 0.0}
    for i in orden:
        cj = cajas[i]
        pz, c = cj["p"], cj["c"]
        s = pz.s
        base = TONO[s.material]
        if s.nombre.split()[0] in resaltar or s.nombre in resaltar or s.grupo in resaltar:
            base = _mezcla(PAPEL, ALMAGRE, 0.45)
        if grises:
            base = "#ffffff" if s.material != "piedra" else "#3a3937"
        for eje, lado in caras_vistas:
            val = c[eje][lado]
            otros = [k for k in range(3) if k != eje]
            a_, b_ = otros
            esquinas = []
            for (ia, ib) in ((0, 0), (1, 0), (1, 1), (0, 1)):
                q = [0, 0, 0]
                q[eje], q[a_], q[b_] = val, c[a_][ia], c[b_][ib]
                esquinas.append(proy(*q))
            cara = Polygon(esquinas)
            if cara.area < 1e-6:
                continue
            tono = _mezcla(base, TINTA, sombra[eje]) if s.material != "piedra" else _mezcla(base, "#000000", sombra[eje] * 2)
            dib.area(cara, tono, "none")
            # aberturas en esta cara
            for vac in pz.vacios:
                if abs(vac[eje][lado] - val) > 1e-6:
                    continue
                if any(vac[k][1] <= c[k][0] + 1e-6 or vac[k][0] >= c[k][1] - 1e-6 for k in otros):
                    continue
                lo = [max(vac[k][0], c[k][0]) for k in range(3)]
                hi = [min(vac[k][1], c[k][1]) for k in range(3)]
                pts = []
                for (ia, ib) in ((0, 0), (1, 0), (1, 1), (0, 1)):
                    q = [0, 0, 0]
                    q[eje] = val
                    q[a_] = (lo[a_], hi[a_])[ia]
                    q[b_] = (lo[b_], hi[b_])[ib]
                    pts.append(proy(*q))
                dib.area(Polygon(pts), _mezcla(tono, TINTA, 0.6) if s.material != "piedra" else "#0b0b0b", TINTA, 0.08)
            # aristas, sin las costuras con otras cajas de la misma pieza
            for k in range(4):
                p1, p2 = esquinas[k], esquinas[(k + 1) % 4]
                if _arista_interna(pz, c, eje, lado, k):
                    continue
                dib.linea([p1, p2], TINTA, aristas)
    return piezas


def _arista_interna(pz, c, eje, lado, k):
    """¿La arista k de la cara (eje, lado) de la caja c es una costura con otra caja coplanar de la misma pieza?"""
    otros = [i for i in range(3) if i != eje]
    a_, b_ = otros
    # aristas: 0: b=lo (a de lo a hi); 1: a=hi; 2: b=hi; 3: a=lo
    eje_borde, lado_borde = [(b_, 0), (a_, 1), (b_, 1), (a_, 0)][k]
    val = c[eje][lado]
    borde = c[eje_borde][lado_borde]
    paralelo = a_ if eje_borde == b_ else b_
    medio = (c[paralelo][0] + c[paralelo][1]) / 2
    for o in pz.cajas:
        if o is c:
            continue
        if abs(o[eje][lado] - val) > 1e-6:
            continue
        # la otra caja sigue del otro lado del borde, en el mismo plano
        if lado_borde == 1 and abs(o[eje_borde][0] - borde) < 1e-6 and o[paralelo][0] <= medio <= o[paralelo][1]:
            return True
        if lado_borde == 0 and abs(o[eje_borde][1] - borde) < 1e-6 and o[paralelo][0] <= medio <= o[paralelo][1]:
            return True
    return False
