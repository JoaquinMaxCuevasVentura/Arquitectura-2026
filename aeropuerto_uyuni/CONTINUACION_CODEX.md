# Continuación del modelo · 4 de octubre de 2026

Base: `acf7f58`, rama de origen `claude/clever-hypatia-i19958`. Trabajo en
`codex/continuacion-uyuni`. Se recuperan los complementos de materiales, cámaras
y render preparados en la sesión anterior; no se importa la envolvente antigua.

## Archivo de trabajo

`01_blender/uyuni_v2.blend` es la versión pública regenerada. La fuente sigue
siendo `01_blender/uyuni_modelo.py`; ahora llama al paquete `continuacion/`.
El constructor original sigue funcionando:

```powershell
blender --factory-startup -b --disable-autoexec --python-exit-code 1 -P 01_blender/herramientas/construir_blend.py -- 01_blender/uyuni_modelo.py 01_blender/uyuni_v2.blend
```

La versión local `uyuni_continuacion_local.blend` añade nueve figuras repartidas
entre cuatro variantes escaneadas de Renderpeople y cinco Toyota Land Cruiser 200
detallados de BlenderKit. Los originales se conservan en `assets/local/` y esta
versión del `.blend` se excluye de Git. Para regenerarla, coloca los assets en las
rutas descritas en `01_blender/assets/CREDITOS.md` y configura
`$env:UYUNI_ASSETS_LOCALES='1'` antes de ejecutar el constructor. También se admite
la variable anterior `UYUNI_PERSONAS_LOCALES`. Sin activar assets locales, el
archivo público conserva seis vehículos compartibles provisionales y los proxies
de personas ocultos. El minibús de traslado sigue siendo un modelo genérico: el
Sprinter encontrado no está disponible para esta cuenta: su descarga devuelve
HTTP 403. No se ha adquirido una suscripción ni un modelo de pago.
La vegetación procedural se sustituye por 21.975 instancias de tres matas
escaneadas de Poly Haven con textura seca: LOD0 cerca del frente y LOD2 a partir
de 110 m. No se realiza la geometría de las instancias. También se usan suelo
PBR con deformación suave de coordenadas para reducir repetición y HDRI de
Poly Haven. El catálogo oficial consultado no ofrecía personas
ni vehículos de pasajeros adecuados; esas sustituciones tienen fuentes separadas.

## Frente del Lado Tierra (5 de octubre): restituido de las capturas del cliente

La propuesta de Codex para el frente (tres franjas oscuras con jardineras ovaladas,
estacionamiento en espiga a 60°) no seguía el modelo del cliente y se retiró junto
con `continuacion/exteriores.py`. El frente ahora sale de la fuente
(`uyuni_modelo.frente_lado_tierra`), medido por fotogrametría sobre las capturas
DALUX del 4 de octubre: cámaras calibradas con aristas del edificio (cubierta,
anexo, celosías) y rectas de fuga, con las plantas de dos capturas distintas
coincidiendo en ±0,5 m. Todo queda paralelo a la fachada.

De norte a sur: línea amarilla a 0,5 m del cordón; dos carriles de llegada con
discontinua blanca en Y −13,5 y un recuadro claro frente a cada ME-2; jardineras
A (X −25,5 a 2,6) y B (X 6 a 82,3) de tierra oscura con cordón de hormigón y
cuatro anillos elevados blancos (0,20 × 0,45 m); carriles de salida con el andén
del bus junto a la B y la línea amarilla que la rodea; separador amarillo L1
(Y −32,6, 0,60 m) y la plaza de estacionamiento (X −4,5 a 77,4, Y −33,2 a −55,4,
con la cuña del sudoeste) con dos hexágonos elevados blancos, dos líneas de
espiga en zigzag a 45°, el andén de enfrente y la cebra del extremo este; en la
isla sudeste, dos columnas amarillas. Parámetros: `FRENTE`, `JARDINERAS`, `ESPIGA`,
`ANDENES`, `CEBRA`, `DISCOS` y `COLUMNAS`.

