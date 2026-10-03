# Traspaso: visualización de la Terminal de Pasajeros del Aeropuerto de Uyuni

**Fecha:** 3 de octubre de 2026 · **Blender:** 5.2.2 LTS, Cycles · **Rama del repositorio:** `claude/clever-hypatia-i19958`

Esta guía permite que otra persona o IA continúe el proyecto sin repetir la auditoría. Antes de tocar el modelo, lee las secciones 1 a 6. Para saber de dónde sale cada medida, ve a `00_auditoria/AUDITORIA.md`.

**Plazos del brief:**
- Renders fijos (fase 5): sábado 3 o domingo 4 de octubre.
- Video del dron (fase 6): lunes 5 de octubre.
- Presentación: reunión de 15 minutos con el Ministro.

---

## 1. Estado por fase

| Fase | Qué pide el brief | Estado |
|---|---|---|
| 0 y 0.5 | Auditoría del DXF y del IFC, y triage de vistas | ✅ Terminada (`00_auditoria/`). |
| 1 | Suprimir lo obsoleto, dinteles rectos a +5,51, mampara M1 y antepecho de 2,40 m | ✅ El modelo se hizo desde cero: lo obsoleto, simplemente, no se modeló. |
| 2 | Cubierta engrapada, retenedores de nieve, goterón sin canaleta, zanja y cielo del alero | ✅ Revisado el 3 de octubre: retenedor fino y cielo listonado (sección 5). |
| 3 | Celosías corten (módulos de 5 × 6 m con planchas de 1 × 2 m) y letrero UYUNI | ✅ 11 módulos y letrero "línea de horizonte". |
| Materiales | PBR | ✅ Procedurales, sin texturas de imagen. |
| 4 | Entorno, vehículos, personas, clima y cielo | ⚠️ **Parcial.** Faltan tres cosas: 1) el paisaje (horizonte, cerros, suelo con textura y vegetación); 2) reemplazar los vehículos y las personas, que hoy son cajas de ubicación que no salen en el render; 3) la variante de cielo nublado. El entorno inmediato ya está: acera, zanja, calzada, estacionamiento y plataforma (los bolardos se quitaron el 3 de octubre). |
| 5 | Cámaras CAM_01 a CAM_04 y renders | ⚠️ Las cámaras están listas (se sumaron CAM_02B, CAM_05, CAM_06 y CAM_07). Las dos propuestas de CAM_07 y los primeros planos del letrero ya se renderizaron en la nube (CPU). **Faltan los renders finales de CAM_01 a CAM_06 con GPU.** |
| 6 | Dron de 20–30 s, 24 fps, 1080p, MP4 H.264 | ⚠️ La trayectoria está lista (`CAM_DRON`, 600 cuadros = 25 s). Faltan la configuración de salida y el render. |
| 7 | Ficha de costos para el Ministro, láminas PDF, MP4 y facturación | ❌ Pendiente (sección 8.6). |

## 2. Contenido del paquete

El paquete (`UYUNI_paquete_traspaso_….zip`) es el repositorio completo:

```
aeropuerto_uyuni/
├── README.md                    uso rápido (escenas, render, parámetros clave)
├── TRASPASO.md                  esta guía
├── CAMBIOS_REUNION_3OCT.md      cambios desde el primer traspaso y cómo llevarlos a un .blend con avance propio
├── PROMPT_CONTINUACION.md       instrucción lista para pegar en otra IA
├── 00_auditoria/
│   ├── AUDITORIA.md             hallazgos, cotas verificadas y decisiones del cliente
│   ├── dxf_audit_report.json    capas, bloques, textos clave y cotas del DXF
│   ├── ifc_audit_report.json    georreferencia, niveles, ejes y estructura del IFC
│   ├── comparativa_original_vs_actual.png
│   ├── vistas/                  16 vistas del DXF aisladas: PNG + DXF limpio + vistas_index.json
│   └── scripts/auditoria_uyuni.py
└── 01_blender/
    ├── uyuni_modelo.py          FUENTE DE VERDAD: genera todo el modelo
    ├── uyuni_v2.blend           el modelo ya generado (escenas UYUNI_DIA, UYUNI_DIA_P2_SALAR_LITIO y UYUNI_CREPUSCULO)
    ├── inventario_escena.json   escenas, colecciones, objetos (con caja envolvente), cámaras, luces, materiales y proxies
    ├── previews/                vistas previas de CAM_01 a CAM_06 (1280 px, 24 muestras)
    ├── verificacion/            modelo superpuesto al CAD: 4 alzados y 2 cortes
    ├── propuestas/              hojas comparativas: dos propuestas de color y letrero (material y geometría)
    └── herramientas/            scripts sin interfaz: construir, renderizar (también las propuestas), verificar,
                                 inventariar y aplicar_cambios_reunion.py (cambios del 3 de octubre sobre un .blend existente)
02_postproduccion/               prompts de IA por vista, prompts de upscale y unificar_color.py (revelado de serie)
reports/                         estudio de costos de renders (proyecto Tupiza): referencia para la fase 7.3
research_notes/                  notas de mercado y costos de renders en Bolivia
```

Los archivos originales del cliente (DXF, IFC y PDF) **no están en el repositorio**, porque es público. Van aparte, en `UYUNI_insumos_cliente.zip`:

| Archivo | Contenido |
|---|---|
| `tp-arq-x-cad-FachadaEste-01.dxf` (30 MB) | Pese al nombre: 4 fachadas, 3 cortes, fichas ME-1 a ME-6, paneles PT1/PT2 y letrero. |
| `AU-SUP-EST-TP-ZZ-MO-TerminalPasajeros.ifc` | Estructura de HºAº exportada con *parts*: las columnas no traen geometría. |
| `AU-CBI-ARQ-TP-ZZ-MO-TerminalPasajeros_detached-AU-SUP-EST-…ifc` | Mismo modelo estructural sin *parts*. Es el que se usó para la geometría. **No es la arquitectura.** |
| `…_detached.pdf` y `…_detached_a.pdf` | Planta Baja y Planta Alta (acabados de piso, ejes 1–20 y A–R). |

## 3. Coordenadas, georreferencia y sol

**Sistema del modelo:** son las coordenadas locales del IFC, en metros.
- **X:** ejes 1 → 20; el eje 1 está en X = 0 y el eje 20 en X = 82,51.
- **Y:** ejes A → R; el eje A está en Y = 0,192 y el Lado Tierra queda hacia −Y.
- **Z:** metros sobre el NPT ±0,00, que equivale al nivel IFC 0P (3666,593 m s.n.m.).

**Georreferencia:**
- Sistema: EPSG:32719 (UTM 19S).
- Origen: E 724 956,439 / N 7 737 860,959.
- Rotación del X local: 148,2058°, antihorario desde el Este.
- Latitud/longitud: −20,4461546 / −66,8497209.
- Norte verdadero en coordenadas locales: **301,043°**, antihorario desde +X. Hay una flecha `NORTE_VERDADERO` en la escena.

**Orientación de cada fachada** (azimut verdadero de su normal):

| Fachada | Normal local | Azimut | Nombre en el DXF |
|---|---|---|---|
| Lado Tierra (eje A, principal) | −Y | 31° (NNE) | FACHADA NORESTE |
| Lado Aire (eje R, pista) | +Y | 211° | FACHADA SUROESTE |
| Testero del eje 1 | −X | 121° (ESE) | **FACHADA OESTE** |
| Testero del eje 20 | +X | 301° (ONO) | **FACHADA ESTE** |

⚠️ **Los nombres de los laterales en el DXF no coinciden con la orientación real.** Por su contenido, el alzado "ESTE" es el testero del eje 20 y el "OESTE" es el del eje 1. El modelo y los documentos usan los nombres del DXF. El sol, en cambio, sigue la orientación real.

**Sol** (algoritmo NOAA, en `sol_posicion()`):

| Escena | Fecha y hora local (UTC−4) | Azimut / elevación | Vector hacia el sol (X, Y, Z locales) |
|---|---|---|---|
| `UYUNI_DIA` | 4 de octubre de 2026, 09:30 | 73,6° / 46,5° | (−0,466; −0,507; 0,725) |
| `UYUNI_CREPUSCULO` | 4 de octubre de 2026, 18:39 | 264,0° / −3,9° | (0,796; 0,601; −0,068) |

Por la mañana el sol da de frente sobre la fachada principal y las celosías proyectan su sombra. Al atardecer, en cambio, la fachada queda a contraluz. Si se cambia el cielo por un HDRI, hay que rotarlo para que su sol quede en la dirección de esa tabla.

**Niveles** (m sobre NPT): C −1,50 · 0P 0,00 · 1P +3,85 · 2P +7,10 · 3P +7,60 · 4P +9,00 · 5P +11,50.

## 4. Cómo comparar con el DXF

- El *model space* del DXF está en **metros a escala 1:1**: las cotas tienen `DIMLFAC = 1000` y por eso muestran mm.
- Hay dos versiones del Lado Tierra en el mismo archivo:
  - **Fila superior (y ≈ 36…62): diseño ORIGINAL.** No sirve para modelar.
  - **Fila inferior (y ≈ −6…20): diseño ACTUAL.**
- Los DXF limpios de `00_auditoria/vistas/` conservan las coordenadas del original.

| Vista (`00_auditoria/vistas/`) | Qué es | DXF → modelo | Se mira desde |
|---|---|---|---|
| `FACHADA_NORESTE_ACTUAL` | Lado Tierra | X = x · Z = y | −Y |
| `FACHADA_SUROESTE` | Lado Aire | X = 187,84 − x · Z = y | +Y |
| `FACHADA_ESTE` | testero del eje 20 | Y = −0,308 + (x − 249,787) · Z = y | +X |
| `FACHADA_OESTE` | testero del eje 1 | Y = −0,308 + (384,834 − x) · Z = y | −X |
| `CORTE_ACTUAL_POR_M1` | corte por una ME-1 | Y = −41,147 − x · Z = y | +X |
| `CORTE_ACTUAL_MURO_CIEGO` | corte por paño ciego | Y = −24,125 − x · Z = y | +X |
| `CORTE_ORIGINAL_B-K-A`, `FACHADA_NORESTE_ORIGINAL` | diseño anterior | Y = −15,193 − x (corte) o X = x (fachada) · Z = y − 42,914 | — |
| `ME1`…`ME6`, `PT1_PT2`, `PANELES_LETRAS_PIRAMIDES` | fichas de detalle 1:1 | coordenadas propias: se mide dentro de cada ficha | — |

**Superposiciones** (`01_blender/verificacion/`):
- Cada `SUPERPOSICION_<vista>.jpg` es un render ortogonal del modelo con el CAD encima, en rojo, con el mismo encuadre y la misma escala que el PNG de la vista.
- Las láminas `lamina_verificacion_alzados.jpg` y `lamina_verificacion_cortes.jpg` las resumen.
- Se regeneran con `herramientas/verificar_alzados.py` y `herramientas/superponer_cad.py` (sección 9).
- **Es la forma más rápida de ver qué falta o qué no encaja.**

