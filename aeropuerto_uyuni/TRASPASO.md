# Traspaso: visualización de la Terminal de Pasajeros del Aeropuerto de Uyuni

**Continuación Codex, 4 de octubre:** leer también `CONTINUACION_CODEX.md`.
La rama `codex/continuacion-uyuni` incorpora exteriores revisados, assets CC0,
cámaras/compositor y el montaje del storyboard de 120 s. Por indicación posterior
del cliente, los paños de la fachada trasera avanzan 0,70 m hasta las pilastras;
solo quedan nichos en las dos crujías de ventanales grandes. La entrada pequeña
es ahora frontal y alineada. Land Cruiser y personas escaneadas se incorporan
en el `.blend` local, excluido de Git; el minibús público sigue provisional.

**Frente del Lado Tierra, 5 de octubre:** las circulaciones y jardineras frente a la
fachada principal se rehicieron fieles al modelo del cliente, medidas por
fotogrametría sobre sus capturas DALUX (±0,5 m): `frente_lado_tierra()` y los
parámetros `FRENTE`, `JARDINERAS`, `ESPIGA`, `ANDENES`, `CEBRA`, `DISCOS` y
`COLUMNAS`. Reemplaza al cantero, el estacionamiento de 120 puestos y el anillo de
antes, y a la propuesta de Codex (`continuacion/exteriores.py`, retirado). No
cambian la fachada, la vereda A111 con sus dársenas, el cordón ni las calles de los
testeros. Con `CONTEXTO_IA = True` (`continuacion/pipeline.py`) la vegetación del
terreno y los vehículos provisionales no salen en el render: el contexto se agrega
con IA. Detalle en `CONTINUACION_CODEX.md`.

**Fecha:** 3 de octubre de 2026, actualizada el 4 de octubre: por la tarde, Lado Aire, laterales y detalles; por la noche, carpintería negro mate, veredas de la A111, contexto del aeropuerto y librea de BoA (las dos en `CAMBIOS_4OCT_FACHADAS.md`) · **Blender:** 5.2.2 LTS, Cycles · **Rama del repositorio:** `claude/clever-hypatia-i19958`

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
| 2 | Cubierta engrapada, retenedores de nieve, goterón sin canaleta, zanja y cielo del alero | ✅ Revisado el 3 de octubre (cielo listonado). El retenedor sigue el detalle del cliente del 4 de octubre (sección 5). |
| 3 | Celosías corten (módulos de 5 × 6 m con planchas de 1 × 2 m) y letrero UYUNI | ✅ 14 módulos (3 más en la OESTE desde el 4 de octubre) y letrero "línea de horizonte". |
| Materiales | PBR | ✅ Procedurales, sin texturas de imagen. |
| 4 | Entorno, vehículos, personas, clima y cielo | ⚠️ **Parcial.** Faltan dos cosas: 1) reemplazar los vehículos y las personas, que hoy son cajas de ubicación que no salen en el render; 2) la variante de cielo nublado. Ya está, desde el 4 de octubre: <br>• **Lado Tierra** según la A111: vereda de ≈ 8,8 m con dos dársenas y zanja; frente según el modelo del cliente (5 de octubre): calzada, jardineras A y B con anillos blancos, separador amarillo, plaza de estacionamiento con hexágonos y espiga, andenes y cebra; calles de los testeros y acceso (los bolardos se quitaron el 3 de octubre). <br>• **Lado Aire:** veredas y cordón de la A111, camino de servicio, plataforma con marcas, dos mangas y dos 737-800 con la librea de BoA. <br>• **Contexto:** pista 13/31 con marcas OACI (su distancia a la terminal es supuesta), calle de rodaje, manga de viento, terreno de 45 km con cerros y el Salar, y paja brava. |
| 5 | Cámaras y renders fijos | ✅ Lote de 24 imágenes terminado con GPU: 12 encuadres por paleta, incluidos CAM_02B y CAM_07B. Dos CAM_01 en 8K y las 22 restantes en 4K. La hora azul se actualiza con neón atenuado e interior cálido; el video continúa en pausa. |
| 6 | Dron de 20–30 s, 24 fps, 1080p, MP4 H.264 | ⚠️ La trayectoria está lista (`CAM_DRON`, 600 cuadros = 25 s). Faltan la configuración de salida y el render. |
| 7 | Ficha de costos para el Ministro, láminas PDF, MP4 y facturación | ❌ Pendiente (sección 8.6). |

## 2. Contenido del paquete

El paquete (`UYUNI_paquete_traspaso_….zip`) es el repositorio completo:

