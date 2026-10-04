# Instrucción para continuar el proyecto con otra IA (v3)

Copia el bloque de abajo y pégalo como primer mensaje.

**Adjunta:**
1. `UYUNI_paquete_traspaso_2026-10-04_v3.zip`: este repositorio completo y actualizado.
2. `UYUNI_insumos_cliente.zip`: el DXF, los IFC y los PDF originales (el mismo de antes).
3. `UYUNI_renders_finales.zip`: los renders entregados de las dos propuestas (el cliente todavía elige), que sirven de referencia del aspecto actual.
4. **El avance anterior de la IA:**
   - el `.blend` "formal" en el que venía trabajando y los scripts o archivos que haya generado;
   - si trabaja vía MCP en tu PC, basta con decirle dónde está el `.blend`.

`UYUNI_novedades_desde_v2.zip` trae solo lo nuevo desde el paquete v2. Sirve si la IA ya tiene el v2.

Si la IA no acepta zips, sube por separado al menos estos archivos:
- `TRASPASO.md`, `CAMBIOS_REUNION_3OCT.md`, `00_auditoria/AUDITORIA.md` y `02_postproduccion/GUIA_REALISMO_FOTOGRAFICO.md`;
- `01_blender/uyuni_modelo.py` y `01_blender/herramientas/aplicar_cambios_reunion.py`;
- `01_blender/inventario_escena.json`, las hojas de `01_blender/propuestas/` y las de `01_blender/fotorrealismo/`;
- el DXF original.

---

