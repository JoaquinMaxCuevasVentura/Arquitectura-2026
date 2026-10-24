"""Ayudas comunes para dibujar las láminas en SVG (milímetros de papel)."""
import base64
import os

AQUI = os.path.dirname(os.path.abspath(__file__))

# Colores por fuente (referencias graficas.md §3)
F = "#1b1b1b"        # Flaubert
B = "#8a5a2b"        # Boitard (sepia del grabado)
I = "#c8341e"        # inferencia
G = "#2f5d8a"        # salidas de modelos (reservado)
AMARILLO = "#f2d64b" # lo que la regla pedía y la copia no hizo
GRIS = "#9a9a9a"
PAPEL = "#ffffff"
# Halo blanco para rótulos sobre tramas
HALO = 'stroke="#ffffff" stroke-width="0.55" stroke-linejoin="round" paint-order="stroke"'
MACIZO = "#eadfcb"   # macizos de Wissous

FUENTES = [
    ("Garamond", "normal", 400, "eb-garamond-latin-400-normal.woff2"),
    ("Garamond", "italic", 400, "eb-garamond-latin-400-italic.woff2"),
    ("Garamond", "normal", 600, "eb-garamond-latin-600-normal.woff2"),
    ("Plex", "normal", 400, "ibm-plex-sans-condensed-latin-400-normal.woff2"),
    ("Plex", "normal", 500, "ibm-plex-sans-condensed-latin-500-normal.woff2"),
]


def estilo_fuentes(carpeta):
    """@font-face con las fuentes incrustadas (SIL OFL), para que el SVG viaje solo."""
    reglas = []
    for fam, est, peso, archivo in FUENTES:
        ruta = os.path.join(carpeta, archivo)
        datos = base64.b64encode(open(ruta, "rb").read()).decode()
        reglas.append(
            f"@font-face{{font-family:'{fam}';font-style:{est};font-weight:{peso};"
            f"src:url(data:font/woff2;base64,{datos}) format('woff2');}}")
    return "\n".join(reglas)


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# Anchos de carácter medidos con Chromium (medir_anchos.js), en em
_ANCHOS = None


def ancho(t, fuente="p400", tam=2.4):
    """Ancho aproximado de un texto en mm (sin interletraje)."""
    global _ANCHOS
    if _ANCHOS is None:
        import json
        _ANCHOS = json.load(open(os.path.join(AQUI, "anchos.json"), encoding="utf-8"))
    tabla = _ANCHOS[fuente]
    return sum(tabla.get(c, 0.5) for c in str(t)) * tam


def partir(t, ancho_mm, fuente="p400", tam=2.4):
    """Corta un texto en líneas que no pasen de ancho_mm."""
    lineas, actual = [], ""
    for palabra in str(t).split():
        prueba = (actual + " " + palabra).strip()
        if actual and ancho(prueba, fuente, tam) > ancho_mm:
            lineas.append(actual)
            actual = palabra
        else:
            actual = prueba
    if actual:
        lineas.append(actual)
    return lineas


class Hoja:
    """Una hoja en mm. Junta elementos SVG y escribe el archivo."""

    def __init__(self, ancho, alto, carpeta_fuentes):
        self.ancho, self.alto = ancho, alto
        self.partes = []
        self.defs = []
        self.carpeta_fuentes = carpeta_fuentes

    def add(self, s):
        self.partes.append(s)

    def svg(self):
        css = estilo_fuentes(self.carpeta_fuentes) + """
text{font-family:'Plex','IBM Plex Sans Condensed',sans-serif}
.g{font-family:'Garamond','EB Garamond',serif}
.gi{font-family:'Garamond','EB Garamond',serif;font-style:italic}
.b{font-weight:500}
"""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{self.ancho}mm" height="{self.alto}mm" '
                f'viewBox="0 0 {self.ancho} {self.alto}">\n'
                f'<style>{css}</style>\n<defs>{"".join(self.defs)}</defs>\n'
                f'<rect width="{self.ancho}" height="{self.alto}" fill="{PAPEL}"/>\n'
                + "\n".join(self.partes) + "\n</svg>\n")

    def guardar(self, ruta):
        open(ruta, "w", encoding="utf-8").write(self.svg())


