# Lo posible y lo conveniente

## El jardín de Bouvard y Pécuchet, su manual y la respuesta plausible

*Propuesta de artículo para* Astrágalo *A44 (2027), «Bouvard & Pécuchet. Arquitectura y desencanto: de la Enciclopedia a la inteligencia artificial». Borrador 2, 19 de octubre de 2026. Reemplaza al borrador 1.*

> **Convocatoria.** Editor: José Enrique López Canti (Universidad de Sevilla). Envío hasta el **15 de junio de 2027**; publicación prevista en septiembre de 2027. Plantilla oficial y ficha de evaluación en `/mnt/project-files/convocatoria/`.
>
> **Forma:** de 5.000 a 9.000 palabras **contando notas y referencias**; Chicago autor-fecha, 17.ª ed., con página exacta en toda cita literal; tres resúmenes de hasta 250 palabras (español, inglés, portugués), sin notas; hasta 5 palabras clave en minúsculas, mejor del Tesauro de la UNESCO; dos archivos, uno anónimo, con las autocitas como (XXXXX año, pág.); figuras dentro del texto como «Fig. X», con derechos; títulos sin negritas ni mayúsculas, con numeración decimal; declaración de uso de IA. Revisión por doble ciego con doce criterios, entre ellos originalidad, método y rigor en el análisis de fuentes.

---

## 0. Qué cambió desde el borrador 1

El borrador 1 proponía una prueba: comparar el jardín que describe Flaubert con el manual que sus personajes leen. Esa prueba ya se hizo en una primera pasada (ficha completa en [`analisis/concordancias Flaubert-Boitard.md`](analisis/concordancias%20Flaubert-Boitard.md)). El resultado cambió la tesis.

El borrador 1 suponía que el manual ordenaba el saber por efectos y **omitía** las condiciones del sitio. No es así. El manual pide estudiar el terreno antes que nada, pone las «conveniencias» como regla de todo el libro y advierte, una por una, casi todas las fallas que después narra Flaubert. Incluso rechaza la clasificación de los jardines por géneros que Flaubert le atribuye. Lo que pierde las condiciones no es el manual. Es **la copia**.

La propuesta queda más clara y más fácil de poner a prueba. Además, este borrador está escrito en un lenguaje más simple y ya no se apoya en otros proyectos del autor.

---

## 1. La idea en tres frases

1. En el capítulo II de *Bouvard et Pécuchet*, dos copistas jubilados arman un jardín con un manual en la mano, y el jardín fracasa delante de sus invitados.
2. El manual advertía casi todas esas fallas, pero ellos copiaron la lista de objetos y dejaron las reglas que decían dónde, cuándo y para quién sirve cada objeto.
3. Una respuesta generada por inteligencia artificial puede hacer el mismo recorte, y este artículo lo pone a prueba con el mismo manual.

### Resumen provisional (unas 200 palabras)

En el capítulo II de *Bouvard et Pécuchet*, los dos copistas transforman su huerta de Normandía siguiendo *L'Architecte des jardins* de Pierre Boitard, un manual práctico de la colección Roret. Levantan una tumba etrusca de yeso, un Rialto sobre un estanque sin agua, una pagoda y una roca de piedras pegadas con cemento. Ante sus invitados, el jardín fracasa. Este artículo compara pasaje por pasaje la novela con el manual y muestra que el libro advertía casi todas esas fallas: pedía estudiar el terreno, prohibía las rocas artificiales en un terreno llano, mandaba esconder las tumbas de la vista de la casa y declaraba que la huerta burguesa adornada no tenía reglas. Los copistas tomaron el catálogo de objetos y dejaron las reglas, que Boitard llama «conveniencias». Se preguntaron qué era posible y no qué era conveniente. El artículo extiende la prueba a dos modelos generativos de texto y uno de imagen, con consignas fijas, para ver si la respuesta plausible repite ese recorte, con y sin el texto del manual a la vista. La conclusión discute qué le falta a una respuesta posible para convertirse en una decisión de proyecto, y por qué el propio manual dejaba la última palabra a quien está en el sitio.

**Palabras clave (provisionales):** jardines, manuales, copia, inteligencia artificial, Flaubert. *(Contrastar con el Tesauro de la UNESCO.)*