## 5. Decisiones del cliente (no cambiar sin consultarle)

1. **Letrero "línea de horizonte": se mantiene.** Es un concepto, no la "estructura anamórfica" que el brief pedía eliminar (esa no aparece en los archivos recibidos).
   - Lleva montículos de sal y letras UYUNI sobre una línea de horizonte a +7,764, con su reflejo debajo (marcos y letras en contorno).
   - La modulación sale del CAD: 1446 · 2000 · 1000 · 2717 · 3×1000 · 1184 · 5576 · 5952 · 2000 · 6401 · 308. El texto queda solo sobre el ingreso principal (ME-2 de X 53,49–57,77).
   - **Reunión del 3 de octubre:**
     - **Montículos:** pasan a ser **pirámides facetadas en 3D**, ya no chapas planas perforadas. Tienen dos caras triangulares unidas por una arista que baja del vértice al centro de la base, donde sobresale 15 cm en las grandes y 10 cm en las chicas. El sol ilumina una cara y deja la otra en penumbra.
     - **Despegue:** todo el conjunto (letras, pirámides y horizonte) **flota despegado de la chapa** sobre pernos ocultos. El dorso queda a 12 cm de la chapa y las letras tienen 8 cm de espesor, así la sombra se separa de la pieza.
     - **Juego sobre la puerta de salida:** sobre la ME-2 izquierda (centro X 16,80) se suma un **juego asimétrico de 3 pirámides sin texto** (grande + 2 chicas) con su tramo de horizonte (X 13,30–20,30) y sus reflejos.
     - **Material:** blanco o **acero corten**, según la propiedad `letras_corten` de la escena. P1 lleva corten sobre parapeto antracita; P2, blanco.
2. **Geometría de las letras: hay dos versiones para probar**, en colecciones hermanas dentro de `LETRERO_HORIZONTE_UYUNI`:
   - **A `LETRERO_A_SOBRESALE`:** como en el CAD. Las letras suben 0,25 m por encima del antepecho (+9,264) y el reflejo baja 0,35 m por debajo (+6,264).
   - **B `LETRERO_B_CONTENIDO`:** queda dentro de los 2,40 m del antepecho. El horizonte va al centro (+7,812) y cada pieza se reescala al 72 % sobre su eje, con 12 cm libres arriba y abajo (`LETRERO_B_MARGEN`).
   - Por defecto se ve la A. Para ver la B, excluye la colección A y activa la B en la capa de vista, o usa `herramientas/render_propuestas.py` con las variantes `P1B` y `P2B`.
3. **Celosías:** 2 en la OESTE, 2 en la ESTE, 5 PT2 en el Lado Tierra y 2 PT2 en el Lado Aire. Las posiciones y variantes exactas están en `CELOSIAS`.
4. **En los detalles PT1/PT2, las tramas grises son vacíos (calados)** y las líneas salmón son el bastidor que sostiene las planchas por detrás.
5. **Retenedor de nieve (revisado el 3 de octubre):**
   - **18 cm de alto** sobre la chapa;
   - **doble tubo delgado de 1"** (25,4 mm);
   - abrazaderas sobre un nervio de cada dos (cada 0,60 m);
   - **fijado sobre la primera correa**. La correa no está en el IFC: se supone a 0,30 m del borde libre (`CORREA_1_DIST_BORDE`, punto abierto 11).
6. **Hero shot (CAM_01): luz de mañana**, con el sol sobre la fachada y las sombras de las planchas corten.
7. **Materiales (revisados el 3 de octubre):**
   - **Muros y columnas:** panel EPS de 80 mm con malla y **revoque proyectado continuo**, sin placas ni juntas verticales. Viga y columna van revocadas en el mismo plano y tono que el muro. Solo hay una **buña horizontal fina** (10 mm) arriba y abajo de la viga de +5,51 a +6,01. Hacen de fondo neutro.
   - **Carpintería de aluminio:** antracita mate `#3A3E41`, no negro brillante.
   - **Cielo falso del alero:** **parrilla de listones** de 40 × 100 mm, perpendiculares a la fachada cada 0,15 m (antecedente del Rectorado), sobre perfiles portantes y un **plenum negro mate** que oculta el interior del alero. Las luminarias son lineales, entre listones.
   - **Sin bolardos ni postes de iluminación peatonal:** no están en el presupuesto.
   - **Colores:** dependen de la propuesta (punto 11).
   - **Hora azul:** bañadores cálidos al pie de las celosías y nieve en el borde de la cubierta.
8. **Elementos de los laterales (aprobados):**
   - en la OESTE: rombo perforado, bloque con mástil y volumen saliente;
   - en la ESTE: franja nervada de +4,41 a +6,21.
