# Cambios del 4 de octubre (tarde): Lado Aire, laterales y detalles

**Insumos nuevos del cliente:**
- DXF de la planta baja (A111), de la fachada SUROESTE (Lado Aire), de las fachadas ESTE y OESTE y del detalle de las puertas ME-2;
- dos capturas con el detalle del retenedor de nieve;
- dos capturas del modelo del cliente con las mangas y los aviones (vista aérea y acercamiento).

Los DXF no van en el repositorio (es público): se suman a `UYUNI_insumos_cliente.zip`.

**Sin renders:** el cliente pidió no gastar en pruebas de render. Todo se verificó dibujando el modelo sobre los DXF con matplotlib: cortes y proyecciones ortogonales, nada de Cycles ni EEVEE.
- Las láminas están en `01_blender/verificacion/` (sección 9).
- Las herramientas son `herramientas/exportar_geometria.py` y `herramientas/superponer_cad_2d.py`.

## 1. Fachada principal (Lado Tierra): nicho solo en los ventanales

- Solo los vanos con mampara ME-1 o ME-2 conservan el nicho: su paño sigue retirado 0,70 m, en el plano del muro.
- Los demás paños van **al ras de la cara de las columnas** (Y −0,308):
  - los ciegos;
  - los de los rombos ME-3;
  - los que quedan detrás de las celosías;
  - los del anexo.
- **Altura del paño al ras:** sube hasta el plenum del cielo del alero (+6,815). En el anexo, hasta su cubierta.
- **Rombos ME-3:** pasan al plano del paño que los contiene.
- **Testeros:** los dos arrancan en la cara de las columnas, como en los alzados laterales. Entre esa cara y el muro, el del eje 1 sube solo hasta el retorno del antepecho, para no compartir caras con él.
- **En el script:** `vano_con_nicho()`, `y_muro_ne()` y `muro_landside()`.
- **Cámaras:** cambia lo que se ve en CAM_01, CAM_03, CAM_06 y CAM_07, sobre todo en los extremos y en los vanos ciegos de los ejes 6-7, 10-11 y 15-17.

## 2. Puertas ME-2 según su detalle

- **Hojas corredizas:** las dos hojas automáticas, de DVH con marco delgado, corren **por el lado interior del perfil de 170 mm**, cerradas y solapadas con los montantes.
  - Antes iban 10 cm por delante del plano del vidrio. Por esa rendija se veía la luz interior (la línea naranja que marcó el cliente).
- **Viga y operador:**
  - viga de acero negro mate de 170 × 200 mm, de +2,44 a +2,64, en todo el ancho;
  - el operador de la puerta automática va debajo, de +2,32 a +2,44, del lado interior.
- **Montantes y paños fijos:**
  - el montante central existe solo sobre la viga;
  - los fijos laterales llegan hasta +2,40 y los de arriba arrancan en +2,44;
  - en el vano de la puerta no hay umbral ni vidrio exterior.
- **En el script:** `ME2_PUERTA` y `mamparas()` (`unidad_me2`).
- **Verificación:** `ME2_CORTE_HORIZONTAL.jpg` y `ME2_CORTE_VERTICAL.jpg`, superpuestos a las secciones 1 y 2 del detalle.

## 3. Retenedor de nieve según el detalle

- **Abrazadera:**
  - chapa de 6 mm, de 174 mm de alto y 113 mm de base, con la cabeza redondeada;
  - va perpendicular a la chapa y en el plano del nervio;
  - lleva dos orejas de 38 mm que muerden el nervio, con su perno.
- **Tubos:** tres agujeros de 23 mm, con los centros a 48,5, 92,5 y 137,5 mm de la base, y un tubo por agujero.
- **Posición:** el eje queda a **1,398 m del borde de la cubierta, medido sobre la pendiente**, encima de la primera correa y casi sobre la línea de las columnas. Las abrazaderas van cada dos nervios (0,60 m).
- **Nieve del crepúsculo:** una capa fina hasta el retenedor y, pendiente arriba, la nieve que el retenedor sostiene, apoyada contra su tubo inferior.
- **En el script:** `RETENEDOR`, `retenedor_marco()`, `retenedor_nieve()` y `nieve_crepusculo()`.
- **Verificación:** `RETENEDOR_NIEVE_CORTE.jpg`.