```
aeropuerto_uyuni/
├── README.md                    uso rápido (escenas, render, parámetros clave)
├── TRASPASO.md                  esta guía
├── CAMBIOS_REUNION_3OCT.md      cambios desde el primer traspaso y cómo llevarlos a un .blend con avance propio
├── CAMBIOS_REUNION_3OCT_uyuni_modelo.diff   los mismos cambios, línea por línea, en el script
├── CAMBIOS_4OCT_FACHADAS.md     Lado Aire, laterales, mangas y aviones, nichos, ME-2 y retenedor (4 de octubre, tarde);
│                                respuestas del cliente, veredas de la A111, contexto y librea de BoA (noche, sección 11)
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
    ├── verificacion/            modelo superpuesto al CAD: alzados, cortes y plantas (las del Lado Aire, los
    │                            laterales, la ME-2, el retenedor, las veredas del Lado Tierra y el contexto son
    │                            proyecciones 2D, sin render; ENCUADRE_*: perspectiva aproximada de CAM_10 y CAM_04)
    ├── propuestas/              hojas comparativas: dos propuestas de color y letrero (material y geometría)
    ├── fotorrealismo/           hojas de las pruebas de realismo: día, materiales, vidrio, noche y muestreo
    └── herramientas/            scripts sin interfaz: construir, renderizar (también las propuestas, y en franjas
                                 que se retoman: render_banda.py y unir_bandas.py), verificar, inventariar,
                                 aplicar_cambios_reunion.py y aplicar_cambios_4oct.py (decisiones del 3 y del 4 de octubre
                                 sobre un .blend existente), las pruebas de realismo prueba_*.py (hoja_muestreo.py saca
                                 los números de prueba_muestreo.py) y la verificación sin render: exportar_geometria.py
                                 y superponer_cad_2d.py
02_postproduccion/               GUIA_REALISMO_FOTOGRAFICO.md y sus documentos de detalle (fotorrealismo, materiales,
                                 iluminación nocturna, muestreo y rendimiento), prompts de IA por vista, de upscale y
                                 unificar_color.py
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
| `…_Sheet_-_A111_-_PLANTA_BAJA.dxf` (4 de octubre) | Planta baja arquitectónica en coordenadas del modelo (1:1): muros, puertas, vidrios, columnas y cordón de vereda (capa A-FLOR). |
| `tp-arq-x-cad-FachadaSUROESTE_FACHADATRASERA.dxf` (4 de octubre) | Alzado del Lado Aire con sus carpinterías y puertas. |
| `tp-arq-x-cad-FachadaESTE_y_FachadaOESTE.dxf` (4 de octubre) | Los dos testeros. Respecto del DXF anterior solo suma 3 módulos de celosía en la OESTE. |
| `tp-arq-x-cad-detalle_puertas_ME-2.dxf` (4 de octubre) | Elevación y secciones de la ME-2: hojas corredizas, viga de acero y operador. |

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
- ⚠️ **El origen no está en el sitio real de la terminal.** Con esta georreferencia, las cabeceras publicadas de la pista 13/31 caen en X −1034,5 y X 2962,6: la pista sale paralela al eje X, como el edificio, pero a ≈ 55 m del **Lado Tierra**, lo que no es posible. El modelo conserva esas X y la orientación, y pone el eje de la pista del Lado Aire, a una distancia supuesta de 330 m (`PISTA`; `CAMBIOS_4OCT_FACHADAS.md`, sección 11.3). Hace falta el plano de sitio para confirmarlo.

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
| `FACHADA_SUROESTE` | Lado Aire | X = 187,866 − x · Z = y (hasta el 4 de octubre se usó 187,84: la planta A111 muestra que el alzado va corrido 2,6 cm) | +Y |
| `FACHADA_ESTE` | testero del eje 20 | Y = −0,308 + (x − 249,787) · Z = y | +X |
| `FACHADA_OESTE` | testero del eje 1 | Y = −0,308 + (384,834 − x) · Z = y | −X |
| `CORTE_ACTUAL_POR_M1` | corte por una ME-1 | Y = −41,147 − x · Z = y | +X |
| `CORTE_ACTUAL_MURO_CIEGO` | corte por paño ciego | Y = −24,125 − x · Z = y | +X |
| `CORTE_ORIGINAL_B-K-A`, `FACHADA_NORESTE_ORIGINAL` | diseño anterior | Y = −15,193 − x (corte) o X = x (fachada) · Z = y − 42,914 | — |
| `ME1`…`ME6`, `PT1_PT2`, `PANELES_LETRAS_PIRAMIDES` | fichas de detalle 1:1 | coordenadas propias: se mide dentro de cada ficha | — |

**DXF del 4 de octubre** (en `UYUNI_insumos_cliente.zip`, sin vistas aisladas):

| DXF | DXF → modelo | Se mira desde |
|---|---|---|
| Planta baja A111 | X = x · Y = y (1:1) | arriba |
| Fachada SUROESTE | X = 187,866 − x · Z = y | +Y |
| Fachadas ESTE y OESTE: la ESTE en x < 320 | Y = x − 250,095 · Z = y | +X |
| Fachadas ESTE y OESTE: la OESTE en x > 320 | Y = 384,526 − x · Z = y | −X |
| Detalle ME-2: sección 1 (horizontal) | X = x − 30,148 + X₀ de la ME-2 · Y = 0,479 + (y + 25,45) | arriba |
| Detalle ME-2: sección 2 (vertical) | Y = 0,479 + (x − 36,233) · Z = y + 24,42 | +X |

**Superposiciones** (`01_blender/verificacion/`):
- **Con render (3 de octubre):** `SUPERPOSICION_FACHADA_NORESTE_ACTUAL.jpg` y los dos cortes son renders ortogonales del modelo con el CAD encima, en rojo, con el mismo encuadre y la misma escala que el PNG de la vista. Se regeneran con `herramientas/verificar_alzados.py` y `herramientas/superponer_cad.py` (sección 9). Las láminas `lamina_verificacion_alzados.jpg` y `lamina_verificacion_cortes.jpg` son de esa fecha: todavía muestran el Lado Aire y los laterales anteriores.
- **Sin render (4 de octubre):** el Lado Aire (`LADO_AIRE_*`), los alzados SUROESTE, ESTE y OESTE (`SUPERPOSICION_FACHADA_*`), los nichos de la fachada principal, la ME-2, el retenedor, el 737 con su librea, las veredas del Lado Tierra sobre la A111 (`LADO_TIERRA_*`) y el contexto (`CONTEXTO_*`: plataforma, pista, cabeceras y horizonte). Son cortes y proyecciones del modelo dibujados con matplotlib sobre los DXF del cliente, con `herramientas/exportar_geometria.py` y `herramientas/superponer_cad_2d.py` (sección 9). No gastan render.
- **Encuadres sin render:** `ENCUADRE_CAM_10_PISTA_HORIZONTE.jpg` y `ENCUADRE_CAM_04_AEREA_GENERAL.jpg` son perspectivas aproximadas (orden de pintor, sin luz ni cielo) para ver qué entra en cuadro.
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
   - **Decisión del 4 de octubre: queda la A**, con las letras de tamaño original, sin reducción. La B se conserva en el modelo, pero ya no se entrega.
3. **Celosías:** 5 en la OESTE (4 PT1 y una en rampa, `PT1R`, según el DXF del 4 de octubre; apoyan a +0,11), 2 en la ESTE, 5 PT2 en el Lado Tierra y 2 PT2 en el Lado Aire. Las posiciones y variantes exactas están en `CELOSIAS`.
4. **En los detalles PT1/PT2, las tramas grises son vacíos (calados)** y las líneas salmón son el bastidor que sostiene las planchas por detrás.
5. **Retenedor de nieve (detalle del cliente del 4 de octubre; reemplaza la versión del 3 de octubre):**
   - abrazadera de chapa de 6 mm, de **174 mm de alto y 113 mm de base**, con la cabeza redondeada, perpendicular a la chapa y en el plano del nervio;
   - dos orejas de 38 mm que muerden el nervio, con su perno;
   - **tres agujeros de 23 mm** (centros a 48,5, 92,5 y 137,5 mm de la base), con un tubo en cada uno;
   - eje a **1,398 m del borde, medido sobre la pendiente**, encima de la primera correa (casi sobre la línea de las columnas);
   - abrazaderas sobre un nervio de cada dos (cada 0,60 m);
   - todo en `RETENEDOR`;
   - **tubos:** tres, de 21,3 mm (1/2"), uno por agujero. Confirmado por el cliente el 4 de octubre por la noche (uno de 1" no entraría en el agujero de 23 mm).
6. **Hero shot (CAM_01): luz de mañana**, con el sol sobre la fachada y las sombras de las planchas corten.
7. **Materiales (revisados el 3 de octubre):**
   - **Muros y columnas:** panel EPS de 80 mm con malla y **revoque proyectado continuo**, sin placas ni juntas verticales. Viga y columna van revocadas en el mismo plano y tono que el muro. Solo hay una **buña horizontal fina** (10 mm) arriba y abajo de la viga de +5,51 a +6,01. Hacen de fondo neutro.
   - **Carpintería de aluminio:** **negro mate** `#2E2F31`, pintura en polvo: sin metálico y con rugosidad 0,60 (`PERFIL_COLOR`, `PERFIL_RUGOSIDAD`, `mat_perfil()`). Así lo pide el detalle de la ME-2 y lo confirmó el cliente el 4 de octubre por la noche; el 3 de octubre había sido antracita `#3A3E41`. Puertas de acero, viga y operador de la ME-2 llevan el mismo acabado.
   - **Cielo falso del alero:** **parrilla de listones** de 40 × 100 mm, perpendiculares a la fachada cada 0,15 m (antecedente del Rectorado), sobre perfiles portantes y un **plenum negro mate** que oculta el interior del alero. Las luminarias son lineales, entre listones.
   - **Sin bolardos ni postes de iluminación peatonal:** no están en el presupuesto.
   - **Colores:** dependen de la propuesta (punto 11).
   - **Hora azul:** bañadores cálidos al pie de las celosías y nieve en el borde de la cubierta.
