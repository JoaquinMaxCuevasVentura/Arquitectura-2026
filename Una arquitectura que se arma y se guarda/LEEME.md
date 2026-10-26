# Una arquitectura que se arma y se guarda

Proyecto de artículo de Joaquin Max Cuevas Ventura para la *Revista De Arquitectura* (Universidad de Chile), n.º 52, «Intervención en arquitectura y urbanismo + temática libre». **Cierre: 15 de enero de 2027. Envío previsto: 12 de enero.**

**Estado al 26 de octubre de 2026:** borrador cero. Todavía no hay trabajo de campo. Están listos la pregunta, la tesis provisional, los contrastes que podrían tumbarla, el protocolo de campo y las reglas de las láminas.

## El proyecto en un párrafo

En La Paz, muchos puestos de venta se construyen cada mañana y se guardan cada noche: se despliega una tela, se disponen cajas, se tensa una cubierta, se ordena la mercancía, se marca un borde. El artículo estudia esa construcción diaria como arquitectura. Se observan varios ciclos completos de tres puestos de una misma tipología, se conversa con sus responsables y se hacen láminas de collage que unen cada estado del puesto con el gesto que lo produce. **Pregunta:** ¿qué conocimiento arquitectónico se produce en esa secuencia de gestos, cómo se aprende, y qué hace con él una intervención urbana? **Tesis provisional:** la forma del puesto está en el orden de sus operaciones más que en su objeto; por eso, una intervención que fija la forma sin leer la secuencia puede conservar el objeto y perder la arquitectura.

## Qué hay y para qué sirve

| Archivo | Qué es | Qué decisión permite |
|---|---|---|
| `analisis/01_convocatoria_RA52.md` | Bases de la convocatoria (con su procedencia), lista de lo que falta confirmar, sección recomendada y calendario | A qué sección se postula y cuándo se hace cada cosa |
| `analisis/02_pregunta_tesis_y_contrastes.md` | **El archivo central.** Pregunta, tesis en cinco hipótesis, qué resultado tumbaría cada una, qué demuestra cada prueba, control de la expansión y puntos de decisión | Conservar, modificar o descartar la tesis con criterios fijados antes del campo |
| `analisis/03_estado_del_arte_y_fuentes.md` | Fuentes marcadas como verificadas, existentes o pendientes; el antecedente más cercano (Moatasim) y qué añade este artículo | Qué se puede citar ya y qué hay que leer primero |
| `analisis/04_referencias_desarmadas_y_laminas.md` | Cada referencia desarmada (qué se toma, qué cambia, qué se deja); la estética de Servino evaluada; reglas de notación de las láminas | Cómo se dibujan las láminas y con qué condiciones |
| `campo/protocolo.md` | Cómo elegir lugar y puestos, consentimiento, qué registrar, vocabulario de operaciones, mediciones, guía de conversación, devolución y privacidad | Cómo se hace el campo |
| `campo/ficha_de_ciclo.md` | Plantilla para cada ciclo observado | — |
| `campo/registro_de_operaciones.csv` | La tabla de operaciones (vacía): una fila por operación | — |
| `campo/comparar_ciclos.py` | Compara los ciclos de cada puesto y dice si la secuencia es estable | Si se sostiene la hipótesis H1, o si «secuencia» pasa a «repertorio» |
| `analisis/05_carcamo_toro_henao_y_donde_leer.md` | Lo que aportan los dos artículos que envió el autor (Cárcamo Pino, 2025b; Toro Henao, 2014), propuestas de estructura y epígrafe, y dónde leer cada libro del núcleo (Internet Archive y Monoskop) | Qué leer primero; si el artículo adopta dos hipótesis y dos conclusiones |
| `taxonomia/` | Taxonomía visual: 32 imágenes de dominio público en tres tableros (el árbol, el mapa de fechas y el relato), con su catálogo y su `LEEME.md` | Qué parte del ciclo no muestra el archivo; si las seis categorías alcanzan (H2) |
| `articulo/borrador_v0.md` | El artículo: título, resúmenes, secciones 1-4 y 7 escritas; 5, 6 y 8 como guías con lo que debe ir | — |

Para comparar ciclos: `python3 campo/comparar_ciclos.py` (solo usa la biblioteca estándar).

## Lo que decide el autor esta semana

1. **Confirmar las bases** en la página de la revista (la lista está en `01`). No se pudieron leer con herramientas automáticas porque la página tiene una verificación anti-bots.
2. **Elegir tipología, lugar y los tres puestos** (criterios en `campo/protocolo.md`, sección 2).
3. **Revisar la pregunta ajustada y los umbrales** de las hipótesis (`02`). Los umbrales se pueden cambiar ahora; después del campo, no.
4. **La estética de las láminas:** la de Servino entra con cinco correcciones (`04`, sección 2). La primera lámina se pone a prueba el 23 de noviembre.
5. **La estructura y el epígrafe:** dos hipótesis y dos conclusiones, como Cárcamo Pino, y un epígrafe con palabras de una vendedora (`05`, sección 2).
6. ***Contenida*:** pasar el enlace a la tipografía. No está en los repositorios de GitHub ni en Drive, y los canales de Are.na que nombran las notas de *Altiplano* ya no aparecen en la cuenta. Queda «en espera» hasta verla (`02`, sección 7).

## Reglas de trabajo

- **El autor decide** la pregunta, la tesis, las interpretaciones, el título y la revista. Quien asista propone y explica.
- **No se inventan citas, páginas ni fuentes.** Las marcas [V], [E] y [P] de `03` dicen qué se puede citar. Nada [E] o [P] se cita textualmente.
- **El repositorio es público.** Las fotos, las fichas con conversaciones y todo lo que identifique a una persona van a `campo/privado/` (Git lo ignora) o a Drive.
- **Los archivos de `analisis/` son registro:** no se reescriben; se añaden secciones fechadas.
- **Lenguaje llano**, comillas latinas «», citas con autor, año y página, como en el artículo sobre *Altiplano*.
- **Declaración de IA:** si un asistente redacta o corrige texto del artículo, se añade a la declaración final.

## De dónde viene

- **Del artículo sobre *Altiplano*** (repositorio `Altiplano`) vienen la disección tectónica (apoyo, vano, masa, límite), los cuatro pasos de Lundberg, la collage de Fuão, la casa como collage de Monteys y Fuertes, el manuaje de Cárcamo Pino y la regla de verificar cada cita. Aquí la *inmersión* de Lundberg se sustituye por la **devolución** de la lámina a quien arma el puesto.
- **De la tesis «Arquitectura collage»** (UMSA, 2023) viene el collage como instrumento de indagación y no de representación final, con su poética (fragmento, corte, encuentro, pegado) y su retórica (papier-collé, fotocollage, digital).
- **Del método general del autor** viene el ciclo de reunir, desarmar, proponer, ensayar, contrastar, decidir y consolidar. `02` elige los contrastes que mandan en este proyecto.
