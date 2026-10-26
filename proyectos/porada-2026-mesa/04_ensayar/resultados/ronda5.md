# Ronda 5 · mejoras desde los precedentes (E7): las dos síntesis posibles

Generado por `python3 -m mesa` (instrumentos/). Supuestos: P = 1000 N, H = 300 N, CH 4-13 % (fabricación 8 %), límite de flexión de la piedra 2.33 MPa. Geometría común: caballete a 450 mm del extremo, pie de 180 mm.

| Versión | Masa (kg) | Piedra (kg) | K1 madera | K2 piedra a compresión | K3 movimientos | K4 estable sin lastre | K5 ≤ 25 kg |
|---|---|---|---|---|---|---|---|
| **B2** Tablas clavijadas | 101.6 | 0.0 | ✓ 100.0% | — sin piedra | ✓ | ✓ vuelco en extremo sin piedra 2325 N (2.32 × P) | ✓ más pesada: tabla 2 9.7 kg |
| **AB** Síntesis candidata | 106.3 | 4.6 | ✓ 99.0% | ✓ flexión máx. en piedra 0.0 MPa (modelo b) / 0.0 MPa (modelo a) | ✓ | ✓ vuelco en extremo sin piedra 2329 N (2.33 × P) | ✓ más pesada: tabla 2 9.7 kg · piedra: collar izq 2.3 kg |
| **B3** Tablas con tabla de servicio | 107.7 | 7.6 | ✓ 98.3% | ✓ flexión máx. en piedra 0.0 MPa (modelo b) / 0.0 MPa (modelo a) | ✓ | ✓ vuelco en extremo sin piedra 2292 N (2.29 × P) | ✓ más pesada: tabla 1 8.3 kg · piedra: mármol asentado 7.6 kg |

## E8 · E9 · E2b · Tablas (propuesta B)

- **B2** · E8: flecha bajo P 1.04 mm (tabla sola 0.62; asiento del apoyo central 0.83; reparto por lengüetas ÷3) → ✓; flexión en la tabla 3.5 MPa (límite 33.7); en el travesaño 2.8 MPa. E9: una tabla suelta vuelca con 184 N (trabada) → ✓. E2b: tabla de 164 mm, junta 3.0 mm al 8 % → 0.75 mm al 13 % y 4.80 mm al 4 % (varía 2.2 mm entre 6 y 11 %); ancho máximo de tabla 182 mm → ✓.
- **AB** · E8: flecha bajo P 1.04 mm (tabla sola 0.62; asiento del apoyo central 0.83; reparto por lengüetas ÷3) → ✓; flexión en la tabla 3.5 MPa (límite 33.7); en el travesaño 2.8 MPa. E9: una tabla suelta vuelca con 184 N (trabada) → ✓. E2b: tabla de 164 mm, junta 3.0 mm al 8 % → 0.75 mm al 13 % y 4.80 mm al 4 % (varía 2.2 mm entre 6 y 11 %); ancho máximo de tabla 182 mm → ✓.
- **B3** · E8: flecha bajo P 1.08 mm (tabla sola 0.73; asiento del apoyo central 0.83; reparto por lengüetas ÷3) → ✓; flexión en la tabla 4.1 MPa (límite 33.7); en el travesaño 2.8 MPa. E9: una tabla suelta vuelca con 157 N (trabada) → ✓. E2b: tabla de 140 mm, junta 3.0 mm al 8 % → 1.08 mm al 13 % y 4.54 mm al 4 % (varía 1.9 mm entre 6 y 11 %); ancho máximo de tabla 182 mm → ✓.

## E12 · Interferencias (cruces de piezas fuera de los ensambles previstos)

