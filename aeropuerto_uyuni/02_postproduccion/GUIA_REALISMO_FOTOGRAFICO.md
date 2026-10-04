# Guía de realismo fotográfico en Blender 5.2: lo aprendido en Uyuni

Resumen de todo lo investigado y probado sobre el modelo, en un solo lugar. Cada sección remite al documento con la prueba, las imágenes y el detalle:

| Documento | Qué tiene | Prueba |
|---|---|---|
| `FOTORREALISMO_BLENDER.md` | Cámaras, exposición con False Color, microbisel, compositor | CAM_01 de día |
| `MATERIALES_INTELIGENTES.md` | Materiales que responden a la geometría, receta por material, vidrio de control solar | CAM_06, CAM_05 y CAM_01 |
| `ILUMINACION_NOCTURNA.md` | Fundamentos de iluminación, composición y escena nocturna | CAM_03 en la hora azul |

Las herramientas de cada prueba están en `01_blender/herramientas/` (`prueba_*.py`) y sus hojas, en `01_blender/fotorrealismo/`.

**Lo que no se toca:** el diseño, la geometría del edificio y las decisiones del cliente (`TRASPASO.md`, sección 5). Todo lo de esta guía mejora la manera de fotografiar el edificio, no el edificio.

## 0. Orden de trabajo

Cada paso cambia lo que mide el siguiente, por eso el orden importa:
1. **Cámaras:** encuadres bloqueados y verticales rectas.
2. **Física de los materiales:** metálico binario, albedos entre 0,03 y 0,85, rugosidad variable.
3. **Luz de día:** sol y cielo calibrados con False Color, ya con los albedos correctos.
4. **Materiales inteligentes:** polvo, pátina del corten, variación por pieza y vidrio.
5. **Contexto:** suelo, vegetación, cerros, vehículos y personas.
6. **Noche:** luces prácticas en Kelvin, interior con profundidad y exposición medida.
7. **Compositor:** la óptica de la cámara.
8. **Render y salidas.**
9. **Verificación** después de cada paso: antes y después con la misma cámara y la misma luz.

## 1. Cámara y composición

| Regla | Valor |
|---|---|
| Verticales rectas | Cámara horizontal (rotación X = 90°) y encuadre con `shift_y`. Se enderezan CAM_01, CAM_03, CAM_05 y CAM_06; CAM_07 ya lo está. CAM_02, CAM_02B, CAM_04 y el dron se inclinan a propósito. **Es el cambio que más acerca un render a una foto de arquitectura** |
| Altura | 1,65 m (los ojos). CAM_03, más baja (de 1,2 a 1,6 m), para que el piso mojado duplique la fachada. CAM_07 queda elevada a pedido del cliente |
| Lente | De 24 a 35 mm en exteriores, con sensor de 36 mm |
| Profundidad de campo | Nada, o casi nada: en arquitectura todo va nítido (como a f/8–f/11) |
| Bloquear antes de iluminar | Los reflejos dependen del punto de vista: primero el encuadre, después la luz |
| Composición | Foco en el acceso y el letrero; líneas (cordón, calzada, reflejos) que llevan hacia ellos; horizonte bajo si manda el cielo y alto si mandan los reflejos; escala humana junto al acceso; nada que toque la línea del techo |

Detalle: `FOTORREALISMO_BLENDER.md` (sección 2) e `ILUMINACION_NOCTURNA.md` (sección 3).

## 2. Exposición: medir, no adivinar

Se mide con *View Transform* `False Color`, sin compositor. Leyenda calibrada en Blender 5.2 (pasos de exposición respecto del gris medio):

| Color | Negro | Azul | Celeste | Cian | Verde | **Gris** | Verde lima | Amarillo | Naranja | Rojo | Blanco |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EV | ≤ −10 | −9 a −7 | −6 a −5 | −4 a −2 | −1 | **0** | +1 | +2 | +3 a +4 | +5 a +6 | ≥ +7 |

