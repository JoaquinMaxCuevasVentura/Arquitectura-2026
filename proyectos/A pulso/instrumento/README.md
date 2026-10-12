# Instrumento de *A pulso*

Herramientas para ordenar los ensayos: imprimir pautas, registrar o digitalizar las repeticiones, superponerlas por condición, medir, hacer láminas y exportar trazos al editor tipográfico. Corresponden a los módulos M1–M4 de la propuesta.

**No hace falta instalar nada.** Basta abrir `index.html` en un navegador (Chrome, Edge, Firefox o Safari). Funciona sin conexión. Los datos no salen del equipo: cada bloque se descarga como un archivo `.json`, y el navegador solo guarda la última configuración y una copia de respaldo de la captura en curso.

## Módulos

| Página | Módulo | Qué hace |
|---|---|---|
| `pautas.html` | — | Pautas A4 con celdas, líneas guía en cian y cuatro marcas de registro, en las alturas de la norma ISO 3098 (5, 10 y 20 mm). Incluye una versión sin líneas guía para la condición C1. |
| `captura.html` | M1 | Captura en tableta con lápiz: posición, tiempo, presión e inclinación de cada repetición, y por lo tanto la **partitura** (orden y dirección de los trazos). Sigue la secuencia del protocolo y numera sola. |
| `digitalizar.html` | M2 | De una foto o un escaneo a trazas: corrige la perspectiva con las marcas, borra la pauta (canal azul), separa las celdas y extrae la línea central. |
| `superponer.html` | M3 · M4 | Repeticiones, densidad y trazo mediano por condición; métricas y partitura más frecuente; medidas a mano; lámina A3; SVG para el atlas; medianos en unidades de fuente para el editor (altura de la mayúscula = 700). |
| `banco.html` | — | Alturas de montaje de las cuatro posiciones del tablero (15°, mesa, pizarra, 45°) para cada cuerpo. |
| `ficha.html` | — | Ficha de ensayo, medidas, lista del piloto, hoja de sesión y consentimiento. |

El espécimen con procedencia (M5) se construye en la fase F6, con los glifos y su clave `apulso.procedencia` (ver `../tipografia/Plan tipográfico.md`).

## Flujo de un bloque en papel

1. Imprimir la pauta a tamaño real y llenar su encabezado.
2. Escribir en el banco con la condición del bloque. En D2 (papel vegetal sobre la pauta), calcar y rellenar antes las cuatro marcas.
3. Escanear la hoja a 600 ppp. Para letras de 10 mm o menos, una foto solo sirve si se toma de cerca, desde arriba y con luz pareja.
4. En **Digitalizar**: elegir la imagen y la pauta, hacer clic en las cuatro marcas (1 arriba a la izquierda, 2 arriba a la derecha, 3 abajo a la derecha, 4 abajo a la izquierda), revisar las celdas y descargar. Se descargan dos archivos: el bloque `.json` y sus filas para `registro_ensayos.csv`.
5. En **Superponer**: abrir los bloques, elegir el gesto y las condiciones, leer, medir e imprimir la lámina.

## Formato de un bloque (`a-pulso.bloque`, versión 1)

```json
{
  "formato": "a-pulso.bloque", "version": 1, "creado": "2026-10-12T16:00:00Z",
  "origen": "tableta | escaneo | sintetico",
  "bloque": {
    "persona": "P00", "sesion": "S01", "condicion": "A2B2",
    "variables": { "A": "A2", "B": "B2", "C": "C0", "D": "D0" },
    "altura_x_mm": 10, "herramienta": "portaminas 0,5 HB", "superficie": "bond",
    "fecha": "2026-10-12", "orden_en_sesion": 2, "pauta": "A4H-h10-L-3x5", "nota": ""
  },
  "ensayos": [
    {
      "id": "AP-P00-S01-A2B2-G5-R01", "gesto": "G5", "repeticion": 1, "calentamiento": false,
      "trazos": [ { "puntos": [[x, y, t, presion, inclinacionX, inclinacionY], …] } ],
      "grosor_mm": 0.62, "componentes": 1,
      "tinta": "data:image/png;base64,…", "tinta_caja": [x0, y0, x1, y1]
    }
  ]
}
```