8. **Elementos de los laterales (aprobados):**
   - en la OESTE: rombo perforado, bloque con mástil y volumen saliente (la caja de la puerta de embarque 1);
   - en la ESTE: franja nervada de +4,41 a +6,21;
   - **desde el 4 de octubre, según el DXF:**
     - en la ESTE, puertas dobles y simples con rejilla y el patio techado;
     - en la OESTE, los 3 módulos de celosía nuevos (`CAMBIOS_4OCT_FACHADAS.md`, sección 5).
9. **Colecciones:** se usa la lista de la Tarea 0.2 del brief, de `_REF_CAD` a `08_CAMERAS_LIGHTS`, más `10_MANGAS_AERONAVES` y `11_CONTEXTO_AEROPUERTO` (4 de octubre).
11. **Dos propuestas de color para la gerencia (reunión del 3 de octubre).** Las elige la propiedad `propuesta` de la escena: 0 es P1 (escena `UYUNI_DIA`) y 1 es P2 (escena `UYUNI_DIA_P2_SALAR_LITIO`). Los colores están en `PALETA`.

    | Elemento | P1 "Patrimonio Ferroviario" | P2 "Salar & Litio" |
    |---|---|---|
    | Celosías | Acero corten, óxido cobrizo cálido | Blanco perla |
    | Parapeto y remates | Antracita mate | Blanco perla |
    | Letrero y pirámides | **Corten** (`letras_corten` = 1) | **Gris casi negro** `#2E3133` (`letras_gris` = 1), decidido el 4 de octubre |
    | Cubierta | Antracita | Gris claro metálico |
    | Cielo listonado | Símil madera | Blanco |
    | Muros y columnas | Hormigón claro `#B9B5AD` | **Casi negro** `#36393B` (4 de octubre; antes `#6B6E70`) |
    | Carpintería | **Negro mate** `#2E2F31` (4 de octubre; antes antracita) | Negro mate |

    El color de la cubierta, la madera del cielo en P1 y el bastidor de las celosías (color del muro en P2) no se pidieron expresamente: son propuestas mías y conviene confirmarlas.

    La vista para la gerencia es `CAM_07_PROPUESTAS`. Parte de la perspectiva de la captura del cliente, que está guardada tal cual como `CAM_07B_CAPTURA_CLIENTE`, mejorada así: fachada completa con márgenes, 28 mm desde 6,0 m de altura y verticales rectas.
12. **Vidrio de las fachadas y control solar (4 de octubre):**
    - **DVH:**
      - vidrio interior laminado incoloro de 3+3 mm;
      - cámara de aire;
      - vidrio exterior de 4 mm, acoplado o laminado con una lámina o un tratamiento de control solar.
    - **Menos reflexión:** el arquitecto pide bajar la reflectividad del vidrio exterior. La fachada no debe parecer un espejo ciego: tiene que dejar ver la estructura de adentro (columnas, vigas y carpinterías).
    - **Tono más oscuro:** se valida, porque contrasta y resalta la estructura y los elementos blancos del edificio.
    - **En el modelo:** ya está, con la variante 6 de `02_postproduccion/MATERIALES_INTELIGENTES.md`, sección 4 (`VIDRIO` y `mat_vidrio`: tinte `#6E808E` y capa de baja reflexión). Para que se vea la estructura detrás del vidrio, falta modelar las columnas y vigas interiores cercanas a la fachada, a partir del IFC.
    - **Opciones finales para el cliente (4 de octubre):** P1 con letras corten sobre el parapeto antracita y P2 con letras casi negras sobre el parapeto blanco, las dos con la geometría A y este vidrio.
    - **Para llevarlo a un `.blend` con avance propio:** `01_blender/herramientas/aplicar_cambios_4oct.py`, después de `aplicar_cambios_reunion.py`.
