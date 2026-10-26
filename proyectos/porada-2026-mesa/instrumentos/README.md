# Instrumento paramétrico de la mesa

Un instrumento para seguir pensando: describe cada versión como un conjunto de piezas, la mide contra los criterios K1-K5 con los ensayos E1-E4 (y E8, E9 y E2b para la propuesta B), y dibuja las láminas. **Python 3.10 o superior, sin dependencias.**

```bash
cd proyectos/porada-2026-mesa/instrumentos
python3 -m mesa                 # todas las rondas
python3 -m mesa --ronda 1       # solo una
python3 -m unittest test_mesa   # comprobaciones contra cálculos a mano
```

Escribe:
- `../04_ensayar/resultados/rondaN.md` y `.json`: tablas de resultados.
- `../03_proponer/laminas/*.svg`: láminas A3 por versión y comparativas por ronda. Se abren en el navegador o en Illustrator e Inkscape.
- `../05_consolidar/modelos/*.obj`: modelo 3D base de las candidatas V4, B2, AB y B3.

## Qué hay en cada archivo

| Archivo | Qué hace |
|---|---|
| `mesa/materiales.py` | Nogal, fresno y mármol con su fuente (FPL 2010, Kessler 1919). Factor de diseño 1/3 |
| `mesa/geometria.py` | Pieza (prisma recto con material y función del Cuadro 1) y Mesa (masa, centro de gravedad, volúmenes) |
| `mesa/versiones.py` | Cada versión como función. `configurar()` cambia la geometría común |
| `mesa/calculos.py` | E1-E4, E8, E9, E2b, criterios K1-K5 y supuestos comunes (P, H, humedad, umbrales) |
| `mesa/dibujo.py` | Láminas SVG: alzado y planta 1:10, sección, detalle de la unión 1:2,5, comparativas 1:20 |
| `mesa/modelo3d.py` | Exporta las candidatas vigentes a OBJ + MTL (`../05_consolidar/modelos/`): base de masas para D5, Blender o Rhino |
| `mesa/__main__.py` | Rondas, lecturas y salida de resultados |

## Modelos y sus límites (qué **no** demuestran)

- **E1, piedra como viga**: biapoyada, peso propio más P en el centro, flexión elástica. No considera vetas, fisuras ni impacto.
- **E2, movimiento**: lineal, con el coeficiente **tangencial** (el peor caso), entre 4 y 13 % de humedad, fabricada al 8 %. No considera el abarquillado ni la velocidad del cambio.
- **E3, vuelco**: equilibrio de momentos sobre la arista exterior del pie, con y sin las piezas de piedra. Indica si la mesa se desliza antes de volcar (rozamiento 0,4). No considera golpes.
- **E4, unión**: empuje H en el tablero. El momento en cada unión travesaño-montante se resiste con un par hombro-llave, cuyo brazo es la mitad de la altura del travesaño.
  - **Modelo a**: solo resisten esas uniones (conservador).
  - **Modelo b**: el momento se reparte con las uniones montante-cabezal.
  - La llave se calcula como viga corta, cargada en el alto de la espiga y apoyada arriba y abajo. «Cabe» significa: ancho ≤ ½ del espesor de la espiga y profundidad ≤ ⅓ del vuelo.
  - **Es un modelo para comparar versiones con los mismos supuestos, no para dimensionar.** No considera la rigidez real de las uniones ni el apriete de la cuña.
- **E8, flecha de una tabla** (B): tabla biapoyada bajo P en el centro o, con apoyo central, viga continua de dos vanos (Δ = 0,015 P l³/EI) más lo que cede el travesaño bajo el puntal. Con lengüetas sueltas se **supone** que la carga se reparte entre tres tablas.
- **E9, vuelco de una tabla suelta** (B): balancín sobre la arista exterior del cabezal.
- **E2b, juntas entre tablas** (B): cada tabla, clavijada en su eje, crece igual hacia ambos lados. Cada junta cambia b · C · ΔCH.
- **Resistencias**: medias de probeta limpia (FPL, tabla 5-3a) divididas por 3. Para el mármol, MOR de 7 MPa: el extremo bajo del rango, **a confirmar con la ficha del mármol elegido** (EN 12372).

Para pasar a la producción hará falta un cálculo con la norma de mobiliario (EN 12521 / EN 1730) y probetas reales. Ese paso queda en [`../05_consolidar/entregables.md`](../05_consolidar/entregables.md).
