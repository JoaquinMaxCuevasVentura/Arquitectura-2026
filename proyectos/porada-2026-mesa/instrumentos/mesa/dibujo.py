"""Láminas SVG en A3 apaisado (1680 × 1188 px = 4 px por mm de papel).

Notación del artículo: ( ) fuente · * decisión del dibujo · MAYÚSCULAS lo que hace la mano ·
⊥ apoyo · ○ vano · ● masa · = límite (Cuadro 1) · ✕ unión (añadido en este proyecto).
"""
from html import escape

from .geometria import SIMBOLO
from .versiones import H, L, W

PAPEL = "#f6f1e7"
TINTA = "#2b2b2b"
SIENA = "#a5562a"
MADERA = {"nogal": "#b98c63", "fresno": "#e2cba3"}
PIEDRA = "#9aa1a6"
FUENTE = "Helvetica, Arial, sans-serif"
PX_MM = 4.0                      # px por mm de papel


def _fill(pieza, cortada=False):
    if pieza.material.es_piedra:
        return "url(#piedra-corte)" if cortada else "url(#piedra)"
    color = MADERA["fresno"] if "fresno" in pieza.material.nombre else MADERA["nogal"]
    return "#6b4a2e" if cortada else color


def _defs():
    return f"""<defs>
<pattern id="piedra" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
<rect width="6" height="6" fill="{PIEDRA}"/><line x1="0" y1="0" x2="0" y2="6" stroke="#6e757a" stroke-width="1.2"/></pattern>
<pattern id="piedra-corte" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
<rect width="4" height="4" fill="#5d6469"/><line x1="0" y1="0" x2="0" y2="4" stroke="#2f3438" stroke-width="1.4"/></pattern>
</defs>"""


def _texto(x, y, t, tam=13, color=TINTA, peso="normal", anc="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FUENTE}" font-size="{tam}" fill="{color}" '
            f'font-weight="{peso}" text-anchor="{anc}">{escape(t)}</text>')


class Vista:
    """Proyección ortogonal de piezas a un rectángulo de papel. eje_h/eje_v: 'x', 'y' o 'z'."""

    def __init__(self, ox, oy, escala, eje_h, eje_v, rango_h, rango_v):
        self.ox, self.oy, self.k = ox, oy, PX_MM / escala
        self.eh, self.ev, self.rh, self.rv = eje_h, eje_v, rango_h, rango_v

    def p(self, h, v):
        return self.ox + (h - self.rh[0]) * self.k, self.oy + (self.rv[1] - v) * self.k

    def rect(self, pieza, estilo):
        h0, h1 = getattr(pieza, self.eh)
        v0, v1 = getattr(pieza, self.ev)
        x0, y1 = self.p(h0, v0)
        x1, y0 = self.p(h1, v1)
        return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" {estilo}/>'

    @property
    def ancho(self):
        return (self.rh[1] - self.rh[0]) * self.k

    @property
    def alto(self):
        return (self.rv[1] - self.rv[0]) * self.k


def _suelo(v, ancho_extra=20):
    x0, y = v.p(v.rh[0], 0)
    return f'<line x1="{x0 - ancho_extra:.1f}" y1="{y:.1f}" x2="{x0 + v.ancho + ancho_extra:.1f}" y2="{y:.1f}" stroke="{TINTA}" stroke-width="1.6"/>'


def _cota(v, a, b, nivel, texto, horizontal=True):
    if horizontal:
        x0, y = v.p(a, nivel)
        x1, _ = v.p(b, nivel)
        return (f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}" stroke="{TINTA}" stroke-width="0.8"/>'
                f'<line x1="{x0:.1f}" y1="{y - 5:.1f}" x2="{x0:.1f}" y2="{y + 5:.1f}" stroke="{TINTA}" stroke-width="0.8"/>'
                f'<line x1="{x1:.1f}" y1="{y - 5:.1f}" x2="{x1:.1f}" y2="{y + 5:.1f}" stroke="{TINTA}" stroke-width="0.8"/>'
                + _texto((x0 + x1) / 2, y - 6, texto, 11, anc="middle"))
    x, y0 = v.p(nivel, a)
    _, y1 = v.p(nivel, b)
    return (f'<line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y1:.1f}" stroke="{TINTA}" stroke-width="0.8"/>'
            f'<line x1="{x - 5:.1f}" y1="{y0:.1f}" x2="{x + 5:.1f}" y2="{y0:.1f}" stroke="{TINTA}" stroke-width="0.8"/>'
            f'<line x1="{x - 5:.1f}" y1="{y1:.1f}" x2="{x + 5:.1f}" y2="{y1:.1f}" stroke="{TINTA}" stroke-width="0.8"/>'
            + f'<text x="{x - 8:.1f}" y="{(y0 + y1) / 2:.1f}" font-family="{FUENTE}" font-size="11" fill="{TINTA}" '
              f'text-anchor="middle" transform="rotate(-90 {x - 8:.1f} {(y0 + y1) / 2:.1f})">{escape(texto)}</text>')


