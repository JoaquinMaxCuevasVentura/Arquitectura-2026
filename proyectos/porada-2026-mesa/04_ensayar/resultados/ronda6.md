# Ronda 6 · propuesta final, iteración 1: AB corregida por E12

Generado por `python3 -m mesa` (instrumentos/). Supuestos: P = 1000 N, H = 300 N, CH 4-13 % (fabricación 8 %), límite de flexión de la piedra 2.33 MPa. Geometría común: caballete a 450 mm del extremo, pie de 180 mm.

| Versión | Masa (kg) | Piedra (kg) | K1 madera | K2 piedra a compresión | K3 movimientos | K4 estable sin lastre | K5 ≤ 25 kg |
|---|---|---|---|---|---|---|---|
| **AB** Síntesis candidata | 106.3 | 4.6 | ✓ 99.0% | ✓ flexión máx. en piedra 0.0 MPa (modelo b) / 0.0 MPa (modelo a) | ✓ | ✓ vuelco en extremo sin piedra 2329 N (2.33 × P) | ✓ más pesada: tabla 2 9.7 kg · piedra: collar izq 2.3 kg |
| **F1** Propuesta final | 106.2 | 4.6 | ✓ 99.0% | ✓ flexión máx. en piedra 0.0 MPa (modelo b) / 0.0 MPa (modelo a) | ✓ | ✓ vuelco en extremo sin piedra 2326 N (2.33 × P) | ✓ más pesada: tabla 2 9.7 kg · piedra: collar izq 2.3 kg · caballete izq armado 15.9 kg |

## E8 · E9 · E2b · Tablas (propuesta B)

- **AB** · E8: flecha bajo P 1.04 mm (tabla sola 0.62; asiento del apoyo central 0.83; reparto por lengüetas ÷3) → ✓; flexión en la tabla 3.5 MPa (límite 33.7); en el travesaño 2.8 MPa. E9: una tabla suelta vuelca con 184 N (trabada) → ✓. E2b: tabla de 164 mm, junta 3.0 mm al 8 % → 0.75 mm al 13 % y 4.80 mm al 4 % (varía 2.2 mm entre 6 y 11 %); ancho máximo de tabla 182 mm → ✓.
- **F1** · E8: flecha bajo P 1.04 mm (tabla sola 0.62; asiento del apoyo central 0.83; reparto por lengüetas ÷3) → ✓; flexión en la tabla 3.5 MPa (límite 33.7); en el travesaño 2.8 MPa. E9: una tabla suelta vuelca con 184 N (trabada) → ✓. E2b: tabla de 164 mm, junta 3.0 mm al 8 % → 0.75 mm al 13 % y 4.80 mm al 4 % (varía 2.2 mm entre 6 y 11 %); ancho máximo de tabla 182 mm → ✓.

## E12 · Interferencias (cruces de piezas fuera de los ensambles previstos)

- **AB**: 52 cruces previstos (ensambles), **8 fuera de ensamble**: clavija 3 izq × montante izq (20 × 20 × 40 mm); cuña 3 izq × montante izq (60 × 8 × 15 mm); clavija 3 der × montante der (20 × 20 × 40 mm); cuña 3 der × montante der (60 × 8 × 15 mm); clavija 4 izq × montante izq (20 × 20 × 40 mm); cuña 4 izq × montante izq (60 × 8 × 15 mm); clavija 4 der × montante der (20 × 20 × 40 mm); cuña 4 der × montante der (60 × 8 × 15 mm).
- **F1**: 64 cruces previstos (ensambles), **0 fuera de ensamble**. Piezas encoladas: caballete izq (pie, montante y cabezal encolados) 15.9 kg; caballete der (pie, montante y cabezal encolados) 15.9 kg; apoyo central (puntal y cabezal encolados) 3.6 kg.

## E1 · Piedra como viga

No aplica en esta ronda: ninguna versión usa la piedra como viga.

## E2 · Movimiento de la madera frente a la piedra

- **AB** · espiga en el agujero del collar (alto, z): holgura de fabricación 0.62 mm/lado; junta máxima 1.11 mm/lado → ✓. Sin holgura, la madera hinchada abre la piedra.
- **AB** · espiga en el agujero del collar (espesor, y): holgura de fabricación 0.31 mm/lado; junta máxima 0.55 mm/lado → ✓. Sin holgura, la madera hinchada abre la piedra.
- **F1** · espiga en el agujero del collar (alto, z): holgura de fabricación 0.62 mm/lado; junta máxima 1.11 mm/lado → ✓. Sin holgura, la madera hinchada abre la piedra.
- **F1** · espiga en el agujero del collar (espesor, y): holgura de fabricación 0.31 mm/lado; junta máxima 0.55 mm/lado → ✓. Sin holgura, la madera hinchada abre la piedra.
- Todas: el ancho del tablero (1000 mm) varía 24.7 mm entre 4 y 13 % y 13.7 mm entre 6 y 11 %.

## E3 · Vuelco con y sin piedra (N)

| Versión | Extremo sin / con | Borde sin / con | Horizontal sin / con | ¿Desliza antes? | Aporte piedra | Caballete a ≤ (mm) | o alargar pie (mm) | ¿Retirar «estabiliza»? |
|---|---|---|---|---|---|---|---|---|
| AB | 2329 / 2434 | 3992 / 4173 | 532 / 556 | sí | +5% | 489 | 0 | sí |
| F1 | 2326 / 2431 | 3988 / 4168 | 532 / 556 | sí | +5% | 489 | 0 | sí |

## E4 · La unión (modelo b; entre paréntesis, modelo a, más conservador)

- **AB** · llave de fresno (Fraxinus americana): T = 1023 N (2045); flexión en la llave 8.3 MPa (16.6) frente a un límite de 34.3; profundidad mínima 14 mm (19), cabe hasta 47 → cabe (cabe); apoyo en el montante 0.64 MPa; peso de la llave / rozamiento = 0.002. Collar: compresión 0.08 MPa (0.17); el apoyo en el montante baja de 0.64 a 0.08 MPa.
- **F1** · llave de fresno (Fraxinus americana): T = 1023 N (2045); flexión en la llave 8.3 MPa (16.6) frente a un límite de 34.3; profundidad mínima 14 mm (19), cabe hasta 47 → cabe (cabe); apoyo en el montante 0.64 MPa; peso de la llave / rozamiento = 0.002. Collar: compresión 0.08 MPa (0.17); el apoyo en el montante baja de 0.64 a 0.08 MPa.
