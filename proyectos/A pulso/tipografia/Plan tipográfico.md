# Plan tipográfico

**Entregable E6 (tipografía técnica *A pulso*) y E12 (plantilla de rotulación) · plan para F5 (semanas 12–18)**

La tipografía demuestra que las reglas sirven, y cada glifo tiene que poder decir de dónde viene. Como la situación del proyecto es el plano de arquitectura, la fuente es **técnica**: mayúsculas de palo seco, cifras y signos de plano, pensada para rotular. Este plan fija lo que conviene decidir antes de dibujar.

## 1. Métricas

| Parámetro | Valor | Nota |
|---|---|---|
| Unidades por eme | 1000 | |
| Altura de la mayúscula | 700 | El instrumento exporta los medianos con esta escala: h = 700 unidades |
| Grosor de referencia | 70 (h/10) | Corresponde a ISO 3098 tipo B; el tipo A sería h/14 ≈ 50 |
| Inclinación | 0° o 15° | Vertical o inclinada a 75° sobre la horizontal, como permite la norma. La inclinación de cada estilo sale de la medición de astas, no de la norma |
| Descendentes | Solo para cifras y signos que lo pidan | Sin minúsculas en la versión mínima |

## 2. Juego de glifos

**Mínimo (≈ 70 por maestro)**: ver `glifos_minimos.txt`.
- Mayúsculas *A–Z*, *Ñ* y vocales con tilde.
- Cifras *0–9*.
- Puntuación española.
- Los **signos de plano**: ° ± Ø × % = + / : · ‘ ’ ( ) —.

**Extendido**: minúsculas para notas, más signos (≤ ≥ ∅ ′ ″), y alternativas contextuales de las letras frecuentes.

**Orden de dibujo.** Primero las letras con evidencia directa en el repertorio: *I, O, A, R* y el rótulo *PLANTA 1:50* (*P, L, N, T, 1, 5, 0*). Después se transfieren las reglas a las letras de igual estructura:

| Estructura | Letras |
|---|---|
| Astas y horizontales | I → L, T, E, F, H |
| Curvas | O → C, G, Q, S, 0, 6, 8, 9 |
| Diagonales | A → V, W, X, Y, K, M, N, Z, 4, 7 |
| Asta y bucle | R → P, B, D, 2, 3, 5 |
| Signos | 1:50 → resto de cifras y signos de plano |

## 3. Ejes y estilos

Los dos ejes se eligen en la **Decisión 2** (S13), entre las variables que produjeron las reglas más consistentes. Las etiquetas de ejes propios en OpenType llevan **cuatro letras mayúsculas**:

| Variable | Etiqueta | Rango |
|---|---|---|
| Guía | `GUIA` | 0 = a pulso (C0) · 50 = regla T (C2) · 100 = plantilla (C3) |
| Plano | `PLNO` | 0 = tablero 15° (B0) · 100 = pizarra (B2) |
| Apoyo | `APOY` | 0 = antebrazo apoyado (A0) · 100 = brazo suspendido (A2) |
| Herramienta | `HERR` | 0 = portaminas (D0) · 100 = estilógrafo (D1) |

**`GUIA` es el candidato natural**: hace tipografía de la gradación de prescripción instrumental, que es la idea central del proyecto. Con dos ejes hay **cuatro maestros**. Las instancias llevan el nombre de un puesto o de un instrumento: *Tablero*, *Mesa*, *Pizarra*, *Regla*, *Plantilla*.

**Si la interpolación no funciona** (porque los extremos tienen estructuras de puntos incompatibles), se publican estilos estáticos y se anota como hallazgo.

## 4. Del trazo a la letra

1. En `superponer.html`, elegir la persona, el gesto y la condición, y descargar «Medianos para el editor». El SVG trae la línea base en y = 0 y la altura de la mayúscula en y = −700.
2. Importarlo en el editor como fondo del glifo.
3. Construir el contorno según el **modo de traducción** declarado:
   - **calco:** contorno alrededor de una traza seleccionada;
   - **esqueleto + herramienta:** el mediano como recorrido de un **estilógrafo de grosor h/10**, con terminales redondas. Es la herramienta propia de la letra técnica;
   - **regla:** dibujo que respeta una o más reglas del catálogo;
   - **interpolación:** maestros redibujados con la misma estructura de puntos.
