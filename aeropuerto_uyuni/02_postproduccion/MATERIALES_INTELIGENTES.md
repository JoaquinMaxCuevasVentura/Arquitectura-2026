# Materiales inteligentes en Blender 5.2: revisión de la investigación, prueba y prompt

Este documento sigue al de fotorrealismo (`FOTORREALISMO_BLENDER.md`). Junta tres cosas:
- la revisión de la investigación sobre materiales procedurales "inteligentes" (tutoriales de Kaizen Tutorials y de Dragon Boots Studios), contrastada con Blender 5.2 y con este proyecto;
- una prueba pequeña sobre el modelo;
- el prompt para que otra IA mejore todos los materiales del `.blend` formal.

Un material "inteligente" calcula sus máscaras en el momento del render, a partir de la geometría: aristas (Bevel), cavidades (Ambient Occlusion), orientación (normal) y altura (posición). No necesita mapas UV ni horneado. Es justo lo que pide este proyecto:
- el modelo se genera por código y casi no tiene UV;
- si el script cambia la geometría, los materiales se adaptan solos.

## 1. La prueba (CAM_06 y CAM_05, propuesta 1)

**Hoja de resultados:** `01_blender/fotorrealismo/Prueba_materiales_CAM06_CAM05.jpg`.

**Herramienta:** `01_blender/herramientas/prueba_materiales.py`. Aplica las máscaras sobre una copia del modelo (propuesta 1, letras corten) y renderiza tres cosas:
- el antes;
- el diagnóstico de las máscaras;
- el después.

El antes y el después usan la luz corregida de la prueba de fotorrealismo (×0,6) y las verticales rectas.

| Técnica | Qué se hizo | Resultado |
|---|---|---|
| **Metálico binario** | Corten, chapas, bastidor y carpintería a 0; galvanizado a 1 | **El cambio más visible en el corten:** celosías y letras pierden el brillo plástico y quedan mates, como el óxido real |
| **Corten por lotes** | *Random Per Island*: ±15 % de valor por plancha, y un tono más pardo en algo menos de la mitad de ellas. En las letras, ±5 % | Las planchas de 1 × 2 m se leen como piezas de acero distintas, como en una fachada real de corten |
| **Salpicado al pie** | Franja de 30 cm con la Z del mundo deformada por ruido, en el color de la tierra del sitio | **Lo que más realismo suma en las vistas peatonales:** una franja irregular al pie de muros y columnas, que asienta el edificio en el suelo |
| **Polvo en cavidades y velo en lo oscuro** | AO en los valles de los nervios del antepecho (0,06 m) y en los encuentros (0,10 a 0,35 m), y un velo de 8 a 12 % en chapas, carpintería y bastidor | El antracita deja de ser un negro "de catálogo". Los nervios y los encuentros toman un polvo claro muy leve |
| **Pátina por geometría** | Caras superiores y cantos más oscuros (máscaras Arriba y Arista) | Casi no se ve a esta distancia: las planchas tienen 1 mm de espesor. Pesa en piezas gruesas y en vistas desde arriba |
| **Listones por isla, galvanizado y asfalto con Voronoi** | Tono, veta y rugosidad por listón; *spangle* y árido | Correcto pero imperceptible a estas distancias: el cielo está en sombra y los tubos y el árido son chicos. Sirve para acercamientos (CAM_02B) |
| **Vidrio de control solar** (CAM_01) | Cinco variantes, de la actual a la receta *Backfacing* | Ver la sección 4. La recomendada es física (capa fina, sin metálico) y cuesta lo mismo que la actual |

**Costo de render** (CPU, 1280 px, 96 muestras):

| Versión | CAM_06 | CAM_05 |
|---|---|---|
| Antes | 108 s | 98 s |
| Después, con AO y Bevel de 8 rayos y el AO dentro del relieve | 342 s (+217 %) | 258 s (+163 %) |
| Con 2 rayos de AO y 4 de Bevel | 235 s (+118 %) | 172 s (+76 %) |
| Además, el relieve del polvo sin AO | **174 s (+61 %)** | **131 s (+34 %)** |

Dos lecciones, con el mismo resultado visual:
1. **Bastan 2 rayos de AO y 4 de Bevel.** Con 96 a 384 muestras de cámara, el ruido de esos rayos se promedia y el OIDN limpia el resto.
2. **Nada que dependa de un AO o de un Bevel debe alimentar la altura de un `Bump`.** Cycles evalúa esa altura tres veces: en el punto y desplazada en x y en y. Por eso el AO pasa a costar el triple. Aquí eso solo sumaba entre 42 y 57 puntos de costo.

Lo que queda (+34 a +61 %) es el AO de las superficies grandes (revoque y vereda) y el Bevel del corten.
- **Fijas:** se puede pagar.
- **Video del dron:** conviene regenerar los materiales sin la máscara de cavidad. Arriba y Pie no lanzan rayos y son casi gratis.