*El resumen se traduce al inglés y al portugués después del punto de decisión D1.*

---

## 2. El caso

### 2.1 La escena

Con la herencia de Bouvard, los dos copistas compran una granja con casa y huerta en Chavignolles, Normandía. Al llegar, la huerta tiene dos alamedas en cruz, legumbres en los arriates, «des cyprès nains et des quenouilles» y un muro con espalderas (Flaubert 1910, 26). Meses después, tras fracasar con los frutales, se prometen ahorrar «leur peine et leur argent» (53), pero los árboles muertos dejan «des intervalles fort vilains» en el huerto (54). Pécuchet hace varios dibujos con su estuche de dibujo, «ils n'arrivaient à rien de satisfaisant», y entonces encuentran en su biblioteca *L'Architecte des jardins* de Boitard (54).

Con el libro arman, con un solo peón y poca plata, una tumba etrusca de yeso negro con «l'apparence d'une niche à chien», un Rialto sobre un estanque que no retiene el agua, una cabaña a la que le queman el techo de paja «pour la rendre plus poétique», una pagoda china de troncos y hojalata, y una roca de granitos pegados con cemento, «pareil à une gigantesque pomme de terre» (55–56). Talan el tilo más grande, casi muerto, y lo tienden a lo largo del jardín para que parezca «renversé par la foudre» (56).

Después invitan a cenar a los notables del pueblo. A los postres se abren las cortinas y el jardín aparece: «C'était, dans le crépuscule, quelque chose d'effrayant». La tumba es «un cube au milieu des épinards» y el puente veneciano, «un accent circonflexe par-dessus les haricots» (61). Nadie entiende la tumba, ni la cabaña quemada, ni el muro en ruinas. El cura, al irse, le dice a Pécuchet que no encuentra «convenable ce simulacre de tombeau au milieu des légumes» (64). La señora Bordin se engancha el vestido en el tilo: «Mon Dieu ! quelle bêtise que cet arbre !» (65).

### 2.2 El libro

El manual existe. Es el *Nouveau manuel complet de l'architecte des jardins* de Pierre Boitard, de la *Librairie encyclopédique de Roret*, una colección de manuales prácticos para todos los oficios. Está digitalizado en Internet Archive, texto y atlas de láminas, y el ejemplar digitalizado es **de la Biblioteca de la Universidad de Sevilla** (A 039(a)/018–019), la misma universidad que publica *Astrágalo*.

El manual Roret es un eslabón entre la *Encyclopédie* y el manual técnico moderno. Ordena un saber en capítulos, láminas y recetas, y lo vende barato para que cualquiera lo aplique. Es, en pequeño, la promesa de la que habla la convocatoria: que más información disponible mejore la capacidad de decidir y construir.

### 2.3 Lo que mostró el cotejo

Flaubert copia a Boitard casi literalmente, con cambios pequeños que se pueden marcar. Entre [corchetes], lo que la copia cambió:

| Boitard (s. f.) | Flaubert (1910) |
|---|---|
| «un ex-voto marquant la place où un chevalier est tombé sous le fer d'un assassin» (72) | «un ex-voto [à la vierge], [indiquant] la place où un [seigneur] est tombé sous le fer d'un assassin» (54) |
| «pour but de faire naître d'agréables souvenirs à un colon ou à un voyageur» (63) | «[pour] faire naître [des] souvenirs à un colon ou à un voyageur» (54) |
| «ces jeux bizarres, ou si l'on aime mieux de ces jeux d'enfans» (73) | «[le plus beau spécimen] se voyait naguère dans un jardin wurtembergeois» (54) |
| un templo del amor y, en una gruta, un «fauteuil gothique» que dispara «vingt jets d'eau» (75) | «un [boudoir] où des jets d'eau vous inondaient quand on se posait sur le [sofa]» (54) |
| «C'est sur le principe erroné de l'unité de genre, que les auteurs ont échafaudé leur classification des jardins» (55) | «L'auteur les divise en une infinité de genres» (54) |

El cotejo completo mostró tres cosas *(primera lectura, a confirmar)*:

1. **La copia se queda con el catálogo.** De 13 elementos del jardín, 9 tienen correspondencia directa en el manual: la tumba, la cabaña, la pagoda, la roca, el laberinto y otros. Lo que no pasa al jardín son las reglas que acompañan a cada uno.
2. **Las fallas están donde estaba la regla.** De 9 fallas narradas, 6 ocurren justo donde el manual había advertido. Sobre el terreno llano, Boitard escribe: «Gardez-vous bien de ces roches factices, monceaux de pierres ridicules, qui semblent tombées du ciel au milieu d'un gazon» (50). La tumba debe quedar donde no se la vea «d'aucune partie du bâtiment» (69). Y el «genre terrible» que copian, con árboles fulminados y cabañas quemadas, viene de un pasaje de Chambers que Boitard cita como ejemplo de lo absurdo: «Je demande si des hommes de bon sens peuvent donner de telles absurdités pour les règles» (20).
3. **El manual tenía una entrada para su caso, y estaba vacía.** Boitard llama «potager pittoresque» a la huerta burguesa adornada, que «appartient le plus souvent à des négocians retirés» (29). Al llegar a ella escribe: «Nous n'indiquerons aucune règle pour tracer une composition qui n'en a point» (116).

### 2.4 Lo posible y lo conveniente

Antes de construir, Bouvard y Pécuchet revisan los géneros del manual uno por uno. El fantástico les parece «réservé aux princes», el templo sería «encombrant» y las plantas americanas cuestan demasiado. «Mais les rocs étaient possibles» (55). Su filtro es **lo posible**: lo que alcanza con la plata, el trabajo y el espacio que tienen.

El filtro del manual es otro: **lo conveniente**. Boitard llama «convenances» a la regla sin la cual «on ne créera que des compositions ridicules ou absurdes» (49). Son tres: que la obra vaya con el lugar, con su tiempo y con las costumbres de quienes la habitan. En este artículo se traduce como **conveniencia**, en el sentido antiguo de decoro: lo que conviene a un lugar, a un tiempo y a una gente.

El cura, al despedirse, juzga el jardín con la palabra del manual. Es la escena en pocas líneas: los copistas preguntaron qué era posible y los vecinos respondieron con lo que era conveniente.

La inteligencia artificial generativa vuelve actual esta diferencia. Un modelo siempre puede responder con algo posible. La pregunta de proyecto es si responde algo conveniente, y quién decide eso. El propio Boitard deja la última palabra a una persona: «C'est à l'artiste placé sur les localités à sentir et apprécier ces nuances» (226).

---

## 3. Pregunta e hipótesis

**Pregunta.** Cuando un saber de proyecto pasa de un manual a sus lectores, y de ahí a una máquina que genera respuestas, ¿qué se conserva y qué se pierde? ¿Se pierde siempre lo mismo?

Como en *Remiendos*, cada hipótesis dice antes de la prueba qué resultado la haría caer. Lo que no vale es mover los criterios después de ver los datos.

**H1. La copia se queda con el catálogo.** Bouvard y Pécuchet copian los objetos y los efectos del manual, y dejan las reglas que los acompañan.

- *Cómo se prueba:* la ficha de concordancias. Para cada elemento del jardín se separa en Boitard lo que es catálogo (objeto, efecto) y lo que es regla (condición, advertencia, duda del autor), y se ve qué pasa a la novela y al jardín.
- *Cae si:* las reglas pasan a la copia tanto como los objetos; o si la edición que usó Flaubert no traía esas reglas. En este segundo caso el manual sí las omitía y vuelve la tesis del borrador 1.
- *Estado:* la primera lectura la sostiene. Falta fijar la edición y una segunda lectura.

**H2. Las fallas están donde estaba la regla.** Las fallas del jardín ocurren donde el manual había puesto una advertencia que la copia no tomó.

- *Cómo se prueba:* se clasifican todas las fallas que narra Flaubert según su origen (sitio, conveniencia, contraejemplo ejecutado, ejecución, azar) y se busca si el manual las advertía.
- *Cae si:* menos de la mitad de las fallas tienen una advertencia previa en la edición que usó Flaubert, según dos lecturas independientes.
- *Estado:* 6 de 9 en primera lectura.

