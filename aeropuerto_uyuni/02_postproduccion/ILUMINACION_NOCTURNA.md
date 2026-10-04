# Iluminación y composición, sobre todo de noche: revisión de la investigación, prueba y prompt

Este documento sigue a `FOTORREALISMO_BLENDER.md` y a `MATERIALES_INTELIGENTES.md`. Junta tres cosas:
- la revisión de la investigación sobre fundamentos de iluminación 3D y su relación con el sombreado, contrastada con Blender 5.2 y con este proyecto;
- una prueba pequeña sobre la escena nocturna (CAM_03, hora azul);
- el prompt para que otra IA aplique lo que sirve.

El sombreado y la luz son dos caras de la misma ecuación: un material bien hecho se ve plano si la luz no "excita" su rugosidad y su relieve. De noche esto pesa más, porque cada fuente se ve y cada error de proporción salta a la vista.

## 1. La prueba (CAM_03, escena UYUNI_CREPUSCULO)

**Hoja de resultados:** `01_blender/fotorrealismo/Prueba_noche_CAM03.jpg`.

**Herramienta:** `01_blender/herramientas/prueba_noche.py`. Renderiza el antes y el después, cada uno con su False Color.

**Lo que la escena ya tenía bien resuelto:**
- 16 Spots en el alero, a 3000 K: los barridos de luz en los muros;
- 5 uplights en las celosías, a 2700 K;
- una luna tenue (0,03 a 7500 K);
- cielo de hora azul con el sol a −3,94°;
- piso mojado con charcos.

**Lo que estaba flojo:**
- los emisores en RGB: el interior, naranja (≈ 2000 K), y las luminarias del alero a ≈ 2200 K, mientras sus Spots están a 3000 K;
- el interior era una caja emisiva pareja: ventanas planas y casi quemadas;
- el letrero, en +5/+6 EV;
- la exposición, puesta a ojo (0,6);
- la cámara, inclinada 5,24°.

| Cambio | Qué se hizo | Resultado |
|---|---|---|
| **Verticales rectas** | `shift_y` de 0,061 en lugar de inclinar | Columnas paralelas |
| **Todo en Kelvin** | `Blackbody` en los emisores: alero 3000 K, interior 3500 K, letrero 4000 K | Luminarias y barridos con el mismo blanco cálido; el interior deja de ser naranja |
| **Luz práctica** | Luminaria con `emission_sampling = "NONE"` y sin visibilidad difusa; Spots ×1,6 | La luminaria se ve igual. Barridos de +1/+2 EV en el centro, sin luz duplicada ni ruido de emisores chicos |
| **Interior con profundidad** | Caja emisiva a 0,25; paredes claras (0,45); 30 Area Lights de techo (3500 K, 1000 W, `Spread` de 110°); 7 mostradores | Ventanas con gradiente y luz que baja del techo, en vez de un plano quemado. Los mostradores casi no se ven a esta distancia: falta contenido (personas, señalética, columnas) |
| **Exposición medida** | De 0,6 a 1,1 (+0,5 EV), con False Color | Cielo de −1 a 0; interior de +2 a +4 con forma; letrero de +3/+4, legible |
| **Óptica nocturna** | `Fog Glow` leve, viñeteo al 30 % y grano de ±0,2 % | Halo suave en las fuentes. Con ±0,4 %, el grano parecía ruido en las zonas oscuras |

**Costo:** el mismo (169 s antes y 168 s después, en CPU, a 1280 px y 128 muestras).
- 30 Area Lights más no cuestan con el *light tree*.
- Que la luminaria no se muestree, en cambio, ahorra.

**Queda para la otra IA:**
- el contenido del interior;
- probar el letrero en 5000 K (con 4000 K se lee blanco cálido);
- los Light Groups;
- las muestras de un render final (512 a 1024).

## 2. Revisión de la investigación: qué aplica a este proyecto

**Se adopta:**

