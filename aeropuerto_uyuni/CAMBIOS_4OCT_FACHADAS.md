# Cambios del 4 de octubre (tarde y noche): Lado Aire, laterales, detalles y contexto

Las secciones 1 a 10 son los cambios de la tarde. La sección 11 recoge las respuestas del cliente de la noche y lo que se hizo con ellas: carpintería en negro mate, veredas del Lado Tierra según la A111, contexto del aeropuerto (calles, estacionamiento, pista, rodaje, terreno y paja brava) y librea de BoA.

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
- **Librea:** la de BoA desde la respuesta del cliente (sección 11.4). Antes era blanca genérica, sin marcas.
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
- **Plataforma:** de hormigón, en losas de 5 × 5 m (`mat_plataforma`). Desde la sección 11 llega hasta Y 130 (la calle de rodaje más 28 m) y va de X −110 a 200.
- **Marcas amarillas:** calle de rodaje en Y 102 y, en cada puesto, la guía y la barra de parada de la rueda de nariz. La calle de rodaje sigue hacia la pista (sección 11.3).
- **En el script:** `cordon_aire()`, `entorno_aire()` y `puestos_aviones()`.

## 8. Puntos que se consultaron al cliente

Respuestas de la noche del 4 de octubre:

| Punto | Respuesta | En el modelo |
|---|---|---|
| ME-6 del bloque (X 0,21–4,49): la planta la pone en la línea interior del eje I, detrás del muro macizo | "Está bien como le dejaste" | Sigue en la línea interior |
| Alturas del vestíbulo (+7,325; el alzado ESTE sugiere +6,91) y del anexo (+6,30; ESTE +6,21, SO +5,62) | "Déjalo como estaba por ahora" | Sin cambios |
| Mangas y aviones: puertas de embarque, orientación y librea | La orientación está bien; BoA tiene autorización | Librea de BoA (11.4) |
| Tubos del retenedor | Tres tubos de 1/2", según el dibujo | Ya estaba así: tres de 21,3 mm |
| Color de la carpintería (el detalle de la ME-2 dice "negro mate") | "Acércate al negro mate" | Negro mate (11.1) |
| Cordón del Lado Tierra (la A111 dibuja una vereda de ≈ 8,8 m con dos dársenas) | "Aplica las veredas y de paso realiza el modelado de más contexto" | Aplicado (11.2) y contexto nuevo (11.3) |

Siguen abiertos:
1. **Remate de la cubierta sobre el eje I:**
   - el modelo la corta al ras de las pilastras, como en el alzado ESTE;
   - el alzado SO dibuja líneas de cubierta a +7,33 y +7,51, y además marca la cumbrera a +13,43.
2. **Galería del bloque:**
   - el vano de 4,40 m hacia la pista se interpretó como una galería cubierta abierta, con un muro vidriado y una puerta doble hacia el recinto del bloque.
3. **Lo nuevo de la sección 11 que no está en los planos:** posición de la pista, calles, estacionamiento y librea (ver 11.6).

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
| `AVION_737_800_VISTAS.jpg` | El 737-800 con la librea de BoA: los dos lados, planta y frente |
| `LADO_TIERRA_PLANTA_VEREDAS.jpg`, `LADO_TIERRA_VEREDA_ESQUINA_OESTE.jpg`, `LADO_TIERRA_VEREDA_DARSENA_1.jpg` | Corte a −0,10 de veredas, cordones e islas (verde) con la A111 encima (rojo fino) |
| `LADO_TIERRA_PLANTA_SITIO.jpg` | Calzada, cantero, estacionamiento, anillo y acceso, en planta |
| `CONTEXTO_PLATAFORMA_RODAJE.jpg`, `CONTEXTO_AEROPUERTO_PLANTA.jpg`, `CONTEXTO_PISTA_CABECERAS.jpg` | Plataforma, rodaje, pista y sus marcas; la paja brava como puntos |
| `CONTEXTO_HORIZONTE.jpg` | Horizonte de cerros visto desde la terminal, con la dirección de cada cámara |
| `ENCUADRE_CAM_10_PISTA_HORIZONTE.jpg`, `ENCUADRE_CAM_04_AEREA_GENERAL.jpg` | Encuadre aproximado de esas cámaras, en perspectiva y sin render |

Las tres superposiciones de los alzados (`SUPERPOSICION_FACHADA_*`) ahora son proyecciones 2D: no están hechas con render. Las de la fachada NE y de los cortes siguen siendo las del 3 de octubre, hechas con render, y `lamina_verificacion_alzados.jpg` todavía muestra el Lado Aire anterior.

Los encuadres (`ENCUADRE_*`) tampoco son renders: son una proyección en perspectiva dibujada con matplotlib, sin luz, sombras ni cielo, y con orden de pintor (alguna cara grande puede quedar mal ordenada). Sirven para revisar qué entra en cuadro, no cómo se verá.

## 10. Cómo llevarlo a un `.blend` con avance propio

