"""El juego de planos de F1, con cotas, ejes y marcas de pieza. Lo usan las láminas del concurso y el libro.

    cd proyectos/porada-2026-mesa/instrumentos && python3 -m mesa.laminas_f1     # → ../05_consolidar/planos/*.svg
"""
from pathlib import Path

from . import construccion as cons
from . import planos as pl
from . import versiones as v

SALIDA = Path(__file__).resolve().parents[2] / "05_consolidar" / "planos"

# número de pieza: el del despiece y las láminas
PIEZAS = {1: "tabla", 2: "lengüeta", 3: "clavija", 4: "cuña", 5: "pie", 6: "montante", 7: "cabezal",
          8: "travesaño", 9: "puntal", 10: "cabezal central", 11: "collar", 12: "llave"}
PASOS = {1: "se paran los caballetes", 2: "el travesaño atraviesa los montantes",
         3: "los collares de piedra entran en las espigas", 4: "las llaves aprietan la piedra: un golpe de mazo",
         5: "el apoyo central, a horcajadas del travesaño", 6: "las tablas bajan con sus clavijas; las lengüetas entre ellas",
         7: "las cuñas atraviesan el cabezal y traban cada tabla"}

XC = 750
X_CARA, X_COLLAR, X_LLAVE, X_FIN = 780, 850, 878, 920
ZT, H, ZC = 710, 750, 650


def _sol():
    return cons.modelo()


def alzado(escala=10, cotas=True, marcas=True):
    d = pl.Dibujo(escala)
    pl.ortografica(d, _sol(), "frente", ocultos=("travesaño", "llave", "puntal"))
    for x in (-XC, 0, XC):
        d.eje(x, -40, x, H + 60)
    d.linea([(-1300, 0), (1300, 0)], sw=0.25)
    if cotas:
        d.cota_h(-1200, 1200, H + 70, ref=H, lado=1)
        d.cadena_h([-1200, -XC, XC, 1200], -70, ref=0, lado=-1)
        d.cadena_v([0, 90, 300, ZC, ZT, H], -1290, ref=-1200, lado=-1, textos=["90", "210", "350", "60", "40"])
        d.cota_v(0, H, -1390, ref=-1290, lado=-1)
    if marcas:
        for n, (u, w, dx, dy) in {1: (-1000, 730, -4, -7), 7: (-XC + 30, 690, -9, -6), 6: (-XC, 470, -9, 0),
                                  5: (-XC - 60, 45, -10, 3), 8: (-300, 300, 0, 7), 9: (0, 520, 7, 0),
                                  10: (30, 680, 8, -6), 11: (X_CARA + 35, 260, 4, 8), 12: (X_LLAVE - 14, 370, 6, -6),
                                  4: (XC + 45, 675, 8, -5)}.items():
            d.marca(n, u, w, dx, dy)
    return d


def lateral(escala=10, cotas=True, marcas=True):
    d = pl.Dibujo(escala)
    pl.ortografica(d, _sol(), "lado", ocultos=("montante",))
    d.eje(0, -40, 0, H + 60)
    d.linea([(-560, 0), (560, 0)], sw=0.25)
    if cotas:
        d.cota_h(-500, 500, H + 70, ref=H, lado=1)
        d.cota_h(-450, 450, ZC - 70, ref=ZC, lado=-1, ext=False, txt="900")
        d.cota_h(-130, 130, 160, ref=None, lado=1, txt="260")
        d.cota_h(-400, 400, -70, ref=0, lado=-1)
    if marcas:
        for n, (u, w, dx, dy) in {11: (40, 330, 7, -3), 12: (0, 205, -6, 6), 6: (-90, 470, -8, 0),
                                  5: (-300, 45, -5, 6), 7: (-300, 680, -6, -6)}.items():
            d.marca(n, u, w, dx, dy)
    return d


