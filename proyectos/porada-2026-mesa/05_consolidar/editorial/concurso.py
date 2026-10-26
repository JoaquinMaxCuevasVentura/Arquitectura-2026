"""Los entregables del concurso: las tres láminas A3, el informe A4 y la vista previa. En inglés y sin nombre.

Bando, art. 4: informe A4 vertical de ≤ 3000 caracteres, sin imágenes, con solo el código y el título en la cabecera;
3 láminas A3 horizontales en un PDF de ≤ 5 MB (1: panorama, escenarios, concepto, fuentes; 2: planos, secciones,
axonometrías, despieces, detalles; 3: renders y fotos de maqueta); vista previa JPG de ≤ 1 MB.
"""
import re
import shutil
from pathlib import Path

from PIL import Image

import armar as ar
from libro import CACHE, PROYECTO, Libro, esc, md, svg_a, tam_svg
from mesa import laminas_f1 as lf, versiones
from mesa.despiece import despiece

REN = PROYECTO / "05_consolidar" / "renders"
CAP = PROYECTO / "01_reunir" / "capturas"
DEST = PROYECTO / "05_consolidar" / "concurso"
DIR = CACHE / "concurso"

TITULO = "Punto fermo"
BAJADA = "A trestle table in solid walnut, with one stone in the joint"
REGLA = "Wood moves and comes apart; the only fixed point is the stone where it locks."

INFORME = [
    "**Punto fermo** is a dining table for eight in solid noce canaletta, built as the oldest form of the type: boards resting on trestles. Medieval tables were not fixed: they were set up and taken away (Viollet-le-Duc, 1873). Modern furniture fixes the top and then fights its movement with hardware. Punto fermo goes back to the unfixed top, with workshop precision.",
    "**Concept.** Solid wood moves: a metre of walnut changes about 14 mm in width between seasons, while stone does not move at all. The table is built on that difference: wood moves and comes apart; the only fixed point is the stone where it locks. Six loose boards (2400 × 164 × 40 mm) are each pinned on their axis by an ash dowel and locked by an ash wedge driven through the trestle head, so every board moves on its own and the joint between boards shows the season: 0.8 mm when the air is humid, 4.8 mm when it is dry. Loose ash splines under each joint keep the boards level and close the gap below.",
    "**The fixed point.** The stretcher's through-tenon passes through the trestle post and through a collar of Nero Sahara Noir marble; a tapered ash key, set with a mallet, presses the stone against the post. The stone works only in compression (0.08 MPa), never glued and never in bending, with 1 mm of clearance per side. It is not a luxury placed next to the wood but the place where the wood is held. Bertonio's Aymara dictionary (1612) has a word for it, *chhakhua*: the stone driven into the wall to tie the roof poles to it, and also the poles tied to it: the whole joint.",
    "**Making and use.** 48 parts, no metal hardware, one mallet. No part weighs more than 16 kg (a glued trestle): the table travels flat and is assembled in seven steps. A damaged board is replaced without dismantling the table: two wedges out, the spline slides out through the end, the board lifts away. Beyond the key, the end grain of the tenon stays visible and shows its rings.",
    "**Materials and finishes.** Noce canaletta for boards, trestles and stretcher; frassino for dowels, wedges, splines and keys; Nero Sahara Noir, honed, with 3 mm chamfers: three materials of the Porada collection, each doing the job it does best. Walnut and ash are oiled, so the surface remains something to touch.",
    "**Method.** Each claim was checked against a source or a calculation whose threshold was written down before computing. The stone cannot be a beam (9.9 MPa against 2.3 allowed); its weight neither steadies nor locks the frame; every joint was checked part by part for clashes.",
]


def caracteres(textos):
    """Los caracteres del informe, con espacios, sin las marcas de negrita y cursiva; más el título y la bajada."""
    plano = "\n".join(re.sub(r"[*`]", "", t) for t in textos)
    return len(plano) + len(TITULO) + len(BAJADA) + 2, plano


# ------------------------------------------------------------------ retícula A3 (mm)
def X(c):
    return 12 + (c - 1) * 33.3333


def W(n):
    return n * 33.3333 - 4


FILA = 45.6


def Y(k):
    return 12 + (k - 1) * FILA


