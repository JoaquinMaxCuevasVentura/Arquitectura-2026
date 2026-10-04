# Cambios desde el primer traspaso (reunión del 3 de octubre)

Este documento sirve para **llevar estos cambios al modelo "formal"**: el `.blend` en el que otra IA venía avanzando (contexto, assets, ajustes) cuando se cortó su sesión.

- **Base:** versión del primer traspaso (commit `7b19bea`).
- **Versión nueva:** `01_blender/uyuni_modelo.py` de este paquete.
- **Diferencias línea por línea:** `CAMBIOS_REUNION_3OCT_uyuni_modelo.diff`, en esta misma carpeta.

## 1. Qué cambió

| Elemento | Antes (`7b19bea`) | Ahora | Dónde está en el script |
|---|---|---|---|
| Retenedor de nieve | Doble barra de Ø 34 mm a 0,40 m del borde, abrazaderas en cada nervio | **18 cm de alto, doble tubo de 1" (25,4 mm)**, abrazaderas cada 2 nervios (0,60 m), **sobre la primera correa** (supuesta a 0,30 m del borde) | `CORREA_1_DIST_BORDE`, `RETENEDOR`, `retenedor_nieve()` |
| Muros, columnas y vigas | Placas de Duralit 1,20 × 2,40 con juntas y tornillos; columnas y vigas de hormigón visto | **Revoque proyectado continuo** sobre panel EPS de 80 mm, sin juntas. Viga y columna en el mismo plano y tono que el muro. Solo hay **buñas finas** de 10 mm arriba y abajo de la viga (+5,51 y +6,01) | `mat_revoque()`, `PALETA["muro"]` |
| Bolardos | Uno por vano | **Eliminados** (no están en el presupuesto) | `entorno()` |
| Cielo del alero | Luxalon cerrado (lamas de 84 mm) | **Parrilla de listones** de 40 × 100 mm, perpendiculares a la fachada cada 0,15 m, sobre portantes y **plenum negro mate**. Luminarias lineales entre listones | `CIELO_LISTON`, `cielo_alero()`, `mat_cielo()` |
| Carpintería | Negra metálica | **Antracita mate** `#3A3E41` | `PERFIL_COLOR` |
| Letrero: relieve | Letras de 10 cm pegadas a 3 cm de los nervios | **Todo el conjunto despegado**: dorso a 12 cm de la chapa, letras de 8 cm. La sombra se separa de la pieza | `LETRERO_SEP`, `LETRERO_FONDO` |
| Letrero: montículos | Triángulos planos perforados | **Pirámides facetadas en 3D**: dos caras triangulares (sol y penumbra) y una arista que sobresale 15 cm (grandes) o 10 cm (chicas) en la base | `PIRAMIDE_FONDO`, `letrero_variante()` |
| Letrero: puerta de salida | — | **Juego de 3 pirámides sin texto** (grande + 2 chicas) sobre la ME-2 izquierda, con tramo de horizonte de X 13,30 a 20,30 y reflejos | `LETRERO_SALIDA` |
| Letrero: geometría | Una sola (sobresale) | **A sobresale** (como el CAD) y **B contenida** en los 2,40 m (escala 72 %), en dos colecciones | `variantes_letrero()`, `LETRERO_B_MARGEN` |
| Letrero: material | Blanco | **Blanco o corten**, según la propiedad `letras_corten` | `mat_letrero()`, `color_corten()` |
| Colores | Una paleta (chocolate, crema, corten) | **Dos propuestas**: P1 "Patrimonio Ferroviario" y P2 "Salar & Litio" (sección 5, punto 11 de `TRASPASO.md`), según la propiedad `propuesta` | `PALETA`, `mat_propuesta()`, `PROPIEDADES_ESCENA` |
| Escenas | `UYUNI_DIA`, `UYUNI_CREPUSCULO` | Más **`UYUNI_DIA_P2_SALAR_LITIO`** (misma mañana, paleta P2) | `escena_propuesta_2()` |
| Cámaras | CAM_01 a CAM_06 y dron | Más **`CAM_07_PROPUESTAS`** (perspectiva del cliente mejorada) y **`CAM_07B_CAPTURA_CLIENTE`** (la captura tal cual) | `camaras_propuestas()` |
| Cielo | Aire 1,0 · aerosoles 0,08 · ozono 1,2 | Aire 0,9 · aerosoles 0,02 · ozono 3,0: azul más profundo | `CIELO_ATMOSFERA` |
| Nieve del crepúsculo | Hasta 0,40 m del borde | Hasta el nuevo retenedor (0,30 m) | `nieve_crepusculo()` |

