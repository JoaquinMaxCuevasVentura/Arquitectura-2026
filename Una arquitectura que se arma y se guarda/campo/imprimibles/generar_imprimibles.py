"""Genera las hojas del campo para imprimir en A4.

    hoja_de_informacion.pdf  para dejar a quien arma el puesto (protocolo, sección 3)
    ficha_de_ciclo.pdf       para llenar a mano en cada ciclo (versión impresa de ficha_de_ciclo.md)

Uso: python3 "campo/imprimibles/generar_imprimibles.py"  (necesita Chromium; ruta en la variable CHROME)
Los textos están aquí: para corregirlos, editar este archivo y volver a generar.
Las hojas llenas no se suben al repositorio: van a campo/privado/ o a Drive.
"""
import os
import subprocess
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome")
FECHA = "26 de octubre de 2026"

TINTA = "#2b2620"
GRIS = "#7a7166"
ROJO = "#c0262d"
SERIF = "'Liberation Serif', 'DejaVu Serif', serif"
SANS = "'DejaVu Sans', 'Liberation Sans', sans-serif"

VERBOS = ["descargar", "desatar", "armar", "apoyar", "calzar", "atar", "tensar", "colgar", "cubrir", "desplegar",
          "apilar", "ordenar", "señalar", "delimitar", "limpiar", "recoger", "plegar", "enfardar", "cargar",
          "encadenar", "ch'allar"]
CATEGORIAS = ["apoyo", "cubierta", "masa", "boca", "borde", "guardado", "costumbre y rito", "otra"]

ESTILO = f"""
@page {{ size: A4; margin: 14mm 15mm 13mm 15mm; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; color: {TINTA}; font-family: {SANS}; font-size: 10pt; line-height: 1.35; background: #fff; }}
h1 {{ font-family: {SERIF}; font-size: 22pt; margin: 0 0 1mm; line-height: 1.1; }}
h2 {{ font-family: {SERIF}; font-size: 13pt; margin: 4mm 0 1.5mm; }}
.sub {{ color: {GRIS}; font-style: italic; margin: 0 0 3mm; }}
.pagina {{ break-after: page; }}
.pagina:last-child {{ break-after: auto; }}
.pie {{ color: {GRIS}; font-size: 7.5pt; margin-top: 3mm; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 0.6pt solid {TINTA}; padding: 0 1.5mm; vertical-align: top; }}
th {{ font-size: 8pt; text-align: left; background: #efebe4; padding: 1mm 1.5mm; }}
.linea {{ border-bottom: 0.6pt solid {TINTA}; height: 5.7mm; }}
.caja {{ display: inline-block; width: 3.4mm; height: 3.4mm; border: 0.7pt solid {TINTA}; vertical-align: -0.5mm;
         margin: 0 1mm 0 2.5mm; }}
.raya {{ display: inline-block; border-bottom: 0.6pt solid {TINTA}; min-width: 18mm; height: 4mm; }}
"""


def documento(titulo, cuerpo, extra=""):
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{titulo}</title>'
            f"<style>{ESTILO}{extra}</style></head><body>{cuerpo}</body></html>")


def caja(texto):
    return f'<span style="white-space:nowrap"><span class="caja"></span>{texto}</span>'


def raya(mm=18):
    return f'<span class="raya" style="min-width:{mm}mm"></span>'


# ---------------------------------------------------------------- hoja de información