def H(n):
    return n * FILA - 0.6


def en(x, y, w=None, h=None, extra=""):
    s = [f"left:{x:.2f}mm", f"top:{y:.2f}mm"]
    if w is not None:
        s.append(f"width:{w:.2f}mm")
    if h is not None:
        s.append(f"height:{h:.2f}mm")
    return ";".join(s) + (";" + extra if extra else "")


def juntas():
    return "".join(f'<div class="junta" style="top:{Y(k) - 0.6:.2f}mm"></div>' for k in range(2, 7))


def franja(n, que, codigo):
    return (f'<div class="franja" style="{en(12, 4.5, 396)}"><span><b>{TITULO}</b> · {n}/3 · {esc(que)}</span>'
            f'<span>porada international design award 2026 · tables · {esc(codigo)}</span></div>')


def foto(lb, arch, w, h, gris=False, ppp=220, contener=False):
    src = lb.imagen(arch, w, None if contener else h, gris=gris, igualar=gris, ppp=ppp)
    return f'<img src="{src}" alt="">'


def lamina(contenido):
    return f'<div class="lamina">{contenido}</div>'


# ------------------------------------------------------------------ lámina 1: concept, scenarios, sources
def lamina_1(lb, codigo, planos):
    c = franja(1, "concept · use scenarios · sources", codigo)
    # el título, cortado por una junta; el punto de piedra, entero
    c += f'<div class="titulo" style="{en(X(1) - 1.2, Y(1) + 2, None, None, "font-size:23mm")}">{TITULO.lower()}<span class="punto"></span></div>'
    c += f'<div class="junta" style="left:{X(1)}mm;width:{W(4) + 2}mm;top:{Y(1) + 17.4:.2f}mm;z-index:3"></div>'
    c += f'<div class="sub" style="{en(X(1), Y(1) + 27, W(4))}">{esc(BAJADA.lower())}</div>'
    c += (f'<div class="regla" style="{en(X(1), Y(2) - 4, W(4))}">{esc(REGLA)}</div>'
          f'<div class="cuerpo" style="{en(X(1), Y(2) + 20, W(4))}">'
          + "".join(f"<p>{md(t)}</p>" for t in [
              "Solid wood moves about 14 mm per metre between seasons; stone does not move. Six loose walnut boards are each pinned on their axis and locked by an ash wedge: the joint between them shows the season.",
              "The only fixed point is a collar of **Nero Sahara Noir**. The stretcher's through-tenon passes through the post and through the stone; an ash key, set with a mallet, presses the stone against the post. The stone works only in compression, never glued, never in bending.",
          ]) + "</div>")
    # el nodo, en sección horizontal: la idea en un dibujo
    sn = svg_a(lf.nodo_planta(5, marcas=False).svg(1.0), 70)
    wn, hn = tam_svg(sn)
    c += (f'<div style="{en(X(1), Y(4) - 8, wn, hn)}">{sn}</div>'
          f'<div class="pie" style="{en(X(1) + wn + 4, Y(4) - 6, W(4) - wn - 4)}"><b>the joint</b>, horizontal section 1:5: '
          f'post (end grain), tenon, stone collar (black), ash key. 1 mm clearance per side; the stone is only squeezed</div>')
    # el render principal
    c += f'<div style="{en(X(5), Y(1), W(8), H(4))}">{foto(lb, REN / "general_F1.png", W(8), H(4))}</div>'
    c += f'<div class="pie etq" style="{en(X(5) + 3, Y(4) + H(1) - 6, W(6))}">noce canaletta, frassino, nero sahara noir · 2400 × 1000 × 750 mm · 8 people</div>'
    # los cuatro escenarios
    esc_ = [("1", "at the table", "eight people; the ends stay free for the knees: the trestles stand 450 mm from the ends"),
            ("2", "assembly", "seven steps, one mallet, no hardware; no part weighs more than 16 kg"),
            ("3", "seasons", "the joint between boards: 0.8 mm humid, 3 mm as made, 4.8 mm dry. the stone does not move"),
            ("4", "repair", "two wedges out, the spline slides out through the end, one board lifts away")]
    y0 = Y(5)
    hi = 64
    for i, (n, t, d) in enumerate(esc_):
        x = X(1 + 2 * i)
        c += f'<div class="rot" style="{en(x, y0 + 1, W(2))}"><span class="n">{n}</span>{esc(t)}</div>'
        c += f'<div class="pie" style="{en(x, y0 + 7 + hi + 2.5, W(2))}">{esc(d)}</div>'
    c += f'<div style="{en(X(1), y0 + 7, W(2), hi)}">{foto(lb, REN / "frente_F1.png", W(2), hi)}</div>'
    pasos = "".join(f'<div style="display:inline-block;width:{W(2) / 4 - 0.6:.2f}mm;margin:0 0.6mm 1.5mm 0;vertical-align:top">'
                    f'{svg_a(planos[f"montaje_{k}"][0].svg(0.8), W(2) / 4 - 0.6)}</div>' for k in range(1, 8))
    c += f'<div style="{en(X(3), y0 + 9, W(2), hi)}">{pasos}</div>'
    for j, (arch, lab) in enumerate((("junta_0p75.png", "0.8"), ("junta_3p00.png", "3.0"), ("junta_4p80.png", "4.8"))):
        c += f'<div style="{en(X(5), y0 + 7 + j * 21.6, W(2), 20.8)}">{foto(lb, REN / arch, W(2), 20.8)}</div>'
        c += f'<div class="pie etq" style="{en(X(5) + 2, y0 + 7 + j * 21.6 + 15.5, 30)}">{lab} mm</div>'
    c += f'<div style="{en(X(7), y0 + 7, W(2), hi)}">{foto(lb, REN / "cabezal_F1.png", W(2), hi)}</div>'
    # las fuentes: dominio público
    fuentes = [("recorte_bertonio_p069_chakhua_chhakhua.jpg", "Bertonio 1612: chhakhua, the stone where the poles are tied"),
               ("semper_1879_derstil-II_p201.jpg", "Semper 1879: the table as Gestell"),
               ("violletleduc_1873_mobilier-I_p257.jpg", "Viollet-le-Duc 1873: tables on trestles, «pas à demeure»"),
               ("squier_1877_p280.jpg", "Squier 1877: Tiwanaku stones cut «like mortise and tenon»")]
    c += f'<div class="rot" style="{en(X(9), y0 + 1, W(4))}"><span class="n">→</span>sources</div>'
    for i, (arch, pie) in enumerate(fuentes):
        w = (W(4) + 4) / 4 - 4
        x = X(9) + i * (w + 4)
        c += f'<div class="contener" style="{en(x, y0 + 7, w, hi)}">{foto(lb, CAP / arch, w, hi, gris=True, ppp=300, contener=True)}</div>'
        c += f'<div class="pie" style="{en(x, y0 + 7 + hi + 2.5, w)}">{esc(pie)}</div>'
    return lamina(c)


