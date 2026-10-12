# Plan tipográfico

**Entregable E6 de *A pulso* · plan para F5 (semanas 12–18)**

La tipografía es la prueba de que las reglas sirven. Por eso cada glifo tiene que poder decir de dónde viene. Este plan fija lo que conviene decidir antes de dibujar: métricas, juego de glifos, ejes, procedencia y cómo pasar del trazo mediano al contorno.

## 1. Métricas

| Parámetro | Valor | Nota |
|---|---|---|
| Unidades por eme | 1000 | |
| Altura x | 500 | El instrumento exporta los medianos con esta escala: 30 mm = 500 unidades |
| Ascendentes | ≈ 780 | A precisar con las *d* y *h* de G6 (en la pauta P, la línea de ascendentes está a 1,75 h ≈ 875) |
| Descendentes | ≈ −250 | Sin datos en el repertorio: si hacen falta *g, j, p, q, y*, agregar un gesto con descendente en la confirmación |
| Tildes | sobre la altura x, ≈ 620–700 | Medir la tilde de *adhesión* en G6 |

## 2. Juego de glifos

**Mínimo (≈ 60 por maestro)**: ver `glifos_minimos.txt`. Son las minúsculas *a–z*, la *ñ*, *á é í ó ú ü*, la puntuación española (. , ; : ¿ ? ¡ ! - « » ’ “ ” ( )), el espacio y .notdef.

**Extendido (≈ 200)**: mayúsculas, cifras, *Á É Í Ó Ú Ü Ñ*, algunos signos más, y las alternativas contextuales de las letras frecuentes.

**Orden de dibujo.** Primero las letras de la palabra de prueba, porque tienen evidencia directa (*n, o, a, d, h, e, s, i*). Después las letras de igual estructura, a las que se transfieren las reglas:

| Estructura | Letras |
|---|---|
| Asta y arco | n → m, h, r, u (por simetría) |
| Óvalo | o → c, e, a, d, b, p, q, g |
| Diagonal | v → w, y, x, k, z |
| Asta sola | i → l, j, t, f |
| Otras | s, ñ y las tildes |

## 3. Ejes y estilos

Los dos ejes se eligen en la **Decisión 2** (S13), entre las variables que produjeron las reglas más consistentes. Las etiquetas de ejes propios en OpenType llevan **cuatro letras mayúsculas**:

| Variable | Etiqueta sugerida | Rango |
|---|---|---|
| Apoyo | `APOY` | 0 = antebrazo apoyado (A0) · 100 = brazo suspendido (A2) |
| Plano | `MURO` | 0 = mesa (B0) · 100 = muro (B2) |
| Límite | `CNAL` | 0 = libre (C0) · 100 = canal estrecho (C2) |
| Resistencia | `ROCE` | 0 = liso (D0) · 100 = áspero (D1) |

Con dos ejes hay **cuatro maestros**, uno en cada esquina, y las instancias llevan el nombre de un puesto de escritura en lugar de un peso: *Mesa*, *Atril*, *Muro*, *Canal*, *Roce*.

**Si la interpolación no funciona** (porque las formas de los extremos son demasiado distintas para tener la misma estructura de puntos), se publican estilos estáticos. Es una salida válida y se anota como hallazgo.

## 4. Del trazo a la letra

1. En `superponer.html`, elegir la persona, el gesto y la condición, y descargar «Medianos para el editor». El SVG trae la línea base en y = 0 y la altura x en y = −500 (SVG con y hacia abajo).
2. Importarlo en el editor como fondo o capa de referencia del glifo.
3. Construir el contorno según el **modo de traducción** declarado:
   - **calco:** contorno alrededor de una traza seleccionada (no del mediano), con limpieza mínima;
   - **esqueleto + herramienta:** el mediano como recorrido de una pluma de ancho o de expansión definidos, aplicados igual en todo el alfabeto;
   - **regla:** dibujo libre que respeta una o más reglas del catálogo, y solo eso;
   - **interpolación:** los maestros se redibujan con la misma estructura de puntos; los medianos de cada condición son la guía.
4. Anotar la procedencia (sección 5) antes de pasar al glifo siguiente.
5. Probar en texto: a 10, 24 y 72 pt en cada iteración, y la palabra *adhesión* en todas las instancias.

## 5. Procedencia de cada glifo

Cada glifo guarda su origen en la biblioteca del glifo (`lib` en UFO, o «nota» en Glyphs) con esta clave:

```json
"apulso.procedencia": {
  "modo": "regla",
  "reglas": ["R-03", "R-07"],
  "condiciones": ["A2B2"],
  "ensayos": ["AP-P00-S04-A2B2-G5-R01", "AP-P00-S04-A2B2-G5-R07"],
  "mediano": "AP-P00-G5-A2B2-mediano.svg",
  "nota": "unión baja aplicada también a m y h"
}
```

El espécimen (M5, fase F6) leerá estas claves para mostrar, al tocar una letra, sus reglas, sus condiciones y sus ensayos.

## 6. Variabilidad: alternativas que se alternan

Para que el texto conserve la dispersión de la mano, cada letra frecuente puede tener 3–5 alternativas tomadas de repeticiones reales (`n.alt1`, `n.alt2`…). En el texto se alternan con la función `calt`. Un esquema posible, que se rota entre tres formas:

```
@base = [a d e h i n o s];
@alt1 = [a.alt1 d.alt1 e.alt1 h.alt1 i.alt1 n.alt1 o.alt1 s.alt1];
@alt2 = [a.alt2 d.alt2 e.alt2 h.alt2 i.alt2 n.alt2 o.alt2 s.alt2];

feature calt {
  lookup ciclo {
    sub @base @base' by @alt1;
    sub @alt1 @base' by @alt2;
  } ciclo;
} calt;
```

En una secuencia de letras de la clase, la forma base va seguida de la alternativa 1, esta de la 2 y luego se vuelve a la base. Hay que **comprobarlo en el editor y en navegadores**: el comportamiento del contexto anterior dentro de una misma búsqueda puede variar entre motores. *Beowolf* (LettError, 1990) es el precedente: la variabilidad como propiedad del tipo.

## 7. Herramientas

- **Editor:** Glyphs o FontLab (comerciales), RoboFont (macOS), o FontForge y Fontra (libres).
- **Compilación libre:** fuentes en UFO más un `.designspace` con los ejes, compiladas con `fontmake`.
- **Pruebas:** el espécimen web y un documento de prueba con texto real en español.

## 8. Licencia

Si la fuente se publica con la **SIL Open Font License (OFL)**, puede usarse en la docencia y en otros proyectos, y el espécimen puede incluir los archivos. Hay que decidirlo antes de la difusión (F6) y anotarlo en la bitácora.