13. **Fachada Lado Aire, pista y plataforma (4 de octubre):**
    - se aprueba la perspectiva general del Lado Aire;
    - hay que incorporar al render las **mangas de abordaje**, **aeronaves Boeing de la aerolínea estatal** (BoA) y la **extensión de la pista hasta el horizonte**, para que las tomas aéreas no muestren vacíos;
    - especificación en la sección 8.7.
14. **Fachada Lado Aire, laterales, mangas y aviones (4 de octubre, tarde, con los DXF nuevos):**
    - **fachada:** se modela como la dibujan la planta A111 y el alzado SO:
      - el bloque de los ejes 1-5 llega al eje R;
      - el resto de la fachada es el muro del eje I, con pilastras, puertas, ventanas, nicho, marquesina y vestíbulo;
    - **mangas:** dos, en las dos puertas de embarque del nivel 1P;
    - **aviones:** dos 737-800 estacionados como en la captura del modelo del cliente;
    - **entorno:** veredas y cordón de la planta, y el camino de servicio de la vista aérea;
    - **detalle:** `CAMBIOS_4OCT_FACHADAS.md`; lo que falta confirmar está en su sección 8.
15. **Fachada principal: nicho solo en los ventanales (4 de octubre).** Los paños con ME-1 o ME-2 quedan retirados en el plano del muro. Todos los demás van al ras de la cara de las columnas: ciegos, con rombos ME-3, detrás de las celosías y en el anexo.
16. **Puertas ME-2 según su detalle (4 de octubre):**
    - las hojas corredizas automáticas corren por el lado interior del perfil;
    - van bajo una viga de acero negro mate de 170 × 200 mm, con el operador debajo;
    - no queda ninguna rendija que deje ver el interior.
17. **Respuestas del cliente (4 de octubre, noche; `CAMBIOS_4OCT_FACHADAS.md`, secciones 8 y 11):**
    - **aviones:** la orientación está bien y llevan la **librea de BoA**, que tiene autorización;
    - **ME-6 del bloque:** queda en la línea interior, como estaba;
    - **alturas del vestíbulo y del anexo:** quedan como estaban "por ahora";
    - **retenedor:** tres tubos de 1/2";
    - **carpintería:** negro mate (punto 7);
    - **Lado Tierra:** se aplican la vereda y las dársenas de la A111 y se modela más contexto: calles, estacionamiento, pista, rodaje, terreno y vegetación. El 5 de octubre, el frente (calzada, jardineras y plaza) pasa a seguir el modelo del cliente.
10. **Reglas de oro del brief:**
    - el DXF solo sirve para verificar: no se calca ni se importa como geometría;
    - toda la geometría se genera con `bpy` a partir de medidas numéricas;
    - ningún objeto queda suelto en la colección raíz;
    - después de cada iteración se purgan los datos huérfanos.

## 6. Supuestos y puntos abiertos: qué revisar contra el DXF

Están ordenados de mayor a menor impacto en los renders.

| # | Tema | Cómo está hoy | Qué revisar | Parámetro o función |
|---|---|---|---|---|
| 1 | **Testero del eje 20 (FACHADA ESTE)** | ✅ Resuelto el 4 de octubre: puertas dobles y simples con rejilla y el patio techado, según el DXF. | Mira `SUPERPOSICION_FACHADA_ESTE.jpg`. | `testero_este()` |
| 2 | **Cumbrera** | +13,02, según los alzados laterales. | Las fachadas NE y SO marcan +13,43. La diferencia se ve en las superposiciones NE y SO: la banda nervada del CAD queda más alta que la del modelo. **Confirmar con el cliente antes de cambiarla.** | `CUMBRERA_Z` (mueve solo el vértice de la cumbrera de `PERFIL_CUBIERTA`) |
| 3 | **Volumen saliente del Lado Aire (esquina del eje 1)** | ✅ Resuelto el 4 de octubre: es la caja de la puerta de embarque 1 (X 0,83–2,83, como en el alzado SO), con su frente vidriado. Ahí se apoya la manga 1. | — | `CAJA_OESTE`, `elementos_laterales()` |
| 4 | **Elemento vertical en la esquina del eje 1 / Lado Aire** | ✅ Modelado el 4 de octubre como bajante con abrazaderas, a las alturas del alzado SO. | Si el cliente aclara que es una escalera de gato, se cambia. | `BAJANTE_OESTE` |
| 5 | **Mástil OESTE** | X = 0,6. Es un supuesto, porque el alzado no da su posición en X. | Se puede confirmar con el alzado SO. | `MASTIL_OESTE` |
| 6 | **Lado Aire** | ✅ Resuelto el 4 de octubre con la planta A111 y el alzado SO: carpinterías, puertas, pilastras, marquesina, nicho, vestíbulo y bloque. | Lo que falta confirmar está en `CAMBIOS_4OCT_FACHADAS.md`, sección 8. | `fachada_aire()` |
| 7 | **Rombo perforado OESTE** | Usa el material del letrero: corten en P1 y blanco en P2. | Confirmar con el cliente. | `elementos_laterales()` |
| 8 | **Entorno** | ✅ Desde el 4 de octubre (noche), todo el cordón sigue la planta A111: en el Lado Tierra, vereda de ≈ 8,8 m con dos dársenas y la zanja de 0,50 × 0,20 m del corte bajo el alero; en el Lado Aire y los laterales, veredas y cordón, más el camino de servicio de la vista aérea del cliente. | Mira `LADO_TIERRA_PLANTA_VEREDAS.jpg`: desvío máximo de 1 cm con la A111. | `cordon_tierra()`, `DARSENAS_TIERRA`, `entorno()`, `cordon_aire()`, `entorno_aire()` |
| 12 | **Contexto que no está en los planos** | Frente del Lado Tierra (calzada, jardineras, plaza): medido por fotogrametría sobre las capturas DALUX del cliente (±0,5 m), no sobre un plano. Calles de los testeros y acceso: propuesta. Pista 13/31 con las X de la georreferencia y el eje a una distancia **supuesta** de 330 m del Lado Aire (sección 3). | Plano de sitio o de accesos del cliente (para pasar el frente a cotas de obra), y la distancia real entre la terminal y la pista. | `frente_lado_tierra()`, `calzada_frente()`, `FRENTE`, `JARDINERAS`, `PISTA`, `RODAJE`, `contexto_aeropuerto()` |
| 9 | **Cerchas de la cubierta** | No están modeladas, porque no se ven desde afuera. | Los cortes las dibujan. Son opcionales. | — |
| 10 | **Interiores** | Una caja emisiva cálida en cada lado, según el brief: "interiores básicos". | — | `envolvente_general()`, `fachada_aire()` |
| 11 | **Primera correa de la cubierta** | ✅ Resuelto con el detalle del cliente: el retenedor va a 1,398 m del borde, medido sobre la pendiente. | — | `RETENEDOR` |

