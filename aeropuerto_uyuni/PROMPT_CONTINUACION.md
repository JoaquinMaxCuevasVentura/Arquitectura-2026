# Instrucción para continuar el proyecto con otra IA (v3.1)

Copia el bloque de abajo y pégalo como primer mensaje.

**Adjunta:**
1. `UYUNI_paquete_traspaso_2026-10-04_v3.1.zip`: este repositorio completo y actualizado.
2. `UYUNI_insumos_cliente.zip`: el DXF, los IFC y los PDF originales (el mismo de antes).
3. `UYUNI_renders_opciones_finales.zip`: las dos opciones finales del 4 de octubre en 4K, con sus acercamientos del letrero (el cliente elige entre ellas). Sirven de referencia del aspecto actual.
4. **El avance anterior de la IA:**
   - el `.blend` "formal" en el que venía trabajando y los scripts o archivos que haya generado;
   - si trabaja vía MCP en tu PC, basta con decirle dónde está el `.blend`.

`UYUNI_novedades_desde_v3.zip` trae solo lo nuevo desde el paquete v3. Sirve si la IA ya tiene el v3: en ese caso, usa el mensaje corto de `LEEME_PRIMERO.md` en lugar de este prompt.

Si la IA no acepta zips, sube por separado al menos estos archivos:
- `TRASPASO.md`, `CAMBIOS_REUNION_3OCT.md`, `00_auditoria/AUDITORIA.md`, `02_postproduccion/GUIA_REALISMO_FOTOGRAFICO.md` y `02_postproduccion/MUESTREO_Y_RENDIMIENTO.md`;
- `01_blender/uyuni_modelo.py`, `01_blender/herramientas/aplicar_cambios_reunion.py` y `aplicar_cambios_4oct.py`;
- `01_blender/inventario_escena.json`, las hojas de `01_blender/propuestas/` y las de `01_blender/fotorrealismo/`;
- el DXF original.

---