| Zona | De día | De noche (hora azul) |
|---|---|---|
| Muros claros | +1 a +2 al sol; −1 a −2 en sombra | centro de los barridos de luz, de +1 a +2 |
| Cielo | 0 a +1 arriba; no más de +4 en el horizonte | −1 a 0 |
| Interior visto por el vidrio | (reflejo) | +2 a +3 |
| Fuentes de luz | solo los reflejos del sol en rojo | solo las fuentes, de +3 a +5; nada quemado salvo el núcleo de las luminarias |
| Asfalto | −2 a −4 | — |

**Cómo se ajusta:**
- **De día:** la exposición de la cámara queda en 0 y se ajustan juntos el sol y el cielo. La prueba bajó ambos a ×0,6: sol de 4,5 a 2,7 y cielo de 0,18 a 0,108.
- **De noche:** la exposición se ajusta como el tiempo de obturación de una cámara (en la prueba, de 0,6 a 1,1), y la proporción entre las luces no se toca.
- *View Transform* AgX, *Look* Medium High Contrast.

## 3. Luz de día

- **Cielo:** `MULTIPLE_SCATTERING` (es el "Nishita *multiscatter*"), con el aire limpio de 3660 m (`CIELO_ATMOSFERA`). El truco del doble cielo no hace falta.
- **Sol:** de 0,53° a 0,6° de tamaño, para sombras nítidas. Mañana del 4 de octubre a las 09:30, ya calculada para Uyuni.
- **Perspectiva atmosférica:** solo sobre los cerros lejanos, con el pase de Mist. Nada de bruma sobre el edificio.
- **Sombras que rompen la luz plana:** las del propio edificio (celosías, alero, letrero) y, si acaso, sombras de nubes sobre el terreno lejano. En el altiplano no hay árboles: nada de *gobos* de follaje.

## 4. Luz de noche (hora azul)

| Elemento | Receta |
|---|---|
| Cielo | Sol entre −4° y −6° (el modelo está a −3,94°). Cielo y luces quedan a 2–3 EV de distancia |
| Temperaturas | Todo en Kelvin: luces con `use_temperature`, emisores con `Blackbody`. Alero, 3000 K; interior, 3500 K; letrero LED, de 4000 K (blanco cálido) a 5000 K (blanco neutro); uplights de las celosías, 2700 K. **Lo que se ve debe tener la misma temperatura que lo que ilumina** |
| Luminarias | Se ven pero no iluminan: `material.cycles.emission_sampling = "NONE"` y el objeto sin visibilidad difusa. Ilumina el Spot que tiene adentro: menos ruido y sin luz duplicada |
| Interior | No una caja emisiva pareja. Paredes claras, una grilla de Area Lights de techo con `Spread` y algo que iluminar: mostradores, columnas, personas. De noche, el interior es el foco |
| Letrero | Brillante pero legible: entre +3 y +5 EV |
| Light Groups | Cielo, interior, alero, letrero y uplights en grupos separados (`view_layer.lightgroups` y `objeto.lightgroup`): las proporciones se ajustan en el compositor sin volver a renderizar |
| Movimiento (opcional) | Exposición larga: personas algo movidas y estelas de faros, con desenfoque de movimiento |

Detalle y prueba: `ILUMINACION_NOCTURNA.md`.

## 5. Materiales

