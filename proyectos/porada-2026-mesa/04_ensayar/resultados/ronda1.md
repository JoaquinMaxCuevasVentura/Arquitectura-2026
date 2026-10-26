# Ronda 1 · versiones iniciales

Generado por `python3 -m mesa` (instrumentos/). Supuestos: P = 1000 N, H = 300 N, CH 4-13 % (fabricación 8 %), límite de flexión de la piedra 2.33 MPa. Geometría común: caballete a 450 mm del extremo, pie de 80 mm.

| Versión | Masa (kg) | Piedra (kg) | K1 madera | K2 piedra a compresión | K3 movimientos | K4 estable sin lastre | K5 ≤ 25 kg |
|---|---|---|---|---|---|---|---|
| **V0** Lastre (borrador) | 101.9 | 29.4 | ✓ 91.5% | ✗ flexión máx. en piedra 9.9 MPa (modelo b) / 9.9 MPa (modelo a) | ✗ | ✗ vuelco en extremo sin piedra 1372 N (1.37 × P) | ✗ más pesada: barra de piedra 29.4 kg · piedra: barra de piedra 29.4 kg |
| **V1** Llave (cchacuru) | 88.0 | 0.5 | ✓ 99.9% | ✗ flexión máx. en piedra 8.3 MPa (modelo b) / 16.6 MPa (modelo a) | ✓ | ✗ vuelco en extremo sin piedra 1653 N (1.65 × P) | ✗ más pesada: tablero 59.1 kg · piedra: llave izq 0.3 kg |
| **V2** Hincada (chhakhua literal) | 138.2 | 57.2 | ✓ 86.1% | ✓ flexión máx. en piedra 1.4 MPa (modelo b) / 2.9 MPa (modelo a) | ✗ | ✗ vuelco en extremo sin piedra 1652 N (1.65 × P) | ✗ más pesada: tablero 59.1 kg · piedra: pie izq 28.6 kg |
| **V3** Solo madera (control) | 87.6 | 0.0 | ✓ 100.0% | — sin piedra | ✓ | ✗ vuelco en extremo sin piedra 1655 N (1.66 × P) | ✗ más pesada: tablero 59.1 kg |

## E1 · Piedra como viga

- **V0**: luz 1500 mm, sección 160 × 40 mm → σ peso propio 1.12 MPa + σ por P 8.79 MPa = **9.91 MPa** (límite 2.33). ¿Lo salva el mármol más resistente (15/3 = 5 MPa)? **no**. Carga puntual admisible: 138 N.

## E2 · Movimiento de la madera frente a la piedra

- **V0** · barra de piedra entre las dos mitades del tablero: holgura de fabricación 5.75 mm/lado; junta máxima 10.36 mm/lado → ✗. Si cada mitad se fija junto a la piedra, la junta casi no cambia; si se fija en el borde exterior, la junta varía lo indicado.
- **V1** · llave de piedra en la caja de la espiga (ancho): holgura de fabricación 0.11 mm/lado; junta máxima 0.25 mm/lado → ✓. Se fija la piedra a la humedad mínima o se deja holgura de fabricación.
- **V2** · montante en la caja de piedra (ancho, y): holgura de fabricación 1.78 mm/lado; junta máxima 3.21 mm/lado → ✗. Sin holgura, la madera hinchada abre la piedra.
- **V2** · montante en la caja de piedra (espesor, x): holgura de fabricación 0.41 mm/lado; junta máxima 0.74 mm/lado → ✓. Sin holgura, la madera hinchada abre la piedra.
- Todas: el ancho del tablero (1000 mm) varía 24.7 mm entre 4 y 13 % y 13.7 mm entre 6 y 11 %.

## E3 · Vuelco con y sin piedra (N)

| Versión | Extremo sin / con | Borde sin / con | Horizontal sin / con | ¿Desliza antes? | Aporte piedra | Caballete a ≤ (mm) | o alargar pie (mm) | ¿Retirar «estabiliza»? |
|---|---|---|---|---|---|---|---|---|
| V0 | 1372 / 1927 | 2847 / 4000 | 380 / 533 | sí | +40% | 355 | 95 | no |
| V1 | 1653 / 1663 | 3432 / 3452 | 458 / 460 | sí | +1% | 400 | 50 | no |
| V2 | 1652 / 2816 | 3181 / 5423 | 424 / 723 | sí | +71% | 401 | 49 | no |
| V3 | 1655 / 1655 | 3437 / 3437 | 458 / 458 | sí | +0% | 401 | 49 | no |

## E4 · La unión (modelo b; entre paréntesis, modelo a, más conservador)

- **V1** · llave de mármol (catálogo Porada, por elegir): T = 1023 N (2045); flexión en la llave 8.3 MPa (16.6) frente a un límite de 2.3; profundidad mínima 53 mm (75), cabe hasta 37 → no cabe (no cabe); apoyo en el montante 0.64 MPa; peso de la llave / rozamiento = 0.006.
- **V2** · llave de fresno (Fraxinus americana): T = 1023 N (2045); flexión en la llave 8.3 MPa (16.6) frente a un límite de 34.3; profundidad mínima 14 mm (19), cabe hasta 37 → cabe (cabe); apoyo en el montante 0.64 MPa; peso de la llave / rozamiento = 0.002. Paredes de la caja: 1.44 MPa (2.88) frente a 2.33.
- **V3** · llave de fresno (Fraxinus americana): T = 1023 N (2045); flexión en la llave 8.3 MPa (16.6) frente a un límite de 34.3; profundidad mínima 14 mm (19), cabe hasta 37 → cabe (cabe); apoyo en el montante 0.64 MPa; peso de la llave / rozamiento = 0.002.