No cambian la fachada, la vereda A111 con sus dársenas (asfalto, como antes), el
cordón, la zanja ni las calles de los testeros de los ejes 1 y 20 hasta la
plataforma. La comparación malla por malla con `8b00602` da 245 mallas idénticas;
solo cambian los objetos del frente, los proxies de colocación de tres vehículos
y la dispersión del paisaje. Láminas: `verificacion/LADO_TIERRA_PLANTA_FRENTE.jpg`
y `LADO_TIERRA_PLANTA_SITIO.jpg`.

## Contexto con IA (`CONTEXTO_IA` en `continuacion/pipeline.py`)

Con `CONTEXTO_IA = True` (valor por defecto), el render solo muestra arquitectura,
sitio, aeronaves, mangas y los assets locales de alta calidad: la dispersión de
matas del terreno y los vehículos provisionales (GLB públicos que no son el modelo
real) quedan en el archivo con `hide_render`, para que la IA agregue el contexto
sin heredar assets mediocres. Para recuperarlos, poner `CONTEXTO_IA = False` y
regenerar, o desmarcar `hide_render` en `UY_PAJA_BRAVA_DISPERSION` y en
`11_VEHICULOS_PERSONAS`.

Las dos propuestas de fachada siguen siendo **Patrimonio Ferroviario** y
**Salar & Litio**. Se conserva el acabado actual de la cubierta P2. No se cambian
las cotas de cubierta, posición de pista ni geometría del rótulo.

## Fachada trasera revisada por el cliente

Los ocho paños opacos entre pilastras avanzan 0,70 m: su cara exterior pasa de
Y 43,872 a Y 44,572. Las cuatro ventanas pequeñas ME-4, enrollables y la puerta
P-01 acompañan el nuevo plano. Solo las dos crujías con grandes ME-5/ME-6
mantienen el fondo retranqueado. Se conservan pilastras, marquesina, vestíbulo,
bloque del eje R y cubierta. Los pisos y el cierre interior se prolongan bajo los
paños avanzados. La pequeña entrada entre ejes 7 y 8 cambia, por confirmación
del cliente, a una puerta frontal alineada de 1,00 x 2,10 m; se elimina su nicho
y la puerta lateral. El cambio se realiza en `fachada_aire()` del constructor.

## Cámaras, montaje y compositor

**Revisión puntual del 4 de octubre, antes de renders:** se conservan dos
opciones de celosías del lateral del eje 1, por indicación del cliente:

- **A, lateral recto:** `01_blender/uyuni_v2.blend`. Conserva la fila anterior,
  incluido su módulo terminal en rampa, con la esquina ya corregida.
- **B, lateral en zigzag:** `01_blender/uyuni_v2_lateral_zigzag.blend`. Usa cuatro
  módulos en zigzag PT2B/PT2A de 5 x 6 m y conserva el quiebre del último módulo:
  su primer metro sube de 5 a 6 m y desde ese pico baja en diagonal durante 4 m
  hasta 2 m, según la última captura del cliente. El remate PT2BR refleja el
  módulo PT2R del CAD, conserva sus calados y enlaza a 5 m con el panel contiguo.
  La base se alinea a 0,20 m y la fila se
  desplaza 32 mm para que el perfil superior coincida con el frente en la esquina.

En las dos opciones las chapas se recortan hasta el encuentro con una junta de
3 mm y un único poste interior de 40 x 40 mm. Los nuevos cantos de 1 mm quedan
cerrados; en B la altura del poste acompaña el perfil en zigzag. La corrección
está en `celosias()`. Cada archivo conserva las dos propuestas de color y las
23 cámaras con sus ajustes y animaciones. La comprobación de B conserva además
las otras 430 mallas y verifica que los cinco paneles estén cerrados y compartidos
por las dos escenas de propuesta.

Para regenerar cada opción desde la carpeta `aeropuerto_uyuni`:

```powershell
$env:UYUNI_CELOSIA_LATERAL='recta'
blender --factory-startup -b --disable-autoexec --python-exit-code 1 -P 01_blender/herramientas/construir_blend.py -- 01_blender/uyuni_modelo.py 01_blender/uyuni_v2.blend
$env:UYUNI_CELOSIA_LATERAL='zigzag'
blender --factory-startup -b --disable-autoexec --python-exit-code 1 -P 01_blender/herramientas/construir_blend.py -- 01_blender/uyuni_modelo.py 01_blender/uyuni_v2_lateral_zigzag.blend
Remove-Item Env:UYUNI_CELOSIA_LATERAL
```