```text
Vas a continuar un proyecto de visualización arquitectónica en Blender 5.2 (Cycles) con Python (bpy): la Terminal de Pasajeros del Aeropuerto de Uyuni, en Bolivia. No empieces de cero.

Contexto:
- Ya trabajaste en este proyecto a partir del primer paquete de traspaso (commit 7b19bea), pero tu sesión se cortó a mitad de camino. Tu avance quedó en el .blend "formal" que te adjunto (o te indico) y en los scripts que hayas generado.
- Mientras tanto, otro asistente hizo seis cosas sobre el modelo de la versión anterior (la sexta, al final de la lista):
  1. implementó los cambios de la reunión con el cliente del 3 de octubre (aeropuerto_uyuni/CAMBIOS_REUNION_3OCT.md) y las decisiones del 4 de octubre (TRASPASO.md, sección 5);
  2. renderizó en 4K las dos opciones finales que eligió el cliente (las tienes en UYUNI_renders_opciones_finales.zip);
  3. investigó y probó en el modelo cómo llegar al realismo fotográfico: cámaras, exposición, materiales, vidrio y luz nocturna;
  4. midió en la escena qué ajustes de render pagan y cuáles no, y cómo atraviesa la luz el vidrio (02_postproduccion/MUESTREO_Y_RENDIMIENTO.md);
  5. dejó todo resumido en aeropuerto_uyuni/02_postproduccion/GUIA_REALISMO_FOTOGRAFICO.md, con un documento de detalle por tema;
  6. con los DXF nuevos del cliente (4 de octubre) modeló:
     - la fachada Lado Aire y los testeros ESTE y OESTE;
     - las mangas y dos 737-800;
     - las veredas y el camino de servicio;
     - los nichos de la fachada principal solo en los ventanales;
     - las puertas ME-2 y el retenedor de nieve según sus detalles.
     Está en aeropuerto_uyuni/CAMBIOS_4OCT_FACHADAS.md y lo verificó sin renders, con láminas 2D (01_blender/verificacion/).

Adjuntos:
1. UYUNI_paquete_traspaso_2026-10-04_v3.1.zip:
   - el modelo paramétrico actualizado (01_blender/uyuni_modelo.py) y su .blend;
   - los scripts que aplican solo los cambios del 3 y del 4 de octubre sobre un .blend existente (01_blender/herramientas/aplicar_cambios_reunion.py y aplicar_cambios_4oct.py);
   - TRASPASO.md, con las decisiones del cliente;
   - la guía de realismo y sus cuatro documentos de detalle (02_postproduccion/), con las pruebas que ya funcionan en 5.2 (01_blender/herramientas/prueba_*.py) y sus hojas (01_blender/fotorrealismo/).
2. UYUNI_insumos_cliente.zip: el DXF, los IFC y los PDF originales.
3. UYUNI_renders_opciones_finales.zip: las dos opciones finales del 4 de octubre (P1 con letras corten y P2 con letras y muros casi negros, las dos con la geometría A); el cliente elige entre ellas.
4. Tu avance anterior: el .blend formal y tus scripts.

Antes de proponer nada, lee completos TRASPASO.md, CAMBIOS_REUNION_3OCT.md, CAMBIOS_4OCT_FACHADAS.md, GUIA_REALISMO_FOTOGRAFICO.md y MUESTREO_Y_RENDIMIENTO.md. Si necesitas saber de dónde sale una medida, consulta 00_auditoria/AUDITORIA.md.

Tareas, en este orden. Después de cada una, muéstrame el antes y el después con la misma cámara y la misma luz.

0. Revisa qué tenías adelantado y repórtamelo antes de seguir.
   - Inventaría el .blend formal y tus scripts: colecciones, objetos, materiales y assets que agregaste, y qué modificaste del modelo base.
   - Compáralo con los pendientes de TRASPASO.md (secciones 6 y 8) y con la guía de realismo. Arma una lista: hecho, a medias, no empezado.
   - No rehagas lo que ya está hecho ni descartes tu avance.

1. Integra los cambios de la reunión en el formal sin perder tu avance.
   - Si no modificaste uyuni_modelo.py: copia el .blend formal y ejecuta sobre la copia 01_blender/herramientas/aplicar_cambios_reunion.py (CAMBIOS_REUNION_3OCT.md, sección 2A) y después aplicar_cambios_4oct.py (decisiones del 4 de octubre: letras y muros casi negros en P2, vidrio elegido, geometría A).
   - Si modificaste tu copia del script: porta los cambios a mano con la sección 2C y aeropuerto_uyuni/CAMBIOS_REUNION_3OCT_uyuni_modelo.diff; las del 4 de octubre están en TRASPASO.md (sección 5, puntos 2, 11 y 12) y en uyuni_modelo.py (LETRAS_GRIS, VIDRIO, mat_letrero, mat_vidrio y mat_emisor).
   - Verifica con CAM_07_PROPUESTAS en UYUNI_DIA (P1) y UYUNI_DIA_P2_SALAR_LITIO (P2), contra los renders de las opciones finales.

2. La revisión contra el DXF ya está hecha (CAMBIOS_4OCT_FACHADAS.md, con los DXF nuevos del cliente del 4 de octubre):
   - Lado Aire;
   - testeros ESTE y OESTE;
   - nichos de la fachada principal;
   - puertas ME-2;
   - retenedor de nieve;
   - mangas y aviones.
   Si tu .blend formal es anterior, regenera la geometría desde uyuni_modelo.py (no hay parche para estos cambios) y vuelve a enlazar tus colecciones. No cambies la cumbrera ni los puntos de la sección 8 de ese documento: solo dime qué encuentras.

3. Cámaras (guía, sección 1): verticales rectas con shift_y en CAM_01, CAM_03, CAM_05 y CAM_06; altura de ojos; lentes de 24 a 35 mm.

4. Física de los materiales y luz de día (guía, secciones 2, 3 y 5):
   - metálico binario y albedos dentro de 0,03–0,85, según la tabla de MATERIALES_INTELIGENTES.md (sección 3);
   - después, sol y cielo calibrados con False Color (punto de partida probado: ×0,6). La exposición de la cámara queda en 0;
   - microbisel, rugosidad variable y Diffuse Roughness.

5. Materiales inteligentes y vidrio: el prompt de MATERIALES_INTELIGENTES.md (sección 7), completo, con la receta del vidrio (sección 4).
   - En Cycles, el sol no atraviesa el vidrio (MUESTREO_Y_RENDIMIENTO.md, sección 3). Cuando modeles la estructura detrás del vidrio, usa el vidrio transparente para los rayos de sombra de esa sección.
   - El vidrio elegido deja pasar 2,9 % de la luz, y con eso la estructura no se ve de día. No cambies el tinte sin preguntarme: prepárame la comparación con #A9BCCB y la misma capa (15 %) en CAM_05 y CAM_07.

6. Contexto y paisaje con assets de Poly Haven (TRASPASO 8.1 y guía, sección 6):
   - suelo de tierra y grava clara con costras de sal; paja brava y tola; cerros bajos;
   - sin árboles ni césped; calzada y plataforma libres; escala real de las texturas.
   Después, vehículos y personas reales en lugar de los 15 proxies (TRASPASO 8.2).

6b. Lado Aire (pedido del cliente del 4 de octubre; TRASPASO 5.13, 5.14 y 8.7):
   - ya están en el modelo:
     - las dos mangas, en las puertas de embarque del nivel 1P;
     - dos 737-800 genéricos con librea blanca (mangas_y_aviones);
     - veredas, camino de servicio, plataforma y marcas (entorno_aire);
   - librea de BoA, la aerolínea estatal: pregúntame antes de usarla;
   - falta la pista real (4000 × 45 m, cabeceras 13/31, casi paralela a la fachada), con la calle de rodaje, la señalización OACI y su extensión hasta el horizonte, para que las tomas aéreas no muestren vacíos.

7. Escena nocturna: el prompt de ILUMINACION_NOCTURNA.md (sección 5).

8. Cielo (TRASPASO 8.3): luz de mañana sincronizada con el sol del script y una variante de cielo nublado invernal.

9. Compositor, render y video (guía, secciones 7 y 8; TRASPASO 8.4 y 8.5). Los ajustes de render salen del prompt de MUESTREO_Y_RENDIMIENTO.md (sección 5): perfiles de borrador y final, y el video del dron con semilla animada. Déjalo listo para que yo renderice en mi PC con GPU:
   - CAM_01 a CAM_07 en 4K, con las dos propuestas en CAM_07;
   - video del dron en 1080p, 24 fps, MP4 H.264.

Reglas:
- No cambies las decisiones del cliente (TRASPASO.md, sección 5) sin preguntarme. En particular:
  - el letrero "línea de horizonte" va despegado 12 cm de la chapa, con pirámides facetadas en 3D, y lleva un juego de 3 pirámides sin texto sobre la puerta de salida;
  - las dos propuestas de color tienen que seguir funcionando hasta que el cliente elija:
    - P1 "Patrimonio Ferroviario": corten, parapeto antracita, letrero corten;
    - P2 "Salar & Litio": blanco integral; letras y pirámides en gris casi negro (#2E3133) y muros casi negros (#36393B), decisión del 4 de octubre;
    - geometría del letrero: la A (tamaño original, sin reducción), decidida el 4 de octubre. La B se conserva, pero ya no se entrega;
    - todo se maneja con las propiedades de escena "propuesta", "letras_corten" y "letras_gris" y con las colecciones LETRERO_A_SOBRESALE y LETRERO_B_CONTENIDO;
  - el retenedor de nieve sigue el detalle del cliente: abrazadera de 174 × 113 mm con tres tubos, a 1,398 m del borde medido sobre la pendiente (RETENEDOR);
  - en la fachada principal solo los vanos con ME-1/ME-2 van en nicho; los demás paños, al ras de las columnas;
  - las puertas ME-2 siguen su detalle: hojas corredizas por dentro, viga de acero negro mate y operador;
  - muros y columnas de revoque continuo, sin juntas y con buñas solo en la viga;
  - cielo del alero listonado sobre plenum negro;
  - carpintería antracita mate;
  - sin bolardos ni postes de iluminación peatonal;
  - el hero shot es con luz de mañana;
  - vidrio de las fachadas (4 de octubre): DVH con laminado incoloro de 3+3 mm adentro y 4 mm con control solar afuera; tono oscuro y poca reflexión, para que la fachada no parezca un espejo ciego y deje ver la estructura de adentro. Ya está en el modelo (VIDRIO; MATERIALES_INTELIGENTES.md, sección 4, variante 6);
  - Lado Aire (4 de octubre): perspectiva general aprobada. La fachada, los laterales, las mangas y los aviones ya están según los DXF nuevos (CAMBIOS_4OCT_FACHADAS.md). Falta la pista hasta el horizonte (paso 6b).
- Realismo (guía de realismo):
  - mejora la manera de fotografiar el edificio, no el edificio;
  - los colores de PALETA no se tocan; el metálico y la rugosidad sí, según la tabla, y dime el valor anterior y el nuevo;
  - la terminal es nueva: sin desgaste, grietas, óxido corrido ni mugre oscura. Solo un polvo claro y salino de días;
  - mide siempre con False Color, con las metas de la guía (sección 2);
  - no bajes los rebotes, no apagues las cáusticas ni bajes el clamp para ganar tiempo: en esta escena no ahorran y oscurecen (MUESTREO_Y_RENDIMIENTO.md). Para iterar, umbral de ruido 0,03.
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