**H3. La respuesta plausible copia la copia.** Un modelo generativo hace el mismo recorte que Bouvard y Pécuchet. Tiene dos partes:

- **H3a, sin la fuente.** Si se le pregunta por el manual de Boitard sin dárselo, el modelo responde con la versión de Flaubert: un catálogo de géneros. La novela se copió y se comentó mucho más que el manual, así que lo plausible es la copia. *Cae si* la mayoría de las respuestas mencionan las conveniencias o el rechazo de los géneros.
- **H3b, con la fuente.** Si se le da el capítulo completo de Boitard y se le pide un jardín para la huerta de Chavignolles, el modelo igual entrega el catálogo y deja las reglas. Esto prueba la pregunta de la convocatoria: si más información, por sí sola, mejora la decisión. *Cae si* la mayoría de las salidas aplican por su cuenta al menos dos reglas del manual al sitio (terreno llano, falta de agua, jardín chico, tumba a la vista).

Las tres hipótesis valen aunque caigan. Si cae H3, el artículo dirá que el modelo no repite el recorte, y en qué condiciones.

### Lo que este artículo no afirma

- No afirma que una máquina «piense» como Bouvard y Pécuchet. Compara **procedimientos**: tomar un repertorio y usarlo sin las reglas de su uso.
- No juzga a Boitard. Al contrario: muestra que el manual era más lúcido que sus lectores.
- No mide el costo ambiental de los modelos. El eje 6 de la convocatoria aparece en una sola frase, si el caso la pide (§5).
- No habla de «la IA» en general. Los resultados del protocolo valen para esos modelos, con esas consignas, en esa fecha.

---

## 4. Método

El método es el habitual del autor (reunir, desarmar, proponer, ensayar, contrastar, decidir), con contrastes elegidos para un artículo de teoría con un ensayo proyectual. Cada instrumento existe porque resuelve una dificultad concreta, y se dice cuál.

### 4.1 La ficha de concordancias

**Dificultad que resuelve:** sin ella, la relación entre Flaubert y Boitard se queda en una cita suelta, y H1 y H2 no se pueden probar.

La primera pasada está hecha. Usa letras de evidencia adaptadas de *Remiendos*: **F** (está en Flaubert), **B** (está en Boitard), **C** (Chambers citado por Boitard), **I** (inferencia) y, más adelante, **G** (generado por un modelo). Falta:

- fijar la fecha de la edición digitalizada, que se presenta como «seconde édition» y no tiene año, y averiguar qué edición tuvo Flaubert;
- verificar cada página en el facsímil, porque el OCR confunde cifras;
- buscar el origen de tres géneros que no están en Boitard: «grave», «mystérieux» y «rêveur»;
- una segunda lectura, hecha por otra persona sin ver la primera clasificación.

### 4.2 Los corchetes: la copia anotada

**Dificultad que resuelve:** decir «Flaubert copia a Boitard» no muestra nada. Hay que ver la copia.

El artículo pone los textos uno al lado del otro y marca entre corchetes lo que cambió, como en §2.3. Es un recurso tipográfico simple, y el mismo sirve para las salidas de los modelos: Boitard, Flaubert y la máquina, alineados, con los cambios a la vista. En las figuras puede ir en dos tintas, el texto de origen en gris y lo cambiado en negro.

### 4.3 La lámina: dos jardines a la misma escala

**Dificultad que resuelve:** la novela describe el jardín como una serie de efectos. Para ver que las fallas son de sitio hay que **dibujar el sitio**.

- **Planta reconstruida** del jardín de Chavignolles con todo lo que el capítulo dice de posiciones: la cruz de alamedas, la «charmille» (el seto alto de carpes), la espaldera, el «vigneau» (un montículo), la «tonnelle» (el emparrado), la escalinata, la celosía al fondo, el granero. Cada trazo lleva su letra de evidencia y lo inferido va en línea discontinua.
- Al lado, a la misma escala, el **jardín de Wissous** de la lámina 18 de Boitard. Es su modelo para un terreno de no más de un arpent, junto a la casa modesta de un hombre de letras, con la huerta «masqué de manière à n'être pas aperçu» (Boitard s. f., 115–116). Es la respuesta del manual para un caso como este.
- La lámina tiene que mostrar de un vistazo qué recomendaba el manual y qué se hizo. Si no lo muestra mejor que el texto, se descarta.

