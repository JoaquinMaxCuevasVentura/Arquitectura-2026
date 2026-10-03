# Fotorrealismo en Blender 5.2: revisión de la investigación, prueba y prompt

Este documento junta tres cosas:
- la revisión de la investigación sobre técnicas de fotorrealismo (videos y artículos de ArchViz), contrastada con Blender 5.2 y con este proyecto;
- una prueba pequeña sobre el modelo;
- el prompt para que otra IA aplique las mejoras en el `.blend` formal.

## 1. La prueba (CAM_01, propuesta 1)

**Hoja de resultados:** `01_blender/fotorrealismo/Prueba_fotorrealismo_CAM01.jpg`.

**Herramienta:** `01_blender/herramientas/prueba_fotorrealismo.py`. Aplica las técnicas sobre una copia del modelo y renderiza el antes y el después, cada uno con su diagnóstico en False Color.

| Técnica | Qué se hizo | Resultado |
|---|---|---|
| **Verticales rectas** | CAM_01 estaba inclinada 4,46°. Se dejó horizontal y se encuadró con `shift_y` = 0,069 | **El cambio más visible.** Las columnas y las celosías dejan de converger hacia arriba |
| **Exposición por la luz** | Con False Color, los muros al sol daban +2 EV y el cielo del horizonte +5/+6 EV (al borde del quemado). Sol 4,5 → 2,7 y cielo 0,18 → 0,108 (×0,6 = −0,7 EV) | **El segundo cambio más visible.** Los muros quedan entre +1 y +2 EV y el horizonte en +3/+4. Sale un cielo azul más profundo, muros gris claro (no blancos) y corten más rico. Con ×0,5, el asfalto y el corten quedan algo oscuros |
| **Microbisel en el shader** | Nodo Bevel: 4 mm en chapas, 6 mm en el letrero, 8 mm en el revoque, 2 mm en perfiles y 5 mm en hormigón | Aristas de columnas, marcos y letras con un brillo fino. Es sutil pero quita el "filo de cartón" |
| **Rugosidad variable en metales** | Ruido de ±0,05 a 0,07 sobre la rugosidad de chapas, perfiles y galvanizado | Sutil: el reflejo deja de ser uniforme |
| **Vidrio abombado (DVH)** | Ruido de baja frecuencia (escala 0,35) en un Bump de fuerza 0,04 | Reflejos levemente ondulados. Se notará más cuando haya contexto que reflejar (cerros, vehículos) |
| **Albedos físicos** | Letrero blanco 0,89 → 0,78; plenum y sellos de 0,001 a 0,03 | Menos aspecto "lechoso" |
| **Óptica en el compositor** | Bloom (umbral 1,2, fuerza 0,12), distorsión −0,008, aberración 0,006, viñeteo al 30 % y grano de ±0,6 % | Acabado de cámara real, sin efecto evidente |

**Costo de render:** el microbisel y la óptica suman alrededor de un 10 %. Se midió en CPU con la cola de 4K corriendo al mismo tiempo, así que el dato es aproximado.

### Leyenda de False Color, calibrada en Blender 5.2

Pasos de exposición respecto del gris medio (0,18 lineal):

| Color | Negro | Azul | Celeste | Cian | Verde | **Gris** | Verde lima | Amarillo | Naranja | Rojo | Blanco |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EV | ≤ −10 | −9 a −7 | −6 a −5 | −4 a −2 | −1 | **0** | +1 | +2 | +3 a +4 | +5 a +6 | ≥ +7 (quemado) |

**Metas para un exterior a pleno sol:**

| Zona | Meta |
|---|---|
| Muros claros al sol | +1 a +2 |
| Muros en sombra | −1 a −2 |
| Asfalto | −2 a −4 |
| Cielo alto | 0 a +1 |
| Horizonte | no más de +4 |
| Rojo | solo en reflejos del sol |

## 2. Revisión de la investigación: qué aplica a este proyecto

**Se adopta:**