**Otros entregables desde el primer traspaso** (no tocan el modelo):
- `02_postproduccion/PROMPTS_IA_RENDERS.md`: prompts de postproducción con IA por cámara.
- `02_postproduccion/unificar_color.py`, con `.bat` y guía: unifica el color de las imágenes hechas con IA.
- `02_postproduccion/PROMPT_UPSCALE_PROPUESTAS.md`: prompts y ajustes para escalar ×2 los renders de las propuestas.
- `01_blender/herramientas/render_propuestas.py`: renderiza las propuestas y las geometrías del letrero.
- `01_blender/propuestas/`: hojas comparativas de las dos propuestas y del letrero.

## 2. Cómo pasarlos al modelo formal

### A) Script de cambios puntuales (recomendado)

`01_blender/herramientas/aplicar_cambios_reunion.py` aplica **solo** estos cambios sobre el `.blend` abierto:
- **No regenera** el modelo.
- **No toca** objetos, colecciones ni materiales ajenos a la lista de la sección 3.
- **No purga** datos huérfanos.
- Se puede ejecutar más de una vez.

1. Haz una copia del `.blend` formal.
2. Abre la copia en Blender 5.2. `uyuni_modelo.py` (la versión nueva) debe estar en la carpeta de arriba del script, o escribe su ruta en la variable `MODELO`.
3. Ejecuta el script de una de estas formas:
   - **En Blender:** *Scripting > Open > `aplicar_cambios_reunion.py` > Run Script*. Luego guarda.
   - **Vía MCP:** `exec(open(p, encoding="utf-8").read(), {"__file__": p, "__name__": "__main__"})`.
   - **Sin interfaz:** `python aplicar_cambios_reunion.py -- formal.blend formal_actualizado.blend`.
4. Lee el informe que imprime (líneas `[CAMBIOS 3 OCT]`) y revisa `CAM_07_PROPUESTAS` en las escenas `UYUNI_DIA` (P1) y `UYUNI_DIA_P2_SALAR_LITIO` (P2).

Detalles a tener en cuenta:
- **Escena P2:** si el formal tiene colecciones propias (contexto, assets) en `UYUNI_DIA`, el script también las enlaza a la escena nueva.
- **Materiales:** se reemplazan en todos los objetos que los usan. Por eso un objeto que la otra IA duplicó de un muro también pasa a revoque.
- **Mundo:** si la otra IA puso un HDRI, el script no lo toca. Solo ajusta el cielo procedural del script.
- **Cubierta modificada:** el retenedor se reconstruye con la geometría del script. Si la otra IA cambió la cubierta (por ejemplo, la cumbrera a +13,43), revisa que el retenedor siga apoyado en la chapa.

**Cómo se probó:**
1. Se generó un `.blend` con la versión del primer traspaso.
2. Se le agregó un "avance" simulado: una colección de contexto, un asset en `07_ASSETS` y un muro duplicado.
3. Se aplicó el script.

Resultado: los 185 objetos del modelo y las 3 escenas quedaron **idénticos** a los del script nuevo (geometría, materiales, cámaras y propiedades), y el avance simulado se conservó.

### B) Regenerar con el script nuevo

Solo sirve si el formal no tiene nada propio dentro de las colecciones del script. `limpiar()` borra todo lo que haya en `_REF_CAD` a `08_CAMERAS_LIGHTS`, **incluidas `06_ENTORNO_SITE` y `07_ASSETS`**, y purga los huérfanos. Lo que esté en colecciones propias se conserva, pero hay que volver a enlazarlo en las escenas (ver la sección 7 de `TRASPASO.md`).

### C) Portar a mano

