"""Las piezas del libro de Punto fermo: la retícula, el texto con marcas, las figuras con su estado, las imágenes,
las planas (páginas compuestas), las aperturas de capítulo, las fichas de ensayo y los índices.
Lo usan contenido.py (el libro), concurso.py (láminas e informe) y armar.py.
"""
import html
import itertools
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

AQUI = Path(__file__).resolve().parent
PROYECTO = AQUI.parents[1]                       # proyectos/porada-2026-mesa
CACHE = AQUI / ".cache"
LIBRO = CACHE / "libro"
IMG = LIBRO / "img"
FUENTES = AQUI / "fuentes"
sys.path.insert(0, str(PROYECTO / "instrumentos"))

# ------------------------------------------------------------------ la retícula (mm): la doble es el tablero a 1:5
PAG_W, PAG_H = 240.0, 200.0
TABLA, JUNTA = (1000 - 15) / 6 / 5, 3 / 5        # una tabla (164,17 mm) y su junta (3 mm), a 1:5
PASO = TABLA + JUNTA                             # 33,433
LINEA = PASO / 8                                 # 4,179
AIRE, MARGEN, CABEZAL, TEXTO = 18.0, (18.0, 82.0), (82.0, 98.0), (98.0, 222.0)
PAPEL = (244, 242, 236)


def fila(k):
    """Arriba de la fila k (1 a 6)."""
    return (k - 1) * PASO


def filas(n):
    """Alto de n filas seguidas (con las juntas de adentro)."""
    return n * PASO - JUNTA


def en(x, y, w=None, h=None, extra=""):
    s = [f"left:{x:.3f}mm", f"top:{y:.3f}mm"]
    if w is not None:
        s.append(f"width:{w:.3f}mm")
    if h is not None:
        s.append(f"height:{h:.3f}mm")
    return ";".join(s) + (";" + extra if extra else "")


# ------------------------------------------------------------------ texto con marcas
MARCAS = re.compile(r"(\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[\[[^\]]+\]\])")
ETIQUETAS = re.compile(r"(</?(?:br|span|b|i|em|strong)\b[^>]*>)")


def esc(t):
    return html.escape(str(t), quote=False)


def md(t):
    """*cursiva*, **negrita**, ***las dos***, `mono` y [[id|texto]] (llamada a otra página).
    Deja pasar <br>, <span>, <b> e <i> tal cual."""
    t = str(t)
    if "<" in t:
        return "".join(x if ETIQUETAS.fullmatch(x) else md(x) for x in ETIQUETAS.split(t) if x)
    out = []
    for p in MARCAS.split(t):
        if not p:
            continue
        if p.startswith("***"):
            out.append(f"<strong><em>{md(p[3:-3])}</em></strong>")
        elif p.startswith("**"):
            out.append(f"<strong>{md(p[2:-2])}</strong>")
        elif p.startswith("*"):
            out.append(f"<em>{md(p[1:-1])}</em>")
        elif p.startswith("`"):
            out.append(f'<code>{esc(p[1:-1])}</code>')
        elif p.startswith("[["):
            ref, _, txt = p[2:-2].partition("|")
            out.append(f'<a class="ref" href="#{ref}">{md(txt) if txt else ""}<span class="flecha"> → %%P:{ref}%%</span></a>')
        else:
            out.append(esc(p))
    return "".join(out)


def plano(t):
    return re.sub(r"[*`]|\[\[[^|\]]*\|?|\]\]", "", str(t))


# ------------------------------------------------------------------ figuras y su estado
ESTADOS = {
    "instrumento": ("instrumento", ""),             # dibujada por el código, desde los cálculos
    "simulacion": ("simulación", "simulacion"),     # render de Blender: no es una foto
    "dominio": ("dominio público", ""),
    "pendiente": ("pendiente", "pendiente"),        # un lugar que espera la maqueta, la foto o el permiso
}


