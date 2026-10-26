# Bitácora

Cada entrada registra qué movimiento se hizo (**reunir · desarmar · proponer · ensayar · contrastar · decidir · consolidar**), qué se decidió (**conservar · modificar · descartar · cambiar la pregunta**), por qué y cuál es la siguiente acción. Los movimientos no van en orden: hay retornos.

---

### 26-10-2026 · 1 · Reunir: el encargo
- **Hecho**: se leyeron las bases oficiales (XIV edición, mesas, cierre el 31-01-2027) y el catálogo de materiales de Porada. → [`00_encargo/`](00_encargo/)
- **Hallazgo de procedimiento**: el concurso exige proyectos **inéditos y anónimos**, y este repositorio es **público**.
- **Decisión**: no publicar el diseño hasta que el autor decida la visibilidad (O7).
- **Siguiente acción**: el autor decide.

### 26-10-2026 · 2 · Reunir: las fuentes
- **Hecho**: en Internet Archive se reunieron Bertonio (1612/1879), Semper (1851, 1879), Squier (1877), Viollet-le-Duc (1873), *Wood Handbook* (2010) y Kessler (1919), todos con página y captura. Monoskop no fue accesible desde este entorno. → [`01_reunir/fichero.md`](01_reunir/fichero.md)
- **Siguiente acción**: desarmar.

### 26-10-2026 · 3 · Contrastar con la fuente → cambiar la pregunta (E5)
- **Hecho**: en Bertonio, *Chakhua* (montón) y *Chhakhua* (piedra hincada donde se atan los palos, y también los palos atados) son **dos entradas** (F01). El artículo las da como un solo nombre.
- **Decisión**: **cambiar la pregunta**. La pregunta deja de ser «cómo pesa la piedra sobre la madera» y pasa a ser **«cómo se une la madera a una piedra fija»**. El lastre se queda sin su palabra.
- **Siguiente acción**: revisar Bertonio 2011, p. 330, y corregir el artículo si corresponde (O1).

### 26-10-2026 · 4 · Desarmar y proponer
- **Hecho**: se desarmaron 5 imágenes y 13 fuentes. Diagnóstico: **las referencias visuales tiran hacia la masa y el concurso, hacia el armazón de madera**. Se fijaron criterios K1-K10 y cuatro versiones (V0 lastre, V1 llave, V2 hincada, V3 control).
- **Prerregistro**: los umbrales de los ensayos se fijaron **antes** del instrumento, en el commit `7e6165b`.

### 26-10-2026 · 5 · Ensayar, ronda 1 → descartar tres de cuatro
- **E1**: la barra de V0 llega a 9,9 MPa frente a 2,3 → **V0 descartada**.
- **E2**: V2 exige acuñar el montante → **«hincar» deja de ser la acción**.
- **E3**: con la geometría de partida, el lastre **sí** ayudaba (+40 %), pero no bastaba. La **geometría** lo resuelve mejor y vale para todas → **corrección común: pie de 180 mm**. Se eligió alargar el pie y no acercar el caballete para no quitar sitio a las rodillas en las cabeceras.
- **E4**: la llave de mármol no cabe en la espiga (necesita 53-75 mm, caben 37). La de fresno cabe con 14-19 mm. El peso de la llave es el 0,6 % del rozamiento → **V1 descartada; se retira «el peso traba»**.
- **K5**: falla en **todas** por el tablero de 59 kg en una sola pieza. Es un problema común, no de la piedra.
- **Siguiente acción**: derivar versiones donde la madera cargue la piedra (V0b) y donde la piedra trabaje solo a compresión (V4).

### 26-10-2026 · 6 · Ensayar, ronda 2 → la piedra no se justifica por la estructura
- **Resultado**: V0b y V4 cumplen K1-K4. En V4 la piedra trabaja a 0,08-0,17 MPa de compresión y reparte el apoyo de la llave (0,64 → 0,08 MPa). Con la geometría corregida, la condición prerregistrada se cumple y **se retira «la piedra estabiliza»**.
- **Contraste incómodo**: el control **V3 cumple lo mismo sin piedra**. En ninguna versión la piedra es necesaria para la estructura.
- **Decisión**: **modificar el concepto**. La frase del borrador («la gravedad de la piedra sostiene la ligereza del armazón») queda retirada por E1, E3, E4 y E5. Formulaciones candidatas que **sí** sostienen las fuentes y los cálculos, para que elija el autor:
  1. «La madera sostiene y se mueve; la piedra queda fija y recibe la unión» (E2, E4, F01).
  2. «La madera atraviesa la piedra» (V4, en sentido literal).