## 2. Revisión de la investigación: qué aplica a este proyecto

**Se adopta:**

| Técnica | Cómo, en Blender 5.2 y para Uyuni |
|---|---|
| **Aristas con Bevel · Normal** (producto punto) | `Bevel` → `Vector Math: Dot Product` con `Geometry > Normal` → `Map Range` invertido. El rango 0,70–1,0 de los tutoriales tiene una razón geométrica: en el filo de una arista de 90°, la normal biselada queda a 45° de la cara, y cos 45° = 0,707. En las caras planas el producto vale 1. En una arista obtusa (un pliegue de 30°) la normal se desvía solo 15° y el mínimo es 0,966: la máscara casi no la ve. Es correcto desde lo físico: las aristas vivas se marcan más |
| **Radio del bisel variable** | El ruido modula el `Radius`, con lo que el ancho de la máscara varía a lo largo de la arista y no queda "de computadora". Probado |
| **Cavidades con Ambient Occlusion** | Nodo AO, salida `AO` invertida (1 − AO) y pasada por `Map Range`. **`Only Local` apagado**, para que vea los encuentros entre objetos distintos (muro con vereda, columna con muro). `Distance` en metros, según el tamaño del detalle: 0,06 m para los nervios de la chapa y 0,30 m para rincones de muro |
| **Máscara por gravedad** (polvo que sube del suelo) | Más simple que en el tutorial: `Geometry > Position` → `Separate XYZ` → Z, en metros. No hace falta el `Gradient Texture` con el `Mapping` girado 90°. Se le suma ruido a la Z (deformación de dominio) para que el borde sea irregular. Se limita a las caras verticales |
| **Máscara "hacia arriba"** (la cuarta máscara que propone el primer texto) | `Normal` → Z → `Map Range` 0,55–0,95. Es la principal para el polvo: el polvo se asienta por gravedad en alféizares, remates, caras superiores de letras y tubos |
| **Ruptura con ruido y deformación de dominio** | **El nodo Musgrave ya no existe: desde Blender 4.1 está fusionado en `Noise Texture`**. Ese nodo tiene tipos (`FBM`, `MULTIFRACTAL`, `RIDGED_MULTIFRACTAL`, `HYBRID_MULTIFRACTAL`, `HETERO_TERRAIN`) y una entrada `Distortion`, que deforma el dominio sin nodos extra. Se usan manchas grandes multiplicadas por manchas finas |
| **Metálico binario** | La pintura y el óxido son dieléctricos (0) y el metal desnudo conduce (1). Los valores intermedios solo valen en la transición entre ambos. **El modelo tiene 8 materiales del edificio con metálico intermedio**, entre 0,15 y 0,9, y 2 en los *proxies* de vehículos (ver la sección 3) |
| **Rugosidad por estados** | Polvo de 0,90 a 0,95, pintura satinada de 0,35 a 0,5, mate de 0,55 a 0,7, óxido de 0,8 a 0,92, metal galvanizado de 0,3 a 0,45. Nunca un valor constante: ruido de ±0,05 |
| **Relieve con sentido físico** | El polvo es materia que se deposita: relieve positivo. Lo que se pierde (poros, picaduras) es relieve negativo: `Bump` con `Invert`. En 5.2, el `Bump` tiene además `Filter Width` (antialias del relieve) |
| **Capas dentro de un solo Principled** | Para polvo y pátina conviene mezclar las entradas (color, rugosidad, metálico, normal) de un único Principled BSDF. Un `Mix Shader` evalúa los dos BSDF donde el factor no es 0 ni 1: es más caro y más ruidoso. Solo se justifica si las capas son de tipo distinto (por ejemplo, vidrio con una película de polvo) |
| **Voronoi F1 por celda** | La salida `Color` da un valor aleatorio por celda. Sirve para el *spangle* del galvanizado (cristales de zinc) y para el árido del asfalto. Probado |
| **Voronoi Distance to Edge + filtrado con F1 + deformación de dominio** | No hay grietas en un edificio nuevo, pero la técnica es ideal para **la costra de sal del suelo del altiplano**: polígonos irregulares, solo en algunas zonas y con bordes curvados. En 5.2 el Voronoi tiene `Detail`, `Roughness` y `Lacunarity` (fractal) y `Normalize` |
| **Escala aplicada y coordenadas del mundo** | Bevel y AO trabajan en metros del mundo. **Se verificó que ningún objeto del modelo tiene escala distinta de 1.** Además, las máscaras usan la posición y la normal del mundo, así el polvo continúa sin cortes de un objeto al vecino |

**Se agrega (no está en la investigación, pero sigue la misma lógica):**

