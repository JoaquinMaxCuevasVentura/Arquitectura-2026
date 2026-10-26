# Ronda 3 · propuesta B, versión inicial (con el control V3)

Generado por `python3 -m mesa` (instrumentos/). Supuestos: P = 1000 N, H = 300 N, CH 4-13 % (fabricación 8 %), límite de flexión de la piedra 2.33 MPa. Geometría común: caballete a 450 mm del extremo, pie de 180 mm.

| Versión | Masa (kg) | Piedra (kg) | K1 madera | K2 piedra a compresión | K3 movimientos | K4 estable sin lastre | K5 ≤ 25 kg |
|---|---|---|---|---|---|---|---|
| **V3** Solo madera (control) | 96.4 | 0.0 | ✓ 100.0% | — sin piedra | ✓ | ✓ vuelco en extremo sin piedra 2208 N (2.21 × P) | ✗ más pesada: tablero 59.1 kg |
| **B1** Tablas posadas | 95.5 | 0.0 | ✓ 100.0% | — sin piedra | ✗ | ✗ vuelco en extremo sin piedra 2186 N (2.19 × P) · tabla suelta 219 N | ✓ más pesada: tabla 1 11.6 kg |

## E8 · E9 · E2b · Tablas (propuesta B)

- **B1** · E8: flecha bajo P 5.80 mm (tabla sola 5.80; asiento del apoyo central 0.00; reparto por lengüetas ÷1) → ✗; flexión en la tabla 7.2 MPa (límite 33.7). E9: una tabla suelta vuelca con 219 N (sin trabar) → ✗. E2b: tabla de 196 mm, junta 5.0 mm al 8 % → 2.31 mm al 13 % y 7.15 mm al 4 % (varía 2.7 mm entre 6 y 11 %); ancho máximo de tabla 182 mm → ✗.

## E12 · Interferencias (cruces de piezas fuera de los ensambles previstos)

- **V3**: 4 cruces previstos (ensambles), **0 fuera de ensamble**.
- **B1**: 24 cruces previstos (ensambles), **0 fuera de ensamble**.

## E1 · Piedra como viga

No aplica en esta ronda: ninguna versión usa la piedra como viga.

## E2 · Movimiento de la madera frente a la piedra

- Todas: el ancho del tablero (1000 mm) varía 24.7 mm entre 4 y 13 % y 13.7 mm entre 6 y 11 %.

## E3 · Vuelco con y sin piedra (N)

| Versión | Extremo sin / con | Borde sin / con | Horizontal sin / con | ¿Desliza antes? | Aporte piedra | Caballete a ≤ (mm) | o alargar pie (mm) | ¿Retirar «estabiliza»? |
|---|---|---|---|---|---|---|---|---|
| V3 | 2208 / 2208 | 3785 / 3785 | 505 / 505 | sí | +0% | 475 | 0 | sí |
| B1 | 2186 / 2186 | 3747 / 3747 | 500 / 500 | sí | +0% | 473 | 0 | sí |

## E4 · La unión (modelo b; entre paréntesis, modelo a, más conservador)

- **V3** · llave de fresno (Fraxinus americana): T = 1023 N (2045); flexión en la llave 8.3 MPa (16.6) frente a un límite de 34.3; profundidad mínima 14 mm (19), cabe hasta 37 → cabe (cabe); apoyo en el montante 0.64 MPa; peso de la llave / rozamiento = 0.002.
- **B1** · llave de fresno (Fraxinus americana): T = 1023 N (2045); flexión en la llave 8.3 MPa (16.6) frente a un límite de 34.3; profundidad mínima 14 mm (19), cabe hasta 37 → cabe (cabe); apoyo en el montante 0.64 MPa; peso de la llave / rozamiento = 0.002.
