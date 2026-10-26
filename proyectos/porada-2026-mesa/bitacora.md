# Bitácora

Cada entrada registra qué movimiento se hizo (**reunir · desarmar · proponer · ensayar · contrastar · decidir · consolidar**), qué se decidió (**conservar · modificar · descartar · cambiar la pregunta**), por qué y cuál es la siguiente acción. Los movimientos no van en orden: hay retornos.

---

### 26-10-2026 · 1 · Reunir: el encargo
- **Hecho**: se leyeron las bases oficiales (XIV edición, mesas, cierre el 31-01-2027) y el catálogo de materiales de Porada. → [`00_encargo/`](00_encargo/)
- **Hallazgo de procedimiento**: el concurso exige proyectos **inéditos y anónimos**, y este repositorio es **público**.
- **Decisión**: no publicar el diseño hasta que el autor decida la visibilidad (O7).
- **Siguiente acción**: el autor decide.

### 26-10-2026 · 2 · Reunir: las fuentes
- **Hecho**: en Internet Archive se reunieron Bertonio (1612/1879), Semper (1851, 1879), Squier (1877), Viollet-le-Duc (1873), *Wood Handbook* (2010) y Kessler (1919), todos con página y captura. Monoskop no fue accesible desde este entorno. → [`01_reunir/fichero.md`](01_reunir/fichero.md)
- **Siguiente acción**: desarmar.

### 26-10-2026 · 3 · Contrastar con la fuente → cambiar la pregunta (E5)
- **Hecho**: en Bertonio, *Chakhua* (montón) y *Chhakhua* (piedra hincada donde se atan los palos, y también los palos atados) son **dos entradas** (F01). El artículo las da como un solo nombre.
- **Decisión**: **cambiar la pregunta**. La pregunta deja de ser «cómo pesa la piedra sobre la madera» y pasa a ser **«cómo se une la madera a una piedra fija»**. El lastre se queda sin su palabra.
- **Siguiente acción**: revisar Bertonio 2011, p. 330, y corregir el artículo si corresponde (O1).

### 26-10-2026 · 4 · Desarmar y proponer
- **Hecho**: se desarmaron 5 imágenes y 13 fuentes. Diagnóstico: **las referencias visuales tiran hacia la masa y el concurso, hacia el armazón de madera**. Se fijaron criterios K1-K10 y cuatro versiones (V0 lastre, V1 llave, V2 hincada, V3 control).
- **Prerregistro**: los umbrales de los ensayos se fijaron **antes** del instrumento, en el commit `7e6165b`.

### 26-10-2026 · 5 · Ensayar, ronda 1 → descartar tres de cuatro
- **E1**: la barra de V0 llega a 9,9 MPa frente a 2,3 → **V0 descartada**.
- **E2**: V2 exige acuñar el montante → **«hincar» deja de ser la acción**.
- **E3**: con la geometría de partida, el lastre **sí** ayudaba (+40 %), pero no bastaba. La **geometría** lo resuelve mejor y vale para todas → **corrección común: pie de 180 mm**. Se eligió alargar el pie y no acercar el caballete para no quitar sitio a las rodillas en las cabeceras.
- **E4**: la llave de mármol no cabe en la espiga (necesita 53-75 mm, caben 37). La de fresno cabe con 14-19 mm. El peso de la llave es el 0,6 % del rozamiento → **V1 descartada; se retira «el peso traba»**.
- **K5**: falla en **todas** por el tablero de 59 kg en una sola pieza. Es un problema común, no de la piedra.
- **Siguiente acción**: derivar versiones donde la madera cargue la piedra (V0b) y donde la piedra trabaje solo a compresión (V4).

### 26-10-2026 · 6 · Ensayar, ronda 2 → la piedra no se justifica por la estructura
- **Resultado**: V0b y V4 cumplen K1-K4. En V4 la piedra trabaja a 0,08-0,17 MPa de compresión y reparte el apoyo de la llave (0,64 → 0,08 MPa). Con la geometría corregida, la condición prerregistrada se cumple y **se retira «la piedra estabiliza»**.
- **Contraste incómodo**: el control **V3 cumple lo mismo sin piedra**. En ninguna versión la piedra es necesaria para la estructura.
- **Decisión**: **modificar el concepto**. La frase del borrador («la gravedad de la piedra sostiene la ligereza del armazón») queda retirada por E1, E3, E4 y E5. Formulaciones candidatas que **sí** sostienen las fuentes y los cálculos, para que elija el autor:
  1. «La madera sostiene y se mueve; la piedra queda fija y recibe la unión» (E2, E4, F01).
  2. «La madera atraviesa la piedra» (V4, en sentido literal).
- **Siguiente acción**: E6, el nodo V4 a 1:1 junto al V3, para decidir si la piedra se queda por razones que el cálculo no mide.

### 26-10-2026 · 7 · Retorno: el autor advierte que predeterminó el concepto
- **Hecho**: el autor señala que, al fijar de antemano piedra + *chhaxwa*, el proceso pudo quedar inclinado hacia un resultado.
- **Lectura**: los ensayos sí contradijeron el borrador (E1, E4, E5), pero todas las versiones seguían discutiendo **dónde va la piedra**. Ninguna podía proponer que el problema fuera otro.
- **Decisión**: **abrir una propuesta B** con otra entrada al problema, sacada de la misma bibliografía, con su propio prerregistro y medida con el mismo instrumento y los mismos criterios. Después se comparan A y B, y se busca una síntesis si son compatibles. → [`03_proponer/propuesta_B.md`](03_proponer/propuesta_B.md)
