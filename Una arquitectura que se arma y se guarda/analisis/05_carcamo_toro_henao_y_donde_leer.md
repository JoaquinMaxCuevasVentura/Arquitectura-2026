# 05. Cárcamo Pino, Toro Henao y dónde leer el núcleo teórico

26 de octubre de 2026. Registro de la etapa.

El autor envió dos artículos que considera referentes de escritura y estructura, y que «podrían aportar» al artículo, sin obligación de usarlos. También pidió buscar libros para el contenido teórico en Internet Archive o Monoskop. Este archivo registra lo que aporta cada artículo, con las citas cotejadas en el PDF enviado, y dónde se puede leer cada obra del núcleo.

## 1. Lo que aportan los dos artículos

### Cárcamo Pino (2025b), «Oralitura/literatura y manuaje/lenguaje: una revisión por reescritura»

*Revista Chilena de Literatura*, 112: 233-264. PDF del autor; citas cotejadas hoy [V].

**Tres ideas que sirven directamente.**

1. **Una «mano», como una mano de póker.** En una nota, Cárcamo Pino cita su conversación con Salazar Sánchez: además del órgano, existe la acepción de «mano» como «conjunto de acciones manuales relacionadas en un ámbito específico», y una mano de póker es «un set articulado de movimientos manuales (y sus resultados) desplegados en el ámbito del juego» (Salazar Sánchez y Cárcamo Pino, 2021: 1484, cit. en Cárcamo Pino, 2025b: 244, n. 10). Es un nombre en castellano para lo que el borrador llama la secuencia: **armar un puesto es una mano**. Y lo es en los dos sentidos del habla corriente: la partida que se juega cada día y la «buena mano» de quien la juega.
2. **El *manoaje*, con o.** Al cerrar, propone «referirnos a manoaje (con o) cuando aludimos a un subgrupo contextual de acciones manuales, un manoaje específico, por ejemplo, para un ámbito profesional, una disciplina, un tipo de soporte» (Cárcamo Pino, 2025b: 259). El conjunto de gestos con que se arma un puesto sería un manoaje específico.
3. **El manuaje como sistema de transmisión.** Reescribiendo a Fall, sostiene que el manuaje «no es solo una manera de ver el pasado, sino que es también un conjunto/sistema de conocimientos y experiencias, y un conjunto/sistema de transmisión de esos conocimientos y experiencias» (Cárcamo Pino, 2025b: 248). Responde de frente la pregunta original del autor: qué conocimiento se produce y **se transmite** en el montaje.

**Dos citas de apoyo.**

- El propósito de «dar legitimidad y justicia epistémica» a prácticas corporales «minusvaloradas, invisibilizadas» por «el monopolio de la escritura y el lenguaje» (Cárcamo Pino, 2025b: 259). Ya se usó en *Altiplano*. Aquí justifica estudiar un saber que nadie escribió.
- En nota, con Pareyson, la formatividad: «un hacer tal que, mientras hace, se inventa el “modo de hacer”» (Pareyson, cit. en Cárcamo Pino, 2025b: 246, n. 12). Es la otra cara de H1: si la secuencia no resulta estable, quizá se inventa al armar. Es la hipótesis del «repertorio».

**La estructura del artículo.**

| Sección | Qué hace |
|---|---|
| 1. Introducción | Problematización; **hipótesis principal («tópica») e hipótesis auxiliar («metodológica»)**; objetivos; metodología; justificación del método |
| 2. Desarrollo | Revisión de cada concepto por separado (A y B) y reescritura cruzada (Ab y Ba) |
| 3. Discusión | Similitudes, diferencias y alcances |
| 4. Conclusiones | **Conclusión tópica y conclusión auxiliar metodológica** |

Lleva epígrafe (Godofredo Iommi: «Siempre lo mismo, pero nunca igual»), notas largas y etimologías.

### Toro Henao (2014), «Oralitura y tradición oral. Una propuesta de análisis de las formas artísticas orales»

*Lingüística y Literatura*, 65: 239-256. PDF enviado; citas cotejadas hoy [V].