def _rotulo(v, h, vv, dx, dy, texto, color=TINTA):
    x, y = v.p(h, vv)
    xt, yt = x + dx, y + dy
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="{color}"/>'
            f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{xt:.1f}" y2="{yt:.1f}" stroke="{color}" stroke-width="0.7"/>'
            + _texto(xt + (4 if dx >= 0 else -4), yt + 4, texto, 12, color, anc="start" if dx >= 0 else "end"))


def _piedra_oculta(mesa, v):
    """La piedra que otra pieza tapa se marca con contorno discontinuo (convención de línea oculta)."""
    return "".join(v.rect(p, f'fill="none" stroke="{SIENA}" stroke-width="1.3" stroke-dasharray="4 3"')
                   for p in mesa.piezas if p.material.es_piedra)


def alzado(mesa, v, rotulos=True):
    out = [_suelo(v)]
    for p in sorted(mesa.piezas, key=lambda p: -p.y[0]):            # de atrás hacia adelante, por la cara frontal
        out.append(v.rect(p, f'fill="{_fill(p)}" stroke="{TINTA}" stroke-width="0.9"'))
    out.append(_piedra_oculta(mesa, v))
    if rotulos:
        out += _rotulos_alzado(mesa, v)
    return "".join(out)


def planta(mesa, v):
    out = []
    for p in sorted(mesa.piezas, key=lambda p: p.centro[2]):
        if p.nombre.startswith("tablero"):
            out.append(v.rect(p, f'fill="{MADERA["nogal"]}" fill-opacity="0.35" stroke="{TINTA}" stroke-width="1.2"'))
        elif p.z[1] >= H - 0.1 or p.material.es_piedra and p.z[1] >= H - 0.1:
            out.append(v.rect(p, f'fill="{_fill(p)}" stroke="{TINTA}" stroke-width="1"'))
        else:                                                          # bajo el tablero: líneas ocultas
            out.append(v.rect(p, f'fill="none" stroke="{TINTA}" stroke-width="0.7" stroke-dasharray="5 3"'))
    return "".join(out)


def seccion(mesa, v, x_corte=0.0):
    """Corte transversal por x = x_corte, mirando hacia +x: lo cortado en oscuro, lo de atrás en alzado."""
    out = [_suelo(v)]
    detras = [p for p in mesa.piezas if p.x[0] > x_corte]
    cortadas = [p for p in mesa.piezas if p.x[0] <= x_corte <= p.x[1]]
    for p in sorted(detras, key=lambda p: -p.centro[0]):
        out.append(v.rect(p, f'fill="{_fill(p)}" stroke="{TINTA}" stroke-width="0.7"'))
    for p in cortadas:
        out.append(v.rect(p, f'fill="{_fill(p, True)}" stroke="{TINTA}" stroke-width="1.8"'))
    return "".join(out)


def _rotulos_alzado(mesa, v):
    out = []
    der = [p for p in mesa.piezas if p.centro[0] > 0]
    tab = [p for p in mesa.piezas if p.nombre.startswith("tablero")][0]
    out.append(_rotulo(v, -900, H - 20, 40, -26, f"{SIMBOLO['limite']} tablero, nogal macizo"))
    cab = [p for p in der if p.nombre.startswith("montante")][0]
    out.append(_rotulo(v, cab.centro[0], 560, 60, -20, f"{SIMBOLO['apoyo']} caballete (Gestell, F06)"))
    piedras = [p for p in der if p.material.es_piedra] or [p for p in mesa.piezas if p.material.es_piedra]
    if piedras:
        pi = piedras[0]
        out.append(_rotulo(v, pi.centro[0], pi.centro[2], 70, 60,
                           f"{SIMBOLO[pi.funcion]} {pi.nombre.split(' izq')[0].split(' der')[0]}, mármol",
                           SIENA))
    return out