| Técnica | Para qué |
|---|---|
| `Geometry > Random Per Island` | Un valor aleatorio por isla de malla. Cada plancha de corten de 1 × 2 m y cada listón del cielo (copias del modificador Array) es una isla. Sirve para variar color, rugosidad y veta pieza por pieza, como en una obra real. Probado |
| `Principled > Diffuse Roughness` | Rugosidad del componente difuso: aplana la luz rasante en superficies porosas. Valores: 0,8 en revoque, 0,7 en hormigón, 0,5 en óxido y 0,6 en asfalto |
| `Principled > Thin Film` | Interferencia de capa fina. Es la física real del vidrio de control solar con capa de óxido (ver la sección 4) |

**Se adapta al proyecto:**

| Técnica de la investigación | Por qué cambia en Uyuni | Alternativa |
|---|---|---|
| Desgaste de aristas que deja ver el metal (*chipping*) | **La terminal es nueva**: no lleva roturas ni desconchones | La máscara de aristas se usa para la pátina del corten, más densa en los cantos |
| Grietas y arañazos con Voronoi | Obra nueva | La misma técnica, para la costra de sal del contexto y el árido del asfalto |
| Mugre oscura en cavidades | El clima es seco. En agosto y septiembre (época de vientos) hay polvo fino y salino en todo; el render es del 4 de octubre | Polvo **claro y salino**, del color del suelo. Pesa sobre todo en lo horizontal: en cavidades verticales, al 35 % |
| Suciedad que sube desde el suelo | Las lluvias son de diciembre a marzo; en octubre solo queda el rastro | Franja de 30 cm al pie de muros y columnas, con el color de la tierra del sitio y opacidad baja |
| Pintura sobre metal con `Mix Shader` | En el corten, el óxido **es** el acabado | Corten como un solo Principled dieléctrico con pátina variable (sección 3) |
| Gradiente de dos colores de pintura | No hay pinturas bicolores en el proyecto | No aplica |

**No aplica o es impreciso:**
- **Pointiness:**
  - depende de la densidad de vértices, y el modelo tiene caras grandes y n-gonos generados desde curvas: ahí no detecta nada útil;
  - solo funciona en Cycles.
- **Aristas por diferencia de dos Bevel (`Mix: Difference`):**
  - funciona como detector binario, pero tiene dos defectos;
  - cuesta el doble: dos Bevel, cuando la normal sin biselar sale gratis de `Geometry > Normal`;
  - al pasar un color a un valor, Cycles usa la luminancia (0,21 R + 0,72 G + 0,07 B). Por eso, el ancho de la máscara cambia con la orientación de la arista: una desviación de la normal en Y pesa diez veces más que en Z;
  - el producto punto, o `Vector Math: Distance` (que vale 2·sen(θ/2)), no depende de la orientación.
- **`Mapping` girado 90° para el gradiente vertical:** sobra. La Z de la posición, en metros, es más directa y no depende del origen del objeto.
- **EEVEE, horneado y exportación a motores en tiempo real:** el proyecto se renderiza en Cycles, video del dron incluido. En EEVEE, el Bevel no funciona. Hornear solo haría falta para una versión web o VR.
- **"La rugosidad es el 70 % del realismo":** es una frase hecha, no un dato medido. Lo que sí es cierto es que una rugosidad uniforme delata el CG más que un color plano.
- **Metal expuesto con rugosidad baja en los bordes:** no hay metal expuesto en el proyecto.

**Advertencias técnicas de Blender 5.2:**
- **El Bevel solo ve la malla del mismo objeto.** Usa la misma intersección local que el *subsurface scattering*. El encuentro entre dos objetos distintos (columna con muro) no se bisela ni aparece en la máscara de aristas: para eso está el AO.
- **Costo** (medido en la sección 1): Bevel y AO lanzan rayos extra en cada punto sombreado.
  - Usa 2 rayos de AO y 4 de Bevel.
  - Nunca los pongas en la altura de un `Bump`.
  - Ponlos solo en los materiales donde se ven: el Bevel de aristas no aporta en las planchas de 1 mm.
  - Enciende `Only Local` cuando no hagan falta los demás objetos.
  - Cycles descarta las ramas que no llegan a la salida: una máscara del grupo que no se usa no cuesta.
  - Ojo: una propiedad leída con un nodo `Attribute` no apaga el AO, porque su valor se conoce recién en el render. Para ahorrar de verdad hay que regenerar el material sin esa rama.
- **Medición:** el material de diagnóstico `UY_DIAG_MASCARAS` de la prueba pinta las tres máscaras en rojo, verde y azul con *View Layer > Material Override*. Hay que mirarlo antes de ajustar colores.
- **Coordenadas:** los ruidos que deben acompañar a una pieza (veta, lote de una plancha) van en coordenadas de objeto o por isla. Los que deben ser continuos en todo el edificio (polvo, salpicado) van en coordenadas del mundo.

## 3. Receta por material

Valores de color en sRGB; entre paréntesis, la luminancia lineal (rango físico de 0,03 a 0,85). "Polvo" usa el grupo `UY_MASCARAS_ALTIPLANO` con los pesos indicados: cavidades (AO), caras hacia arriba y salpicado al pie.

