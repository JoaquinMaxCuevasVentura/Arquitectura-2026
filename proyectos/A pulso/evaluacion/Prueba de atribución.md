# Prueba de atribución

**Responde a la subpregunta P4: ¿reconoce un lector en la letra terminada el puesto o el instrumento que la originó? · Semana 17**

Es la prueba más directa de que el puesto o el instrumento quedaron en la forma, y no solo en el relato de quien escribió.

## Diseño

- **Elección forzada entre dos.** En cada ensayo se muestran dos versiones del mismo rótulo de plano, compuestas en dos estilos (por ejemplo *Tablero* y *Pizarra*, o *A pulso* y *Plantilla*). La pregunta es siempre la misma y se adapta a la pareja: «Una de estas dos se escribió de pie, en una pizarra. ¿Cuál?» o «Una de estas dos se trazó con plantilla. ¿Cuál?».
- **Estímulos:** 20 pares con rótulos distintos y reales de un plano, que usen las letras dibujadas. Por ejemplo: *PLANTA ALTA, CORTE A-A, FACHADA NORTE, ESC. 1:100, DORMITORIO, COCINA, ESTAR, BAÑO, NPT +3.45, DETALLE 2*. Todos a la misma altura (5 mm impresos, como en un plano), negro sobre blanco.
- **Lado aleatorio:** en la mitad de los pares, el estilo que se pregunta va a la izquierda; el orden de los pares se baraja para cada lector.
- **Sin retroalimentación:** el lector no sabe si acertó hasta el final, para que no aprenda durante la prueba.
- **Lectores:** de 10 a 15 personas que **no** hayan visto el proyecto. Se anota si son arquitectos formados en tablero, formados con CAD, o de otro oficio, porque puede cambiar el resultado. Es una segunda forma de la pregunta P2: ¿reconoce mejor el instrumento quien lo usó?
- **Duración:** unos 5 minutos por persona.

**Antes de la fuente:** si en la semana 17 la tipografía no está lista, la prueba puede hacerse con rótulos digitalizados de G6 (*PLANTA 1:50*) de dos condiciones. Así se prueba si la condición se reconoce en la escritura, todavía no en la letra diseñada. Conviene hacer las dos versiones y comparar.

## Cálculo

El azar acierta el 50 %. Con 12 lectores y 20 pares hay **240 respuestas**:

| Aciertos | Porcentaje | Probabilidad de lograrlo por azar | Lectura |
|---|---|---|---|
| 134 o más | ≥ 55,8 % | < 0,05 | Por encima del azar |
| 168 o más | ≥ 70 % | prácticamente nula | **Claramente perceptible**: el umbral que fija la propuesta |

Esta cuenta trata cada respuesta como independiente. Como las de una misma persona no lo son del todo, se completa con un análisis por lector: **15 o más aciertos sobre 20** está por encima del azar para esa persona (p ≈ 0,02). El resultado se informa así: «__ de __ lectores distinguieron las condiciones; aciertos totales: __ %».

## Hoja de respuestas

| Lector | Oficio (T, D u otro) | Par 1 | Par 2 | … | Par 20 | Aciertos |
|---|---|---|---|---|---|---|
| L01 | | izq. / der. | | | | /20 |

Las respuestas se guardan en `evaluacion/respuestas_atribucion.csv`, con las columnas `lector, oficio, par, rotulo, lado_correcto, respuesta, acierto`.

## Qué se hace con el resultado

- **Por encima del 70 %:** la condición se lee en la letra. Se informa qué pares fallaron más: muestran qué letras perdieron la marca de su condición.
- **Entre el azar y el 70 %:** la condición se percibe débilmente. Hay que comparar la versión escrita con la versión de la fuente: si la escrita se reconoce y la fuente no, la traducción borró la diferencia.
- **En el azar:** es un resultado, no un fracaso. La condición puede vivir en el gesto y en el relato sin pasar a la forma terminada. Se anota en los hallazgos y en el texto final.
