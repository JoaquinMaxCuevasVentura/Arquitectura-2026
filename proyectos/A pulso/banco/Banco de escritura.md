# Banco de escritura: el tablero reconstruido

**Entregable E1 de *A pulso* · diseño v2 · octubre de 2026**

El banco es la parte arquitectónica del proyecto: un tablero de dibujo reconstruido para que cada uno de sus instrumentos pueda quitarse, cambiarse o exagerarse. Responde a una sola regla: **cambiar una variable a la vez sin cambiar nada más**. Por eso todo gira en torno a una pieza que no cambia, el tablero, y la hoja ocupa siempre el mismo lugar sobre él.

## Un tablero, cuatro apoyos

| Plano | Apoyo | Qué representa | Qué cambia en el cuerpo |
|---|---|---|---|
| **B0 · 15°** (base) | Cuña: dos cartelas de 600 × 161 con tope | El tablero de dibujo del estudiante y del dibujante | Sentado; el antebrazo descansa en el tablero |
| **B1 · horizontal** | Los dos listones sobre la mesa | La mesa de la generación CAD, donde se anota sobre un plano impreso | El gesto ocurre en el plano de la mesa |
| **B2 · vertical** | El listón superior trabado entre pasadores en dos montantes del muro | La pizarra del docente que demuestra la letra | De pie; el gesto pasa al hombro y va contra la gravedad |
| **B3 · 45°** (opcional) | Atril: dos cartelas de 460 × 460 con tope | El extremo del plano inclinado | La mano queda muy por encima del codo |

El tablero lleva dos listones en el dorso, a 20 mm de los bordes superior e inferior. Son los únicos puntos de apoyo en las cuatro posiciones. **Sobre la cara de escritura no hay tornillos ni marcas**, salvo las esquinas de la hoja. **El canto izquierdo debe quedar recto y liso**, porque sobre él corre la regla T.

**La hoja va siempre en el mismo lugar:** centrada en el ancho, con su centro a 200 mm del borde superior del tablero. Las pautas del proyecto son A4. Debajo queda una franja de unos 250 mm para el antebrazo.

**El ángulo de B0** es de 15° por defecto. Si las entrevistas de oficio muestran que los arquitectos formados en tablero usaban otro ángulo de forma habitual, se cambia el cateto vertical de la cuña (cateto = 600 × tangente del ángulo) antes de la serie.

## Alturas referidas al cuerpo

Las alturas se fijan respecto de quien escribe, para que una condición sea la misma en cuerpos distintos (calculadora `instrumento/banco.html`, lámina B-06):

| Plano | Criterio del proyecto | Qué se ajusta |
|---|---|---|
| B0 · 15° | El codo queda 30 mm por encima del borde inferior del tablero, con el antebrazo apoyado | Altura del asiento |
| B1 · mesa | El codo queda 30 mm por encima del plano | Altura del asiento |
| B2 · pizarra | El centro de la hoja queda a la altura del hombro, de pie | Agujero de los pasadores (pasos de 25 mm; error ≤ 12 mm) |
| B3 · 45° | El codo queda 20 mm por encima del borde inferior del tablero | Altura del asiento |

Son criterios de diseño, no normas ergonómicas. Si al probarlos en la maqueta resultan forzados, se cambian **antes** de la serie y se anota el cambio en el protocolo.

## Los instrumentos sobre el tablero

| Variable | Cómo se arma |
|---|---|
| **A · Apoyo** | A0: el antebrazo descansa en el tablero, debajo de la hoja. A1: solo el canto de la mano toca el papel. A2: nada toca el tablero salvo la herramienta. Se verifica en el video lateral |
| **C · Guía** | C0: pauta con líneas guía, a pulso. C1: pauta sin líneas guía (esquinas de celda y barra de referencia). C2: regla T de 60 cm sobre el canto izquierdo y escuadra sobre ella; los rectos se trazan contra el instrumento. C3: plantilla de rotulación ISO 3098 de 10 mm sobre la regla T, con su estilógrafo |
| **D · Herramienta** | D0: portaminas 0,5 HB sobre bond. D1: estilógrafo 0,35 o 0,5. D2: papel vegetal fijado sobre la pauta, con las cuatro marcas calcadas y rellenadas antes de escribir |

## Piezas y materiales

Todo sale de **medio tablero de terciado o multilaminado de 18 mm (1220 × 1220)**. El despiece está en la lámina B-05.

