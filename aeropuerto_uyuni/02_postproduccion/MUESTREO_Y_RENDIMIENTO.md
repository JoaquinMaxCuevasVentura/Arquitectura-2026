# Muestreo y rendimiento en Cycles: revisión del análisis y prueba en la escena

Un análisis del funcionamiento interno de Cycles propone una configuración base de render. Cubre:
- muestreo adaptativo y tope de muestras;
- eliminación de ruido en animación;
- poligonaje y BVH;
- transparencias con alfa;
- clamp;
- volúmenes, cáusticas y Fast GI;
- el visor.

Aquí se prueba qué parte vale para estos renders: imágenes fijas de arquitectura, en Blender 5.2.2, con Cycles en una CPU de 4 núcleos.

- **Herramientas:** `01_blender/herramientas/prueba_muestreo.py` (los renders) y `hoja_muestreo.py` (los números y las hojas).
- **Hojas:** `01_blender/fotorrealismo/Prueba_muestreo_CAM07.jpg` y `Prueba_vidrio_sol_noche_poligonos.jpg`.

**En resumen:**
1. **El umbral de ruido es la única palanca que ahorra tiempo de verdad.** Con 0,03, el render es 3,8 veces más rápido que con nuestro 0,008, a cambio del doble de error en el detalle fino. Sirve para borradores y revisiones; no para los finales.
2. **En los finales, el tope de muestras decide la calidad del edificio, no el umbral.** El 22 % de los píxeles llega al tope de 384. Con 1024 tarda un 69 % más y el error baja un 20 %.
3. **Lo demás del análisis no ahorra tiempo en esta escena:**
   - el mínimo de 16 muestras;
   - los rebotes cortos, que además oscurecen un poco;
   - apagar las cáusticas reflectivas, que oscurece un 2,5 %.

   El *path guiding*, que no está en el análisis, cuesta un 39 % más sin mejorar nada.
4. **El poligonaje casi no pesa en el tiempo:** 170 veces más triángulos tardaron lo mismo. Pesa en la memoria: unos 94 bytes por triángulo en Cycles.
5. **De noche, el clamp indirecto va en 10, no de 3 a 5 como decía la receta anterior.** Con 4, las ventanas encendidas y sus reflejos en el piso mojado pierden un 16 % de luz. Para Cycles, el interior visto a través del vidrio es luz indirecta.
6. **El vidrio es el hallazgo importante:**
   - en Cycles, el sol no lo atraviesa;
   - el vidrio elegido deja pasar 2,9 % de la luz.

   Con eso, la estructura interior que pide ver el arquitecto no se va a ver de día. Para lo primero hay una receta; lo segundo hay que confirmarlo con el cliente (sección 3).

## 1. La prueba

**Vista:** CAM_07 con P2, letrero A, a 1280 × 720. P2 es la más exigente en rebotes por el blanco integral.

**La referencia (R) son los ajustes de los renders finales:**
- umbral de ruido 0,008, tope de 384 muestras y mínimo automático;
- rebotes 12/6/6/12 (total, difusos, especulares, transmisión) y 8 transparentes;
- clamp directo 0 e indirecto 8;
- las dos cáusticas encendidas, como vienen;
- OIDN con albedo y normal, prefiltro `ACCURATE`.

Cada variante cambia solo lo suyo.

**Cómo se mide el error:**
- Se mide sobre la imagen final, ya con la transformación de vista, en niveles de 8 bits (de 0 a 255). Es una media cuadrática: un error de 1 es un nivel promedio de diferencia.
- R2 es R con otra semilla. Lo que cambia entre R y R2 es el ruido que le queda a R.
- Las demás variantes usan la semilla de R y comparten sus primeras muestras, así que su ruido se parece al de R. Por eso se comparan contra R2, que es independiente, y se descuenta el ruido de R. El resultado estima el error contra la imagen convergida.

