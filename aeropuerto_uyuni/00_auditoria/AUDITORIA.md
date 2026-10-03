# Auditoría técnica: Terminal de Pasajeros, Aeropuerto de Uyuni (Fases 0 y 0.5)

**Fecha:** 3 de octubre de 2026
**Estado:** auditoría terminada. Todavía **no se generó geometría en Blender**: queda a la espera de tu confirmación.
**Archivos que acompañan este resumen:**
- `dxf_audit_report.json`: criterio de aceptación de la Tarea 0.1.
- `ifc_audit_report.json`.
- `vistas/`: 16 vistas aisladas, cada una en PNG y en un DXF limpio (sin cotas, textos, tramas ni directrices), más `vistas_index.json`.
- `scripts/auditoria_uyuni.py`: el script que genera todo lo anterior y se puede volver a correr.

---

## 1. Qué contiene realmente cada archivo

| Archivo | Lo que se esperaba | Lo que contiene |
|---|---|---|
| `tp-arq-x-cad-FachadaEste-01.dxf` (30 MB, AutoCAD 2018) | Alzado Este | 4 fachadas (NE, SO, E, O), 2 cortes actuales, 1 corte original, 6 fichas de mamparas ME1–ME6, paneles perforados PT1/PT2, letras UYUNI y rombos. |
| `AU-SUP-EST-…TerminalPasajeros.ifc` (12,8 MB) | Estructura | Estructura de hormigón armado (Revit 2027, IFC4 ReferenceView) exportada con *parts*. |
| `AU-CBI-ARQ-…_detached-AU-SUP-EST-….ifc` (11,5 MB) | Arquitectura | ⚠️ **Es el mismo modelo estructural**: el vínculo EST exportado desde el modelo ARQ. Tiene idénticas clases y cantidades. **No incluye** muros cortina, ventanas, puertas, cubierta ni revestimientos. |
| 2 PDF | Planos | Planta Baja y Planta Alta (plantas de acabados de piso), con ejes 1–20 y A–R. No hay cortes ni alzados. |

## 2. DXF: diagnóstico general

- **Escala:** el model space está en **metros, a escala 1:1** (`$INSUNITS=6`). Las 306 cotas tienen `DIMLFAC=1000`, así que muestran mm. **Ningún detalle está re-escalado**: las escalas de 1:3 a 1:300 existen solo en los viewports.
- **Capas:** hay 23 922 entidades y el **89 % está en la capa `0`**. Hay 109 capas definidas, la mayoría vacías, incluidas capas en chino que vienen de catálogos de perfiles. Las anotaciones están en `0-COTAS*`, `0-TEXTO*`, `0-EJES`, `0-COD VENTANA` y `0-COD LOU`.
- **Dos versiones del Lado Tierra en el mismo model space:**
  - **Fila superior** (y ≈ 36…62): diseño **ORIGINAL**. Tiene el vidrio en el eje K, una doble pantalla ciega en el eje A que sube hasta +7,60, una canaleta colgada y un cielo inclinado entre K y A.
  - **Fila inferior** (y ≈ −6…20): diseño **ACTUAL**, el que usan las presentaciones `FACHADA` y `FACHADA (2)`.
- **La presentación `CORTE` está desactualizada:** sus 2 viewports apuntan a una zona vacía. Los cortes vigentes están en x = −47…−5.
- **Textos:** no hay ningún texto que diga "ALERO", "PARAPETO", "ANTEPECHO", "CANALETA", "PANTALLA", "UYUNI", "DURALIT" ni "CORTEN". Esos elementos se identificaron por su geometría. El CAD llama "ME-1" a lo que el brief llama "M1".
- **Bloques heredados de Revit desactualizados:** `Rectangular Mullion - M_160x65` y `System Panel - VT_10_A_10_VT_6`. Los textos vigentes de las fichas dicen 170×65 y DVH 4+4/12/3+3.

### Triage de vistas (Fase 0.5.2)

