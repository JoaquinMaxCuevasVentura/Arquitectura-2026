# Lo posible y lo conveniente

## El jardín de Bouvard y Pécuchet, su manual y la respuesta plausible

*Propuesta de artículo para* Astrágalo *A44 (2027), «Bouvard & Pécuchet. Arquitectura y desencanto: de la Enciclopedia a la inteligencia artificial». Borrador 3, 19 de octubre de 2026 (revisado esa noche con las pruebas piloto, la nota de lectura de Flaubert y la lectura de los estudios previos). Reemplaza al borrador 2, que queda en `/mnt/project-files/propuesta/archivo/` y en el historial de la rama.*

> **Convocatoria.** Editor: José Enrique López Canti (Universidad de Sevilla). Envío hasta el **15 de junio de 2027**; publicación prevista en septiembre de 2027. Plantilla oficial y ficha de evaluación en `/mnt/project-files/convocatoria/`.
>
> **Forma:** de 5.000 a 9.000 palabras **contando notas y referencias**; Chicago autor-fecha, 17.ª ed., con página exacta en toda cita literal; tres resúmenes de hasta 250 palabras (español, inglés, portugués), sin notas; hasta 5 palabras clave en minúsculas, mejor del Tesauro de la UNESCO; dos archivos, uno anónimo, con las autocitas como (XXXXX año, pág.); figuras dentro del texto como «Fig. X», con derechos; títulos sin negritas ni mayúsculas, con numeración decimal; declaración de uso de IA. Revisión por doble ciego con doce criterios, entre ellos originalidad, método y rigor en el análisis de fuentes.

---

## 0. Qué cambió desde el borrador 2

Las pruebas y sus criterios, escritos antes de hacerlas, están en [`analisis/Bitácora de decisiones.md`](analisis/Bitácora%20de%20decisiones.md).

1. **Ya había estudios sobre el manual.** Stéphanie Dord-Crouslé (2003) siguió las notas de lectura de Flaubert sobre Boitard a través de los borradores. Patrick Feyler (2006) escribió que la novela omite las precauciones con que Boitard acompañaba sus consejos. Jeffrey Thomas (2019) comparó el ex-voto con el manual. La idea central del borrador 2, que la copia se queda con el catálogo y deja las reglas, **ya no es el hallazgo del artículo. Pasa a ser su punto de partida, citado.** El aporte se mueve a lo que esos estudios no hacen: medirlo elemento por elemento, dibujarlo como proyecto y llevar la copia hasta una máquina.
2. **La edición está fechada.** El ejemplar de Sevilla no es de 1834. Es una segunda edición vendida hacia 1859. Las reglas que importan, como las conveniencias, el rechazo de los géneros y Chambers como contraejemplo, ya estaban en el primer libro de jardines de Boitard, de 1825. El riesgo mayor del borrador 2, que Flaubert hubiera leído un Boitard sin reglas, queda muy reducido.
3. **Las páginas están verificadas** en el facsímil. Cambiaron seis.
4. **Dos hallazgos nuevos en el cotejo.** El ex-voto copia un pasaje que Thomas no cita, y la copia deja su condición: «Dans un site très-pittoresque, montagneux». El género «mystérieux», que parecía inventado, sale con toda probabilidad de una caverna de Boitard, que según él no se puede construir.
5. **Arquitectura y diseño gráfico, donde ayudan.** La planta a escala pasa de figura a prueba: dice qué fallas son de sitio. La copia anotada se vuelve una lámina de cotejo. Cada imagen dice de dónde viene.
6. **H2 pasó la segunda lectura.** Dos lectores que no vieron la primera clasificación marcan como advertidas las mismas 6 de 9 fallas. Además coinciden en que 5 de las 9 dependen de la posición o la escala, así que la planta queda como prueba.
7. **Las pruebas piloto con IA cambiaron H3.** Con el capítulo IV en la mano, el modelo no repite el recorte de los copistas: hace de cura, aun cuando se le pide la lista de Bouvard y Pécuchet. Sin el libro, le atribuye a Boitard los géneros que él rechazaba, sacados de la tradición y no de Flaubert. H3 se reescribe (§3). Como los modelos que generaron veían la memoria del proyecto, el protocolo completo se hará en sesiones limpias, con una consigna nueva: pedir como ellos (§4.4).
8. **Hay un borrador 0 del artículo** ([`articulo/Borrador 0.md`](articulo/Borrador%200.md)), escrito como prueba de la estructura. Los apartados 1 a 4 se sostienen con citas verificadas y entran en su extensión. El 5 queda como esqueleto hasta tener datos, que es lo que debía pasar.
9. **La planta tiene sus datos** ([`analisis/planta - datos del texto.md`](analisis/planta%20-%20datos%20del%20texto.md)): todas las posiciones que da Flaubert, la lámina 18 de Boitard y una medida. El tilo tumbado ocupa «toute la longueur du jardin» (Flaubert 1910, 56), así que el jardín mide, en una dirección, lo que un árbol.
10. **La nota de Flaubert y los estudios, leídos** (bitácora, P1 cierre). La nota de lectura (Carnet 18 bis) ya es catálogo, sin conveniencias ni condiciones: la regla se pierde al leer, como había mostrado Dord-Crouslé (2003). Los borradores agregan dos cosas que los estudios leídos no señalan: el filtro de lo posible está desde el primero (f. 171), y en el de la cena Bouvard le responde al cura convirtiendo la conveniencia en gusto (f. 190). Ningún estudio cuenta las fallas del jardín ni lo dibuja. Leclerc (2019) hace algo vecino con los fracasos agrícolas y queda como antecedente de método.

---

## 1. La idea en tres frases

1. En el capítulo II de *Bouvard et Pécuchet*, dos copistas jubilados arman un jardín con un manual en la mano, y el jardín fracasa delante de sus invitados.
2. El manual advertía casi todas esas fallas, pero la copia se quedó con la lista de objetos y dejó las reglas que decían dónde, cuándo y para quién sirve cada uno. Eso ya lo vieron los estudios sobre la novela.
3. Este artículo lo mira como arquitecto: dibuja el jardín a escala para ver qué reglas eran de sitio, y le pide el mismo jardín a una máquina para ver si repite el recorte.

