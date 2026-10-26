"""Compara los ciclos de cada puesto para probar H1: «la secuencia es estable».

Decisión que permite (analisis/02, sección 3): si en dos de los tres puestos
menos de 7 de cada 10 operaciones se repiten en el mismo orden entre ciclos,
la tesis pasa de «secuencia» a «repertorio». Se usa el promedio entre pares
de ciclos; un par bajo el umbral (un día de lluvia, otra persona) se señala
como desviación que hay que explicar, no como inestabilidad.

Cada operación es «verbo:elemento». Las repeticiones seguidas de la misma
operación (apilar:caja, apilar:caja…) cuentan como una sola: importa el orden,
no cuántas cajas hay. La medida es la subsecuencia común más larga entre dos
ciclos dividida por el largo del ciclo más largo.

Uso:  python3 comparar_ciclos.py [registro_de_operaciones.csv] [--umbral 0.7]
"""

import csv
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path


def leer(ruta):
    ciclos = defaultdict(list)  # (puesto, fase, ciclo) -> [(orden, operación)]
    with open(ruta, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            if not fila["verbo"].strip():
                continue
            operacion = f'{fila["verbo"].strip().lower()}:{fila["elemento"].strip().lower()}'
            clave = (fila["puesto"].strip(), fila["fase"].strip().lower(), fila["ciclo"].strip())
            ciclos[clave].append((int(fila["orden"]), operacion))
    secuencias = {}
    for clave, filas in ciclos.items():
        seq = [op for _, op in sorted(filas)]
        secuencias[clave] = [op for i, op in enumerate(seq) if i == 0 or op != seq[i - 1]]
    return secuencias


def subsecuencia_comun(a, b):
    tabla = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            tabla[i + 1][j + 1] = tabla[i][j] + 1 if x == y else max(tabla[i][j + 1], tabla[i + 1][j])
    comun, i, j = [], len(a), len(b)
    while i and j:
        if a[i - 1] == b[j - 1]:
            comun.append(a[i - 1])
            i, j = i - 1, j - 1
        elif tabla[i - 1][j] >= tabla[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return comun[::-1]


def main():
    args = sys.argv[1:]
    umbral = 0.7
    if "--umbral" in args:
        k = args.index("--umbral")
        umbral = float(args[k + 1])
        del args[k:k + 2]
    ruta = Path(args[0]) if args else Path(__file__).with_name("registro_de_operaciones.csv")
    secuencias = leer(ruta)
    if not secuencias:
        print(f"{ruta}: todavía no hay operaciones registradas.")
        return

    por_puesto = defaultdict(dict)
    for (puesto, fase, ciclo), seq in secuencias.items():
        por_puesto[(puesto, fase)][ciclo] = seq

    estables = {}
    for (puesto, fase), ciclos in sorted(por_puesto.items()):
        print(f"\n{puesto} · {fase} · {len(ciclos)} ciclo(s)")
        if len(ciclos) < 2:
            print("  Hace falta al menos un segundo ciclo para comparar.")
            continue
        proporciones = []
        for (c1, s1), (c2, s2) in combinations(sorted(ciclos.items()), 2):
            comun = subsecuencia_comun(s1, s2)
            p = len(comun) / max(len(s1), len(s2))
            proporciones.append(p)
            print(f"  {c1} frente a {c2}: {len(comun)} de {max(len(s1), len(s2))} en el mismo orden ({p:.0%})")
        promedio = sum(proporciones) / len(proporciones)
        estables[(puesto, fase)] = promedio >= umbral
        nucleo = list(ciclos.values())[0]
        for seq in list(ciclos.values())[1:]:
            nucleo = subsecuencia_comun(nucleo, seq)
        print(f"  Núcleo común a todos los ciclos: {' → '.join(nucleo) or '(ninguno)'}")
        print(f"  Promedio: {promedio:.0%} → {'estable' if estables[(puesto, fase)] else 'no estable'} (umbral {umbral:.0%})")
        if min(proporciones) < umbral <= promedio:
            print("  Un par queda bajo el umbral: es una desviación que hay que explicar (¿lluvia? ¿otra persona?).")

    for fase in sorted({f for _, f in estables}):
        puestos = [p for (p, f) in estables if f == fase]
        n_estables = sum(estables[(p, fase)] for p in puestos)
        print(f"\nH1, {fase}: {n_estables} de {len(puestos)} puestos con secuencia estable.", end=" ")
        if len(puestos) - n_estables >= 2:
            print("H1 cae en esta fase: revisar «secuencia» frente a «repertorio» (analisis/02).")
        elif len(puestos) < 3:
            print("Faltan puestos para decidir.")
        else:
            print("H1 se sostiene en esta fase.")


if __name__ == "__main__":
    main()