class Libro:
    def __init__(self, imprenta=False):
        self.imprenta = imprenta
        self.partes = []
        self.figuras = []
        self.indice = []                 # (nivel, id, texto)
        self.terminos = {}               # término → ids donde aparece (índice final)
        self._ids = itertools.count(1)
        import shutil
        shutil.rmtree(IMG, ignore_errors=True)
        IMG.mkdir(parents=True, exist_ok=True)

    def add(self, *h):
        self.partes.extend(h)

    def nuevo_id(self, base="a"):
        return f"{base}{next(self._ids)}"

    # --- figuras
    def figura(self, que, origen, estado):
        n = len(self.figuras) + 1
        fid = f"fig-{n}"
        self.figuras.append(dict(n=n, id=fid, que=que, origen=origen, estado=estado))
        return n, fid

    def etiqueta(self, estado):
        nombre, clase = ESTADOS[estado]
        return f'<span class="etiqueta {clase}">{nombre}</span>'

    def pie(self, n, estado, t):
        return f'<span class="fn">fig. {n}</span>{self.etiqueta(estado)}{md(t)}'

    def termino(self, clave, fid):
        self.terminos.setdefault(clave, []).append(fid)

    # --- imágenes
    def imagen(self, origen, ancho_mm, alto_mm=None, gris=False, igualar=False, recorte=None, ppp=260,
               calidad=86, nombre=None):
        """Copia una imagen del proyecto a la caché, a su tamaño de página (ppp), y devuelve su ruta relativa."""
        origen = Path(origen)
        im = Image.open(origen)
        im = ImageOps.exif_transpose(im).convert("RGB")
        if recorte:
            w, h = im.size
            im = im.crop((int(recorte[0] * w), int(recorte[1] * h), int(recorte[2] * w), int(recorte[3] * h)))
        if alto_mm:                          # recorte al formato del lugar (cover)
            r = ancho_mm / alto_mm
            w, h = im.size
            if w / h > r:
                nw = int(h * r)
                im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
            else:
                nh = int(w / r)
                im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
        px = int(ancho_mm / 25.4 * ppp)
        if im.size[0] > px:
            im = im.resize((px, int(im.size[1] * px / im.size[0])), Image.LANCZOS)
        if gris:
            im = ImageOps.grayscale(im).convert("RGB")
        if igualar:
            im = igualar_papel(im, PAPEL)
        nombre = nombre or f"{origen.stem}_{int(ancho_mm)}{'g' if gris else ''}.jpg"
        destino = IMG / nombre
        im.save(destino, quality=calidad, optimize=True, progressive=True)
        return f"img/{nombre}"


def igualar_papel(im, papel):
    """Lleva el papel de un escaneo al del libro: divide por el fondo (la mediana del borde) y multiplica por el papel."""
    a = np.asarray(im).astype(np.float32)
    borde = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
    f = np.percentile(borde, 70, axis=0)
    if f.min() < 120:
        return im
    a = a * (np.array(papel, np.float32) / np.maximum(f, 1))
    return Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------ bloques de texto corrido

def p(t, clase=""):
    c = f' class="{clase}"' if clase else ""
    return f"<p{c}>{md(t)}</p>"


def ps(*ts):
    return "".join(p(t) for t in ts)


def lista(items, numerada=False, clase=""):
    tag = "ol" if numerada else "ul"
    c = f' class="{clase}"' if clase else ""
    return f"<{tag}{c}>" + "".join(f"<li>{md(i)}</li>" for i in items) + f"</{tag}>"


def margen(t, clase=""):
    return f'<span class="margen {clase}">{md(t)}</span>'


def cita(original, de=""):
    d = f'<span class="de">{md(de)}</span>' if de else ""
    return f'<div class="cita">{md(original)}{d}</div>'


def regla(t):
    return f'<p class="regla">{md(t)}</p>'


def prerregistro(t, titulo="prerregistro"):
    return f'<div class="prerregistro"><div class="titulo">{titulo}</div>{t if t.startswith("<") else p(t)}</div>'