| Idea de la investigación | Cómo, en Blender 5.2 y para Uyuni |
|---|---|
| **Bloquear la cámara antes de iluminar** | Los reflejos y los ángulos dependen del punto de vista. Las cámaras del modelo ya están fijas. Primero se enderezan las verticales con `shift_y` (CAM_03 estaba inclinada 5,24°) y recién después se ilumina |
| **La sombra modela el volumen; sobreiluminar mata la jerarquía** | De noche, la oscuridad es parte de la imagen. Jerarquía para CAM_03: el interior encendido y el letrero son el foco; los barridos de luz en los muros dan el ritmo; el alero, la cubierta y el cielo son el descanso. Nada de luces "de relleno" sin fuente |
| **Ley del inverso del cuadrado** | Spot, Point y Area la cumplen en Cycles; el Sun no (rayos paralelos). Su firma en arquitectura nocturna son los **barridos de luz** que dejan los downlights del alero en el muro: intensos arriba y desvanecidos hacia abajo. Ya están en el modelo (16 Spots de 3000 K) |
| **El tamaño de la fuente define la penumbra** | Sol de 0,53° (sombras nítidas de día). Downlights con radio de 3 a 5 cm: el borde del barrido es nítido, como en la realidad. Interior con Area Lights grandes: luz suave. **Para revisar el relieve de un material, se ilumina un momento con una luz dura y rasante**; con luz suave, el `Bump` se diluye y no se sabe si está bien calibrado |
| **Kelvin para las fuentes reales y RGB solo para lo sintético** | En 5.2, las luces tienen `use_temperature` y `temperature` (el modelo ya las usa), y los materiales emisivos usan el nodo `Blackbody`. Valores para este proyecto: downlights del alero, 3000 K; interior de la terminal, 3500 K; letrero LED, 4000 K (se lee blanco cálido; con 5000 K, blanco neutro); uplights de las celosías, 2700 K. **Lo que se ve tiene que tener la misma temperatura que lo que ilumina** |
| **Suelo que rebota y recorta la silueta** | De noche, el piso mojado (propiedad `humedad`) hace de espejo de las fuentes: es la mitad de la imagen de CAM_03. La silueta contra el cielo es la razón por la que se fotografía en la hora azul y no de noche cerrada: el cielo queda más claro que el parapeto antracita |
| **Luces prácticas** | Las fuentes que se ven en la imagen (interior, luminarias del alero, letrero) justifican toda la luz. Es lo que ya hace el modelo: cada luminaria del alero tiene su Spot |
| **Aislar cada fuente para evaluarla** | En Blender hay algo mejor que ocultar luces: los **Light Groups** de Cycles (`View Layer > Light Groups` y `objeto.lightgroup`). Se renderiza un pase por grupo (cielo, interior, alero, letrero, uplights) y las proporciones se ajustan en el compositor sin volver a renderizar |
| **Respuesta microfacetaria (GGX)** | El Principled usa GGX con *multiscatter*. Una fuente chica muestra la variación de rugosidad solo cerca del brillo; una grande la extiende. Por eso la rugosidad variable de los materiales se luce con el cielo de día y casi no se ve con los Spots de noche: es normal |
| **Albedo dentro de rango** | Ya aplicado: de 0,03 a 0,85 (ver `MATERIALES_INTELIGENTES.md`) |

**Se adapta al proyecto:**

| Idea de la investigación | Por qué cambia en Uyuni | Alternativa |
|---|---|---|
| Apagar el World (Strength 0) y partir de un "cuarto oscuro" | Es para producto o estudio. En exterior, el cielo **es** la luz de relleno: de día, el cielo físico calibrado; de noche, el cielo de la hora azul (sol entre −4° y −6°) | El cuarto oscuro sirve para el *lookdev* de materiales y para revisar cada luz práctica por separado (mejor con Light Groups) |
| Luz de recorte (*rim* o *kicker*) detrás del objeto | En arquitectura, una luz sin fuente visible se nota falsa | El recorte lo da el propio cielo de la hora azul, más claro que el edificio, y los reflejos del piso mojado |
| Bajar el piso con `RGB Curves` para que no compita | Rompe el albedo físico y cambia cómo rebota la luz | Albedo físico; el contraste se resuelve con luz y encuadre. Si hace falta, se corrige después, en el compositor o en la gradación |
| Rugosidad escalar fija (0,7 a 0,8) en vez del mapa | Una rugosidad constante delata el CG | Se conserva la variación y solo se ajusta su rango |
| Lente de 80 mm para producto | Para aislar un objeto | Arquitectura: de 24 a 35 mm a la altura de los ojos, con verticales rectas |
| Spot con cono y difuminado para iluminar solo el activo | Es un viñeteado hecho con luz | En arquitectura, los Spots son los downlights reales del proyecto, con su cono real. El viñeteado se hace en el compositor y es leve |