- **Siguiente acción**: E6, el nodo V4 a 1:1 junto al V3, para decidir si la piedra se queda por razones que el cálculo no mide.

### 26-10-2026 · 7 · Retorno: el autor advierte que predeterminó el concepto
- **Hecho**: el autor señala que, al fijar de antemano piedra + *chhaxwa*, el proceso pudo quedar inclinado hacia un resultado.
- **Lectura**: los ensayos sí contradijeron el borrador (E1, E4, E5), pero todas las versiones seguían discutiendo **dónde va la piedra**. Ninguna podía proponer que el problema fuera otro.
- **Decisión**: **abrir una propuesta B** con otra entrada al problema, sacada de la misma bibliografía, con su propio prerregistro y medida con el mismo instrumento y los mismos criterios. Después se comparan A y B, y se busca una síntesis si son compatibles. → [`03_proponer/propuesta_B.md`](03_proponer/propuesta_B.md)

### 26-10-2026 · 8 · Proponer y ensayar B, ronda 3 → modificar
- **Hecho**: el prerregistro de B se fijó antes de calcular (commit `38a6dc6`). B1, la lectura literal de Viollet-le-Duc (tablas posadas), falla E8 (flecha de 5,8 mm), E9 (una tabla suelta vuelca con 219 N) y E2b (la tabla debe medir ≤ 182 mm). Cumple K5, que en A falla siempre.
- **Hallazgo no buscado**: la **cuña vuelve** en B por una razón propia (E9), no por el concepto.
- **Decisión**: **modificar** → B2: 6 tablas de 164 mm, clavija acuñada, lengüetas sueltas y apoyo central.

### 26-10-2026 · 9 · Ensayar, ronda 4 → A y B son compatibles
- **Resultado**: B2 cumple todo lo aplicable sin piedra. AB (tablero de B2 + collar de V4) cumple K1-K5.
- **Contraste**: las reglas de A y B son la misma vista desde dos lados: la madera se mueve; la piedra no. → [`03_proponer/sintesis.md`](03_proponer/sintesis.md)
- **Decisión**: **no cerrar todavía**. La elección entre B2 y AB depende de lo que el cálculo no mide: E6 (¿el collar se lee como unión?) y E10 (¿las juntas molestan en el uso?). Además hacen falta E7 (originalidad) y las decisiones del autor sobre el mármol, el nombre (O6) y la frase del concepto.
- **Siguiente acción**: construir las dos maquetas 1:1 (el nodo collar/llave y tres tablas de 600 mm) y revisar los compendios 2017-2018.

### 26-10-2026 · 10 · Reunir de nuevo: precedentes (E7) → modificar el argumento
- **Pedido del autor**: mirar a los ganadores de Porada y de concursos afines para mejorar las dos propuestas.
- **Hallazgo**: Porada ya celebra «l'incontro tra legno e marmo» (*Oswood*, *Osmose*). El jurado premia el macizo trabajado, los arquetipos, los componentes con individualidad, la intercambiabilidad y el material de acento en la unión. → [`01_reunir/precedentes.md`](01_reunir/precedentes.md)
- **Decisión**: **modificar el argumento**. Lo que distingue a A es que la piedra trabaja como unión, no la combinación de materiales. A B se le agrega **B3**, una tabla de servicio intercambiable con mármol asentado, y la **familia** banco-consola-mesa. Quedan dos síntesis posibles (AB y B3), que conviene no sumar en la misma mesa.
- **Herramienta**: el autor pide **Blender en la nube** (Geometry Nodes, materiales procedurales) y descarta Rhino. El prerregistro de E6a y E10a (lectura visual con renders) se fija antes de renderizar.