| Vista | Estado | Colección sugerida |
|---|---|---|
| CORTE_ACTUAL_POR_M1, CORTE_ACTUAL_MURO_CIEGO | ACTUAL | `REF_CAD_DETALLES_CUBIERTA` |
| FACHADA_NORESTE_ACTUAL (Lado Tierra) | ACTUAL | `REF_CAD_ALZADO_LADO_TIERRA` |
| FACHADA_SUROESTE (Lado Aire) | ACTUAL | `REF_CAD_ALZADO_LADO_AIRE` |
| FACHADA_ESTE, FACHADA_OESTE | ACTUAL | `REF_CAD_ALZADOS_LATERALES` |
| ME1, ME2, ME3, ME4, ME5, ME6 | DETALLE | `REF_CAD_DETALLES_M1` |
| PT1_PT2, PANELES_LETRAS_PIRAMIDES | DETALLE | `REF_CAD_DETALLES_CELOSIA` |
| CORTE_ORIGINAL_B-K-A, FACHADA_NORESTE_ORIGINAL | ORIGINAL | `REF_CAD_ANTES` (para la lámina "antes vs. después") |

La planta general no está en el DXF. Las columnas y los ejes salen del IFC (sección 4).

## 3. Verificación de cotas: lo acordado en la reunión contra lo que dice el CAD

| Ítem | Reunión / brief | CAD (fuente) | Estado |
|---|---|---|---|
| Altura de vano M1 | 5,51 m | 5510 mm (ME1, cortes y fachada NE) | ✅ |
| Perfil | 170 × 65 mm | "PERFIL DE ALUMINIO 170X65MM … NEGRO MATE" (ME1, ME2, ME6) | ✅ El travesaño es **65 × 65 mm**; el brief no lo menciona. |
| Modulación ME-1 | "según CAD" | 2150 mm de ancho; 2 paños de 1075 mm a ejes; vidrio de 978 mm; paño inferior de 2335 mm y superior de 2980 mm; travesaño a +2,40/+2,465 | ✅ (dato para modelar) |
| Termopanel | "≈ 21 mm" | 4+4 laminado (PVB 0,38) + cámara de 12 + 3+3 laminado (PVB 0,38) = **26,8 mm** (el CAD acota 26) | ⚠️ **Error en el brief**: la suma no da 21. Se modela con 27 mm. |
| Vidrio exterior | control solar | "VIDRIO FLOTADO CONTROL SOLAR 4MM" en la hoja exterior | ✅ |
| Antepecho | 2,40 m | de +6,612 a +9,012 = 2400 mm | ✅ Calza exacto con una placa Duralit de 1,20 × 2,40 en vertical. |
| Alero / volado | 2,00 m | Cielo de **2,014 m** (cara del panel sobre el dintel → cara interior del antepecho). Medido desde la cara exterior del vidrio hasta la cara exterior del antepecho: 2,11 m | ✅ |
| Dintel | horizontal, +5,51 | Viga de HºAº 300×500 de +5,51 a +6,01, recta | ✅ (ya corregido en el CAD actual) |
| Sin canaleta | — | El corte actual no tiene canaleta; el original sí | ✅ |
| Zanja de drenaje | a nivel de suelo | **0,50 m de ancho × 0,20 m de profundidad**, bajo la línea de goteo | ✅ |
| Acera | — | 4,00 m desde la cara de la columna; bordillo de −0,15 | ✅ (dato) |
| Cubierta | chapa con nervios cada 30 cm | Trama `FP_1` con líneas cada **0,30 m**; pendiente **9,0° (15,9 %)** | ✅ |
| Retenedor de nieve | doble barra a 0,40 m del borde | Una abrazadera dibujada a **≈ 1,35 m del borde**, sobre la línea del muro | ⚠️ Difiere |
| Celosía | módulo de 5,00 × 6,00 m; placas de 1,00 × 2,00 m | PT1/PT2: 5000 × 6000 con 15 placas de 1000 × 2000 | ✅ Espesor de 1 mm y separación de 12 cm: no figuran en el CAD; se usa el brief. |
| PT2 | — | Remate en zigzag: picos a 6,0 m y valles a ≈ 5,0 m, con periodo de 2 m | (dato) |
| Letras UYUNI | corpóreas corten | Detalle de 1,18 m de ancho por letra × 1,50 m de alto | ✅ |
| Cumbrera | — | +13,43 en las fachadas NE/SO; +12,92 / +13,02 en las laterales | ⚠️ Inconsistencia de 0,4–0,5 m entre vistas |

