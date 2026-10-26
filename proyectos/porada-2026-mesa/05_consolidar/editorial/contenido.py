"""El contenido del libro de Punto fermo: texto, figuras y planas, en el orden del método.

Los datos salen del proyecto (el instrumento, los resultados de los ensayos, el modelo constructivo y los renders);
el texto condensa los documentos del repositorio, que siguen siendo la referencia: si algo difiere, manda el repositorio.
"""
from libro import (AIRE, CABEZAL, JUNTA, LINEA, MARGEN, PAG_H, PAG_W, PASO, PROYECTO, TABLA, TEXTO, Capitulo,
                   apertura, cita, en, ensayo, esc, fig, fila, filas, img, juntas, lista, margen, md, p,
                   palabra_cortada, plana, plano, prerregistro, ps, regla, svg_a, tabla, tam_svg, vacio)
from mesa import construccion, laminas_f1 as lf, planos as pl, versiones
from mesa.calculos import e11_cuna_gravedad, ensayar
from mesa.construccion import Solido
from mesa.despiece import despiece

CAP = PROYECTO / "01_reunir" / "capturas"
REN = PROYECTO / "05_consolidar" / "renders"

EPIGRAFES = {
    "1": ("«Il legno, in essenza naturale […], potrà essere abbinato ad altri materiali (preferibilmente scelti tra quelli in collezione)».",
          "La madera, en esencia natural, podrá combinarse con otros materiales, preferiblemente los de la colección.",
          "Bando del Porada International Design Award 2026, art. 1"),
    "2": ("«Chhakhua; La piedra hincada en la pared para atar en ella los palos del techo. Palos atados a las piedras del moxinete.»",
          "La palabra nombra la piedra y también los palos atados a ella: la unión entera.",
          "Ludovico Bertonio, *Vocabulario de la lengua aymara*, 1612, II, p. 69"),
    "3": ("«das Gestell; ein Zusammenwirken des Stützwerkes mit dem Rahmenwerk zu einem in sich Vollständigen.»",
          "El caballete: soporte y bastidor que actúan juntos y forman algo completo en sí mismo.",
          "Gottfried Semper, *Der Stil*, II, 1879, §131, p. 201"),
    "4": ("«ces meubles n'étaient composés que de grands panneaux posés sur des tréteaux pliants, qu'ils n'étaient pas à demeure.»",
          "Eran grandes tableros sobre caballetes plegables: no estaban fijos.",
          "Eugène Viollet-le-Duc, *Dictionnaire raisonné du mobilier*, I, 1873, p. 257"),
    "5": ("«The loads should be carefully considered and a large factor of safety allowed.»",
          "Las cargas deben considerarse con cuidado y dejar un gran factor de seguridad.",
          "D. W. Kessler, *Commercial Marbles of the United States*, 1919, p. 11"),
    "6": ("«pensar como el agua»: los paneles se dejan flotar, sin cola, porque la madera respira con la humedad.",
          "Lo que respira no se pega.",
          "Galen A. Johnson, «Forest and Philosophy», 2007, p. 70 (de segunda mano: cotejo de *Contenida*)"),
    "7": ("«cut with alternate grooves and projections, like mortise and tenon, so as to fit immovably into each other».",
          "Los sillares de Tiwanaku, cortados como caja y espiga para encajar sin moverse.",
          "E. G. Squier, *Peru*, 1877, p. 280"),
    "8": ("«on dressait et l'on enlevait les tables».",
          "Las mesas se armaban y se retiraban.",
          "Viollet-le-Duc, 1873, p. 257"),
}


def ren(lb, arch, w, h, **kw):
    """Un render del proyecto a su lugar; si todavía no existe, un lugar pendiente."""
    if not (REN / arch).exists():
        return vacio(f"render pendiente: {arch}", w, h)
    return img(lb.imagen(REN / arch, w, h, **kw))


# ------------------------------------------------------------------ gráficos (una serie; el umbral en almagre, rotulado)

def grafico_junta():
    """E2b: la junta entre tablas según la humedad de la madera (B2/F1)."""
    W, H, x0, y0 = 118.0, 52.0, 14.0, 6.0
    w, h = W - x0 - 4, H - y0 - 10
    hum = [4, 13]
    junta = {4: 4.80, 8: 3.0, 13: 0.75}

    def X(m):
        return x0 + (m - 4) / 9 * w

    def Y(j):
        return y0 + h - j / 6 * h
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}mm" height="{H}mm" font-family="IBM Plex Mono">']
    s.append(f'<rect x="{x0}" y="{Y(5):.2f}" width="{w}" height="{Y(0.5) - Y(5):.2f}" fill="#9a3b22" fill-opacity="0.07"/>')
    for j in (0.5, 5):
        s.append(f'<line x1="{x0}" x2="{x0 + w}" y1="{Y(j):.2f}" y2="{Y(j):.2f}" stroke="#9a3b22" stroke-width="0.25" stroke-dasharray="1.2 0.8"/>')
    s.append(f'<text x="{x0 + w}" y="{Y(5) - 1:.2f}" font-size="2.1" text-anchor="end" fill="#9a3b22">límite prerregistrado: 0,5–5 mm</text>')
    for m in (4, 6, 8, 10, 13):
        s.append(f'<line x1="{X(m):.2f}" x2="{X(m):.2f}" y1="{y0 + h}" y2="{y0 + h + 1.2}" stroke="#1d1c1a" stroke-width="0.15"/>')
        s.append(f'<text x="{X(m):.2f}" y="{y0 + h + 4}" font-size="2.1" text-anchor="middle" fill="#4f4d48">{m} %</text>')
    for j in (0, 1, 2, 3, 4, 5, 6):
        s.append(f'<text x="{x0 - 2}" y="{Y(j) + 0.7:.2f}" font-size="2.1" text-anchor="end" fill="#4f4d48">{j}</text>')
    s.append(f'<line x1="{x0}" x2="{x0 + w}" y1="{y0 + h}" y2="{y0 + h}" stroke="#1d1c1a" stroke-width="0.2"/>')
    s.append(f'<polyline points="{X(4):.2f},{Y(4.8):.2f} {X(13):.2f},{Y(0.75):.2f}" fill="none" stroke="#1d1c1a" stroke-width="0.55"/>')
    for m, lab, dy in ((4, "4,8 mm · seco", -2.0), (8, "3,0 mm · fabricación", -2.0), (13, "0,75 mm · húmedo", -2.0)):
        j = junta[m]
        s.append(f'<circle cx="{X(m):.2f}" cy="{Y(j):.2f}" r="0.9" fill="#1d1c1a"/>')
        s.append(f'<text x="{X(m) + (1.5 if m < 13 else -1.5):.2f}" y="{Y(j) + dy:.2f}" font-size="2.2" '
                 f'text-anchor="{"start" if m < 13 else "end"}" fill="#1d1c1a">{lab}</text>')
    s.append(f'<text x="{x0 - 10}" y="{y0 - 2}" font-size="2.1" fill="#4f4d48">junta (mm)</text>')
    s.append(f'<text x="{x0 + w}" y="{H - 0.6}" font-size="2.1" text-anchor="end" fill="#4f4d48">humedad de la madera</text>')
    s.append("</svg>")
    return "".join(s)


def grafico_cuna():
    """E11: el empuje de la cuña de piedra (29,4 kg) según el rozamiento, frente a lo que pide el balanceo."""
    r = e11_cuna_gravedad()
    filas_ = [f for f in r["filas"] if abs(f["masa_kg"] - 29.4) < 0.01]
    T = r["T_b_N"]
    W, H, x0, y0 = 118.0, 50.0, 16.0, 7.0
    w, h = W - x0 - 4, H - y0 - 9
    vmax = 1200

    def Y(v):
        return y0 + h - v / vmax * h
    bw = w / len(filas_) * 0.42
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}mm" height="{H}mm" font-family="IBM Plex Mono">']
    for v in (0, 400, 800, 1200):
        s.append(f'<line x1="{x0}" x2="{x0 + w}" y1="{Y(v):.2f}" y2="{Y(v):.2f}" stroke="#d3cdc2" stroke-width="0.12"/>')
        s.append(f'<text x="{x0 - 2}" y="{Y(v) + 0.7:.2f}" font-size="2.1" text-anchor="end" fill="#4f4d48">{v}</text>')
    for i, f in enumerate(filas_):
        cx = x0 + (i + 0.5) * w / len(filas_)
        e = f["empuje_N"]
        s.append(f'<rect x="{cx - bw / 2:.2f}" y="{Y(e):.2f}" width="{bw:.2f}" height="{Y(0) - Y(e):.2f}" fill="#1d1c1a"/>')
        s.append(f'<text x="{cx:.2f}" y="{Y(e) - 1.2:.2f}" font-size="2.2" text-anchor="middle" fill="#1d1c1a">{e:.0f} N</text>')
        mu = f"μ = {f['mu']:.1f}".replace(".", ",")
        s.append(f'<text x="{cx:.2f}" y="{y0 + h + 4}" font-size="2.1" text-anchor="middle" fill="#4f4d48">{mu}</text>')
    s.append(f'<line x1="{x0}" x2="{x0 + w}" y1="{Y(T):.2f}" y2="{Y(T):.2f}" stroke="#9a3b22" stroke-width="0.45" stroke-dasharray="1.6 0.9"/>')
    s.append(f'<text x="{x0 + w}" y="{Y(T) - 1.2:.2f}" font-size="2.2" text-anchor="end" fill="#9a3b22">lo que pide el balanceo (E4): {T:.0f} N</text>')
    s.append(f'<text x="{x0 - 12}" y="{y0 - 2.5}" font-size="2.1" fill="#4f4d48">empuje (N)</text>')
    s.append("</svg>")
    return "".join(s)


# ------------------------------------------------------------------ miniaturas de las versiones

def _solidos(mesa):
    out = []
    for pz in mesa.piezas:
        nombre = pz.nombre
        mat = "piedra" if pz.material.es_piedra else ("fresno" if "fresno" in pz.material.nombre else "nogal")
        veta = "z" if nombre.startswith(("montante", "clavija", "puntal", "llave")) else (
            "y" if nombre.startswith(("pie", "cabezal")) else "x")
        out.append(Solido(nombre, 0, mat, [(pz.x, pz.y, pz.z)], veta=veta))
    return out


def miniatura(fabrica, geo=None, escala=40):
    versiones.configurar(**(geo or {"a_extremo": 450, "pie_x": 180}))
    d = pl.Dibujo(escala)
    pl.ortografica(d, _solidos(fabrica()), "frente")
    d.linea([(-1300, 0), (1300, 0)], sw=0.15)
    return d.svg(1.0)


# ------------------------------------------------------------------ el libro