### 4.4 El protocolo de generación

**Dificultad que resuelve:** sin protocolo, la parte sobre inteligencia artificial sería una ilustración elegida a gusto, y H3 no podría caer.

**Consignas**, escritas y archivadas antes de generar:

| | Consigna | Prueba |
|---|---|---|
| C1 | «¿Cómo clasifica Pierre Boitard los jardines en *L'Architecte des jardins*?» | H3a |
| C2 | «Diseña un jardín para una huerta en Normandía según *L'Architecte des jardins* de Boitard.» | H3a, y base de comparación para H3b |
| C3 | La consigna C2 más el texto completo del capítulo IV de Boitard (conveniencias y escenas) pegado en la consigna. | H3b |
| C4 | La consigna C3 más las condiciones del sitio que da Flaubert: huerta en uso, terreno llano, agua acarreada, casa a la vista, poca plata. | H3b |

**Modelos:** dos modelos de texto de empresas distintas y un modelo de imagen (este último solo para C2 y C4), con nombre, versión y fecha registrados. Diez salidas por consigna y por modelo, todas, sin elegir.

**Códigos**, la misma lista para todas las salidas:

- *Catálogo:* géneros nombrados, fábricas propuestas (tumba, puente, pagoda, roca, ruina, cabaña…), efectos prometidos.
- *Regla:* estudio del sitio; conveniencias; terreno llano; agua; tamaño del jardín; tumba lejos de la casa; nada de rocas artificiales; el «potager pittoresque» sin reglas.
- *Atribución:* le atribuye a Boitard la clasificación por géneros; le atribuye el «genre terrible» de Chambers; nombra a Flaubert sin que se lo pidan.
- *Objeción anticipada:* defiende una mezcla incoherente con un argumento listo, como hace Boitard cuando aconseja responder con el jardín botánico de Calcutta a quien objete su escena exótica (65).

**Qué demuestra y qué no.** El protocolo muestra cómo responden estos modelos a estas consignas en esta fecha. No demuestra nada sobre la inteligencia artificial en general, y el artículo lo dice así. Si C3 y C4 cambian mucho los resultados, también es un hallazgo: querría decir que la regla no se pierde por falta de información, sino por la forma de pedir.

### 4.5 Contraste situado: ¿exótico para quién?

**Dificultad que resuelve:** el eje 4 de la convocatoria pide pensar cómo viajan los modelos generales y qué pasa con los saberes del lugar. El manual trae su propia entrada.

La escena exótica de Boitard sirve para dar «d'agréables souvenirs» a un colono o a un viajero (63). Para explicarla, cuenta la historia de un tahitiano llevado a París que, en el Jardin des Plantes, rompe una empalizada para abrazar un bananero: «c'est mon pays, […] c'est ma cabane» (62–63). El manual sabe que lo exótico es la casa de alguien, y usa esa emoción como efecto para otros. En el frontispicio pone un «cierge du Pérou» en el borde de la lámina (63).

El contraste es una sola consigna más a los mismos modelos: «una escena exótica según Boitard» y «un jardín en La Paz según Boitard», para comparar qué repertorio sacan para cada caso.

**Límite fijado de antemano:** este contraste ocupa un apartado, no un segundo caso. Si pide más, va a la lista de continuaciones.

### 4.6 Decidir

Hay dos puntos de decisión con fecha (§8). En cada uno se anota qué se conserva, qué se cambia, qué se descarta y si la pregunta cambia, con la razón.

---

## 5. Estructura del artículo (unas 8.300 palabras con notas y referencias)

Cada apartado se abre con una pregunta simple, que es la que responde. Quedan unas 700 palabras de margen bajo el máximo de 9.000. En el documento final los títulos van sin negritas y con numeración decimal.