**Letrero de noche corregido después del lote del 4 de octubre:** ambas paletas
conservan la base metálica, corten en P1 y casi negra en P2. Según la referencia
posterior del cliente se añaden frentes luminosos tipo neón en los trazos CAD:
UYUNI, su grafismo invertido, montículos y línea horizontal. También se enciende
el interior existente detrás del vidrio. Los difusores se enlazan solo a las
escenas de hora azul; la paleta diurna permanece. La fuente reproducible es
`01_blender/continuacion/letrero_nocturno.py`, integrada en `pipeline.py`.
La escena `UYUNI_CREPUSCULO_P2_SALAR_LITIO` queda guardada con la misma cámara,
exposición y luces de P1, y su compositor lee su propia escena.

**Abiertos desde el 4 de octubre (preguntar al cliente):**
- **La estructura detrás del vidrio:** para que se vea, hay que modelar las columnas y vigas interiores cercanas a la fachada (del IFC). Confirmar cuáles quiere ver el arquitecto. Además (`02_postproduccion/MUESTREO_Y_RENDIMIENTO.md`, sección 3):
  - en Cycles, el sol no atraviesa el vidrio: para que la estructura reciba luz de afuera, el vidrio tiene que ser transparente para los rayos de sombra (la receta está en esa sección);
  - el vidrio elegido deja pasar 2,9 % de la luz, mucho menos que un DVH de control solar habitual (de 20 a 50 %; los más oscuros, de 10 a 20 %). Con eso la estructura no se ve de día. Proponer al cliente el tinte `#A9BCCB` con la misma capa, que deja pasar 15 % (medido) y de día se sigue viendo oscuro, y mostrarle la prueba antes de cambiarlo.
- **La librea de BoA:** el cliente confirmó que BoA tiene autorización. Es una aproximación, porque no hubo referencia gráfica: con una foto o el manual de marca se ajustan los colores, la deriva y la tipografía.
- **La distancia entre la terminal y la pista:** hoy es supuesta (330 m al eje). Sacarla de un plano de sitio del cliente o medirla en OpenStreetMap o Google Earth sobre la terminal existente (secciones 3 y 8.7).
- **Lado Aire, laterales y detalles:** siguen abiertos dos puntos de `CAMBIOS_4OCT_FACHADAS.md`, sección 8:
  - el remate de la cubierta sobre el eje I;
  - la galería del bloque.
- **Contexto nuevo:** los cuatro puntos de `CAMBIOS_4OCT_FACHADAS.md`, sección 11.6: la distancia de la pista, las calles y el estacionamiento (son una propuesta), el cerco perimetral (no está modelado) y la librea.

**Ya resueltos (no hace falta volver a revisarlos):**
- Termopanel: 26,8 mm según el CAD (4+4 / 12 / 3+3). El brief decía 21 mm por error de suma.
- Ejes del DXF contra los del IFC: hay diferencias de 2 a 7 cm (eje 12 del DXF contra el 11′ del IFC, y eje 17). Se usan los del IFC.
- Columnas del anexo (ejes 18–20): sobresalían ≈ 1 m por encima de su cubierta y se veían en el hero shot. Se corrigió el 3 de octubre y ahora terminan en ella.