def componer(lb, laminas=None, informe=None):
    """laminas: rutas PNG de las tres láminas del concurso; informe: (texto, caracteres) del informe."""
    planos = lf.juego()
    caps = []

    # ---------------------------------------------------------- tapa, créditos, índice
    tapa = (juntas()
            + palabra_cortada("punto", AIRE - 1.5, fila(3) + 0.62 * TABLA, punto=False)
            + palabra_cortada("fermo", AIRE - 1.5, fila(5) + 0.62 * TABLA)
            + f'<div class="rotulo" style="{en(AIRE, 12.5, 200)}">una mesa de caballetes en nogal macizo, con una piedra en la unión</div>'
            + f'<div class="rotulo" style="{en(AIRE, fila(6) + 12, 120)}">documento de trabajo · porada international design award 2026 · '
              f'tavoli · legno massello<br><span class="gris">el proyecto, el método y los entregables · octubre de 2026</span></div>')
    lb.add(plana(tapa, "der", pid="tapa"))

    creditos = (f'<div class="rotulo" style="{en(AIRE, fila(2), 64)}">punto fermo<br><span class="gris">título provisional</span></div>'
                f'<div class="texto-plana" style="{en(TEXTO[0], fila(2), 124)}">'
                + p("Este libro reúne el proyecto entero antes de entregarlo: lo que se leyó, lo que se desarmó, las versiones que se propusieron, los ensayos con su prerregistro, las decisiones y lo que queda por hacer a mano. Es un **documento de trabajo**: no se entrega al concurso.")
                + p("**No lleva nombre de autor.** El concurso exige proyectos inéditos y anónimos: el nombre va solo en el formulario de inscripción. Los shakers tampoco firmaban sus muebles (Johnson, p. 72).")
                + p("Las figuras dicen qué son: **instrumento** (dibujadas por el código del proyecto, desde sus cálculos), **simulación** (renders: no son fotos), **dominio público** (con su fuente) o **pendiente** (un lugar en almagre que espera la maqueta, la foto o el permiso).")
                + "</div>"
                + f'<div class="rotulo" style="{en(AIRE, fila(6) + 2, 200)}">proyectos/porada-2026-mesa · '
                  f'el texto condensa los documentos del repositorio: si algo difiere, manda el repositorio</div>')
    lb.add(plana(creditos, "izq"))
    lb.add(plana(f'<div class="indice-general" style="{en(TEXTO[0] - 80, fila(2), 204, 150)}">%%INDICE%%</div>'
                 f'<div class="rotulo" style="{en(AIRE, 12.5, 100)}">índice</div>', "der", pid="indice-general"))

    # ---------------------------------------------------------- resumen
    resumen_izq = (f'<div class="rotulo" id="resumen" style="{en(AIRE, 12.5, 100)}">resumen</div>'
                   f'<div class="texto-plana" style="{en(TEXTO[0], fila(2), 124)}">'
                   + p("*Punto fermo* es una mesa de comedor de nogal macizo para el Porada International Design Award 2026. Es una **mesa de caballetes**, la forma más antigua del tipo: seis tablas sueltas, clavijadas y acuñadas sobre dos caballetes, que se mueven con la humedad y muestran la estación en sus juntas.", "entrada")
                   + p("Lo único que no se mueve es una piedra. La espiga del travesaño atraviesa un collar de mármol, y una llave de fresno lo aprieta contra el montante. La piedra trabaja solo a compresión, como pide la estereotomía; la madera se mueve y se arma, como pide la madera.")
                   + p("El libro sigue el método con que se hizo: **reunir, desarmar, proponer, ensayar y contrastar, decidir, consolidar**. Cada afirmación lleva su fuente o su ensayo; cada ensayo, lo que se registró antes de calcular; cada decisión, lo que la cambiaría. Lo que falta hacer a mano —las maquetas, la prueba con personas, la muestra de la piedra— queda en almagre.")
                   + "</div>")
    numeros = [("2400 × 1000 × 750", "mm · ocho personas"), ("48", "piezas, ningún herraje, un mazo"),
               ("106,7 kg", "en total; la pieza más pesada, 16,0 kg"), ("4,6 kg", "de piedra: dos collares de Nero Sahara Noir"),
               ("0,08 MPa", "la compresión en la piedra"), ("0,8 – 4,8 mm", "la junta entre tablas, de húmedo a seco"),
               ("12", "cuñas de fresno a la vista"), ("3", "errores que el propio proceso encontró")]
    filas_num = "".join(f'<div style="display:flex;align-items:baseline;margin-bottom:2.6mm"><span class="grande" style="width:86mm">{esc(a)}</span>'
                        f'<span class="rotulo" style="width:70mm">{esc(b)}</span></div>' for a, b in numeros)
    resumen_der = (f'<div style="{en(AIRE, fila(2) - 2, 204)}">{filas_num}</div>'
                   f'<div class="rotulo" style="{en(PAG_W - AIRE - 160, fila(6) + 16, 160)}">los tres errores: Bertonio da dos palabras donde el borrador '
                   f'leía una (E5); la clavija de las tablas centrales caía dentro del montante (E12); la de la tabla exterior asomaba por el cabezal (E12)</div>')
    lb.add(plana(resumen_izq, "izq"), plana(resumen_der, "der"))

    # ---------------------------------------------------------- la mesa a 1:5: la doble página es el tablero
    d = pl.Dibujo(5)
    pl.ortografica(d, construccion.modelo(), "planta", ocultos=("cabezal", "pie", "travesaño", "collar", "montante", "puntal"))
    svg = d.svg(0)
    import re as _re
    svg = _re.sub(r'viewBox="[^"]+" width="[^"]+" height="[^"]+"', 'viewBox="-240 -100 480 200" width="480mm" height="200mm"', svg, 1)
    n_15, fid_15 = lb.figura("la planta de F1 a 1:5: la doble página es el tablero", "instrumentos/mesa/planos.py", "instrumento")
    rot = (f'<div class="vertical" style="{en(7, fila(2), None, None)}">la doble página es el tablero a 1:5 · las tablas son las filas · '
           f'el caballete cae a 90 mm del borde · el lomo es el apoyo central · fig. {n_15} · instrumento</div>')
    lb.add(plana(f'<div style="{en(0, 0, 480, 200)}" id="{fid_15}">{svg}</div>{rot}', "izq"),
           plana(f'<div style="{en(-240, 0, 480, 200)}">{svg}</div>', "der"))

    # ================================================================== 1 · encargo
    c = Capitulo(lb, "1", "encargo", "el encargo")
    c.sec(1, "Lo que pide el concurso")
    c.add(p("El Porada International Design Award 2026, XIV edición, organizado por Porada con POLI.design del Politecnico di Milano, pide «nuevos *concept* innovadores sobre las distintas tipologías de **mesas**». El macizo tiene que ser «prevalente, pero no necesariamente exclusivo». La madera puede combinarse con otros materiales, «preferiblemente» del catálogo de la empresa: es una preferencia, no una obligación (art. 1)."),
          p("Las soluciones deben valorizar «las tecnologías productivas y los procesos de *lavorazione e nobilitazione* típicos del macizo» —el trabajo y el acabado— y cumplir la función, la seguridad, la ergonomía y criterios de sostenibilidad. El cierre es el **31 de enero de 2027**."),
          margen("**bando** · art. 1 y 7<br>leído el 26-10-2026 en italiano y en inglés; donde difieren, manda el italiano<br><br>`00_encargo/fuentes/`"))
    c.sec(2, "Cómo juzga el jurado")
    c.add(tabla(["", "criterio (art. 7)", "lo que pide al proyecto"], [
        ["1", "originalidad", "no repetir lo que ya existe: ni en los ganadores ni en el catálogo (E7)"],
        ["2", "innovación referida al trabajo típico del macizo", "que la idea esté en cómo se trabaja la madera"],
        ["3", "experimentación con materiales y **acabados de superficie**", "*nobilitazione*: aceite, cepillado, la testa"],
        ["4", "escenarios de uso y *concepts* nuevos: lo tipológico, lo tecnológico y lo morfológico", "armar, desarmar, reparar, la estación"],
        ["5", "adherencia a los valores y la identidad de Porada", "esencias y mármoles del catálogo, oficio de Brianza"],
        ["—", "Mención Allievi", "el equilibrio entre artesanía tradicional y diseño moderno **en el desarrollo estructural**"],
    ], cols=["mono", "", ""]),
          p("**Lectura**: el jurado premia lo que se hace **con la madera**. La piedra puede estar, pero si se lleva el protagonismo trabaja en contra de los criterios 2 y 3. Esa lectura entra como criterio en el proyecto (K1, K3)."))
    c.sec(3, "Qué se entrega")
    c.add(tabla(["pieza", "formato", "contenido"], [
        ["informe", "A4 vertical, **≤ 3000 caracteres**, sin imágenes, en italiano o inglés", "motivaciones, concepto general, materiales"],
        ["láminas", "**3 A3 horizontales** en un PDF de **≤ 5 MB**, sobre la plantilla oficial", "1: panorama, escenarios, concepto, fuentes · 2: planos, secciones, axonometrías, despieces, detalles · 3: renders y fotos de maqueta"],
        ["vista previa", "JPG de **≤ 1 MB**", "la imagen síntesis"],
    ], cols=["mono", "", ""]),
          p("No se admiten láminas extra. Los archivos se nombran con el código del participante (`report_`, `boards_`, `preview_`) y pueden reemplazarse hasta el cierre. Están en el capítulo 8 [[s-8-1|]]."))
    c.sec(4, "Lo que el concurso exige del proceso")
    c.add(p("Dos condiciones afectan a **cómo** se trabaja, no solo a qué se entrega: el proyecto debe ser **inédito** («originali ed inedite e sviluppate espressamente per il concorso») y **anónimo** (art. 2 y 3). Cualquier nombre en los materiales entregados excluye el proyecto, y eso incluye los metadatos de los PDF y de las imágenes."),
          p("El proyecto se desarrolla en un repositorio de GitHub que hoy es **público** y lleva el nombre del autor. Si el diseño queda a la vista antes del fallo, cualquier jurado puede encontrarlo. Lo más simple y seguro es volverlo privado hasta el 26 de febrero de 2027 (O7). Es una decisión del autor y está en la lista de lo que falta [[s-8-3|]]."),
          margen("<span class='almagre'>**pendiente** · la visibilidad del repositorio</span>"))
    lb.add(apertura(lb, c, EPIGRAFES["1"]), c.cerrar())
    caps.append(c)

    # ================================================================== 2 · reunir
    c = Capitulo(lb, "2", "reunir", "reunir: las fuentes")
    c.sec(1, "La palabra: dos entradas donde el borrador leía una")
    c.add(p("El borrador partía de *chhaxwa* y de una glosa: Bertonio daría «un solo nombre» para las piedras amontonadas y para la piedra hincada. En el facsímil de 1879 de la edición de Juli de 1612 son **dos entradas**:"),
          cita("**Chakhua**; Piedras del camino, o como las que amontonan limpiando las chacaras.<br>**Chhakhua**; La piedra hincada en la pared para atar en ella los palos del techo. Palos atados a las piedras del moxinete.",
               "Bertonio 1612/1879, II, p. 69 · F01"),
          p("En la ortografía de Bertonio, *ch*, *chh* y *cch* son consonantes distintas: son dos palabras que se parecen, no una con dos sentidos. Y la segunda dice más que el borrador: *chhakhua* nombra la piedra **y también los palos atados a ella**. Es la palabra de **una unión**, no de un lastre. La pregunta del proyecto cambió aquí (E5): dejó de ser «cómo pesa la piedra sobre la madera» y pasó a ser «**cómo se une la madera a una piedra fija**»."),
          p("Del mismo diccionario salen las acciones posibles de la unión: *cchacuru* es la **cuña** y también la estaca que se hinca (I, pp. 153 y 229, F03); *achuthaptatha*, «trabarse así de ambas partes» (I, p. 458, F04). Y una objeción: en 1612 el aymara dice «mesa» con la palabra castellana (I, p. 208, F02). No hay una «mesa andina» que diseñar."),
          margen("**F01-F04** · fuente primaria<br>leído en la fuente primaria, con captura<br><br>IA `vocabulariodela03bertgoog` n77<br><br><span class='almagre'>pendiente: la transcripción de 2011, p. 330, y un aymarista</span>"))
    c.sec(2, "Tectónica y estereotomía, en Semper")
    c.add(p("La distinción que el borrador tomaba de Frampton viene de Gottfried Semper, que es de dominio público: se fue a la fuente. En *Die vier Elemente* (1851, pp. 55-56) la masa va **abajo** —el terraplén, la albañilería— y la madera **arriba**, en el techo (F05). En *Der Stil* (1879, §131) la mesa de caballetes es el caso tipo del ***Gestell***: soporte y bastidor que forman algo completo en sí mismo (F06). Una mesa es tectónica por definición: la pregunta no es si lo es, sino **dónde entra la masa en un objeto que por tipo no la tiene**."),
          p("Y la regla que decide todo lo demás: los materiales estereotómicos resisten el aplastamiento —su principio constructivo es la **compresión**— y se les da forma quitando masa (§161, p. 334, F07). Es la misma regla que da la ingeniería: el mármol es débil a flexión (Kessler, 1919, F13)."),
          margen("**F05-F07** · fuente primaria<br>Semper 1851, pp. 55-56<br>Semper 1879, pp. 201 y 334"))
    c.sec(3, "La piedra que se ensambla como madera")
    c.add(p("En Tiwanaku la estereotomía se arma con lógica de carpintería: los sillares se cortan «**like mortise and tenon**», con pernos y grapas en T, sin mortero (Squier, 1877, pp. 280-281, F08). Es un antecedente andino que no es folclore. La mesa puede hacer lo **inverso**: un armazón de madera trabado con una pieza de piedra."),
          p("La duda queda escrita: la lectura de Squier es del siglo XIX, y los estudios recientes sobre las grapas fundidas *in situ* no se leyeron. No se afirma nada de su técnica ni de su metalurgia."),
          margen("**F08** · fuente primaria<br>Squier 1877, pp. 280-281"))
    c.sec(4, "La mesa como tipo")
    c.add(p("Viollet-le-Duc describe la mesa medieval como **tableros posados sobre caballetes plegables, que no estaban fijos**: se armaban y se retiraban de las salas (1873, p. 257, F09). La historia europea de la mesa ya trae la tensión del proyecto: la de madera, que se arma; y la de piedra o mármol, fija, que se queda. *Dresser la table*, armar la mesa, es además un escenario de uso."),
          p("Y un problema con nombre: el ***roulement des pieds***, el balanceo de las patas, que se resuelve con **ensambles** —escuadras y cartelas— y no con peso (pp. 263-264, F10). Sirve de control para el ensayo E3."),
          margen("**F09-F10** · fuente primaria<br>Viollet-le-Duc 1873, pp. 257, 263-264"))
    c.sec(5, "Los datos del material")
    c.add(tabla(["", "dato", "valor", "fuente"], [
        ["F11", "cambio dimensional del nogal negro, por 1 % de humedad", "radial 0,00190 · tangencial 0,00274", "FPL 2010, tabla 13-5"],
        ["F11", "humedad de un mueble de interior", "8 % (6-10); seco 4-9; húmedo 8-13", "FPL 2010, tabla 13-2"],
        ["F12", "nogal negro, a 12 %", "MOR 101 · MOE 11 600 · compresión ∥ 52,3 · ⊥ 7,0 · corte 9,4 MPa", "FPL 2010, tabla 5-3a"],
        ["F12", "fresno blanco, a 12 %", "MOR 103 · MOE 12 000 · ∥ 51,1 · ⊥ 8,0 · corte 13,2 MPa", "FPL 2010, tabla 5-3a"],
        ["F13", "mármol: resistencia a flexión «comparativamente baja»", "compresión 54-346 MPa; flexión 7-15 MPa (rango de trabajo)", "Kessler 1919, p. 11"],
    ], cols=["mono", "", "mono", ""]),
          p("De ahí sale el dato más decisivo para una mesa de macizo: **la madera se mueve unos 13,7 mm por metro de ancho entre estaciones; la piedra, nada**. Sobre esa diferencia se construyen las dos propuestas."))
    c.sec(6, "Pensar como el agua")
    c.add(p("Galen A. Johnson, filósofo y ebanista, escribe una estética de la madera. Sus citas llegan **de segunda mano**: se cotejaron con el artículo en otro proyecto del autor, *Contenida*, y aquí no se volvieron a cotejar (F15)."),
          lista(["**«Pensar como el agua»** (p. 70): los paneles se dejan flotar, sin cola, porque la madera respira con la humedad. Es la regla de la propuesta B dicha por un ebanista.",
                 "**Los anillos cuentan la vida del árbol** (pp. 63-64): un corte del tronco «puede leerse como la historia de la vida del árbol». Respalda dejar **la testa a la vista** donde la madera atraviesa la piedra.",
                 "**La superficie como «membrana táctil»** (p. 62): un argumento para el acabado al aceite, que se toca."]),
          margen("**F15** · de segunda mano<br>Johnson 2007, *Environmental Philosophy* 4 (1-2): 59-75<br><span class='almagre'>pendiente: cotejo de primera mano</span>"))
    c.sec(7, "Los precedentes")
    c.add(p("Se leyeron los compendios de ganadores de 2017 (mesas pequeñas) y 2018 (escritorios), el catálogo de Porada y los concursos afines (E7). 2026 es la primera edición dedicada a la **mesa de comedor**, y ningún ganador usó caballetes, tablas sueltas ni uniones de piedra."),
          p("Pero el catálogo **ya junta madera y mármol**: *Oswood* celebra «l'incontro tra due materiali» y *Osmose* tiene patas de mármol. *Augusto* tiene una base de elementos encastrados y *Beam*, un travesaño a la vista. Y el lenguaje de tablas ya fue premiado en otro concurso: *Planks*, de Max Lamb (Wood Awards 2016), con tablas fijas. Lo original no puede ser juntar madera y piedra: tiene que ser **el modo del encuentro**."),
          tabla(["lo que el jurado premió", "dónde"], [
              ["el macizo trabajado como protagonista", "*Screen*, 2018"],
              ["componentes con individualidad, que se componen", "*Whirl*, 2018"],
              ["intercambiabilidad funcional", "*Odette*, 2018"],
              ["el material de acento en la unión: el detalle precioso", "*Sliding Plates*, *Fly*, *Ninfea*"],
              ["una familia de medidas", "*Leo*, 2017"],
          ]),
          margen("**E7** · precedentes<br>compendios 2017-2018 (POLI.design), catálogo de Porada, Wood Awards 2016<br><br>las imágenes tienen derechos: se citan, no se copian"))
    c.sec(8, "Los materiales")
    c.add(p("Se mantienen los materiales del catálogo de Porada, los tres de uso en sus mesas: **nogal canaleta** (*Juglans nigra*) para las tablas y los caballetes, **fresno** para clavijas, cuñas, lengüetas y llaves, y mármol **Nero Sahara Noir** apomazado para los collares (K8)."),
          p("Una propuesta de materiales bolivianos se contrastó afirmación por afirmación. El nogal de los Yungas no es *Juglans neotropica* —que además está **En Peligro**— sino *J. boliviana*, descrita primero como *J. nigra* var. *boliviana*: **el mismo nogal negro que el canaletta**. Es un vínculo que va al relato, no a la fabricación. La piedra de Comanche es **granito** según la ley de La Paz de 2012, no andesita, y queda registrada como alternativa. La «piedra que bloquea por gravedad» se calculó y no funciona (E11)."),
          margen("`01_reunir/materiales_bolivianos.md`<br>GBIF, Lexivox, ESPEN, BioOne"))
    c.sec(9, "Lo que se buscó y no se usó")
    c.add(lista(["Las **cinco referencias visuales** del borrador: su autoría no está verificada. No se reproducen: quedan cinco lugares en almagre [[refs-visuales|]].",
                 "**Frampton** (1995): citado a través del artículo del autor. Tiene derechos vigentes: no se captura.",
                 "**Monoskop**: no fue accesible desde el entorno de trabajo (error 500).",
                 "**Kessler, tabla 6** (módulo de rotura por mármol): página girada que el OCR no leyó. Por eso el mármol se calcula con un rango, a confirmar con la ficha EN 12372."]))
    lb.add(apertura(lb, c, EPIGRAFES["2"]), c.cerrar())
    caps.append(c)
    lb.add(lamina_fuentes(lb))

    # ================================================================== 3 · desarmar
    c = Capitulo(lb, "3", "desarmar", "desarmar: el problema")
    c.sec(1, "La entrada: la unión")
    c.add(p("El problema amplio —tectónica y estereotomía en una mesa de macizo— se trabaja por una entrada delimitada: **la unión**, el lugar donde la madera y la piedra se tocan. Desde ahí se conecta con lo mayor: el orden del tipo, el uso y la producción."))
    c.sec(2, "Partes")
    c.add(tabla(["", "parte", "en la mesa", "lo que la condiciona"], [
        ["⊥", "apoyo", "caballetes: pie, montante, cabezal", "estabilidad, balanceo (F10), suelo irregular"],
        ["○", "vano", "el lugar de las rodillas; la distancia entre caballetes", "ergonomía; cuántas personas caben"],
        ["●", "masa", "la piedra, o la madera que pesa", "trabaja bien solo a compresión (F07, F13); peso por pieza"],
        ["=", "límite", "el tablero: superficie, canto", "humedad (F11), calor, limpieza, tacto"],
        ["✕", "unión", "donde apoyo, masa y límite se encuentran", "todo lo anterior a la vez"],
    ], cols=["mono", "", "", ""]),
          p("El cuadro de las partes viene del artículo del autor, *Cosecha de piedras* (F14), que es inédito y no se reproduce."))
    c.sec(3, "Relaciones")
    c.add(lista(["**Carga**: la gravedad, del tablero a los caballetes y al suelo.",
                 "**Balanceo**: un empuje horizontal deforma el armazón en paralelogramo. Se resiste con ensambles, no con peso (F10).",
                 "**Movimiento**: la madera cambia de ancho con la humedad; la piedra no (F11). Es del orden de **1 cm en 1 m** entre invierno y verano.",
                 "**Uso**: rodillas, codos, alguien que se apoya o se sienta en el borde; el calor y los líquidos.",
                 "**Montaje**: armar y desarmar (F09); el peso de la pieza más pesada."]))
    c.sec(4, "Acciones")
    c.add(tabla(["acción", "fuente", "operación"], [
        ["hincar", "*cchacuntatha* (F03); *chhakhua* «hincada» (F01)", "encastrar en una caja"],
        ["atar", "*chhakhua* «para atar» (F01)", "amarre (se descarta: en un mueble la fibra se afloja)"],
        ["**acuñar**", "*cchacuru*, la cuña (F03)", "cuña o llave que traba una espiga pasante"],
        ["trabar de ambas partes", "*achuthaptatha* (F04)", "ensamble recíproco"],
        ["encajar", "*haquithaptatha* (F02)", "caja y espiga"],
        ["asentar", "la gravedad", "la piedra se apoya por su peso, sin cola"],
        ["amontonar", "*chakhua* (F01)", "apilar: la figura del montón, no de la unión"],
    ]))
    c.sec(5, "Conflictos")
    c.add(tabla(["", "conflicto", "consecuencia"], [
        ["C1", "la madera se mueve y la piedra no (F11)", "no se puede **pegar** piedra a madera a contraveta: hay que dejar holgura"],
        ["C2", "la piedra es débil a flexión (F07, F13)", "la piedra **no puede ser viga**"],
        ["C3", "las bases premian la madera; las referencias tiran a la masa", "la piedra no puede llevarse el protagonismo"],
        ["C4", "Semper pone la masa abajo; el borrador, arriba (F05)", "la inversión hay que decidirla"],
        ["C5", "*chhakhua* (unión) frente a *chakhua* (montón) (F01)", "el lastre se queda sin su palabra"],
        ["C6", "la mesa es un mueble ajeno al mundo andino (F02)", "no hay «mesa andina» que diseñar"],
        ["C7", "madera y piedra tienen tolerancias distintas", "la junta debe absorber la tolerancia"],
        ["C8", "el peso dificulta el transporte", "límite de 25 kg por pieza"],
    ], cols=["mono", "", ""]))
    c.sec(6, "Criterios, fijados antes de calcular")
    c.add(p("Cada criterio dice **con qué se mide**: un cálculo, el contraste con una fuente, una prueba física o el juicio de otros. Así un instrumento no responde preguntas que no puede responder. Los umbrales de K1-K5 se escribieron antes del instrumento (`7e6165b`) y no se movieron después."),
          tabla(["", "criterio", "cómo se mide", "umbral"], [
              ["K1", "madera protagonista", "cálculo: % del volumen", "≥ 85 %"],
              ["K2", "piedra a compresión", "cálculo: flexión en la piedra", "≤ MOR/3 = 2,33 MPa"],
              ["K3", "movimientos compatibles", "cálculo: holguras; ¿cola a contraveta?", "≤ 3 mm por lado; sin cola piedra-madera"],
              ["K4", "estable sin depender del lastre", "cálculo: vuelco sin piedra", "≥ 2 × la carga de referencia"],
              ["K5", "transporte y montaje", "cálculo: la pieza más pesada", "≤ 25 kg"],
              ["K6", "fidelidad a la fuente", "contraste con fuentes", "la acción es la que dice la fuente"],
              ["K7", "escenario de uso nuevo", "juicio y ensayo de uso", "—"],
              ["K8", "identidad Porada", "contraste con el catálogo", "esencias y mármoles de catálogo"],
              ["K9", "sin folclorismo", "juicio de terceros (E6)", "lo andino como lógica, no como imagen"],
              ["K10", "originalidad", "contraste con precedentes (E7)", "sin antecedente directo de la unión"],
          ], cols=["mono", "", "", "mono"]),
          margen("<span class='almagre'>**prerregistro**</span><br>`7e6165b` · 12:10<br>umbrales de A, antes del instrumento"))
    c.sec(7, "Objeciones serias")
    c.add(tabla(["", "objeción", "cómo se atiende"], [
        ["O1", "«un solo nombre» para montón y piedra hincada: no lo dice Bertonio", "la unión, no el lastre; revisar el artículo"],
        ["O2", "la «mesa andina» no existe", "el tipo es europeo; de los Andes viene una lógica constructiva con referencia explícita"],
        ["O3", "la piedra puede ser solo ornamento", "una versión de control sin piedra (V3) y E6"],
        ["O4", "«la gravedad de la piedra sostiene la ligereza del armazón»: físicamente, al revés", "E1, E3, E4 y E11"],
        ["O5", "folclorismo: la «roca andina»", "K9: la piedra se corta, no se imita (F07)"],
        ["O6", "poner un nombre aymara a un producto italiano", "un título descriptivo; la palabra va en el informe con su fuente"],
        ["O7", "publicar el proceso en un repositorio público", "volverlo privado hasta el fallo"],
    ], cols=["mono", "", ""]))
    lb.add(apertura(lb, c, EPIGRAFES["3"]), c.cerrar())
    caps.append(c)

    # ================================================================== 4 · proponer
    c = Capitulo(lb, "4", "proponer", "proponer: dos entradas y una síntesis")
    c.sec(1, "Propuesta A, desde el concepto del autor")
    c.add(p("Las cuatro primeras versiones discuten **dónde va la piedra**, cada una con una acción de la fuente. Todas comparten caballetes, travesaño y tablero, para poder compararlas."),
          tabla(["", "versión", "acción", "qué se probó"], [
              ["V0", "lastre: una barra de mármol en el tablero", "asentar", "¿puede la piedra ser viga? (E1)"],
              ["V1", "llave de piedra en la espiga", "acuñar", "¿cabe una llave de mármol? (E4)"],
              ["V2", "montante hincado en un pie de piedra", "hincar", "¿qué holgura pide? (E2)"],
              ["V3", "solo madera: el control", "acuñar", "¿hace falta la piedra?"],
              ["V0b", "piedra asentada en un canal, sin cola", "asentar", "derivada de E1"],
              ["V4", "collar: la espiga atraviesa la piedra", "atravesar", "derivada de E4"],
          ], cols=["mono", "", "", ""]),
          p("Los ensayos descartaron V0, V1 y V2, y retiraron tres frases del borrador: «la piedra estabiliza», «el peso traba» y «la gravedad de la piedra sostiene la ligereza del armazón». El control **V3 cumplió lo mismo que V4 sin piedra**: en ninguna versión la piedra era necesaria para la estructura."))
    c.sec(2, "El autor advierte que predeterminó el concepto")
    c.add(p("Al fijar de antemano piedra y *chhaxwa*, el proceso pudo quedar inclinado hacia un resultado. Los ensayos sí contradijeron el borrador, pero todas las versiones seguían discutiendo dónde va la piedra: ninguna podía proponer que el problema fuera otro. Se abrió entonces una **propuesta B** con otra entrada, sacada de la misma bibliografía, con su propio prerregistro (`38a6dc6`) y medida con el mismo instrumento."))
    c.sec(3, "Propuesta B, desde la bibliografía y sin la premisa")
    c.add(p("B parte de dos fuentes que convergen: **la madera se mueve 13,7 mm por metro** (F11) y **la mesa medieval no fijaba el tablero** (F09). El mueble moderno fija el tablero y después pelea contra su movimiento con herrajes; B vuelve al tablero que no se fija, con precisión de taller. Su relación: «**cada tabla se mueve sola; la mesa muestra la estación**»."),
          tabla(["", "versión", "resultado"], [
              ["B1", "5 tablas de 196 mm posadas sobre los caballetes", "✗ flecha 5,8 mm (E8); una tabla suelta vuelca con 219 N (E9); tabla demasiado ancha (E2b)"],
              ["B2", "6 tablas de 164 mm, clavijadas y acuñadas, con lengüetas y apoyo central", "✓ todo lo aplicable, sin piedra"],
              ["B3", "B2 con una tabla de servicio con mármol asentado", "✓ K1-K5; nace de los precedentes (E7)"],
          ], cols=["mono", "", ""]),
          p("Un hecho que nadie buscaba: **la cuña volvió en B por una razón propia**. Una tabla suelta vuelca si alguien se sienta en su punta, así que hay que trabarla."))
    c.sec(4, "La síntesis: la misma regla vista desde dos lados")
    c.add(p("Las reglas de A y de B no chocan: son la misma regla vista desde lados distintos. En B, **la madera se mueve** y la mesa no lo esconde. En A, **la piedra no se mueve**: es el punto fijo donde se traba la madera. Juntas dan una sola regla, que además coincide con la fuente —la piedra hincada, fija, donde se atan los palos— y con los cálculos:"),
          regla("La madera se mueve y se arma; lo único fijo es la piedra donde se traba."),
          p("La cuña aparece en las dos por razones independientes: en A traba la espiga contra el collar (E4); en B traba cada tabla al cabezal (E9). La cuña, *cchacuru*, es **el verbo común de la mesa**. AB —el tablero de B2 con el collar de V4— cumplió K1-K5 en la ronda 4."))
    c.sec(5, "Lo que no se propuso")
    c.add(lista(["**Atar**, aunque es la acción literal de *chhakhua*: en un mueble de uso diario la fibra se afloja.",
                 "**Un tablero de piedra sobre un armazón de madera**: pone la piedra a flexión en todo el vano (C2) y deja la madera como accesorio (K1).",
                 "**La roca imitada**: por K9 y O5. La piedra se corta; no se imita."]))
    lb.add(apertura(lb, c, EPIGRAFES["4"]), c.cerrar())
    caps.append(c)
    lb.add(lamina_versiones(lb))

    # ================================================================== 5 · ensayar
    c = Capitulo(lb, "5", "ensayar", "ensayar y contrastar")
    c.sec(1, "Cómo se ensaya")
    c.add(p("Cada ensayo es **la prueba más pequeña que responde una incertidumbre**. Antes de calcular se escribe qué resultado cambiaría la idea, y se guarda en git: el umbral no se mueve después de ver el resultado. Cuando hubo una cuenta a mano previa, se dice. Cada ensayo dice además **qué no demuestra**."),
          tabla(["supuesto", "valor"], [
              ["P · una persona apoyada", "1000 N"], ["H · un empuje horizontal", "300 N"],
              ["humedad: fabricación · rango", "8 % · 4-13 % (6-11 % estacional)"],
              ["factor de diseño de la madera", "1/3 del MOR"], ["rozamiento madera-madera", "μ = 0,4"],
          ], cols=["", "mono"]),
          margen("<span class='almagre'>**los prerregistros, en git**</span><br>`7e6165b` 12:10 · A<br>`38a6dc6` 12:28 · B<br>`c7b8cbb` 12:43 · E6a, E10a<br>`924e6a0` 13:56 · E11<br>`f3f5ad9` 16:43 · E12"))
    c.sec(2, "Los ensayos de la propuesta A")
    c.add(ensayo("E1", "la piedra como viga", "¿Puede una barra de mármol ser parte del tablero (V0)?", [
        ("prerregistro", "si la flexión supera MOR/3 = 2,33 MPa, la piedra no puede ser viga", True),
        ("resultado", "**9,9 MPa** en la barra. Ni el mármol más resistente (15/3 = 5 MPa) la salva."),
        ("decisión", "**descartar V0**; derivar V0b: la madera carga la piedra"),
        ("no demuestra", "el comportamiento a largo plazo ni la rotura real")], ("no cumple", False), "ronda 1"),
          ensayo("E2", "el movimiento", "¿Qué holgura pide una piedra encajada en madera?", [
        ("prerregistro", "si la junta supera 3 mm por lado, o hay cola a contraveta, no cumple K3", True),
        ("resultado", "V2 pide **1,8 mm por lado** y en seco llega a 3,2 mm: hay que acuñar el montante"),
        ("decisión", "«hincar» deja de ser la acción: pasa a ser encajar y acuñar")], ("no cumple", False), "ronda 1"),
          ensayo("E3", "el vuelco", "¿Estabiliza la piedra la mesa?", [
        ("prerregistro", "si el aporte del lastre no es necesario para resistir 2 P en el extremo, se retira «la piedra estabiliza»", True),
        ("resultado", "con el pie de 80 mm ninguna versión llegaba a 2 P; el lastre sumaba +40 % y no alcanzaba. **Alargar el pie a 180 mm** lo resuelve para todas"),
        ("decisión", "**corrección común**: pie de 180 mm. Con la geometría corregida, el aporte de la piedra baja a +16 % y no hace falta: se retira la frase")], ("modificar", True), "rondas 1-2"),
          ensayo("E4", "la unión", "¿Cabe una llave de piedra en la espiga? ¿Traba el peso?", [
        ("prerregistro", "si la llave de mármol pide más profundidad de la que cabe, la piedra no puede ser la llave", True),
        ("resultado", "la de mármol necesita **53-75 mm** y caben 37; la de fresno, 14-19 mm. El peso de la llave es el **0,6 %** del rozamiento que la sostiene"),
        ("decisión", "**descartar V1**; se retira «el peso traba». V4: la espiga atraviesa un collar de piedra que trabaja a **0,08-0,17 MPa** de compresión")], ("no cumple", False), "ronda 1"),
          ensayo("E5", "la palabra", "¿Dice Bertonio «un solo nombre»?", [
        ("prerregistro", "ninguno: el contraste se hizo al leer la fuente, y así se declara", True),
        ("resultado", "dos entradas: *chakhua* y *chhakhua* (F01)"),
        ("decisión", "**cambiar la pregunta**: la unión, no el lastre")], ("cambiar la pregunta", True), "ronda 1"))
    c.sec(3, "Los ensayos de la propuesta B")
    c.add(ensayo("E8", "la flecha de una tabla", "¿Se hunde una tabla frente a sus vecinas?", [
        ("prerregistro", "si la flecha bajo P supera 2 mm, hacen falta lengüetas o un apoyo intermedio", True),
        ("resultado", "B1: **5,8 mm**. B2, con lengüetas y apoyo central: **1,0 mm** (0,6 de la tabla, repartida entre tres, y 0,8 del travesaño bajo el puntal)"),
        ("no demuestra", "que las lengüetas sueltas repartan la carga entre tres tablas: es un supuesto")], ("cumple en B2", True), "rondas 3-4"),
          ensayo("E9", "el vuelco de una tabla", "¿Puede una tabla ir solo posada?", [
        ("prerregistro", "si una tabla suelta vuelca con menos de 2 P, hay que trabarla", True),
        ("resultado", "vuelca con **219 N** (B1) y **184 N** (B2): hay que trabarla. La **cuña vuelve**, por una razón propia"),
        ("decisión", "clavija de fresno en el eje de cada tabla, acuñada")], ("modificar", True), "rondas 3-4"),
          ensayo("E2b", "las juntas entre tablas", "¿Qué ancho de tabla deja la junta entre 0,5 y 5 mm?", [
        ("prerregistro", "si la junta sale del rango entre 4 y 13 % de humedad, cambia el ancho de la tabla", True),
        ("resultado", "tabla **≤ 182 mm**. Con 164 mm y junta de 3 mm al 8 %: **0,75 mm** al 13 % y **4,8 mm** al 4 %. La estación se ve en la junta"),
        ("no demuestra", "si la junta molesta en el uso: eso es E10")], ("cumple", True), "rondas 3-4"),
          fig(lb, svg_a(grafico_junta(), 118), "E2b: la junta según la humedad", "contenido.py · grafico_junta",
              "instrumento", "La junta entre tablas, de 164 mm con 3 mm al 8 %, según la humedad de la madera: una sola recta, del húmedo al seco. La banda es el rango prerregistrado."))
    c.sec(4, "Los ensayos de la síntesis")
    c.add(ensayo("E7", "la originalidad", "¿Existe un antecedente directo?", [
        ("prerregistro", "si existe, cambia la unión o el argumento, no solo el aspecto", True),
        ("resultado", "no hay antecedente de la unión; **sí del argumento** «madera y mármol» (*Oswood*, *Osmose*)"),
        ("decisión", "**modificar el argumento**: la piedra no es lujo junto a la madera, es el punto fijo de la unión. Nace B3")], ("modificar", True), "ronda 5"),
          ensayo("E11", "la piedra en cuña", "¿Puede una piedra en cuña tensar el caballete con su propio peso?", [
        ("prerregistro", "si con la piedra más pesada razonable (29 kg) el empuje no llega a lo que pide el balanceo, el bloqueo por gravedad se descarta; y si la piedra sube y baja más de 2 mm entre estaciones, tampoco sirve", True),
        ("resultado", "empuja como máximo **538 N** sin rozamiento y ~190 N sobre fieltro; el balanceo pide **1023 N**. Harían falta 56-185 kg de piedra. Y sube y baja **6,9 mm**"),
        ("decisión", "**descartar**. Es la tercera vez que el peso de la piedra no alcanza (E3, E4, E11)")], ("no cumple", False), "e11"),
          fig(lb, svg_a(grafico_cuna(), 118), "E11: el empuje de la cuña", "contenido.py · grafico_cuna", "instrumento",
              "La piedra más pesada razonable (29,4 kg) en una cuña de 15°: su empuje según el rozamiento, frente a lo que pide el balanceo. Ninguna barra llega a la línea."),
          ensayo("E12", "las interferencias", "¿Se cruzan piezas donde no hay ensamble?", [
        ("prerregistro", "cualquier cruce de más de 0,1 mm fuera de los ensambles previstos es un error de dibujo; se declara que la interferencia ya se había visto", True),
        ("resultado", "en AB y B2, la clavija y la cuña de las **tablas centrales caían dentro del montante**: 8 cruces. Al dibujar la sección A-A apareció otro: la clavija de la tabla exterior **asomaba 3 mm** por el cabezal de 850"),
        ("decisión", "**modificar**: en F1 la cuña atraviesa el cabezal y el cabezal mide 900 mm. 0 cruces; 72 ensambles verificados en el modelo constructivo")], ("modificar", True), "ronda 6"))
    c.sec(5, "Lo que el cálculo no responde")
    c.add(p("Dos preguntas deciden entre las versiones y ninguna es un cálculo: **¿se lee el collar como parte de la unión o como adorno?** (E6) y **¿molestan las juntas en el uso?** (E10). Las dos son pruebas físicas, pendientes. Hay una versión previa con renders (E6a, E10a), prerregistrada antes de renderizar, que se puede hacer ya con cinco personas."),
          prerregistro(lista(["**E6a**: si 3 de 5 personas llaman a la piedra adorno, decoración o perilla, el collar cambia de forma o de tamaño, o la propuesta pasa a B2.",
                              "**E10a**: si 3 de 5 leen la junta como defecto, se revisa cómo se muestra (lengüeta a ras, canto achaflanado).",
                              "**E6 y E10**: el nodo a 1:1 y tres tablas de 600 mm usadas una semana."])),
          p("Una observación **no prerregistrada**, anotada como tal: a la distancia de la vista general, el collar casi no se ve, con mármol negro o con piedra gris mate. Lo que limita su lectura es su tamaño, no la piedra."),
          margen("<span class='almagre'>**pendiente** · E6a, E10a, E6, E10</span><br><br>`04_ensayar/E6a_E10a_hoja.md`"))
    lb.add(apertura(lb, c, EPIGRAFES["5"]), c.cerrar())
    caps.append(c)
    lb.add(lamina_junta(lb))

    # ================================================================== 6 · decidir
    c = Capitulo(lb, "6", "decidir", "decidir: la bitácora")
    c.sec(1, "La bitácora, como un guion")
    c.add(p("Cada entrada registra qué movimiento se hizo, qué se decidió —conservar, modificar, descartar o cambiar la pregunta—, por qué, y cuál es la siguiente acción. Los movimientos no van en orden: hay retornos. Al margen, la hora y el commit: el código de tiempo del proyecto."),
          guion())
    c.sec(2, "La propuesta final: F1")
    c.add(p("La iteración que pidió el autor: una versión final con lo mejor de A y de B. **No cierra el proyecto**: las pruebas físicas todavía pueden cambiarla, y está escrito antes de hacerlas qué resultado la cambiaría."),
          tabla(["criterio del jurado", "B2 · solo madera", "**F1 · collar de piedra**", "B3 · tabla de servicio"], [
              ["1 · originalidad", "el lenguaje de tablas ya fue premiado (*Planks*)", "**sin antecedente directo**: la piedra es el punto fijo de una unión", "mármol en el tablero: cerca de *Oswood*"],
              ["2 · trabajo del macizo", "clavijas, cuñas, lengüetas", "lo mismo y una espiga pasante acuñada que atraviesa la piedra", "igual que B2, y un canal"],
              ["3 · materiales y acabados", "una esencia, dos caras", "nogal, fresno y mármol, cada uno con su trabajo; la testa a la vista", "nogal y mármol asentado"],
              ["4 · escenarios de uso", "armar, reparar, la estación", "los mismos, y la unión que se aprieta a mano", "los mismos, y la tabla que se cambia"],
              ["5 · identidad Porada", "catálogo", "catálogo", "catálogo"],
              ["riesgo", "«solo madera bien hecha»", "que el collar se lea como adorno (E6)", "dos razones para una piedra"],
          ], ancha=True),
          lista(["**Conservar** AB: es la síntesis compatible de A y B, y su originalidad está donde E7 no encontró antecedentes.",
                 "**Modificar** la cuña (E12): atraviesa el cabezal; 12 cuñas quedan a la vista. El cabezal pasa a 900 mm.",
                 "**Descartar** B3 como versión final: suma piedra con otra razón (control de expansión).",
                 "**B2 queda como salida prerregistrada** si E6 dice «adorno»: en el modelo es cambiar un parámetro."]))
    c.sec(3, "Lo que cambiaría esta decisión")
    c.add(prerregistro(tabla(["si…", "entonces…"], [
        ["en E6a, 3 de 5 llaman a la piedra adorno", "el collar cambia de forma o de tamaño y se repite E6a"],
        ["en E6 (el nodo 1:1) se confirma «adorno»", "**la propuesta final pasa a B2** con la corrección de E12"],
        ["en E10 la junta molesta en el uso", "se revisa cómo se muestra la junta"],
        ["la ficha del mármol da un MOR menor que 7 MPa", "nada: el collar trabaja a 0,08 MPa. Se registra"],
        ["el autor elige otro título o frase (O6)", "cambian el informe y las láminas; el diseño, no"],
    ])), margen("`05_consolidar/propuesta_final.md`"))
    c.sec(4, "Título y frase, provisionales")
    c.add(p("«**Punto fermo**»: en italiano, el punto fijo, lo que no se mueve; también se dice de algo cierto, y *punto fermo* es el punto final de una frase. *Fermo* es además el tope o la traba de un carpintero. Nombra la regla de la mesa sin usar una palabra aymara como marca (O6): *chhakhua* va en el informe, con su fuente. Lo deciden el autor y, si hiciera falta, quienes hablan la lengua."),
          regla("Il legno si muove e si monta; l'unica cosa ferma è la pietra dove si incastra."))
    lb.add(apertura(lb, c, EPIGRAFES["6"]), c.cerrar())
    caps.append(c)

    # ================================================================== 7 · la mesa
    c = Capitulo(lb, "7", "fermo", "la mesa: punto fermo")
    c.sec(1, "La regla, en la mesa")
    c.add(p("Seis tablas de nogal canaleta de 2400 × 164 × 40 mm se posan sobre dos caballetes y un apoyo central. Cada tabla lleva una clavija de fresno en su eje sobre cada caballete; una cuña de fresno atraviesa el cabezal y la traba. Entre tabla y tabla, una lengüeta suelta reparte la carga y cierra la junta por debajo. Cada tabla se mueve sola: la junta pasa de 0,8 mm en tiempo húmedo a 4,8 mm en seco.", "entrada"),
          p("El travesaño une los caballetes. Su espiga pasante atraviesa el montante y un **collar de mármol Nero Sahara Noir** de 70 × 110 × 150 mm; una **llave de fresno**, golpeada con un mazo, aprieta la piedra contra el montante. La piedra trabaja a 0,08 MPa de compresión, sin cola y sin flexión, con un milímetro de holgura por lado. Es el único punto fijo de la mesa."),
          fig(lb, ren(lb, "general_F1.png", 124, 80), "F1, vista general", "05_consolidar/renders/general_F1.png", "simulacion",
              "F1. Nogal canaleta, fresno y Nero Sahara Noir; renderizado con Cycles desde el árbol de Geometry Nodes del proyecto."))
    c.sec(2, "Materiales y acabados")
    c.add(tabla(["", "material", "dónde", "acabado"], [
        ["nogal canaleta", "*Juglans nigra*, catálogo Porada", "tablas, pies, montantes, cabezales, travesaño, puntal", "aceite: la superficie como membrana táctil (F15)"],
        ["fresno", "*Fraxinus*, catálogo Porada", "clavijas, cuñas, lengüetas, llaves", "natural, aceitado; claro sobre el nogal: la unión se ve"],
        ["Nero Sahara Noir", "mármol del catálogo, de las mesas de Porada", "dos collares", "apomazado; aristas achaflanadas de 3 mm"],
    ]),
          p("**La testa queda a la vista**: más allá de la llave, la espiga del travesaño asoma 42 mm y muestra sus anillos (Johnson, pp. 63-64). Las cuñas asoman 10 mm por cada costado del cabezal. Lo que traba se ve; lo que se mueve, también."),
          fig(lb, ren(lb, "testa_F1.png", 124, 84), "la testa de la espiga", "05_consolidar/renders/testa_F1.png", "simulacion",
              "La espiga atraviesa el montante y el collar; la llave de fresno aprieta la piedra; la testa queda a la vista."))
    c.sec(3, "Escenarios de uso")
    c.add(lista(["**A la mesa**: ocho personas, tres por lado y una en cada cabecera (estimación de dibujo). Las cabeceras quedan libres para las rodillas: el caballete está a 450 mm del extremo (E3).",
                 "**Armar y desarmar**, con un mazo y sin herrajes, en siete pasos. La pieza más pesada, el caballete encolado, pesa 16,0 kg (K5).",
                 "**La estación**: la junta registra la humedad del aire. La piedra no se mueve: es el punto fijo.",
                 "**Reparar**: una tabla se cambia sin desarmar la mesa. Se sacan sus dos cuñas, se desliza la lengüeta por la testa y la tabla sale."]),
          montaje_figura(lb, planos))
    c.sec(4, "Planos")
    c.add(p("Los planos salen del **modelo constructivo** de F1: cada pieza con sus espigas, cajas, ranuras y agujeros. Antes de dibujar, el modelo verifica que cada parte que entra en otra pieza quepa en un vacío de esa pieza (72 ensambles, ningún error). Todo lo que no sale de un ensayo es una **decisión de dibujo**: las espigas del caballete, la horquilla del puntal, el ahusado de la llave (1:40) y las ranuras de las lengüetas."),
          margen("los números en círculo son los del despiece<br><br>ejes y cortes en almagre<br><br>piedra cortada: negro<br>madera en testa: anillos<br>madera a lo largo: líneas en la fibra"))
    for nombre in ("alzado", "planta"):
        dib, titulo, escala = planos[nombre]
        c.add(fig(lb, svg_a(dib.svg(1.5), 204), f"F1, {titulo}", "instrumentos/mesa/laminas_f1.py", "instrumento",
                  f"F1, {titulo}, {escala} en la lámina; aquí, reducido al ancho de la página.", clase="ancha flota"))
    for nombre in ("lateral", "seccion_a", "detalle_tablas"):
        dib, titulo, escala = planos[nombre]
        c.add(fig(lb, svg_a(dib.svg(1.5), 124 if nombre != "lateral" else 110), f"F1, {titulo}", "instrumentos/mesa/laminas_f1.py",
                  "instrumento", f"F1, {titulo}. Escala {escala} en la lámina; aquí, ajustado a la columna."))
    c.sec(5, "Despiece")
    m = versiones.f1()
    filas_d = []
    marca = {v: k for k, v in lf.PIEZAS.items()}
    for f_ in despiece(m):
        dims = " × ".join(f"{d_:g}" for d_ in f_["medidas_mm"]).replace(".", ",")
        mat = f_["material"].split(" (")[0].replace("mármol", "Nero Sahara Noir").replace(", por elegir", "")
        filas_d.append([str(marca.get(f_["pieza"], "")), f_["pieza"], mat, dims, str(f_["cantidad"]),
                        f"{f_['masa_total_kg']:.1f}".replace(".", ",")])
    c.add(fig(lb, svg_a(planos["despiece"][0].svg(1.5), 204), "F1, despiece axonométrico", "instrumentos/mesa/laminas_f1.py", "instrumento",
              "Despiece axonométrico: las tablas, las lengüetas, el apoyo central, los collares, las llaves y las cuñas, separados de los caballetes.",
              clase="ancha flota"),
          tabla(["n.º", "pieza", "material", "medidas (mm)", "cant.", "kg"], filas_d, cols=["mono", "", "", "mono", "mono d", "mono d"],
                total=["", "total", "", "", str(len(m.piezas)), f"{m.masa():.1f}".replace(".", ",")]))
    lb.add(apertura(lb, c, EPIGRAFES["7"]), c.cerrar())
    caps.append(c)
    lb.add(lamina_nodo_real(lb))
    lb.add(lamina_renders(lb))

    # ================================================================== 8 · consolidar
    c = Capitulo(lb, "8", "consolidar", "consolidar: los entregables")
    c.sec(1, "Los entregables del concurso")
    c.add(p("Las tres láminas, el informe y la vista previa se arman con el mismo sistema que este libro, en inglés, y **sin nombre**: los PDF salen sin autor en sus propiedades. El código del participante (`CODICE`) se reemplaza al inscribirse. La plantilla oficial solo se ve después de registrarse: las láminas están hechas para pasarse a ella sin cambiar su contenido."),
          margen("`05_consolidar/concurso/`<br>`boards_CODICE.pdf`<br>`report_CODICE.pdf`<br>`preview_CODICE.jpg`"))
    if laminas:
        for i, ruta in enumerate(laminas, 1):
            c.add(fig(lb, img(lb.imagen(ruta, 204, None, ppp=200, nombre=f"lamina_{i}.jpg")), f"lámina {i} del concurso",
                      f"05_consolidar/concurso/boards_CODICE.pdf, p. {i}", "instrumento",
                      f"Lámina {i} de 3, A3 horizontal, reducida al 48,6 %.", clase="ancha flota"))
    if informe:
        texto, n = informe
        c.add(p(f"**El informe** tiene {n} caracteres de los 3000 permitidos. Va completo:"),
              f'<div class="cita" style="font-size:6.6pt">{md(texto)}</div>')
    c.sec(2, "Control final, antes de subir")
    c.add(lista(["Código de seis cifras con el prefijo P o S; nombres de archivo `report_`, `boards_`, `preview_`.",
                 "**Ningún nombre** en los materiales: textos, rótulos y metadatos (PDF y EXIF).",
                 "Exactamente 3 láminas A3 horizontales en un PDF de ≤ 5 MB; vista previa ≤ 1 MB; informe ≤ 3000 caracteres.",
                 "Cada afirmación del informe tiene su ficha o su ensayo; nada marcado como pendiente entra como hecho.",
                 "Revisión cruzada con los cinco criterios del jurado y la Mención Allievi."], numerada=True, clase="pendientes"))
    c.sec(3, "Lo que falta, y es del autor")
    c.add(lista(["Decidir la **visibilidad del repositorio** hasta el fallo (O7).",
                 "Hacer **E6a y E10a** con cinco personas, con la hoja de prueba.",
                 "Construir **E6** (el nodo 1:1, con un retazo de Nero Sahara Noir) y **E10** (tres tablas de 600 mm, una semana de uso).",
                 "Pedir la **muestra y la ficha del mármol** (EN 12372) y escribir a los organizadores: categoría y criterio de identidad.",
                 "**Registrarse** para tener la plantilla de las láminas, y pasar las láminas a ella.",
                 "Confirmar el **título** y la **frase** (O6).",
                 "Revisar **Bertonio 2011, p. 330**, y corregir el artículo si corresponde (O1).",
                 "Cotejar de primera mano la cita de **Johnson** (F15).",
                 "Reemplazar los renders de la lámina 3 por **fotos de las maquetas** cuando existan."], numerada=True, clase="pendientes"))
    c.sec(4, "Calendario")
    c.add(tabla(["semanas", "fechas", "movimiento", "hecho cuando…"], [
        ["1-2", "27 oct – 9 nov", "visibilidad · registro · consulta · retazos de piedra y madera", "hay plantilla, respuestas y retazos"],
        ["3-4", "10 – 23 nov", "construir y probar E6 y E10", "responden según su prerregistro"],
        ["5", "24 – 30 nov", "decidir F1 o B2, la frase y el nombre", "entrada en la bitácora"],
        ["6-10", "1 dic – 4 ene", "fotos de maqueta; ajustes; láminas sobre la plantilla", "láminas en borrador completo"],
        ["11-12", "5 – 18 ene", "informe en italiano o inglés; revisión cruzada", "todo en borrador final"],
        ["13", "19 – 25 ene", "control final y **subida**", "confirmación por correo"],
        ["14", "26 – 31 ene", "margen: no dejar la subida para el último día", "—"],
    ], cols=["mono", "mono", "", ""]))
    lb.add(apertura(lb, c, EPIGRAFES["8"]), c.cerrar())
    caps.append(c)

    # ---------------------------------------------------------- referencias, imágenes, índice, colofón
    lb.add(referencias(), lista_imagenes(lb), indice_final(), colofon())
    return caps