| § | Apartado | Pregunta que lo abre | Palabras | Ejes |
|---|---|---|---|---|
| 1 | **Un acento circunflejo.** La cortina se abre. El jardín, los invitados y el veredicto. | ¿Qué vieron los invitados? | 700 | — |
| 2 | **El manual.** Boitard, los manuales Roret y el lugar del manual entre la *Encyclopédie* y el manual técnico. Las conveniencias. | ¿Qué decía de verdad el libro? | 1.200 | 1 |
| 3 | **La copia anotada.** Boitard y Flaubert lado a lado, con corchetes. El catálogo y la regla. | ¿Qué se llevó la copia y qué dejó? | 1.500 | 2 |
| 4 | **Lo que la tierra se bebe.** Las fallas según su origen y la lámina de los dos jardines. La entrada vacía del «potager pittoresque». | ¿Dónde falló el jardín, y por qué ahí? | 1.300 | 3, 7 |
| 5 | **El quinto copista.** Protocolo y resultados. ¿La máquina copia a Boitard o a Flaubert? | ¿Qué copia una máquina cuando le pedimos «un jardín según Boitard»? | 1.400 | 2, 3, 5 |
| 6 | **Exótico para quién.** El tahitiano, el bananero y el «cierge du Pérou». | ¿Desde dónde es exótico lo exótico? | 600 | 1, 4 |
| 7 | **El que está en el sitio.** Lo posible y lo conveniente. Qué le falta a una respuesta posible para ser una decisión de proyecto, y qué significa para la enseñanza. Vuelta al acento circunflejo. | ¿Quién decide lo que conviene? | 900 | 3, 5 |
| — | Notas y referencias (Chicago autor-fecha 17.ª) | | ~700 | |

**Figuras (6–8):** el frontispicio exótico de Boitard; una o dos láminas de fábricas (tumbas, pagodas, puentes), de dominio público; la copia anotada con corchetes; la lámina de los dos jardines a la misma escala; la tabla de fallas; un mosaico **sin elegir** de las diez salidas de imagen de una misma consigna.

**Sobre el eje 6.** Si entra, entra en una frase del apartado 7: en Chavignolles el agua del estanque se acarrea a mano y se pierde; en una respuesta generada el agua no se ve, porque está en otra parte, en la refrigeración de los centros de datos (Crawford 2021). Si la frase se siente forzada, se quita.

---

## 6. Cómo se va a escribir

**Lenguaje.** Simple, sin pretensión, como alguien que viene de la arquitectura y el diseño gráfico y publica su primer artículo. Frases cortas. Cada término técnico se explica la primera vez («fábrica», «conveniencia», «potager»). Pocos nombres propios por párrafo. Solo citas verificadas, con su página.

**Epígrafe.** Se propone el de la señora Bordin: «Mon Dieu ! quelle bêtise que cet arbre !» (Flaubert 1910, 65). Es corto, está verificado, es la voz de una mujer y es el veredicto del jardín dicho por una vecina. La alternativa sería Boitard, «Nous n'indiquerons aucune règle pour tracer une composition qui n'en a point» (s. f., 116), pero esa frase trabaja mejor dentro del texto, en el apartado 4.

**Una figura que lleva el argumento.** El artículo abre y cierra con el **acento circunflejo**. Al abrirse la cortina, el Rialto de Chavignolles se ve como «un accent circonflexe par-dessus les haricots» (Flaubert 1910, 61): un puente reducido a un signo tipográfico. Es la figura del artículo, porque la copia guarda el signo y pierde la condición. Se puede contar en cuatro Rialtos, en un párrafo cada uno o menos:

1. El de Venecia, que cruza un canal real en una ciudad hecha sobre el agua.
2. El de Chavignolles, sobre un estanque que «la terre buvait» (55), en un jardín que el manual no habría aprobado. Flaubert lo inventa: en Boitard no hay ningún Rialto. La palabra «vénitienne» aparece en el manual solo para una góndola (239–240).
3. El de The Venetian, en Las Vegas (1999), una réplica del puente en un hotel-casino del desierto, con canales artificiales y góndolas: ahí el agua la pone el dinero.
4. Uno generado por un modelo de imagen para la huerta de Normandía, que no necesita agua porque no existe.

El cierre vuelve al acento. Una respuesta generada puede poner el acento sobre cualquier palabra. Saber si esa palabra lo lleva sigue siendo trabajo de quien conoce la lengua, como el jardín lo era de quien está en el sitio.