# ------------------------------------------------------------------ lámina 2: drawings
def lamina_2(lb, codigo, planos):
    c = franja(2, "drawings · sections · details · exploded axonometry · parts", codigo)

    def dib(d, x, y, titulo, escala, margen=1.5, ancho=None):
        s = d.svg(margen)
        if ancho:
            s = svg_a(s, ancho)
        w, h = tam_svg(s)
        return (f'<div style="{en(x, y, w, h)}">{s}</div>'
                f'<div class="rot" style="{en(x, y - 4.2, 150)}">{esc(titulo)} <span class="escala">{esc(escala)}</span></div>')

    c += dib(lf.alzado(15), 12, 20, "elevation", "1:15")
    c += dib(lf.lateral(15), 206, 20, "end elevation", "1:15")
    c += dib(lf.seccion_a(15), 300, 20, "section A-A, through the trestle", "1:15")
    c += dib(lf.planta(15), 12, 101, "plan", "1:15")
    c += dib(lf.nodo_alzado(5), 210, 101, "the joint, elevation", "1:5")
    c += dib(lf.nodo_planta(5), 300, 101, "the joint, horizontal section", "1:5")
    c += dib(lf.detalle_tablas(5), 210, 172, "boards on the head: dowel, wedge, spline", "1:5")
    c += dib(lf.axon(25, despiece=True), 12, 207, "exploded axonometry", "1:25", margen=1.0)
    # lista de piezas
    m = versiones.f1()
    marca = {v: k for k, v in lf.PIEZAS.items()}
    nombres = {"tabla": "board", "lengüeta": "spline", "clavija": "dowel", "cuña": "wedge", "pie": "foot", "montante": "post",
               "cabezal": "head", "cabezal central": "central head", "travesaño": "stretcher", "puntal": "central strut",
               "collar": "collar", "llave": "key"}
    mats = {"nogal canaleta": "noce canaletta", "fresno": "frassino", "mármol": "Nero Sahara Noir"}
    filas = ""
    for f_ in despiece(m):
        mat = next(v for k, v in mats.items() if f_["material"].startswith(k))
        dims = " × ".join(f"{d_:g}" for d_ in f_["medidas_mm"])
        filas += (f'<tr><td>{marca.get(f_["pieza"], "")}</td><td>{nombres.get(f_["pieza"], f_["pieza"])}</td><td>{mat}</td>'
                  f'<td>{dims}</td><td class="d">{f_["cantidad"]}</td><td class="d">{f_["masa_total_kg"]:.1f}</td></tr>')
    filas += f'<tr class="total"><td></td><td>total</td><td></td><td></td><td class="d">{len(m.piezas)}</td><td class="d">{m.masa():.1f}</td></tr>'
    c += (f'<div class="rot" style="{en(124, 207 - 4.2, 120)}">parts</div>'
          f'<div style="{en(124, 207, 140)}"><table class="tabla-piezas"><thead><tr><th>no.</th><th>part</th>'
          f'<th>material</th><th>mm</th><th>qty</th><th>kg</th></tr></thead><tbody>{filas}</tbody></table></div>')
    # secuencia de montaje
    c += f'<div class="rot" style="{en(274, 214 - 4.2, 130)}">assembly, in seven steps</div>'
    for k in range(1, 8):
        col, fil = (k - 1) % 4, (k - 1) // 4
        s = svg_a(planos[f"montaje_{k}"][0].svg(0.8), 31)
        c += (f'<div style="{en(274 + col * 33.5, 214 + fil * 34, 31)}">{s}'
              f'<div class="pie" style="margin-top:0.6mm"><b>{k}</b> {esc(PASOS_EN[k])}</div></div>')
    c += (f'<div class="pie" style="{en(124, 268, 140)}">tolerances: 1 mm per side in the stone, 0.5 mm in loose joints · '
          f'the trestle is glued (through-tenons, wedged); everything else comes apart · walnut and ash oiled · '
          f'stone honed, 3 mm chamfers · ash key tapered 1:40 · numbers in circles: parts list</div>')
    return lamina(c)