| Técnica | Cómo, en Blender 5.2 y para Uyuni |
|---|---|
| Verticales rectas con *shift* | Cámara con rotación X = 90°, sin inclinación. Encuadre con `camera.data.shift_y`. CAM_07 ya está así. Faltan CAM_01, CAM_05 y CAM_06. CAM_02 (detalle desde arriba), CAM_02B (mirando hacia arriba), CAM_04 (aérea) y el dron se inclinan a propósito |
| Exposición con False Color, corrigiendo la luz | *Color Management > View Transform > False Color*, solo para medir. Se ajustan el sol (`UY_SOL_MANANA`) y la fuerza del cielo en la misma proporción. **La exposición de la cámara queda en 0.** Verificar con las dos propuestas: los blancos de P2 son los más exigentes |
| AgX | Ya está, con *Medium High Contrast* |
| Cielo físico de dispersión múltiple | Es el que la investigación llama "Nishita multiscatter". En 5.2 el tipo se llama `MULTIPLE_SCATTERING` y ya está en uso (`CIELO_ATMOSFERA`). **El truco del doble cielo con Light Path no hace falta** |
| Sol de 0,545° | El script usa 0,53°. En el aire limpio de 3660 m conviene entre 0,53° y 0,6°, no más |
| Microbisel (nodo Bevel) | Probado: radios de la tabla de arriba. Para aristas grandes conviene además un bisel real de 1 a 2 cm en la geometría: borde superior del antepecho, esquinas de columnas y goterón |
| Rugosidad nunca constante | En metales (probado) y en el vidrio: marcas de limpieza muy suaves, con rugosidad de 0,02 a 0,05 |
| Vidrio abombado | Probado. Mantener la fuerza baja: entre 0,03 y 0,05 con Distance 0,05 |
| Albedos físicos (blancos ≤ 0,85, negros ≥ 0,03) | Ver la sección 3 |
| Revoque no perfectamente plano | Bump de muy baja frecuencia (ondas de llana de 0,5 a 1 m), fuerza 0,05 a 0,1 y distancia 1 a 2 mm. Se ve con luz rasante |
| Contexto que tape el horizonte | Cerros bajos a 5–20 km, con Displace sobre un plano o con un modelo de elevación SRTM / Copernicus (TRASPASO 8.1) |
| Subdivisión adaptativa con desplazamiento | En 5.2 es una opción del modificador Subdivision (`use_adaptive_subdivision`) más `scene.cycles.dicing_rate`, `dicing_camera` y `max_subdivisions`. **Solo para el terreno en primer plano** (grava, huellas, bordes de la calzada), no para el edificio |
| Vegetación estratificada con variación aleatoria | Con especies del altiplano (ver "Se adapta"). Dispersión con Geometry Nodes e instancias: rotación Z de 0 a 360°, inclinación de 1 a 3°, escala ±20 %, recorte por cámara |
| Perspectiva atmosférica | A 3660 m el aire es muy limpio: va solo sobre los cerros lejanos, con el pase de Mist en el compositor (más barato y sin ruido) o un volumen de densidad 0,0001–0,0003. Nada de bruma sobre el edificio |
| Pases para posproducción | EXR multicapa *half float* con Mist, AO y Cryptomatte (objeto y material), además del PNG de 16 bits |
| Higiene de assets importados | Para vehículos, personas y vegetación: *Apply Scale*, *Limited Dissolve* en mallas trianguladas, instancias (Alt+D o Geometry Nodes) y unir por material. El edificio del script ya está a escala 1 |

**Se adapta al proyecto:**