def tabla(cab, filas_, ancha=False, cols=None, total=None):
    """cols: clases por columna ('mono', 'd' para números a la derecha)."""
    cols = cols or [""] * len(cab)
    h = [f'<table class="tabla{" ancha" if ancha else ""}"><thead><tr>']
    h += [f"<th>{esc(c)}</th>" for c in cab]
    h.append("</tr></thead><tbody>")
    for f in filas_:
        clase_fila = ""
        if isinstance(f, dict):
            clase_fila, f = f.get("clase", ""), f["celdas"]
        h.append(f'<tr class="{clase_fila}">' + "".join(
            f'<td class="{cols[i]}">{md(c)}</td>' for i, c in enumerate(f)) + "</tr>")
    if total:
        h.append('<tr class="total">' + "".join(f'<td class="{cols[i]}">{md(c)}</td>' for i, c in enumerate(total)) + "</tr>")
    h.append("</tbody></table>")
    return "".join(h)


def fig(lb, contenido, que, origen, estado, pie, clase="en-texto", fid=None, terminos=()):
    n, f_id = lb.figura(que, origen, estado)
    for t in terminos:
        lb.termino(t, f_id)
    clase_estado = " simulacion" if estado == "simulacion" else ""
    return (f'<figure class="{clase}{clase_estado}" id="{fid or f_id}"><div class="marco">{contenido}</div>'
            f'<figcaption>{lb.pie(n, estado, pie)}</figcaption></figure>')


def img(src, ancho_mm=None, alto_mm=None):
    st = []
    if ancho_mm:
        st.append(f"width:{ancho_mm}mm")
    if alto_mm:
        st.append(f"height:{alto_mm}mm")
    return f'<img src="{src}" style="{";".join(st)}" alt="">'


def svg_a(svg, ancho_mm=None, alto_mm=None):
    """Cambia el tamaño de un SVG (conserva el viewBox). Con None, queda a su escala."""
    m = re.search(r'viewBox="([\d.\- ]+)"', svg)
    x0, y0, w, h = map(float, m.group(1).split())
    if ancho_mm and not alto_mm:
        alto_mm = ancho_mm * h / w
    elif alto_mm and not ancho_mm:
        ancho_mm = alto_mm * w / h
    if ancho_mm:
        svg = re.sub(r'width="[\d.]+mm" height="[\d.]+mm"', f'width="{ancho_mm:.3f}mm" height="{alto_mm:.3f}mm"', svg, count=1)
    return svg


def tam_svg(svg):
    m = re.search(r'width="([\d.]+)mm" height="([\d.]+)mm"', svg)
    return float(m.group(1)), float(m.group(2))


def vacio(texto, ancho_mm, alto_mm):
    return f'<div class="vacio" style="width:{ancho_mm}mm;height:{alto_mm}mm">{md(texto)}</div>'


# ------------------------------------------------------------------ capítulos y secciones

class Capitulo:
    def __init__(self, lb, num, palabra, corrida):
        self.lb, self.num, self.palabra, self.corrida = lb, num, palabra, corrida
        self.secciones = []
        self.html = []
        self.id = f"cap-{num}"

    def sec(self, n, titulo, corrida=None):
        sid = f"s-{self.num}-{n}".replace(".", "-")
        self.secciones.append((f"{self.num}.{n}", titulo, sid))
        c = esc(corrida or f"{self.num}.{n} · {plano(titulo).lower()}")
        self.html.append(f'<h2 id="{sid}" data-corrida="{c}"><span class="n">{self.num}.{n}</span>{md(titulo)}</h2>')

    def add(self, *h):
        """Las notas al margen van primero: flotan junto al primer párrafo del grupo, nunca al final de un capítulo."""
        notas = [x for x in h if x.startswith('<span class="margen')]
        self.html.extend(notas + [x for x in h if not x.startswith('<span class="margen')])

    def cerrar(self):
        return (f'<section class="capitulo texto" id="{self.id}-texto" data-corrida="{esc(self.num)} · {esc(self.corrida)}">'
                + "".join(self.html) + '<div style="clear:both;height:0"></div></section>')


# ------------------------------------------------------------------ planas

_PL = itertools.count(1)