9. **Colecciones:** se usa la lista de la Tarea 0.2 del brief, de `_REF_CAD` a `08_CAMERAS_LIGHTS`.
11. **Dos propuestas de color para la gerencia (reunión del 3 de octubre).** Las elige la propiedad `propuesta` de la escena: 0 es P1 (escena `UYUNI_DIA`) y 1 es P2 (escena `UYUNI_DIA_P2_SALAR_LITIO`). Los colores están en `PALETA`.

    | Elemento | P1 "Patrimonio Ferroviario" | P2 "Salar & Litio" |
    |---|---|---|
    | Celosías | Acero corten, óxido cobrizo cálido | Blanco perla |
    | Parapeto y remates | Antracita mate | Blanco perla |
    | Letrero y pirámides | **Corten** (`letras_corten` = 1) | Blanco, con sombras por relieve |
    | Cubierta | Antracita | Gris claro metálico |
    | Cielo listonado | Símil madera | Blanco |
    | Muros y columnas | Hormigón claro `#B9B5AD` | Gris neutro `#6B6E70` |
    | Carpintería | Antracita mate | Antracita mate |

    El color de la cubierta, la madera del cielo en P1 y el bastidor de las celosías (color del muro en P2) no se pidieron expresamente: son propuestas mías y conviene confirmarlas.

    La vista para la gerencia es `CAM_07_PROPUESTAS`. Parte de la perspectiva de la captura del cliente, que está guardada tal cual como `CAM_07B_CAPTURA_CLIENTE`, mejorada así: fachada completa con márgenes, 28 mm desde 6,0 m de altura y verticales rectas.
10. **Reglas de oro del brief:**
    - el DXF solo sirve para verificar: no se calca ni se importa como geometría;
    - toda la geometría se genera con `bpy` a partir de medidas numéricas;
    - ningún objeto queda suelto en la colección raíz;
    - después de cada iteración se purgan los datos huérfanos.

## 6. Supuestos y puntos abiertos: qué revisar contra el DXF

Están ordenados de mayor a menor impacto en los renders.

| # | Tema | Cómo está hoy | Qué revisar | Parámetro o función |
|---|---|---|---|---|
| 1 | **Testero del eje 20 (FACHADA ESTE)** | Solo tiene celosías, 2 ME-3 y la franja nervada. | El CAD dibuja además 2 puertas dobles detrás de las PT2, 1 puerta doble con sobreluz, 2 vanos grandes tipo portón y 2 elementos menores. **No están modelados.** Se ven en el final del dron y en vistas oblicuas. Mira `SUPERPOSICION_FACHADA_ESTE.jpg`. | `envolvente_general()` |
| 2 | **Cumbrera** | +13,02, según los alzados laterales. | Las fachadas NE y SO marcan +13,43. La diferencia se ve en las superposiciones NE y SO: la banda nervada del CAD queda más alta que la del modelo. **Confirmar con el cliente antes de cambiarla.** | `CUMBRERA_Z` (mueve solo el vértice de la cumbrera de `PERFIL_CUBIERTA`) |
| 3 | **Volumen saliente del Lado Aire (esquina del eje 1)** | Se modeló en X 0,3–2,8, Y 48,47–50,51 y Z 3,45–6,15. La X es un supuesto. | El alzado SO dibuja en esa posición un rectángulo enmarcado en **X 0,804–2,804 y Z 3,82–6,12**, con marco de 40 mm y travesaño a +5,90. Si es el mismo elemento, hay que ajustar la X y agregar esa carpintería. | `CAJA_OESTE`, `PLATAFORMA_OESTE` |
| 4 | **Elemento vertical en la esquina del eje 1 / Lado Aire** | No está modelado. | Los alzados SO y OESTE muestran un elemento vertical con travesaños a distintas alturas, en X ≈ −0,36…−0,10. Puede ser una escalera de gato o una bajante con abrazaderas. | nuevo, en `elementos_laterales()` |
| 5 | **Mástil OESTE** | X = 0,6. Es un supuesto, porque el alzado no da su posición en X. | Se puede confirmar con el alzado SO. | `MASTIL_OESTE` |
| 6 | **Lado Aire** | Las ventanas ME-4, ME-5 y ME-6 son vanos simples aproximados desde el alzado SO. | El CAD trae el despiece de las carpinterías, las puertas menores y la ubicación exacta de cada ME. Las fichas ME4, ME5 y ME6 están en `vistas/`. | `VENTANAS_AIRE`, `envolvente_general()` |
| 7 | **Rombo perforado OESTE** | Usa el material del letrero: corten en P1 y blanco en P2. | Confirmar con el cliente. | `elementos_laterales()` |
| 8 | **Entorno** | El corte da la acera de 4,00 m, el bordillo de 0,15 m y la zanja de 0,50 × 0,20 m. La calzada, el estacionamiento y la plataforma del Lado Aire son supuestos. | No hay planta de emplazamiento en los archivos recibidos. Si el cliente la tiene, conviene pedirla. | `entorno()`, `CALZADA_Y` |
| 9 | **Cerchas de la cubierta** | No están modeladas, porque no se ven desde afuera. | Los cortes las dibujan. Son opcionales. | — |
| 10 | **Interiores** | Una caja emisiva cálida, según el brief: "interiores básicos". | — | `envolvente_general()` |
| 11 | **Primera correa de la cubierta** | El retenedor de nieve se fija sobre ella; se supuso a 0,30 m del borde libre. | Ubicarla en el plano de la estructura metálica. | `CORREA_1_DIST_BORDE` |

**Ya resueltos (no hace falta volver a revisarlos):**
- Termopanel: 26,8 mm según el CAD (4+4 / 12 / 3+3). El brief decía 21 mm por error de suma.
- Ejes del DXF contra los del IFC: hay diferencias de 2 a 7 cm (eje 12 del DXF contra el 11′ del IFC, y eje 17). Se usan los del IFC.
- Columnas del anexo (ejes 18–20): sobresalían ≈ 1 m por encima de su cubierta y se veían en el hero shot. Se corrigió el 3 de octubre y ahora terminan en ella.