| Variante | Tiempo | Muestras por píxel (media) | Píxeles en el tope | Error | En celosía y letrero | Luminancia |
|---|---|---|---|---|---|---|
| **R · referencia (los finales)** | 209 s | 206 | 22 % | 0,56 | 1,3 y 1,2 | — |
| U3 · umbral 0,03, tope 2048, mínimo 16 (la receta del análisis) | 54 s (×0,26) | 47 | 0 % | 1,03 | 2,6 y 1,9 | igual |
| U3B · umbral 0,03 con tope 384 y mínimo automático | 55 s (×0,27) | 59 | 0 % | 0,98 | 2,5 y 1,9 | igual |
| U3SD · U3 sin eliminación de ruido (la receta del análisis para animación) | 57 s (×0,27) | 47 | 0 % | 3,27 | 3,6 y 4,6 (portal: 5,5) | igual |
| RB · rebotes 4/2/2/4 | 215 s (×1,03) | 205 | 22 % | 0,60 | 1,3 y 1,3 | de −0,3 a −0,7 % |
| SC · sin cáusticas reflectivas | 221 s (×1,06) | 206 | 23 % | 1,08 | 1,8 y 2,7 | de −2,5 a −2,8 % |
| PG · *path guiding* | 290 s (×1,39) | 198 | 20 % | 0,59 | 1,3 y 1,3 | igual |
| R1K · tope 1024 | 353 s (×1,69) | 290 | 6 % | 0,44 | 1,0 y 0,9 | igual |

**Muestras por píxel en R** (pase `Debug Sample Count`):
- **El cielo no tiene ruido.** El fondo visto de frente no se muestrea, así que el cielo se detiene en el mínimo (80 muestras), con error 0.
- **El asfalto:** mediana de 224 muestras; el 14 % llega al tope.
- **El edificio es el que gasta:** la celosía llega al tope de 384 en el 62 % de sus píxeles y el portal, en el 40 %. En toda la imagen, el 22 % de los píxeles llega al tope. Con el tope de 1024, solo el 6 %.

**Poligonaje** (CAM_05 a 960 px y 128 muestras; las letras subdivididas con *Simple*, que no cambia la forma):

| | Triángulos | Tiempo total | Preparación (sincronizar y BVH) | Render | Memoria del proceso | Memoria de Cycles |
|---|---|---|---|---|---|---|
| Letras tal cual | 0,07 M | 77 s | 1 s | 76 s | 967 MB | 121 MB |
| Letras subdivididas (nivel 6) | 11,7 M | 80 s | 9 s | 71 s | 2591 MB | 1216 MB |

Las dos imágenes son iguales: difieren en 0,5 niveles, lo que da el ruido. El render no cambió. Subieron la preparación, 8 s, y la memoria: 1,1 GB en Cycles, unos 94 bytes por triángulo.

**Noche** (CAM_03 de la prueba nocturna, 1280 px, 128 muestras con umbral 0,01; contra el render sin clamp):

| Clamp indirecto | Tiempo | Luminancia total | Zonas oscuras | Zonas medias | Zonas claras: ventanas y sus reflejos |
|---|---|---|---|---|---|
| Sin clamp (0) | 201 s | — | — | — | — |
| **10** | 170 s | −0,7 % | −0,1 % | −0,4 % | −1,1 % |
| 4 (la receta anterior) | 159 s | −10,3 % | −1,4 % | −4,4 % | **−16,1 %** |

**Luciérnagas, en la imagen con ruido** (antes de OIDN):
- **Las fuertes** (más de 1 por encima de su valor limpio) son las mismas en los tres: 4 píxeles en toda la imagen.
- **Los valores sueltos moderados** (más de 0,3 por encima) sí bajan con el clamp: 745 píxeles sin clamp, 549 con 10 y 60 con 4. Pero OIDN ya los limpia.
- En la imagen final, lo único que cambia es la luz que se pierde. Con 128 muestras y OIDN, esta escena no tiene un problema de luciérnagas que justifique bajar el clamp.

## 2. Revisión del análisis, punto por punto