| N.º | Pieza | Cant. | Medidas (mm) | Plano |
|---|---|---|---|---|
| 1 | Tablero de escritura | 1 | 600 × 600 × 18 | todos |
| 2 | Listón del tablero | 2 | 600 × 42 × 18 | todos |
| 3 | Cartela del atril (despunte 30) | 2 | triángulo 460 × 460 | B3 |
| 4 | Travesaño del atril | 2 | 564 × 70 × 18 | B3 |
| 5 | Tope del atril | 1 | 600 × 30 × 18 | B3 |
| 6 | Montante de muro | 2 | 90 × 750 × 18 | B2 |
| 7 | Cartela de la cuña (despunte 20) | 2 | triángulo 600 × 161 | B0 |
| 8 | Travesaño de la cuña | 1 | 564 × 70 × 18 | B0 |
| 9 | Tope de la cuña | 1 | 600 × 30 × 18 | B0 |

**Herrajes:** 4 pasadores de varilla lisa de acero Ø8 × 32; 6 tarugos Ø8 y 6 tornillos 5 × 60; unos 30 tornillos 4 × 30 y cola vinílica; fieltro antideslizante; inclinómetro (aplicación del teléfono).

**Instrumentos y herramientas:** regla T de 60 cm; escuadras de 45° y 30/60°; plantilla de rotulación ISO 3098 de 10 mm con estilógrafo de 1,0 (tipo B: trazo = h/10); estilógrafos de 0,35 y 0,5; portaminas 0,5 HB; papel bond y vegetal A4. Conviene pedir prestados a los participantes los instrumentos que conserven: también son archivo.

## Armado

1. **Tablero.** Lijar la cara de escritura (grano 180) y sellarla con un acabado mate. Pegar y atornillar los dos listones en el dorso, a 20 mm de los bordes, con los tornillos desde los listones. Dejar el canto izquierdo recto, lijado y sin astillas. Marcar las esquinas de la hoja A4 (centro a 200 mm del borde superior).
2. **Cuña de 15°.** Cortar en diagonal un rectángulo de 600 × 161 para obtener las dos cartelas, con un corte recto porque esa es la superficie de apoyo. Despuntar 20 mm el vértice agudo. Unirlas con el travesaño trasero y atornillar el tope sobre las hipotenusas, en el extremo bajo. Fieltro debajo. **Verificar el ángulo con el inclinómetro** sobre el tablero apoyado.
3. **Atril de 45°** (opcional). Igual que la cuña, a partir de un cuadrado de 460 × 460, con despunte de 30.
4. **Montantes.** Perforar en cada uno 27 agujeros Ø8,5 de 15 mm de profundidad, cada 25 mm sobre el eje, empezando a 50 mm del borde inferior; numerarlos cada cinco. Fijarlos al muro a plomo, con 420 mm entre ejes y el borde inferior a 1250 mm del piso. Cubren hombros de unos 1170 a 1770 mm. Si no se puede perforar el muro, se atornillan a un tablero de 600 × 1200 apoyado en el muro y trabado en el piso.
5. **Para colgar el tablero (B2):** dos pasadores de apoyo en el agujero que indica la calculadora y dos de traba dos agujeros más arriba. El listón de 42 mm queda justo entre ellos (4 + 42 + 4 = 50 = dos pasos), así que el tablero no se levanta con los trazos ascendentes.

## Antes de la madera: maqueta

Para el piloto alcanza con una maqueta:

- **B0:** el tablero de cartón (o cualquier tablero liso de 600 × 600) apoyado en la mesa con un libro de unos 16 cm de alto bajo el borde trasero. Da unos 15°; se verifica con el inclinómetro.
- **B2:** la hoja pegada en el muro, con su centro a la altura del hombro.

Lo que se aprenda en el piloto (por ejemplo, que la franja del antebrazo resulta corta a 15°) se corrige en este documento antes de cortar madera.

## Verificaciones antes de cada sesión

- El tablero no se mueve: está apoyado en sus dos listones o trabado entre los pasadores.
- B0 y B3: el ángulo medido se anota en la ficha.
- La hoja está en sus marcas y fijada con cinta en los cuatro bordes.
- C2 y C3: la regla T corre sin juego por el canto; la plantilla no se desliza.
- D2: las cuatro marcas están calcadas y rellenadas en el vegetal.
- La altura del asiento o el agujero de los pasadores coincide con la hoja de medidas de la persona.

## Archivos

- `planos/B-01_tablero.svg` a `B-06_posiciones.svg`: láminas A3 en SVG, reunidas en `Banco de escritura - planos.pdf`.
  - B-01: tablero.
  - B-02: cuña de 15°.
  - B-03: atril de 45°.
  - B-04: montantes de muro (pizarra).
  - B-05: despiece.
  - B-06: las cuatro posiciones.
- Los planos se generan con `instrumento/herramientas/generar_planos.js` a partir de las medidas de `instrumento/lib/banco.js`. Si una medida cambia, se cambia allí y se regeneran los planos, la calculadora y este documento.