### Resumen provisional (unas 220 palabras)

En el capítulo II de *Bouvard et Pécuchet*, los dos copistas transforman su huerta de Normandía siguiendo *L'Architecte des jardins* de Pierre Boitard, un manual práctico de la colección Roret. Levantan una tumba etrusca de yeso, un Rialto sobre un estanque sin agua, una pagoda y una roca de piedras pegadas con cemento. Ante sus invitados, el jardín fracasa. Los estudios de la novela ya mostraron que Flaubert, desde sus notas de lectura, dejó fuera las precauciones del manual. Este artículo lo lee desde la arquitectura. Compara la novela con el manual elemento por elemento y muestra que el libro advertía casi todas las fallas. Pedía estudiar el terreno, prohibía las rocas artificiales en un terreno llano, mandaba esconder las tumbas de la vista de la casa y declaraba que la huerta burguesa adornada no tenía reglas. Después dibuja el jardín a escala junto al modelo que el manual daba para un caso igual, y ve cuáles de esas reglas eran de sitio. Los copistas se preguntaron qué era posible; el manual, qué era conveniente. Por último, pide el mismo jardín a modelos generativos, con y sin el texto del manual, para ver si la respuesta plausible repite ese recorte. La conclusión discute qué le falta a una respuesta posible para ser una decisión de proyecto, y por qué el manual dejaba la última palabra a quien está en el sitio.

**Palabras clave (provisionales):** jardines, manuales, copia, inteligencia artificial, Flaubert. *(Contrastar con el Tesauro de la UNESCO.)*

*El resumen se traduce al inglés y al portugués después del punto de decisión D1.*

---

## 2. El caso

### 2.1 La escena

Con la herencia de Bouvard, los dos copistas compran una granja con casa y huerta en Chavignolles, Normandía. Al llegar, la huerta tiene dos alamedas en cruz, legumbres en los arriates, «des cyprès nains et des quenouilles» y un muro con espalderas (Flaubert 1910, 26). Meses después, tras fracasar con los frutales, se prometen ahorrar «leur peine et leur argent» (53), pero los árboles muertos dejan «des intervalles fort vilains» en el huerto (54). Pécuchet hace varios dibujos con su estuche de dibujo, «ils n'arrivaient à rien de satisfaisant», y entonces encuentran en su biblioteca *L'Architecte des jardins* de Boitard (54).

Con el libro arman, con un solo peón y poca plata, una tumba etrusca de yeso negro con «l'apparence d'une niche à chien», un Rialto sobre un estanque que no retiene el agua, una cabaña a la que le queman el techo de paja «pour la rendre plus poétique», una pagoda china de troncos y hojalata, y una roca de granitos pegados con cemento, «pareil à une gigantesque pomme de terre» (55–56). Talan el tilo más grande, casi muerto, y lo tienden a lo largo del jardín para que parezca «renversé par la foudre» (56).

Después invitan a cenar a los notables del pueblo. A los postres se abren las cortinas y el jardín aparece: «C'était, dans le crépuscule, quelque chose d'effrayant». La tumba es «un cube au milieu des épinards» y el puente veneciano, «un accent circonflexe par-dessus les haricots» (61). Nadie entiende la tumba, ni la cabaña quemada, ni el muro en ruinas. El cura, al irse, le dice a Pécuchet que no encuentra «convenable ce simulacre de tombeau au milieu des légumes» (64). La señora Bordin se engancha el vestido en el tilo: «Mon Dieu ! quelle bêtise que cet arbre !» (65).

### 2.2 El libro

El manual existe. Es el *Nouveau manuel complet de l'architecte des jardins* de Pierre Boitard, de la *Librairie encyclopédique de Roret*, una colección de manuales prácticos para todos los oficios. Está digitalizado en Internet Archive, texto y atlas de láminas. El ejemplar es **de la Biblioteca de la Universidad de Sevilla** (A 039(a)/018–019), la misma universidad que publica *Astrágalo*.

El catálogo de Sevilla le pone «[1834?]», que es el año de la primera edición. El libro se presenta como «seconde édition», y lleva encuadernados catálogos de Roret de junio de 1859. Es, entonces, una segunda edición vendida hacia 1859. Flaubert leyó el manual entre 1872 y 1874. Las reglas que este artículo cita ya estaban en el primer libro de jardines de Boitard (1825, 5–6), así que cualquier edición a su alcance las traía.

El manual Roret es un eslabón entre la *Encyclopédie* y el manual técnico moderno. Ordena un saber en capítulos, láminas y recetas, y lo vende barato para que cualquiera lo aplique. Es, en pequeño, la promesa de la que habla la convocatoria: que más información disponible mejore la capacidad de decidir y construir.

### 2.3 Lo que mostró el cotejo

Flaubert copia a Boitard casi literalmente, con cambios pequeños que se pueden marcar. Entre [corchetes], lo que la copia cambió. En la última columna, lo que la copia dejó.

| Boitard (s. f.) | Flaubert (1910) | Lo que quedó fuera |
|---|---|---|
| «un ex-voto marquant la place où un chevalier est tombé sous le fer d'un assassin» (72) | «un ex-voto [à la vierge], [indiquant] la place où un [seigneur] est tombé sous le fer d'un assassin» (54) | «Dans un site très-pittoresque, montagneux» (72) |
| «faire naître d'agréables souvenirs à un colon ou à un voyageur» (63) | «[pour] faire naître [des] souvenirs à un colon ou à un voyageur» (54) | En Francia, la escena dura «quatre ou cinq mois de l'année au plus» (65) |
| «caractérisent le genre terrible et mystérieux de ces voûtes effrayantes», con musgos (229) | «de la mousse et des grottes, le genre [mystérieux]» (54) | La caverna no se construye: la regla es para quien ya tiene una (229; 1825, 109) |
| «ces jeux bizarres, ou si l'on aime mieux de ces jeux d'enfans» (73) | «[le plus beau spécimen] se voyait naguère dans un jardin wurtembergeois» (54) | «Sous ce titre, qui n'est pas trop convenable» (73) |
| «C'est sur le principe erroné de l'unité de genre, que les auteurs ont échafaudé leur classification des jardins» (55) | «L'auteur les divise en une infinité de genres» (54) | Todo el párrafo: Boitard rechaza los géneros (55–57) |