Sin esa variable el constructor usa A. Estos comandos construyen los archivos;
no inician renders.

El inventario contiene **12 vistas fijas**: 01, 02, 02B, 03 (hora azul), 04,
05, 06, 07, 07B (captura del cliente), 08, 09 y 10. Hay además diez cámaras del
storyboard y una del recorrido original. La 07B se incorpora a la cola de vistas
fijas, que antes la omitía. El cliente elige la opción B con lateral en zigzag
y autoriza iniciar las imágenes fijas: **24 vistas, 12 en cada paleta**.
CAM_01 P1 y P2 se completan a 7680 x 4320. Después el cliente solicita bajar
las **22 pendientes a 3840 x 2160** para reducir el tiempo. Los dos originales
8K se conservan y se excluyen de la nueva cola. El video conserva la pausa anterior.

El guion entregado se conserva en `01_blender/guion/`. La escena
`UYUNI_VIDEO_MASTER_120S` monta diez escenas por cortes: 1–2880, 24 fps, 120 s.
Cada plano tiene cámara propia, sensor de 36 mm y lente constante; posiciones,
objetivos y rotaciones se muestrean por cuadro con smootherstep e interpolación
LINEAR. El foco animado y f-stop siguen el guion. Motion blur: 0,5 cuadros.

El Salar se genera en una escena independiente. El plano de Corten usa sol
occidental en coordenadas georreferenciadas, como contraluz del testero Este.
El cierre reutiliza los contornos y pirámides del letrero A, con máscaras por
capas y permanencia final. El cierre conserva sus contornos sin distorsión óptica.
El recorrido anterior `CAM_DRON` de 600 cuadros también se conserva.

Compositor: referencia explícita a cada escena, Bloom diurno, óptica leve,
viñeta y grano; Fog Glow nocturno. Cycles usa GPU; el compositor usa CPU.
La escena nublada es otro estado meteorológico, compatible con las dos paletas.

## Render

Imágenes pendientes: 4K PNG de 16 bits con copia JPEG, OIDN Accurate/High, 1024 muestras y ruido .008
de día / .005 de noche. Dron: 512 muestras, ruido .01, semilla animada,
rebotes 12/6/6/12, transparencia 16, motion blur .5. El render de animación
aplica el perfil de shaders DRON sin nodos AO/Bevel para evitar el coste del perfil
de estudio. Los scripts seleccionan una GPU real antes de comenzar.
El archivo se guarda con shaders DRON para que la animación desde Blender también
use esa simplificación. `render_plan --mode stills --profile final` activa ESTUDIO
para las imágenes fijas.

```powershell
# Render del programa, por imágenes y con reanudación por configuración/hash.
blender --factory-startup -b --disable-autoexec 01_blender/uyuni_v2.blend -P 01_blender/herramientas/render_storyboard.py -- --out 01_blender/renders_video --proposal P1

# Revisar montaje y rangos sin renderizar.
blender --factory-startup -b --disable-autoexec 01_blender/uyuni_v2.blend -P 01_blender/herramientas/render_storyboard.py -- --out 01_blender/renders_video --check

# Validar las 24 vistas sin renderizar. Conserva la geometría de B, cámaras y luces.
blender --factory-startup -b --disable-autoexec --python-exit-code 1 01_blender/uyuni_v2_lateral_zigzag.blend -P 01_blender/herramientas/render_plan.py -- --mode plan-stills --profile final --proposal both --resolution 4k --out 01_blender/renders_finales --compositor optics --transparent-bounces 16

# Imágenes fijas en ambas paletas, incluida la hora azul de P2.
blender --factory-startup -b --disable-autoexec --python-exit-code 1 01_blender/uyuni_v2_lateral_zigzag.blend -P 01_blender/herramientas/render_plan.py -- --mode stills --profile final --proposal both --resolution 4k --out 01_blender/renders_finales --compositor optics --transparent-bounces 16
```