| Regla | Valor |
|---|---|
| **Metálico binario** | 0 en pinturas, óxido, polvo y vidrio; 1 en metal desnudo (galvanizado). Hoy hay 8 materiales con valores intermedios |
| **Albedos** | Entre 0,03 y 0,85 en luminancia lineal: letrero blanco `#E5E5E1`; celosía blanca de P2 `#E6E5E0`; nieve `#E8EBF0`; plenum, sello y neumático `#303030`; asfalto `#323230` |
| **Rugosidad** | Nunca constante: ruido de ±0,05. Polvo de 0,90 a 0,95; pintura satinada de 0,35 a 0,5; mate de 0,55 a 0,7; óxido de 0,8 a 0,92; galvanizado de 0,3 a 0,45 |
| **Rugosidad difusa** | `Diffuse Roughness` del Principled: revoque 0,8, hormigón 0,7, óxido 0,5 y asfalto 0,6 |
| **Microbisel** | Nodo `Bevel` en el shader: 4 mm en chapas, 6 mm en el letrero, 8 mm en el revoque, 2 mm en perfiles y 5 mm en hormigón |
| **Máscaras inteligentes** | Un grupo, `UY_MASCARAS_ALTIPLANO`, en coordenadas del mundo, con cinco máscaras: aristas (`Bevel` · `Normal`), cavidades (AO con los demás objetos), caras hacia arriba (Z de la normal), pie de los muros (Z del mundo deformada con ruido) y ruptura (`Noise` fBM con `Distortion`) |
| **Polvo del altiplano** | Claro y salino (`#BDB3A1`), de días y no de años. En cavidades, en caras hacia arriba y como salpicado de tierra (`#8E826E`) al pie de los muros. Lo maneja la propiedad de escena `polvo` |
| **Corten** | Dieléctrico, con un lote por plancha (*Random Per Island*: ±15 %, algunas más pardas) y pátina más densa en caras superiores y cantos |
| **Variación por pieza** | *Random Per Island* en los listones del cielo y en las planchas de corten |
| **Galvanizado y asfalto** | *Spangle* y árido con Voronoi F1 |
| **Vidrio de control solar** (elegido por el cliente) | Un solo Principled: metálico 0, transmisión 1, IOR 1,52, `Thin Wall`; tinte oscuro `#6E808E`; capa de baja reflexión `Thin Film` de 67 nm con IOR 1,8 (≈ 13 % por cara); ondas de templado (`Wave Texture` en bandas de 0,33 m, con fase por paño); polvo en el perímetro. La fachada no debe parecer un espejo ciego: detrás del vidrio tiene que haber estructura que ver. **Nada de metálico para el reflejo ni del truco de Backfacing** |
| **Costo** | AO con 2 rayos y Bevel con 4. Nunca un AO o un Bevel en la altura de un `Bump` (Cycles la evalúa tres veces). Costo medido: de +34 a +61 % |
| **Diagnóstico** | El material `UY_DIAG_MASCARAS`, como *Material Override*, pinta aristas, cavidades y gravedad en rojo, verde y azul |

Detalle, receta por material y prueba: `MATERIALES_INTELIGENTES.md`.

## 6. Contexto y assets

- **Escala real:** *Apply Scale* en todo asset importado. Las texturas PBR de Poly Haven, a su tamaño real (cada asset dice cuántos metros cubre). Si la escala no coincide, la textura se ve borrosa o repetida.
- **Mapeo:** sin UV, con `Box` en el nodo `Image Texture` y algo de `Blend`, en coordenadas de objeto o del mundo.
- **Suelo:** tierra y grava clara, costras de sal (Voronoi *Distance to Edge* filtrado con F1, en manchas) y piedras sueltas. La calzada y la plataforma quedan libres.
- **Vegetación:** paja brava y tola, sin árboles ni césped. Se dispersan con Geometry Nodes: rotación Z al azar, inclinación de 1 a 3°, escala ±20 % y recorte por cámara. Las hojas llevan algo de traslucidez.
- **Relieve:** cerros bajos a 5–20 km, con `Displace` o un modelo de elevación. La subdivisión adaptativa, solo en el primer plano del terreno.
- **Orden:**
  - colecciones propias (`10_CONTEXTO_PAISAJE`, `11_VEHICULOS_PERSONAS`), enlazadas en las tres escenas;
  - todo cargado por código;
  - cada asset registrado en `01_blender/assets/CREDITOS.md`.

## 7. Compositor

| | De día | De noche |
|---|---|---|
| Glare | `Bloom`: umbral 1,2, fuerza 0,12, tamaño 0,55 | `Fog Glow`: umbral 1,5, fuerza 0,08, tamaño 0,5 |
| Lente | Distorsión −0,008 y dispersión 0,006, con `Fit` | La misma |
| Viñeteo | 30 % | 30 % |
| Grano | ±0,6 % en lineal | ±0,2 % en lineal (de noche pesa mucho más: con ±0,4 % ya parecía ruido) |