Estos cambios tocan la geometría de casi todo el edificio, así que no hay parche.
- **Recomendado:**
  1. regenerar desde `uyuni_modelo.py`;
  2. volver a enlazar las colecciones propias (TRASPASO.md, sección 7).
- **Se borran al regenerar:** los objetos dentro de las colecciones del script, incluidas las nuevas `10_MANGAS_AERONAVES` y `11_CONTEXTO_AEROPUERTO`.
- **`aplicar_cambios_reunion.py`:** ya conoce los nombres nuevos del retenedor, así que no lo duplica.
- **`aplicar_cambios_4oct.py`:** además de las decisiones de color de la mañana, pasa la carpintería a negro mate (sección 11.1) en un `.blend` existente. El resto de esta lista es geometría: se regenera.

## 11. Respuestas del cliente y contexto (noche del 4 de octubre)

### 11.1 Carpintería en negro mate

- **Color:** `PERFIL_COLOR` pasa de antracita `#3A3E41` a negro mate **`#2E2F31`** (≈ 0,027 de luminancia lineal: el negro más oscuro que en el render no se vuelve un hueco sin forma).
- **Acabado:** pintura en polvo mate: sin metálico (antes 0,25) y rugosidad 0,60 (`PERFIL_RUGOSIDAD`).
- **Alcance:**
  - perfiles de las mamparas, rombos ME-3, ventanas y cajas del Lado Aire;
  - puertas de acero, con el mismo acabado (`UY_PUERTA_ACERO_NEGRO_MATE`);
  - viga y operador de la ME-2, que antes usaban el sello negro.
- **Material:** `UY_ALUMINIO_NEGRO_MATE` (`mat_perfil()`), en lugar de `UY_ALUMINIO_ANTRACITA_MATE`. Las herramientas de prueba (`prueba_materiales.py`, `prueba_fotorrealismo.py`) usan el nombre nuevo.

### 11.2 Veredas del Lado Tierra según la A111

- **Cordón (capa A-FLOR, `cordon_tierra()`):**
  - línea general a Y −8,413: la vereda tiene ≈ 8,8 m desde el muro;
  - **dos dársenas** de ascenso y descenso (X 20,975–34,004 y 62,96–75,988): 2,10 m de fondo, tramo recto de 7,17 m y rampas a 45° con curvas de r 1,0 (`DARSENAS_TIERRA`, `DARSENA`);
  - esquina oeste: curva de r 4,021 y contracurva de r 1,0 hasta X 0,43; esquina este de r 1,0;
  - sigue en los cordones laterales (X −3,57 y 85,515) hasta el Lado Aire.
- **Vereda** (`UY_VEREDA_TIERRA`) de hormigón fratasado, con la **zanja** de drenaje y su rejilla a lo largo del alero (X −0,23 a 72,56).
- **Verificación:** el cordón del modelo coincide con el de la A111 con un desvío máximo de 1,0 cm (medio, 1,6 mm), por la discretización de los arcos.
- **Detalle:** el borde de cada vereda queda 1 cm dentro de su cordón, y el asfalto 5 cm por debajo de él. Así no hay caras coplanares (también en las veredas del Lado Aire).
- **Proxies:** las vagonetas y el minibús van en la calzada y en las dársenas; los turistas, en la vereda.
- **Cámaras:** cambia lo que se ve en CAM_01, CAM_03, CAM_05, CAM_06 y CAM_07. Ninguna se movió.

### 11.3 Contexto nuevo (no está en los planos del cliente)

Armado con la vista aérea del modelo del cliente y con los datos publicados del aeródromo.

**Calles y estacionamiento del Lado Tierra (`calzada_tierra()`, `islas_tierra()`, `senalizacion_tierra()`):**
- **Calzada frontal:** dos carriles (7,0 m) con sentido hacia el eje 1, para que el edificio quede a la derecha del conductor; línea de carril discontinua y trazos en la boca de cada dársena.
- **Cantero central:** 3,0 m, cortado por dos pasos peatonales tipo cebra frente a las dos ME-2.
- **Estacionamiento:** cuatro filas a 90° de 30 puestos de 2,50 × 5,00 (120 puestos), con pasillos de 6,0 m.
- **Islas:** de grava volcánica oscura con cordón de hormigón: las islas negras del modelo del cliente.
- **Anillo de 7,0 m alrededor del estacionamiento:**
  - por los testeros sube hasta la plataforma (las calles que unen el Lado Tierra con el Lado Aire en la vista aérea);
  - por el sur sale el **camino de acceso** hacia Uyuni (−X, 3 km);
  - eje amarillo discontinuo en los tramos de doble sentido y bordes blancos en el acceso.

**Pista, rodaje y plataforma (`contexto_aeropuerto()`, colección `11_CONTEXTO_AEROPUERTO`):**
- **Pista 13/31:** 4000 × 45 m de asfalto, con zonas de parada de 60 m con chevrones amarillos.
- **Marcas OACI:**
  - umbral de 12 franjas;
  - designación "31" y "13" en cifras de 9 m, legibles desde cada aproximación;
  - eje discontinuo;
  - punto de visada a 400 m;
  - zona de toma de contacto;
  - bordes de 0,90 m.