## 4. IFC: georreferenciación y estructura

- **Sistema de coordenadas:** EPSG:32719 (WGS84 / UTM 19S). `IfcMapConversion` es identidad; las coordenadas reales están en el *placement* del IfcSite/IfcBuilding:
  - **E 724 956,439 / N 7 737 860,959 / cota 3666,743 m s.n.m.**
  - Rotación del eje X local: **148,2058°** (antihorario desde el Este).
  - Latitud/longitud: −20,4461546 / −66,8497209.
  - Convergencia de meridianos: −0,751°.
- **Orientación** (azimut verdadero de la normal de cada fachada):
  - Lado Tierra (eje A, "FACHADA NORESTE"): **31,0° (NNE)**.
  - Lado Aire (eje R): 211,0°.
  - Lateral del eje 1 ("ESTE"): 121,0°.
  - Lateral del eje 20 ("OESTE"): 301,0°.
  - Norte verdadero en coordenadas locales del edificio: **301,04°** antihorario desde +X.
- **Niveles:** el **NPT ±0,00 del DXF corresponde al nivel IFC "0P" = 3666,593 m s.n.m.** Lo confirma que los +7,100 y +7,600 del DXF coinciden con 2P y 3P.

  | Nivel | C | 0P | 1P | 2P | 3P | 4P | 5P |
  |---|---|---|---|---|---|---|---|
  | Sobre NPT (m) | −1,50 | 0,00 | +3,85 | +7,10 | +7,60 | +9,00 | +11,50 |

- **Ejes** (coordenadas locales):
  - Ejes 1–20 cada **4,80 m**, con juntas en 11/11′ (0,50 m) y 17/18 (0,45 m). El eje 20 está en x = 82,51.
  - A = 0,192 · K = 4,213 · B = 9,282 … R = 48,321. A–K = 4,02 m.
- **Estructura:**
  - Columnas de HºAº de **0,40 × 1,00 m** sobre el eje A, cada 4,80 m, desde la cara exterior (y = −0,308) hasta la cara interior (y = +0,692). Llegan a +7,60.
  - Vigas, zapatas, losas, 20 muros y escaleras: todo de hormigón.
  - **No hay cerchas de acero ni cubierta en el IFC.** Nada vuela más allá de las columnas hacia el Lado Tierra. La cubierta y el alero se modelan desde el corte del DXF.
- **Correspondencia DXF ↔ IFC** (ver `vistas_index.json`):
  - Fachada NE: `X_ifc = x_dxf`. Las líneas de eje del DXF están en 0,0 / 4,8 / 9,6…, igual que en el IFC.
  - Corte por M1: `Y_ifc = −41,147 − x_dxf`.
  - Corte original: `Y_ifc = −15,193 − x_dxf`.
  - Las alturas del DXF están en metros sobre NPT.
  - Hay dos diferencias menores entre el CAD y Revit:
    - Eje "12" del DXF en 48,52 contra el eje 11′ del IFC en 48,50.
    - Eje 17 del DXF en 72,43 contra 72,36 en el IFC.

## 5. Elementos a suprimir (Fase 1.1): dónde aparecen

| Elemento | Dónde aparece | Conclusión |
|---|---|---|
| Doble pantalla ciega exterior (Lado Tierra) | Solo en el CORTE ORIGINAL (eje A, hasta +7,60) | Ya no está en el diseño actual. No se modela. |
| Canaletas perimetrales colgadas | Solo en el CORTE ORIGINAL (+7,05 a +9,53) | El actual va sin canaleta. No se modela. |
| Planos inclinados sobre ventanales | Original (cielo inclinado entre K y A) | El actual tiene el dintel horizontal a +5,51. |
| Pirámides de vidrio sobre la cubierta y "alas de avión" | **No están ni en el DXF ni en los IFC**: el IFC arquitectónico real no se exportó | No se modelan. |
| "Falsa isóptica" / UYUNI anamórfico | La FACHADA NE ACTUAL todavía muestra **UYUNI con una copia espejada y 5 rombos** sobre el antepecho (x ≈ 30–62) | ❓ Ver pregunta 1. |

