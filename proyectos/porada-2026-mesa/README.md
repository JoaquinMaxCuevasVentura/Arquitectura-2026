# Mesa · Porada International Design Award 2026

Proyecto de mesa de madera maciza para la XIV edición del concurso Porada, dedicada a las mesas. Cierre: 31-01-2027. Se trabaja con el método del autor: **reunir → desarmar → proponer → ensayar → contrastar → decidir → consolidar**, con retornos. La regla es que ningún contraste se omite y que cada incorporación resuelve una dificultad identificada.

> ⚠️ **Antes de nada**: el concurso exige proyectos **inéditos y anónimos**, y este repositorio es **público**. Ver [`00_encargo/bases.md`](00_encargo/bases.md#️-condiciones-que-afectan-a-cómo-usamos-github).

## Estado al 26-10-2026

- **La pregunta cambió.** El borrador decía: «la gravedad de la piedra sostiene la ligereza del armazón». Bertonio (1612) distingue *chakhua* (montón) de *chhakhua* (piedra hincada donde se atan los palos). Los ensayos mostraron que la piedra no puede ser viga (E1), que no puede ser llave (E4) y que su peso ni traba ni hace falta para estabilizar (E3, E4, E11). La pregunta vigente es **cómo se une la madera a una piedra fija**, y la propuesta B agrega otra: **cómo se muestra que la madera se mueve**.
- **Dos propuestas y una síntesis** ([`03_proponer/sintesis.md`](03_proponer/sintesis.md)):
  - **A · V4 Collar**, desde el concepto del autor: la espiga atraviesa un bloque de mármol que trabaja solo a compresión. Cumple K1-K4 y falla K5 (tablero de 59 kg).
  - **B · B2 Tablas clavijadas**, propuesta propia desde la bibliografía, sin la premisa de la piedra: 6 tablas sueltas, clavijadas y acuñadas; la junta muestra la estación. Cumple todo lo aplicable, sin piedra.
  - **AB**: el tablero de B2 con el collar de V4. Cumple K1-K5. Regla común: **la madera se mueve y se arma; lo único fijo es la piedra donde se traba**.
  - **B3**: B2 con una **tabla de servicio intercambiable** con mármol asentado. Cumple K1-K5. Nace de los precedentes.
- **Precedentes (E7)**: Porada ya junta madera y mármol (*Oswood*, *Osmose*), así que lo original tiene que ser **el modo del encuentro**. El jurado premia componentes con individualidad, intercambiabilidad y el detalle precioso de la unión. → [`01_reunir/precedentes.md`](01_reunir/precedentes.md)
- **Materiales bolivianos** (entrada 12 de la bitácora): el nogal de los Yungas es *Juglans boliviana*, descrito primero como variedad del mismo nogal negro que el canaletta de Porada; la piedra de Comanche es **granito** según la ley de La Paz de 2012. Propuesta: nogal canaleta para producir, el vínculo andino en el relato y el **granito de Comanche apomazado** como piedra candidata del collar de AB. La piedra que bloquea por gravedad se descartó con E11. → [`01_reunir/materiales_bolivianos.md`](01_reunir/materiales_bolivianos.md)
- **Lo que decide entre B2, AB y B3 no es un cálculo**: es E6 (¿el collar se lee como unión o como adorno?) y E10 (¿las juntas molestan en el uso?). Las dos son pruebas físicas, pendientes. Hay una versión previa con renders de Blender (E6a, E10a) que se puede hacer ya con la [hoja de prueba](04_ensayar/E6a_E10a_hoja.md).

![Ronda 5](03_proponer/laminas/comparativa_r5.svg)

| AB · el collar | B2 · solo madera | B3 · tabla de servicio |
|---|---|---|
| ![AB](05_consolidar/renders/general_AB.png) | ![B2](05_consolidar/renders/general_B2.png) | ![B3](05_consolidar/renders/general_B3.png) |

## Mapa

Los números ordenan carpetas, no el tiempo.

| Carpeta | Movimiento | Qué hay |
|---|---|---|
| [`00_encargo/`](00_encargo/) | reunir | bases verificadas (PDF oficiales), materiales de Porada, dudas para los organizadores |
| [`01_reunir/`](01_reunir/) | reunir | [fichero](01_reunir/fichero.md) de 17 fichas con página, transcripción y dudas; [capturas](01_reunir/capturas/) de dominio público; referencias visuales del autor |
| [`02_desarmar/`](02_desarmar/) | desarmar | [referencias](02_desarmar/referencias.md) (qué se toma, cambia, deja y por qué), [problema](02_desarmar/problema.md) (partes, relaciones, acciones, conflictos, criterios K1-K10), [objeciones](02_desarmar/objeciones.md) |
| [`03_proponer/`](03_proponer/) | proponer | [versiones A](03_proponer/versiones.md), [propuesta B](03_proponer/propuesta_B.md), [síntesis](03_proponer/sintesis.md), [láminas SVG A3](03_proponer/laminas/) |
| [`04_ensayar/`](04_ensayar/) | ensayar · contrastar · decidir | [ensayos](04_ensayar/ensayos.md) con prerregistro, resultado, contraste y decisión; [resultados por ronda](04_ensayar/resultados/) |
| [`05_consolidar/`](05_consolidar/) | consolidar | [entregables, dependencias y calendario](05_consolidar/entregables.md); [modelos 3D base](05_consolidar/modelos/) |
| [`instrumentos/`](instrumentos/) | (todos) | instrumento paramétrico en Python: cálculo, láminas y OBJ ([README](instrumentos/README.md)); **modelo de Blender** con Geometry Nodes, materiales procedurales y renders que corren en la nube ([README](instrumentos/blender/README.md)) |
| [`bitacora.md`](bitacora.md) | decidir | cada decisión con su porqué y su siguiente acción |

## Cómo se aplicó el método

- **Contrastes elegidos para este proyecto**, porque es un proyecto técnico y material con una retórica:
  - **cálculo** para uso, cuerpo, material y uniones (E1-E4, E8, E9, E2b, E11);
  - **contraste con fuentes** para la palabra y el tipo (E5, F02, F09);
  - **pruebas físicas** para la percepción y el uso (E6, E10);
  - **antecedentes** para la originalidad (E7).
  
  Cada ensayo dice **qué no demuestra**.
- **Prerregistro**: los umbrales se fijaron antes de calcular y quedaron en git. Los de A están en `7e6165b`, antes del instrumento. Los de B, en `38a6dc6`, antes de su cálculo. Cuando un contraste no tuvo prerregistro (E5) o hubo cuentas a mano previas (E8, E9, E11), se dice.
- **El ensayo puede contradecir**. Se descartaron V0, V1, V2, B1 y la cuña por gravedad (E11). La frase del borrador se retiró. Cuando un resultado favorecía la idea del autor (E3, ronda 1: el lastre sí ayudaba), también se registró.
- **Control de expansión**: cada pieza nueva responde a una dificultad identificada:
  - V0b y V4 salen de E1 y E4;
  - B2 sale de E8, E9 y E2b;
  - el exportador OBJ sirve para la lámina 3;
  - los renders de Blender sirven para E6a y E10a, que se pidieron antes de las maquetas.
  
  No se hizo atlas ni aplicación web, porque ninguna decisión depende de ellos.

## Decisiones pendientes del autor

1. **Visibilidad del repositorio** hasta el fallo (26-02-2027).
2. **Construir E6 y E10** (maquetas 1:1) y, con su resultado, elegir **B2 o AB**.
3. **La frase del concepto** (candidatas en la [bitácora](bitacora.md), entradas 6 y 9) y **el nombre** (O6: usar una palabra aymara como nombre de producto).
4. **La piedra**: de catálogo (Nero Sahara Noir) o **granito de Comanche** apomazado. Para Comanche hacen falta una muestra, su color y su ficha (SERGEOMIN; EN 1926, EN 12372), y hay que consultar a los organizadores si una piedra fuera de catálogo es aceptable. E6a, con las dos piedras ([renders](05_consolidar/renders/)).
5. **Revisar Bertonio 2011, p. 330**, y corregir el artículo si corresponde (O1).
6. **Confirmar la cita de Galen Johnson** (F15), que viene de la tesis *Contenida*.