## 4. Fachada Lado Aire (SUROESTE)

**Coordenadas:**
- La planta A111 está en las coordenadas del modelo (1:1).
- El alzado SO va corrido 2,6 cm respecto de la planta y del IFC: X = 187,866 − x. Todo se modeló con las X de la planta.

**Lo que corrige el DXF:**
- **Solo el bloque de los ejes 1-5 llega al eje R**, con la cara a 48,601.
- **Entre los ejes 5 y 17**, la fachada es el muro del eje I:
  - cara a 43,872, panel de 0,16 m;
  - pilastras de las columnas C40×100, de 0,46 m, hasta 44,572 y +7,01;
  - buñas de las vigas de borde a +3,26, +3,76, +6,51 y +7,01.
- **Cubierta:** entre los ejes 5 y 17 termina al ras de las pilastras (alzado ESTE: +8,47 en Y 44,54), con un remate. Sobre el bloque sigue el perfil completo.

**Carpinterías y puertas (X de la planta):**
- **ME-4:** cuatro, de dos paños, de +4,82 a +6,51.
- **ME-5:**
  - dos altas, de tres paños, de +3,76 a +6,51;
  - una baja, de 0 a +2,66.
- **ME-6:** corrediza de 38,659 a 42,94, con fijos de 1,103 m y dos hojas que corren por dentro.
- **Enrollables:** cinco puertas de chapa galvanizada de 1,60 m de alto (PR-11 y PR-10).
- **P-01:** puerta batiente de 1,00 × 2,10.

**Volúmenes:**
- **Nicho de entrada** entre los ejes 7 y 8 (X 29,03–30,23, 1,2 m de fondo), con la puerta en su costado este.
- **Marquesina de hormigón** entre los ejes 5 y 7, según el IFC: losa a +3,65..+3,70, viga de borde, dos vigas laterales y viguetas V10x25 cada 0,50 m.
- **Vestíbulo de los ejes 10-11** (X 42,97–48,23, hasta Y 46,894 y +7,325), de dos niveles:
  - abajo, la losa del IFC a +3,70 y la puerta corrediza de su costado oeste;
  - arriba, la **puerta de embarque 2**, un frente vidriado de 2,00 × 2,30 con travesaño a +5,90.
- **Bloque del eje R:**
  - un **vano libre** de 9,80 a 14,20, hasta +3,26, a una galería cubierta. Al fondo de la galería está la ME-5 del muro del eje I;
  - una **abertura con antepecho** de 0,40, de 14,50 a 17,84;
  - un **muro vidriado con puerta doble** en X 8,0;
  - la **caja de la puerta de embarque 1** (X 0,83–2,83), que sobresale 1,91 m hacia la pista, con el mismo frente vidriado.

**Detalles e interior:**
- **Bajante** con abrazaderas en la esquina del eje 1, como dibujan los alzados SO y OESTE. Es el punto abierto 4 anterior.
- **Interior básico detrás de la fachada:**
  - piso;
  - losa del 1P a +3,85;
  - fondo y cielo cálidos (`luz_interior`), igual que en el Lado Tierra.

**Anexo (ejes 18-20):**
- Su muro hacia la pista va en Y 43,624, como en la planta. Antes estaba en 44,54.
- Las PT2 del Lado Aire van en el plano 43,88, delante del muro.

**En el script:**
- parámetros desde `Y_FACHADA_AIRE` hasta `BAJANTE_OESTE`;
- funciones `fachada_aire()`, `ventana()`, `corrediza()`, `enrollable()`, `puerta_batiente()`, `rejilla()` y `vidriado_embarque()`.

## 5. Fachadas ESTE y OESTE

**OESTE (testero del eje 1):** el DXF nuevo solo cambia esto respecto del anterior:
- suma **dos PT1 y un módulo en rampa**: la celosía cubre de Y −0,579 a 24,421;
- **módulo en rampa (`PT1R`):** tope a 6,0 m en el primer metro y bajada a 45° hasta 2,0 m. Son las planchas de la PT1 recortadas por ese contorno;
- **apoyo:** las celosías de la OESTE apoyan a +0,11 (`Z_CELOSIA_FACHADA`).