**Diferencias dentro del propio CAD (no copiarlas al modelo):**
- **Alero en los laterales:** los alzados ESTE y OESTE no dibujan el volado de 2 m ni el antepecho en el extremo del Lado Tierra. Cortan la cubierta en Y ≈ −0,26, a ≈ +8,9. Los cortes vigentes y la fachada NE sí los dibujan. El modelo sigue los cortes, por eso en las superposiciones laterales el antepecho sobresale del contorno rojo.
- **Diseño original:** la fila superior del DXF (doble pantalla, canaleta, vidrio en el eje K) es el diseño descartado.
- **Retenedor:** el CAD lo ubica a ≈ 1,35 m del borde; manda la decisión del cliente (0,40 m).

## 7. Cómo está hecho el modelo

**`01_blender/uyuni_modelo.py` es la fuente de verdad.** El `.blend` se regenera desde ahí. El script tiene seis bloques:
1. **Parámetros:** todas las cotas.
2. **Utilidades:** `Malla`, para cajas y prismas con bmesh, y `placa_con_huecos`.
3. **Materiales:** la clase `Nodos`, un ayudante de nodos.
4. **Geometría.**
5. **Luz, cielo y cámaras.**
6. **`construir()`.**

| Función | Colección | Objetos principales |
|---|---|---|
| `estructura` | `01_ESTRUCTURA` | `UY_COLUMNAS_EJE_A` (0,40 × 1,00) y `UY_VIGAS_DINTEL_300x500` |
| `muro_landside`, `mamparas` | `02_ENVOLVENTE`, `03_CARPINTERIAS_M1` | paños `UY_MURO_NE_*` (revoque con buñas) y `UY_MAMPARA_M1_FRAMES/GLASS/SELLOS` (7 ME-1 y 2 ME-2) |
| `antepecho_alero` | `02_ENVOLVENTE` | `UY_ANTEPECHO_2_40_CHAPA`, `UY_ANTEPECHO_NERVIOS` (Array cada 0,30), `UY_CIELO_LISTONES` (Array cada 0,15), `UY_CIELO_PLENUM_NEGRO`, `UY_LUMINARIAS_ALERO` |
| `cubierta` | `04_CUBIERTA_INDUSTRIAL` | `UY_CUBIERTA_CHAPA`, `UY_CUBIERTA_NERVIOS_*`, `UY_RETENEDOR_*`, `UY_GOTERON_BORDE`, `UY_CUBIERTA_ANEXO` |
| `envolvente_general` | `02_ENVOLVENTE`, `03_CARPINTERIAS_M1` | testeros, fachadas del Lado Aire, anexo, ME-3 e interior |
| `elementos_laterales` | `02_ENVOLVENTE` | `UY_ROMBO_OESTE_*`, `UY_MASTIL_OESTE`, `UY_DESCANSO_ESCALONES_OESTE`, `UY_FRANJA_ESTE_*` |
| `celosias` | `05_CELOSIAS_CORTEN` | `UY_CELOSIA_<fachada>_<variante>_<n>` y `UY_CELOSIAS_BASTIDOR` |
| `letrero` | `02_ENVOLVENTE/LETRERO_HORIZONTE_UYUNI/LETRERO_A_SOBRESALE` y `.../LETRERO_B_CONTENIDO` | letras, reflejo, pirámides 3D, marcos, separadores y líneas de horizonte (sufijo `_A` o `_B`) |
| `entorno` | `06_ENTORNO_SITE` | acera, zanja con rejilla, bordillo, calzada, estacionamiento, plataforma y `UY_SUELO_ALTIPLANO` (plano de 4 × 4 km) |
| `assets` | `07_ASSETS/PROXIES_COLOCACION` | 15 cajas de ubicación, ocultas en el render (ver 8.2) |
| `referencias_cad` | `_REF_CAD/*` | las vistas del CAD como planos de referencia, ocultos en el render |
| `camaras_y_dron` | `08_CAMERAS_LIGHTS` | 9 cámaras fijas (con `CAM_07_PROPUESTAS` y `CAM_07B_CAPTURA_CLIENTE`), `CAM_DRON` con su objetivo `DRON_OBJETIVO` y `NORTE_VERDADERO` |

- **`DATOS_GEOM`:** es un JSON incrustado con los contornos de las planchas PT1, PT2A, PT2B y PT2R, las letras UYUNI y el letrero. Se extrajeron de las tramas del DXF y ya restan los calados. Son datos: no hace falta tocarlos.
- **Tres escenas, mismas colecciones:**
  - `UYUNI_DIA` (propuesta 1) agrega `08_LUZ_DIA`.
  - `UYUNI_DIA_P2_SALAR_LITIO` (propuesta 2) comparte `08_LUZ_DIA` y el cielo de la mañana.
  - `UYUNI_CREPUSCULO` agrega `08_LUZ_CREPUSCULO` (luna, spots bajo el alero y bañadores de las celosías) y `09_NIEVE_CREPUSCULO`.
- **Propiedades de escena que leen los materiales** (nodo Attribute, tipo *View Layer*):

  | Propiedad | Material que la lee | Día | Hora azul |
  |---|---|---|---|
  | `humedad` | asfalto y acera mojados | 0 | 1 |
  | `nieve` | nieve en el suelo | 0 | 0,6 |
  | `luz_interior` | interior encendido | 0,6 | 7 |
  | `luz_alero` | luminarias del alero | 0 | 1 |
  | `luz_letrero` | letrero encendido (solo si es blanco) | 0 | 2,5 |
  | `propuesta` | cubierta, parapeto, muros, cielo, celosías y bastidor (`PALETA`) | 0 en `UYUNI_DIA`, 1 en `UYUNI_DIA_P2_SALAR_LITIO` | 0 |
  | `letras_corten` | letrero, pirámides y rombo OESTE: 1 corten, 0 blanco | 1 en P1, 0 en P2 | 0 |

  Cambiarlas en *Scene Properties > Custom Properties* modifica el aspecto sin tocar los materiales.