### 26-10-2026 · 11 · Consolidar una herramienta: Blender en la nube
- **Pedido del autor**: modelar las pruebas en Blender, en la nube y desde su GitHub (Geometry Nodes, materiales procedurales); Rhino se descarta.
- **Hecho**: `bpy` 5.2.3 corre sin pantalla en el contenedor. Un solo árbol de Geometry Nodes («Mesa Porada») genera B2, AB, B3 y la familia (banco, consola, mesa) a partir de los parámetros del instrumento. Cada pieza lleva un atributo de veta para orientar la fibra. Los mármoles procedurales son de catálogo (Nero Sahara Noir y Marrone Emperador Dark). Se agrega un workflow de GitHub Actions para renderizar en la nube. → [`instrumentos/blender/`](instrumentos/blender/README.md)
- **Para qué sirve, y para qué no**: sirve para la lectura visual previa (E6a, E10a, con su [hoja de prueba](04_ensayar/E6a_E10a_hoja.md)) y para la base de la lámina 3. No sirve para medir peso, montaje ni uso: eso queda para las maquetas.
- **Siguiente acción**: el autor hace E6a y E10a con 5 personas; después vienen E6 y E10 físicos.
- **Renders listos** (10 tomas, Cycles a 48 muestras, ~2 min cada una en CPU) → [`05_consolidar/renders/`](05_consolidar/renders/). El primer material de nogal se descartó porque de cerca se leía como chapa ondulada; se cambió por fibra fina antes de la tanda final.
- **Observación no prerregistrada** (se anota como tal, no como resultado de un ensayo): a la distancia de la vista general, **el collar de AB casi no se ve**: AB y B2 se parecen mucho. En B3, el mármol de la tabla de servicio sí se lee a esa distancia. Si la piedra tiene que ser *el punto fijo* de la mesa, en AB solo lo es de cerca. **Pregunta para E6a**: ¿alcanza con que la unión se lea de cerca, o el collar tiene que crecer?

### 26-10-2026 · 12 · Reunir y contrastar: materiales bolivianos → modificar el filtro, descartar el nudo por gravedad (E11)
- **Pedido del autor**: evaluar una dirección material boliviana con un triple filtro (Porada, mecánico, poético). Opción 1: nogal andino (*Juglans neotropica*) + andesita de Comanche. Opción 2: morado + travertino. Incluye una «síntesis operativa» del nudo: la piedra baja por gravedad, abre dos tirantes y bloquea las patas.
- **Contraste con fuentes** → [`01_reunir/materiales_bolivianos.md`](01_reunir/materiales_bolivianos.md):
  - El nogal de los Yungas es *J. boliviana*, no *J. neotropica*; esta última está **En Peligro** (UICN). *J. boliviana* se describió primero como *J. nigra* var. *boliviana*: es pariente del noce canaletta de Porada.
  - La ley departamental de La Paz (2012) llama a la piedra de Comanche **granito**, no andesita. La andesita de Tiwanaku se atribuye al cerro Khapia.
  - El morado es sensibilizante, pesa 1,5 veces lo que el nogal y crece lento; el travertino ya está en el catálogo de Porada.
- **E11** (prerregistrado en `924e6a0` antes de calcular): la cuña empuja como máximo 538 N y el balanceo pide 1023 N; además la piedra se mueve 6,9 mm entre estaciones → **descartar** la síntesis operativa.
- **Decisión**:
  - **Modificar el filtro mecánico**: «la piedra trabaja solo a compresión, asentada o apretada por la madera, nunca pegada ni a flexión; las holguras se calculan y se dejan».
  - **Conservar** el nogal canaleta para producir; lo andino entra como vínculo botánico verificado, no como material.
  - **Proponer** el granito de Comanche apomazado como piedra candidata del collar de AB, pendiente de muestra y ficha.
  - **Descartar** la opción 2 en su forma propuesta.
- **Herramienta**: se agrega una piedra ígnea gris mate genérica al árbol de Blender (no es el granito de Comanche: no hay muestra) y se renderizan el nodo y la vista general de AB con ella, para que E6a compare las dos piedras.
- **Observación no prerregistrada** (los renders `nodo_AB_ignea` y `general_AB_ignea`): de cerca, la piedra mate se lee como **masa**, sin la veta que en el Nero Sahara llama la atención por sí misma. A distancia general, las dos piedras son una mancha oscura del mismo tamaño: **el problema de visibilidad del collar no lo cambia la piedra, lo cambia su tamaño**. E6a dirá si «masa» se entiende como «lo que traba».
- **Siguiente acción**: el autor elige; si va con Comanche, conseguir una muestra y su ficha (SERGEOMIN; EN 1926, EN 12372) y hacer E6a con las dos piedras.