def detalle_nodo(mesa, v):
    """Alzado ampliado de la unión derecha travesaño-montante (o barra-cabezal en V0)."""
    out = [_suelo(v, 0) if v.rv[0] <= 0 else ""]
    out.append(f'<clipPath id="clip-{mesa.codigo}"><rect x="{v.ox:.1f}" y="{v.oy:.1f}" width="{v.ancho:.1f}" '
               f'height="{v.alto:.1f}"/></clipPath><g clip-path="url(#clip-{mesa.codigo})">')
    for p in sorted(mesa.piezas, key=lambda p: -p.y[0]):
        out.append(v.rect(p, f'fill="{_fill(p)}" stroke="{TINTA}" stroke-width="1.2"'))
    out.append(_piedra_oculta(mesa, v))
    out.append("</g>")
    out += _rotulos_detalle(mesa, v)
    out.append(f'<rect x="{v.ox:.1f}" y="{v.oy:.1f}" width="{v.ancho:.1f}" height="{v.alto:.1f}" fill="none" '
               f'stroke="{TINTA}" stroke-width="0.6" stroke-dasharray="2 3"/>')
    return "".join(out)


NOMBRES_DETALLE = {"montante": "⊥ montante", "travesaño": "⊥ travesaño y espiga pasante", "cabezal": "⊥ cabezal",
                   "tablero": "= tablero", "llave": "✕ llave", "collar": "✕ collar de piedra", "barra": "● barra de piedra",
                   "pie": "⊥ pie"}


def _rotulos_detalle(mesa, v):
    out, vistos, fila = [], set(), 0
    x_txt = v.ox + v.ancho + 14
    for p in sorted(mesa.piezas, key=lambda p: -p.centro[2]):
        clave = p.nombre.split()[0]
        if clave in vistos or p.centro[0] < 0 or clave not in NOMBRES_DETALLE:
            continue
        h = min(max(p.centro[0], v.rh[0] + 5), v.rh[1] - 5)
        z = min(max(p.centro[2], v.rv[0] + 5), v.rv[1] - 5)
        if not (v.rh[0] < p.x[1] and p.x[0] < v.rh[1] and v.rv[0] < p.z[1] and p.z[0] < v.rv[1]):
            continue
        vistos.add(clave)
        x, y = v.p(h, z)
        yt = v.oy + 20 + fila * 34
        color = SIENA if p.material.es_piedra else TINTA
        dims = f"{p.x[1] - p.x[0]:.0f}×{p.y[1] - p.y[0]:.0f}×{p.z[1] - p.z[0]:.0f}"
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{color}"/>'
                   f'<polyline points="{x:.1f},{y:.1f} {x_txt - 6:.1f},{yt:.1f}" fill="none" stroke="{color}" stroke-width="0.6"/>')
        out.append(_texto(x_txt, yt + 4, NOMBRES_DETALLE[clave], 12, color))
        out.append(_texto(x_txt, yt + 18, f"{p.material.nombre.split(' (')[0]} {dims}", 10, color))
        fila += 1
    return out


def _partir(texto, n):
    lineas, actual = [], ""
    for palabra in texto.split(" "):
        if actual and len(actual) + 1 + len(palabra) > n:
            lineas.append(actual)
            actual = "      " + palabra
        else:
            actual = f"{actual} {palabra}" if actual else palabra
    return lineas + [actual]


def _marca(ok):
    return "—" if ok is None else ("✓" if ok else "✗")