**Los corchetes.** Son el recurso visual del artículo (§4.2). Muestran la copia en vez de describirla.

**Lo que no se usa.** Nada de *Cosecha de piedras* ni de los trabajos del Altiplano: son otro proyecto. Tampoco la fórmula ni las expresiones propias de Cárcamo Pino: de sus artículos se aprende la construcción, pero la voz tiene que ser la del autor.

**Relación con las propuestas anteriores.** De *Remiendos* vienen las letras de evidencia y la costumbre de fijar antes qué resultado haría caer una hipótesis. De *A pulso* viene leer un manual como partitura: Boitard prescribe qué debe sentir quien mira. En la versión anónima estas referencias se citan como (XXXXX año, pág.) y salen de la lista final. El artículo tiene que sostenerse sin ellas.

---

## 7. Política de IA y transparencia

El artículo usa modelos generativos **como objeto de estudio**, no para redactar. Para cumplir la política de *Astrágalo*:

- se declaran los modelos, las versiones, las fechas, las consignas y el número de salidas;
- las salidas se archivan completas y se ponen a disposición si la revista lo pide;
- se aclara qué figuras son generadas y bajo qué condiciones de uso se publican.

**Esta propuesta.** El cotejo de fuentes y la redacción de este borrador se hicieron con ayuda de Claude (Anthropic). Si algo de este trabajo queda en el artículo, va en la declaración de uso de IA.

---

## 8. Plan de trabajo (hasta el 15 de junio de 2027)

| Fase | Fechas | Trabajo | Entregable | Punto de decisión |
|---|---|---|---|---|
| **Reunir** | nov 2026 | Edición crítica de la novela. Fecha de la edición de Boitard y qué edición tuvo Flaubert (dosieres de lectura). Estudios previos sobre el capítulo II. Política de IA y plantilla. | Corpus y bibliografía. | — |
| **Desarmar** | nov–dic 2026 | Verificar páginas en el facsímil. Segunda lectura de la ficha. Origen de «grave», «mystérieux» y «rêveur». | Ficha verificada. | **D1 (fin de diciembre): H1 y H2.** ¿Se sostienen con la edición correcta y dos lecturas? Si no, se reformula la tesis antes de generar nada. |
| **Proponer** | ene 2027 | Planta reconstruida y lámina de los dos jardines. Copia anotada con corchetes. | 2 láminas y una figura. | ¿La lámina muestra algo que la tabla no muestra? |
| **Ensayar** | feb–mar 2027 | Protocolo de generación, codificación y contraste situado. | Archivo de salidas y tabla de códigos. | **D2 (fin de marzo): H3.** ¿Se sostiene, cambia o cae? |
| **Redactar** | abr–may 2027 | Versión completa. Lectura de una o dos personas de confianza. Figuras y derechos. | Borrador completo. | ¿Queda una objeción seria sin responder? |
| **Consolidar** | 1–15 jun 2027 | Pasar a la plantilla. Chicago autor-fecha. Resúmenes en inglés y portugués. Versión anónima y metadatos. Declaración de IA. Envío. | Dos archivos `.docx` y envío. | — |

---

## 9. Riesgos

| Riesgo | Señal | Respuesta |
|---|---|---|
| **Flaubert usó otra edición**, sin las reglas que se citan | Las citas de Flaubert no coinciden con esta edición, o los dosieres nombran otra | Comparar ediciones Roret en Gallica e Internet Archive. Si las reglas no estaban, H1 cae y vuelve la tesis del borrador 1, que también es publicable. |
| **Alguien ya hizo este cotejo** | Aparece un estudio de fuentes del capítulo II | Se cita, y el aporte pasa a la lectura de proyecto (lo posible y lo conveniente), la lámina y el eslabón de la máquina. Se busca en la fase Reunir. |
| **La máquina sí conoce a Boitard** | En C1 los modelos describen las conveniencias | Es un resultado: H3a cae y el apartado 5 cuenta eso. |
| **El paralelo con la IA se vuelve metáfora** | El apartado 5 se puede escribir sin los datos | Volver al protocolo: el apartado se escribe desde la tabla de códigos. |
| **Expansión** (más episodios, más manuales, más modelos) | Aparece un segundo caso | Regla: un episodio, un manual. Lo demás va a una lista de continuaciones. |
| **Derechos de imágenes generadas** | Términos de uso del modelo | Elegir modelos que permitan publicar. Si no, describir y no reproducir. |
| **Se mezcla con otros proyectos** | Aparecen piedras, Tiwanaku o el Altiplano | Se saca. Este artículo no los necesita. |

