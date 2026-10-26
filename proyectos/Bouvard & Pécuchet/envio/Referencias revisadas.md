# Referencias revisadas (Chicago autor-fecha, 17.ª ed.)

> 26 de octubre de 2026, sobre la lista del Borrador 0 del 24 de octubre. No cambié el borrador: los cambios están abajo, en «Qué cambió y por qué», para que el hilo de redacción los pase si está de acuerdo. Ver «Resultado»: la lista acordada ya está en el borrador.
>
> Datos comprobados hoy en Crossref y doi.org: páginas de Bender et al. (610–23), Dord-Crouslé (93–118) y Feyler (229–42); DOI de Bender et al., Carpo, Villagómez y Salazar-Sánchez y Cárcamo-Pino; autores de este último. Identificadores del ejemplar de Boitard en Internet Archive (A039a018, texto, 411 imágenes; A039a019, atlas, 295 imágenes; los dos con Public Domain Mark 1.0). Origen de la edición de Flaubert que se usa: Wikisource la transcribe del facsímil de Gallica (ark bpt6k208211x).

## Resultado

El hilo de redacción revisó esta lista el 26 de octubre (commit fc7a2bb de la rama del borrador) y pasó al borrador lo que se sostiene. **Desde entonces la lista vive solo en el borrador**, y `armar_docx.py` la toma de ahí: así no hay dos versiones que se separen.

- **Pasaron:** rangos abreviados (también 616–17 y 115–16 en el texto), 1751–65 sin Neuchâtel, DOI de Bender et al., «n.º», minúscula en los títulos franceses, Salazar-Sánchez y Cárcamo-Pino (también en el texto), subtítulos con dos puntos.
- **Con otra forma:** Boitard lleva «Nueva ed.», porque la portada dice «Nouvelle édition» (hoja n8 del facsímil) y la «seconde édition» solo aparece en la nota de la p. vi. Flaubert 1910 queda sin número de volumen y con [FALTA] hasta ver el facsímil: ni el «tome I» de Wikisource ni mi «Vol. 1 de» están comprobados. Los borradores se explican con una cláusula en §3.1 («que se citan por manuscrito y folio») y no con una nota, porque las normas (§8) no quieren referencias en las notas. Las entradas sin fecha van después de las fechadas del mismo autor.
- **No pasaron, y tenía razón el borrador:** Carnet 18 bis, Ms gg 10 y la *Correspondance* se quedan en la lista con «Citado en …». Chicago pide listar el original y la fuente secundaria cuando el original no se vio; mi propuesta de sacarlos era la regla de APA. Lumen se queda: el PDF dice «Coedición de Editorial Universitaria con Editorial Lumen SRL, 2004». Las comillas altas las pone solo el programa. El [1973] de Maturana y Varela entra cuando la nota de §7 pase a texto.
- **Arreglado en el programa** a partir de la revisión: las “ ” que el borrador anida dentro de « » pasan a ‘ ’, y las notas [FALTA …] que llevan corchetes adentro se reconocen enteras.

## Lo que propuse (para el registro)

