# Láminas

Borradores de la máquina (Claude, Anthropic), hechos el 24 de octubre de 2026 a pedido de Joaco, para que los verifique y los redibuje a mano. Los criterios se fijaron antes de dibujar y los resultados están en la bitácora (P12).

**No son las figuras del envío.** Las normas de la revista (§6) piden figuras de 16 × 10 cm como máximo, a 300 ppp. Estas láminas están en A4 apaisado: reducidas a ese tamaño, los rótulos quedan entre 2,4 y 3,8 pt. Para el envío se rehacen al tamaño final, con lo explicativo en el pie y rótulos de unos 7 pt o más.

## Qué hay

| Archivo | En el borrador | Qué muestra | Fuentes |
|---|---|---|---|
| `fig1-puentes.svg` | Fig. 1, §1 | Las seis láminas de puentes del atlas de Boitard (27–32): 32 puentes, todos sobre agua dibujada. Abajo, la regla de la p. 238 («rien n'est plus ridicule qu'un pont sans eau») y lo que hizo la copia (Flaubert 1910, 55, 61–62). | B, F |
| `fig2-cotejo.html` | Fig. 2, §3.1 | Seis frases del párrafo de los géneros (Flaubert 1910, 54) frente a sus fuentes en Boitard. La columna de la máquina queda vacía hasta el protocolo limpio. | B, F, G |
| `fig3-dos-jardines.svg` | Fig. 3, §4.2 | Wissous (lám. 18 de Boitard) y Chavignolles reconstruido, a la misma escala supuesta. | B, F, I |
| `fig4-vistas-comedor.svg` | Fig. 4, §4.2 | Lo que se ve desde los dos lugares posibles del comedor, un corte de la ventana al bosquete y el recorrido del agua del estanque. | F, B, I |
| `fig5-escena-exotica.svg` | Fig. 5, §6 | La lámina «Jardin exotique» (Pl. 1ère) con las plantas numeradas en el orden en que Boitard las describe (63–65), los dos frontispicios y lo que pasó a la novela. | B, F, I |

Si el mosaico de imágenes generadas entra en el apartado 5, la escena exótica pasa a ser la Fig. 6. La tabla de fallas no es una lámina: es la Tabla 1 del borrador, con el número de cada falla en la planta.

La Fig. 2 es un HTML de una página (A4 apaisado) porque es una tabla de texto; se abre en el navegador o se pasa a PDF con `render.js`.

## Cómo leerlas

- **Color por fuente:** negro, Flaubert (F); sepia, Boitard (B); rojo, lo inferido (I); azul, la máquina (G).
- **Amarillo:** dónde la copia se aparta de la regla. En las Fig. 1, 4 y 5 es lo que la regla pedía y la copia no hizo; en la Fig. 3, lo que Boitard excluye en un jardín chico y la copia construyó. Cada leyenda lo dice.
- **Líneas:** continua, lo da el texto, también el lugar; discontinua negra, lo da el texto pero el lugar o la medida es supuesto; discontinua roja, supuesto.
- **Números:** Wissous conserva los de Boitard (1–19, en cursiva). En Chavignolles, un círculo abierto tiene equivalente en Wissous; uno lleno (20–29), no.
- **Rótulos** con letra y página: [F 56], [B 68], [I].
- **Qué no demuestran.** Las medidas, las alturas y la escala son supuestas. Que una zona quede oculta en el dibujo dice que el texto la permite, no que existiera.

## Cómo se rehacen

Los programas están en `fuente/`. Hacen falta Python 3 con numpy y Pillow, y Node con Playwright y Chromium.

No van en el repositorio, y hay que bajarlos aparte:

- **Las fuentes**, EB Garamond e IBM Plex Sans Condensed (SIL OFL), en woff2, de `https://cdn.jsdelivr.net/npm/@fontsource/eb-garamond@5.0.8/files/` y `https://cdn.jsdelivr.net/npm/@fontsource/ibm-plex-sans-condensed@5.0.8/files/`: `eb-garamond-latin-400-normal`, `-400-italic`, `-600-normal`, e `ibm-plex-sans-condensed-latin-400-normal` y `-500-normal`. Cada SVG las lleva incrustadas, así que para ver las láminas no hacen falta.
- **Las hojas del atlas** de Boitard (Internet Archive, `A039a019`, ejemplar de la Biblioteca de la Universidad de Sevilla, Public Domain Mark 1.0): la 34 a resolución completa (`page/n34.jpg`, guardada como `n34_full.jpg`), las 88 a 98 a 1600 px (`page/n88_w1600.jpg`, guardadas como `n88.jpg`, etc.) y la 68 a resolución completa para el trazado de Wissous. Los recortes de `boitard.py` están en píxeles de esas versiones.

```sh
cd fuente
node medir_anchos.js FUENTES anchos.json                    # anchos de letra (ya está en el repositorio)
python3 trazar_wissous.py hoja68.jpg wissous_trazado.json   # caminos de la lám. 18 (ya está)
python3 planta.py FUENTES wissous_trazado.json SALIDA       # Fig. 3 y Fig. 4
python3 boitard.py FUENTES ATLAS SALIDA                     # Fig. 1 y Fig. 5
python3 cotejo.py FUENTES SALIDA/fig2-cotejo.html           # Fig. 2
node render.js SALIDA/fig1-puentes.svg SALIDA/fig1-puentes 297 210   # PDF y PNG (escala 3 por defecto)
```

`chavignolles.py` tiene la reconstrucción del jardín (lugares, alturas y el cálculo de lo que se ve desde cada ventana) y lo usa `planta.py`; `svg.py` tiene las ayudas comunes.