| Material | Hoy | Recomendado |
|---|---|---|
| `UY_CHAPA_CUBIERTA` | P1 `#373C40`, met 0,35, rug 0,45. P2 `#C3C6C8`, met 0,55, rug 0,35 | **P1:** chapa prepintada, met **0**, rug 0,45 ± 0,06. **P2:** hay que definir si es chapa pintada gris (met 0) o aluzinc sin pintar (met 1, base ≈ `#B8BBBD`, con *spangle*). Polvo: cavidades 0,6 (AO 0,06 m, nervios), arriba 0,55, velo 0,12, opacidad 0,6. Es lo que más se ve en las aéreas |
| `UY_CHAPA_ANTEPECHO_REMATES` | P1 met 0,15; P2 met 0 | met **0**; rug ± 0,06; polvo en los valles de los nervios (AO 0,06 m) y en la cara superior del remate, con un velo de 0,12: en lo oscuro, nada queda negro puro en un lugar polvoriento |
| `UY_CELOSIA_CORTEN_O_BLANCA` | P1 met 0,20, rug 0,80; P2 `#EFEEE9` (0,85) | **P1, corten inteligente:** met **0**; lotes por plancha (*Random Per Island*): ±15 % de valor, y en algo menos de la mitad de las planchas un tono más pardo (`#5E2C1A`); caras superiores (65 %) y cantos (40 %) con pátina densa `#3A1A0E`; rug de 0,80 a 0,92; rug difusa 0,5; salpicado al pie. **P2:** `#E6E5E0` (0,79), met 0, rug 0,45; polvo en los cantos superiores |
| `UY_LETRERO_BLANCO_O_CORTEN` | corten met 0,20; blanco `#F3F3EF` (0,89), rug 0,28; **gris oscuro `#45494C`, rug 0,45, en P2 desde el 4 de octubre** | **Corten:** igual que la celosía, pero con ±5 % entre piezas (una letra distinta de otra parece un defecto). **Blanco:** `#E5E5E1` (0,78), rug 0,30–0,35 con ruido. Polvo leve en las caras superiores de letras y pirámides |
| `UY_BASTIDOR_CELOSIAS` | P1 `#232323`, met 0,60 | met **0** (acero pintado); polvo arriba |
| `UY_ALUMINIO_ANTRACITA_MATE` | `#3A3E41`, met 0,25, rug 0,55 | met **0** (pintura en polvo mate), rug 0,55–0,65 con ruido. Polvo en alféizares y travesaños (arriba 0,7) y en el encuentro con el vidrio (AO 0,10 m) |
| `UY_ACERO_GALVANIZADO` | `#9DA1A5`, met 0,9, rug 0,35 | met **1**; base `#B4B8BA`; *spangle* con Voronoi F1 (escala 60): ±8 % de valor y rug de 0,30 a 0,46. Polvo arriba |
| `UY_REVOQUE_CONTINUO` y `UY_REVOQUE_FACHADA_BUNAS` | grano del mortero, ±3 % de tono, rug 0,92 / 0,90 | rug difusa 0,8; ondas de llana (ruido de escala 1,4, de 2 a 3 mm). Polvo: salpicado al pie 0,85 (30 cm), cavidades 0,45 y alféizares 0,6, opacidad 0,55 |
| `UY_HORMIGON_VISTO` | marcas de encofrado, rug 0,78 | rug difusa 0,7; polvo y salpicado (probado). Sin probar: poros con Voronoi F1 (escala 300, 5 % de las celdas, relieve negativo) |
| `UY_HORMIGON_FRATASADO` (veredas) | juntas cada 2,40 m y humedad | rug difusa 0,7; tierra acumulada al pie de los muros y en las juntas (AO 0,35 m, peso 0,9) |
| `UY_ASFALTO` | `#2E2E2D` (0,027) | `#323230` (0,03); árido con Voronoi F1 (escala 160); rug difusa 0,6. Opcional: manchas de aceite en los estacionamientos |
| `UY_PINTURA_VIAL_BLANCA` | plana | que herede el relieve del asfalto, con un borde levemente irregular |
| `UY_SUELO_ALTIPLANO` | ruido procedural | PBR de Poly Haven y costra de sal con Voronoi *Distance to Edge*: polígonos de 0,3 a 1 m, filtrados con F1 y deformados con ruido |
| `UY_CIELO_LISTONES` | la misma veta en todos los listones | por listón (*Random Per Island*): ±8 % de valor, fase de la veta distinta y rug ± 0,06. Probado |
| `UY_PLENUM_NEGRO_MATE` y `UY_SELLO_ESTRUCTURAL_NEGRO` | 0,001 y 0,003 | `#303030` (0,03) |
| `UY_VIDRIO_CONTROL_SOLAR` | met 0,15 (atajo para que refleje), transmisión 0,8 | met **0**, transmisión 1; el reflejo sale de una capa fina (`Thin Film` de 50 nm con IOR 2,4), con ondas de templado y polvo en el perímetro. Receta completa en la sección 4. Probado |
| `UY_NIEVE` (escena crepuscular) | `#F4F6FA` (0,92), *subsurface* 0,2 | `#E8EBF0` (0,82); *subsurface* con *random walk*; destellos opcionales con Voronoi |
| Vehículos y personas | *proxies* | Se reemplazan por assets. En la pintura de auto: base dieléctrica más `Coat` 1; si es metalizada, met 1 más `Coat`. Neumático en 0,03 |

