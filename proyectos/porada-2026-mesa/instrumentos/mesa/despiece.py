"""Despiece de una versión: las piezas iguales agrupadas, con material, medidas, cantidad y masa."""
import re
from collections import OrderedDict

ORDEN = ("tabla", "lengüeta", "clavija", "cuña", "pie", "montante", "cabezal", "travesaño", "puntal", "collar", "llave")


def _tipo(nombre):
    base = re.sub(r"\s*\(.*\)", "", nombre)
    base = re.sub(r"\s+(\d+|izq|der|central)\b", "", base).strip()
    return base


def despiece(mesa):
    """Filas: pieza, material, medidas (largo × ancho × alto, mm), cantidad, masa unitaria y total (kg)."""
    grupos = OrderedDict()
    for p in mesa.piezas:
        nombre = _tipo(p.nombre)
        if p.nombre.startswith("cabezal central"):
            nombre = "cabezal central"
        dims = sorted(((p.x[1] - p.x[0]), (p.y[1] - p.y[0]), (p.z[1] - p.z[0])), reverse=True)
        clave = (nombre, p.material.nombre, tuple(round(d, 1) for d in dims))
        g = grupos.setdefault(clave, {"pieza": nombre, "material": p.material.nombre, "medidas_mm": clave[2],
                                      "cantidad": 0, "masa_kg": p.masa_kg, "funcion": p.funcion})
        g["cantidad"] += 1
    filas = list(grupos.values())
    for f in filas:
        f["masa_total_kg"] = f["masa_kg"] * f["cantidad"]
    filas.sort(key=lambda f: (next((i for i, o in enumerate(ORDEN) if f["pieza"].startswith(o)), 99), f["pieza"]))
    return filas