El cotejo completo está en [`analisis/concordancias Flaubert-Boitard.md`](analisis/concordancias%20Flaubert-Boitard.md). Muestra tres cosas:

1. **La copia se queda con el catálogo.** De 13 elementos del jardín, 9 tienen correspondencia directa en el manual: la tumba, la cabaña, la pagoda, la roca, el laberinto y otros. Lo que no pasa al jardín son las reglas que acompañan a cada uno.
2. **Las fallas están donde estaba la regla.** Sobre el terreno llano, Boitard escribe: «Gardez-vous bien de ces roches factices, monceaux de pierres ridicules, qui semblent tombées du ciel au milieu d'un gazon» (50). La tumba debe quedar donde no se la vea «d'aucune partie du bâtiment» (69). Y el «genre terrible» que copian, con árboles fulminados y cabañas quemadas, viene de un pasaje de Chambers que Boitard cita como ejemplo de lo absurdo: «Je demande si des hommes de bon sens peuvent donner de telles absurdités pour les règles» (20).
3. **El manual tenía una entrada para su caso, y estaba vacía.** Boitard llama «potager pittoresque» a la huerta burguesa adornada, que «appartient le plus souvent à des négocians retirés» (29). Al llegar a ella escribe que es «le produit du caprice et du mauvais goût» y que «Nous n'indiquerons aucune règle pour tracer une composition qui n'en a point» (116).

### 2.4 Lo que ya se sabe y lo que falta

| Estudio | Qué hace | Qué se toma | Qué no hace |
|---|---|---|---|
| Dord-Crouslé 2003 | Compara la nota de lectura de Flaubert (Carnet 18 bis) con Boitard, pasaje por pasaje, y sigue el párrafo de los géneros por cinco etapas de borradores. Dice que Flaubert calla las conveniencias y que, con los consejos del manual, los personajes no habrían hecho ese jardín (párr. 19–20). | H1 entera, como premisa. La nota: la regla ya falta ahí. | Probar su frase falla por falla y dibujar el jardín. |
| Feyler 2006 | Dice que el resumen de Flaubert omite las precauciones de Boitard (párr. 49). Describe la cruz de alamedas del jardín que encuentran (7–8). | La observación, como premisa citada. La cruz, para la planta. | Dar medidas y contar qué se pierde y dónde falla. |
| Thomas 2019 | Compara el ex-voto con un pasaje de Boitard que no es el más cercano. Nota que los vidrios de color no vienen del manual. | La idea de una sugerencia leída como obligación. | Ver la condición que la copia deja. |
| Leclerc 2019 | Sigue los fracasos agrícolas del mismo capítulo por informantes, notas y borradores hasta su causa. | El método. Y la respuesta de Maurice Sand, que Flaubert no aprovechó: «chaque faute est spéciale au milieu où l'on opère». | El jardín y el manual. |

Ninguno de los estudios encontrados cuenta las fallas del jardín, lo dibuja o sigue la copia hasta una máquina. Ese es el lugar del artículo. *(Dord-Crouslé y Feyler se leyeron en OpenEdition, por párrafos; antes de citarlos textual hay que cotejar con el PDF y dar la página impresa.)*

**La cadena tiene más eslabones.** Entre el manual y la novela hay una nota de lectura y varios borradores ([ficha, §0](analisis/concordancias%20Flaubert-Boitard.md)). La nota ya es catálogo; del rechazo de los géneros queda un «on a inventé des genres» que los borradores vuelven «L'auteur les divise». El primer borrador ya filtra por lo posible: los copistas encuentran en Chambers y en Boitard «bien des choses impossibles» y «se résignent à faire» (Ms g 225-2, f. 171). Y en un borrador de la cena, Bouvard le responde al cura con la otra palabra: «est-ce qu'on n'a pas le droit de bâtir dans son domaine ce qui vous plaît ? si celui-là ne vous convient pas tant pis» (f. 190). La conveniencia llega al final de la cadena, pero como gusto.

### 2.5 Lo posible y lo conveniente

Antes de construir, Bouvard y Pécuchet revisan los géneros del manual uno por uno. El fantástico les parece «réservé aux princes», el templo sería «encombrant» y las plantas americanas cuestan demasiado. «Mais les rocs étaient possibles» (Flaubert 1910, 55). Su filtro es **lo posible**: lo que alcanza con la plata, el trabajo y el espacio que tienen.

El filtro del manual es otro: **lo conveniente**. Boitard llama «convenances» a la regla sin la cual «on ne créera que des compositions ridicules ou absurdes» (49). Son tres: que la obra vaya con el lugar, con su tiempo y con las costumbres de quienes la habitan. Para el jardín chico de una casa modesta lo dice así: hay que ponerlo en armonía con la casa y «avec les goûts et la fortune du propriétaire, convenances qui sont de première considération» (116). En este artículo se traduce como **conveniencia**, en el sentido antiguo de decoro: lo que conviene a un lugar, a un tiempo y a una gente.

El cura, al despedirse, juzga el jardín con la palabra del manual. Es la escena en pocas líneas: los copistas preguntaron qué era posible y los vecinos respondieron con lo que era conveniente.

La inteligencia artificial generativa vuelve actual esta diferencia. Un modelo siempre puede responder con algo posible. La pregunta de proyecto es si responde algo conveniente, y quién decide eso. El propio Boitard deja la última palabra a una persona: «C'est à l'artiste placé sur les localités à sentir et apprécier ces nuances» (226).

---

## 3. Pregunta e hipótesis

**Pregunta.** Cuando un saber de proyecto pasa de un manual a sus lectores, y de ahí a una máquina que genera respuestas, ¿qué se conserva y qué se pierde? ¿Se pierde siempre lo mismo?

Cada hipótesis dice antes de la prueba qué resultado la haría caer. Lo que no vale es mover los criterios después de ver los datos.

**H1. La copia se queda con el catálogo** *(premisa, ya señalada por Feyler 2006 y Dord-Crouslé 2003; aquí se mide)*. Bouvard y Pécuchet copian los objetos y los efectos del manual, y dejan las reglas que los acompañan.