| Técnica de la investigación | Por qué cambia en Uyuni | Alternativa |
|---|---|---|
| "Gobo" con árboles fuera de cuadro | **En el altiplano de Uyuni no hay árboles.** Sombras de árboles serían un contexto falso | Sombras de nubes sobre el suelo (son típicas del altiplano), de un mástil o de vehículos y personas. Las sombras propias de celosías, alero y letrero ya rompen la luz plana |
| Vegetación en tres capas (césped, maleza) | No hay césped | Suelo de tierra y grava clara con costras de sal; matas de paja brava (*Festuca orthophylla*) y tola (*Parastrephia*) de distintos tamaños, con puntas secas; piedras sueltas. Hojas y briznas con traslucidez (Subsurface o Transmission bajos) |
| Desportillado de aristas (Voronoi, AO interior) | Es una terminal **nueva**: no lleva desgaste ni roturas | Solo una suciedad muy sutil: polvo en una franja de 20 a 30 cm al pie de los muros y, si acaso, una chorreadura leve bajo el goterón. El corten ya trae su variación de óxido |
| Espacio de trabajo Rec.2020 o ACEScg | Existe en 5.2 (`bpy.data.colorspace.working_space`), pero la paleta está definida en sRGB y se convierte a lineal Rec.709 | No cambiarlo para los renders de decisión. Si se prueba, hay que convertir la paleta y comparar. El beneficio en colores neutros es pequeño |
| Lente de 20 mm a 1,70 m | Fue pensado para vivienda | La fachada de 85 m pide entre 24 y 35 mm (CAM_01 usa 32, CAM_07 usa 28) a 1,65 m. CAM_07 queda elevada a propósito, por pedido del cliente |

**No aplica:**
- **Agua y estanques:** no hay. El piso mojado de la hora azul ya existe.
- **Reescalado de texturas con IA:** los materiales son procedurales y las texturas de Poly Haven vienen en 4K u 8K.
- **Megascans:** hoy se distribuye por Fab, con su propia licencia. Es más seguro usar Poly Haven (CC0) y registrar todo en `CREDITOS.md`.

**Advertencias técnicas de Blender 5.2:**
- **El compositor es un grupo de nodos:**
  - Se asigna con `scene.compositing_node_group` y sale por un *Group Output*. Ya no hay nodo *Composite*.
  - Las mezclas se hacen con el nodo *Mix* compartido.
  - Glare y Lens Distortion se configuran por sus entradas: `Type`, `Threshold`, `Strength`, `Distortion`, `Dispersion`, `Fit`.
  - Hay ruido blanco y coordenadas de imagen para generar grano.
- **El compositor usa la GPU por defecto.** Sin GPU (en la nube) se cae; para evitarlo, usa `scene.render.compositor_device = "CPU"`.
- **Medición sin compositor:** antes de medir con False Color, desactiva el compositor; si no, el viñeteo y el bloom alteran la lectura.

## 3. Paleta: albedos fuera de rango

Valores en luminancia lineal. El rango físico va de 0,03 a 0,85.

| Material | Hoy | Recomendado |
|---|---|---|
| Letrero blanco `#F3F3EF` | 0,89 | `#E5E5E1` (0,78) |
| Celosía blanca P2 `#EFEEE9` | 0,85 | `#E6E5E0` (0,79) |
| Parapeto P2 `#ECEBE6` y cielo P2 `#EDECE8` | 0,83 y 0,84 | Pueden quedar. Si P2 se ve "lechoso", bajar a 0,78–0,80 |
| Nieve `#F4F6FA` | 0,92 | `#E8EBF0` (0,82) |
| Plenum `#030303` y sello `#0B0B0B` | 0,001 y 0,003 | `#303030` (0,03). El plenum sigue leyéndose negro entre los listones |
| Neumático `#121212` | 0,006 | `#303030` |
| Asfalto oscuro `#2E2E2D` | 0,027 | `#323230` (0,03) |
| Corten oscuro `#4F2413` | 0,030 | En el límite: puede quedar |

---

## 4. Prompt para la otra IA

Pégalo después del prompt de continuación, cuando ya haya integrado los cambios del 3 de octubre. Adjunta la hoja `Prueba_fotorrealismo_CAM01.jpg`.

