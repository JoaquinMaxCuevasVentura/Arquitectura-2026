# Banco de escritura

**Entregable E1 de *A pulso* · diseño v1 · octubre de 2026**

El banco es la parte arquitectónica del proyecto: un puesto de escritura a escala del cuerpo cuyas configuraciones son las condiciones de ensayo. El diseño responde a una sola regla: **cambiar una variable a la vez sin cambiar nada más**. Por eso todo el banco gira en torno a una pieza que no cambia, el tablero, y la hoja ocupa siempre el mismo lugar sobre él.

## Un tablero, tres apoyos

| Plano | Apoyo | Qué cambia en el cuerpo |
|---|---|---|
| **B0 · horizontal** | El tablero descansa plano sobre una mesa, sobre sus dos listones | El gesto ocurre en el plano de la mesa; el antebrazo puede apoyarse en la zona inferior del tablero |
| **B1 · 45°** | El tablero se apoya en el atril: sus listones sobre las hipotenusas de dos cartelas y el listón inferior contra un tope | El antebrazo descansa en la pendiente; la mano queda más alta que el codo |
| **B2 · vertical** | El listón superior del tablero queda atrapado entre dos pares de pasadores en los montantes del muro | De pie; el gesto se hace contra la gravedad y con el hombro |

El tablero lleva dos listones en el dorso, a 20 mm de los bordes superior e inferior. Esos listones son los únicos puntos de apoyo en las tres posiciones: en la mesa lo elevan 18 mm, en el atril descansan sobre las cartelas y en el muro el superior se aloja entre los pasadores. Sobre la cara de escritura no hay tornillos ni marcas, salvo las cuatro esquinas de la hoja.

**La hoja va siempre en el mismo lugar:** A3 apaisada, centrada en el ancho, con su centro a 200 mm del borde superior del tablero. Debajo queda una franja de unos 250 mm para el antebrazo. Así, entre B0, B1 y B2 solo cambia la orientación y la altura del plano, no la relación entre la hoja y el tablero.

## Alturas referidas al cuerpo

Las alturas no se fijan en centímetros absolutos sino respecto de quien escribe, para que una condición sea la misma en cuerpos distintos (ver la calculadora `instrumento/banco.html` y la lámina B-05):

| Plano | Criterio del proyecto | Qué se ajusta |
|---|---|---|
| B0 | El codo queda 30 mm por encima del plano de escritura, con el antebrazo apoyado | Altura del asiento (o de la mesa) |
| B1 | El codo queda 20 mm por encima del borde inferior del tablero inclinado | Altura del asiento |
| B2 | El centro de la hoja queda a la altura del hombro, de pie | Agujero de los pasadores (pasos de 25 mm; error ≤ 12 mm) |

Son criterios de diseño, no normas ergonómicas: se eligieron para que cada posición sea cómoda y repetible. Si al probarlos en la maqueta resultan forzados, se cambian **antes** de la serie y se anota el cambio en el protocolo.

Medidas que hay que tomar a cada persona (hoja «Medidas y montaje»): codo sobre el asiento, hombro de pie y codo a punta de los dedos, además de la altura de la mesa y del asiento usados.

## Las otras variables en el mismo banco

| Variable | Cómo se arma sobre el tablero |
|---|---|
| **A · Apoyo** | A0: el antebrazo descansa en el tablero, debajo de la hoja. A1: solo el canto de la mano toca el papel (variante: la mano sobre el tiento). A2: nada toca el tablero salvo la herramienta. La condición se verifica en el video lateral. |
| **C · Límite** | Plantillas de MDF de 5 mm cortadas con láser (`plantillas/`), que se apoyan sobre la hoja con los agujeros sobre las marcas de registro y se sujetan con dos prensas en los bordes del tablero. C1: canal entre la línea base y la altura x. C2: canal de 0,75 h desde la línea base. C3: ventana de 0,6 h de ancho por celda. Cada plantilla corresponde a un código de pauta. |
| **D · Resistencia** | D0: la hoja directamente sobre el tablero. D1: cuatro hojas de lija de grano 150 unidas por detrás con cinta, bajo la hoja. D2: goma eva de 3–5 mm bajo la hoja. D3 (opcional, tardía): incisión sobre arcilla o cera. |

## Piezas y materiales

Todo sale de **medio tablero de terciado o multilaminado de 18 mm (1220 × 1220)**. El despiece está en la lámina B-04.