- *Cómo se prueba:* la ficha de concordancias, con páginas verificadas.
- *Cae si:* las reglas pasan a la copia tanto como los objetos, o si la edición que usó Flaubert no traía esas reglas.
- *Estado:* se sostiene. La edición ya no es un riesgo serio, porque las reglas están en 1825 y en la segunda edición. La nota de Flaubert ya no trae las reglas: el corte está en la lectura. Falta ver la primera edición del *Manuel* (1834), que no se encontró digitalizada.

**H2. Las fallas están donde estaba la regla.** Las fallas del jardín ocurren donde el manual había puesto una advertencia que la copia no tomó.

- *Cómo se prueba:* se clasifican las 9 fallas que narra Flaubert y se busca si el manual las advertía, con dos lecturas independientes. Después, la planta a escala (§4.3) muestra cuáles son de sitio.
- *Cae si:* menos de la mitad de las fallas tienen una advertencia previa según las dos lecturas.
- *Estado:* se sostiene. Las tres lecturas (la mía y dos lectores automáticos que no vieron la mía) dan las mismas 6 de 9 advertidas. Hay 7 de 9 coincidencias exactas; las diferencias son dos fallas que ellos dejan como dudosas. Falta una lectura humana antes de D1.

**H3. Lo plausible borra la excepción** *(reescrita después de dos pruebas piloto; bitácora, P5 y P8)*. Tiene dos partes:

- **H3a, sin la fuente.** Si se le pregunta por el manual sin dárselo, el modelo le atribuye a Boitard una clasificación por géneros, la misma que Boitard rechazaba, y no menciona las conveniencias. No la saca de Flaubert sino de la tradición de los tratados de jardines. Lo plausible es la media de esa tradición, y Boitard era la excepción. *Cae si* la mayoría de las respuestas a C1 mencionan las conveniencias o el rechazo de los géneros. *Piloto:* 2 de 2 la sostienen, y ninguna nombra a Flaubert.
- **H3b, con la fuente.** Con el capítulo IV en la consigna, el modelo no hace de copista sino de cura: aplica las conveniencias y objeta los elementos con las reglas del manual, también cuando se le pide como lo pidieron Bouvard y Pécuchet (C5). *Cae si* la mayoría de las salidas de C3, C4 o C5 de cualquiera de los modelos ejecutan la lista o aplican menos de dos reglas al sitio. *Piloto:* 6 de 6 la sostienen.
- **Lo que se dejó atrás.** La versión anterior decía que, aun con el capítulo IV, el modelo entregaba el catálogo y dejaba las reglas. Cayó en los dos pilotos. Si el protocolo limpio la recupera, se vuelve a ella y se dice.
- **Lo imprevisto.** Todas las salidas que proponen un diseño piden datos del sitio, y casi todas dicen qué no saben. La máquina sabe que no está en el lugar. Bouvard y Pécuchet, que sí estaban, no lo preguntaron.
- *Estado:* hipótesis de trabajo para D2. Los pilotos no son datos: un solo tipo de modelo, de la misma familia que ayudó a escribir esta propuesta, en un entorno que tenía la memoria del proyecto.

Las tres hipótesis valen aunque caigan. Si cae H3, el artículo dirá que el modelo no repite el recorte, y en qué condiciones.

### Lo que este artículo no afirma

- No afirma que una máquina «piense» como Bouvard y Pécuchet. Compara **procedimientos**: tomar un repertorio y usarlo sin las reglas de su uso.
- No juzga a Boitard. Al contrario: muestra que el manual era más lúcido que sus lectores.
- No pretende haber descubierto que Flaubert recorta a Boitard. Eso ya está dicho. Lo mide, lo dibuja y lo prueba con otra clase de copista.
- No mide el costo ambiental de los modelos. El eje 6 de la convocatoria aparece en una sola frase, si el caso la pide (§5).
- No habla de «la IA» en general. Los resultados del protocolo valen para esos modelos, con esas consignas, en esa fecha.

---

## 4. Método

El método es el habitual del autor (reunir, desarmar, proponer, ensayar, contrastar, decidir), con contrastes elegidos para un artículo de teoría con un ensayo proyectual. Cada instrumento existe porque resuelve una dificultad concreta, y se dice cuál. Lo que viene de la arquitectura y del diseño gráfico entra solo donde resuelve algo.

### 4.1 La ficha de concordancias

**Dificultad que resuelve:** sin ella, la relación entre Flaubert y Boitard se queda en una cita suelta, y H1 y H2 no se pueden probar.

Está hecha y verificada. Usa letras de evidencia adaptadas de *Remiendos*: **F** (está en Flaubert), **B** (está en Boitard), **C** (Chambers citado por Boitard), **I** (inferencia) y, más adelante, **G** (generado por un modelo). La ficha separa la nota de lectura, los borradores y el texto publicado (§0 de la ficha). La regla ya falta en la nota.

### 4.2 La copia anotada, como lámina de cotejo

**Dificultad que resuelve:** decir «Flaubert copia a Boitard» no muestra nada. Hay que ver la copia, y ver también lo que quedó fuera.

Es la parte de diseño gráfico del artículo. Los textos van alineados en tres columnas: Boitard, Flaubert y la máquina. El texto de origen va en gris, lo cambiado en negro y entre [corchetes], y la condición que la copia dejó va al margen, tachada con una línea fina. Así se ve de un golpe qué se tomó, qué cambió y qué no se tomó. El mismo recurso sirve para las salidas de los modelos. Las columnas se alinean por fila, elemento por elemento, como las columnas de datos del *Naturgemälde* de Humboldt (1807).

Cada imagen del artículo lleva en el pie qué es: propia, de dominio público (Boitard, Flaubert), propuesta de la máquina o pendiente de permiso. Esto ayuda a cumplir lo que pide la revista sobre derechos de figuras.

### 4.3 La planta: dos jardines a la misma escala

**Dificultad que resuelve:** la tabla de fallas dice *que* el manual advertía, pero no dice si la falla es de sitio. Algunas solo se ven en planta: la tumba a la vista de la casa, la roca en un terreno llano, el laberinto en un jardín chico. Para verlas hay que **dibujar el sitio**.