| Lo que propone | En nuestra escena | Qué hacemos |
|---|---|---|
| **El ruido es varianza: el muestreo adaptativo congela los píxeles que ya convergieron** | Correcto. El cielo se detiene en el mínimo con error 0, el asfalto en una mediana de 224 muestras y el edificio gasta el tope | Muestreo adaptativo siempre encendido |
| **Umbral de ruido 0,03 como "punto óptimo"** | 3,8 veces más rápido que nuestro 0,008 (55 s contra 209 s). Duplica el error en el detalle fino: celosía 2,5 contra 1,3 niveles. Al 200 % casi no se distingue; la diferencia ×8 muestra dónde está | **0,03 para borradores y revisiones con el cliente.** En los finales, de 0,008 a 0,01: el error cae justo en el detalle que el cliente mira, las celosías y el letrero |
| **"Cada décima menos duplica o triplica el tiempo"** | Aquí el tiempo crece casi en proporción: de 0,03 a 0,008 (×3,75) tardó ×3,8 | Regla práctica: el tiempo es proporcional a 1/umbral |
| **Max Samples es un techo para las zonas difíciles, no las muestras de toda la imagen** | Correcto. Con 0,008, el 22 % de los píxeles (el edificio) llega al tope de 384: ahí manda el tope, no el umbral. Con 1024 tarda un 69 % más y el error baja un 20 % (letrero, de 1,2 a 0,9) | En la GPU, tope de 1024. En la CPU de la nube, 384 es un buen compromiso |
| **Min Samples = 16** | Cycles igual hace 32. Frente al mínimo automático (48 con umbral 0,03), el error es algo mayor (1,03 contra 0,98) por el mismo tiempo. Con pocas muestras, el ruido estimado de cada píxel es él mismo ruidoso, y algunos píxeles se detienen antes de tiempo | Mínimo en 0, que es el automático |
| **En animación, sin eliminación de ruido y con semilla animada: el ruido se ve como grano de película** | Que el denoise cuadro a cuadro parpadea es cierto: no ve los cuadros vecinos. Lo del grano no se sostiene aquí. Con 0,03 y sin denoise, el error sube a 3,3 niveles (5,5 en el portal oscuro). Es un moteado de color concentrado en las sombras y en los materiales oscuros: no se parece al grano parejo de una película | En las fijas, OIDN siempre. Para el video del dron, ver la sección 4 |
| **El poligonaje casi no pesa: el BVH busca en tiempo logarítmico** | Correcto en tiempo: 170 veces más triángulos (11,7 M) tardaron lo mismo en el render. La preparación subió de 1 a 9 s y la memoria de Cycles, de 0,12 a 1,2 GB (unos 94 bytes por triángulo) | Los assets de Poly Haven no son un problema de tiempo. En la GPU, el límite es la memoria: los repetidos (personas, autos, matas) van como instancias |
| **Transparencia con alfa: cada capa es un rebote transparente; al llegar al límite, negro** | Correcto. Hoy la escena no tiene ningún material con alfa | Con follaje o personas recortadas: Transparent de 16 a 32, y revisar que no haya manchas negras donde se superponen. En los primeros planos, mejor geometría real |
| **Clamp directo en 0** | Correcto: el directo lleva los brillos del sol en el vidrio y en la chapa | Directo en 0, siempre |
| **Clamp indirecto en 10, sin bajarlo de más** | Correcto, y aquí se ve por qué. De noche, con 4, las ventanas encendidas y sus reflejos pierden un 16 %: el interior que se ve a través del vidrio y lo que refleja el piso mojado son luz indirecta para Cycles. Con 10 pierden un 1 % y el render es un 15 % más rápido que sin clamp. Las luciérnagas fuertes no cambian; OIDN limpia las demás | De día, 8 (no hay diferencia práctica con 10). De noche, 10 |
| **Volume Bounces en 0; subir Max Steps si un VDB muestra cortes** | No hay volúmenes. En 5.2, `volume_max_steps` sigue existiendo (1024 por defecto) | Para la bruma del horizonte, el pase Mist en el compositor, no un volumen |
| **Cáusticas reflectivas apagadas** | No ahorra tiempo (221 s contra 209 s) y oscurece el edificio de 2,5 a 2,8 %. Apaga el brillo de todas las superficies después del primer rebote (vidrio, chapa, pintura satinada, incluso el asfalto), no solo las cáusticas nítidas | Encendidas, como vienen |
| **Cáusticas refractivas encendidas si hay vidrio** | No alcanza. En Cycles, el vidrio con transmisión es opaco para los rayos de sombra, y el sol no lo atraviesa, con las cáusticas encendidas o apagadas, y aun sin clamp (sección 3) | Encendidas, y el vidrio transparente para los rayos de sombra donde se vea el interior (sección 3) |
| **Rebotes cortos: total de 2 a 4, difusos 1 o 2** | No ahorra tiempo (215 s contra 209 s): al aire libre, los caminos ya terminan solos en el cielo. Oscurece un poco (de −0,3 a −0,7 %). Con muros claros o en interiores, la pérdida sería mayor | 12/6/6/12, como hasta ahora |
| **Fast GI apagado** | Correcto: reemplaza la luz indirecta lejana por un AO y aplana | No se usa |
| **Visor sin eliminación de ruido** | Correcto con OIDN en la CPU, que demora cada movimiento de la cámara. Con OptiX en la GPU, la demora es mínima | Al encuadrar: apagado, o con *Start Sample* de 8 a 16 |
| ***Path guiding*** (no está en el análisis; solo funciona en la CPU) | 39 % más de tiempo con el mismo error. De día, al aire libre, no hay luz difícil que aprender | Apagado. Solo valdría la pena en interiores o con luz que entra por aberturas |