- **B2**: 50 cruces previstos (ensambles), **8 fuera de ensamble**: clavija 3 izq × montante izq (20 × 20 × 40 mm); cuña 3 izq × montante izq (60 × 8 × 15 mm); clavija 3 der × montante der (20 × 20 × 40 mm); cuña 3 der × montante der (60 × 8 × 15 mm); clavija 4 izq × montante izq (20 × 20 × 40 mm); cuña 4 izq × montante izq (60 × 8 × 15 mm); clavija 4 der × montante der (20 × 20 × 40 mm); cuña 4 der × montante der (60 × 8 × 15 mm).
- **AB**: 52 cruces previstos (ensambles), **8 fuera de ensamble**: clavija 3 izq × montante izq (20 × 20 × 40 mm); cuña 3 izq × montante izq (60 × 8 × 15 mm); clavija 3 der × montante der (20 × 20 × 40 mm); cuña 3 der × montante der (60 × 8 × 15 mm); clavija 4 izq × montante izq (20 × 20 × 40 mm); cuña 4 izq × montante izq (60 × 8 × 15 mm); clavija 4 der × montante der (20 × 20 × 40 mm); cuña 4 der × montante der (60 × 8 × 15 mm).
- **B3**: 58 cruces previstos (ensambles), **5 fuera de ensamble**: tabla 4 (de servicio) × mármol asentado (1400 × 100 × 20 mm); clavija 4 izq × montante izq (20 × 20 × 40 mm); cuña 4 izq × montante izq (60 × 8 × 15 mm); clavija 4 der × montante der (20 × 20 × 40 mm); cuña 4 der × montante der (60 × 8 × 15 mm).

## E1 · Piedra como viga

No aplica en esta ronda: ninguna versión usa la piedra como viga.

## E2 · Movimiento de la madera frente a la piedra

- **AB** · espiga en el agujero del collar (alto, z): holgura de fabricación 0.62 mm/lado; junta máxima 1.11 mm/lado → ✓. Sin holgura, la madera hinchada abre la piedra.
- **AB** · espiga en el agujero del collar (espesor, y): holgura de fabricación 0.31 mm/lado; junta máxima 0.55 mm/lado → ✓. Sin holgura, la madera hinchada abre la piedra.
- **B3** · mármol asentado en el canal de la tabla central (ancho): holgura de fabricación 0.55 mm/lado; junta máxima 1.23 mm/lado → ✓. Se fija la piedra a la humedad mínima o se deja holgura de fabricación.
- Todas: el ancho del tablero (1000 mm) varía 24.7 mm entre 4 y 13 % y 13.7 mm entre 6 y 11 %.

## E3 · Vuelco con y sin piedra (N)

| Versión | Extremo sin / con | Borde sin / con | Horizontal sin / con | ¿Desliza antes? | Aporte piedra | Caballete a ≤ (mm) | o alargar pie (mm) | ¿Retirar «estabiliza»? |
|---|---|---|---|---|---|---|---|---|
| B2 | 2325 / 2325 | 3985 / 3985 | 531 / 531 | sí | +0% | 489 | 0 | sí |
| AB | 2329 / 2434 | 3992 / 4173 | 532 / 556 | sí | +5% | 489 | 0 | sí |
| B3 | 2292 / 2465 | 3929 / 4225 | 524 / 563 | sí | +8% | 485 | 0 | sí |

## E4 · La unión (modelo b; entre paréntesis, modelo a, más conservador)

- **B2** · llave de fresno (Fraxinus americana): T = 1023 N (2045); flexión en la llave 8.3 MPa (16.6) frente a un límite de 34.3; profundidad mínima 14 mm (19), cabe hasta 37 → cabe (cabe); apoyo en el montante 0.64 MPa; peso de la llave / rozamiento = 0.002.
- **AB** · llave de fresno (Fraxinus americana): T = 1023 N (2045); flexión en la llave 8.3 MPa (16.6) frente a un límite de 34.3; profundidad mínima 14 mm (19), cabe hasta 47 → cabe (cabe); apoyo en el montante 0.64 MPa; peso de la llave / rozamiento = 0.002. Collar: compresión 0.08 MPa (0.17); el apoyo en el montante baja de 0.64 a 0.08 MPa.
- **B3** · llave de fresno (Fraxinus americana): T = 1023 N (2045); flexión en la llave 8.3 MPa (16.6) frente a un límite de 34.3; profundidad mínima 14 mm (19), cabe hasta 37 → cabe (cabe); apoyo en el montante 0.64 MPa; peso de la llave / rozamiento = 0.002.