**Lo que sirve: el análisis motifémico**, que toma de Enrique Ballón Aguirre (*Tradición oral peruana*, 2006).

- El **motivo** es «la unidad temática más pequeña del relato oral» y su realización concreta es el **motifema** (Toro Henao, 2014: 242).
- En los motivos, aunque el sentido cambie con el contexto, «una parte se mantiene estable y fija» (ibid.: 243). Los motifemas son las «realizaciones [...] concretas de un motivo en una variante determinada» (ibid.).
- El método no empieza por los motivos: «Se propone primeramente descubrir los motifemas, o realizaciones concretas de los motivos» (ibid.: 244).

**Cómo se traslada al puesto.** Es un método pensado para un saber no escrito, y separa lo fijo de lo variable, que es justo lo que pide H1:

- el **motivo** es la operación (*cubrir*, *apilar*, *calzar*): el verbo del registro;
- el **motifema** es su realización en un puesto y un ciclo: *tensar el nailon contra la reja con dos cuerdas, a las 06:40*;
- igual que el método, el registro anota primero las realizaciones (`campo/registro_de_operaciones.csv`: verbo, elemento, apoyo, nota) y deja que los motivos estables aparezcan al comparar ciclos (`comparar_ciclos.py`).

Su estructura es más simple: introducción, propuesta metodológica con precisiones conceptuales, aplicación a un corpus (dieciocho relatos) y conclusiones.

## 2. Propuestas para el borrador

| # | Propuesta | Estado |
|---|---|---|
| 1 | **«Mano» y «manoaje» en la sección 3** («Las manos»), con las citas de arriba | **Hecho** en `articulo/borrador_v0.md`; se puede quitar |
| 2 | **Motivo y motifema en la sección 4** («Comparación»), como la manera de leer el registro | **Hecho** en el borrador, en una frase; se puede quitar |
| 3 | **Dos hipótesis y dos conclusiones, como Cárcamo Pino.** La *tópica* es la tesis del puesto: la forma está en la secuencia. La *metodológica* dice que la lámina y su devolución dejan ver algo que el registro solo no muestra. Esta segunda ya tiene sus pruebas en `02`, sección 5: legibilidad, reconocimiento y comparación. El artículo cerraría con una conclusión para cada una | **Decide el autor.** En *Altiplano* no se adoptó la fórmula estructural de Cárcamo Pino, para ganar sencillez (`Altiplano`, `analisis/09`). Aquí no se propone la fórmula, solo partir la hipótesis en dos. Encaja con la sección de teoría de la revista y vuelve explícito lo que el método ya hace |
| 4 | **El epígrafe.** No el de Iommi: es el de Cárcamo Pino, y en *Altiplano* se descartó un epígrafe por la misma razón. Mejor una frase de una vendedora, dicha en el campo y citada con su permiso. Una mujer, como prefería el autor en *Altiplano*, y alguien que habla desde el puesto, no sobre él | **Decide el autor** después del campo. Si no aparece, el artículo va sin epígrafe |

## 3. Dónde leer el núcleo teórico

Búsqueda de hoy en Internet Archive y en Monoskop. Tres advertencias:

- **«Préstamo»** es el préstamo digital controlado de Internet Archive: legal y gratuito, pide una cuenta y presta el libro por horas o semanas.
- **«Subido por usuarios»:** copias de libros con derechos que alguien subió con una licencia que no puso el titular. Su situación legal es dudosa: mejor el préstamo, la biblioteca o la editorial.
- **Monoskop** es un wiki de bibliografías sobre arte y teoría. Algunas de sus páginas enlazan PDF cuya licencia no siempre es clara. Aquí sirvió para confirmar datos de edición.