**Diferencias dentro del propio CAD (no copiarlas al modelo):**
- **Alero en los laterales:** los alzados ESTE y OESTE no dibujan el volado de 2 m ni el antepecho en el extremo del Lado Tierra. Cortan la cubierta en Y ≈ −0,26, a ≈ +8,9. Los cortes vigentes y la fachada NE sí los dibujan. El modelo sigue los cortes, por eso en las superposiciones laterales el antepecho sobresale del contorno rojo.
- **Diseño original:** la fila superior del DXF (doble pantalla, canaleta, vidrio en el eje K) es el diseño descartado.
- **Retenedor:** el CAD lo ubicaba a ≈ 1,35 m del borde. El detalle del cliente del 4 de octubre lo confirma: 1,398 m sobre la pendiente, y así está en el modelo.
- **Alzado SO contra la planta A111:** el alzado va corrido 2,6 cm en X. Además dibuja la ME-6 del bloque, que en la planta queda en la línea interior, detrás del muro del eje R. El modelo sigue la planta.

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
| `muro_landside`, `mamparas` | `02_ENVOLVENTE`, `03_CARPINTERIAS_M1` | paños `UY_MURO_NE_*` (en nicho, revoque con buñas) y `UY_MURO_NE_RAS_*` (al ras de las columnas), `UY_MAMPARA_M1_FRAMES/GLASS/SELLOS` (7 ME-1 y 2 ME-2) y `UY_ME2_VIGA_OPERADOR_*` |
| `antepecho_alero` | `02_ENVOLVENTE` | `UY_ANTEPECHO_2_40_CHAPA`, `UY_ANTEPECHO_NERVIOS` (Array cada 0,30), `UY_CIELO_LISTONES` (Array cada 0,15), `UY_CIELO_PLENUM_NEGRO`, `UY_LUMINARIAS_ALERO` |
| `cubierta` | `04_CUBIERTA_INDUSTRIAL` | `UY_CUBIERTA_CHAPA`, `UY_CUBIERTA_NERVIOS_*`, `UY_RETENEDOR_PLACAS/OREJAS/TUBOS`, `UY_GOTERON_BORDE`, `UY_CUBIERTA_ANEXO` |
| `envolvente_general` | `02_ENVOLVENTE`, `03_CARPINTERIAS_M1` | testeros, anexo, ME-3 e interior. Llama a `fachada_aire` y a `testero_este` |
| `fachada_aire` | `02_ENVOLVENTE`, `03_CARPINTERIAS_M1`, `04_CUBIERTA_INDUSTRIAL` | `UY_FACHADA_AIRE_EJE_I`, `UY_PILASTRAS_AIRE`, `UY_BLOQUE_AIRE_*`, `UY_MARQUESINA_AIRE`, `UY_NICHO_AIRE*`, `UY_VESTIBULO_AIRE_*`, `UY_CARPINTERIAS_AIRE_*`, `UY_PUERTAS_AIRE_ACERO`, `UY_ENROLLABLES_AIRE_*`, `UY_INTERIOR_AIRE_*`, `UY_BAJANTE_OESTE` y `UY_GOTERON_LADO_AIRE` |
| `testero_este` | `02_ENVOLVENTE`, `03_CARPINTERIAS_M1` | `UY_TESTERO_EJE_20`, `UY_PATIO_ESTE_*` y `UY_PUERTAS_ESTE_*` |
| `elementos_laterales` | `02_ENVOLVENTE` | `UY_ROMBO_OESTE_*`, `UY_MASTIL_OESTE`, `UY_CAJA_EMBARQUE_OESTE*`, `UY_DESCANSO_ESCALONES_OESTE`, `UY_FRANJA_ESTE_*` |
| `celosias` | `05_CELOSIAS_CORTEN` | `UY_CELOSIA_<fachada>_<variante>_<n>` y `UY_CELOSIAS_BASTIDOR` |
| `letrero` | `02_ENVOLVENTE/LETRERO_HORIZONTE_UYUNI/LETRERO_A_SOBRESALE` y `.../LETRERO_B_CONTENIDO` | letras, reflejo, pirámides 3D, marcos, separadores y líneas de horizonte (sufijo `_A` o `_B`) |
| `entorno` | `06_ENTORNO_SITE` | Lado Tierra según la A111: `UY_VEREDA_TIERRA`, `UY_CORDON_TIERRA`, `UY_ZANJA_DRENAJE` y `UY_ZANJA_REJILLA`. Frente (`frente_lado_tierra`): `UY_CALZADA_ASFALTO` (calzada frontal, calles de los testeros, acceso y calle del eje 20), `UY_FRENTE_PLAZA_ASFALTO`, `UY_FRENTE_JARDINERAS_CORDON` / `_TIERRA`, `UY_FRENTE_ANILLOS_BLANCOS` / `_TIERRA`, `UY_FRENTE_CORDONES_AMARILLOS`, `UY_FRENTE_PLAZA_CORDONES`, `UY_FRENTE_ESPIGA_CORDONES`, `UY_FRENTE_ANDENES_BUS`, `UY_FRENTE_COLUMNAS_AMARILLAS`, `UY_FRENTE_PASOS_ME2`, `UY_SENALIZACION_VIAL` y `UY_SENALIZACION_VIAL_AMARILLA`. Llama a `entorno_aire`, `contexto_aeropuerto`, `terreno` y `paja_brava` |
| `entorno_aire` | `06_ENTORNO_SITE` | `UY_VEREDA_AIRE_OESTE/ESTE`, `UY_CORDON_AIRE_*`, `UY_PLATAFORMA_AIRE_HORMIGON`, `UY_CAMINO_SERVICIO_AIRE` y sus marcas, `UY_PLATAFORMA_MARCAS_AMARILLAS` |
| `contexto_aeropuerto` | `11_CONTEXTO_AEROPUERTO` | `UY_PISTA_13_31_ASFALTO`, `UY_CALLE_RODAJE_ASFALTO`, `UY_PISTA_MARCAS_BLANCAS`, `UY_PISTA_Y_RODAJE_MARCAS_AMARILLAS` y `UY_MANGA_VIENTO_*` |
| `terreno` | `06_ENTORNO_SITE` | `UY_SUELO_ALTIPLANO`: malla polar de 45 km con cerros, curvatura y el atributo `salar` |
| `paja_brava` | `11_CONTEXTO_AEROPUERTO` | `UY_PAJA_BRAVA_MATA` (la malla de una mata, oculta en el render) y `UY_PAJA_BRAVA_DISPERSION` (puntos con el modificador de Geometry Nodes `UY_GN_PAJA_BRAVA`) |
| `mangas_y_aviones` | `10_MANGAS_AERONAVES` | `UY_MANGAS_EMBARQUE`, `UY_MANGAS_FUELLES_Y_RUEDAS` y los dos 737-800 (`UY_AVION_737_<parte>_1` y `_2`, con mallas compartidas), con la librea de BoA en `UY_AVION_737_LIBREA_*` |
| `assets` | `07_ASSETS/PROXIES_COLOCACION` | 15 cajas de ubicación, ocultas en el render (ver 8.2) |
| `referencias_cad` | `_REF_CAD/*` | las vistas del CAD como planos de referencia, ocultos en el render |
| `camaras_y_dron` | `08_CAMERAS_LIGHTS` | 12 cámaras fijas (con `CAM_07_PROPUESTAS`, `CAM_07B_CAPTURA_CLIENTE`, `CAM_08_LADO_AIRE`, `CAM_09_MANGA_737` y `CAM_10_PISTA_HORIZONTE`), `CAM_DRON` con su objetivo `DRON_OBJETIVO` y `NORTE_VERDADERO`. Ven hasta 60 km, por los cerros |

- **`DATOS_GEOM`:** es un JSON incrustado con los contornos de las planchas PT1, PT2A, PT2B, PT2R y PT1R, las letras UYUNI y el letrero. Se extrajeron de las tramas del DXF y ya restan los calados. La PT1R son las planchas de la PT1 recortadas por la rampa del DXF del 4 de octubre. Son datos: no hace falta tocarlos.
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