- **Nombres:** objetos, mallas, materiales y mundos llevan el prefijo `UY_`. Unidades en metros, escala 1,0.

> ⚠️ **Al volver a ejecutar el script, `limpiar()` borra todo lo que haya en sus colecciones** (`_REF_CAD` a `08_CAMERAS_LIGHTS`, más las de luz y nieve), elimina y recrea las escenas `UYUNI_CREPUSCULO` y `UYUNI_DIA_P2_SALAR_LITIO` y purga los datos huérfanos.
> - Para llevar los cambios del 3 de octubre a un `.blend` que ya tiene avance propio, **no hace falta regenerarlo**: usa `herramientas/aplicar_cambios_reunion.py` (ver `CAMBIOS_REUNION_3OCT.md`).
> - Cualquier cosa que se agregue **a mano** dentro de esas colecciones (por ejemplo, assets en `07_ASSETS`) se pierde.
> - Opción recomendada: agregar los assets **por código**. Se guardan en `01_blender/assets/` y una función nueva del script los importa (append o link) y los ubica, así todo sigue siendo regenerable.
> - Opción alternativa, si se colocan a mano: usar una colección propia (por ejemplo, `10_CONTEXTO_ASSETS`), enlazarla en **las dos escenas** y no volver a ejecutar el script; o volver a enlazarla después de ejecutarlo:
>   ```python
>   for n in ("UYUNI_DIA", "UYUNI_DIA_P2_SALAR_LITIO", "UYUNI_CREPUSCULO"):
>       sc = bpy.data.scenes[n]
>       if "10_CONTEXTO_ASSETS" not in sc.collection.children:
>           sc.collection.children.link(bpy.data.collections["10_CONTEXTO_ASSETS"])
>   ```

## 8. Pendientes, con su especificación

### 8.1 Contexto y paisaje (fase 4.1)

**Atmósfera:** árida, de altura y fría (altiplano a 3667 m). La referencia es el concurso del Aeropuerto Pichoy de Mathias Klotz: sobria, elegante y con la arquitectura integrada al paisaje.

**Hoy:** el suelo es un plano de 4 × 4 km con un material procedural. Su nieve se controla con la propiedad `nieve`. No hay relieve ni vegetación.

**Por hacer:**
- Suelo de tierra o grava clara con variación, con textura PBR, y matas de paja brava dispersas.
- Relieve suave y cerros bajos en el horizonte.
- Si se quiere el horizonte real, se puede partir de un modelo de elevación (SRTM o Copernicus GLO-30) centrado en la latitud y longitud de la sección 3, rotado con el norte local.
- Mantener libre la zona de la calzada y de la plataforma.

### 8.2 Vehículos y personas (fases 4.2 y 4.3)

Hay que reemplazar los 15 proxies de `07_ASSETS/PROXIES_COLOCACION`. Sus posiciones también están en `inventario_escena.json`, en la clave `proxies_a_reemplazar`. Son cajas ocultas en el render que solo sirven de guía.

| Proxy | Tipo | Centro de la base X; Y; Z | Rotación Z | Tamaño L × A × H (m) |
|---|---|---|---|---|
| `UY_4x4_01` | vagoneta 4x4 | 8,0; −7,2; −0,15 | 0° | 4,90 × 1,94 × 2,50 |
| `UY_4x4_02` | vagoneta 4x4 | 24,5; −7,2; −0,15 | 0° | 4,90 × 1,94 × 2,50 |
| `UY_4x4_03` | vagoneta 4x4 (en circulación, carril opuesto) | 47,0; −11,4; −0,15 | 180° | 4,90 × 1,94 × 2,50 |
| `UY_4x4_04_ESTAC` | vagoneta 4x4 estacionada | 31,3; −32,5; −0,15 | 90° | 4,90 × 1,94 × 2,50 |
| `UY_4x4_05_ESTAC` | vagoneta 4x4 estacionada | 36,5; −32,5; −0,15 | 90° | 4,90 × 1,94 × 2,50 |
| `UY_MINIBUS_TRANSFER` | minibús de transfer | 63,0; −7,4; −0,15 | 0° | 6,40 × 2,05 × 2,55 |
| `UY_TURISTA_00` … `_06` | turistas en la acera | ver el inventario (Z = 0,00) | — | 1,62–1,74 de alto |
| `UY_TURISTA_07`, `_08` | turistas junto a las vagonetas, en la calzada | ver el inventario (Z = −0,15) | — | — |

**Qué pide el brief:**
- 3 o 4 vagonetas 4x4 tipo Toyota Land Cruiser clásicas del Salar, con parrilla de expedición, estacionadas y en circulación.
- Minibuses turísticos de transfer.
- Turistas con ropa de abrigo, de montaña o de trekking, con mochilas y maletas.

**Fuentes:**
- **Poly Haven** (CC0) sirve para HDRI, texturas (asfalto, hormigón, grava, tierra, roca, nieve) y algunos modelos de vegetación, rocas y objetos.
- Si Poly Haven no tiene vehículos o personas adecuados, usar otra fuente con **licencia que permita uso comercial**.
- Anotar fuente, autor, licencia y URL de cada asset en `01_blender/assets/CREDITOS.md`.
- Si se trabaja a través del MCP de Blender, su addon trae una opción para Poly Haven.

