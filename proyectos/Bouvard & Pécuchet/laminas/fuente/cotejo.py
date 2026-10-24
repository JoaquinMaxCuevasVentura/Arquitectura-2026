"""Cotejo: la Tabla 1 del borrador, el párrafo de los géneros frase por frase.

Uso: python3 cotejo.py carpeta_fuentes salida.html   (hoja de trabajo)
     python3 cotejo.py --tabla                       (la tabla del borrador, en Markdown)

La hoja de trabajo es un HTML de una página A4 apaisada, con las fuentes
incrustadas; render.js lo pasa a PDF. Lleva además la columna de la máquina y
los pasos intermedios de Flaubert (nota de lectura y borrador), que la tabla
del borrador deja para el texto. Las citas de Boitard están verificadas en la
imagen del facsímil (Internet Archive, A039a018); las de Flaubert, en la
edición de 1910.
En la columna de Flaubert: «c» son palabras de Boitard (gris en la hoja,
cursiva en la tabla), «n» las de Flaubert, «x» lo que reemplaza o agrega dentro
de una frase copiada (entre corchetes) y «e» un corte ([…]).
"""
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

from svg import B, F, G, NUMERO, esc, estilo_fuentes  # noqa: E402

GRIS_COPIA = "#8f8f8f"

FILAS = [
    {
        "genero": "Los géneros",
        "pags": "F 54 · B 21, 56",
        "boitard": "«D'autres auteurs ont encore inventé plusieurs genres de jardins» (21).",
        "flaubert": [("L'auteur", "x"), (" les divise en une infinité de ", "n"), ("genres", "c"), (".", "n")],
        "cadena": "nota: «on a inventé des genres» (f. 8) · borrador: «L'auteur les divise par genres, ou scènes» (f. 169)",
        "afuera": "«Je n'ai donc pu admettre des genres fondés sur des nuances si fugitives» (56).",
    },
    {
        "genero": "El exvoto",
        "pags": "F 54 · B 72",
        "boitard": "«une fontaine dédiée à une madone […], un ex-voto marquant la place où "
                   "un chevalier est tombé sous le fer d'un assassin» (72).",
        "flaubert": [("[…]", "e"), (" et un « ", "n"), ("ex-voto", "c"), (" ", "n"), ("à la vierge", "x"), (", ", "n"),
                     ("indiquant", "x"), (" ", "n"), ("la place où un", "c"), (" ", "n"), ("seigneur", "x"),
                     (" ", "n"), ("est tombé sous le fer d'un assassin", "c"), (" ».", "n")],
        "cadena": "nota: «exvoto à une madone marquant la place où un chevalier est tombé…» (f. 8v)",
        "afuera": "«Dans un site très-pittoresque, montagneux» (72).",
    },
    {
        "genero": "El exótico",
        "pags": "F 54 · B 63, 65",
        "boitard": "«La scène exotique peut donc avoir pour but de faire naître d'agréables souvenirs "
                   "à un colon ou à un voyageur»; en el borde de la lámina, «un cierge du Pérou» (63).",
        "flaubert": [("[…]", "e"), (" le genre ", "n"), ("exotique", "c"), (", en plantant des ", "n"), ("cierges du Pérou", "c"),
                     (" « ", "n"), ("pour", "x"), (" ", "n"), ("faire naître", "c"), (" ", "n"), ("des", "x"),
                     (" ", "n"), ("souvenirs à un colon ou à un voyageur", "c"), (" ».", "n")],
        "cadena": "nota: todavía «d'agréables souvenirs» (f. 8)",
        "afuera": "«ce genre de tableau ne peut exister chez nous que pendant quatre ou cinq mois de "
                  "l'année au plus» (65).",
    },
    {
        "genero": "El terrible",
        "pags": "F 54 · B 19–20",
        "boitard": "Chambers, citado por Boitard: «Les tableaux du genre terrible, dit-il, sont composés "
                   "de […] rochers arides près à s'écrouler […]. Les arbres ont une forme hideuse […] ; "
                   "vous voyez que les autres ont été noircis et fracassés par la foudre. Les bâtimens "
                   "sont en ruine ou à demi consumés par le feu […]. Rien d'entier ne subsiste, sinon "
                   "quelques chétives cabanes» (19–20).",
        "flaubert": [("On compose le ", "n"), ("genre terrible", "c"), (" avec des ", "n"),
                     ("rocs suspendus", "x"), (", des ", "n"), ("arbres fracassés", "c"), (", des ", "n"),
                     ("cabanes", "c"), (" ", "n"), ("incendiées", "x"), (" ;", "n")],
        "cadena": "",
        "afuera": "«Je demande si des hommes de bon sens peuvent donner de telles absurdités pour les "
                  "règles, les principes de l'art des jardins» (20).",
    },
    {
        "genero": "El majestuoso",
        "pags": "F 54 · B 52–53",
        "boitard": "«Par des pyramides, des obélisques, des arcs de triomphe, des colonnes trajanes, "
                   "rappelez aux promeneurs la grandeur du maître […]. L'orgueil de l'homme est un champ "
                   "vaste, ne craignez pas d'exagérer» (52).",
        "flaubert": [("Les ", "n"), ("obélisques", "c"), (" et les ", "n"), ("arcs de triomphe", "c"),
                     (" caractérisent le genre majestueux ;", "n")],
        "cadena": "",
        "afuera": "«Telles sont les convenances de mœurs» (53).",
    },
    {
        "genero": "El fantástico",
        "pags": "F 54 · B 73–75",
        "boitard": "«ces jeux bizarres, ou si l'on aime mieux de ces jeux d'enfans», tomados de «un jardin "
                   "des environs de Stuttgard, qui existait en 1791» (73): un jabalí de mármol, «le monstre "
                   "de marbre» (73); un ermitaño que resulta ser «un automate»; «la barque enchantée», que "
                   "lleva al «temple de l'amour» (74), y, en una gruta, «un fauteuil gothique» donde, al "
                   "sentarse, «vingt jets d'eau […] l'inondent» (75).",
        "flaubert": [("Il y a même le genre ", "n"), ("fantastique", "c"), (", dont ", "n"),
                     ("le plus beau spécimen", "x"), (" se voyait ", "n"), ("naguère", "x"), (" ", "n"),
                     ("dans un jardin", "c"), (" ", "n"), ("wurtembergeois", "x"),
                     (" — car on y rencontrait successivement ", "n"), ("un sanglier, un ermite", "c"),
                     (", ", "n"), ("plusieurs sépulcres", "x"), (", et ", "n"), ("une barque", "c"),
                     (" se détachant d'elle-même ", "n"), ("du rivage", "c"),
                     (", pour vous conduire dans un ", "n"), ("boudoir", "x"), (" où ", "n"),
                     ("des jets d'eau vous inondaient", "c"), (" quand on se posait sur le ", "n"),
                     ("sofa", "x"), (".", "n")],
        "cadena": "",
        "afuera": "«Sous ce titre, qui n'est pas trop convenable» (73); «l'amusement du prince» (75).",
    },
]