## 4. Vidrio de control solar

Revisión del texto sobre el vidrio reflectivo ("espejo unidireccional"), contrastado con Blender 5.2 y con el modelo, y prueba en CAM_01 con seis variantes, con la misma luz y el mismo encuadre.

**Decisión del cliente (4 de octubre): variante 6.**
- **DVH:** vidrio interior laminado incoloro de 3+3 mm, cámara de aire y vidrio exterior de 4 mm, acoplado o laminado con lámina o tratamiento de control solar.
- **El arquitecto pide menos reflexión:** que la fachada no sea un espejo ciego y deje ver la estructura de adentro (columnas, vigas y carpinterías).
- **Valida el tono más oscuro:** contrasta y resalta la estructura y los elementos blancos.
- **Para el render:** la variante 6 es el tinte oscuro de la 5 con una capa de baja reflexión. La reflectancia baja de ≈ 34 % a ≈ 13 % por cara, y el cielo reflejado, un 23 %.
- **Ya está en `uyuni_modelo.py`:** constante `VIDRIO` y función `mat_vidrio`. Para un `.blend` con avance propio, con `aplicar_cambios_4oct.py`.
- **Pendiente:** para que se vea la estructura detrás del vidrio, esta tiene que existir en el modelo. Hoy, detrás del vidrio hay una caja vacía: hay que modelar las columnas y vigas interiores cercanas a la fachada, a partir del IFC.

**Hoja:** `01_blender/fotorrealismo/Prueba_vidrio_CAM01.jpg`. **Herramienta:** `01_blender/herramientas/prueba_vidrio.py`.

| Variante | Qué es | Luminancia media* (cielo reflejado / interior) | Lectura |
|---|---|---|---|
| 1 · Hoy | metálico 0,15, transmisión 0,8 | 149 / 125 | El reflejo toma el tinte azul de la base: es un atajo, no física |
| 2 · Capa fina | metálico 0, transmisión 1, `Thin Film` de 57 nm con IOR 2,4 | 169 / 111 | Reflejo plateado y neutro, más claro, con la física correcta |
| 3 · Físico completo | capa de 50 nm (azul acero), tinte `#A9BCCB`, ondas de templado y polvo en el perímetro | 160 / 102 | **Recomendado.** Reflejo azul acero, interior más oscuro, reflejos apenas ondulados |
| 4 · Receta *Backfacing* | `Mix Shader` por `Backfacing`; por fuera, metálico 0,9 sobre `#0D151D`, sin transmisión | 49 / 24 | Casi negro: refleja menos que un vidrio común |
| 5 · Físico oscuro | como el 3, con tinte `#6E808E` | 154 / 93 | Desde afuera, apenas más oscuro que el 3: de día manda el reflejo. El tinte pesa de cerca, desde adentro y en la hora azul |
| **6 · Elegido: oscuro, baja reflexión** | tinte `#6E808E`; capa de IOR 1,8 y 67 nm; ondas y polvo; interior a 3500 K | 119 / 67 | **Elegido por el cliente.** Refleja un 23 % menos de cielo que el 5. El vidrio queda oscuro y los muros claros contrastan |

\*En el mismo paño, de 0 a 255 en la imagen final. Las seis tardan lo mismo: de 110 a 116 s con la CPU compartida, y 62 s la 6, con la CPU libre.

**La física del texto es correcta:**
- No existe un vidrio que deje pasar la luz en un solo sentido (reciprocidad de Helmholtz). El "espejo" de día sale de tres cosas:
  - la diferencia de iluminancia entre afuera y adentro, de 100 a 1 o más;
  - la capa reflectiva, que refleja del 20 al 40 %;
  - la absorción del vidrio tintado.
- En Uyuni la diferencia es aún mayor, porque a 3660 m el sol es más intenso:
  - de día, el vidrio se verá casi siempre como espejo;
  - en la hora azul, al revés: el interior encendido se ve desde afuera (CAM_03).