> ⚠️ **Al volver a ejecutar el script, `limpiar()` borra todo lo que haya en sus colecciones** (`_REF_CAD` a `08_CAMERAS_LIGHTS`, `10_MANGAS_AERONAVES` y `11_CONTEXTO_AEROPUERTO`, más las de luz y nieve), elimina y recrea las escenas `UYUNI_CREPUSCULO` y `UYUNI_DIA_P2_SALAR_LITIO` y purga los datos huérfanos.
> - Para llevar los cambios del 3 de octubre a un `.blend` que ya tiene avance propio, **no hace falta regenerarlo**: usa `herramientas/aplicar_cambios_reunion.py` (ver `CAMBIOS_REUNION_3OCT.md`).
> - Cualquier cosa que se agregue **a mano** dentro de esas colecciones (por ejemplo, assets en `07_ASSETS`) se pierde.
> - Opción recomendada: agregar los assets **por código**. Se guardan en `01_blender/assets/` y una función nueva del script los importa (append o link) y los ubica, así todo sigue siendo regenerable.
> - Opción alternativa, si se colocan a mano: usar una colección propia (por ejemplo, `20_ASSETS_PROPIOS`), enlazarla en **las dos escenas** y no volver a ejecutar el script; o volver a enlazarla después de ejecutarlo:
>   ```python
>   for n in ("UYUNI_DIA", "UYUNI_DIA_P2_SALAR_LITIO", "UYUNI_CREPUSCULO"):
>       sc = bpy.data.scenes[n]
>       if "20_ASSETS_PROPIOS" not in sc.collection.children:
>           sc.collection.children.link(bpy.data.collections["20_ASSETS_PROPIOS"])
>   ```

## 8. Pendientes, con su especificación

### 8.1 Contexto y paisaje (fase 4.1)

**Atmósfera:** árida, de altura y fría (altiplano a 3667 m). La referencia es el concurso del Aeropuerto Pichoy de Mathias Klotz: sobria, elegante y con la arquitectura integrada al paisaje.

**Hoy (desde el 4 de octubre, noche; `CAMBIOS_4OCT_FACHADAS.md`, sección 11.3):**
- **Suelo:** una malla polar de 45 km de radio con material procedural, plana hasta 3,5 km. Su nieve se controla con la propiedad `nieve`.
- **Relieve:** curvatura de la Tierra y cordones de cerros aproximados (`CERROS`): la cordillera de Chichas al este, hasta ≈ 2,4° sobre el horizonte, y lomas al sur y al norte. Al oeste, el Salar plano y blanco desde 15 km.
- **Vegetación:** paja brava instanciada con Geometry Nodes (unas 22 000 matas) en manchas, fuera de lo pavimentado y de la franja de la pista. Las jardineras del frente son de tierra, como en el modelo del cliente. Con `CONTEXTO_IA = True` la dispersión no sale en el render.
- **Lejanía:** el color del suelo se aclara y se enfría con la distancia.

**Por hacer:**
- Textura PBR para el suelo cercano (tierra o grava clara), en lugar del ruido procedural.
- **El horizonte real:** los cerros son una aproximación. Para el real, se puede partir de un modelo de elevación (SRTM o Copernicus GLO-30) centrado en la latitud y longitud de la sección 3 y rotado con el norte local, y reemplazar la altura de `altura_terreno()`.
- Si un render muestra la paja brava muy repetida, sumar dos o tres mallas de mata distintas: la dispersión toma una sola, `UY_PAJA_BRAVA_MATA`.

### 8.2 Vehículos y personas (fases 4.2 y 4.3)

Hay que reemplazar los 15 proxies de `07_ASSETS/PROXIES_COLOCACION`. Sus posiciones también están en `inventario_escena.json`, en la clave `proxies_a_reemplazar`. Son cajas ocultas en el render que solo sirven de guía.

| Proxy | Tipo | Centro de la base X; Y; Z | Rotación Z | Tamaño L × A × H (m) |
|---|---|---|---|---|
| `UY_4x4_01` | vagoneta 4x4 en circulación, carril junto al cordón | 8,0; −10,163; −0,15 | 180° | 4,90 × 1,94 × 2,50 |
| `UY_4x4_02` | vagoneta 4x4 en la dársena 1 | 27,489; −7,363; −0,15 | 180° | 4,90 × 1,94 × 2,50 |
| `UY_4x4_03` | vagoneta 4x4 en circulación, carril exterior | 47,0; −13,663; −0,15 | 180° | 4,90 × 1,94 × 2,50 |
| `UY_4x4_04_ESTAC` | vagoneta 4x4 estacionada (fila 2) | 30,25; −31,913; −0,15 | 270° | 4,90 × 1,94 × 2,50 |
| `UY_4x4_05_ESTAC` | vagoneta 4x4 estacionada (fila 2) | 35,25; −31,913; −0,15 | 270° | 4,90 × 1,94 × 2,50 |
| `UY_MINIBUS_TRANSFER` | minibús de transfer en la dársena 2 | 69,474; −7,403; −0,15 | 180° | 6,40 × 2,05 × 2,55 |
| `UY_TURISTA_00` … `_08` | turistas en la vereda (dos, junto a la dársena 1) | ver el inventario (Z = 0,00) | — | 1,62–1,74 de alto |

Desde el 4 de octubre (noche) la calzada frontal tiene sentido hacia el eje 1: los vehículos que circulan miran hacia −X (rotación 180°).

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
| `CAM_08_LADO_AIRE` | DIA | Aérea desde la plataforma, como la vista del modelo del cliente: fachada del Lado Aire, mangas y aviones. |
| `CAM_09_MANGA_737` | DIA | La manga 1 con su 737 en primer plano y la fachada detrás. |
| `CAM_10_PISTA_HORIZONTE` | DIA | Aérea desde el oeste: la pista hasta el horizonte, el rodaje, los aviones y la terminal, con el Salar al fondo. |

**Antes de los renders finales:** aplicar las mejoras de fotorrealismo de `02_postproduccion/FOTORREALISMO_BLENDER.md`. Son, sobre todo, exposición medida con False Color (la escena estaba ≈ 0,7 EV sobreexpuesta) y verticales rectas con *shift*. Se probaron en CAM_01.

**Después, los materiales:** `02_postproduccion/MATERIALES_INTELIGENTES.md`. Máscaras procedurales (aristas, cavidades y gravedad) para el polvo fino del altiplano y la pátina del corten, metálico binario, variación pieza por pieza y receta para cada material, con el vidrio de control solar con capa fina. Se probaron en CAM_06, CAM_05 y CAM_01.

**Y la noche:** `02_postproduccion/ILUMINACION_NOCTURNA.md`. Emisores en Kelvin, luz práctica (la luminaria se ve y el Spot ilumina), interior con profundidad y exposición medida con False Color. Se probó en CAM_03.