def flaubert_html(segmentos):
    out = []
    for t, tipo in segmentos:
        # espacio fino de la tipografía francesa: que « ; » no queden solos
        t = t.replace(" ;", "\u00a0;").replace("« ", "«\u00a0").replace(" »", "\u00a0»")
        if tipo in ("c", "e"):
            out.append(f'<span class="copia">{esc(t)}</span>')
        elif tipo == "x":
            out.append(f'<span class="cambio">[{esc(t)}]</span>')
        else:
            out.append(esc(t))
    return "".join(out)


def html(carpeta_fuentes):
    css = estilo_fuentes(carpeta_fuentes) + f"""
@page{{size:297mm 210mm;margin:0}}
html,body{{margin:0;padding:0;background:#fff}}
.hoja{{position:relative;width:297mm;height:210mm;overflow:hidden;color:{F};
  font-family:'Garamond','EB Garamond',serif}}
.titulo{{position:absolute;left:14mm;top:12.1mm;font-size:4.4mm;font-weight:600;line-height:1}}
.fig{{position:absolute;right:10mm;top:10.9mm;font-size:3.4mm;font-weight:600;line-height:1}}
.sub{{position:absolute;left:14mm;top:19.0mm;width:250mm;font-size:2.4mm;line-height:1.32}}
table{{position:absolute;left:14mm;top:31mm;width:269mm;border-collapse:collapse;table-layout:fixed}}
th{{font-family:'Plex',sans-serif;font-weight:500;font-size:2.25mm;text-align:left;
  padding:0 2.2mm 1.6mm 0;vertical-align:bottom;border-bottom:0.25mm solid {F}}}
td{{vertical-align:top;padding:2.2mm 2.8mm 2.4mm 0;border-bottom:0.15mm solid #cfcfcf;
  font-size:2.8mm;line-height:1.3}}
td.gen{{font-family:'Plex',sans-serif;font-weight:500;font-size:2.5mm;line-height:1.25}}
td.gen span{{display:block;font-weight:400;font-size:1.95mm;color:#6e6e6e;margin-top:0.6mm}}
td.boitard{{color:{B}}}
.copia{{color:{GRIS_COPIA}}}
.cambio{{color:{F}}}
.cadena{{display:block;font-family:'Plex',sans-serif;font-size:2.0mm;line-height:1.3;color:#6e6e6e;
  margin-top:1.2mm}}
td.afuera{{color:{B};padding-left:2.6mm;text-decoration:line-through;text-decoration-thickness:0.09mm;
  text-decoration-color:rgba(27,27,27,0.6)}}
td.maquina{{color:{G};font-family:'Plex',sans-serif;font-size:2.2mm;line-height:1.35;
  vertical-align:middle;border-left:0.15mm dashed {G};border-right:0.15mm dashed {G};
  padding:2mm 2.4mm;background:#f3f6fa}}
.conv{{position:absolute;left:14mm;top:180mm;width:180mm;font-family:'Plex',sans-serif;
  font-size:2.0mm;line-height:1.55}}
.conv b{{font-weight:500}}
.pie{{position:absolute;left:208mm;top:180mm;width:79mm;font-size:1.8mm;line-height:1.3}}
"""
    filas = []
    for i, f in enumerate(FILAS):
        maquina = ""
        if i == 0:
            maquina = (f'<td class="maquina" rowspan="{len(FILAS)}">Pendiente. Se llena con las salidas '
                       'del protocolo limpio (apartado 5): la misma consigna a varios modelos, con el '
                       'capítulo de Boitard delante. Los pilotos no entran aquí.</td>')
        cadena = f'<span class="cadena">{esc(f["cadena"])}</span>' if f["cadena"] else ""
        filas.append(
            f'<tr><td class="gen">{esc(f["genero"])}<span>{esc(f["pags"])}</span></td>'
            f'<td class="boitard">{esc(f["boitard"])}</td>'
            f'<td>{flaubert_html(f["flaubert"])}{cadena}</td>'
            f'{maquina}<td class="afuera">{esc(f["afuera"])}</td></tr>')
    etiqueta = NUMERO["cotejo"]
    cuerpo = f"""
<div class="hoja">
<div class="titulo">La copia, frase por frase</div>
<div class="fig">{etiqueta}</div>
<div class="sub">Seis frases del párrafo de los géneros (Flaubert 1910, 54) frente a sus fuentes en el manual
(Boitard s. f.). En gris, las palabras de Boitard que Flaubert conserva; en negro, las suyas; entre [corchetes],
lo que reemplaza o agrega dentro de una frase copiada. A la derecha, tachado, lo que la copia dejó afuera.</div>
<table>
<colgroup><col style="width:24mm"><col style="width:80mm"><col style="width:78mm"><col style="width:27mm"><col style="width:60mm"></colgroup>
<tr><th></th><th style="color:{B}">Boitard (s. f.)</th><th>Flaubert (1910, 54)</th>
<th style="color:{G}">La máquina</th><th style="color:{B}">Lo que la copia dejó afuera</th></tr>
{''.join(filas)}
</table>
<div class="conv"><b>Cómo leer:</b> <span style="color:{GRIS_COPIA}">gris</span>, palabras de Boitard
que siguen en la copia · negro, palabras de Flaubert · [corchetes], lo que reemplaza o agrega en una frase
copiada · <span style="text-decoration:line-through">tachado</span>, lo que no pasó · en sepia, Boitard ·
<span style="color:{G}">en azul, la máquina</span>.<br>
Las notas grises bajo Flaubert son los pasos intermedios: la nota de lectura (Carnet 18 bis, en
Dord-Crouslé 2003) y el borrador (Ms g 225-2).</div>
<div class="pie">Hoja de trabajo de la {etiqueta}: en el artículo va como tabla de texto, sin la columna
de la máquina ni los pasos intermedios. Textos: Boitard (s. f.), facsímil de Internet Archive (A039a018),
páginas verificadas en la imagen; Flaubert (1910), cap. II. Montaje: borrador de la máquina (Claude,
Anthropic), a pedido del autor, para verificar. Los dos textos son de dominio público.</div>
</div>"""
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{etiqueta}</title><style>{css}</style></head><body>{cuerpo}</body></html>\n'