**Para no perder escala ni posición:**
- Copiar a cada modelo la matriz de su proxy: ubicación, rotación Z y apoyo a la cota Z de la base.
- Ajustar la escala al largo real (Land Cruiser ≈ 4,9 m).
- Dejar los proxies ocultos o borrarlos.

### 8.3 Cielo y clima (fase 4.4)

**Día:**
- Hoy usa el cielo procedural `MULTIPLE_SCATTERING` de Blender 5.2, configurado con altitud 3666,6 m, aire 0,9, aerosoles 0,02 y ozono 3,0 (`CIELO_ATMOSFERA`, ajustado el 3 de octubre para un azul más profundo, de aire seco de altura). Su sol está sincronizado con `UY_SOL_MANANA` (fuerza 4,5).
- Si se usa un HDRI (Poly Haven), hay que rotarlo para que su sol coincida con la dirección de la sección 3, o usarlo solo para reflejos y mantener el sol del script.

**Hora azul:** cielo de dispersión con el sol a −3,9°, piso mojado, nieve sutil, interior a 2700–3200 K, spots bajo el alero y bañadores en las celosías.

**Falta la variante "cielo plomizo invernal con nubes bajas"** que el brief ofrece como alternativa. Hay dos caminos: un HDRI nublado o el cielo con más aerosoles más un volumen de niebla suave.

### 8.4 Renders finales (fase 5)

| Cámara | Escena | Qué muestra |
|---|---|---|
| `CAM_01_HERO_LADO_TIERRA` | DIA | Hero a la altura de los ojos (1,65 m), 32 mm: M1, alero de 2 m y sombras de las celosías. |
| `CAM_02_DETALLE_ALERO` | DIA | Encuentro superior: chapa engrapada, retenedores, goterón y antepecho. |
| `CAM_02B_DETALLE_CIELO` | DIA | Cielo listonado, columnas y M1 desde la acera. |
| `CAM_03_CREPUSCULAR_NIEVE` | **CREPUSCULO** | Hora azul, piso mojado con reflejos e interior cálido. |
| `CAM_04_AEREA_GENERAL` | DIA | Aérea semicenital: volumetría limpia del Lado Tierra y del Lado Aire. |
| `CAM_05_LETRERO_HORIZONTE` | DIA | Concepto del letrero. |
| `CAM_06_DETALLE_CELOSIA` | DIA | Planchas corten, calados y sus sombras. |
| `CAM_07_PROPUESTAS` | DIA y DIA_P2_SALAR_LITIO | Fachada completa para que la gerencia elija la propuesta de color (punto 11 de la sección 5). Se renderiza con `herramientas/render_propuestas.py`. |

**Antes de los renders finales:** aplicar las mejoras de fotorrealismo de `02_postproduccion/FOTORREALISMO_BLENDER.md`. Son, sobre todo, exposición medida con False Color (la escena estaba ≈ 0,7 EV sobreexpuesta) y verticales rectas con *shift*. Se probaron en CAM_01.

**Después, los materiales:** `02_postproduccion/MATERIALES_INTELIGENTES.md`. Máscaras procedurales (aristas, cavidades y gravedad) para el polvo fino del altiplano y la pátina del corten, metálico binario, variación pieza por pieza y receta para cada material, con el vidrio de control solar con capa fina. Se probaron en CAM_06, CAM_05 y CAM_01.

**Configuración** (hoy: 4K al 50 %, 256 muestras, GPU, OIDN, AgX Medium High Contrast):
1. Resolución de 3840 × 2160 al **100 %**.
2. Cycles en GPU, con OptiX o CUDA activado en *Preferences > System*.
3. 512 muestras con umbral adaptativo de 0,01 y eliminación de ruido.
4. Salida en PNG de 16 bits, o EXR multicapa si se va a posproducir.
5. Opcional: pases de Mist, AO y Cryptomatte, y Glare en el compositor para las luces de la hora azul.

**Render por lotes** (desde Blender, en el *Scripting*):
```python
import bpy, os
salida = r"C:\RUTA\renders"
for cam in ["CAM_01_HERO_LADO_TIERRA", "CAM_02_DETALLE_ALERO", "CAM_02B_DETALLE_CIELO", "CAM_03_CREPUSCULAR_NIEVE",
            "CAM_04_AEREA_GENERAL", "CAM_05_LETRERO_HORIZONTE", "CAM_06_DETALLE_CELOSIA"]:
    sc = bpy.data.scenes["UYUNI_CREPUSCULO" if cam.startswith("CAM_03") else "UYUNI_DIA"]
    sc.camera = bpy.data.objects[cam]
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format, sc.render.image_settings.color_depth = "PNG", "16"
    sc.render.filepath = os.path.join(salida, cam + ".png")
    bpy.ops.render.render(write_still=True, scene=sc.name)
```

### 8.5 Animación del dron (fase 6)

**Trayectoria:** `CAM_DRON` está en `UYUNI_DIA`, cuadros 1–600 a 24 fps (25 s). Una restricción *Track To* la hace mirar a `DRON_OBJETIVO`.

