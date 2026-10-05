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
fijas, que antes la omitía. Las 12 vistas en ambas paletas supondrían 24 imágenes;
la configuración completa de ese lote en 8K queda para la reanudación.
Por indicación del cliente, los renders finales y el video quedan en pausa tras
guardar esta corrección. No se ha iniciado el lote de 8K.

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

Imágenes: 4K PNG de 16 bits, OIDN Accurate/High, 1024 muestras y ruido .008
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

# Imágenes fijas. P2 se incluye como CAM_07_P2.
blender --factory-startup -b --disable-autoexec 01_blender/uyuni_v2.blend -P 01_blender/herramientas/render_plan.py -- --mode stills --profile final --out 01_blender/renders_finales --compositor optics --transparent-bounces 16
```

## Verificación y pendientes de aprobación

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
vidrio, la iluminación del letrero nocturno, el registro de estructura interior
IFC y el reemplazo del minibús genérico. El Land Cruiser está incorporado en la
versión local. Se conserva el vidrio
aprobado `#6E808E`; la alternativa `#A9BCCB` solo aparece en renders comparativos.
Halo y bañadores nocturnos se ensayan sin guardarlos sobre la escena de trabajo.
Las personas y vehículos son contexto estático: falta animar sus acciones del
guion. No se incorpora música ni locución sin archivos autorizados. Los renders
de revisión no constituyen el master final del video de dos minutos.

La revisión de cámaras incluye 30 imágenes (inicio, mitad y final de cada plano).
La prueba temporal del recorrido corto contiene 48 cuadros a 1080p y 24 fps,
con versiones RAW y OIDN; se realizó antes de añadir el Land Cruiser y las nuevas
variantes de personas. Comprueba movimiento y denoising, no la apariencia final
de esos assets. No se ha renderizado el master completo de 120 segundos.

También se verificaron tres vistas de revisión P1, P2 y hora azul a 3840 x 2160,
PNG de 16 bits, 128 muestras y umbral .02. Se renderizaron con OptiX en una
RTX 3070 Laptop; los ajustes de producción del archivo no se modificaron.