def plana(contenido, lado=None, clase="", rotulo=None, pid=None):
    """Una página compuesta a sangre. lado: "izq" (par) o "der" (impar). El lado no lo fuerza el CSS: armar.py
    lee en qué página cayó cada plana (por su marca ¦plN¦, que después se borra) e inserta páginas en blanco donde haga falta."""
    l = {"izq": " izquierda", "der": " derecha"}.get(lado, "")
    r = ""
    if rotulo:
        x = 6.5 if lado != "der" else PAG_W - 9.5
        r = f'<div class="vertical" style="{en(x, fila(2), None, None)}">{esc(rotulo)}</div>'
    marca = f"pl{next(_PL)}"
    i = f' id="{pid}"' if pid else ""
    antes = f"%%B:{marca}%%" if lado else ""
    return (f'{antes}<div class="plana{l} {clase}"{i} data-pl="{marca}" data-lado="{lado or ""}">'
            f'<span class="marca-pl">¦{marca}¦</span>{contenido}{r}</div>')


def juntas(desde=1, hasta=6, ancho=PAG_W, x=0.0, color=None):
    c = f";background:{color}" if color else ""
    return "".join(f'<div class="junta" style="left:{x}mm;width:{ancho}mm;top:{fila(k) - JUNTA:.3f}mm{c}"></div>'
                   for k in range(max(2, desde), hasta + 1))


def palabra_cortada(palabra, x, base, tam=72.0, punto=True):
    """La palabra gigante, con el punto de piedra; su línea de base en `base` (mm desde arriba de la página)."""
    pt = '<span class="punto"></span>' if punto else ""
    alto_linea = tam
    top = base - tam * 0.80                        # Newsreader: la línea de base cae a ~0,80 del cuerpo
    return (f'<div class="gigante" style="left:{x:.2f}mm;top:{top:.2f}mm;font-size:{tam}mm;line-height:{alto_linea}mm">'
            f'{esc(palabra)}{pt}</div>')


def apertura(lb, cap, epigrafe=None, lead=None):
    """Doble página de apertura: el número y el índice del capítulo a la izquierda; la palabra cruza el lomo."""
    base = fila(5) + 0.62 * TABLA                  # la x-altura queda entre dos tablas: la junta la corta
    pal = palabra_cortada(cap.palabra, AIRE - 1.5, base)
    indice = "".join(f'<a href="#{sid}"><span class="pg">%%P:{sid}%%</span>{esc(num)}  {md(t)}</a>' for num, t, sid in cap.secciones)
    izq = (f'<div class="rotulo" style="{en(AIRE, 12.5, 120)}">capítulo {esc(cap.num)} · {esc(cap.corrida)}</div>'
           f'<div class="numero" style="{en(AIRE - 1, fila(2) - 3, 60)}">{esc(cap.num)}</div>'
           f'<div class="indice-cap" style="{en(TEXTO[0], fila(2), 110)}">{indice}</div>'
           + pal + juntas())
    der_pal = palabra_cortada(cap.palabra, AIRE - 1.5 - PAG_W, base)
    epi = ""
    if epigrafe:
        orig, trad, de = epigrafe
        epi = (f'<div class="epigrafe" style="{en(PAG_W - AIRE - 110, fila(6) + 2, 110)}">{md(orig)}'
               f'<span class="trad">{md(trad)}</span><span class="de">{md(de)}</span></div>')
    ld = f'<div class="lead" style="{en(TEXTO[0] - PAG_W + PAG_W, fila(1) + 6, 124)}">{md(lead)}</div>' if lead else ""
    der = der_pal + juntas() + epi + ld
    lb.indice.append(cap)
    return plana(izq, "izq", pid=cap.id) + plana(der, "der")


# ------------------------------------------------------------------ fichas de ensayo

def ensayo(codigo, nombre, pregunta, campos, veredicto=None, ref=None, eid=None):
    """campos: (rótulo, texto[, almagre]). veredicto: (texto, cumple)."""
    v = ""
    if veredicto:
        txt, ok = veredicto
        v = f'<span class="veredicto{"" if ok else " no"}">{esc(txt)}</span>'
    dl = "".join(f'<dt class="{"almagre" if len(c) > 2 and c[2] else ""}">{esc(c[0])}</dt><dd>{md(c[1])}</dd>' for c in campos)
    i = f' id="{eid}"' if eid else ""
    return (f'<div class="ensayo"{i}><div class="cab"><span>{esc(codigo)} · {esc(nombre)}</span>'
            f'<span class="codigo">{v}{esc(ref or "")}</span></div>'
            f'<div class="pregunta">{md(pregunta)}</div><dl>{dl}</dl></div>')