class Vista:
    """Pasa de metros del modelo a mm de la hoja: escala 1:e, origen y eje y hacia arriba."""

    def __init__(self, x_mm, y_mm, escala, x0=0.0, y0=0.0, voltear=True):
        self.x_mm, self.y_mm = x_mm, y_mm   # dónde cae (x0, y0) en la hoja
        self.k = 1000.0 / escala             # mm de papel por metro
        self.x0, self.y0 = x0, y0
        self.voltear = voltear

    def p(self, x, y):
        X = self.x_mm + (x - self.x0) * self.k
        Y = self.y_mm - (y - self.y0) * self.k if self.voltear else self.y_mm + (y - self.y0) * self.k
        return round(X, 3), round(Y, 3)

    def d(self, pts, cerrar=True):
        s = " ".join(f"{'M' if i == 0 else 'L'}{x},{y}"
                     for i, (x, y) in enumerate(self.p(*q) for q in pts))
        return s + (" Z" if cerrar else "")


def trazo(color=F, ancho=0.25, guion=None, relleno="none", opacidad=None, extra=""):
    s = f'stroke="{color}" stroke-width="{ancho}" fill="{relleno}"'
    if guion:
        s += f' stroke-dasharray="{guion}"'
    if opacidad is not None:
        s += f' fill-opacity="{opacidad}"'
    s += ' stroke-linejoin="round" stroke-linecap="round"'
    return s + (" " + extra if extra else "")


def texto(x, y, t, tam=2.4, color=F, clase="", ancla="start", peso=None, extra=""):
    c = f' class="{clase}"' if clase else ""
    w = f' font-weight="{peso}"' if peso else ""
    return (f'<text x="{x}" y="{y}" font-size="{tam}" fill="{color}" '
            f'text-anchor="{ancla}"{c}{w} {extra}>{esc(t)}</text>')


def texto_lineas(x, y, lineas, tam=2.4, interlinea=1.25, **kw):
    """Varias líneas; cada línea puede ser str o lista de (texto, clase, color)."""
    out = []
    for i, ln in enumerate(lineas):
        yy = round(y + i * tam * interlinea, 3)
        if isinstance(ln, str):
            out.append(texto(x, yy, ln, tam, **kw))
        else:
            spans = "".join(
                f'<tspan{(" class=" + chr(34) + c + chr(34)) if c else ""}'
                f'{(" fill=" + chr(34) + col + chr(34)) if col else ""}>{esc(t)}</tspan>'
                for t, c, col in ln)
            anc = kw.get("ancla", "start")
            col = kw.get("color", F)
            cl = f' class="{kw["clase"]}"' if kw.get("clase") else ""
            out.append(f'<text x="{x}" y="{yy}" font-size="{tam}" fill="{col}" '
                       f'text-anchor="{anc}"{cl}>{spans}</text>')
    return "\n".join(out)


def numero(x, y, n, r=1.55, lleno=False, color=F, tam=None):
    """Número en un círculo: abierto (equivale a uno de Wissous) o lleno (20 y más)."""
    tam = tam or r * 1.25
    fondo = color if lleno else PAPEL
    tc = PAPEL if lleno else color
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fondo}" stroke="{color}" stroke-width="0.22"/>'
            + texto(x, round(y + tam * 0.36, 3), n, tam, tc, ancla="middle", peso=500))


def barra_escala(x, y, escala, metros=(0, 5, 10, 20, 30), etiqueta="", color=I):
    """Barra de escala gráfica; va en rojo porque la escala es supuesta (I)."""
    k = 1000.0 / escala
    out = []
    for a, b in zip(metros[:-1], metros[1:]):
        i = metros.index(a)
        out.append(f'<rect x="{x + a * k}" y="{y}" width="{(b - a) * k}" height="1.1" '
                   f'fill="{color if i % 2 == 0 else PAPEL}" stroke="{color}" stroke-width="0.18"/>')
    for m in metros:
        out.append(texto(round(x + m * k, 3), y + 3.6, m, 2.1, color, ancla="middle"))
    out.append(texto(round(x + metros[-1] * k + 2.0, 3), y + 1.2, "m", 2.1, color))
    if etiqueta:
        out.append(texto(x, y - 1.4, etiqueta, 2.1, color))
    return "\n".join(out)