- **Posición:**
  - las cabeceras se pasaron de sus coordenadas publicadas a coordenadas locales con la georreferencia del IFC: X −1034,5 (cabecera 31) y X 2962,6 (cabecera 13);
  - la pista resulta **paralela al eje X**, como el edificio;
  - esa misma georreferencia la pone a ≈ 55 m del Lado Tierra, lo que no puede ser: el origen del IFC no está en el sitio real de la terminal;
  - se mantuvieron las X y la orientación, y el eje se puso del Lado Aire a una **distancia supuesta de 330 m** (`PISTA["y"]`). Así la plataforma queda fuera de la franja de 150 m, y las colas de los 737 y la cumbrera quedan bajo la superficie de transición 1:7.
- **Calle de rodaje:** de 23 m, de la plataforma a la pista en X 150, con curvas de enlace, eje amarillo que sale de la calle de rodaje de la plataforma, punto de espera a 90 m del eje de la pista y curvas de entrada a la pista en los dos sentidos.
- **Plataforma:** pasa a X −110..200 e Y 40..130 (antes −160..260 y 40..175).
- **Manga de viento** junto a la pista, naranja y blanca.

**Terreno (`terreno()`):**
- el plano de 4 × 4 km pasa a una malla polar de **45 km de radio**, plana hasta 3,5 km;
- más allá, la curvatura de la Tierra (con refracción) y **cordones de cerros** (`CERROS`): la cordillera de Chichas al este (hasta ≈ 2,4° sobre el horizonte) y lomas al sur y al norte;
- al oeste y noroeste, el **Salar de Uyuni** desde 15 km: plano y blanco (atributo `salar` de la malla, que lee `mat_suelo`). Desde una cámara alta se ve como franja blanca en el horizonte;
- `mat_suelo` aclara y enfría el color con la distancia (perspectiva aérea aproximada);
- la lámina `CONTEXTO_HORIZONTE.jpg` muestra el horizonte por azimut y hacia dónde mira cada cámara;
- las cámaras ven hasta 60 km (`clip_end`).

**Paja brava (`paja_brava()`):**
- matas de 0,3 a 0,8 m (*Festuca orthophylla*), en manchas, en el suelo libre hasta 650 m del edificio. No van en calles, veredas, plataforma ni rodaje, ni en la franja de 75 m a cada lado del eje de la pista;
- más densas en las islas del estacionamiento y en el cantero;
- son 21 981 instancias de Geometry Nodes de una sola malla (`UY_PAJA_BRAVA_MATA`, oculta en el render), sobre los puntos de `UY_PAJA_BRAVA_DISPERSION`: casi no pesan en memoria.

### 11.4 Librea de BoA en los dos 737-800

El cliente confirmó que BoA tiene autorización. No hubo referencia gráfica de la librea: es una aproximación.
- fuselaje blanco;
- **deriva y winglets en azul BoA** `#1C3F94`;
- **tres franjas rojo, amarillo y verde** (los colores de la bandera) que cruzan la deriva en diagonal, como una cola de ave en vuelo;
- **"BoA"** en azul sobre las ventanillas delanteras, de 1,10 m de alto, y "Boliviana de Aviación" debajo de ellas, en los dos lados y legibles desde cada uno.

En el script:
- `LIBREA_BOA`, `franjas_deriva()`, `texto_fuselaje()` y `piel_deriva()`;
- la deriva se arma con estaciones cada ≈ 0,6 m (`estaciones_deriva()`), para que la librea, a 6 mm de la piel, quede siempre por fuera.

### 11.5 Cámara nueva

- **`CAM_10_PISTA_HORIZONTE`:** aérea desde el oeste, a 90 m sobre el borde de la pista, con lente de 30 mm.
  - la pista nace abajo a la izquierda y llega al horizonte;
  - la calle de rodaje lleva a la plataforma;
  - los dos 737 y la terminal quedan a la derecha;
  - al fondo (mira al noroeste) queda el Salar.
- Sin renderizar: se revisó con `ENCUADRE_CAM_10_PISTA_HORIZONTE.jpg`.

### 11.6 Para confirmar con el cliente

1. **Distancia de la pista a la terminal:**
   - se supuso 330 m entre la fachada y el eje de la pista;
   - con un plano de sitio o la distancia real, se corrige con un solo parámetro (`PISTA["y"]`);
   - también confirmar en qué tramo de la pista queda la terminal: con la georreferencia del IFC, a 1 km de la cabecera 31.
2. **Calles, estacionamiento y acceso:** son una propuesta de contexto, no un diseño. Si hay un plano de urbanización o de accesos, se reemplazan.
3. **Cerco perimetral:** no se modeló. Las calles de los testeros llegan a la plataforma sin portón, como en la vista aérea del cliente. ¿Dónde va el límite del Lado Aire?
4. **Librea:** con una foto o el manual de marca de BoA, se ajustan los colores, el logo de la deriva y la tipografía del nombre.