---

## 10. Referencias de partida

*Las de la convocatoria van marcadas (C). Las demás se verifican en la fase Reunir antes de citarlas.*

**Fuentes primarias**

- Flaubert, Gustave. 1910. *Bouvard et Pécuchet*. En *Œuvres complètes de Gustave Flaubert*, t. I. París: Louis Conard. Primera edición: París: Lemerre, 1881. (C) *(Para el artículo, pasar a una edición crítica: Pléiade 2021 o GF Flammarion, ed. de Stéphanie Dord-Crouslé, 1999.)*
- Boitard, Pierre. S. f. *Nouveau manuel complet de l'architecte des jardins, ou l'art de les composer et de les décorer*. Nouvelle édition. 2 vols. París: Roret. Ejemplar de la Biblioteca de la Universidad de Sevilla, A 039(a)/018–019, digitalizado en Internet Archive (`A039a018`, `A039a019`). *(Fechar la edición. El catálogo le pone «[1834?]».)*
- Chambers, William. 1772. *A Dissertation on Oriental Gardening*. Londres. *(Solo en el pasaje que Boitard cita.)*

**Convocatoria y marco**

- Diderot, Denis, y Jean Le Rond d'Alembert, eds. 1751–1772. *Encyclopédie*. (C)
- Calatrava Escobar, Juan Antonio. 1988. Tesis doctoral sobre la *Encyclopédie*. (C) *(Verificar título.)*
- Carpo, Mario. 2011. *The Alphabet and the Algorithm*. Cambridge, MA: MIT Press. (C)
- Carpo, Mario. 2023. *Beyond Digital: Design and Automation at the End of Modernity*. Cambridge, MA: MIT Press. (C)
- Crawford, Kate. 2021. *Atlas of AI*. New Haven: Yale University Press. (C)
- Pasquinelli, Matteo. 2023. *The Eye of the Master: A Social History of Artificial Intelligence*. Londres: Verso. (C)
- Bender, Emily M., Timnit Gebru, Angelina McMillan-Major y Shmargaret Shmitchell. 2021. «On the Dangers of Stochastic Parrots: Can Language Models Be Too Big?». En *FAccT '21*, 610–623. Nueva York: ACM. (C)
- Barnes, Julian. 1984. *Flaubert's Parrot*. Londres: Jonathan Cape. (C)

**Sobre la novela** *(a completar con la búsqueda de estudios previos)*

- Foucault, Michel. «Un "fantastique" de bibliothèque». *(Verificar año y edición.)*
- Queneau, Raymond. Prefacio a *Bouvard et Pécuchet*. *(Verificar año y editorial.)*

**Para la figura del acento circunflejo**

- The Venetian Resort, Las Vegas (inaugurado en mayo de 1999). *(Fuentes ya revisadas: WATG, RIBA Journal, Las Vegas Nevada Museum. Elegir una citable.)*

---

## 11. Próximos pasos (dos semanas)

1. **Fechar la edición de Boitard.** Comparar la edición de Sevilla con otras ediciones Roret en Gallica, y buscar en los dosieres de lectura de Flaubert cuál usó. Es lo que más puede cambiar la tesis.
2. **Verificar en el facsímil** las páginas de las 20 citas de Boitard que usa la ficha.
3. **Pedir una segunda lectura** de la tabla de fallas (§4 de la ficha) a alguien que no haya visto la primera.
4. **Leer la política de IA de *Astrágalo*** completa, para ver qué pide declarar cuando la IA es el objeto de estudio.
5. **Elegir el título.** Opciones: *Lo posible y lo conveniente*; *Un acento circunflejo sobre los porotos*; *El jardín de Chavignolles: lo que la copia deja fuera*.
