# Instrucción para continuar el proyecto con otra IA

Copia el bloque de abajo y pégalo como primer mensaje. Adjunta los dos zips:
- `UYUNI_paquete_traspaso_….zip` (este repositorio);
- `UYUNI_insumos_cliente.zip` (el DXF, los IFC y los PDF originales).

Si la IA no acepta zips, sube por separado al menos estos archivos:
- `TRASPASO.md`, `00_auditoria/AUDITORIA.md` y `01_blender/uyuni_modelo.py`;
- `01_blender/inventario_escena.json` y las imágenes de `01_blender/verificacion/`;
- el DXF original.

---

```text
Vas a continuar un proyecto de visualización arquitectónica en Blender 5.2 (Cycles) con Python (bpy): la Terminal de Pasajeros del Aeropuerto de Uyuni, en Bolivia. No empieces de cero. Ya existen un modelo paramétrico verificado, una auditoría del DXF y del IFC, y decisiones confirmadas por el cliente.

Adjuntos:
1. UYUNI_paquete_traspaso_….zip:
   - el modelo paramétrico (01_blender/uyuni_modelo.py) y el .blend ya generado;
   - la auditoría (00_auditoria/);
   - las superposiciones del modelo con el CAD (01_blender/verificacion/) y el inventario de la escena;
   - la guía aeropuerto_uyuni/TRASPASO.md.
2. UYUNI_insumos_cliente.zip: el DXF, los IFC y los PDF originales del cliente.

Antes de proponer nada, lee completo aeropuerto_uyuni/TRASPASO.md. Si necesitas saber de dónde sale una medida, consulta 00_auditoria/AUDITORIA.md.

Reglas:
- No cambies las decisiones del cliente (sección 5 de TRASPASO.md) sin preguntarme. En particular:
  - el letrero "línea de horizonte" se mantiene, con pirámides facetadas en 3D y despegado 12 cm de la chapa;
  - hay dos propuestas de color (P1 "Patrimonio Ferroviario" con letrero corten, P2 "Salar & Litio" en blanco) y dos geometrías del letrero (A sobresale, B contenida): no elijas por el cliente;
  - el retenedor de nieve es un doble tubo de 1" de 18 cm de alto sobre la primera correa;
  - muros y columnas de revoque continuo, sin juntas; sin bolardos;
  - el hero shot es con luz de mañana.
- uyuni_modelo.py es la fuente de verdad:
  - todo cambio de geometría va en el script, con medidas numéricas tomadas del DXF;
  - el DXF solo sirve para verificar: no calques ni importes sus líneas como geometría.
- Mantén las coordenadas (las del IFC, en metros), el prefijo UY_ y las colecciones.
  - Las transformaciones DXF → modelo están en la sección 4 de TRASPASO.md.
  - Ojo: en el DXF, la FACHADA ESTE es el testero del eje 20 y la OESTE es la del eje 1.
- Todo tiene que poder regenerarse ejecutando el script en Blender 5.2. Al regenerar, el script borra lo que haya en sus colecciones; lee el aviso de la sección 7.
- Para cada asset externo (Poly Haven u otro), registra en 01_blender/assets/CREDITOS.md la fuente, el autor, la licencia y la URL. Las licencias deben permitir uso comercial.
- Si algo del CAD es ambiguo o contradice una decisión, pregúntame antes de suponer.
- Plazos: los renders vencen el domingo 4 de octubre y el video del dron el lunes 5. Prioriza lo que se ve en CAM_01 a CAM_04 y en el recorrido del dron.

Tareas, en este orden:
1. Revisa el modelo contra el DXF usando la tabla de la sección 6 de TRASPASO.md y las superposiciones de 01_blender/verificacion/.
   - Modela lo que falta en el testero del eje 20: puertas y vanos.
   - Ajusta el volumen saliente y el elemento vertical de la esquina del eje 1 / Lado Aire.
   - Detalla las carpinterías del Lado Aire (ME-4, ME-5 y ME-6).
   - No cambies la cumbrera (+13,02 contra +13,43): solo dime qué encuentras.
2. Contexto y paisaje de altiplano (sección 8.1): suelo con textura, paja brava, relieve suave y cerros en el horizonte, con el estilo sobrio de Mathias Klotz.
3. Reemplaza los 15 proxies por vehículos y personas reales (sección 8.2), con las posiciones de inventario_escena.json.
4. Cielo: mantén la luz de mañana sincronizada con el sol del script y agrega la variante de cielo nublado invernal (sección 8.3).
5. Deja lista la configuración de los renders finales y del video del dron (secciones 8.4 y 8.5), para que yo los renderice en mi PC con GPU:
   - renders en 4K;
   - video en 1080p, 24 fps, MP4 H.264.

Entrega:
- el uyuni_modelo.py actualizado y los assets nuevos, con su CREDITOS.md;
- una lista de cambios con el valor anterior y el nuevo de cada parámetro;
- capturas o renders de verificación de lo que cambiaste, en lo posible con el mismo encuadre que las superposiciones;
- lo que no pudiste resolver y por qué.
```