def lamina(mesa, r, notas):
    """Lámina de una versión: alzado y planta 1:10, sección 1:10, detalle del nodo 1:2,5 y resultados."""
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1680 1188" width="1680" height="1188">')
    s.append(_defs())
    s.append(f'<rect width="1680" height="1188" fill="{PAPEL}"/>')
    s.append(_texto(60, 70, f"{mesa.codigo} · {mesa.nombre}", 30, peso="bold"))
    s.append(_texto(60, 98, f"{mesa.accion.upper()} — «{mesa.relacion}»", 16, SIENA))
    s.append(_texto(60, 120, f"Ronda {mesa.ronda} · masa {r['masa_total_kg']:.0f} kg (piedra {r['masa_piedra_kg']:.1f} kg) "
                             f"· escalas 1:10 y 1:2,5 (detalle) sobre A3", 13))
    ve = Vista(60, 170, 10, "x", "z", (-L / 2 - 40, L / 2 + 40), (0, H + 30))
    s.append(_texto(60, 145, "ALZADO LONGITUDINAL", 12, peso="bold"))
    s.append(alzado(mesa, ve))
    s.append(_cota(ve, -L / 2, L / 2, H + 18, f"{L:.0f}"))
    s.append(_cota(ve, 0, H, -L / 2 - 25, f"{H:.0f}", horizontal=False))
    vp = Vista(60, 560, 10, "x", "y", (-L / 2 - 40, L / 2 + 40), (-W / 2 - 20, W / 2 + 20))
    s.append(_texto(60, 552, "PLANTA (líneas ocultas: bajo el tablero)", 12, peso="bold"))
    s.append(planta(mesa, vp))
    vs = Vista(1100, 170, 10, "y", "z", (-W / 2 - 20, W / 2 + 20), (0, H + 30))
    s.append(_texto(1100, 145, "SECCIÓN TRANSVERSAL x = 0, mirando al caballete", 12, peso="bold"))
    s.append(seccion(mesa, vs))
    s.append(_cota(vs, -W / 2, W / 2, H + 18, f"{W:.0f}"))
    if mesa.nodo.get("tipo") == "viga":
        rango_h, rango_v = (650, 950), (560, 790)
    else:
        rango_h, rango_v = (700, 960), (180, 420)
    vd = Vista(1100, 560, 2.5, "x", "z", (rango_h[0], rango_h[1] - 60), rango_v)
    s.append(_texto(1100, 552, "DETALLE DE LA UNIÓN (alzado, 1:2,5)", 12, peso="bold"))
    s.append(detalle_nodo(mesa, vd))
    # Resultados
    y = 1000
    s.append(_texto(60, y, "CRITERIOS (prerregistrados en 02_desarmar/problema.md)", 12, peso="bold"))
    for i, (k, d) in enumerate(r["K"].items()):
        s.append(_texto(60 + (i % 3) * 520, y + 30 + (i // 3) * 22, f"{_marca(d['cumple'])} {k} · {d['texto']}"[:88], 12))
    for j, n in enumerate(notas[:4]):
        s.append(_texto(1100, 958 + j * 17, n[:80], 12, SIENA if n.startswith("*") else TINTA))
    s.append(_texto(60, 1150, "( ) fuente del fichero · * decisión del dibujo, no de la fuente · MAYÚSCULAS lo que hace la mano · "
                              "⊥ apoyo ○ vano ● masa = límite ✕ unión · rayado: mármol; ocre: nogal; claro: fresno", 11))
    s.append("</svg>")
    return "".join(s)


def lamina_comparativa(mesas, resultados, titulo, lectura=()):
    cols = 3
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1680 1188" width="1680" height="1188">', _defs(),
         f'<rect width="1680" height="1188" fill="{PAPEL}"/>', _texto(60, 70, titulo, 28, peso="bold"),
         _texto(60, 96, "Alzados longitudinales a 1:20 sobre A3, mismos supuestos; ✓ cumple · ✗ no cumple · — no aplica · "
                "contorno discontinuo: piedra oculta", 14),
         _texto(60, 118, "K1 madera ≥ 85 % del volumen · K2 piedra ≤ 2,3 MPa a flexión · K3 junta ≤ 3 mm/lado · "
                "K4 vuelco sin piedra ≥ 2 P · K5 pieza ≤ 25 kg", 13, SIENA)]
    for i, (m, r) in enumerate(zip(mesas, resultados)):
        ox, oy = 60 + (i % cols) * 540, 150 + (i // cols) * 500
        v = Vista(ox, oy + 40, 20, "x", "z", (-L / 2 - 20, L / 2 + 20), (0, H + 20))
        s.append(_texto(ox, oy + 20, f"{m.codigo} · {m.nombre}", 17, peso="bold"))
        s.append(_texto(ox, oy + 38, m.accion.upper(), 12, SIENA))
        s.append(alzado(m, v, rotulos=False))
        yy = oy + 240
        s.append(_texto(ox, yy, f"masa {r['masa_total_kg']:.0f} kg · piedra {r['masa_piedra_kg']:.1f} kg", 12))
        for j, (k, d) in enumerate(r["K"].items()):
            s.append(_texto(ox, yy + 22 + j * 19, f"{_marca(d['cumple'])} {k} · {d['texto']}"[:86], 11))
    if lectura:
        filas = (len(mesas) - 1) // cols + 1
        libres = filas * cols - len(mesas)
        if libres:                                   # en los huecos de la última fila
            x0, y0, ancho = 60 + (cols - libres) * 540, 150 + (filas - 1) * 500 + 20, libres * 540 - 20
        else:                                        # debajo de la última fila
            x0, y0, ancho = 60, 150 + filas * 500 - 80, 1560
        s.append(_texto(x0, y0, "LECTURA", 13, peso="bold"))
        y = y0 + 26
        for t in lectura:
            for trozo in _partir(t, int(ancho / 6.4)):
                s.append(_texto(x0, y, trozo, 12.5, SIENA if t.startswith("→") else TINTA))
                y += 20
            y += 4
    s.append("</svg>")
    return "".join(s)