## 3. El vidrio y la luz que lo atraviesa

El análisis pide dejar encendidas las cáusticas refractivas cuando hay vidrio. En esta escena eso no alcanza.

**Qué hace Cycles:**
- Para iluminar un punto, traza un rayo de sombra hacia cada luz: el sol, el cielo y las lámparas.
- Un vidrio con transmisión corta ese rayo: para la luz directa es opaco. Pasa con un Principled con `Transmission` 1, también con `Thin Wall`.
- La luz solo puede llegar por el otro camino: el rayo que rebota en el piso, atraviesa el vidrio y encuentra el sol por casualidad. Es una cáustica refractiva.
- Con un sol de medio grado y un vidrio casi liso, eso no pasa nunca en la práctica, ni siquiera sin clamp.

**La prueba** (escena aparte, en `prueba_muestreo.py`):
- un muro con una ventana de 2 × 2 m: una mitad abierta y la otra con el vidrio del modelo;
- el sol de la mañana, a 46,5°, entra al piso de adentro;
- se mide cuánto sol suma la mancha detrás del vidrio, contra la de la mitad abierta.

| Variante | Sol que pasa por el vidrio |
|---|---|
| VC1 · el vidrio del modelo, cáusticas refractivas encendidas (como vienen) | 0 % |
| VC0 · cáusticas refractivas apagadas | 0 % |
| VC1N · encendidas y sin clamp | 0 % |
| VST0 · vidrio transparente para los rayos de sombra, cáusticas apagadas | 4,3 % |
| VST1 · vidrio transparente para los rayos de sombra, cáusticas encendidas | 4,6 % |

En VC1, la mancha detrás del vidrio queda tan oscura como la sombra del muro: es la base contra la que se miden las demás.

**El vidrio elegido deja pasar 2,9 % de la luz** (VT: sin sol y con el cielo negro, la cámara mira un panel uniforme por las dos mitades).
- Es la transmitancia de los dos paños del DVH juntos: cada cara del paño de 27 mm deja pasar el tinte `#6E808E` (≈ 21 % en luminancia), menos lo que refleja la capa.
- Un DVH con lámina de control solar suele dejar pasar entre 20 y 50 % de la luz visible; los más oscuros, de 10 a 20 %.
- Con 2,9 %, la estructura no se va a ver de día aunque se modele y se ilumine el interior: desde afuera, el vidrio es casi opaco.