```text
Siguiente etapa: fotorrealismo. Partes del .blend formal, ya actualizado con los cambios del 3 de octubre. En el paquete tienes:
- la revisión técnica, en 02_postproduccion/FOTORREALISMO_BLENDER.md;
- una prueba que ya funciona en Blender 5.2: 01_blender/herramientas/prueba_fotorrealismo.py, con su hoja de resultados (adjunta).
Implementa estas mejoras de forma permanente y regenerable: como parámetros y funciones en uyuni_modelo.py, o en un script propio que se ejecute después del modelo. Nada a mano sin dejarlo en código.

Reglas:
- No cambies el diseño, la geometría del edificio ni las dos propuestas de color (PALETA, propiedades "propuesta" y "letras_corten", letrero A y B). Lo que sigue mejora la manera de fotografiarlo, no lo que se fotografía.
- Es un aeropuerto nuevo en el altiplano, a 3660 m:
  - sin árboles, sin césped y sin desgaste ni roturas en aristas;
  - aire muy limpio;
  - vegetación: paja brava y tola.
- Todo asset externo va en colecciones propias, enlazadas en las tres escenas, y se registra en 01_blender/assets/CREDITOS.md.
- Compara siempre antes y después con el mismo encuadre, y mide la exposición con False Color (leyenda en el documento).

Tareas, en este orden:

1. Exposición. Con False Color y sin compositor, en CAM_01 y en CAM_07, con las dos propuestas:
   - deja los muros claros al sol entre +1 y +2 EV y el horizonte en +4 EV como máximo;
   - ajústalo con la potencia del sol y la fuerza del cielo, en la misma proporción. La exposición de la cámara queda en 0;
   - punto de partida probado: sol 2,7 y cielo 0,108 (×0,6);
   - revisa especialmente los blancos de P2.

2. Cámaras:
   - deja CAM_01, CAM_05 y CAM_06 horizontales (rotación X = 90°) y encuadra con shift_y, como hace enderezar_camara();
   - CAM_02, CAM_02B, CAM_04 y el dron conservan su inclinación;
   - eye level a 1,65 m y lentes de 24 a 35 mm en exteriores.

3. Materiales (sección 2 y tabla de la sección 3):
   - microbisel con nodo Bevel en chapas, letrero, revoque, perfiles, hormigón y listones;
   - bisel geométrico de 1 a 2 cm en el borde del antepecho, las esquinas de columnas y el goterón;
   - rugosidad variable en metales y vidrio;
   - vidrio levemente abombado;
   - ondas de llana de muy baja frecuencia en el revoque;
   - albedos dentro de 0,03–0,85;
   - polvo muy sutil al pie de los muros (franja de 20–30 cm). Nada de desportillado.

4. Contexto del altiplano:
   - suelo de tierra y grava clara, con texturas PBR de Poly Haven y costras de sal;
   - paja brava y tola dispersas con Geometry Nodes (instancias, rotación Z aleatoria, inclinación de 1 a 3°, escala ±20 %, recorte por cámara);
   - piedras sueltas;
   - cerros bajos en el horizonte (Displace o modelo de elevación);
   - en el primer plano del terreno, desplazamiento con subdivisión adaptativa: dicing_rate 1,0 en final y 4 en vista previa, dicing_camera = cámara activa, max_subdivisions de 8 a 12;
   - calzada y plataforma, libres.

5. Atmósfera y luz:
   - sol entre 0,53° y 0,6°;
   - perspectiva atmosférica solo sobre los cerros (pase de Mist en el compositor);
   - opcional: sombras de nubes sobre el terreno lejano. Si caen sobre el edificio, pregúntame antes.

6. Compositor (Blender 5.x: grupo de nodos en scene.compositing_node_group; con GPU puede ir en GPU):
   - bloom suave (umbral 1,2, fuerza 0,12);
   - distorsión −0,008 y aberración cromática 0,006, con Fit;
   - viñeteo al 30 %;
   - grano de ±0,6 %;
   - punto de partida: compositor_optica() de la herramienta de prueba. Que se pueda desactivar con un interruptor.

7. Salidas de render:
   - AgX Medium High Contrast;
   - EXR multicapa half float con Mist, AO y Cryptomatte (objeto y material), más PNG de 16 bits;
   - muestreo adaptativo con umbral de 0,01 y OIDN con albedo y normal;
   - deja la GPU configurada para renderizar en mi PC.

Entrega:
- el código con los parámetros nuevos (valor anterior y nuevo de cada uno);
- antes y después de CAM_01 y CAM_07 (P1 y P2), con su False Color;
- el tiempo de render de cada uno;
- lo que no pudiste resolver.
```