PASOS_EN = {1: "stand the trestles", 2: "the stretcher through the posts", 3: "the stone collars onto the tenons",
            4: "the keys press the stone: one mallet blow", 5: "the central strut astride the stretcher",
            6: "the boards with their dowels; splines between them", 7: "the wedges through the heads lock each board"}


# ------------------------------------------------------------------ lámina 3: renders
def lamina_3(lb, codigo):
    c = franja(3, "renders", codigo)
    c += f'<div style="{en(X(1), Y(1), W(6), H(4))}">{foto(lb, REN / "nodo_F1.png", W(6), H(4))}</div>'
    c += f'<div class="pie etq" style="{en(X(1) + 3, Y(4) + H(1) - 7, W(5))}">the fixed point: the tenon passes through the stone; the ash key presses it against the post</div>'
    c += f'<div style="{en(X(7), Y(1), W(6), H(2))}">{foto(lb, REN / "testa_F1.png", W(6), H(2))}</div>'
    c += f'<div class="pie etq" style="{en(X(7) + 3, Y(2) + H(1) - 7, W(5))}">beyond the key, the end of the tenon stays in view: end grain, oiled</div>'
    c += f'<div style="{en(X(7), Y(3), W(6), H(2))}">{foto(lb, REN / "cabezal_F1.png", W(6), H(2))}</div>'
    c += f'<div class="pie etq" style="{en(X(7) + 3, Y(4) + H(1) - 7, W(5))}">twelve ash wedges through the heads: each board is locked on its own</div>'
    c += f'<div style="{en(X(1), Y(5), W(8), H(2))}">{foto(lb, REN / "frente_F1.png", W(8), H(2))}</div>'
    c += f'<div style="{en(X(9), Y(5), W(4), H(2))}">{foto(lb, REN / "planta_F1.png", W(4), H(2))}</div>'
    c += f'<div class="pie" style="{en(X(9) + 3, Y(6) + H(1) - 7, W(4))}">from above: six boards, five joints</div>'
    return lamina(c)