**ESTE (testero del eje 20):** ya estaba en el DXF anterior, pero no se había modelado (punto abierto 1):
- **puertas dobles:** tres, de 1,85 m, con rejilla de ventilación encima, de +2,07 a +2,85. Dos quedan detrás de las PT2;
- **puerta simple:** una, con rejilla de +2,02 a +2,31;
- **patio techado:** su boca son dos vanos de 3,21 m de alto, a los lados de la columna del eje E. El fondo está retirado hasta X 77,90; lleva una puerta al fondo y otra en el costado norte.
- **En el script:** `PUERTAS_DOBLES_ESTE`, `PUERTAS_SIMPLES_ESTE`, `PATIO_ESTE` y `testero_este()`.

## 6. Mangas y aeronaves

**Puertas de embarque:**
- Las dos "cajas vidriadas" del alzado SO están a la misma altura (+3,82 a +6,12) y tienen el mismo ancho (2,00 m). Son las **puertas de embarque del nivel 1P (+3,85)**:
  - una en la caja del bloque del eje 1;
  - otra en el vestíbulo de los ejes 10-11.
- Quedan a 45 m una de otra: alcanza para dos 737-800 sin choque de alas.

**Mangas (`manga_embarque()`):**
- pasarela fija desde la puerta;
- rotonda de 3,6 m sobre columna, en Y 52,6, antes del camino de servicio;
- túnel telescópico de dos tramos (2,50 × 3,00 y 2,75 × 3,25), con pendiente de +3,85 a +2,55 (1:11);
- columna de traslación con tren de ruedas;
- cabina con fuelle, girada hacia la puerta L1 del avión.

**Aeronaves (`avion_737_partes()`):**
- **Modelo:** dos Boeing 737-800 generados por código, con las medidas reales: 39,45 m de largo, 35,7 m de envergadura con winglets y 12,55 m de alto.
- **Partes:** fuselaje, alas con flecha y diedro, winglets, motores CFM56 con pilón, estabilizadores, tren, ventanillas y puesto de pilotaje.
- **Librea:** blanca genérica, sin marcas.
- **Mallas:** los dos aviones las comparten.

**Estacionamiento:**
- Como en la captura del cliente: casi paralelos a la fachada, con la nariz hacia el eje 1, 20° hacia el edificio (`AVION_RUMBO`).
- La puerta L1 de cada avión queda en la cabina de su manga (`PUERTA_DESDE_ROTONDA`).

**Cámaras nuevas, sin renderizar:**
- `CAM_08_LADO_AIRE`: aérea desde la plataforma, como la vista del cliente;
- `CAM_09_MANGA_737`: la manga 1 con su avión en primer plano.

## 7. Entorno del Lado Aire

- **Veredas y cordón según la planta A111 (capa A-FLOR):**
  - lateral oeste hasta X −3,57;
  - frente del bloque hasta 50,779;
  - bajo la marquesina hasta 46,779, con la dársena a nivel de calzada;
  - a lo largo de la fachada hasta 49,079;
  - lateral este hasta 85,515;
  - esquinas de radio 1 m.
- **Camino de servicio de asfalto** (la banda azul de la vista aérea): entre Y 55 y 65, con bordes continuos y eje discontinuo blancos.
- **Plataforma:** de hormigón, en losas de 5 × 5 m (`mat_plataforma`).
- **Marcas amarillas:** calle de rodaje en Y 102 y, en cada puesto, la guía y la barra de parada de la rueda de nariz.
- **En el script:** `cordon_aire()`, `entorno_aire()` y `puestos_aviones()`.

## 8. Para confirmar con el cliente

1. **ME-6 del bloque (X 0,21–4,49):**
   - el alzado SO la dibuja;
   - la planta la pone en la línea interior del eje I, detrás del muro macizo del eje R. Así se modeló, por eso no se ve.
   - ¿Va en la cara exterior?