- **Planta reconstruida** del jardín de Chavignolles con todo lo que el capítulo dice de posiciones: la cruz de alamedas, la «charmille» (un paseo de árboles podados en seto), la espaldera, el «vigneau» (un montículo), la «tonnelle» (el emparrado), la escalinata, la celosía al fondo, el granero. Lo que da el texto va en línea continua y lo que hubo que suponer, en punteado, con su letra de evidencia.
- **Visuales.** Desde las ventanas del comedor, que es desde donde los invitados ven el jardín al abrirse la cortina, se trazan las líneas de vista. Así se comprueba la regla de la tumba, que no debía verse «d'aucune partie du bâtiment» (Boitard s. f., 69).
- Al lado, a la misma escala, el **jardín de Wissous** de la lámina 18 de Boitard. Es su modelo para un terreno de no más de un arpent, junto a la casa modesta de un hombre de letras, con la huerta «masqué de manière à n'être pas aperçu» (116). Es la respuesta del manual para un caso como este.
- **Primero a mano.** La planta se dibuja a mano. Una versión digital se hace solo si agrega algo, por ejemplo para medir.
- **Convenciones gráficas** ([`analisis/referencias graficas.md`](analisis/referencias%20graficas.md)): el agua como circuito que no cierra, a la manera de los dibujos de Luis F. Benedit para el Fitotrón (1972); la vista que se revela, como en las solapas de Repton (1816); lo que se ve desde el comedor, trazado como isovista (Benedikt 1979); los dos jardines redibujados a una sola escala, como en Durand (1799–1801); cada fuente en su color (F negro, B sepia, I rojo) y en amarillo lo que la regla pedía y la copia no hizo. Benedit es referencia de método: su obra tiene derechos y no va como figura.
- **Regla de decisión, fijada antes.** La planta entra al artículo si al menos 4 de las 9 fallas dependen de la posición o de la escala según los dos lectores de H2. Si quedan menos, se reduce a una figura chica. **Resultado:** 5 de 9, con acuerdo de los dos lectores en las nueve (la roca, la tumba, el árbol, el eco y el conjunto). La planta queda. Además, la lámina tiene que mostrar de un vistazo qué recomendaba el manual y qué se hizo; si no lo muestra mejor que la tabla, se descarta.

### 4.4 El protocolo de generación

**Dificultad que resuelve:** sin protocolo, la parte sobre inteligencia artificial sería una ilustración elegida a gusto, y H3 no podría caer.

**Consignas**, escritas y archivadas antes de generar:

| | Consigna | Prueba |
|---|---|---|
| C1 | «¿Cómo clasifica Pierre Boitard los jardines en *L'Architecte des jardins*?» | H3a |
| C2 | «Diseña un jardín para una huerta en Normandía según *L'Architecte des jardins* de Boitard.» | H3a, y base de comparación para H3b |
| C3 | La consigna C2 más el texto del capítulo IV de Boitard, «Des convenances et des scènes» (49–75), pegado en la consigna. | H3b |
| C4 | La consigna C3 más las condiciones del sitio que da Flaubert: huerta en uso, terreno llano, agua acarreada, casa a la vista, poca plata. | H3b |
| C5 | **Pedir como ellos.** El capítulo IV, las mismas condiciones y la lista de Bouvard y Pécuchet: tumba etrusca, puente veneciano sobre un estanque, cabaña, pagoda, roca y el tilo tumbado «como por un rayo». «¿Cómo lo hacemos?» | H3, la forma de pedir |

**Modelos:** dos modelos de texto de empresas distintas y un modelo de imagen (este último solo para C2 y C4), con nombre, versión y fecha registrados. Diez salidas por consigna y por modelo, todas, sin elegir.

**Sesiones limpias.** Cada salida se genera en una sesión nueva, sin memoria, sin instrucciones personales y sin historial, por API o con una cuenta creada para eso. Se archiva el contexto del sistema de cada sesión. La prueba piloto mostró por qué: los modelos que generaron veían la memoria de este proyecto, y eso se notaba en las respuestas (bitácora, P5).

**Códigos**, la misma lista para todas las salidas. El libro de códigos completo está en la bitácora.

- *Catálogo:* géneros nombrados, fábricas propuestas (tumba, puente, pagoda, roca, ruina, cabaña…), efectos prometidos.
- *Regla:* estudio del sitio; conveniencias; terreno llano; agua; tamaño del jardín; tumba lejos de la casa; nada de rocas artificiales; el «potager pittoresque» sin reglas; el rechazo de los géneros.
- *Atribución:* le atribuye a Boitard la clasificación por géneros; le atribuye el «genre terrible» de Chambers; nombra a Flaubert sin que se lo pidan.
- *Objeción anticipada:* defiende una mezcla incoherente con un argumento listo, como hace Boitard cuando aconseja responder con el jardín botánico de Calcutta a quien objete su escena exótica (65).
- *Sitio y duda* (agregados después del piloto): pide datos del lugar antes de cerrar el diseño; dice qué no sabe.
- *Ejecuta o juzga* (para C5): da instrucciones para construir la lista; objeta un elemento con una regla de lugar, de tiempo o de costumbres.

**Codificación ciega.** Dos personas codifican sin saber qué consigna produjo cada salida. Se informa el acuerdo entre ellas.

**Qué demuestra y qué no.** El protocolo muestra cómo responden estos modelos a estas consignas en esta fecha. No demuestra nada sobre la inteligencia artificial en general, y el artículo lo dice así. Los pilotos sugieren que, para la máquina, la regla no se pierde por la forma de pedir: se pierde cuando falta la fuente. El protocolo completo lo confirma o lo corrige.

### 4.5 Contraste situado: ¿exótico para quién?

**Dificultad que resuelve:** el eje 4 de la convocatoria pide pensar cómo viajan los modelos generales y qué pasa con los saberes del lugar. El manual trae su propia entrada.

La escena exótica de Boitard sirve para dar «d'agréables souvenirs» a un colono o a un viajero (63). Para explicarla, cuenta la historia de un tahitiano llevado a París que, en el Jardin des Plantes, rompe una empalizada para abrazar un bananero: «c'est mon pays, […] c'est ma cabane» (62–63). El manual sabe que lo exótico es la casa de alguien, y usa esa emoción como efecto para otros. En el frontispicio pone un «cierge du Pérou» en el borde de la lámina (63).