Esta opción es para el caso en que la otra IA editó su propia copia de `uyuni_modelo.py`. Usa el `.diff` y porta, en este orden:
1. Parámetros: `PALETA`, `PERFIL_COLOR`, `CIELO_ATMOSFERA`, `CIELO_LISTON`, `LETRERO_*`, `PIRAMIDE_FONDO`, `CORREA_1_DIST_BORDE` y `RETENEDOR`.
2. Materiales: `mat_propuesta`, `mat_revoque`, `color_corten`, `mat_celosia`, `mat_cielo`, `mat_letrero` y las claves nuevas de `crear_materiales`.
3. Geometría: `cielo_alero`, `retenedor_nieve`, `variantes_letrero`, `letrero`, `letrero_variante` y `dentro_poligono`; y en `entorno`, borrar los bolardos.
4. Escenas: `camaras_propuestas`, `camara(shift_y)`, `geometria_letrero`, `PROPIEDADES_ESCENA`, `propiedades_escena`, `escena_propuesta_2`, `nieve_crepusculo` y los cambios en `construir` y `limpiar`.
5. La guarda final `if __name__ == "__main__": construir()`.

## 3. Nombres que cambian (para buscarlos en el formal)

| Antes | Ahora |
|---|---|
| Material `UY_DURALIT_FIBROCEMENTO` | `UY_REVOQUE_FACHADA_BUNAS` en los paños `UY_MURO_NE_*`; `UY_REVOQUE_CONTINUO` en el resto (testeros, Lado Aire, anexo, volumen saliente) |
| Material `UY_HORMIGON_VISTO` en columnas y vigas | `UY_REVOQUE_CONTINUO` (columnas) y `UY_REVOQUE_FACHADA_BUNAS` (vigas). El hormigón visto queda en zanja, bordillo y escalones |
| Material `UY_CHAPA_CAFE_CHOCOLATE_ACERGAL` | `UY_CHAPA_CUBIERTA` (cubierta, nervios, anexo) y `UY_CHAPA_ANTEPECHO_REMATES` (antepecho, sus nervios, goterón, franja ESTE) |
| Material `UY_CORTEN_OXIDADO` | `UY_CELOSIA_CORTEN_O_BLANCA` |
| Material `UY_ALUMINIO_ANODIZADO_NEGRO_MATE` | `UY_ALUMINIO_ANTRACITA_MATE` |
| Material `UY_BASTIDOR_ACERO_NEGRO` | `UY_BASTIDOR_CELOSIAS` |
| Material `UY_LETRERO_BLANCO` | `UY_LETRERO_BLANCO_O_CORTEN` (también lo usa el rombo OESTE) |
| Material `UY_PLENUM_NEGRO` | `UY_PLENUM_NEGRO_MATE` |
| Material `UY_LUXALON_ALUMINIO_CHAMPAGNE` | `UY_CIELO_LISTONES` |
| `UY_BOLARDOS` y su material `UY_BOLARDO_ACERO_GRAFITO` | eliminados |
| `UY_CIELO_PLENUM`, `UY_CIELO_LUXALON_LAMAS` | `UY_CIELO_PLENUM_NEGRO`, `UY_CIELO_LISTONES` (Array cada 0,15) |
| `UY_LUMINARIAS_ALERO` (cajas de 18 cm) | `UY_LUMINARIAS_ALERO` (lineales de 1,20 m entre listones) |
| `UY_RETENEDOR_ABRAZADERAS`, `UY_RETENEDOR_BARRAS_TUBULARES` | `UY_RETENEDOR_ABRAZADERAS` (placa de 18 cm, Array cada 0,60) y `UY_RETENEDOR_TUBOS_1PULG` |
| Colección `LETRERO_HORIZONTE_UYUNI` con 6 objetos (letras, reflejo, montículos perforados, reflejo de montículos, horizonte, separadores) | Las mismas piezas en las subcolecciones `LETRERO_A_SOBRESALE` y `LETRERO_B_CONTENIDO`, con sufijo `_A` o `_B`. Los montículos pasan a `UY_LETRERO_PIRAMIDES_SAL_3D_*` |

## 4. Supuestos que conviene confirmar

1. **Primera correa a 0,30 m del borde libre.** El IFC no trae la estructura metálica. Si cambia, ajusta `CORREA_1_DIST_BORDE`.
2. **Detalles de color que no se pidieron expresamente:**
   - cubierta antracita en P1 y gris claro metálico en P2;
   - cielo símil madera en P1;
   - bastidor de celosías del color del muro en P2;
   - rombo OESTE con el material del letrero.
3. **Letrero B:** se resolvió **reescalando** al 72 %, con letras de 1,08 m. La alternativa "cortar" (mantener 1,50 m y recortar el reflejo en el borde inferior del parapeto) no está modelada.
4. **El texto sigue en la posición del CAD,** sobre el ingreso principal. No se centró exactamente en la puerta: el centro de UYUNI queda a 0,5 m del eje de la ME-2.