**Con la misma capa de baja reflexión, medido:**

| Tinte | Deja pasar |
|---|---|
| `#6E808E` (el elegido, variante 6) | 2,9 % |
| `#8E9FAD` (intermedio) | 7,2 % |
| `#A9BCCB` (el de la variante 3) | 15,1 % |

**Qué significa para el proyecto:**
1. **Hoy no se nota.** Detrás del vidrio hay un interior básico con luz propia (`INTERIOR_PISO` e `INTERIOR_LUZ`), que no depende del sol.
2. **Para "vislumbrar la estructura interna"** que pide el arquitecto (`TRASPASO.md`, sección 5, punto 12) hacen falta tres cosas:
   - modelar las columnas y vigas cercanas a la fachada, a partir del IFC;
   - que el sol y el cielo entren: vidrio transparente para los rayos de sombra (receta abajo);
   - que el vidrio deje pasar una fracción realista. **Hay que confirmarlo con el cliente**, porque validó el aspecto actual. Propuesta: el tinte `#A9BCCB` con la misma capa (15 %), probado antes en CAM_05 y CAM_07. De día, el vidrio va a seguir viéndose oscuro, porque el interior está mucho más oscuro que la calle.
3. **De noche pasa lo mismo al revés:** la luz del interior no sale por el vidrio a la vereda ni al alero. Con el vidrio transparente para los rayos de sombra, la vereda junto a las ventanas recibe el resplandor del interior, uno de los rasgos de una foto nocturna real.

**Receta: vidrio transparente para los rayos de sombra**
- En una copia del material del vidrio, `Light Path` > `Is Shadow Ray` va al factor de un `Mix Shader`: arriba, el Principled de siempre; abajo, un `Transparent BSDF`.
- **Color del `Transparent BSDF`:** la transmitancia de cada cara. El paño es una caja, así que el rayo de sombra lo cruza dos veces.
  - Con el color del tinte, pasa un 4,3 %.
  - Para que la sombra coincida con lo que ve la cámara (2,9 %), el color es el tinte × 0,82, que es lo que no refleja la capa.
- **Cáusticas refractivas encendidas.** Así entra también la luz que rebota afuera, en el suelo y en los muros. Con ellas, la mancha sumó 0,3 puntos (4,6 contra 4,3 %): no hay doble conteo que preocupe.
- La cámara ve el vidrio igual que antes: solo cambian las sombras y la luz que pasa.
- El costo de render no cambia.

## 4. Ajustes de render para este proyecto

Ya están en la sección 8 de `GUIA_REALISMO_FOTOGRAFICO.md`.

| Parámetro | Borradores y revisiones | Finales de día | Finales de noche |
|---|---|---|---|
| Umbral de ruido | 0,03 | 0,008 | 0,005 |
| Tope de muestras | 384 | 384 en la CPU; 1024 en la GPU | de 512 a 1024 |
| Mínimo de muestras | 0 (automático) | 0 | 0 |
| Rebotes: total, difusos, especulares, transmisión | 12 / 6 / 6 / 12 | igual | igual |
| Transparentes | 8; de 16 a 32 si hay follaje o personas con alfa | igual | igual |
| Clamp directo / indirecto | 0 / 8 | 0 / 8 | 0 / 10 |
| Cáusticas reflectivas y refractivas | encendidas | encendidas | encendidas |
| *Light tree* | sí | sí | sí |
| *Path guiding* | no | no | no |
| Fast GI | no | no | no |
| Eliminación de ruido | OIDN con albedo y normal, prefiltro `ACCURATE` | igual | igual |
| Filtro | 1,5 px | igual | igual |
| Semilla | fija | fija | fija |

**Vidrio:** donde se vea el interior, vidrio transparente para los rayos de sombra (sección 3).