`--only CAM_01_P1` selecciona una vista. Sin `--proposal` se conserva la cola
anterior de 13 trabajos; sin `--resolution 8k` se conserva la salida a 4K.
La hora azul P2 usa una copia temporal de la escena de hora azul, con las mismas
luces y cámara, y las propiedades de color de P2. Las escenas no se guardan
sobre los archivos de diseño.

El lote local se ejecuta con `herramientas/render_lote.py configuracion.json`:
un proceso de Blender por imagen, plan validado, registro de progreso, comprobación
de dimensiones según el plan y PNG de 16 bits, y reanudación por el manifiesto. Cada proceso
activa ESTUDIO: microbisel, rugosidad variable, vidrio y máscaras de aristas,
cavidades y polvo. Se conservan sol 2,7, cielo 0,108, posición de luces,
encuadres y shift de cámaras. Los archivos `materiales.json` y `plan.json`
registran los ajustes utilizados. Los originales locales van a
`D:/Codex_Renders/Uyuni_2026-10-04_4K/`, por el espacio disponible en C:.
Los dos renders terminados en 8K permanecen en la carpeta anterior `_8K`.
La nueva cola registra esos dos como previos y procesa únicamente las 22 pendientes.
Un archivo `PAUSAR_DESPUES_ACTUAL.txt` en la carpeta de control pausa la cola
tras acabar la imagen actual. La versión pública de B conserva el contexto
limpio `CONTEXTO_IA` definido por Claude.

## Verificación y pendientes de aprobación

El video se retoma el 5 de octubre, por tomas independientes. Se mantienen diez
tomas, 120 s y 24 fps para P1/P2. El cliente cambia todas las tomas a 1080p
el 5 de octubre para producir bases destinadas a Google Flow. La toma 09, Ingreso UYUNI,
pasa a hora azul por indicación del cliente: hereda el cielo, exposición, neón
atenuado e interior cálido ya validados, conserva la cámara y los 192 cuadros.
`storyboard.actualizar_hora_azul` permite actualizar un montaje existente y se
comprueba dos veces sin cambiar mallas, cámaras, acciones ni energía de luces.

`render_storyboard.py` separa las salidas en `P1/toma_01` ... `P2/toma_10`,
con manifiesto y PNG16 por fotograma. `--shot 2,3` selecciona tomas;
`--keyframes --draft --width 1280 --samples 32` produce inicio/mitad/final.
`--start N --end M` limita la prueba temporal; `--encode` produce el MP4 de cada
toma con gestión de color consistente. La reanudación verifica la fuente y
los scripts; el MP4 también verifica el manifiesto de entrada. `--pause-file`
pausa antes del siguiente fotograma. `--check` exporta `plan.json` sin render.
Las revisiones locales quedan en `outputs/Video_Tomas`, fuera del repositorio.
El master de dos minutos todavía no se ha producido. Las pruebas 4K de 128 muestras
midieron 55–74 segundos por cuadro, antes de la decisión de producir en 1080p.
`render_video_lote.py` organiza las veinte tomas en bloques de hasta 144 cuadros,
con fuente y scripts congelados, manifiestos, H.264 y reanudación. `video_encode.py`
codifica cada bloque y `video_media.py` verifica resolución, duración y FPS;
el lote compara tres fotogramas decodificados con los PNG de origen. Solo después
de verificar y guardar el MP4 se liberan los PNG temporales del bloque.
El perfil conserva umbral de ruido .01, OIDN, motion blur .5 y rebotes; utiliza
128 muestras y datos persistentes. No se reducen las intensidades de luz.
Las tomas 01 y 10 son comunes a las dos paletas y se reutilizan verificadas.

El cliente elige mantener 128 muestras y activar OpenImageDenoise en GPU.
`render_storyboard.py --denoise-gpu` conserva calidad High, prefilter Accurate,
pasos de albedo/normal, compositor CPU, umbral .01 y los demás parámetros. El
plan, estado y manifiesto registran el dispositivo de reducción de ruido.
El lote lee `denoise_gpu: true` en su configuración. Las pruebas con la escena
ya cargada, mientras seguía la cola, midieron 23,7 → 15,0 s en la toma 03 y
29,6 → 20,9 s en la 09; diferencia RGB media de 0,044 y 0,029 sobre 255.
Son tiempos bajo carga compartida y no una garantía para todas las tomas.
Una interrupción de CUDA después del cuadro 278 se recuperó sin repetir los
cuadros guardados. Se cerró y verificó Salar P1/P2 antes de cambiar el código
congelado de la cola. La transición guarda configuración, estado e identificadores
previos y verifica los SHA de las entregas. La fuente .blend permanece idéntica.
`gpu_retries: 2` permite dos reinicios del proceso de render ante errores GPU,
conservando el manifiesto y sin intervenir en el Blender abierto por el usuario.