```text
Vas a continuar un proyecto de visualización arquitectónica en Blender 5.2 (Cycles) con Python (bpy): la Terminal de Pasajeros del Aeropuerto de Uyuni, en Bolivia. No empieces de cero.

Contexto:
- Ya trabajaste en este proyecto a partir del primer paquete de traspaso (commit 7b19bea), pero tu sesión se cortó a mitad de camino. Tu avance quedó en el .blend "formal" que te adjunto (o te indico) y en los scripts que hayas generado.
- Mientras tanto, otro asistente hizo cuatro cosas sobre el modelo de la versión anterior:
  1. implementó los cambios de la reunión con el cliente del 3 de octubre (aeropuerto_uyuni/CAMBIOS_REUNION_3OCT.md);
  2. renderizó las dos propuestas de color en 4K (las tienes en UYUNI_renders_finales.zip);
  3. investigó y probó en el modelo cómo llegar al realismo fotográfico: cámaras, exposición, materiales, vidrio y luz nocturna;
  4. dejó todo resumido en aeropuerto_uyuni/02_postproduccion/GUIA_REALISMO_FOTOGRAFICO.md, con un documento de detalle por tema.

Adjuntos:
1. UYUNI_paquete_traspaso_2026-10-04_v3.zip:
   - el modelo paramétrico actualizado (01_blender/uyuni_modelo.py) y su .blend;
   - el script que aplica solo los cambios de la reunión sobre un .blend existente (01_blender/herramientas/aplicar_cambios_reunion.py);
   - TRASPASO.md, con las decisiones del cliente;
   - la guía de realismo y sus tres documentos de detalle (02_postproduccion/), con las pruebas que ya funcionan en 5.2 (01_blender/herramientas/prueba_*.py) y sus hojas (01_blender/fotorrealismo/).
2. UYUNI_insumos_cliente.zip: el DXF, los IFC y los PDF originales.
3. UYUNI_renders_finales.zip: los renders entregados de las dos propuestas (el cliente todavía no eligió).
4. Tu avance anterior: el .blend formal y tus scripts.

Antes de proponer nada, lee completos TRASPASO.md, CAMBIOS_REUNION_3OCT.md y GUIA_REALISMO_FOTOGRAFICO.md. Si necesitas saber de dónde sale una medida, consulta 00_auditoria/AUDITORIA.md.

Tareas, en este orden. Después de cada una, muéstrame el antes y el después con la misma cámara y la misma luz.

0. Revisa qué tenías adelantado y repórtamelo antes de seguir.
   - Inventaría el .blend formal y tus scripts: colecciones, objetos, materiales y assets que agregaste, y qué modificaste del modelo base.
   - Compáralo con los pendientes de TRASPASO.md (secciones 6 y 8) y con la guía de realismo. Arma una lista: hecho, a medias, no empezado.
   - No rehagas lo que ya está hecho ni descartes tu avance.

1. Integra los cambios de la reunión en el formal sin perder tu avance.
   - Si no modificaste uyuni_modelo.py: copia el .blend formal y ejecuta 01_blender/herramientas/aplicar_cambios_reunion.py sobre la copia (CAMBIOS_REUNION_3OCT.md, sección 2A).
   - Si modificaste tu copia del script: porta los cambios a mano con la sección 2C y aeropuerto_uyuni/CAMBIOS_REUNION_3OCT_uyuni_modelo.diff.
   - Verifica con CAM_07_PROPUESTAS en UYUNI_DIA (P1) y UYUNI_DIA_P2_SALAR_LITIO (P2), contra los renders finales.

2. Completa la revisión contra el DXF (TRASPASO.md, sección 6):
   - testero del eje 20;
   - esquina del eje 1 / Lado Aire;
   - carpinterías ME-4, ME-5 y ME-6.
   No cambies la cumbrera: solo dime qué encuentras.

3. Cámaras (guía, sección 1): verticales rectas con shift_y en CAM_01, CAM_03, CAM_05 y CAM_06; altura de ojos; lentes de 24 a 35 mm.

4. Física de los materiales y luz de día (guía, secciones 2, 3 y 5):
   - metálico binario y albedos dentro de 0,03–0,85, según la tabla de MATERIALES_INTELIGENTES.md (sección 3);
   - después, sol y cielo calibrados con False Color (punto de partida probado: ×0,6). La exposición de la cámara queda en 0;
   - microbisel, rugosidad variable y Diffuse Roughness.

5. Materiales inteligentes y vidrio: el prompt de MATERIALES_INTELIGENTES.md (sección 7), completo, con la receta del vidrio (sección 4).

6. Contexto y paisaje con assets de Poly Haven (TRASPASO 8.1 y guía, sección 6):
   - suelo de tierra y grava clara con costras de sal; paja brava y tola; cerros bajos;
   - sin árboles ni césped; calzada y plataforma libres; escala real de las texturas.
   Después, vehículos y personas reales en lugar de los 15 proxies (TRASPASO 8.2).

6b. Lado Aire (pedido del cliente del 4 de octubre; TRASPASO 5.13 y 8.7):
   - dos mangas de abordaje generadas por código, en las puertas del modelo del cliente;
   - aeronaves Boeing 737-800 de BoA, la aerolínea estatal. Pregúntame antes de usar su librea; si no se puede, va una librea blanca genérica;
   - la pista real (4000 × 45 m, cabeceras 13/31, casi paralela a la fachada), con la calle de rodaje, la señalización OACI y su extensión hasta el horizonte, para que las tomas aéreas no muestren vacíos.

7. Escena nocturna: el prompt de ILUMINACION_NOCTURNA.md (sección 5).

8. Cielo (TRASPASO 8.3): luz de mañana sincronizada con el sol del script y una variante de cielo nublado invernal.

9. Compositor, render y video (guía, secciones 7 y 8; TRASPASO 8.4 y 8.5). Déjalo listo para que yo renderice en mi PC con GPU:
   - CAM_01 a CAM_07 en 4K, con las dos propuestas en CAM_07;
   - video del dron en 1080p, 24 fps, MP4 H.264.

Reglas:
- No cambies las decisiones del cliente (TRASPASO.md, sección 5) sin preguntarme. En particular:
  - el letrero "línea de horizonte" va despegado 12 cm de la chapa, con pirámides facetadas en 3D, y lleva un juego de 3 pirámides sin texto sobre la puerta de salida;
  - las dos propuestas de color y las dos geometrías del letrero tienen que seguir funcionando hasta que el cliente elija:
    - P1 "Patrimonio Ferroviario": corten, parapeto antracita, letrero corten;
    - P2 "Salar & Litio": blanco integral, muros grises;
    - geometría A: sobresale; geometría B: contenida;
    - todo se maneja con las propiedades de escena "propuesta" y "letras_corten" y con las colecciones LETRERO_A_SOBRESALE y LETRERO_B_CONTENIDO;
  - el retenedor de nieve es un doble tubo de 1", de 18 cm de alto, sobre la primera correa;
  - muros y columnas de revoque continuo, sin juntas y con buñas solo en la viga;
  - cielo del alero listonado sobre plenum negro;
  - carpintería antracita mate;
  - sin bolardos ni postes de iluminación peatonal;
  - el hero shot es con luz de mañana;
  - vidrio de las fachadas (4 de octubre): DVH con laminado incoloro de 3+3 mm adentro y 4 mm con control solar afuera; tono oscuro y poca reflexión, para que la fachada no parezca un espejo ciego y deje ver la estructura de adentro (MATERIALES_INTELIGENTES.md, sección 4, variante 6);
  - Lado Aire (4 de octubre): perspectiva general aprobada; faltan mangas, aeronaves y la pista hasta el horizonte (paso 6b).
- Realismo (guía de realismo):
  - mejora la manera de fotografiar el edificio, no el edificio;
  - los colores de PALETA no se tocan; el metálico y la rugosidad sí, según la tabla, y dime el valor anterior y el nuevo;
  - la terminal es nueva: sin desgaste, grietas, óxido corrido ni mugre oscura. Solo un polvo claro y salino de días;
  - mide siempre con False Color, con las metas de la guía (sección 2).
- uyuni_modelo.py es la fuente de verdad del edificio:
  - todo cambio de geometría va en el script, con medidas numéricas del DXF;
  - el DXF solo sirve para verificar: no calques ni importes sus líneas.
- Todo lo que hagas tiene que poder regenerarse: funciones en el script o scripts propios que corran después del modelo. Nada a mano sin dejarlo en código.
- Mantén las coordenadas (las del IFC, en metros), el prefijo UY_ y las colecciones del script.
  - Las transformaciones DXF → modelo están en TRASPASO.md, sección 4.
  - Ojo: en el DXF, la FACHADA ESTE es el testero del eje 20 y la OESTE es la del eje 1.
- Contexto y assets van en colecciones propias (por ejemplo, 10_CONTEXTO_PAISAJE y 11_VEHICULOS_PERSONAS), enlazadas en las tres escenas y cargadas por código.
  - Al regenerar, uyuni_modelo.py borra lo que haya dentro de SUS colecciones (TRASPASO.md, sección 7).
  - Registra cada asset externo en 01_blender/assets/CREDITOS.md: fuente, autor, licencia y URL. Las licencias deben permitir uso comercial.
- Antes de usar la API, revisa las trampas de Blender 5.2: TRASPASO.md (sección 10) y la guía (sección 10).
- Si algo del CAD es ambiguo o contradice una decisión, pregúntame antes de suponer.
- Prioriza lo que se ve en CAM_01, CAM_03, CAM_04, CAM_07, en la perspectiva del Lado Aire y en el recorrido del dron. El video del dron vence el lunes 5 de octubre.

Entrega:
- el informe del paso 0: qué tenías hecho, a medias y pendiente;
- el uyuni_modelo.py y el .blend actualizados, más los assets nuevos con su CREDITOS.md;
- una lista de cambios con el valor anterior y el nuevo de cada parámetro;
- en cada paso: antes y después, False Color y tiempo de render;
- lo que no pudiste resolver y por qué.
```