Como todo se modela desde cero con bpy, "suprimir" equivale simplemente a no modelar esos elementos.

## 6. Hallazgos que cambian el modelado

1. **M1 no es un muro cortina continuo.** Son unidades discretas entre columnas:
   - 7 × **ME-1** de 2,15 × 5,51 m.
   - 2 × **ME-2** de 4,28 × 5,51 m, que son los accesos con puerta corrediza con sensor.
   - Entre unidades hay paño ciego de panel M2 (EPS + malla + mortero, e = 130 mm).
   - Medidas sobre el DXF, con ejes coincidentes con el IFC:
     - ME-1 va **centrada en el vano**: 1,325 + 2,15 + 1,325 = 4,80 m. Descontada media columna (0,20 m), quedan 1,125 m de paño ciego a cada lado.
     - ME-2: 0,26 + 4,28 + 0,26.
2. **El vidrio pasó del eje K (original) al eje A (actual).** Va contra la cara interior de las columnas de 0,40 × 1,00.
3. **La fachada principal mira al NNE (31°).** En Uyuni recibe sol directo por la mañana y a mediodía; **al atardecer queda a contraluz**:
   - Para la CÁMARA 01 con sombras de las planchas corten conviene media mañana.
   - El atardecer funciona para la CÁMARA 03 crepuscular (interior encendido, fachada en sombra).
4. **Hay dos listas de colecciones distintas en el brief:** la de la Fase 0.3 (`00_ARCH_ESTRUCTURA…`) y la de la Tarea 0.2 (`_REF_CAD`, `01_ESTRUCTURA…08_CAMERAS_LIGHTS`). Propongo usar la segunda, que es más granular, con `_REF_CAD` subdividida según el triage.

## 7. Decisiones confirmadas (3 de octubre de 2026)

| # | Tema | Decisión |
|---|---|---|
| 1 | Letrero UYUNI del antepecho | **Corregido el 3 de octubre: se MANTIENE.** Es el concepto "línea de horizonte": montículos de sal (triángulos perforados) y letras UYUNI sobre el horizonte (+7,764), con su reflejo debajo (marcos y letras en contorno). Elementos **blancos** sobre el antepecho de **chapa café chocolate** (continuación de la cubierta). Modulación del CAD: 1446 · 2000 · 1000 · 2717 · 3×1000 · 1184 · 5576 · 5952 · 2000 · 6401 · 308; letras de 1,50 m con trazo de 200 mm; perforaciones de Ø 50 mm. La "falsa isóptica / estructura anamórfica" a eliminar no es este letrero: no figura en los archivos recibidos. |
| 2 | Celosías | **Oeste: 2 · Este: 2 · Lado Tierra: 5 PT2 · Lado Aire: 2 PT2.** |
| 3 | Retenedores de nieve | Doble barra **a 0,40 m del borde libre**, con abrazaderas sobre los nervios cada 0,30 m. |
| 4 | Hero shot (CAM_01) | **Luz de mañana**, con sol sobre la fachada NNE y sombras de las planchas corten. |
| 5 | Repositorio | Se suben los informes. |
| 6 | Materiales (imagen de referencia del 3 de octubre) | Antepecho en chapa café chocolate con nervios verticales; letrero blanco; muros de Duralit en crema claro; bolardos; bañadores cálidos al pie de las celosías y nieve en el borde (hora azul). |
| — | Cumbrera | Sin respuesta. Se toma el perfil de los alzados laterales (≈ +13,0) para el volumen y queda como parámetro. |
| — | Colecciones | Se usa la lista de la Tarea 0.2 (`_REF_CAD`, `01_ESTRUCTURA` … `08_CAMERAS_LIGHTS`). |