def flaubert_md(segmentos):
    out = []
    for t, tipo in segmentos:
        # comillas a la española, sin espacio por dentro, como en el resto del borrador
        t = t.replace(" « ", " «").replace("« ", "«").replace(" »", "»")
        if tipo == "c":
            out.append(f"*{t}*")
        elif tipo == "x":
            out.append(f"[{t}]")
        else:
            out.append(t)
    return "".join(out)


def tachar(t):
    """Tacha las citas y deja las páginas sin tachar."""
    return re.sub(r"«[^»]*»", lambda m: f"~~{m.group(0)}~~", t)


def tabla_md():
    """La tabla del borrador: sin la columna de la máquina ni los pasos intermedios."""
    lineas = ["| Frase | Boitard (s. f.) | Flaubert (1910, 54) | Lo que la copia dejó afuera (Boitard s. f.) |",
              "|---|---|---|---|"]
    for f in FILAS:
        lineas.append(f'| {f["genero"]} | {f["boitard"]} | {flaubert_md(f["flaubert"])} | {tachar(f["afuera"])} |')
    return "\n".join(lineas) + "\n"


if __name__ == "__main__":
    if sys.argv[1:2] == ["--tabla"]:
        sys.stdout.write(tabla_md())
    else:
        carpeta_fuentes, salida = sys.argv[1:3]
        open(salida, "w", encoding="utf-8").write(html(carpeta_fuentes))
