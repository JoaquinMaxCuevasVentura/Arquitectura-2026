# Mesa Porada en Blender

Un solo **árbol de Geometry Nodes** («Mesa Porada») genera todas las versiones y la familia a partir de los mismos parámetros. Los materiales son **procedurales**: nogal canaleta, fresno y dos mármoles del catálogo. El render es **Cycles en CPU**, así que corre sin pantalla en la nube. No hay texturas de imagen, y el `.blend` pesa poco.

## Correrlo

**En la nube de GitHub**: pestaña *Actions* → **Porada · Blender** → *Run workflow*. Se elige el número de muestras y, si se quiere, solo algunas tomas. Los renders y el `.blend` quedan como *artifact* de la ejecución. También corre solo cuando cambia algo en esta carpeta. El archivo es [`/.github/workflows/porada-blender.yml`](../../../../.github/workflows/porada-blender.yml).

**En cualquier máquina con Python 3.13**:

```bash
pip install bpy==5.2.3                                   # Blender como módulo de Python
python porada_blender.py                                 # escena + .blend + todas las tomas
python porada_blender.py --solo-blend                    # solo el .blend
python porada_blender.py --muestras 128 --tomas nodo_AB nodo_B2
```

**En Blender 5.2 con interfaz**: abrir [`../../05_consolidar/blender/mesa_porada.blend`](../../05_consolidar/blender/). El objeto **Mesa** tiene el modificador «Mesa Porada», con los parámetros en paneles: *Medidas*, *Tablas (propuesta B)*, *Caballetes*, *Unión (propuesta A)* y *Materiales*. La **Familia** (banco, consola, mesa) está oculta detrás; se ve activando su visibilidad.

## Parámetros del árbol y de dónde salen

| Parámetro | Valor de partida | De dónde sale |
|---|---|---|
| Largo × Ancho × Alto × Espesor | 2,40 × 1,00 × 0,75 × 0,04 m | supuestos comunes (`instrumentos/mesa/versiones.py`) |
| N tablas, Junta | 6 / 7; 3 mm | E2b: tabla ≤ 182 mm, junta entre 0,5 y 5 mm |
| Tabla de servicio | B3: sí | E7 (*Whirl*, *Odette*): componente intercambiable con mármol asentado |
| Extremo a caballete, Ancho del pie | 0,45 m; 0,18 m | E3: corrección común (pie de 180 mm) |
| Apoyo central | sí | E8: flecha ≤ 2 mm |
| Collar de piedra | AB y F1: sí | E4: la piedra solo a compresión |
| Cuña en el cabezal, Cabezal / ancho | F1: sí; 0,9 | E12: la clavija de las tablas centrales caía en el montante; la exterior asomaba por un cabezal de 850 |
| Piedra | Nero Sahara Noir (también Marrone Emperador Dark e ígnea gris mate) | E7: los mármoles de las mesas del catálogo; la ígnea, para comparar con el granito de Comanche (entrada 12 de la bitácora) |

Cada pieza guarda un atributo `veta` (0 = X, 1 = Y, 2 = Z) para que el material oriente la fibra según la pieza: los montantes, verticales; los pies y cabezales, a lo ancho.

## Tomas (en `05_consolidar/renders/`)

| Toma | Para qué |
|---|---|
| `general_B2`, `general_AB`, `general_B3` | comparar las tres candidatas con la misma cámara y la misma luz |
| `nodo_AB`, `nodo_B2` | **E6a**: misma cámara; collar de piedra frente a solo la llave de fresno |
| `junta_0p75`, `junta_3p00`, `junta_4p80` | **E10a**: la junta entre tablas húmeda, en fabricación y seca |
| `general_F1`, `frente_F1`, `nodo_F1`, `cabezal_F1`, `testa_F1`, `planta_F1` | **la propuesta final F1**: lámina 3 y el libro. `cabezal_F1` muestra las 12 cuñas pasantes (E12) |
| `nodo_AB_ignea`, `general_AB_ignea` | **E6a con dos piedras**: el collar de AB en piedra ígnea gris mate, con la misma cámara que `nodo_AB` y `general_AB` |
| `servicio_B3` | la tabla de servicio con mármol asentado |
| `familia` | banco (2 tablas), consola (3 tablas) y mesa B3 (7 tablas), del mismo sistema |

## Qué no es

- **No es el modelo constructivo**: no lleva espigas, cajas ni holguras. Las uniones se ven en su volumen exterior, que es lo que importa para la lectura visual.
- **No reemplaza las maquetas** (E6, E10). Ver [`../../04_ensayar/ensayos.md`](../../04_ensayar/ensayos.md).
- Los mármoles son **aproximaciones procedurales**, no muestras escaneadas. La piedra ígnea es **genérica**: no es el granito de Comanche, del que todavía no hay muestra ni color.