4. Anotar la procedencia (sección 5).
5. Probar en uso real: rótulos y cotas a 3,5, 5 y 10 mm impresos sobre un plano, y un título a 20 mm.

## 5. Procedencia de cada glifo

Cada glifo guarda su origen en la biblioteca del glifo (`lib` en UFO, o «nota» en Glyphs):

```json
"apulso.procedencia": {
  "modo": "esqueleto + herramienta",
  "reglas": ["R-02"],
  "condiciones": ["BASE", "A2B2"],
  "ensayos": ["AP-P00-S04-A2B2-G5-R01", "AP-P00-S04-A2B2-G5-R07"],
  "partitura": "↓ ↘",
  "participantes": ["P00", "P03"],
  "mediano": "AP-P00-G5-A2B2-mediano.svg",
  "nota": "bucle bajo transferido a P y B"
}
```

El espécimen (M5) leerá estas claves para mostrar, al tocar una letra, sus reglas, sus condiciones, sus ensayos y la partitura con que se trazó.

## 6. Variabilidad: alternativas que se alternan

Para que un rótulo conserve la dispersión de la mano, cada letra frecuente puede tener 3–5 alternativas tomadas de repeticiones reales (`A.alt1`, `A.alt2`…), alternadas con `calt`:

```
@base = [A E L N O P R T];
@alt1 = [A.alt1 E.alt1 L.alt1 N.alt1 O.alt1 P.alt1 R.alt1 T.alt1];
@alt2 = [A.alt2 E.alt2 L.alt2 N.alt2 O.alt2 P.alt2 R.alt2 T.alt2];

feature calt {
  lookup ciclo {
    sub @base @base' by @alt1;
    sub @alt1 @base' by @alt2;
  } ciclo;
} calt;
```

En una secuencia, la forma base va seguida de la alternativa 1, esta de la 2 y luego se vuelve a la base. Hay que **comprobarlo en el editor y en los navegadores**, porque el contexto anterior dentro de una misma búsqueda puede comportarse distinto según el motor. En el estilo *Plantilla* no hay alternativas: el normógrafo borra la variación, y ese es su sentido.

## 7. La plantilla de rotulación *A pulso* (E12)

Con la fuente terminada, la letra vuelve al instrumento:

1. Tomar el estilo elegido (por ejemplo, *Tablero*) a 5 o 10 mm.
2. Convertir cada glifo en **ranuras de esténcil**: el recorrido del estilógrafo se vuelve una ranura de ancho igual al de la punta más una holgura (≈ 0,1 mm), con **puentes** que sostienen las contraformas (O, A, R, P, B, D, 0, 4, 6, 8, 9).
3. Disponer los glifos en una regleta de unos 240 × 40 mm, con un borde para apoyarla en la regla T, como los normógrafos comerciales.
4. Cortar con láser en acrílico de 1,5–2 mm y probar con el estilógrafo correspondiente.
5. Si el normógrafo comercial lleva un borde elevado o patas para que la tinta no corra, reproducirlas.

La plantilla se estrena en la sesión *La lámina*. Es un instrumento nuevo que educará otros gestos: la pregunta del proyecto se vuelve sobre sí misma.

## 8. Herramientas

- **Editor:** Glyphs o FontLab (comerciales), RoboFont (macOS), o FontForge y Fontra (libres).
- **Compilación libre:** UFO más un `.designspace` con los ejes, compilado con `fontmake`.
- **Plantilla:** exportar los glifos como SVG y preparar las ranuras en un programa vectorial; el corte láser requiere trazos de corte rojos de 0,1 mm.

## 9. Licencia

Si la fuente se publica con la **SIL Open Font License (OFL)**, puede usarse en la docencia y en otros proyectos, y el archivo de la plantilla puede compartirse para que otros la corten. Hay que decidirlo antes de F6.