- **Coordenadas en mm.** `x` se mide desde el borde izquierdo de la celda; `y` hacia arriba desde la línea base. `altura_x_mm` es la altura h de la letra de referencia: en el repertorio técnico, la de la mayúscula. El nombre del campo se conserva por compatibilidad.
- **Tableta:** cada punto lleva `t` (ms desde el primer contacto de la repetición), presión (0–1) e inclinación (grados). Un trazo es un contacto continuo: entre trazos hay un levantamiento.
- **Escaneo:** los puntos son solo `[x, y]` sobre la línea central. No hay orden de trazado ni levantamientos. `grosor_mm` es el área de tinta dividida por el largo de la línea central. `tinta` es la máscara de tinta recortada y `tinta_caja` su ubicación.
- **Calentamiento:** las repeticiones de calentamiento llevan `K` en lugar de `R` en el identificador y no pasan al registro.

## Métricas

| Métrica | Qué mide |
|---|---|
| Ancho, alto, ancho / h, alto / h | Caja de la repetición |
| Bajo la línea base, sobre la altura h | Cuánto se sale de las guías |
| Recorrido | Largo total del trazo (en un escaneo, de la línea central: los retrocesos se superponen y no se cuentan dos veces) |
| Inclinación de las astas | Dirección dominante de los tramos a menos de 30° de la vertical: pico del histograma de ángulos ponderado por el largo, promediado a ±5°. Las diagonales (la pierna de la R) no arrastran la medida. Positiva hacia la derecha |
| Eje de la forma alargada | Eje principal de la nube de puntos; solo si la forma es alargada (razón ≥ 1,8, como un asta) |
| Levantamientos, duración, tiempo en el aire, velocidad, pausas, presión | Solo en tableta. Una pausa es un intervalo de al menos 100 ms bajo 5 mm/s |
| Grosor estimado, manchas separadas | Solo en escaneo |
| Dispersión | Distancia media de la repetición al trazo mediano de su grupo |
| Partitura | Solo en tableta. Orden y dirección de los trazos, por ejemplo «↓ ↘» para una R en dos tiempos: ocho flechas para los trazos abiertos y ↺ ↻ para los que vuelven a su inicio. La tabla muestra la partitura más frecuente y cuántas repeticiones la siguen |

**Trazo mediano:** es la línea central de la región por la que pasa al menos la mitad de las repeticiones, a menos de la tolerancia (por defecto, el 5 % de la altura de la letra). No necesita que las repeticiones se hayan trazado en el mismo orden, por eso sirve igual para escaneos y para tableta. El panel avisa «mediano cortado» cuando esa región tiene más piezas que una repetición típica: las repeticiones están más dispersas que la tolerancia. Hay que subirla y anotarlo, porque eso también es un dato.

## Límites conocidos

- La tinta azul desaparece junto con la pauta. Hay que escribir con grafito o tinta negra.
- Las letras de 10 mm o menos se rectifican a 16 px/mm; una foto lejana no tiene esa resolución. Conviene escanear a 600 ppp.
- Una hoja curvada o con sombras deforma la digitalización. Conviene aplanarla con un vidrio o escanearla.
- Un trazo que se sale de su celda se corta en el borde, y la celda lo avisa («toca el borde»).
- La superficie de la tableta es otra resistencia (variable D): no se mezclan en una misma comparación trazas de tableta y de papel.
- Las métricas sostienen la lectura de las superposiciones, pero no la reemplazan.

## Para desarrollar

```
node pruebas/ejecutar.js              # pruebas del núcleo: geometría, esqueleto, métricas, banco
node pruebas/navegador.js             # pruebas de las páginas en Chromium (requiere Playwright)
node herramientas/generar_ejemplos.js # datos SINTÉTICOS de datos_ejemplo/
node herramientas/generar_planos.js   # planos y plantillas del banco (../banco)
node herramientas/generar_imprimibles.js  # PDF de pautas, fichas y planos
```

- `lib/` contiene el código común. Funciona en el navegador (`window.APulso`) y en node: `nucleo.js` (vocabulario del tablero, identificadores, pautas, registro), `geometria.js`, `imagen.js` (umbral, esqueleto de Zhang–Suen, grafo), `metricas.js` (métricas, partitura, mediano), `banco.js`, `dibujo.js` (SVG de pautas) y `ui.js`.
- **La geometría de las pautas está en un solo lugar** (`nucleo.pautaDesdeCodigo`). La usan la impresión y la digitalización, así que no pueden desalinearse.

## Datos de ejemplo

`datos_ejemplo/` trae cuatro bloques de tableta y dos fotos de hojas A4 **sintéticos** del piloto: I, O y R a 10 mm, en el tablero (BASE) y en la pizarra (A2B2). Son trazas inventadas que sirven para aprender a usar el instrumento. **No son ensayos ni evidencia**, y el instrumento lo avisa cuando se abren. `SINTETICO_marcas.json` trae la posición de las marcas en las fotos.