El contraste es una sola consigna más a los mismos modelos: «una escena exótica según Boitard» y «un jardín en La Paz según Boitard», para comparar qué repertorio sacan para cada caso.

**Límite fijado de antemano:** este contraste ocupa un apartado, no un segundo caso. Si pide más, va a la lista de continuaciones.

### 4.6 Decidir

Hay dos puntos de decisión con fecha (§8). En cada uno se anota en la bitácora qué se conserva, qué se cambia, qué se descarta y si la pregunta cambia, con la razón.

---

## 5. Estructura del artículo (unas 8.300 palabras con notas y referencias)

Cada apartado se abre con una pregunta simple, que es la que responde. Quedan unas 700 palabras de margen bajo el máximo de 9.000. En el documento final los títulos van sin negritas y con numeración decimal.

| § | Apartado | Pregunta que lo abre | Palabras | Ejes |
|---|---|---|---|---|
| 1 | **Un acento circunflejo.** La cortina se abre. El jardín, los invitados y el veredicto. | ¿Qué vieron los invitados? | 700 | — |
| 2 | **El manual.** Boitard, los manuales Roret, la edición y el lugar del manual entre la *Encyclopédie* y el manual técnico. Las conveniencias. Lo que ya dijeron los estudios. | ¿Qué decía de verdad el libro? | 1.200 | 1 |
| 3 | **La copia anotada.** La lámina de cotejo. La nota, los borradores y la novela. El catálogo y la regla. | ¿Qué se llevó la copia y qué dejó? | 1.300 | 2 |
| 4 | **Lo que la tierra se bebe.** Las fallas según su origen y la planta de los dos jardines. La entrada vacía del «potager pittoresque». | ¿Dónde falló el jardín, y por qué ahí? | 1.500 | 3, 7 |
| 5 | **El quinto copista.** Protocolo y resultados. Sin el libro, ¿la máquina copia a Boitard, a Flaubert o a la tradición? Con el libro, ¿hace de copista o de cura? | ¿Qué copia una máquina cuando le pedimos «un jardín según Boitard»? | 1.400 | 2, 3, 5 |
| 6 | **Exótico para quién.** El tahitiano, el bananero y el «cierge du Pérou». | ¿Desde dónde es exótico lo exótico? | 600 | 1, 4 |
| 7 | **El que está en el sitio.** Lo posible y lo conveniente. Qué le falta a una respuesta posible para ser una decisión de proyecto, y qué significa para la enseñanza. Vuelta al acento circunflejo. | ¿Quién decide lo que conviene? | 900 | 3, 5 |
| — | Notas y referencias (Chicago autor-fecha 17.ª) | | ~700 | |

**Figuras (6–8):** el frontispicio exótico de Boitard; una o dos láminas de fábricas (tumbas, pagodas, puentes), de dominio público; la lámina de cotejo; la planta de los dos jardines a la misma escala; la tabla de fallas; un mosaico **sin elegir** de las diez salidas de imagen de una misma consigna.

**Sobre el eje 6.** Si entra, entra en una frase del apartado 7: en Chavignolles el agua del estanque se acarrea a mano y se pierde; en una respuesta generada el agua no se ve, porque está en otra parte, en la refrigeración de los centros de datos (Crawford 2021). Si la frase se siente forzada, se quita.

---

## 6. Cómo se va a escribir

**Lenguaje.** Simple, sin pretensión, como alguien que viene de la arquitectura y el diseño gráfico y publica su primer artículo. Frases cortas. Cada término técnico se explica la primera vez («fábrica», «conveniencia», «potager»). Pocos nombres propios por párrafo. Solo citas verificadas, con su página.

**Epígrafe.** Se propone el de la señora Bordin: «Mon Dieu ! quelle bêtise que cet arbre !» (Flaubert 1910, 65). Es corto, está verificado, es la voz de una mujer y es el veredicto del jardín dicho por una vecina. La alternativa sería Boitard, «Nous n'indiquerons aucune règle pour tracer une composition qui n'en a point» (s. f., 116), pero esa frase trabaja mejor dentro del texto, en el apartado 4.

**Una figura que lleva el argumento.** El artículo abre y cierra con el **acento circunflejo**. Al abrirse la cortina, el Rialto de Chavignolles se ve como «un accent circonflexe par-dessus les haricots» (Flaubert 1910, 61): un puente reducido a un signo tipográfico. Es la figura del artículo, porque la copia guarda el signo y pierde la condición. Para quien viene del diseño gráfico es también una pregunta de oficio: un diacrítico solo tiene sentido sobre la letra que lo lleva. Se puede contar en cuatro Rialtos, en un párrafo cada uno o menos:

1. El de Venecia, que cruza un canal real en una ciudad hecha sobre el agua.
2. El de Chavignolles, sobre un estanque que «la terre buvait» (55), en un jardín que el manual no habría aprobado. Flaubert lo inventa: en Boitard no hay ningún Rialto. La palabra «vénitienne» aparece en el manual solo para una góndola (239–240).
3. El de The Venetian, en Las Vegas (1999), una réplica del puente en un hotel-casino del desierto, con canales artificiales y góndolas: ahí el agua la pone el dinero.
4. Uno generado por un modelo de imagen para la huerta de Normandía, que no necesita agua porque no existe.

El cierre vuelve al acento. Una respuesta generada puede poner el acento sobre cualquier palabra. Saber si esa palabra lo lleva sigue siendo trabajo de quien conoce la lengua, como el jardín lo era de quien está en el sitio.

**Los corchetes y la lámina de cotejo.** Son el recurso visual del artículo (§4.2). Muestran la copia en vez de describirla.

**Lo que no se usa.** Nada del contenido de *Cosecha de piedras* ni de los trabajos del Altiplano: son otro proyecto. De ellos solo se toma la manera de trabajar. Tampoco la fórmula ni las expresiones propias de Cárcamo Pino: de sus artículos se aprende la construcción, pero la voz tiene que ser la del autor.