| Obra | Internet Archive | Monoskop | Para qué decisión |
|---|---|---|---|
| Tassi *et al.* (2013), *Hacer plata sin plata* | **Abierto**, en la colección de la biblioteca del PIEB (`pieb_hacer_plata_sin_plata_el_desborde_de_los_comerciantes_populares_en_bolivia`) | — | Sección 2: pasar de la reseña [E] a la lectura [V]. **Prioridad 1** |
| Heathcott (2019), tianguis | PDF en el sitio del autor (heathcott.nyc), visto en la búsqueda del 26 de octubre | — | Sección 2: qué añade el artículo. **Prioridad 1** |
| Moatasim (2019), *Antipode* | No | — | Sección 2: el antecedente principal. Buscar copia de la autora o pedirla por correo. **Prioridad 1** |
| Leroi-Gourhan (1964-1965), *Le geste et la parole* | Préstamo, t. 1 en francés (`legesteetlaparol0000andr`); la traducción inglesa (MIT, 1993) está subida por usuarios | Página del autor. Confirma la edición castellana: *El gesto y la palabra*, trad. Felipe Carrera D., Caracas, Universidad Central de Venezuela | Sección 3: la cadena operatoria. **Prioridad 2**: basta un capítulo, el de la técnica |
| Lemonnier (1992), *Elements for an Anthropology of Technology* | Subido por usuarios | — | Alternativa a Leroi-Gourhan. Leer uno de los dos |
| Mauss, «Les techniques du corps» | Préstamo de *Sociologie et anthropologie* (1968); la edición castellana de 1971 está subida por usuarios | Página del autor. Confirma la traducción inglesa: «Techniques of the Body», *Economy and Society*, 2(1), 1973: 70-88 | Sección 3: aprender por imitación. Es un artículo corto |
| Lave y Wenger (1991), *Situated Learning* | Préstamo (`situatedlearning0000lave`) | — | Sección 6 y la condición de «aprende» (`02`). **Prioridad 2** |
| Goldstein (2016), *Owners of the Sidewalk* | Préstamo (`ownersofsidewalk0000gold`) | — | Sección 2 (Bolivia) |
| Frampton (1995), *Studies in Tectonic Culture* | Préstamo | — | Ya citado y cotejado en *Altiplano* (p. 5) |
| Ingold (2000), *The Perception of the Environment* | Préstamo | No hay página | Solo si entra el *taskscape* (banco) |
| De Certeau, *La invención de lo cotidiano* | Préstamo en inglés; las ediciones en castellano y en francés están subidas por usuarios | No hay página | Banco: las «tácticas» |
| Lefebvre, *Rhythmanalysis* | No está | Página del autor; no confirma esa obra | Banco |
| Halprin (1969), *The RSVP Cycles* | Préstamo | No hay página | Para elegir entre Halprin y Tschumi (`04`) |
| Tschumi (1981), *The Manhattan Transcripts* | No está | No hay página | Ídem |
| Rudofsky (1964), *Architecture without Architects* | Préstamo | No hay página | Banco; probablemente no entra |
| Sennett (2008), *The Craftsman*; Polanyi (1966), *The Tacit Dimension* | Préstamo | No hay página | Banco |
| Kronenburg (2008), *Portable Architecture* | Préstamo | — | Banco |
| Lazar (2008), *El Alto, Rebel City* | Préstamo | — | Banco: El Alto, asociaciones de comerciantes |
| Rivera Cusicanqui (2015), *Sociología de la imagen* | Subido por usuarios; la editorial Tinta Limón suele publicar con licencia libre [verificar en su sitio] | No hay página | Para el método de las láminas, si entra |
| Benjamin, «Nápoles» (con Lacis, 1925) | Préstamo de *Reflections* (1978) | Página del autor, con *Denkbilder* | Banco: la «porosidad» |
| Gilbreth (1911; 1917) | **Abierto**, dominio público | — | Ya en la taxonomía (n.os 14 y 23) |
| Semper, *Der Stil* (1860-1863) | **Abierto**, dominio público | No hay página | Ya en la taxonomía (n.º 13) |
| Kim (2015); Mörtenböck y Mooshammer (2015); Pallasmaa, *La mano que piensa*; Saenz (1979); Buechler y Buechler (1996) | No están | No hay página | Biblioteca o editorial |

**Orden de lectura sugerido para las dos primeras semanas.** Moatasim, Heathcott y Tassi *et al.* primero, porque deciden la sección 2 y la contribución. Después un capítulo de Leroi-Gourhan (o Lemonnier) y Lave y Wenger. El resto, solo si el campo lo pide (`02`, sección 7).