**Camino A (físico): se adopta, con dos correcciones.**
- El modelo ya tiene lo que este camino pide: un interior básico con piso y luz cálida detrás del vidrio. Son los objetos `INTERIOR_PISO` e `INTERIOR_LUZ`, con la propiedad `luz_interior`: 0,6 de día y 7,0 en la hora azul. El efecto espejo sale solo.
- **La reflectancia no debe salir de un "toque de metálico".** Ese metálico tiñe el reflejo con el color base y no cambia con el ángulo como una capa real.
  - En 5.2, `Thin Film` reproduce lo que es la capa pirolítica o por *sputtering*: un óxido de unas decenas de nanómetros que refleja por interferencia.
  - 57 nm con IOR 2,4 (tipo TiO₂) es un cuarto de onda a 550 nm: reflectancia ≈ 34 %, reflejo plateado.
  - Con 47 a 50 nm, el pico se corre al azul (450 a 480 nm): reflejo azul acero, como el de las fotos.
  - El resto de la luz pasa (transmisión 1) con el tinte del color base, y el reflejo crece en ángulo rasante, como en la realidad.
- **`Volume Absorption` (densidad 5 a 15) es correcto en lo físico, pero aquí no conviene:**
  - con `Thin Wall`, el paño no se trata como un volumen;
  - un volumen cuesta más;
  - el color base ya cumple de tinte de transmisión.

**Camino B (*Backfacing*): no se recomienda en este proyecto.**
1. **Todas las cámaras están afuera** (CAM_01 a CAM_07 y el dron). El truco solo sirve cuando la cámara entra al edificio. Aquí equivale a pintar el vidrio de espejo negro opaco.
2. **Apaga la hora azul.** Sin transmisión por fuera, desaparece el interior encendido de CAM_03.
3. **No funciona con los paños del modelo.** Cada paño es una caja de 27 mm.
   - Su cara interior también mira hacia adentro, así que desde adentro se vería de frente (`Backfacing` = 0) y mostraría el espejo.
   - El truco solo funciona con un plano único y la normal hacia afuera.
4. **La receta no da el 20 a 40 % que describe el mismo texto.**
   - Con metálico 0,9, el color base es la reflectancia a 0°. `#0D151D` es ≈ 0,7 % lineal: el vidrio refleja menos que uno común (4 % por cara) y solo brilla en ángulo rasante.
   - La variante 4 lo muestra: luminancia de 49 contra 160.
   - Un espejo metálico del 30 % necesitaría un color base de ≈ 0,3 lineal (≈ `#959FA8`), no casi negro.
5. Además, el `Mix Shader` evalúa los dos BSDF (sección 2).

**Detalles para romper el aspecto CG: se adoptan, ajustados.**

| Detalle del texto | Ajuste para Uyuni |
|---|---|
| Distorsión de templado (*roller wave*) con un Noise de escala 1,5 a 3 | Es una onda periódica, no un ruido: las marcas de los rodillos del horno de templado tienen un paso de unos 30 cm. Mejor un `Wave Texture` en bandas de 0,33 m, con fase al azar por paño (*Random Per Island*) y algo de `Distortion`. Bump de 0,02 a 0,04, con distancia de 3 mm. Reemplaza al abombado con ruido de la prueba de fotorrealismo. Probado: a la distancia de CAM_01 casi no se percibe, como en la realidad. Se nota de cerca, en el reflejo de líneas rectas como el horizonte |
| Polvo en el perímetro (AO → rugosidad de 0,35 a 0,6) | Correcto, pero el edificio es nuevo: de 0,02 en el centro a 0,15–0,2 junto a la perfilería. AO de 0,12 m con 2 rayos, que nunca entra en un Bump. Probado |
| Tinte del reflejo con base `#0A1118` o `#081014` | Ese tinte, en el color base de un metal, oscurece todo (punto 4). Con capa fina, el tinte del reflejo sale del espesor de la capa, y el color base queda para el tinte de transmisión |
| DVH a 3660 m (no está en el texto) | Un DVH fabricado abajo y sin tubos capilares se infla en Uyuni: cada paño queda convexo y el reflejo se deforma "en almohada" (sección 5). Con una especificación correcta no pasa, así que en el render no se agrega |

**Receta final de `UY_VIDRIO_CONTROL_SOLAR`** (variante 6, elegida por el cliente):

| Parámetro | Valor |
|---|---|
| Shader | un solo Principled BSDF, sin `Mix Shader` |
| Base Color | tinte de transmisión `#6E808E` (oscuro, elegido) |
| Metallic | 0 |
| Roughness | 0,02 en el centro y de 0,15 a 0,2 junto a la perfilería (AO de 0,12 m) |
| IOR | 1,52 |
| Transmission | 1 |
| Thin Wall | sí: cada paño es una caja de 27 mm, y sus dos caras hacen de las dos hojas del DVH |
| Thin Film | **67 nm con IOR 1,8**: capa de baja reflexión, ≈ 13 % por cara, con pico a 482 nm (reflejo azul acero tenue). Las capas de IOR 2,4 (variantes 2, 3 y 5) reflejan ≈ 34 %: demasiado espejo para el pedido del arquitecto |
| Normal | ondas de templado: `Wave Texture` en bandas de 0,33 m con fase por paño y `Bump` de 0,03 con distancia de 3 mm |

## 5. Nota de diseño (para el proyecto, no para el render)