| Entrada | Cambio | Por qué |
|---|---|---|
| Todas | Comillas altas “ ” en los títulos de artículos y capítulos, y ‘ ’ dentro de ellas. | Las normas (§7) piden comillas altas; el borrador usa « ». Lo mismo vale para las citas del cuerpo: `armar_docx.py` ya las convierte en los .docx, pero conviene que el borrador lo haga también. |
| Todas | Rangos de páginas abreviados (610–23, 229–42, 160–61, 1481–87; 93–118 queda igual). | Regla de Chicago para rangos de números. Vale también para las citas del texto: «(Bender et al. 2021, 616–617)» pasa a «616–17». |
| Diderot y d’Alembert | «1751–1765» → «1751–65» en la entrada y en las cuatro que la remiten. Saqué «Neuchâtel: Faulche», que solo vale para los últimos diez tomos. | Misma regla para rangos de años; los tomos 2 y 4 que se citan son de París. |
| Bender et al. | Agregado el DOI; «ACM» desarrollado. | Las normas piden DOI cuando exista (lista de comprobación). |
| Boitard s. f. | Agregados los enlaces de Internet Archive de los dos tomos; «Segunda edición» → «2.ª ed.». | Lista de comprobación: «direcciones web para las referencias donde ha sido posible». **A verificar:** el catálogo de Sevilla dice «Nouvelle édition» y el borrador dice que la portada dice «seconde édition». Chicago sigue la portada; si dice «nouvelle», poner «Nueva ed.». |
| Flaubert 1910 | «t. I» → «Vol. 1 de»; agregado el facsímil de Gallica. | Forma de Chicago para un volumen de obras completas con título propio. **A verificar:** el «tomo I» lo da Wikisource; los volúmenes de Conard no siempre llevan número. El pendiente de pasar a una edición crítica (Pléiade 2021 o GF 1999) sigue en pie, y cambiaría todas las páginas. |
| Flaubert, Carnet 18 bis; Flaubert, Ms gg 10; Flaubert 1998, *Correspondance* | Sacados de la lista. | Se citan a través de Dord-Crouslé (2003) y Carrico (2019), no vistos. Chicago (17.ª ed., 14.260) pide listar solo la fuente que se consultó y citar «en» o «citado en» en el texto, que es lo que ya hace el borrador. Si se cotejan antes de enviar (pendiente del hilo de redacción), vuelven a la lista. |
| Flaubert s. f. | Queda una sola entrada sin fecha de Flaubert, así que no hace falta «s. f.-a», «s. f.-b». | **Decisión pendiente** para el borrador: las citas del texto dicen «(Ms g 225-2, f. 171)», que no coincide con la clave de la lista («Flaubert s. f.»). Las dos opciones aceptables son «(Flaubert s. f., f. 171)» o mantener la signatura y decirlo una vez en una nota («los borradores se citan por su signatura»). Recomiendo la nota: la signatura se entiende mejor y la usan los estudios citados. |
| Salazar y Cárcamo Pino 2021 | → «Salazar-Sánchez, Cristian Gonzalo, y Mauricio Arnoldo Cárcamo-Pino». | Así figuran en Crossref y en el artículo. En el texto pasa a «(Salazar-Sánchez y Cárcamo-Pino 2021, 1485)». Queda igual a la forma de Cárcamo-Pino 2025, que antes no coincidía. |
| Maturana y Varela | En el texto, «(Maturana y Varela [1973] 2004, 73)», con corchetes. Saqué «Buenos Aires: Lumen». | Forma de Chicago autor-fecha para reediciones con la fecha original. El pie de imprenta del PDF del proyecto es solo de Editorial Universitaria; **verificar** en la página de créditos. |
| Revistas sin volumen (Revue Flaubert, Astrágalo, RCL, IJDAH) | «18» → «n.º 18», etc. | En Chicago, cuando la revista numera solo por número, se indica «n.º». |
| Carpo 2018 | Saqué la nota «[Leído solo el resumen.]» de la entrada. | No va en una lista de referencias. Sigue como pendiente del borrador: leer el artículo completo antes de enviar, o citar solo lo que dice el resumen. |
| Leclerc 2019 y Thomas 2019 | Falta la URL. | El sitio de la *Revue Flaubert* no respondió hoy. Están en el mismo número que Carrico. |

## Pendientes que no son de formato

- Dord-Crouslé (2003) y Feyler (2006) se citan por párrafo de OpenEdition. Chicago acepta el párrafo para textos en línea sin páginas fijas, pero los dos tienen PDF paginado (93–118 y 229–42). Si se pasan a páginas, es mejor.
- Manovich (2018) se cita por sección («Aesthetic AI», «The Limits of Statistical Reason»): es correcto para un libro electrónico sin páginas, y conviene decirlo una vez, por ejemplo en la primera cita.
- Baridon (1998), Herschberg Pierrot (1981) y Yamazaki (2019) aparecen en notas de trabajo del borrador, no en el texto. Si entran, hay que sumarlos.
- Las normas piden el archivo RIS si se usó un gestor bibliográfico. No se usó, así que no es obligatorio, pero lo dejé hecho (`referencias.ris`) por si sirve para Zotero.
- La revista cuenta las referencias en el total de 5.000 a 9.000 palabras. Esta lista tiene unas 600.