| N.º | Pieza | Cant. | Medidas (mm) |
|---|---|---|---|
| 1 | Tablero de escritura | 1 | 600 × 600 × 18 |
| 2 | Listón del tablero | 2 | 600 × 42 × 18 |
| 3 | Cartela del atril (triángulo rectángulo, despuntado 30) | 2 | catetos 460 |
| 4 | Travesaño del atril | 2 | 564 × 70 × 18 |
| 5 | Tope transversal | 1 | 600 × 30 × 18 |
| 6 | Montante de muro | 2 | 90 × 750 × 18 |

**Herrajes y otros:** 4 pasadores de varilla lisa de acero Ø8 × 32; 6 tarugos Ø8 y 6 tornillos 5 × 60; unos 30 tornillos 4 × 30 y cola vinílica; 4 prensas pequeñas; varilla de madera Ø15 × 600 con punta de espuma forrada (tiento); MDF de 5 mm para las plantillas; lija de grano 150; goma eva de 3–5 mm; cinta de papel; fieltro antideslizante; inclinómetro (aplicación del teléfono).

## Armado

1. **Tablero.** Lijar la cara de escritura (grano 180) y sellarla con un acabado mate. Pegar y atornillar los dos listones en el dorso, a 20 mm de los bordes, con los tornillos desde los listones: ninguno atraviesa la cara. Marcar las cuatro esquinas de la hoja A3 (centro a 200 mm del borde superior, centrada en el ancho).
2. **Atril.** Cortar en diagonal un cuadrado de 460 × 460 para obtener las dos cartelas, con un corte recto y limpio porque esa es la superficie de apoyo. Despuntar 30 mm el vértice agudo. Unir las cartelas con el travesaño trasero (abajo) y, si hace falta rigidez, con el superior. Atornillar el tope transversal sobre las hipotenusas, en el extremo bajo. Pegar fieltro bajo las cartelas. **Verificar 45° ± 1°** con el inclinómetro sobre la cara del tablero apoyado.
3. **Montantes.** Perforar en cada uno 27 agujeros Ø8,5 de 15 mm de profundidad, cada 25 mm sobre el eje, empezando a 50 mm del borde inferior; numerarlos con lápiz cada cinco. Fijarlos al muro a plomo, con 420 mm entre ejes y el borde inferior a 1250 mm del piso. Con eso se cubren hombros entre unos 1170 y 1770 mm. Si no se puede perforar el muro, atornillarlos a un tablero de 600 × 1200 apoyado en el muro y trabado en el piso.
4. **Para colgar el tablero (B2):** dos pasadores de apoyo en el agujero que indica la calculadora y dos de traba dos agujeros más arriba. Los pasadores sobresalen 17 mm, menos que el espesor del listón, y no tocan el dorso del tablero. El listón de 42 mm queda justo entre ellos (4 + 42 + 4 = 50 = dos pasos), así que el tablero no se levanta con los trazos ascendentes.

## Antes de la madera: maqueta de cartón (F0)

La propuesta pide una maqueta a escala real antes de construir. Con cartón corrugado doble y cinta de embalar:

- un tablero de 600 × 600 con dos tiras de cartón plegado como listones;
- un atril de dos triángulos de 460 mm unidos por una tira, con una regla pegada como tope;
- para B2, la hoja pegada directamente en el muro, con su centro a la altura del hombro.

La maqueta sirve para el piloto (Anexo A de la propuesta) y para comprobar en el cuerpo los tres criterios de altura. Lo que se aprenda (por ejemplo, que la franja del antebrazo es corta en B1) se corrige en este documento antes de cortar madera.

## Verificaciones antes de cada sesión

- El tablero no se mueve: está apoyado en sus dos listones o trabado entre los pasadores.
- B1: la inclinación medida es de 45° ± 1° y se anota en la ficha.
- La hoja está en sus marcas y fijada con cinta en los cuatro bordes.
- C: la plantilla está sobre las marcas y sujeta con dos prensas.
- D: la base (lija o goma eva) cubre toda el área de la pauta y está fija por detrás.
- La altura del asiento o el agujero de los pasadores coincide con la hoja de medidas de la persona.

## Archivos

- `planos/B-01_tablero.svg` … `B-05_posiciones.svg`: láminas A3 en SVG. Los mismos planos están reunidos en `Banco de escritura - planos.pdf`.
- `plantillas/topes_C*_<pauta>.svg`: archivos de corte láser a escala 1:1 para las pautas del piloto y de la serie. Las plantillas de otras pautas se descargan desde `instrumento/pautas.html`.
- Los planos se generan con `instrumento/herramientas/generar_planos.js` a partir de las medidas de `instrumento/lib/banco.js`. Si una medida cambia, se cambia allí y se regeneran los planos, la calculadora y este documento.