def planta(escala=10, cotas=True, marcas=True, cortes=True):
    d = pl.Dibujo(escala)
    pl.ortografica(d, _sol(), "planta", ocultos=("cabezal", "pie", "travesaño", "collar"))
    for x in (-XC, 0, XC):
        d.eje(x, -560, x, 560)
    d.eje(-1300, 0, 1300, 0)
    if cotas:
        d.cota_h(-1200, 1200, 600, ref=500, lado=1)
        d.cadena_h([-1200, -XC, 0, XC, 1200], -680, ref=-500, lado=-1)
        b = (1000 - 15) / 6
        d.cota_v(-500, 500, 1300, ref=1200, lado=1)
        d.cadena_v([-500, -500 + b, -500 + b + 3], 1240, ref=1200, lado=1, textos=["164", "3"])
    if cortes:
        for x, letra in ((XC, "A"), (815, "B")):
            for y in (-525, 525):
                d.linea([(x, y), (x, y + (50 if y > 0 else -50))], pl.ALMAGRE, 0.45)
                d.texto(x, y + (50 if y > 0 else -50), letra, 2.2, color=pl.ALMAGRE, dy=(3.4 if y < 0 else -1.2))
    if marcas:
        d.marca(1, -1000, -418, -4, 7)
        d.marca(2, -1100, -335, -6, 6)
    return d


def seccion_a(escala=5, cotas=True, marcas=True):
    d = pl.Dibujo(escala)
    pl.ortografica(d, _sol(), "lado", corte=-XC)
    d.eje(0, -30, 0, H + 40)
    d.linea([(-560, 0), (560, 0)], sw=0.25)
    if cotas:
        d.cota_h(-400, 400, -45, ref=0, lado=-1)
        d.cota_h(-250, 250, -18, ref=None, lado=-1, txt="rebaje 500 × 5")
        d.cota_h(-130, 130, 420, ref=None, lado=1)
        d.cota_h(-450, 450, ZC - 35, ref=ZC, lado=-1, ext=False, txt="900")
        d.cadena_v([0, 90, ZC, ZT, H], 540, ref=500, lado=1, textos=["90", "560", "60", "40"])
    if marcas:
        for n, (u, w, dx, dy) in {1: (-420, 730, -3, -8), 2: (-332, 730, 2, -9), 3: (-251, 690, 8, -2),
                                  4: (-247, 675, 9, 6), 7: (-370, 680, -8, 3), 6: (-90, 470, -9, 0),
                                  8: (0, 300, 10, 4), 5: (-300, 45, -6, 7)}.items():
            d.marca(n, u, w, dx, dy)
    return d


def nodo_alzado(escala=2.5, cotas=True, marcas=True):
    d = pl.Dibujo(escala)
    pl.ortografica(d, _sol(), "frente", recorte=(680, 190, 950, 420), ocultos=("travesaño", "llave", "vacios:montante"))
    d.eje(XC, 190, XC, 420)
    d.eje(680, 300, 950, 300)
    if cotas:
        d.cadena_h([720, X_CARA, X_COLLAR, X_LLAVE, X_FIN], 430, ref=385, lado=1, textos=["60", "70", "28", "42"])
        d.cadena_v([225, 255, 345, 375], 960, ref=X_FIN, lado=1, textos=["30", "90", "30"])
        d.cota_v(215, 385, 1000, ref=X_LLAVE, lado=1, txt="170")
        d.cota_v(245, 355, 690, ref=720, lado=-1, txt="110")
    if marcas:
        for n, (u, w, dx, dy) in {6: (750, 400, -8, -4), 11: (815, 240, 2, 10), 12: (864, 380, 6, -6),
                                  8: (900, 330, 8, -6)}.items():
            d.marca(n, u, w, dx, dy)
    return d


def nodo_planta(escala=2.5, cotas=True, marcas=True):
    d = pl.Dibujo(escala)
    pl.ortografica(d, _sol(), "planta", corte=-300, recorte=(680, -85, 950, 85))
    d.eje(XC, -85, XC, 85)
    d.eje(680, 0, 950, 0)
    if cotas:
        d.cadena_h([720, X_CARA, X_COLLAR, X_LLAVE, X_FIN], -100, ref=-55, lado=-1, textos=["60", "70", "28", "42"])
        d.cadena_v([-55, -23.5, 23.5, 55], 960, ref=X_COLLAR, lado=1, textos=["31,5", "47", "31,5"])
        d.cota_v(-22.5, 22.5, 1000, ref=X_FIN, lado=1, txt="45")
    if marcas:
        for n, (u, w, dx, dy) in {6: (735, 60, -6, -6), 11: (815, 40, 2, -9), 12: (864, 6, 6, -9), 8: (905, -10, 7, 7)}.items():
            d.marca(n, u, w, dx, dy)
    return d