**Relación con las propuestas anteriores.** De *Remiendos* vienen las letras de evidencia y la costumbre de fijar antes qué resultado haría caer una hipótesis. De *A pulso* viene leer un manual como partitura: Boitard prescribe qué debe sentir quien mira. En la versión anónima estas referencias se citan como (XXXXX año, pág.) y salen de la lista final. El artículo tiene que sostenerse sin ellas.

---

## 7. Política de IA y transparencia

La política de *Astrágalo* pide que los autores declaren «el uso de cualquier herramienta de IA en la redacción o análisis de sus manuscritos», y que especifiquen «el software utilizado, las funciones aplicadas y las secciones del manuscrito donde se ha empleado» (§3.1). Las herramientas de IA no pueden ser autoras. El autor responde por la originalidad y por revisar sesgos, errores o inexactitudes en lo generado (§3.2–3.3). La política no dice nada de la IA como objeto de estudio. Aquí se lee de la manera más segura: todo se declara.

- **Como objeto de estudio:** se declaran los modelos, las versiones, las fechas, las consignas y el número de salidas. Las salidas se archivan completas y se ponen a disposición si la revista lo pide. Se aclara qué figuras son generadas y bajo qué condiciones de uso se publican.
- **Como ayuda en el análisis y la redacción de esta propuesta:** Claude (Anthropic) hizo el cotejo de fuentes, la verificación de páginas con programas propios y la prueba piloto de las consignas, y redactó los borradores. Si algo de este trabajo queda en el artículo, va en la declaración, con las secciones donde se usó.

---

## 8. Plan de trabajo (hasta el 15 de junio de 2027)

| Fase | Fechas | Trabajo | Entregable | Punto de decisión |
|---|---|---|---|---|
| **Reunir** | nov 2026 | Cotejar con el PDF las citas de Dord-Crouslé (2003) y Feyler (2006). Ver en la *Correspondance* la carta de George Sand del 5 de febrero de 1873. Edición crítica de la novela. Buscar la primera edición del *Manuel* (1834). | Corpus y bibliografía. | — |
| **Desarmar** | nov–dic 2026 | Segunda lectura humana de las fallas. *(La ficha ya está cotejada con la nota de Flaubert y con las imágenes.)* | Ficha cerrada. | **D1 (fin de diciembre): H1 y H2.** ¿Se sostienen con la lectura humana? Si no, se reformula la tesis antes de generar nada. |
| **Proponer** | ene 2027 | Planta a mano y lámina de los dos jardines. Lámina de cotejo. | 2 láminas y una figura. | ¿La planta muestra algo que la tabla no muestra? |
| **Ensayar** | feb–mar 2027 | Protocolo de generación completo, codificación ciega y contraste situado. | Archivo de salidas y tabla de códigos. | **D2 (fin de marzo): H3.** ¿Se sostiene, cambia o cae? |
| **Redactar** | abr–may 2027 | Versión completa. Lectura de una o dos personas de confianza. Figuras y derechos. | Borrador completo. | ¿Queda una objeción seria sin responder? |
| **Consolidar** | 1–15 jun 2027 | Pasar a la plantilla. Chicago autor-fecha. Resúmenes en inglés y portugués. Versión anónima y metadatos. Declaración de IA. Envío. | Dos archivos `.docx` y envío. | — |

---

## 9. Riesgos

| Riesgo | Señal | Respuesta |
|---|---|---|
| **El aporte se parece demasiado a lo ya dicho** | Al leer a Dord-Crouslé o a Feyler aparece un recuento parecido de fallas | Leídos: ninguno cuenta las fallas del jardín ni lo dibuja, y Leclerc (2019) hace algo vecino con la agricultura (bitácora, P1 cierre). El aporte se apoya en el recuento, la planta a escala y la máquina. Si apareciera un recuento, la pregunta cambia hacia la planta y la máquina. |
| **Flaubert usó una edición sin las reglas** | La primera edición (1834) no trae las conveniencias, o las notas de Flaubert citan otra cosa | Muy poco probable: las reglas están en 1825 y en la segunda edición. Si pasara, H1 cae para esas reglas y se dice. |
| **La planta no agrega nada** | Menos de 4 fallas dependen de la posición, o la lámina dice lo mismo que la tabla | Se reduce a una figura chica o se quita (regla de §4.3). |
| **La máquina sí conoce a Boitard** | En C1 los modelos describen las conveniencias | Es un resultado: H3a cae y el apartado 5 cuenta eso. |
| **Los pilotos engañan** | En sesiones limpias o con otros modelos, la máquina ejecuta la lista | Es un resultado: se vuelve a la H3 anterior y se dice. Si los modelos se dividen, el apartado 5 los compara. |
| **El apartado 5 se lee como elogio de la máquina** | «Hace de cura» se lee como «lo hace mejor» | El apartado dice qué no demuestra: aplicar las reglas de un texto no es estar en el sitio, y las mismas salidas lo piden. |
| **El paralelo con la IA se vuelve metáfora** | El apartado 5 se puede escribir sin los datos | Volver al protocolo: el apartado se escribe desde la tabla de códigos. |
| **Expansión** (más episodios, más manuales, más modelos) | Aparece un segundo caso | Regla: un episodio, un manual. Lo demás va a una lista de continuaciones. |
| **Derechos de imágenes generadas** | Términos de uso del modelo | Elegir modelos que permitan publicar. Si no, describir y no reproducir. |
| **Se mezcla con otros proyectos** | Aparecen piedras, Tiwanaku o el Altiplano | Se saca. Este artículo no los necesita. |

---

## 10. Referencias de partida

*Las de la convocatoria van marcadas (C). Las marcadas con \* se conocen por resúmenes o citas y hay que leerlas antes de citarlas.*

**Fuentes primarias**