En Blender 5.2:
- el compositor es un grupo de nodos en `scene.compositing_node_group`, con salida por `Group Output`;
- **al nodo `Render Layers` hay que asignarle la escena** (`nodo.scene`);
- sin GPU, `compositor_device = "CPU"`;
- conviene dejar un interruptor para desactivar el compositor al medir.

## 8. Render y salidas

| Parámetro | De día | De noche |
|---|---|---|
| Muestras | 384 a 512 | 512 a 1024 |
| Umbral adaptativo | 0,008 a 0,01 | 0,005 |
| Rebotes (total, difuso, brillo, transmisión) | 12 / 6 / 6 / 12 | igual |
| *Clamp* indirecto | 8 | 3 a 5 (contra las luciérnagas) |
| *Light tree* | sí | sí |
| Eliminación de ruido | OIDN con albedo y normal, *prefilter* `ACCURATE` y calidad `HIGH` | igual |
| Filtro | 1,5 px | igual |

**Salidas:**
- PNG de 16 bits y un JPG de 8 bits con difuminado;
- para posproducir, un EXR multicapa *half float* con Mist, AO y Cryptomatte, y los Light Groups de noche.

**Si se renderiza en CPU en la nube:**
- en franjas que se retoman si el proceso se corta: `render_banda.py` y `unir_bandas.py`;
- el 4K de CAM_07 tardó ~30 min por imagen con 384 muestras.

**En la PC del usuario:** GPU con OptiX o CUDA.

**Video:** secuencia PNG, codificada después con ffmpeg (H.264).

## 9. Verificación, después de cada paso

1. Antes y después con la misma cámara y la misma luz.
2. False Color con las metas de la sección 2, en P1 y en P2.
3. Diagnóstico de máscaras (`UY_DIAG_MASCARAS`).
4. De noche, cada Light Group por separado.
5. Recortes al 100 % donde está el cambio.
6. Tiempo de render antes y después.

## 10. Trampas de Blender 5.2 encontradas en estas pruebas

Se suman a las de `TRASPASO.md` (sección 10):
- **Compositor:**
  - el tipo de `Glare` es una entrada de menú (`"Bloom"`, `"Fog Glow"`);
  - `compositor_device` es GPU por defecto y se cae sin EGL;
  - al nodo `Render Layers` hay que asignarle la escena: si no, renderiza la escena activa.
- **Nodo Musgrave:** no existe desde 4.1. `Noise Texture` tiene tipos (`FBM`, `MULTIFRACTAL`, `RIDGED_MULTIFRACTAL`, `HYBRID_MULTIFRACTAL`, `HETERO_TERRAIN`) y `Distortion`.
- **`bmesh`:** con el módulo `bpy`, existe recién después de `import bpy`.
- **Emisión sin muestreo:** `material.cycles.emission_sampling = "NONE"`.
- **`Blackbody` tiene luminancia 1** (medido en 5.2). Si un emisor pasa de RGB a Kelvin, hay que multiplicar su fuerza por la luminancia del color anterior para no cambiar el brillo. `mat_emisor(..., kelvin=)` del modelo ya lo hace.
- **Luces:** `light.use_temperature` y `light.temperature`; las Area Lights tienen `spread`.
- **Light Groups:** `view_layer.lightgroups.add(name=...)` y `objeto.lightgroup`. El mundo también tiene `lightgroup`.
- **`Bump`:** todo lo que alimenta su altura se evalúa tres veces. Un AO o un Bevel ahí triplica su costo.
- **`Bevel`:** solo ve la malla del mismo objeto. Para los encuentros entre objetos está el AO.
- **Propiedades leídas con `Attribute`:** no apagan ramas en la compilación. Para ahorrar costo de verdad, hay que regenerar el material sin la rama.
- **Paños de vidrio en caja:** el truco de `Backfacing` no funciona con cajas; `Thin Wall` hace de las dos hojas del DVH.
- **PNG de 16 bits:** PIL los trunca. Se leen con `pypng`.
