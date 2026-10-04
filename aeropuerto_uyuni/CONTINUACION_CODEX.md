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
Sprinter encontrado requiere acceso adicional que no se ha confirmado.
La vegetación procedural se sustituye por 21.975 instancias de tres matas
escaneadas de Poly Haven con textura seca: LOD0 cerca del frente y LOD2 a partir
de 110 m. No se realiza la geometría de las instancias. También se usan suelo
PBR con deformación suave de coordenadas para reducir repetición y HDRI de
Poly Haven. El catálogo oficial consultado no ofrecía personas
ni vehículos de pasajeros adecuados; esas sustituciones tienen fuentes separadas.

## Exteriores revisados por las imágenes del cliente

Se conservan la vereda, las dársenas y el drenaje junto a la fachada A111.
El frente se reorganiza con tres franjas oscuras de circulación, cada una con
una jardinera interior ovalada, dos cruces alineados con los ingresos, una fila
de estacionamiento en espiga y una vía exterior más próxima al edificio.
Las franjas oscuras son circulación: no se rellenan enteras con vegetación.
La paja se recorta fuera de las circulaciones y se coloca en las jardineras.

Las dimensiones nuevas son una propuesta basada en imágenes sin escala:
franja de circulación de 5 m, jardinera de 1,44 m de ancho, cordón de 18 cm,
carril exterior de 7 m y fila en espiga de 5 m. Contrastar con el plano antes de
usar esas cotas para obra. Los objetos del trazado anterior se conservan ocultos.

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
blender -b 01_blender/uyuni_v2.blend -P 01_blender/herramientas/render_storyboard.py -- --out 01_blender/renders_video --proposal P1

# Revisar montaje y rangos sin renderizar.
blender -b 01_blender/uyuni_v2.blend -P 01_blender/herramientas/render_storyboard.py -- --out 01_blender/renders_video --check

# Imágenes fijas. P2 se incluye como CAM_07_P2.
blender -b 01_blender/uyuni_v2.blend -P 01_blender/herramientas/render_plan.py -- --mode stills --profile final --out 01_blender/renders_finales --compositor optics --transparent-bounces 16
```

## Verificación y pendientes de aprobación

`validar_continuacion.py` reabre el archivo y compara las 240 mallas base.
Los cambios autorizados son la dispersión del paisaje, la colocación de los dos
vehículos estacionados y los paños de la fachada trasera solicitados por el
cliente. La comparación enumera expresamente esas diez mallas modificadas o
eliminadas y exige que las demás mallas base permanezcan iguales. También
comprueba los ocho paños enrasados, dos nichos, los planos de las seis ventanas
grandes/pequeñas y la puerta frontal. Se comprueban los diez rangos
del montaje, la duración exacta, las referencias del compositor, las verticales
de las cámaras arquitectónicas y todos los cuadros de las trayectorias frente al
volumen principal. Se renderizan inicio/mitad/final de cada plano; esa comprobación
no sustituye una comprobación completa de colisiones con aeronaves, mobiliario
o terreno en producción.

Quedan para revisión: el trazado nuevo y sus cotas, los acabados comparativos de
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
