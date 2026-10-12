# Archivo del tablero

**Entregable E10 de *A pulso* · guía de trabajo**

El archivo reúne lo que el tablero de dibujo dejó escrito sobre el cuerpo: manuales, normas, láminas, planos e instrumentos. No se lee para saber cómo eran las letras, sino **qué cuerpo pedían**. Es la misma lectura que Rebecca Wilkinson hace de Moxon en *(New) Mechanick Exercises*: el manual como coreografía del trabajo.

## 1. Qué se busca

| Tipo | Ejemplos | Dónde buscar |
|---|---|---|
| **Manuales de rotulación y dibujo técnico** | Reinhardt, *Lettering for Draftsmen, Engineers and Students* (1895–96); French y Meiklejohn, *The Essentials of Lettering* (1912); Ching, *Architectural Graphics* (1975; en español, *Manual de dibujo arquitectónico*); manuales en español usados en las facultades de La Paz | Bibliotecas de las facultades de arquitectura; libros de los participantes; Internet Archive y Project Gutenberg para los antiguos |
| **Normas** | ISO 3098 y normas nacionales o institucionales de presentación de planos | Bibliotecas técnicas; apuntes de cátedra |
| **Apuntes y programas de cátedra** | Programas de dibujo técnico o expresión gráfica de primer año; láminas modelo de rotulación | Docentes y exdocentes; archivos de las facultades |
| **Láminas de estudiantes** | Ejercicios de rotulación, carátulas, rótulos de láminas | Los participantes del grupo T |
| **Planos rotulados a mano** | Planos de obra, de aprobación municipal y de concursos | Estudios antiguos; archivos de los participantes; archivos municipales si son accesibles |
| **Instrumentos** | Normógrafos, estilógrafos, portaminas, reglas T, paralelas, escuadras, tableros | Los participantes; tiendas antiguas de artículos de dibujo |

**Primera pregunta para el archivo:** ¿cuándo y cómo dejó de enseñarse la rotulación a mano en las facultades de La Paz? Se responde cruzando programas de cátedra, láminas fechadas y entrevistas.

## 2. Ficha de fuente

Una por fuente, en `archivo/fichas/FUENTE-###.md`.

```
FUENTE-### · [título breve]
Tipo: manual / norma / apunte / lámina / plano / instrumento
Autor o autora · fecha · lugar · edición:
Dónde está (biblioteca, persona, enlace) y permiso de uso:
Quién la usaba y cuándo (si se sabe):
Fotografías: archivo/fotos/FUENTE-###_01.jpg … (con escala)

PRESCRIPCIONES SOBRE EL CUERPO (cita textual + página)
Postura:
Apoyo (antebrazo, mano, codo):
Plano (inclinación del tablero, altura):
Guías (líneas, regla, escuadra, plantilla):
Herramienta y su agarre:
Orden y dirección de los trazos (partitura):
Ritmo, velocidad, repetición:
Correcciones, errores, castigos:
Alturas, grosores e inclinación de la letra:

Lo que la fuente NO dice sobre el cuerpo (y da por sabido):
Relación con las condiciones del banco (A, B, C, D):
```

## 3. Lectura coreográfica

1. **Citar, no resumir.** Las prescripciones se copian textualmente, con su página, porque la forma de la instrucción también es un dato (imperativo, ilustración, ejemplo).
2. **Separar lo que el texto dice de lo que la imagen muestra.** Muchas posturas solo aparecen dibujadas.
3. **Dibujar la partitura.** Cada orden de trazos prescrito se redibuja sobre las letras del repertorio (I, O, A, R y el rótulo) con flechas numeradas, y se escribe en la notación del instrumento: `↓` `↑` `→` `←` `↘` `↗` `↙` `↖` para los trazos rectos y `↺` `↻` para los que vuelven a su inicio. Por ejemplo, la R de dos tiempos es «↓ ↘».
4. **Tabular.** Todas las prescripciones van a `archivo/prescripciones.csv`, con las columnas `fuente, pagina, categoria, cita, letra, partitura, condicion_banco`.
5. **Comparar.** La partitura prescrita se pone junto a la declarada en la entrevista y a la observada en la tableta (ver el Catálogo de reglas).

## 4. Inventario de instrumentos

Cada instrumento prestado o encontrado se fotografía de frente y de perfil, con una regla en la imagen, y se registra en `archivo/instrumentos.csv`:

```
id, tipo, marca, modelo, medidas, alturas_de_letra, grosor_de_trazo, dueño_o_dueña, años_de_uso, notas
INS-001, normógrafo, …, …, …, "2,5 · 3,5 · 5", "0,25 · 0,35 · 0,5", P03, 1985–2002, "mellado en la R"
```

Las marcas de uso (desgaste, mellas, cinta, nombres escritos) se fotografían en detalle: son huellas del cuerpo en el instrumento.

## 5. Permisos

- Las fotos de objetos y documentos de participantes se publican solo con la autorización del consentimiento.
- Los originales no salen de las manos de sus dueños: se fotografían en el lugar.
- Los manuales con derechos vigentes se citan y se fotografían para estudio; para publicarlos en los *Ejercicios* se usan fragmentos breves o redibujos.

## 6. Productos del archivo

- **Fichas de fuente** y **tabla de prescripciones**: alimentan el atlas y el texto.
- ***Ejercicios del tablero*** (E11): una publicación que reedita las partituras de los manuales junto a las observadas en el banco, como ejercicios que cualquiera puede repetir.
- **Inventario de instrumentos**: base de la exposición y de la sesión *La lámina*.
