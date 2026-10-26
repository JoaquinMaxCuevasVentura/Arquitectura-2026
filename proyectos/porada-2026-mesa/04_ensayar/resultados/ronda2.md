# Ronda 2 · propuesta A, derivadas, con la corrección común de E3

Generado por `python3 -m mesa` (instrumentos/). Supuestos: P = 1000 N, H = 300 N, CH 4-13 % (fabricación 8 %), límite de flexión de la piedra 2.33 MPa. Geometría común: caballete a 450 mm del extremo, pie de 180 mm.

| Versión | Masa (kg) | Piedra (kg) | K1 madera | K2 piedra a compresión | K3 movimientos | K4 estable sin lastre | K5 ≤ 25 kg |
|---|---|---|---|---|---|---|---|
| **V3** Solo madera (control) | 96.4 | 0.0 | ✓ 100.0% | — sin piedra | ✓ | ✓ vuelco en extremo sin piedra 2208 N (2.21 × P) | ✗ más pesada: tablero 59.1 kg |
| **V0b** Lastre asentado | 107.8 | 14.7 | ✓ 96.5% | ✓ flexión máx. en piedra 0.0 MPa (modelo b) / 0.0 MPa (modelo a) | ✓ | ✓ vuelco en extremo sin piedra 2131 N (2.13 × P) | ✗ más pesada: tablero 55.8 kg · piedra: piedra embutida 14.7 kg |
| **V4** Collar | 101.2 | 4.6 | ✓ 98.9% | ✓ flexión máx. en piedra 0.0 MPa (modelo b) / 0.0 MPa (modelo a) | ✓ | ✓ vuelco en extremo sin piedra 2212 N (2.21 × P) | ✗ más pesada: tablero 59.1 kg · piedra: collar izq 2.3 kg |

## E12 · Interferencias (cruces de piezas fuera de los ensambles previstos)

- **V3**: 4 cruces previstos (ensambles), **0 fuera de ensamble**.
- **V0b**: 4 cruces previstos (ensambles), **1 fuera de ensamble**: tablero × piedra embutida (1700 × 160 × 20 mm).
- **V4**: 6 cruces previstos (ensambles), **0 fuera de ensamble**.

## E1 · Piedra como viga

No aplica en esta ronda: ninguna versión usa la piedra como viga.

## E2 · Movimiento de la madera frente a la piedra

- **V0b** · piedra asentada en el canal del tablero (ancho): holgura de fabricación 0.88 mm/lado; junta máxima 1.97 mm/lado → ✓. Se fija la piedra a la humedad mínima o se deja holgura de fabricación.
- **V4** · espiga en el agujero del collar (alto, z): holgura de fabricación 0.62 mm/lado; junta máxima 1.11 mm/lado → ✓. Sin holgura, la madera hinchada abre la piedra.
- **V4** · espiga en el agujero del collar (espesor, y): holgura de fabricación 0.31 mm/lado; junta máxima 0.55 mm/lado → ✓. Sin holgura, la madera hinchada abre la piedra.
- Todas: el ancho del tablero (1000 mm) varía 24.7 mm entre 4 y 13 % y 13.7 mm entre 6 y 11 %.

## E3 · Vuelco con y sin piedra (N)

| Versión | Extremo sin / con | Borde sin / con | Horizontal sin / con | ¿Desliza antes? | Aporte piedra | Caballete a ≤ (mm) | o alargar pie (mm) | ¿Retirar «estabiliza»? |
|---|---|---|---|---|---|---|---|---|
| V3 | 2208 / 2208 | 3785 / 3785 | 505 / 505 | sí | +0% | 475 | 0 | sí |
| V0b | 2131 / 2467 | 3653 / 4229 | 487 / 564 | sí | +16% | 466 | 0 | sí |
| V4 | 2212 / 2317 | 3792 / 3972 | 506 / 530 | sí | +5% | 476 | 0 | sí |

## E4 · La unión (modelo b; entre paréntesis, modelo a, más conservador)

- **V3** · llave de fresno (Fraxinus americana): T = 1023 N (2045); flexión en la llave 8.3 MPa (16.6) frente a un límite de 34.3; profundidad mínima 14 mm (19), cabe hasta 37 → cabe (cabe); apoyo en el montante 0.64 MPa; peso de la llave / rozamiento = 0.002.
- **V0b** · llave de fresno (Fraxinus americana): T = 1023 N (2045); flexión en la llave 8.3 MPa (16.6) frente a un límite de 34.3; profundidad mínima 14 mm (19), cabe hasta 37 → cabe (cabe); apoyo en el montante 0.64 MPa; peso de la llave / rozamiento = 0.002.
- **V4** · llave de fresno (Fraxinus americana): T = 1023 N (2045); flexión en la llave 8.3 MPa (16.6) frente a un límite de 34.3; profundidad mínima 14 mm (19), cabe hasta 47 → cabe (cabe); apoyo en el montante 0.64 MPa; peso de la llave / rozamiento = 0.002. Collar: compresión 0.08 MPa (0.17); el apoyo en el montante baja de 0.64 a 0.08 MPa.