**Los ajustes del render:** `02_postproduccion/MUESTREO_Y_RENDIMIENTO.md`. Qué ajustes pagan y cuáles no en esta escena (umbral de ruido, tope de muestras, rebotes, cáusticas, clamp, poligonaje) y cómo atraviesa la luz el vidrio. Se probó en CAM_07, CAM_05, CAM_03 y en una ventana de prueba.

**Resumen de todo:** `02_postproduccion/GUIA_REALISMO_FOTOGRAFICO.md`.

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
            "CAM_04_AEREA_GENERAL", "CAM_05_LETRERO_HORIZONTE", "CAM_06_DETALLE_CELOSIA", "CAM_08_LADO_AIRE",
            "CAM_09_MANGA_737", "CAM_10_PISTA_HORIZONTE"]:
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

### 8.7 Lado Aire: mangas, aeronaves y pista (pedido del 4 de octubre)

**Estado al 4 de octubre por la noche** (`CAMBIOS_4OCT_FACHADAS.md`, secciones 6, 7 y 11):
- **Hecho:**
  - dos mangas generadas por código, en las dos puertas de embarque del nivel 1P;
  - dos 737-800, también generados por código, con medidas reales y la **librea de BoA** (aproximada);
  - veredas, camino de servicio, plataforma y marcas de los puestos;
  - **pista 13/31 hasta el horizonte** con marcas OACI, calle de rodaje, punto de espera, manga de viento y el terreno con cerros y el Salar detrás;
  - `CAM_10_PISTA_HORIZONTE` para mostrarla.
- **Falta confirmar la distancia de la pista a la terminal** (hoy, 330 m supuestos; sección 3): `PISTA["y"]`.
- **Opcional:** cambiar los aviones por un asset con licencia, si se quiere más detalle en primeros planos. `avion_737_partes()` alcanza para las tomas generales.
- **Ajustes:**
  - posición de los aviones: `AVION_RUMBO`, `AVION_PUERTA_L1` y `PUERTA_DESDE_ROTONDA`;
  - medidas de las mangas: `MANGA`;
  - librea: `LIBREA_BOA` (colores, textos y su posición).

Lo que sigue es la especificación original del pedido, que se usó para modelarlo.

**Mangas de abordaje (puentes de embarque):**
- **Cantidad y posición:** las del modelo del cliente (captura de la reunión): dos mangas que salen de la fachada del Lado Aire hacia los puestos de estacionamiento. Confirmar las puertas con el alzado SO del DXF; si no está claro, preguntar.
- **Partes:**
  - rotonda fija junto al edificio, de ≈ 3,5 m de diámetro;
  - túnel telescópico de 2 o 3 tramos, de ≈ 2,8 m de ancho por ≈ 3 m de alto, con pendiente máxima de 1:12;
  - cabina en la puerta del avión: el umbral de la puerta del 737-800 queda a ≈ 2,7 m del piso;
  - columna de apoyo con tren de ruedas.
- **Materiales:** metal pintado blanco o gris claro, con bandas vidriadas. Se generan por código, como el resto del edificio.

**Aeronaves:**
- **Modelo:** Boeing 737-800, que es el que BoA opera en las rutas nacionales (también el 737-700). Medidas: 39,5 m de largo, 35,8 m de envergadura con *winglets* y 12,5 m de alto.
- **Cantidad y posición:** uno o dos, con la nariz hacia la manga.
- **Origen del modelo:** un asset con licencia que permita uso comercial (CC0 o CC-BY de Sketchfab, BlenderKit u otro), registrado en `CREDITOS.md`.
- **Librea:** la de BoA solo si el cliente confirma que se puede usar la marca; si no, una librea blanca genérica. Hay que preguntar.

**Pista y plataforma:**
- **Pista real:** 4000 × 45 m, asfalto, cabeceras 13/31, con balizamiento.
- **Orientación:** el eje largo del edificio (X local) apunta a un azimut de ≈ 301° (sección 3), así que la pista corre casi paralela a la fachada.
- **Posición:** se toma de OpenStreetMap o de Google Earth (`aeroway = runway`) y se pasa a coordenadas locales con la georreferencia de la sección 3.
- **Señalización según el Anexo 14 de la OACI:** umbrales con barras, designadores 13 y 31, eje discontinuo, zona de toma de contacto, punto de visada y bordes.
- **Calle de rodaje:** une la plataforma con la pista, con eje amarillo.
- **Plataforma:** marcas de los puestos en amarillo y líneas de seguridad.
- **Pista entera hasta el horizonte**, con el terreno del altiplano y los cerros detrás, para que CAM_04 y el dron no muestren el borde del suelo.

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
# 6. Verificación SIN render: geometría evaluada a .npz y láminas con matplotlib sobre los DXF del cliente
#    (la carpeta de los DXF es la de UYUNI_insumos_cliente.zip; el segundo paso necesita numpy, matplotlib y ezdxf)
python herramientas/exportar_geometria.py -- uyuni_v2.blend /tmp/geometria.npz
python herramientas/superponer_cad_2d.py /tmp/geometria.npz /ruta/a/los/dxf verificacion
```

Los pasos 2 y 3 renderizan. Cuando no haya que gastar en render, usa el 6: corta y proyecta la geometría del modelo y la dibuja sobre la planta A111 y los alzados del cliente, en menos de un minuto. También dibuja el sitio, la pista, el horizonte y los encuadres aproximados de CAM_10 y CAM_04 (`ENCUADRE_*`), que muestran qué entra en cuadro sin renderizar.

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
- **Geometry Nodes por código (paja brava):**
  - el nodo Random Value cambia sus entradas según `data_type`: primero se fija el tipo y después se buscan `Min` y `Max`;
  - la mata que se instancia puede estar oculta en el render (`hide_render`): el nodo Object Info la sigue leyendo como dependencia;
  - en `depsgraph.object_instances`, cada mata aparece como instancia con `parent` = el objeto de puntos. Un exportador que no las filtre escribe 22 000 mallas: `exportar_geometria.py` las salta y guarda solo los puntos.
- **Texto sobre una superficie curva (librea):** la curva de texto se pasa a malla con el depsgraph evaluado y se corta en franjas (`bmesh.ops.bisect_plane`) antes de proyectarla. Si no, sus triángulos grandes quedan como cuerdas y se meten dentro del fuselaje.