**No aplica o es impreciso:**
- **"La emisión no proyecta sombras suaves si no tiene geometría real":** es impreciso.
  - En Cycles, toda superficie emisiva es geometría e ilumina la escena (muestreo de luces de malla con el *light tree*), con sombras tan suaves como su tamaño.
  - El problema real es el ruido: un emisor chico e intenso es difícil de muestrear.
  - El consejo de fondo es correcto: la luminaria se ve y la luz la pone una luz de Blender.
  - En 5.2 hay una forma más limpia que `Light Path > Is Camera Ray`: en el material, `Emission Sampling = None`, y en el objeto, sin visibilidad difusa. La luminaria se ve en cámara y en los reflejos, pero no ilumina. Probado.
- **"El nodo Musgrave"** (en el bloque sobre BRDF): no existe desde Blender 4.1 (ver `MATERIALES_INTELIGENTES.md`).
- **EEVEE Next con *raytracing*:** el proyecto se renderiza en Cycles.

**Advertencias técnicas de Blender 5.2** (encontradas en la prueba):
- **El nodo `Render Layers` del compositor toma la escena activa si no se le indica otra.** En un `.blend` con tres escenas, un compositor armado para UYUNI_CREPUSCULO renderizaba además UYUNI_DIA y devolvía la imagen de día. Hay que asignar `nodo.scene` siempre.
- **Con el módulo `bpy`, `bmesh` existe recién después de `import bpy`.**
- **La exposición de noche es legítima.** De día se dejó la exposición en 0 y se ajustó la luz (`FOTORREALISMO_BLENDER.md`). De noche, la exposición es como el tiempo de obturación de una cámara: se ajusta para el conjunto, y la proporción entre las luces no se toca.

## 3. Composición de la imagen nocturna

| Principio | Para CAM_03 y el video |
|---|---|
| **Verticales rectas** | Cámara horizontal y `shift_y`. Es lo que más separa una foto de arquitectura de un render |
| **Hora azul** | Sol entre −4° y −6°. El cielo y el interior quedan a 2–3 EV de distancia: los dos se leen. Es la hora en que fotografían los fotógrafos de arquitectura. El modelo ya está a −3,94° |
| **Contraste cálido-frío** | Interior y luminarias cálidos (de 2700 a 3500 K) contra el cielo azul. Las temperaturas tienen que ser coherentes entre sí: si todo es naranja, se ve falso |
| **Foco y recorrido de la mirada** | Foco en el acceso y el letrero. Las líneas del cordón, la calzada y los reflejos llevan hacia ellos |
| **Horizonte y reflejos** | Cámara baja (de 1,2 a 1,6 m) para que el piso mojado duplique la fachada. Horizonte bajo para darle aire al cielo |
| **Escala humana y movimiento** | De noche, una foto real tiene exposición larga: personas algo movidas en el acceso y estelas de faros de un vehículo en la calzada (desenfoque de movimiento con obturador largo). Es opcional, pero es una de las marcas más fuertes de una foto nocturna real |
| **Nada que compita** | Ninguna fuente quemada salvo el núcleo de las luminarias; ni postes ni elementos que toquen la línea del techo |

## 4. Receta para la escena nocturna

| Parámetro | Valor |
|---|---|
| Cielo | `MULTIPLE_SCATTERING` con sol a −4° (el modelo, −3,94°) y fuerza calibrada con False Color: cielo entre −1 y 0 EV |
| Exposición | La de una cámara: se ajusta con False Color (en la prueba, de 0,6 a 1,1). Metas: cielo de −1 a 0 EV; centro de los barridos en los muros, de +1 a +2; interior visto por el vidrio, de +2 a +3; solo las fuentes por encima de +5 |
| Downlights del alero | Los Spots que ya hay, a 3000 K, con radio de 3 a 5 cm. La luminaria visible usa `Blackbody` de 3000 K, `Emission Sampling = None` y sin visibilidad difusa |
| Interior | No una caja emisiva pareja. Paredes claras (0,45), grilla de Area Lights de techo (3500 K, `Spread` de 110°) y algo que iluminar: mostradores, columnas, señalética, unas personas. La caja emisiva queda como un resplandor tenue (0,25) |
| Letrero | `Blackbody` de 4000 K, con intensidad tal que quede entre +3 y +5 EV: brillante, pero con la forma legible |
| Uplights de las celosías | Los que ya hay, a 2700 K: el corten se enciende cálido |
| Luna | Relleno muy tenue y frío (la que ya hay: 0,03 a 7500 K) |
| Light Groups | Cinco grupos (cielo, interior, alero, letrero, uplights) para ajustar proporciones en el compositor |
| Compositor | `Glare` tipo `Fog Glow` muy leve (umbral 1,5, fuerza 0,08), viñeteo al 30 % y grano aditivo de ±0,2 %. Como se suma en lineal, de noche pesa mucho más que de día: con ±0,4 % ya parecía ruido |
| Render | De noche hay más ruido: de 512 a 1024 muestras, `adaptive_threshold` de 0,005, `clamp` indirecto de 3 a 5 contra las luciérnagas, *light tree* encendido, cáusticas apagadas y OIDN con albedo y normal |