**Video del dron** (600 cuadros, en la GPU del usuario):
- **Semilla animada.** Con la semilla fija, el ruido que queda se pega a la pantalla mientras la cámara se mueve.
- **OIDN con albedo y normal**, umbral de 0,01 y tope de 512.
- **Antes del video completo, 2 s de prueba (48 cuadros) en dos versiones:** con OIDN y sin él. Se elige mirándolas en movimiento, no en un cuadro suelto.
  - Si con OIDN las zonas lisas "hierven", sube el tope o baja el umbral.
  - Si no alcanza, renderiza sin OIDN y elimina el ruido después, con un filtro temporal (DaVinci Resolve Studio o Neat Video).
- **Sin eliminación de ruido y con umbral 0,03, como propone el análisis, no:** en esta escena queda un moteado de color en las sombras (sección 2).

**Para ahorrar tiempo sin perder calidad**, por orden:
1. Umbral 0,03 en todo lo que no sea final.
2. Resolución al 50 % para los encuadres.
3. Renderizar en franjas, para retomar si el proceso se corta (`render_banda.py` y `unir_bandas.py`).

**Lo que no conviene:** bajar los rebotes, apagar las cáusticas, el mínimo de 16, el *path guiding* y, de noche, el clamp bajo. En esta escena no ahorran tiempo, o ahorran poco, y los rebotes cortos, las cáusticas apagadas y el clamp bajo oscurecen.

## 5. Para la otra IA

Pégalo cuando llegue al paso 9 del plan (`PROMPT_CONTINUACION.md`). El vidrio va antes, en el paso 5. Adjunta las dos hojas de `01_blender/fotorrealismo/`.

```text
Siguiente etapa: ajustes de render, con lo medido en 02_postproduccion/MUESTREO_Y_RENDIMIENTO.md (léelo completo). La herramienta de la prueba es 01_blender/herramientas/prueba_muestreo.py; las hojas de resultados te las adjunto.

1. Perfiles de render por código: una función que aplique a las tres escenas uno de estos perfiles (sección 4):
   - "borrador": umbral 0,03, tope 384, mínimo automático;
   - "final_dia": umbral 0,008, tope 1024 (en la GPU);
   - "final_noche": umbral 0,005, tope 1024, clamp indirecto 10.
   Lo demás, igual en los tres:
   - rebotes 12/6/6/12 y transparentes 8;
   - clamp directo 0 e indirecto 8 (10 de noche);
   - cáusticas encendidas y light tree;
   - OIDN con albedo y normal (ACCURATE) y filtro de 1,5 px.
2. No bajes los rebotes, no apagues las cáusticas, no uses un mínimo de 16 ni path guiding, y de noche no bajes el clamp: en esta escena no ahorran tiempo y oscurecen (con clamp 4, las ventanas encendidas pierden un 16 %).
3. Vidrio (sección 3): el sol no lo atraviesa en Cycles.
   - Cuando modeles la estructura detrás del vidrio, usa el vidrio transparente para los rayos de sombra, con el color de la receta (tinte × 0,82) y las cáusticas encendidas.
   - Muéstrame antes y después en CAM_05, en CAM_07 y, de noche, en CAM_03, donde la luz del interior tiene que salir a la vereda.
4. El vidrio elegido deja pasar 2,9 %, y con eso la estructura no se ve de día. No cambies el tinte sin preguntarme. Prepárame la comparación con #A9BCCB y la misma capa (15 %) en CAM_05 y CAM_07, para mostrársela al cliente.
5. Video del dron: semilla animada, OIDN con albedo y normal, umbral 0,01 y tope 512. Antes del video completo, renderiza 2 s con OIDN y sin él, y elige mirándolos en movimiento.
6. Cuando agregues assets con alfa (follaje, personas recortadas): Transparent de 16 a 32, y revisa que no aparezcan manchas negras donde se superponen. Los objetos repetidos, como instancias.

Entrega:
- la función de perfiles;
- CAM_07 en borrador y en final, con sus tiempos;
- el antes y el después del vidrio;
- la comparación de los dos tintes.
```
