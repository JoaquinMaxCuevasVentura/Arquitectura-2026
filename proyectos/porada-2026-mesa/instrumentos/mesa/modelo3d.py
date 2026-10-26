"""Exporta una versión a OBJ + MTL (prismas, en metros, eje Y hacia arriba) para modelar y renderizar (D5, Blender, Rhino).

Es una base de masas: los ensambles se dibujan después sobre ella. Los agujeros y cajas no se modelan.
"""
from pathlib import Path

COLORES = {"nogal": (0.55, 0.38, 0.24), "fresno": (0.86, 0.78, 0.62), "marmol": (0.62, 0.64, 0.66)}


def _clave(pieza):
    if pieza.material.es_piedra:
        return "marmol"
    return "fresno" if "fresno" in pieza.material.nombre else "nogal"


def exportar_obj(mesa, carpeta):
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    nombre = mesa.codigo
    mtl = [f"newmtl {k}\nKd {r:.3f} {g:.3f} {b:.3f}\n" for k, (r, g, b) in COLORES.items()]
    (carpeta / f"{nombre}.mtl").write_text("\n".join(mtl), encoding="utf-8")
    lin = [f"# {mesa.codigo} · {mesa.nombre} · unidades: metros", f"mtllib {nombre}.mtl"]
    base = 0
    caras = [(1, 2, 3, 4), (5, 8, 7, 6), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 8, 4), (5, 1, 4, 8)]
    for p in mesa.piezas:
        (x0, x1), (y0, y1), (z0, z1) = p.x, p.y, p.z
        vert = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        lin.append(f"o {p.nombre.replace(' ', '_')}")
        lin.append(f"usemtl {_clave(p)}")
        lin += [f"v {x / 1000:.4f} {z / 1000:.4f} {-y / 1000:.4f}" for x, y, z in vert]   # z del modelo → Y del OBJ
        lin += ["f " + " ".join(str(base + i) for i in c) for c in caras]
        base += 8
    (carpeta / f"{nombre}.obj").write_text("\n".join(lin) + "\n", encoding="utf-8")
    return carpeta / f"{nombre}.obj"
