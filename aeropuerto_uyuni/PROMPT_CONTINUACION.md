# Instrucción para continuar el proyecto con otra IA

Copia el bloque de abajo y pégalo como primer mensaje.

**Adjunta:**
1. `UYUNI_paquete_traspaso_2026-10-03_v2.zip`: este repositorio actualizado, con los cambios de la reunión del 3 de octubre.
2. `UYUNI_insumos_cliente.zip`: el DXF, los IFC y los PDF originales.
3. **El avance anterior de la IA:**
   - el `.blend` "formal" en el que venía trabajando y los scripts o archivos que haya generado;
   - si trabaja vía MCP en tu PC, basta con decirle dónde está el `.blend`.

`UYUNI_cambios_reunion_3oct.zip` trae solo los cambios. Sirve si prefieres pasarlos a mano o si la IA ya tiene el paquete anterior.

Si la IA no acepta zips, sube por separado al menos estos archivos:
- `TRASPASO.md`, `CAMBIOS_REUNION_3OCT.md` y `00_auditoria/AUDITORIA.md`;
- `01_blender/uyuni_modelo.py` y `01_blender/herramientas/aplicar_cambios_reunion.py`;
- `01_blender/inventario_escena.json` y las hojas de `01_blender/propuestas/`;
- el DXF original.

---

