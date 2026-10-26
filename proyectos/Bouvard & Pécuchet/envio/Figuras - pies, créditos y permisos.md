# Figuras y tablas: pies, créditos y permisos

> 26 de octubre de 2026, sobre el mapa de figuras del Borrador 0 (Fig. 1–4, Tablas 1–2) y el README de `laminas/`. Los pies van como piden las normas (§6): Calibri 8, «Fig. X», título, autor, año y fuente, con un comentario breve solo si es indispensable. Si entra el mosaico de imágenes generadas en el apartado 5, la escena exótica pasa a ser la Fig. 5 y hay que renumerar aquí, en el borrador y en `fuente/svg.py` (`NUMERO`).

## Cuántas y de qué tamaño

- Seis de las diez permitidas (cuatro figuras y dos tablas). Quedan cuatro lugares, por ejemplo para el mosaico del apartado 5 y la escena del apartado 6.
- Cada figura: 16 cm de ancho y 10 cm de alto como máximo, a 300 ppp, es decir **1890 × 1181 píxeles como máximo**. Si es más angosta, va alineada a la izquierda. Se puede componer varias imágenes en una.
- Se entregan dentro del texto **y** aparte, como `FIG1.jpg`, `FIG2.jpg`… (jpg, bmp, tiff o png). Las tablas van solo en el texto, como tablas de Word.
- Las normas prohíben subir la resolución con programas de diseño. Esto toca a las Fig. 1 y 4: los borradores usan hojas del atlas bajadas a 1600 px de ancho, que a 16 cm dan unos 254 ppp. Hay que rehacerlas con las hojas a resolución completa (la hoja 88, por ejemplo, tiene 3539 × 2223 px, unos 560 ppp a 16 cm). Las Fig. 2 y 3 son vectoriales y se exportan directamente a 300 ppp.
- Las láminas actuales están en A4 apaisado: reducidas a 16 × 10 cm, los rótulos quedan entre 2,4 y 3,8 pt. El README de `laminas/` ya lo dice: hay que redibujarlas al tamaño final, con rótulos de unos 7 pt o más y lo explicativo en el pie. Los .docx de este envío llevan las láminas actuales como **marcador**, a 10 cm de alto, para ver la paginación; no son las figuras finales.

## Pies

**Fig. 1** Treinta y dos puentes, todos sobre agua: las seis láminas de puentes del atlas de *L'Architecte des jardins* (lám. 27–32). Montaje del autor, 2026, sobre Boitard (s. f.), ejemplar de la Biblioteca de la Universidad de Sevilla en Internet Archive, dominio público.

**Tabla 1** La copia, frase por frase: seis frases del párrafo de los géneros (Flaubert 1910, 54) frente a sus fuentes en el manual. En cursiva, las palabras de Boitard que siguen en la copia; entre corchetes, lo que la copia reemplaza o agrega; tachado, lo que deja afuera. Fuente: elaboración propia sobre Boitard (s. f.) y Flaubert (1910).

**Tabla 2** Las fallas del jardín y lo que decía el manual. Fuente: elaboración propia sobre Flaubert (1910) y Boitard (s. f.).

**Fig. 2** Dos jardines a la misma escala: Wissous, el ejemplo de Boitard para una casa modesta (lám. 18), y Chavignolles, reconstruido con los datos de la novela. En punteado, lo supuesto; en amarillo, lo que Boitard excluye en un jardín de uno o dos *arpents*. Dibujo del autor, 2026, sobre Boitard (s. f., 114–16, lám. 18; dominio público) y Flaubert (1910, cap. II).

**Fig. 3** Lo que se ve desde el comedor la noche de la cena, desde sus dos lugares posibles. En amarillo, lo que no se ve desde ninguno de los dos con el muro y la *charmille* enteros; al lado, un corte con alturas supuestas y el recorrido del agua del estanque. Dibujo del autor, 2026, sobre Flaubert (1910, 26, 28, 59–62).

**Fig. 4** La escena exótica de Boitard, «Jardin exotique» (lám. 1), con las plantas numeradas en el orden en que él las describe. Boitard (s. f., 63–65, lám. 1), ejemplar de la Biblioteca de la Universidad de Sevilla en Internet Archive, dominio público; números del autor, 2026.

En la versión anónima, «del autor» se cambia por «propio» («Montaje propio», «Dibujo propio», «números propios»). Así lo hace `armar_docx.py`.

Cambios frente a los pies del borrador: se agregan el autor y el año (las normas los piden), se sacan las páginas que el texto ya da y los [FALTA] pasan a esta lista. El borrador llama a las figuras «(Fig. 1)»; las normas piden «(Fig. 1.)», con punto. Lo corrige el programa en los .docx.

## Créditos y permisos

| Figura | Material ajeno | Situación | Qué hacer |
|---|---|---|---|
| Fig. 1 y 4 | Hojas del atlas de Boitard, Internet Archive `A039a019` | Public Domain Mark 1.0 (el libro es del siglo XIX). No hace falta permiso. | Dar el crédito de la Biblioteca de la Universidad de Sevilla, como en los pies. Usar las hojas a resolución completa. |
| Fig. 2 | Lámina 18 de Boitard, retrazada | Igual que arriba. | Nada más. |
| Fig. 3 | Ninguno | Obra del autor. | — |
| Todas las láminas | Tipos EB Garamond e IBM Plex Sans Condensed | Licencia SIL Open Font License: se pueden usar en imágenes publicadas sin permiso. | — |
| Mosaico del apartado 5 (si entra) | Imágenes generadas por un modelo | Depende de las condiciones del servicio con que se generen; además hay que declararlo (ver la declaración de IA). | Revisar las condiciones de uso del servicio antes de generar, guardar consigna, fecha y modelo de cada imagen, y decirlo en el pie: «Imagen generada con [modelo], [fecha], consigna C[n]». |
| Tablas 1 y 2 | Citas breves de Boitard y Flaubert | Dominio público. | — |

## Anonimato y metadatos

- Los JPG de `laminas/` no tienen metadatos (sin EXIF ni XMP; comprobado hoy). Los PDF dicen solo «Chromium» y «Skia/PDF». Al exportar las figuras finales desde un programa de dibujo, revisar que el archivo no guarde el nombre del autor, y limpiarlo si lo hace.
- Ninguna figura lleva firma ni rótulo con nombre. Mantenerlo así en el redibujo.