def hoja_de_informacion():
    extra = f"""
body {{ font-size: 11.5pt; line-height: 1.38; }}
h1 {{ font-size: 24pt; }}
h2 {{ font-size: 13.5pt; margin: 3.4mm 0 0.8mm; }}
ul {{ margin: 0; padding-left: 6mm; }}
li {{ margin: 0.6mm 0; }}
p {{ margin: 0 0 1.5mm; }}
.acuerdo {{ border: 1.2pt solid {TINTA}; padding: 2.5mm 4mm; margin-top: 4mm; font-size: 11pt; }}
.acuerdo h2 {{ margin-top: 0; }}
.acuerdo p {{ margin: 1.3mm 0; }}
"""
    cuerpo = f"""
<div class="pagina">
<h1>Cómo se arma un puesto</h1>
<p class="sub">Hoja de información para quien arma el puesto. Esta hoja es para usted.</p>

<h2>¿De qué se trata?</h2>
<p>Estoy estudiando cómo se arma y se guarda un puesto de venta. Armarlo cada día es un saber: dónde apoyarse,
cómo cubrirse, cómo ordenar la mercancía, cómo guardar todo en la tarde. Quiero aprenderlo mirando y
conversando, para escribir un artículo en una revista de arquitectura de la Universidad de Chile.</p>

<h2>¿Qué haría?</h2>
<ul>
<li>Mirar cómo arma el puesto en la mañana y cómo lo guarda en la tarde, unos tres días.</li>
<li>Tomar fotos del puesto y de las manos. <b>Nunca de las caras.</b></li>
<li>Medir el puesto con una cinta.</li>
<li>Conversar con usted después, cuando tenga tiempo. Nunca mientras vende.</li>
</ul>

<h2>¿Qué no haría?</h2>
<ul>
<li>No anoto su nombre. Su puesto tiene un código, por ejemplo «P1».</li>
<li>No pregunto ni anoto cuánto paga, ni sus acuerdos con la alcaldía o con la asociación.</li>
<li>No estorbo la venta ni el paso de la gente.</li>
</ul>

<h2>Sus palabras</h2>
<p>Si algo que usted dice puede ir en el artículo, se lo leo en voz alta y le pido permiso. Sin su permiso,
no va. Si va, va sin su nombre: por ejemplo, «vendedora de verduras, zona norte».</p>

<h2>El dibujo</h2>
<p>En unas dos semanas le traigo un dibujo de su puesto para que me diga si está bien o qué falta.
El dibujo es para usted.</p>

<h2>Puede decir que no</h2>
<p>Puede decir que no, o pedirme que pare cuando quiera, sin dar razones. Si me lo pide, borro lo que
ya anoté y las fotos.</p>

<h2>Quién hace el estudio</h2>
<p>Joaquin Max Cuevas Ventura. Contacto: {raya(88)}</p>

<div class="acuerdo">
<h2>Lo que acordamos</h2>
<p>{caja("Puede mirar cómo armo y guardo el puesto.")}</p>
<p>{caja("Puede tomar fotos del puesto y de las manos, sin caras.")}</p>
<p>{caja("Podemos conversar.")}</p>
<p>No quiero que se anote ni se fotografíe: {raya(85)}</p>
<p>Fecha: {raya(40)} &nbsp;&nbsp; Código del puesto: {raya(20)}</p>
</div>
<p class="pie">Estudio «Una arquitectura que se arma y se guarda», La Paz. Versión del {FECHA}.</p>
</div>
"""
    return documento("Hoja de información", cuerpo, extra)


# ---------------------------------------------------------------- ficha de ciclo

def filas_operaciones(desde, hasta, alto="7.6mm"):
    filas = []
    for n in range(desde, hasta + 1):
        filas.append(f'<tr style="height:{alto}"><td class="n">{n}</td>' + "<td></td>" * 8 + "</tr>")
    return "\n".join(filas)


def tabla_operaciones(desde, hasta):
    return f"""
<table class="ops">
<colgroup><col style="width:6mm"><col style="width:13mm"><col style="width:11mm"><col style="width:20mm">
<col style="width:27mm"><col style="width:24mm"><col style="width:20mm"><col style="width:10mm"><col></colgroup>
<tr><th>#</th><th>Hora</th><th>Quién</th><th>Verbo</th><th>Elemento</th><th>Apoyo usado</th><th>Categoría</th>
<th>F/P</th><th>Notas</th></tr>
{filas_operaciones(desde, hasta)}
</table>"""


def encabezado(n, total):
    return (f'<div class="enc"><b>Ficha de ciclo</b> &nbsp; Puesto P{raya(8)} &nbsp; Ciclo C{raya(8)} &nbsp; '
            f'Fecha {raya(24)}<span class="hoja">hoja {n} de {total}</span></div>')