```text
Vas a continuar un proyecto de visualización arquitectónica en Blender 5.2 (Cycles) con Python (bpy): la Terminal de Pasajeros del Aeropuerto de Uyuni, en Bolivia. No empieces de cero.

Contexto:
- Ya trabajaste en este proyecto a partir del primer paquete de traspaso (commit 7b19bea), pero tu sesión se cortó a mitad de camino. Tu avance quedó en el .blend "formal" que te adjunto (o te indico) y en los scripts que hayas generado.
- Mientras tanto, el 3 de octubre hubo una reunión con el cliente y otro asistente implementó sus cambios sobre el modelo de la versión anterior. Están en el paquete nuevo, descritos en aeropuerto_uyuni/CAMBIOS_REUNION_3OCT.md.

Adjuntos:
1. UYUNI_paquete_traspaso_2026-10-03_v2.zip:
   - el modelo paramétrico actualizado (01_blender/uyuni_modelo.py) y su .blend;
   - el script que aplica solo los cambios de la reunión sobre un .blend existente (01_blender/herramientas/aplicar_cambios_reunion.py);
   - la guía TRASPASO.md, actualizada con las decisiones del 3 de octubre;
   - la auditoría, las verificaciones contra el CAD y las hojas de las dos propuestas (01_blender/propuestas/).
2. UYUNI_insumos_cliente.zip: el DXF, los IFC y los PDF originales.
3. Tu avance anterior: el .blend formal y tus scripts.

Antes de proponer nada, lee completos TRASPASO.md y CAMBIOS_REUNION_3OCT.md. Si necesitas saber de dónde sale una medida, consulta 00_auditoria/AUDITORIA.md.

Tareas, en este orden:

0. Primero, revisa qué tenías adelantado y repórtamelo antes de seguir.
   - Inventaría el .blend formal y tus scripts: qué colecciones, objetos, materiales y assets agregaste, y qué modificaste del modelo base.
   - Compáralo con los pendientes de TRASPASO.md (secciones 6 y 8) y arma una lista: hecho, a medias, no empezado.
   - No rehagas lo que ya está hecho ni descartes tu avance.

1. Integra los cambios de la reunión en el formal sin perder tu avance.
   - Si no modificaste uyuni_modelo.py: haz una copia del .blend formal y ejecuta 01_blender/herramientas/aplicar_cambios_reunion.py sobre ella (CAMBIOS_REUNION_3OCT.md, sección 2A).
   - Si modificaste tu copia del script: porta los cambios a mano, con el .diff y la sección 2C.
   - Verifica con CAM_07_PROPUESTAS en las escenas UYUNI_DIA (P1) y UYUNI_DIA_P2_SALAR_LITIO (P2) contra las hojas de 01_blender/propuestas/.
   - Avísame si algo de tu avance choca con los cambios (por ejemplo, si moviste la cubierta y el retenedor de nieve ya no apoya en la chapa).

2. Completa lo que falte de la revisión contra el DXF (TRASPASO.md, sección 6).
   - Testero del eje 20: puertas y vanos.
   - Volumen saliente y elemento vertical de la esquina del eje 1 / Lado Aire.
   - Carpinterías del Lado Aire (ME-4, ME-5 y ME-6).
   - No cambies la cumbrera (+13,02 contra +13,43): solo dime qué encuentras.

3. Contexto y paisaje de altiplano (sección 8.1), con assets de Poly Haven (CC0):
   - suelo de tierra y grava clara con textura PBR;
   - matas de paja brava dispersas;
   - relieve suave y cerros bajos en el horizonte;
   - estilo sobrio, al modo de Mathias Klotz;
   - calzada y plataforma libres.

4. Reemplaza los 15 proxies por vehículos y personas reales (sección 8.2), en las posiciones de inventario_escena.json: vagonetas 4x4 tipo Land Cruiser, minibuses de transfer y turistas abrigados.

5. Cielo (sección 8.3):
   - mantén la luz de mañana sincronizada con el sol del script;
   - si usas un HDRI, rótalo para que su sol coincida;
   - agrega la variante de cielo nublado invernal.

6. Deja lista la configuración de renders y video (secciones 8.4 y 8.5), para que yo renderice en mi PC con GPU:
   - CAM_01 a CAM_07 en 4K, con las dos propuestas en CAM_07 (01_blender/herramientas/render_propuestas.py ya lo hace);
   - video del dron en 1080p, 24 fps, MP4 H.264.

Reglas:
- No cambies las decisiones del cliente (TRASPASO.md, sección 5) sin preguntarme. En particular:
  - el letrero "línea de horizonte" va despegado 12 cm de la chapa, con pirámides facetadas en 3D, y lleva un juego de 3 pirámides sin texto sobre la puerta de salida;
  - hay dos propuestas de color y dos geometrías del letrero, y las cuatro combinaciones tienen que seguir funcionando hasta que el cliente elija:
    - P1 "Patrimonio Ferroviario": corten, parapeto antracita, letrero corten;
    - P2 "Salar & Litio": blanco integral, muros grises;
    - geometría A: sobresale; geometría B: contenida;
    - todo se maneja con las propiedades de escena "propuesta" y "letras_corten" y con las colecciones LETRERO_A_SOBRESALE y LETRERO_B_CONTENIDO;
  - el retenedor de nieve es un doble tubo de 1", de 18 cm de alto, sobre la primera correa;
  - muros y columnas de revoque continuo, sin juntas y con buñas solo en la viga;
  - cielo del alero listonado sobre plenum negro;
  - carpintería antracita mate;
  - sin bolardos ni postes de iluminación peatonal;
  - el hero shot es con luz de mañana.
- uyuni_modelo.py es la fuente de verdad del edificio:
  - todo cambio de geometría va en el script, con medidas numéricas del DXF;
  - el DXF solo sirve para verificar: no calques ni importes sus líneas.
- Mantén las coordenadas (las del IFC, en metros), el prefijo UY_ y las colecciones del script.
  - Las transformaciones DXF → modelo están en TRASPASO.md, sección 4.
  - Ojo: en el DXF, la FACHADA ESTE es el testero del eje 20 y la OESTE es la del eje 1.
- Contexto y assets van en colecciones propias (por ejemplo, 10_CONTEXTO_PAISAJE y 11_VEHICULOS_PERSONAS), enlazadas en las tres escenas: UYUNI_DIA, UYUNI_DIA_P2_SALAR_LITIO y UYUNI_CREPUSCULO.
  - Mejor todavía: cárgalos por código, con una función en el script, para que todo siga siendo regenerable.
  - Al regenerar, uyuni_modelo.py borra lo que haya dentro de SUS colecciones, incluidas 06_ENTORNO_SITE y 07_ASSETS (TRASPASO.md, sección 7).
- Para cada asset externo (Poly Haven u otro), registra en 01_blender/assets/CREDITOS.md la fuente, el autor, la licencia y la URL. Las licencias deben permitir uso comercial.
- Si algo del CAD es ambiguo o contradice una decisión, pregúntame antes de suponer.
- Plazos: los renders vencen el domingo 4 de octubre y el video del dron el lunes 5. Prioriza lo que se ve en CAM_01, CAM_04, CAM_07 y en el recorrido del dron.

Entrega:
- el informe del paso 0: qué tenías hecho, a medias y pendiente;
- el uyuni_modelo.py y el .blend actualizados, más los assets nuevos con su CREDITOS.md;
- una lista de cambios con el valor anterior y el nuevo de cada parámetro;
- capturas o renders de verificación, en lo posible con los encuadres de 01_blender/verificacion/ y CAM_07;
- lo que no pudiste resolver y por qué.
```