**El corten escurre óxido durante sus primeros meses** (en inglés, *bleeding*) y mancha las superficies claras y porosas de abajo, como el hormigón. Las guías de diseño recomiendan:
- goterones;
- separar el acero de la superficie de abajo;
- franjas de grava que recojan el escurrimiento.

En la P1, las celosías corten están a 20 cm de la vereda de hormigón y a 12 cm del revoque claro. Conviene prever una franja de grava o una canaleta bajo las celosías, o especificar corten prepatinado y sellado.

En el render no se muestran manchas: el edificio se presenta nuevo.

**El DVH de Uyuni necesita tubos capilares o fabricarse en altura.**
- Los fabricantes recomiendan tubos capilares cuando entre la fábrica y la obra hay más de 800 m de diferencia de altura.
- Sin ellos, el aire de la cámara queda a la presión de la fábrica. En Uyuni la presión es un tercio menor que en Santa Cruz: los paños se abomban hacia afuera, el sello trabaja de más y el vidrio puede romperse.
- Un DVH de Santa Cruz (416 m) instalado en Uyuni está en ese caso; uno de La Paz o de El Alto, no.
- Conviene que la especificación de las mamparas ME-1 y ME-2 lo diga.

## 6. Fuentes consultadas

- clima de Uyuni: [Weather Spark](https://weatherspark.com/y/27661/Average-Weather-in-Uyuni-Bolivia-Year-Round) y [Salar de Uyuni, mes a mes](https://www.salardeuyuni.com/blogs/what-s-the-weather-like-at-salar-de-uyuni-month-by-month-guide/);
- corten: [SteelConstruction.info](https://www.steelconstruction.info/Weathering_steel), [Corten Australia](https://cortenaustralia.com.au/design-considerations/) y [DMD](https://dmd-world.com/posts/prevent-bleeding-weathering-steel);
- DVH en altura: [Viridian: tubos capilares](https://www.viridianglass.com/wp-content/uploads/2024/04/TechDirect%E2%84%A2-Specifications-Metal-Spacer-Capillary-Breather-Tubes.pdf) y [Cardinal: capillary tubes](https://www.cardinalcorp.com/glossary/capillary-tubes/);
- nodo Bevel: [manual de Blender 5.2](https://docs.blender.org/manual/en/latest/render/shader_nodes/input/bevel.html);
- API de Blender 5.2: verificada en el propio módulo `bpy` 5.2.2 (nodos, entradas y tipos citados).

## 7. Prompt para la otra IA

Pégalo después del prompt de fotorrealismo (`FOTORREALISMO_BLENDER.md`, sección 4), cuando ya lo haya aplicado. Adjunta las hojas `Prueba_materiales_CAM06_CAM05.jpg` y `Prueba_vidrio_CAM01.jpg`.

```text
Siguiente etapa: materiales. Partes del .blend formal, ya actualizado con los cambios del 3 de octubre y con las mejoras de fotorrealismo (exposición, cámaras y compositor). En el paquete tienes:
- la revisión técnica, en 02_postproduccion/MATERIALES_INTELIGENTES.md: lee completas las secciones 2, 3 y 4;
- una prueba que ya funciona en Blender 5.2: 01_blender/herramientas/prueba_materiales.py, con su hoja de resultados (adjunta), y la del vidrio, prueba_vidrio.py. Trae el grupo de nodos UY_MASCARAS_ALTIPLANO y las funciones capa_polvo(), corten_inteligente(), listones_por_isla(), galvanizado_spangle() y asfalto_arido().

Objetivo: que todos los materiales respondan a la geometría como en la realidad (aristas, cavidades, gravedad, pieza por pieza), sin mapas UV ni horneado y con valores físicos.
Hazlo permanente y regenerable: funciones en uyuni_modelo.py, o un script propio que corra después del modelo. Nada a mano sin dejarlo en código.

Reglas:
- Es una terminal NUEVA en el altiplano, a 3660 m. El clima es seco y en agosto y septiembre los vientos dejan polvo fino y salino; el render es del 4 de octubre:
  - sin desgaste de aristas, desconchones, grietas, arañazos, manchas de óxido ni chorreaduras;
  - el polvo es de días, no de años: a primera vista el edificio tiene que verse nuevo y limpio, y el polvo solo lo asienta en el lugar;
  - nada de mugre oscura: el polvo es claro, del color del suelo.
- No cambies los colores de PALETA ni las propiedades "propuesta" y "letras_corten". Sí puedes corregir el metálico y la rugosidad según la tabla de la sección 3; dime el valor anterior y el nuevo.
- El corten de P1 sigue siendo cobrizo cálido (ref. Cementerio de Trenes): la pátina varía, pero el tono medio no cambia.
- Coordenadas:
  - máscaras y polvo, en coordenadas del mundo (Geometry > Position y Normal), para que sigan sin cortes de un objeto al vecino;
  - la veta y el lote de cada pieza, en coordenadas de objeto o por isla.
- La intensidad del polvo sale de una propiedad de escena "polvo" (0 a 1), leída igual que "propuesta". Valores iniciales: 1,0 en UYUNI_DIA y UYUNI_DIA_P2_SALAR_LITIO, y 0,6 en UYUNI_CREPUSCULO.
- Costo (sección 1 del documento):
  - AO con 2 rayos y Bevel con 4;
  - nada que dependa de un AO o un Bevel en la altura de un Bump;
  - en cada material, solo las máscaras que use;
  - para el video del dron, una opción que regenere los materiales sin la máscara de cavidad;
  - mide el tiempo de render.

Tareas, en este orden:

1. Física de base (sección 3):
   - metálico binario: 0 en pinturas, óxido y polvo; 1 en metal desnudo (galvanizado). Hoy hay 8 materiales del edificio con valores intermedios;
   - albedos entre 0,03 y 0,85;
   - Diffuse Roughness del Principled: revoque 0,8, hormigón 0,7, óxido 0,5 y asfalto 0,6;
   - en la cubierta de P2, pregúntame antes si es chapa pintada gris o aluzinc sin pintar.

2. Grupo de máscaras UY_MASCARAS_ALTIPLANO (copia el de la prueba):
   - Arista: Bevel · Normal (producto punto), con radio variable por ruido;
   - Cavidad: AO con Only Local apagado y distancia según el detalle;
   - Arriba: componente Z de la normal;
   - Pie: Z del mundo deformada con ruido, solo en caras verticales;
   - Ruptura: Noise fBM con Distortion (en 5.2 no existe el nodo Musgrave), multiplicando manchas grandes por manchas finas;
   - Grano: relieve fino del polvo.
   Deja también el material de diagnóstico UY_DIAG_MASCARAS (rojo, verde y azul), con un interruptor para usarlo como Material Override.

3. Polvo del altiplano en cada material, con los pesos de la tabla (capa_polvo()):
   - mezcla color, rugosidad (0,92), metálico (hacia 0) y relieve positivo, en un solo Principled;
   - nada de Mix Shader para esto.

4. Corten inteligente, en las celosías de P1 y en las letras corten:
   - metálico 0;
   - variación por plancha con Random Per Island: ±15 % de valor y un tono más pardo en parte de ellas; en las letras, ±5 %;
   - pátina más densa (#3A1A0E) en caras superiores y cantos;
   - rugosidad de 0,80 a 0,92;
   - salpicado al pie.

5. Variación pieza por pieza con Random Per Island:
   - listones del cielo: valor, fase de la veta y rugosidad;
   - planchas de corten;
   - chapas de la cubierta, si están separadas.

6. Metales y pavimentos:
   - galvanizado con spangle (Voronoi F1);
   - asfalto con árido (Voronoi F1), y pintura vial con el mismo relieve;
   - hormigón visto con poros (Voronoi F1 y relieve negativo);
   - veredas con tierra acumulada al pie de los muros y en las juntas (AO).

7. Vidrio de control solar: la variante 6, elegida por el cliente (sección 4, probada en CAM_01):
   - DVH real: laminado incoloro 3+3 adentro, cámara y 4 mm con control solar afuera; la fachada no debe parecer un espejo ciego;
   - un solo Principled: metálico 0, transmisión 1, IOR 1,52, Thin Wall; color base oscuro, como tinte de transmisión (#6E808E);
   - el reflejo sale de una capa de baja reflexión: Thin Film de 67 nm con IOR 1,8 (≈ 13 % por cara);
   - ondas de templado: Wave Texture en bandas de 0,33 m con fase por paño (Random Per Island) y Bump de 0,03 con 3 mm;
   - polvo en el perímetro: AO de 0,12 m (2 rayos) que lleva la rugosidad de 0,02 a 0,18. Nunca en el Bump;
   - para que se vea la estructura detrás del vidrio, modela las columnas y vigas interiores cercanas a la fachada a partir del IFC, y lleva el interior a 3500 K (Blackbody), sin el resplandor naranja;
   - no uses el truco de Backfacing ni el metálico para el reflejo.

8. Suelo del contexto (si ya está con Poly Haven): costra de sal en manchas, con Voronoi Distance to Edge filtrado con F1 y deformado con ruido. Nunca sobre la calzada ni la plataforma.

9. Verificación:
   - diagnóstico de máscaras en CAM_06 y CAM_05: rojo solo en aristas, verde en rincones y encuentros, azul en caras superiores y al pie;
   - antes y después de CAM_06, CAM_05, CAM_01 y CAM_07, en P1 y en P2, con la misma luz y el mismo encuadre;
   - False Color: los blancos de P2 no deben subir; el polvo no debe mover la exposición de los muros más de 1/3 de EV;
   - tiempo de render antes y después.

Entrega:
- el código con los parámetros nuevos y una lista de cambios por material, con el valor anterior y el nuevo;
- las imágenes de verificación y los tiempos;
- lo que no pudiste resolver.
```