`validar_continuacion.py` reabre el archivo y compara las 240 mallas base.
Los cambios autorizados son la dispersión del paisaje, la colocación de los
vehículos proxy, los paños de la fachada trasera solicitados por el cliente y
los objetos del frente (asfalto, pintura, jardineras y plaza). La comparación
enumera expresamente esas mallas y exige que las demás mallas base permanezcan iguales. También
comprueba los ocho paños enrasados, dos nichos, los planos de las seis ventanas
grandes/pequeñas y la puerta frontal. Se comprueban los diez rangos
del montaje, la duración exacta, las referencias del compositor, las verticales
de las cámaras arquitectónicas y todos los cuadros de las trayectorias frente al
volumen principal. Se renderizan inicio/mitad/final de cada plano; esa comprobación
no sustituye una comprobación completa de colisiones con aeronaves, mobiliario
o terreno en producción.

Quedan para revisión: las cotas del frente (fotogrametría, ±0,5 m), los acabados comparativos de
vidrio, el registro de estructura interior
IFC y el reemplazo del minibús genérico. El Land Cruiser está incorporado en la
versión local. Se conserva el vidrio
aprobado `#6E808E`; la alternativa `#A9BCCB` solo aparece en renders comparativos.
La corrección nocturna solicitada después del lote queda guardada en las dos
opciones de paneles, según la referencia posterior del cliente: difusores tipo
neón sobre UYUNI, el grafismo invertido, los montículos y la línea horizontal.
Los cinco objetos luminosos copian las caras frontales CAD, incluidos sus calados;
se separan 8 mm del metal y tienen 4 mm de espesor. La base metálica conserva
corten (P1) y casi negro (P2), y permanece visible sin difusores en las escenas
diurnas. Neón a 4000 K, fuerza de emisión 2,5: aproximadamente una quinta parte
de la primera prueba, reducida por indicación del cliente. El interior conserva
las 30 luces existentes a 3500 K y suma 15 áreas de 600 W dirigidas hacia el fondo
existente. Una capa mate sobre ese fondo y cielo evita los planos emisivos blancos
detrás del vidrio; no añade recintos ni mobiliario. El tinte aprobado permanece.
Exposición, cámaras, materiales originales, animación y las otras 53 luces
permanecen iguales. Los bañadores de la primera prueba se sustituyen por esta
solución luminosa; esa prueba se conserva localmente para comparar.
`continuacion/letrero_nocturno.py` lo reproduce al regenerar. Para un archivo
existente, `herramientas/aplicar_iluminacion_letrero.py` guarda una copia y verifica
las 459 mallas/cámaras, la idempotencia y los ajustes de escenas.
La hora azul P2 queda guardada y su compositor lee la escena correcta.
Las personas y vehículos permanecen estáticos por pedido del cliente del 5 de
octubre: sus acciones ya no son un pendiente de esta producción para Flow.
No se incorpora música ni locución sin archivos autorizados. Los renders
de revisión no constituyen el master final del video de dos minutos.

La revisión de cámaras incluye 30 imágenes (inicio, mitad y final de cada plano).
La prueba temporal del recorrido corto contiene 48 cuadros a 1080p y 24 fps,
con versiones RAW y OIDN; se realizó antes de añadir el Land Cruiser y las nuevas
variantes de personas. Comprueba movimiento y denoising, no la apariencia final
de esos assets. No se ha renderizado el master completo de 120 segundos.

También se verificaron tres vistas de revisión P1, P2 y hora azul a 3840 x 2160,
PNG de 16 bits, 128 muestras y umbral .02. Se renderizaron con OptiX en una
RTX 3070 Laptop; los ajustes de producción del archivo no se modificaron.