def detalle_tablas(escala=2, cotas=True, marcas=True):
    d = pl.Dibujo(escala)
    pl.ortografica(d, _sol(), "lado", corte=-XC, recorte=(-180, 636, 180, 762))
    b = (1000 - 15) / 6
    y3 = -500 + 2 * (b + 3) + b / 2          # eje de la tabla 3
    if cotas:
        d.cadena_h([-1.5 - b, -1.5, 1.5, 1.5 + b], 768, ref=750, lado=1, textos=["164,2", "3", "164,2"])
        d.cadena_v([ZC, ZT, H], 186, ref=180, lado=1, textos=["60", "40"])
        d.cadena_v([ZC + 10, ZT], -186, ref=-180, lado=-1, textos=["50"])
    if marcas:
        for n, (u, w, dx, dy) in {1: (y3 - 40, 742, -4, -7), 2: (0, 730, 3, -9), 3: (y3, 700, -9, 2),
                                  4: (y3 + 3, 675, -9, 6), 7: (y3 - 50, 668, -8, 6), 6: (0, 690, 6, 7)}.items():
            d.marca(n, u, w, dx, dy)
    return d


DESPIECE = {f"tabla {i}": (0, 0, 520) for i in range(1, 7)}
DESPIECE.update({f"lengüeta {j}": (0, 0, 300) for j in range(1, 6)})
DESPIECE.update({f"cuña {i} {lado}": ((-1 if lado == "izq" else 1) * 170, 0, 0) for i in range(1, 7) for lado in ("izq", "der")})
DESPIECE.update({"collar der": (160, 0, 0), "llave der": (300, 0, 150), "collar izq": (-160, 0, 0),
                 "llave izq": (-300, 0, 150), "apoyo central": (0, 0, 160)})


def axon(escala=20, despiece=False, marcas=True):
    d = pl.Dibujo(escala)
    pl.axonometrica(d, _sol(), desplazar=DESPIECE if despiece else None)
    return d


def montaje(paso, escala=40):
    """Lo armado hasta el paso, con lo que entra en ese paso en almagre."""
    sol = [s for s in _sol() if s.paso <= paso]
    nuevos = {s.nombre for s in sol if s.paso == paso}
    d = pl.Dibujo(escala)
    pl.axonometrica(d, sol, resaltar=nuevos, aristas=0.12)
    return d


def juego():
    """Todos los planos de F1 a su escala de lámina: nombre → (dibujo, título, escala)."""
    return {
        "planta": (planta(), "planta", "1:10"),
        "alzado": (alzado(), "alzado", "1:10"),
        "lateral": (lateral(), "alzado lateral", "1:10"),
        "seccion_a": (seccion_a(), "sección A-A, por el eje del caballete", "1:5"),
        "nodo_alzado": (nodo_alzado(), "el nodo: alzado, con lo oculto a trazos", "1:2,5"),
        "nodo_planta": (nodo_planta(), "el nodo: sección horizontal por el eje del travesaño", "1:2,5"),
        "detalle_tablas": (detalle_tablas(), "tablas sobre el cabezal: clavija, cuña y lengüeta", "1:2"),
        "axon": (axon(), "axonometría", "1:20"),
        "despiece": (axon(despiece=True), "despiece axonométrico", "1:20"),
    } | {f"montaje_{k}": (montaje(k), f"paso {k}: {PASOS[k]}", "1:40") for k in PASOS}


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for nombre, (d, titulo, escala) in juego().items():
        (SALIDA / f"{nombre}.svg").write_text(d.svg(3), encoding="utf-8")
    print("planos:", SALIDA)


if __name__ == "__main__":
    main()