# ------------------------------------------------------------------ el informe
def informe_html(codigo):
    cab = f'<div class="cabecera"><span>{esc(codigo)}</span><span>{TITULO}</span></div>'
    return (f'<div class="informe">{cab}<h1>{TITULO}</h1><div class="bajada">{esc(BAJADA)}</div>'
            + "".join(f"<p>{md(t)}</p>" for t in INFORME) + "</div>")


def armar(args):
    codigo = getattr(args, "codigo", "CODICE")
    shutil.rmtree(DIR, ignore_errors=True)
    ar.preparar_carpeta(DIR)
    shutil.copy2(ar.AQUI / "concurso.css", DIR / "concurso.css")
    lb = Libro()
    import libro
    libro.IMG = DIR / "img"                         # las imágenes de las láminas van a su propia carpeta
    (DIR / "img").mkdir(exist_ok=True)
    planos = lf.juego()
    DEST.mkdir(parents=True, exist_ok=True)

    # las láminas
    html_l = DIR / "laminas.html"
    html_l.write_text(ar.documento([lamina_1(lb, codigo, planos), lamina_2(lb, codigo, planos), lamina_3(lb, codigo)],
                                      "concurso.css", f"{TITULO} · boards", BAJADA), encoding="utf8")
    boards = DEST / f"boards_{codigo}.pdf"
    ar.vivliostyle(html_l, boards)
    ar.metadatos(boards, TITULO, BAJADA, "Porada International Design Award 2026, tables")
    import pymupdf
    d = pymupdf.open(boards)
    assert d.page_count == 3, d.page_count
    mb = boards.stat().st_size / 1e6
    print(f"láminas: {boards} · {d.page_count} A3 · {mb:.2f} MB {'✓' if mb <= 5 else '✗ más de 5 MB'}")
    laminas_png = []
    for i, pg in enumerate(d, 1):
        pix = pg.get_pixmap(dpi=110)
        ruta = DIR / f"lamina_{i}.png"
        pix.save(ruta)
        laminas_png.append(ruta)

    # el informe
    n, plano = caracteres(INFORME)
    assert n <= 3000, f"el informe tiene {n} caracteres (máx. 3000)"
    html_i = DIR / "informe.html"
    html_i.write_text(ar.documento([informe_html(codigo)], "concurso.css", f"{TITULO} · report", BAJADA), encoding="utf8")
    report = DEST / f"report_{codigo}.pdf"
    ar.vivliostyle(html_i, report)
    ar.metadatos(report, TITULO, BAJADA, "Porada International Design Award 2026, tables")
    paginas = pymupdf.open(report).page_count
    assert paginas == 1, f"el informe ocupa {paginas} páginas"
    (DIR / "informe.txt").write_text(TITULO + "\n" + BAJADA + "\n\n" + plano, encoding="utf8")
    print(f"informe: {report} · {n} caracteres con espacios ✓ · 1 página A4")

    # la vista previa: la lámina 1 no; la imagen síntesis es el render general, sin metadatos
    prev = DEST / f"preview_{codigo}.jpg"
    im = Image.open(REN / "general_F1.png").convert("RGB")
    im.thumbnail((2000, 2000))
    calidad = 88
    while True:
        im.save(prev, quality=calidad, optimize=True, progressive=True)    # PIL no copia EXIF si no se le pasa
        if prev.stat().st_size <= 1_000_000 or calidad < 50:
            break
        calidad -= 6
    print(f"vista previa: {prev} · {prev.stat().st_size / 1e6:.2f} MB")
    libro.IMG = CACHE / "libro" / "img"
    return laminas_png, (TITULO + "\n" + BAJADA + "\n\n" + plano, n)