2. **Altura del vestíbulo:**
   - se usó +7,325, como en el alzado SO;
   - el alzado ESTE sugiere +6,91;
   - el IFC solo trae la losa a +3,70.
3. **Remate de la cubierta sobre el eje I:**
   - el modelo la corta al ras de las pilastras, como en el alzado ESTE;
   - el alzado SO dibuja líneas de cubierta a +7,33 y +7,51, y además marca la cumbrera a +13,43.
4. **Altura del anexo:** el modelo usa +6,30; el alzado ESTE da +6,21 y el SO, +5,62.
5. **Mangas y aviones:**
   - ¿son esas las dos puertas de embarque?
   - ¿la orientación y la posición de los aviones están bien?
   - **Librea:** ¿BoA? Solo con autorización para usar la marca.
6. **Tubos del retenedor:**
   - se usaron tres tubos de 21,3 mm (1/2");
   - en la reunión se habló de un doble tubo de 1", pero un tubo de 1" (25,4 mm) no entra en el agujero de 23 mm del detalle;
   - ¿tres tubos o dos?
7. **Color de la carpintería:**
   - el detalle de la ME-2 dice "aluminio negro mate";
   - el modelo usa antracita mate `#3A3E41`, por la decisión del 3 de octubre.
8. **Cordón del Lado Tierra:**
   - la planta A111 dibuja una vereda de ≈ 8,8 m con dos dársenas;
   - el modelo mantiene la de 4,0 m del corte, la de los renders aprobados.
   - Cambiarla afecta CAM_01, CAM_03 y CAM_07: ¿se aplica?
9. **Galería del bloque:**
   - el vano de 4,40 m hacia la pista se interpretó como una galería cubierta abierta, con un muro vidriado y una puerta doble hacia el recinto del bloque.

## 9. Láminas de verificación (`01_blender/verificacion/`)

| Lámina | Qué muestra |
|---|---|
| `LADO_AIRE_PLANTA_CORTE.jpg`, `..._BLOQUE_MARQUESINA.jpg`, `..._VESTIBULO_ANEXO.jpg` | Corte del modelo a +1,00 (negro) y veredas y cordón (verde) sobre la A111 (rojo) |
| `SUPERPOSICION_FACHADA_SUROESTE.jpg` y `LADO_AIRE_ALZADO_SO_*.jpg` | Alzado SO del modelo con el del cliente en rojo |
| `SUPERPOSICION_FACHADA_ESTE.jpg` y `SUPERPOSICION_FACHADA_OESTE.jpg` | Testeros con el DXF nuevo |
| `LADO_TIERRA_NICHOS_CORTE.jpg` | Corte a +1,50 de la fachada principal: paños al ras y nichos |
| `ME2_CORTE_HORIZONTAL.jpg` y `ME2_CORTE_VERTICAL.jpg` | Puerta ME-2 sobre su detalle |
| `RETENEDOR_NIEVE_CORTE.jpg` | Corte por una abrazadera del retenedor |
| `LADO_AIRE_PLANTA_GENERAL.jpg` y `LADO_AIRE_PISO.jpg` | Mangas, aviones, camino de servicio y marcas en planta |
| `AVION_737_800_VISTAS.jpg` | El 737-800 generado: lateral, planta y frente |

Las tres superposiciones de los alzados (`SUPERPOSICION_FACHADA_*`) ahora son proyecciones 2D: no están hechas con render. Las de la fachada NE y de los cortes siguen siendo las del 3 de octubre, hechas con render, y `lamina_verificacion_alzados.jpg` todavía muestra el Lado Aire anterior.

## 10. Cómo llevarlo a un `.blend` con avance propio

Estos cambios tocan la geometría de casi todo el edificio, así que no hay parche.
- **Recomendado:**
  1. regenerar desde `uyuni_modelo.py`;
  2. volver a enlazar las colecciones propias (TRASPASO.md, sección 7).
- **Se borran al regenerar:** los objetos dentro de las colecciones del script, incluida la nueva `10_MANGAS_AERONAVES`.
- **`aplicar_cambios_reunion.py`:** ya conoce los nombres nuevos del retenedor, así que no lo duplica.