def ficha_de_ciclo():
    extra = f"""
.enc {{ font-size: 9.5pt; border-bottom: 1.2pt solid {TINTA}; padding-bottom: 1.5mm; margin-bottom: 3mm; }}
.enc .hoja {{ float: right; color: {GRIS}; }}
.datos td {{ height: 8.2mm; vertical-align: middle; font-size: 9.5pt; }}
.datos td.r {{ width: 33mm; font-weight: bold; background: #f7f4ef; }}
.ops td.n {{ font-size: 8pt; color: {GRIS}; text-align: right; vertical-align: middle; }}
.leyenda {{ font-size: 8pt; margin-top: 2.5mm; line-height: 1.45; }}
.croquis {{ border: 0.8pt solid {TINTA}; height: 84mm; margin-bottom: 3mm; position: relative;
           background-image: linear-gradient(#d9d3c9 0.4pt, transparent 0.4pt),
                             linear-gradient(90deg, #d9d3c9 0.4pt, transparent 0.4pt);
           background-size: 5mm 5mm; }}
.croquis span {{ position: absolute; left: 2mm; top: 1.5mm; background: #fff; padding: 0 1.5mm; font-size: 9pt; }}
.medidas td {{ height: 7.6mm; vertical-align: middle; font-size: 9.5pt; }}
.medidas td.r {{ width: 82mm; }}
.preg {{ font-size: 9.5pt; margin: 1.3mm 0 0; }}
.preg .origen {{ float: right; color: {GRIS}; font-size: 8.5pt; }}
.frases td {{ height: 8.5mm; }}
"""
    total = 4
    datos = f"""
<table class="datos">
<tr><td class="r">Tipo de día</td><td>{caja("común")}{caja("feria")}{caja("otro:")} {raya(30)}</td></tr>
<tr><td class="r">Clima</td><td>{caja("sol")}{caja("nubes")}{caja("lluvia")}{caja("granizo")}{caja("viento")}
 &nbsp; temperatura aprox. {raya(14)}</td></tr>
<tr><td class="r">Consentimiento</td><td>oral, fecha {raya(22)} &nbsp; no registrar: {raya(70)}</td></tr>
<tr><td class="r">Personas</td><td>R {raya(30)} &nbsp; A1 {raya(26)} &nbsp; A2 {raya(26)}</td></tr>
<tr><td class="r">Montaje</td><td>llega el primer bulto {raya(16)} &nbsp; listo para vender {raya(16)}</td></tr>
<tr><td class="r">Desmontaje</td><td>empieza {raya(16)} &nbsp; se va el último bulto {raya(16)}</td></tr>
<tr><td class="r">Fotos</td><td>intervalo {raya(10)} s &nbsp; punto fijo {raya(40)} &nbsp; carpeta {raya(28)}</td></tr>
<tr><td class="r">La noche</td><td>se queda en el lugar: {raya(46)}<br>el resto duerme en
 {caja("casa")}{caja("depósito propio")}{caja("prestado")}{caja("alquilado")}{caja("vehículo")}
 <span style="color:{GRIS}">(sin montos)</span></td></tr>
</table>"""
    leyenda = (f'<div class="leyenda"><b>Verbos</b> (protocolo, sección 5; uno por fila): {" · ".join(VERBOS)}.<br>'
               f'<b>Categorías:</b> {" · ".join(CATEGORIAS)}. &nbsp; <b>F/P:</b> agarre de fuerza o de precisión. '
               f'&nbsp; <b>Quién:</b> R responsable; A1, A2… quienes ayudan.</div>')
    medidas = [("Planta ocupada armado (m²)", ""), ("Bultos guardados: número, medidas, peso aproximado", ""),
               ("Altura de la cubierta (cm)", ""), ("Altura de la boca, donde se cobra y se entrega (cm)", ""),
               ("Alcance sin moverse (cm)", ""), ("Distancia a la circulación (cm)", ""),
               ("Pendiente de la vereda o la calzada", ""), ("Duración del montaje y del desmontaje (min)", "")]
    tabla_medidas = "<table class='medidas'>" + "".join(
        f"<tr><td class='r'>{m}</td><td></td></tr>" for m, _ in medidas) + "</table>"
    preguntas = ["Aprendizaje: ¿quién le enseñó? ¿Qué hacía al principio? Si lo heredó, ¿lo arma como quien se lo dejó?",
                 "Lo primero que arma, y por qué eso primero",
                 "Lo que cambia con lluvia, viento o mucho sol",
                 "¿Dónde duerme el puesto? ¿A qué distancia?",
                 "¿Por qué no lo deja armado de noche?",
                 "Acuerdos con la tienda de atrás o con los vecinos",
                 "Cambios desde que empezó, y por qué",
                 "Si hubo intervención: ¿qué hacía antes que ya no hace?",
                 "Lo que cambiaría del puesto",
                 "Lo que se hace siempre, aunque no haga falta, y en qué momento del armado"]
    conversacion = "".join(
        f'<p class="preg"><b>{i}.</b> {p}<span class="origen">origen: P · V · M · A</span></p>'
        f'<div class="linea"></div><div class="linea"></div>' for i, p in enumerate(preguntas, 1))
    cuerpo = f"""
<div class="pagina">
{encabezado(1, total)}
<h2 style="margin-top:0">Datos</h2>
{datos}
<h2>Operaciones, en orden</h2>
{tabla_operaciones(1, 14)}
<p class="pie">Versión del {FECHA}. La ficha llena va a campo/privado/ o a Drive, nunca al repositorio; las operaciones
pasan el mismo día a registro_de_operaciones.csv, solo con códigos.</p>
</div>

<div class="pagina">
{encabezado(2, total)}
<h2 style="margin-top:0">Operaciones (sigue)</h2>
{tabla_operaciones(15, 43)}
{leyenda}
</div>

<div class="pagina">
{encabezado(3, total)}
<h2 style="margin-top:0">Croquis</h2>
<div class="croquis"><span>1. El lugar vacío: apoyos prestados (fachada, reja, poste, bordillo, árbol, vecino) y huellas
(ganchos, argollas, clavos, marcas). Flecha de la circulación y de la pendiente.</span></div>
<div class="croquis"><span>2. El puesto armado, con cotas en cm. Marcar la boca y el borde.</span></div>
<h2>Mediciones</h2>
{tabla_medidas}
</div>

<div class="pagina">
{encabezado(4, total)}
<h2 style="margin-top:0">Conversación</h2>
<p style="font-size:8.5pt;color:{GRIS};margin:0">Después del ciclo, nunca durante el trabajo. Palabras textuales «entre
comillas»; paráfrasis sin comillas. Origen de cada razón (H3): <b>P</b> propia o aprendida · <b>V</b> acordada con
vecinos · <b>M</b> impuesta por el municipio · <b>A</b> impuesta por la asociación.</p>
{conversacion}
<h2>Frases para citar</h2>
<p style="font-size:8.5pt;color:{GRIS};margin:0 0 1.5mm">Se leen en voz alta a quien las dijo y se pide permiso para
publicarlas con esas palabras (analisis/02, sección 10).</p>
<table class="frases">
<tr><th style="width:6mm">#</th><th>Frase textual</th><th style="width:20mm">¿Leída en voz alta?</th>
<th style="width:26mm">¿Permiso? Fecha</th><th style="width:20mm">¿Epígrafe?</th></tr>
<tr><td>1</td><td></td><td></td><td></td><td></td></tr>
<tr><td>2</td><td></td><td></td><td></td><td></td></tr>
</table>
<h2>Dudas y sorpresas</h2>
<div class="linea"></div><div class="linea"></div>
</div>
"""
    return documento("Ficha de ciclo", cuerpo, extra)


def render(nombre, html):
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / f"{nombre}.html"
        f.write_text(html, encoding="utf8")
        subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={BASE / (nombre + '.pdf')}", f.as_uri()], check=True, capture_output=True)
    print(f"{nombre}.pdf")


def main():
    render("hoja_de_informacion", hoja_de_informacion())
    render("ficha_de_ciclo", ficha_de_ciclo())


if __name__ == "__main__":
    main()