| Cuadro | Cámara (X, Y, Z) | Mira a (X, Y, Z) | Tramo |
|---|---|---|---|
| 1 | −40, −120, 55 | 36, 10, 5 | aproximación aérea desde el Lado Tierra |
| 150 | −15, −45, 22 | 30, 0, 6 | descenso suave |
| 300 | 4, −14, 5 | 30, 0, 5 | entrada al paso rasante |
| 450 | 60, −12, 4,5 | 72, 0, 5 | paso rasante frente a la M1 y las celosías |
| 600 | 98, −26, 36 | 40, 25, 8 | elevación final: cubierta y horizonte |

**Falta configurar la salida:**
1. 1920 × 1080 al 100 %, de 128 a 256 muestras con eliminación de ruido, y *motion blur* activado.
2. Lo más seguro es renderizar una secuencia PNG, porque se puede retomar si se corta, y codificarla después:
   ```bash
   ffmpeg -framerate 24 -i CAM_DRON_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart dron_uyuni.mp4
   ```
   La alternativa es FFmpeg directo desde Blender (MPEG-4, H.264).
3. Antes del render final, revisar la trayectoria con el *viewport* o con una prueba a 25 % y pocas muestras.

**Tiempo:** el total es 600 × el tiempo de un cuadro. Conviene medir un cuadro en la GPU antes de lanzar el render.

### 8.6 Presentación y costos (fase 7)

**7.1 · Ficha para el Ministro:**
- Comparar el modelo antiguo con el nuevo. Hay una base en `00_auditoria/comparativa_original_vs_actual.png` y en las vistas `*_ORIGINAL`.
- Mensajes del brief:
  - ≈ 1.000.000 Bs ahorrados al suprimir la doble pantalla ciega, las canaletas colgadas y las pirámides de vidrio;
  - esos fondos van al termopanel acústico M1, a la cubierta estanca y al aislamiento real;
  - mejora la seguridad climática con los retenedores de nieve y sin canaletas que se congelen.

**7.2 · Láminas PDF:** pocas palabras, renders de alto impacto con llamadas técnicas simples y el MP4 del dron.

**7.3 · Cotización del servicio:** el repositorio tiene estudios de costos de renders en Bolivia hechos para otro proyecto, la terminal de Tupiza. Están en `reports/` y en `research_notes/Costos de renderizado La Paz Bolivia/`. Sirven de referencia para cotizar y para decidir si se emite con o sin factura.

## 9. Herramientas sin interfaz

Funcionan con Blender (`blender -b -P <script> -- …`) o con el módulo `bpy` de Python (`pip install bpy==5.2.2`, que requiere Python 3.13). Se ejecutan desde `01_blender/`:

```bash
# 1. Generar el .blend desde el script (unos 2 s)
python herramientas/construir_blend.py -- uyuni_modelo.py uyuni_v2.blend
# 2. Vistas previas rápidas en CPU (unos 25 s por cámara a 1280 px y 24 muestras)
python herramientas/render_previas.py -- uyuni_v2.blend previews CAM_01_HERO_LADO_TIERRA,CAM_04_AEREA_GENERAL 1280 24
# 3. Alzados y cortes ortogonales con el encuadre del CAD
python herramientas/verificar_alzados.py -- uyuni_v2.blend ../00_auditoria/vistas /tmp/verif 16
# 4. Superposición con el CAD (requiere Pillow)
python herramientas/superponer_cad.py /tmp/verif ../00_auditoria/vistas verificacion
# 5. Inventario de la escena
python herramientas/inventario_escena.py -- uyuni_v2.blend inventario_escena.json
```

La auditoría se vuelve a correr con `00_auditoria/scripts/auditoria_uyuni.py` (usa ezdxf, ifcopenshell, numpy y matplotlib).

## 10. Trampas de la API de Blender 5.2 ya resueltas

- **Cielo:** el tipo `NISHITA` ya no existe. Los tipos son `SINGLE_SCATTERING`, `MULTIPLE_SCATTERING`, `PREETHAM` y `HOSEK_WILKIE`, con las propiedades `altitude`, `air_density`, `aerosol_density`, `ozone_density`, `sun_elevation` y `sun_rotation`.
- **Principled BSDF:** las entradas se llaman `Transmission Weight`, `Subsurface Weight`, `Emission Color` y `Thin Wall`. Para vidrio delgado se usa `Thin Wall = True`.
- **Nodo `ShaderNodeMix`:** tiene varias entradas con el mismo nombre (A, B y Result en sus variantes Float, Vector y Color). Hay que elegirlas por nombre **y** tipo; ver `Nodos.sk()`.
- **Propiedades de escena en materiales:** se leen con el nodo Attribute en modo `attribute_type = "VIEW_LAYER"`.
- **Placas con calados:** una curva 2D con agujeros falla cuando un calado toca el borde. Por eso los contornos se resuelven antes con shapely (contorno − calados) y se rellenan sin superposiciones.
- **Caras coplanares solapadas:** en Cycles dan manchas o franjas negras, porque los rayos de una cara chocan con la otra. Para evitarlo:
  - los retornos del antepecho arrancan detrás de su cara;
  - las columnas extremas y el muro sobre el dintel terminan 1 cm antes de la cara exterior de los testeros.
  
  Si se agrega geometría que toque otra, conviene dejar 1 cm de separación o de traslape.
- **Módulo `bpy` sin interfaz:** si `scene.cycles` no existe, se habilita el addon con `addon_utils.enable("cycles")`. Sin GPU, se usa `scene.cycles.device = "CPU"`.
- **Nervios:** los de la cubierta, el antepecho y la franja ESTE usan modificadores Array cada 0,30 m sin aplicar. Si se exporta a otro programa, hay que aplicarlos antes.