## 5. Prompt para la otra IA

Pégalo después del prompt de materiales (`MATERIALES_INTELIGENTES.md`, sección 7), cuando ya lo haya aplicado. Adjunta la hoja `Prueba_noche_CAM03.jpg`.

```text
Siguiente etapa: iluminación nocturna (escena UYUNI_CREPUSCULO, CAM_03). Partes del .blend formal con las etapas anteriores aplicadas (fotorrealismo y materiales). En el paquete tienes:
- la revisión, en 02_postproduccion/ILUMINACION_NOCTURNA.md: lee completas las secciones 2, 3 y 4;
- una prueba que ya funciona en Blender 5.2: 01_blender/herramientas/prueba_noche.py, con su hoja de resultados (adjunta).
Hazlo permanente y regenerable: funciones en uyuni_modelo.py, o un script propio que corra después del modelo. Nada a mano.

Reglas:
- No cambies el diseño ni las decisiones del cliente. De noche, el letrero sigue la configuración de la escena: letras blancas que emiten. Si quieres proponer letras corten retroiluminadas (halo), pregúntame.
- Toda fuente real va en Kelvin: luces con use_temperature y emisores con Blackbody. Lo que se ve tiene la misma temperatura que lo que ilumina.
- Nada de luces sin fuente visible (rim, kicker) ni de "relleno" que aplane la noche: la oscuridad es parte de la imagen.
- Mide con False Color y sin compositor. La exposición se ajusta como en una cámara, sin tocar las proporciones entre las luces.

Tareas, en este orden:

1. Cámara: CAM_03 horizontal, con shift_y (estaba inclinada 5,24°).

2. Emisores en Kelvin, con un Blackbody en Emission Color:
   - luminarias del alero, 3000 K;
   - interior, 3500 K;
   - letrero, 4000 K (con 5000 K se lee como un blanco neutro: muéstrame los dos).

3. Luminarias del alero: se ven, pero no iluminan.
   - material.cycles.emission_sampling = "NONE" y el objeto sin visibilidad difusa;
   - ilumina el Spot que ya tiene cada una. Ajusta su potencia hasta que el centro de cada barrido de luz quede entre +1 y +2 EV (en la prueba, ×1,6).

4. Interior con profundidad (lo más importante):
   - la caja INTERIOR_LUZ deja de ser la fuente: emisión tenue (≈ 0,25) y paredes claras (#B8B2A8);
   - grilla de Area Lights de techo: 3500 K, Spread de 110°, dos filas a 6,5 m, una por vano;
   - contenido que iluminar: mostradores de check-in, columnas, señalética colgante y algunas personas, a su escala;
   - meta: el interior, visto a través del vidrio, entre +2 y +3 EV, con charcos de luz en el piso.

5. Letrero: entre +3 y +5 EV (en la prueba, luz_letrero = 0,9).

6. Light Groups: cielo (el mundo), interior, alero, letrero y uplights, con sus pases activados.

7. Compositor nocturno, con un interruptor para desactivarlo:
   - Fog Glow con umbral 1,5, fuerza 0,08 y tamaño 0,5;
   - viñeteo al 30 %;
   - grano de ±0,2 % en lineal (con ±0,4 % ya parece ruido);
   - asígnale la escena al nodo Render Layers.

8. Render nocturno: de 512 a 1024 muestras, umbral adaptativo de 0,005, clamp indirecto de 3 a 5 y light tree.

9. Opcional (pregúntame antes): un vehículo con faros y estelas (desenfoque de movimiento) y personas algo movidas en el acceso, como en una exposición larga.

Entrega:
- antes y después de CAM_03, con su False Color, y el pase de cada Light Group;
- los tiempos de render;
- los valores finales de cada luz (potencia, temperatura, tamaño) y de la exposición.
```