- Flaubert, Gustave. 1910. *Bouvard et Pécuchet*. En *Œuvres complètes de Gustave Flaubert*, t. I. París: Louis Conard. Primera edición: París: Lemerre, 1881. (C) *(Para el artículo, pasar a una edición crítica: Pléiade 2021 o GF Flammarion, ed. de Stéphanie Dord-Crouslé, 1999.)*
- Boitard, Pierre. S. f. *Nouveau manuel complet de l'architecte des jardins, ou l'art de les composer et de les décorer*. Nouvelle édition [segunda edición]. 2 vols. París: Roret. Ejemplar de la Biblioteca de la Universidad de Sevilla, A 039(a)/018–019, con catálogos de Roret de 1859; digitalizado en Internet Archive (`A039a018`, `A039a019`).
- Boitard, Pierre. 1825. *Traité de la composition et de l'ornement des jardins*. París: Audot. Internet Archive (`TraiteYdelacomp00Boit`).
- Chambers, William. 1772. *A Dissertation on Oriental Gardening*. Londres. *(Solo en el pasaje que Boitard cita.)*
- Flaubert, Gustave. S. f. Carnet de travail 18 bis, ff. 8–9. Bibliothèque historique de la Ville de Paris. *(Visto en el facsímil y la transcripción de Dord-Crouslé 2003.)*
- Flaubert, Gustave. S. f. *Bouvard et Pécuchet*, borradores. Ms g 225-2, ff. 152v, 169, 171, 190 y 194v. Bibliothèque municipale de Rouen. Transcripción en «Les manuscrits de *Bouvard et Pécuchet*», Université de Rouen Normandie, https://flaubert.univ-rouen.fr/manuscrits/.
- Sand, George. 1873. Carta a Gustave Flaubert, 5 de febrero. En Gustave Flaubert, *Correspondance*, t. IV, editado por Jean Bruneau, 643. París: Gallimard, 1998. \* *(Citada por Leclerc 2019.)*

**Sobre el manual en la novela**

- Dord-Crouslé, Stéphanie. 2003. «Flaubert et les Manuels Roret ou le paradoxe de la vulgarisation. L'art des jardins dans *Bouvard et Pécuchet*». En *Le Partage des savoirs (XVIIIe–XIXe siècles)*, editado por Lise Andries, 93–118. Lyon: Presses universitaires de Lyon. https://doi.org/10.4000/books.pul.6576. *(Leído en OpenEdition; cotejar las citas con el PDF.)*
- Feyler, Patrick. 2006. «Bouvard et Pécuchet jardiniers». En *Les mythologies du jardin de l'Antiquité à la fin du XIXe siècle*, editado por Gérard Peylet, 229–242. Eidôlon 74. Pessac: Presses universitaires de Bordeaux. https://doi.org/10.4000/books.pub.27431. *(Leído en OpenEdition; cotejar las citas con el PDF.)*
- Leclerc, Yvan. 2019. «Bouvard et Pécuchet sur leur terre : comment bien rater sans savoir pourquoi». *Revue Flaubert* 18, «Bouvard et Pécuchet et l'agriculture», editado por Stéphanie Dord-Crouslé y Éric Le Calvez. Centre Flaubert, Université de Rouen.
- Thomas, Jeffrey. 2019. «Le jardin face à *Bouvard et Pécuchet*». *Revue Flaubert* 18.

**Convocatoria y marco**

- Diderot, Denis, y Jean Le Rond d'Alembert, eds. 1751–1772. *Encyclopédie*. (C)
- Calatrava Escobar, Juan Antonio. 1988. «Las ideas estéticas en la *Encyclopédie* de Diderot y D'Alembert». Tesis doctoral, Universidad de Granada. (C)
- Carpo, Mario. 2011. *The Alphabet and the Algorithm*. Cambridge, MA: MIT Press. (C)
- Carpo, Mario. 2023. *Beyond Digital: Design and Automation at the End of Modernity*. Cambridge, MA: MIT Press. (C)
- Crawford, Kate. 2021. *Atlas of AI*. New Haven: Yale University Press. (C)
- Pasquinelli, Matteo. 2023. *The Eye of the Master: A Social History of Artificial Intelligence*. Londres: Verso. (C)
- Bender, Emily M., Timnit Gebru, Angelina McMillan-Major y Shmargaret Shmitchell. 2021. «On the Dangers of Stochastic Parrots: Can Language Models Be Too Big?». En *FAccT '21*, 610–623. Nueva York: ACM. (C) *(La frase del «stochastic parrot» está en las pp. 616–617.)*
- Barnes, Julian. 1984. *Flaubert's Parrot*. Londres: Jonathan Cape. (C)

**Sobre la novela**

- Foucault, Michel. 1967. «Un "fantastique" de bibliothèque». *Cahiers de la Compagnie Madeleine Renaud–Jean-Louis Barrault*, n.º 59: 7–30. Publicado antes en alemán (1964). Reeditado en *Dits et écrits* I, texto n.º 20.
- Queneau, Raymond. 1947. Prefacio a *Bouvard et Pécuchet*. París: Éditions du Point du Jour.

**Para la figura del acento circunflejo**

- The Venetian Resort, Las Vegas (inaugurado en mayo de 1999). *(Fuentes ya revisadas: WATG, RIBA Journal, Las Vegas Nevada Museum. Elegir una citable.)*

---

## 11. Próximos pasos

1. ~~Leer a Dord-Crouslé (2003) y a Feyler (2006) completos~~ (hecho en OpenEdition: no mueven el aporte; bitácora, P1 cierre). Queda **cotejar las citas con el PDF** para dar la página impresa: OpenEdition y HAL bloquean la descarga automática, así que hay que bajarlos desde un navegador.
2. ~~Leer las notas de Flaubert~~ (hecho: la nota es catálogo; la ficha separa nota, borradores y texto, §0).
3. ~~Ver en la imagen las tres citas que el OCR no encontró~~ (hecho: están, pp. 75, 239 y 267; y las páginas 5, 6, 108 y 109 del libro de 1825).
4. **Segunda lectura humana** de la tabla de fallas.
5. **Correr el protocolo en sesiones limpias.** Hace falta acceso por API a dos modelos de empresas distintas, o cuentas nuevas sin memoria. Las consignas ya están fijadas en [`analisis/protocolo - consignas.md`](analisis/protocolo%20-%20consignas.md). Es lo que más puede mover el apartado 5.
6. **Elegir el título.** Opciones: *Lo posible y lo conveniente*; *Un acento circunflejo sobre los porotos*; *El jardín de Chavignolles: lo que la copia deja fuera*.
7. **Leer a Le Calvez**, «Paysage mouvant, paysages décrits dans *Bouvard et Pécuchet*» (citado en el n.º 18 de la *Revue Flaubert*), por si dibuja o mide el jardín.