# ------------------------------------------------------------------ planas intermedias

def lamina_fuentes(lb):
    """Las fuentes, en sus páginas: la lámina de referencias del proyecto (dominio público) y las cinco por verificar."""
    items = [("recorte_bertonio_p069_chakhua_chhakhua.jpg", "F01", "Bertonio 1612/1879, II, p. 69 · *chakhua* / *chhakhua*"),
             ("bertonio_1612-1879_I_p153.jpg", "F03", "Bertonio, I, p. 153 · *cchacuru*, la cuña"),
             ("bertonio_1612-1879_I_p458.jpg", "F04", "Bertonio, I, p. 458 · trabarse de ambas partes"),
             ("semper_1879_derstil-II_p201.jpg", "F06", "Semper 1879, p. 201 · el *Gestell*"),
             ("semper_1879_derstil-II_p334.jpg", "F07", "Semper 1879, p. 334 · la estereotomía"),
             ("squier_1877_p280.jpg", "F08", "Squier 1877, p. 280 · Tiwanaku"),
             ("violletleduc_1873_mobilier-I_p257.jpg", "F09", "Viollet-le-Duc 1873, p. 257 · la mesa que se arma"),
             ("violletleduc_1873_mobilier-I_p264.jpg", "F10", "Viollet-le-Duc 1873, p. 264 · los *goussets*"),
             ("fpl_2010_woodhandbook_tabla13-5_p13-16.jpg", "F11", "FPL 2010, tabla 13-5 · el movimiento"),
             ("kessler_1919_marmoles_p11.jpg", "F13", "Kessler 1919, p. 11 · el mármol a flexión")]
    # retícula de lugares: 4 columnas de 47 mm por página, en las filas 2 a 5 (dos filas por imagen)
    paginas = []
    por_pagina = [items[:4], items[4:8], items[8:]]
    for k, grupo in enumerate(por_pagina):
        cont = ""
        for i, (arch, cod, pie) in enumerate(grupo):
            col = i % 4
            x = AIRE + col * 51
            y = fila(2)
            w, h = 47.0, filas(3)
            n, fid = lb.figura(pie, f"01_reunir/capturas/{arch}", "dominio")
            src = lb.imagen(CAP / arch, w, None, gris=True, igualar=True, ppp=300)
            cont += (f'<div class="contener" style="{en(x, y, w, h)}" id="{fid}"><img src="{src}" alt=""></div>'
                     f'<div class="pie" style="{en(x, fila(5) + 2, w)}"><b>{cod}</b> · fig. {n}<br>{md(pie)}</div>')
        if k == 2:
            # las cinco referencias visuales del borrador: autoría sin verificar
            cont += f'<div id="refs-visuales" style="{en(AIRE + 2 * 51, fila(2), 98, filas(1))}"></div>'
            for i in range(5):
                n, fid = lb.figura(f"referencia visual {i + 1:02d} del borrador", f"01_reunir/referencias_visuales/ref_0{i + 1}.jpg", "pendiente")
                x = AIRE + 2 * 51 + (i % 2) * 51
                y = fila(2) + (i // 2) * PASO
                cont += f'<div style="{en(x, y, 47, filas(1))}" id="{fid}">{vacio(f"ref. 0{i + 1} · fig. {n} · autoría sin verificar: no se reproduce", 47, filas(1))}</div>'
        rot = "reunir · las fuentes, en sus páginas · dominio público" if k < 2 else "reunir · las fuentes · en almagre, lo que espera un permiso"
        paginas.append((cont, rot))
    lado = ["izq", "der", "izq"]
    out = ""
    for (cont, rot), l in zip(paginas, lado):
        cab = f'<div class="rotulo" style="{en(AIRE, 12.5, 200)}">las fuentes, en sus páginas <span class="gris">· lámina de referencias</span></div>'
        out += plana(cab + cont + juntas(color="var(--papel)"), l, rotulo=rot)
    out += plana(f'<div class="texto-plana" style="{en(AIRE, fila(2), 124)}">'
                 + p("**La lámina de referencias** reúne solo lo que puede mostrarse: páginas de obras de dominio público, con su fuente y su página. Cada una hace un trabajo en el proyecto —ordenar, dar una técnica o abrir una pregunta— y su ficha está en el fichero (`01_reunir/fichero.md`).")
                 + p("Las cinco imágenes de referencia del borrador quedan como **lugares en almagre**: su autoría no está verificada. Se reemplazan cuando se sepa de quién son y se tenga permiso, o por fotos propias de las maquetas.")
                 + "</div>", "der")
    return out


def lamina_versiones(lb):
    """Catorce versiones: el índice de las versiones, como el de un catálogo de películas."""
    G1 = {"a_extremo": 450, "pie_x": 80}
    G2 = {"a_extremo": 450, "pie_x": 180}
    vs = [("V0", "lastre", versiones.v0, G1, "✗ E1, E5"), ("V1", "llave de piedra", versiones.v1, G1, "✗ E4"),
          ("V2", "hincada", versiones.v2, G1, "✗ E2, E4"), ("V3", "solo madera", versiones.v3, G2, "control"),
          ("V0b", "lastre asentado", versiones.v0b, G2, "◐ secundaria"), ("V4", "collar", versiones.v4, G2, "◐ → AB"),
          ("B1", "tablas posadas", versiones.b1, G2, "✗ E8, E9, E2b"), ("B2", "tablas clavijadas", versiones.b2, G2, "✓ salida"),
          ("AB", "síntesis", versiones.ab, G2, "→ F1 (E12)"), ("B3", "tabla de servicio", versiones.b3, G2, "◐ registrada"),
          ("F1", "punto fermo", versiones.f1, G2, "✓ final, it. 1")]
    paginas = [vs[:6], vs[6:]]
    out = ""
    for k, grupo in enumerate(paginas):
        cont = f'<div class="rotulo" style="{en(AIRE, 12.5, 200)}">las versiones, una al lado de otra <span class="gris">· alzado 1:40</span></div>'
        for i, (cod, nom, fab, geo, est) in enumerate(grupo):
            col, fil = i % 3, i // 3
            x = AIRE + col * 68
            y = fila(2) + fil * 2 * PASO
            svg = svg_a(miniatura(fab, geo), 62)
            n, fid = lb.figura(f"{cod} · {nom}", "instrumentos/mesa/versiones.py", "instrumento")
            no = est.startswith("✗")
            cont += (f'<div style="{en(x, y + 4, 62)}" id="{fid}">{svg}</div>'
                     f'<div class="rotulo" style="{en(x, y + filas(2) - 9, 62)}"><b style="font-size:9pt">{cod}</b> {esc(nom)}'
                     f'<br><span class="{"almagre" if no else "gris"}">{esc(est)}</span> · fig. {n}</div>')
        letra = "A" if k == 0 else "B"
        cont += f'<div class="grande" style="{en(PAG_W - AIRE - 30, 8, 30)};text-align:right">{letra}</div>'
        out += plana(cont + juntas(color="var(--papel)"), "izq" if k == 0 else "der",
                     rotulo="proponer · índice de versiones · ✗ descartada · ◐ registrada · ✓ vigente")
    return out


def lamina_junta(lb):
    """La junta en tres estaciones (E10a): húmedo, fabricación, seco."""
    tomas = [("junta_0p75.png", "0,75 mm · 13 % · húmedo"), ("junta_3p00.png", "3,0 mm · 8 % · fabricación"),
             ("junta_4p80.png", "4,8 mm · 4 % · seco")]
    cont = f'<div class="rotulo" style="{en(AIRE, 12.5, 200)}">la junta, en tres estaciones <span class="gris">· E10a</span></div>'
    for i, (arch, pie) in enumerate(tomas):
        y = fila(1 + 2 * i)
        h = filas(2)
        n, fid = lb.figura(f"la junta: {pie}", f"05_consolidar/renders/{arch}", "simulacion")
        cont += f'<div style="{en(0, y, 240, h)}" id="{fid}">{ren(lb, arch, 240, h, ppp=200)}</div>'
        cont += f'<div class="pie" style="{en(AIRE, y + h - 8, 120)};color:#f4f2ec">fig. {n} · simulación · {pie}</div>'
    izq = plana(cont, "izq")
    der = plana(f'<div class="texto-plana" style="{en(AIRE, fila(2), 124)}">'
                + p("**Una tabla se mueve sola; la mesa muestra la estación.** Con tablas de 164 mm y una junta de 3 mm al fabricar, la junta llega a 0,75 mm en el aire húmedo y a 4,8 mm en el seco (E2b). Las tres tomas son la misma cámara, la misma luz y la misma mesa: solo cambia la junta.")
                + p("La pregunta de E10a es si la junta **se lee como defecto o como intención**. Se responde con cinco personas y la hoja de prueba; E10, con tres tablas de 600 mm usadas una semana: migas, líquidos, un mantel. La lengüeta suelta debajo de la junta ya la cierra: las migas se quedan arriba.")
                + "</div>"
                + f'<div style="{en(AIRE, fila(5) - 2, 124)}">{svg_a(grafico_junta(), 110)}</div>', "der",
                rotulo="ensayar · la junta en tres estaciones · simulación: no es una foto")
    return izq + der


def lamina_nodo_real(lb):
    """El nodo a tamaño real: la sección horizontal y el alzado, a 1:1, en una doble página."""
    sol = construccion.modelo()
    d1 = pl.Dibujo(1)
    pl.ortografica(d1, sol, "planta", corte=-300, recorte=(690, -100, 930, 100))
    d2 = pl.Dibujo(1)
    pl.ortografica(d2, sol, "frente", recorte=(690, 200, 930, 400), ocultos=("travesaño", "llave", "vacios:montante"))
    import re as _re

    def fijo(svg, x0, y0):
        return _re.sub(r'viewBox="[^"]+" width="[^"]+" height="[^"]+"', f'viewBox="{x0} {y0} 240 200" width="240mm" height="200mm"', svg, 1)
    s1 = fijo(d1.svg(0), 690, -100)
    s2 = fijo(d2.svg(0), 690, -400)
    n1, f1 = lb.figura("el nodo, sección horizontal a 1:1", "instrumentos/mesa/planos.py", "instrumento")
    n2, f2 = lb.figura("el nodo, alzado a 1:1", "instrumentos/mesa/planos.py", "instrumento")
    izq = plana(f'<div style="{en(0, 0, 240, 200)}" id="{f1}">{s1}</div>'
                f'<div class="pie" style="{en(AIRE, 186, 200)}">fig. {n1} · instrumento · el nodo a tamaño real, en sección horizontal por el eje del travesaño. '
                f'montante (en testa), espiga (a lo largo), collar de piedra (negro), llave (en testa)</div>', "izq")
    der = plana(f'<div style="{en(0, 0, 240, 200)}" id="{f2}">{s2}</div>'
                f'<div class="pie" style="{en(AIRE, 186, 200)}">fig. {n2} · instrumento · el nodo a tamaño real, en alzado. '
                f'a trazos, la espiga dentro del montante y del collar, y la llave dentro de la espiga. la piedra mide 70 × 110 × 150 mm</div>', "der",
                rotulo="la mesa · el nodo a tamaño real · 1:1")
    return izq + der


def lamina_renders(lb):
    """La simulación: la lámina 3 antes de las fotos de maqueta."""
    n, fid = lb.figura("F1, vista general a sangre", "05_consolidar/renders/general_F1.png", "simulacion")
    src = lb.imagen(REN / "general_F1.png", 480, 200, ppp=220, nombre="general_F1_doble.jpg") if (REN / "general_F1.png").exists() else ""
    pie = (f'<div class="pie" style="{en(AIRE, 188, 220)}">fig. {n} · simulación · F1, Cycles. '
           f'no es una foto: la lámina 3 la reemplaza por las fotos de las maquetas cuando existan</div>')
    doble = (plana(f'<div style="{en(0, 0, 480, 200)}" id="{fid}"><img src="{src}" alt=""></div>' + pie, "izq")
             + plana(f'<div style="{en(-240, 0, 480, 200)}"><img src="{src}" alt=""></div>', "der"))
    tomas = [("nodo_F1.png", "el nodo: la espiga atraviesa la piedra"), ("cabezal_F1.png", "las cuñas asoman por el cabezal"),
             ("frente_F1.png", "de frente"), ("planta_F1.png", "desde arriba: seis tablas, cinco juntas")]
    cont = f'<div class="rotulo" style="{en(AIRE, 12.5, 200)}">la mesa, simulada <span class="gris">· lámina 3, antes de las maquetas</span></div>'
    pos = [(AIRE, fila(2), 100, filas(3)), (AIRE + 104, fila(2), 100, filas(3)), (AIRE, fila(5), 100, filas(2)), (AIRE + 104, fila(5), 100, filas(2))]
    for (arch, pie_), (x, y, w, h) in zip(tomas, pos):
        if not (REN / arch).exists():
            continue
        n, fid = lb.figura(pie_, f"05_consolidar/renders/{arch}", "simulacion")
        src = lb.imagen(REN / arch, w, h, ppp=240)
        cont += (f'<div style="{en(x, y, w, h)}" id="{fid}"><img src="{src}" alt=""></div>'
                 f'<div class="pie" style="{en(x + 2, y + h - 6, w - 4)};color:#f4f2ec">fig. {n} · {esc(pie_)}</div>')
    ultima = plana(cont, "izq", rotulo="la mesa · simulación")
    n6, f6 = lb.figura("foto de la maqueta de E6 (el nodo 1:1)", "—", "pendiente")
    n10, f10 = lb.figura("foto de la maqueta de E10 (tres tablas)", "—", "pendiente")
    hueco = plana(f'<div class="rotulo" style="{en(AIRE, 12.5, 200)}">las maquetas <span class="gris">· E6 y E10</span></div>'
                  f'<div style="{en(AIRE, fila(2), 100, filas(3))}" id="{f6}">{vacio(f"fig. {n6} · E6 · el nodo a 1:1: montante, espiga, collar de Nero Sahara Noir y llave. la foto va aquí", 100, filas(3))}</div>'
                  f'<div style="{en(AIRE + 104, fila(2), 100, filas(3))}" id="{f10}">{vacio(f"fig. {n10} · E10 · tres tablas de 600 mm después de una semana de uso. la foto va aquí", 100, filas(3))}</div>'
                  f'<div class="texto-plana" style="{en(AIRE, fila(5) + 2, 204)}">'
                  + p("Un render no reemplaza a la maqueta. Estos dos lugares esperan las fotos que deciden la propuesta: la lectura del collar (E6) y el uso de la junta (E10).")
                  + "</div>", "der", rotulo="la mesa · pendiente: la mano")
    return doble + ultima + hueco


def montaje_figura(lb, planos):
    celdas = ""
    for k in range(1, 8):
        dib, titulo, _ = planos[f"montaje_{k}"]
        svg = svg_a(dib.svg(1.0), 39)
        celdas += (f'<div style="display:inline-block;vertical-align:top;width:40mm;margin:0 0.8mm 2.5mm 0">{svg}'
                   f'<div style="font:400 5.8pt/2.9mm var(--mono);margin-top:1mm"><b>{k}</b> · {esc(lf.PASOS[k])}</div></div>')
    return fig(lb, f'<div style="width:124mm">{celdas}</div>', "montaje en siete pasos", "instrumentos/mesa/laminas_f1.py",
               "instrumento", "Armar la mesa: en almagre, lo que entra en cada paso. Se desarma al revés.")


def guion():
    entradas = [
        ("12:10 · 7e6165b", "1 · reunir", "el encargo", "Se leen las bases. El concurso exige proyectos inéditos y anónimos; el repositorio es público.", "no publicar el diseño hasta que el autor decida la visibilidad"),
        ("12:10", "2 · reunir", "las fuentes", "Bertonio, Semper, Squier, Viollet-le-Duc, el Wood Handbook y Kessler, con página y captura. Monoskop no responde.", "desarmar"),
        ("12:10", "3 · contrastar con la fuente", "E5", "*Chakhua* y *chhakhua* son dos entradas. El borrador las leía como una.", "cambiar la pregunta: la unión, no el lastre"),
        ("12:10 · 7e6165b", "4 · desarmar y proponer", "K1-K10", "Las referencias tiran a la masa; el concurso, a la madera. Cuatro versiones. Los umbrales se fijan antes del instrumento.", "ensayar"),
        ("12:27 · d8764ea", "5 · ensayar", "ronda 1", "E1: 9,9 MPa en la barra. E2: hay que acuñar. E3: el pie de 180 mm. E4: la llave de mármol no cabe.", "descartar V0, V1 y V2; derivar V0b y V4"),
        ("12:27", "6 · ensayar", "ronda 2", "V4 cumple; la piedra trabaja a 0,08 MPa. El control V3 cumple lo mismo sin piedra.", "modificar el concepto: se retira «la gravedad de la piedra sostiene la ligereza del armazón»"),
        ("12:28 · 38a6dc6", "7 · retorno", "el autor", "El autor advierte que predeterminó el concepto. Todas las versiones discutían dónde va la piedra.", "abrir la propuesta B, con su prerregistro"),
        ("12:34 · 24ecdaf", "8 · proponer y ensayar B", "rondas 3-4", "B1 falla E8, E9 y E2b. La cuña vuelve por una razón propia. B2 cumple sin piedra; AB, el tablero de B2 con el collar, cumple K1-K5.", "A y B son compatibles: no cerrar todavía"),
        ("12:43 · c7b8cbb", "9 · reunir de nuevo", "E7", "Porada ya junta madera y mármol. El jurado premia componentes con individualidad y el detalle precioso de la unión.", "modificar el argumento; nace B3"),
        ("12:54 · 26124a8", "10 · consolidar una herramienta", "Blender", "Un solo árbol de Geometry Nodes genera B2, AB, B3 y la familia; renders en la nube con GitHub Actions.", "E6a y E10a con cinco personas"),
        ("13:56 · 924e6a0", "11 · reunir y contrastar", "materiales bolivianos", "El nogal de los Yungas es *J. boliviana*; la piedra de Comanche, granito. E11: la cuña por gravedad no alcanza.", "modificar el filtro mecánico; descartar el bloqueo por gravedad"),
        ("16:43 · f3f5ad9", "12 · decidir", "F1", "Al pasar AB a planos, la clavija de las tablas centrales caía dentro del montante (E12).", "conservar AB; modificar la cuña; descartar B3 como final"),
        ("17:10 · 09ad171", "13 · consolidar", "planos", "Al dibujar la sección, la clavija exterior asomaba 3 mm por el cabezal.", "cabezal de 900 mm; planos, renders, láminas y este libro"),
    ]
    h = ['<div class="guion">']
    for tc, mov, tema, accion, dec in entradas:
        h.append(f'<p class="escena">{esc(mov)} · {esc(tema)}</p>'
                 f'<span class="margen"><span class="tc">[ {esc(tc)} ]</span></span>'
                 f'<p class="accion">{md(accion)}</p>'
                 f'<p class="quien">decisión</p><p class="dice decision">{md(dec)}</p>')
    h.append("</div>")
    return "".join(h)


def referencias():
    grupos = {
        "fuentes primarias (dominio público)": [
            "Bertonio, Ludovico (1612). *Vocabulario de la lengua aymara*. Juli. Facsímil de Julius Platzmann, Leipzig: Teubner, 1879. IA `vocabulariodela02bertgoog`, `vocabulariodela03bertgoog`.",
            "Forest Products Laboratory (2010). *Wood Handbook: Wood as an Engineering Material*. FPL-GTR-190. Madison: USDA.",
            "Kessler, D. W. (1919). *Physical and Chemical Tests on the Commercial Marbles of the United States*. Technologic Papers of the Bureau of Standards 123. Washington.",
            "Semper, Gottfried (1851). *Die vier Elemente der Baukunst*. Braunschweig: Vieweg.",
            "Semper, Gottfried (1879). *Der Stil in den technischen und tektonischen Künsten*, II, 2.ª ed. Múnich: Bruckmann.",
            "Squier, E. G. (1877). *Peru: Incidents of Travel and Exploration in the Land of the Incas*. Nueva York: Harper & Brothers.",
            "Viollet-le-Duc, Eugène (1873 [1858]). *Dictionnaire raisonné du mobilier français*, I. París: Morel."],
        "de segunda mano": [
            "Frampton, Kenneth (1995). *Studies in Tectonic Culture*. Cambridge (Mass.): MIT Press. Citado a través de *Cosecha de piedras*.",
            "Johnson, Galen A. (2007). «Forest and Philosophy: Toward an Aesthetics of Wood». *Environmental Philosophy* 4 (1-2): 59-75. Citado según el cotejo de *Contenida*."],
        "el concurso y los precedentes": [
            "Porada Arredi y POLI.design (2026). *Porada International Design Award 2026. Bando*. Italiano e inglés.",
            "POLI.design (2017, 2018). *Compendio dei vincitori*. Porada International Design Award.",
            "Porada. *Tavoli* y *Materiali e finiture*. porada.it, leído el 26-10-2026.",
            "Wood Awards (2016). *Planks*, de Max Lamb."],
        "materiales": [
            "GBIF. *Juglans boliviana*, *Juglans neotropica*: registros, sinónimos y categoría UICN.",
            "Gobierno Autónomo Departamental de La Paz (2012). Ley Departamental n.º 16 (piedra granito de Comanche). Lexivox.",
            "Paredes-Villanueva, K., et al. (2013). «Growth Rate and Climatic Response of *Machaerium scleroxylon*». *Tree-Ring Research* 69 (2)."],
        "propias e inéditas (no se reproducen)": [
            "*Cosecha de piedras*. Artículo del autor, en desarrollo.",
            "*Contenida: acciones para componer una voz*. Libro de trabajo del autor, octubre de 2026."],
    }
    h = ['<section class="capitulo" data-corrida="referencias" id="referencias"><div class="refs">']
    for g, items in grupos.items():
        h.append(f"<h3>{esc(g)}</h3>" + "".join(f"<p>{md(i)}</p>" for i in items))
    h.append("</div></section>")
    return "".join(h)


def lista_imagenes(lb):
    filas_ = "".join(f'<tr><td><a class="pag" href="#{f["id"]}">%%P:{f["id"]}%%</a></td><td>{f["n"]}</td><td>{md(f["que"])}</td>'
                     f'<td class="ruta">{esc(f["origen"])}</td><td>{esc(f["estado"].replace("simulacion", "simulación").replace("dominio", "dominio público"))}</td></tr>'
                     for f in lb.figuras)
    return ('<section class="capitulo" data-corrida="las imágenes" id="imagenes"><div class="texto">'
            + p("Cada figura con su página, de dónde sale en el repositorio y su estado.")
            + f'<table class="lista-imagenes"><thead><tr><th>pág.</th><th>fig.</th><th>qué es</th><th>de dónde sale</th>'
              f'<th>estado</th></tr></thead><tbody>{filas_}</tbody></table></div></section>')


def indice_final():
    entradas = {
        "ensayos": [("E1 · la piedra como viga", "s-5-2"), ("E2 · el movimiento", "s-5-2"), ("E3 · el vuelco", "s-5-2"),
                    ("E4 · la unión", "s-5-2"), ("E5 · la palabra", "s-2-1"), ("E6, E10 · las maquetas", "s-5-5"),
                    ("E6a, E10a · los renders", "s-5-5"), ("E7 · la originalidad", "s-2-7"), ("E8 · la flecha", "s-5-3"),
                    ("E9 · el vuelco de una tabla", "s-5-3"), ("E2b · las juntas", "s-5-3"), ("E11 · la cuña por gravedad", "s-5-4"),
                    ("E12 · las interferencias", "s-5-4")],
        "fuentes": [("F01-F04 · Bertonio", "s-2-1"), ("F05-F07 · Semper", "s-2-2"), ("F08 · Squier", "s-2-3"),
                    ("F09-F10 · Viollet-le-Duc", "s-2-4"), ("F11-F12 · Wood Handbook", "s-2-5"), ("F13 · Kessler", "s-2-5"),
                    ("F14 · Cosecha de piedras", "s-3-2"), ("F15 · Johnson", "s-2-6"), ("F16 · Frampton", "s-2-9")],
        "criterios y objeciones": [("K1-K10 · criterios", "s-3-6"), ("O1-O7 · objeciones", "s-3-7"), ("C1-C8 · conflictos", "s-3-5")],
        "versiones": [("V0-V4 · propuesta A", "s-4-1"), ("B1-B3 · propuesta B", "s-4-3"), ("AB · la síntesis", "s-4-4"),
                      ("F1 · la propuesta final", "s-6-2"), ("F1 · planos", "s-7-4"), ("F1 · despiece", "s-7-5")],
    }
    h = ['<section class="capitulo" data-corrida="índice" id="indice-final"><div class="indice-final">']
    for g, items in entradas.items():
        h.append(f'<div class="letra">{esc(g)}</div>')
        h += [f'<div class="item"><span class="pags"><a class="pag" href="#{i}">%%P:{i}%%</a></span><span>{md(t)}</span></div>' for t, i in items]
    h.append("</div></section>")
    return "".join(h)


def colofon():
    return ('<section class="capitulo" data-corrida="colofón" id="colofon"><div class="texto colofon">'
            + p("**El sistema.** La doble página es el tablero de la mesa a 1:5: 480 × 200 mm. Las seis filas de la retícula son las seis tablas, y la junta de 3 mm, a escala, separa lo que se apila. El lomo es el apoyo central; en las planas, el caballete cae a 90 mm del borde. La interlínea es la octava parte de una tabla. Las palabras de apertura las cortan las juntas; el punto final es un rectángulo negro con la proporción del collar, y es lo único que la junta no corta.")
            + p("**Las letras.** Newsreader (Production Type) e IBM Plex Mono (IBM), las dos con licencia SIL Open Font License. **Las tintas**: tinta y almagre, el rojo del cordel con que el carpintero marca antes de cortar; en este libro marca lo prerregistrado y lo pendiente.")
            + p("**Las herramientas.** El texto se compone en HTML y CSS y pasa a PDF con Vivliostyle (CSS Paged Media sobre Chromium). Los planos los dibuja el código del proyecto desde su modelo constructivo; los gráficos, desde los resultados de los ensayos; los renders, Blender con Cycles, desde un árbol de Geometry Nodes, también en la nube. Se arma con `python3 05_consolidar/editorial/armar.py`.")
            + p("**Asistencia de inteligencia artificial.** El instrumento de cálculo, el modelo constructivo, los planos, los renders, el sistema editorial y los textos de este libro los propuso y los escribió un asistente de inteligencia artificial, a partir de los documentos del proyecto, de las decisiones del autor y de sus referencias, entre ellas el libro de *Contenida*. Las decisiones que este libro deja abiertas son del autor.")
            + p("**Sin nombre.** El concurso pide anonimato hasta el fallo, el 26 de febrero de 2027. Los shakers prohibían firmar los muebles (Johnson, p. 72); aquí es una regla del concurso, no una ética, y dura lo que dura el concurso.")
            + "</div></section>")
