#!/usr/bin/env python3
"""Arma el libro de Punto fermo y los entregables del concurso.

Uso (necesita Node, Python 3 con Pillow, NumPy, PyMuPDF y shapely, y Chromium):
    cd proyectos/porada-2026-mesa/05_consolidar/editorial && npm install     # una vez: Vivliostyle 11.3.3
    python3 armar.py                 # las láminas, el informe, la vista previa y el libro
    python3 armar.py --solo-libro    # solo el libro (usa las láminas ya armadas)
    python3 armar.py --sin-pdf       # solo los HTML en .cache/, para `npx vivliostyle preview`

Escribe:
    ../concurso/boards_CODICE.pdf, report_CODICE.pdf, preview_CODICE.jpg   (sin nombre, sin autor en los metadatos)
    punto_fermo_libro.pdf y muestras/*.jpg
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from libro import CACHE, FUENTES, LIBRO, Libro, esc, md  # noqa: E402

CONCURSO = AQUI.parent / "concurso"
TITULO = "Punto fermo: una mesa de caballetes con una piedra en la unión"


def chromium():
    for c in [os.environ.get("CHROMIUM"), "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"]:
        if c and Path(c).exists():
            return c
    return None


def vivliostyle(html_, pdf):
    viv = AQUI / "node_modules" / ".bin" / "vivliostyle"
    if not viv.exists():
        sys.exit("falta Vivliostyle: corre `npm install` en 05_consolidar/editorial/")
    cmd = [str(viv), "build", str(html_), "-o", str(pdf), "--timeout", "1200", "--log-level", "silent"]
    ch = chromium()
    if ch:
        cmd += ["--executable-browser", ch]
    subprocess.run(cmd, check=True, cwd=html_.parent, stdout=subprocess.DEVNULL)


def metadatos(pdf, titulo, asunto, palabras):
    """Sin autor: el concurso excluye cualquier nombre, también en las propiedades del PDF."""
    import pymupdf
    d = pymupdf.open(pdf)
    d.set_metadata({"title": titulo, "author": "", "subject": asunto, "keywords": palabras,
                    "creator": "05_consolidar/editorial/armar.py · Vivliostyle", "producer": "Vivliostyle + PyMuPDF"})
    tmp = Path(str(pdf) + ".tmp")
    d.save(tmp, garbage=3, deflate=True)
    d.close()
    tmp.replace(pdf)


def preparar_carpeta(destino):
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "fuentes").mkdir(exist_ok=True)
    for f in FUENTES.glob("*.woff2"):
        shutil.copy2(f, destino / "fuentes" / f.name)


def documento(partes, css, titulo, descripcion):
    return "\n".join(['<!doctype html>', '<html lang="es"><head><meta charset="utf-8">', f"<title>{esc(titulo)}</title>",
                      f'<meta name="description" content="{esc(descripcion)}">', f'<link rel="stylesheet" href="{css}">',
                      "</head><body>", *partes, "</body></html>"])


def indice_general(caps):
    h = []
    extra_ini = [("resumen", "resumen"), ("la doble página es el tablero", "tapa")]
    for t, i in extra_ini[:1]:
        h.append(f'<div class="ent menor"><span class="pag"><a class="pag" href="#{i}">%%P:{i}%%</a></span><span class="num"></span><span>{esc(t)}</span></div>')
    for c in caps:
        h.append(f'<div class="ent cap"><span class="pag"><a class="pag" href="#{c.id}">%%P:{c.id}%%</a></span><span class="num">{esc(c.num)}</span>'
                 f'<span>{esc(c.palabra)} <span class="gris" style="font-size:8pt">· {esc(c.corrida)}</span></span></div>')
        for num, t, sid in c.secciones:
            h.append(f'<div class="ent menor"><span class="pag"><a class="pag" href="#{sid}">%%P:{sid}%%</a></span><span class="num">{esc(num)}</span>'
                     f'<span>{md(t)}</span></div>')
    for t, i in (("referencias", "referencias"), ("las imágenes", "imagenes"), ("índice", "indice-final"), ("colofón", "colofon")):
        h.append(f'<div class="ent cap"><span class="pag"><a class="pag" href="#{i}">%%P:{i}%%</a></span><span class="num"></span><span>{esc(t)}</span></div>')
    return "".join(h)


def marcas(pdf):
    """En qué página cayó cada marca ¦id¦ (planas y destinos de las llamadas)."""
    import re
    import pymupdf
    d = pymupdf.open(pdf)
    pags = {}
    for i, pg in enumerate(d):
        texto = pg.get_text()
        for m in re.finditer(r"¦([^¦\s]+)¦", texto):
            pags.setdefault(m.group(1).replace("_", "-"), i + 1)
        for m in re.finditer(r"fig\. (\d+)", texto):          # las figuras, por su pie
            pags.setdefault(f"fig-{m.group(1)}", i + 1)
        for b in pg.get_text("dict")["blocks"]:                  # las secciones, por su número en el canal (82 mm)
            for l in b.get("lines", []):
                for sp in l["spans"]:
                    t = sp["text"].strip()
                    if re.fullmatch(r"\d\.\d+", t) and abs(sp["bbox"][0] / 72 * 25.4 - 82) < 1.5:
                        c, n = t.split(".")
                        pags.setdefault(f"s-{c}-{n}", i + 1)
    return pags


def borrar_marcas(pdf):
    """Borra solo las marcas exactas ¦id¦ (el texto del libro tiene § de verdad: Semper, §131)."""
    import re
    import pymupdf
    d = pymupdf.open(pdf)
    for pg in d:
        hits = pg.search_for("¦")
        for r in hits:                       # las marcas están solas (en el aire del margen o en la esquina)
            pg.add_redact_annot(pymupdf.Rect(r.x0 - 0.5, r.y0 - 0.5, r.x0 + 9, r.y1 + 0.5))
        if hits:
            try:
                pg.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)
            except (TypeError, AttributeError):
                pg.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
    tmp = Path(str(pdf) + ".tmp")
    d.save(tmp, garbage=3, deflate=True)
    d.close()
    tmp.replace(pdf)


def marcar_destinos(base):
    """Pone una marca ¦id¦ al principio de cada elemento al que apunta una llamada %%P:id%%."""
    import re
    ids = {i for i in re.findall(r"%%P:([^%]+)%%", base) if not i.startswith(("fig-", "s-"))}

    def poner(m):
        return m.group(0) + (f'<span class="marca-id">¦{m.group(2).replace("-", "_")}¦</span>' if m.group(2) in ids else "")
    return re.sub(r'(<(?:h2|figure|div|section|span)\b[^>]*\bid="([^"]+)"[^>]*>)', poner, base)


def armar_por_lados(base, html_, pdf, sin_pdf=False):
    """Arma y corrige los lados: cada plana «izq» en página par y cada «der» en impar, con páginas en blanco donde
    haga falta. Después escribe los números de página de las llamadas (sin target-counter: con referencias hacia
    adelante, Vivliostyle recompone y a veces pierde la página con nombre) y vuelve a armar."""
    import re
    base = marcar_destinos(base)
    orden = re.findall(r'data-pl="(pl\d+)" data-lado="(izq|der)"', base)
    blancas = set()

    def con_numeros(h, pags):
        return re.sub(r"%%P:([^%]+)%%", lambda m: f"{pags.get(m.group(1), 0):02d}", h)

    for vuelta in range(16):
        h = re.sub(r"%%B:(pl\d+)%%", lambda m: '<div class="plana blanca"></div>' if m.group(1) in blancas else "", base)
        html_.write_text(con_numeros(h, {}), encoding="utf8")
        if sin_pdf:
            return
        vivliostyle(html_, pdf)
        pags = marcas(pdf)
        malas = [pid for pid, lado in orden if pid in pags and ((pags[pid] % 2 == 0) != (lado == "izq"))]
        if not malas:
            print(f"lados: bien en la vuelta {vuelta + 1}, {len(blancas)} páginas en blanco")
            break
        blancas.add(malas[0])
    else:
        print("lados: no se pudo corregir todo:", malas)
    html_.write_text(con_numeros(h, pags), encoding="utf8")
    vivliostyle(html_, pdf)
    if marcas(pdf) != pags:
        print("aviso: los números de página movieron la composición")
    faltan = sorted(set(re.findall(r"%%P:([^%]+)%%", base)) - set(pags))
    if faltan:
        print("llamadas sin destino:", faltan)
    borrar_marcas(pdf)


def armar_libro(args, laminas=None, informe=None):
    import contenido
    lb = Libro()
    caps = contenido.componer(lb, laminas, informe)
    preparar_carpeta(LIBRO)
    shutil.copy2(AQUI / "estilo.css", LIBRO / "estilo.css")
    partes = [x.replace("%%INDICE%%", indice_general(caps)) for x in lb.partes]
    base = documento(partes, "estilo.css", TITULO, "El libro del proyecto Punto fermo para el Porada International Design Award 2026.")
    html_ = LIBRO / "libro.html"
    pdf = AQUI / "punto_fermo_libro.pdf"
    print("html:", html_, len(lb.figuras), "figuras")
    armar_por_lados(base, html_, pdf, args.sin_pdf)
    if args.sin_pdf:
        return None
    metadatos(pdf, TITULO, "Documento de trabajo: el proyecto, el método y los entregables para el Porada International Design Award 2026 (mesas, macizo)",
              "Porada, mesa de caballetes, nogal, mármol, tectónica, estereotomía, chhakhua")
    import pymupdf
    n = pymupdf.open(pdf).page_count
    print(f"libro: {pdf} · {n} páginas · {pdf.stat().st_size / 1e6:.1f} MB")
    muestras(pdf)
    return pdf


def muestras(pdf, dpi=80):
    """Algunas dobles páginas en JPG, para el README."""
    import pymupdf
    destino = AQUI / "muestras"
    shutil.rmtree(destino, ignore_errors=True)
    destino.mkdir()
    d = pymupdf.open(pdf)

    def imagen(i):
        pix = d[i].get_pixmap(dpi=dpi)
        return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    total = d.page_count
    # la tapa sola; después, dobles páginas que empiezan en par (índice 1 = página 2)
    pares = [(None, 0)] + [(i, i + 1) for i in range(1, total - 1, 2)]
    for k, (a, b) in enumerate(pares):
        ims = [imagen(i) if i is not None else None for i in (a, b)]
        w, h = next(im for im in ims if im is not None).size
        s = Image.new("RGB", (2 * w + 6, h), (58, 58, 56))
        for j, im in enumerate(ims):
            if im is not None:
                s.paste(im, (j * (w + 6), 0))
        s.save(destino / f"doble_{k:02d}.jpg", quality=82, optimize=True, progressive=True)
    print("muestras:", destino, len(pares))


def main():
    ap = argparse.ArgumentParser(description="Arma el libro de Punto fermo y los entregables del concurso.")
    ap.add_argument("--solo-libro", action="store_true")
    ap.add_argument("--sin-pdf", action="store_true")
    ap.add_argument("--codigo", default="CODICE", help="el código del participante, para los nombres de archivo")
    args = ap.parse_args()
    laminas, informe = None, None
    if not args.solo_libro:
        import concurso
        laminas, informe = concurso.armar(args)
    else:
        prev = sorted((CACHE / "concurso").glob("lamina_*.png"))
        laminas = prev or None
        t = CACHE / "concurso" / "informe.txt"
        if t.exists():
            txt = t.read_text(encoding="utf8")
            informe = (txt, len(txt))
    armar_libro(args, laminas, informe)


if __name__ == "__main__":
    main()
