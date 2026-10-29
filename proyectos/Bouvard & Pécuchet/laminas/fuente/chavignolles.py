"""El jardín de Chavignolles reconstruido, y lo que se ve desde la casa.

Metros. x crece hacia la derecha mirando desde la casa; y crece desde la
fachada del jardín (y = 0) hacia la celosía del fondo. Cada elemento lleva:

  ev     de dónde sale que exista: F (Flaubert 1910), I (supuesto)
  pags   páginas de Flaubert 1910
  lugar  de dónde sale su lugar: F si el texto lo da, I si es supuesto
  h      altura en metros (I salvo la tumba: «six pieds», F 55)
  estado "antes" (el jardín que encuentran, 26–38), "obras" (55–57) o "ambos"

Lo que lleva I es una elección para poder dibujar, y está escrita en
analisis/planta - datos del texto.md y en la bitácora (P12).
"""
import math

import numpy as np

LADO = 25.0       # I: lado del jardín, igual al largo del tilo (20–30 m)
PISO = 0.8        # I: el piso bajo está sobre una escalinata (perron, F 38, 56)
OJO_PIE = 1.6     # I: ojos de una persona de pie
ALTO_PISO = 3.2   # I: altura del piso bajo
TUMBA_H = 6 * 0.3248   # F 55: «six pieds de hauteur» (pie de rey)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def elipse(cx, cy, rx, ry, n=28):
    return [(cx + rx * math.cos(2 * math.pi * k / n),
             cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def banda(p, q, ancho):
    (x0, y0), (x1, y1) = p, q
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L * ancho / 2, (x1 - x0) / L * ancho / 2
    return [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]


# --- Lugares (todos I salvo donde se indica) ---------------------------------
CASA = rect(1.5, -9.0, 23.5, 0.0)                 # F 28: casa; ancho I
TILO_PIE = (24.2, 18.6)                            # en la charmille (F 56); punto I
TILO_COPA = (2.6, 18.2)                            # hasta la tonnelle (F 61)
VIGNEAU = (4.0, 21.8, 3.4)                         # centro y radio, I
TUMBA = (19.0, 6.5)                                # en la huerta, F 55; cuadro I
ROCA = (12.5, 12.5)                                # en el césped, F 56; césped I
ESTANQUE = (7.2, 15.2)                             # «l'autre partie du potager», F 55
CABANA = rect(20.8, 22.3, 23.3, 24.8)              # «au bout de la charmille», F 38
PERRON = (12.5, 1.6)                               # escalinata, F 38, 56; punto I
# El eco (F 56): «Le tilleul, jusqu'alors, l'avait empêché de se produire»; la
# pagoda mira al granero, «dont le pignon surmontait la charmille». La recta de la
# escalinata al piñón pasa entonces por el pie del tilo, y el piñón cae adelante a
# la derecha, pasado el caminito (I): concuerda con «à droite une grange» (F 26).
# Con la charmille a la izquierda, el granero quedaría a la izquierda.
PIÑON = (PERRON[0] + 2.05 * (TILO_PIE[0] - PERRON[0]),
         PERRON[1] + 2.05 * (TILO_PIE[1] - PERRON[1]))
GRANJA = rect(PIÑON[0], PIÑON[1] - 3.0, PIÑON[0] + 9.0, PIÑON[1] + 3.0)
TEJOS_Y = [3.0, 5.5, 8.0, 10.0, 15.4, 17.2]        # «grande allée», F 57, 61

ELEMENTOS = [
    # nombre, número, ev, páginas, lugar, forma, alto, estado, sólido
    dict(id="muro", nombre="Muro de las espalderas", ev="F", pags="26, 55", lugar="I",
         forma=rect(24.8, 0.0, 25.2, 12.0), h=2.5, estado="antes", solido=True),
    dict(id="muro_a", nombre="Muro (delante de la brecha)", ev="F", pags="55", lugar="I",
         forma=rect(24.8, 0.0, 25.2, 5.0), h=2.5, estado="obras", solido=True),
    dict(id="muro_b", nombre="Muro (detrás de la brecha)", ev="F", pags="55", lugar="I",
         forma=rect(24.8, 8.0, 25.2, 12.0), h=2.5, estado="obras", solido=True),
    dict(id="ruinas", nombre="Brecha, con las ruinas por tierra", num=27, ev="F", pags="55, 61",
         lugar="I", forma=rect(23.9, 5.0, 26.1, 8.0), h=0.8, estado="obras", solido=False),
    dict(id="charmille", nombre="Charmille, con tilos", num=4, ev="F", pags="26, 28, 56, 62",
         lugar="I", forma=rect(23.5, 12.0, 25.0, 25.0), h=3.5, estado="antes", solido=True),
    # en las obras: abierta «çà et là» (F 55; dónde, I) y sin el tilo más grande (F 56)
    dict(id="charmille_1", nombre="Charmille", ev="F", pags="55", lugar="I",
         forma=rect(23.5, 12.0, 25.0, 14.4), h=3.5, estado="obras", solido=True),
    dict(id="charmille_2", nombre="Charmille", ev="F", pags="55", lugar="I",
         forma=rect(23.5, 15.4, 25.0, 18.1), h=3.5, estado="obras", solido=True),
    dict(id="charmille_3", nombre="Charmille", ev="F", pags="55", lugar="I",
         forma=rect(23.5, 19.1, 25.0, 21.4), h=3.5, estado="obras", solido=True),
    dict(id="charmille_4", nombre="Charmille", ev="F", pags="55", lugar="I",
         forma=rect(23.5, 22.4, 25.0, 25.0), h=3.5, estado="obras", solido=True),
    dict(id="tonnelle", nombre="Tonnelle (emparrado)", num=13, ev="F", pags="26, 29, 61, 65",
         lugar="F", forma=rect(0.4, 3.0, 2.8, 18.6), h=2.4, estado="ambos", solido=True),
    dict(id="vigneau", nombre="Vigneau (montículo)", ev="F", pags="26, 29, 56, 63",
         lugar="F", forma=elipse(VIGNEAU[0], VIGNEAU[1], VIGNEAU[2], VIGNEAU[2]),
         h=2.0, estado="ambos", solido=False, terreno=True),
    dict(id="cabana", nombre="Cahute, luego cabaña rústica", num=23, ev="F", pags="38, 55, 61",
         lugar="F", forma=CABANA, h=2.6, estado="ambos", solido=True),
    dict(id="roca", nombre="Roca", num=20, ev="F", pags="56, 61", lugar="I",
         forma=elipse(ROCA[0], ROCA[1], 1.7, 1.4), h=2.2, estado="obras", solido=True),
    dict(id="tumba", nombre="Tumba etrusca", num=21, ev="F", pags="55, 61, 64", lugar="I",
         forma=rect(TUMBA[0] - 0.7, TUMBA[1] - 0.7, TUMBA[0] + 0.7, TUMBA[1] + 0.7),
         h=TUMBA_H, estado="obras", solido=True),
    dict(id="tilo", nombre="Tilo tumbado", num=25, ev="F", pags="56, 61, 65", lugar="F",
         forma=banda(TILO_PIE, TILO_COPA, 0.9), h=1.0, estado="obras", solido=True),
    dict(id="tilo_copa", nombre="Copa seca del tilo", ev="I", pags="56", lugar="I",
         forma=elipse(5.2, 18.3, 2.6, 1.5), h=2.2, estado="obras", solido=False),
    dict(id="puente", nombre="«Rialto» sobre el estanque", num=22, ev="F", pags="55, 61–62",
         lugar="I", forma=rect(5.0, 14.9, 9.4, 15.5), h=1.3, estado="obras", solido=False),
]
for y in TEJOS_Y:
    for x in (11.0, 14.0):
        ELEMENTOS.append(dict(id=f"tejo_{x}_{y}", nombre="Tejo podado", num=24, ev="F",
                              pags="57, 61", lugar="I", forma=elipse(x, y, 0.45, 0.45, 12),
                              h=1.8, estado="ambos", solido=True))

# Lo que es de la propiedad (I en sus medidas): el jardín, el huerto detrás del
# muro y el bosquete detrás de la charmille (F 26: «au delà du mur un verger,
# après la charmille, un bosquet»).
ZONAS = {
    "jardín": rect(0.0, 0.0, LADO, LADO),
    "huerto (verger)": rect(25.2, 0.0, 36.0, 12.0),
    "bosquete": rect(25.0, 12.0, 36.0, LADO),
}

# Ventanas (I): la casa tiene cinco piezas en hilera (F 28: cocina, «petite
# salle», vestíbulo, «deuxième salle plus grande», salón). El comedor («la
# salle», F 59) es la segunda o la cuarta, según el lado de la cocina.
def ventana(x, z):
    return (x, 0.0, z)

Z_BAJO = PISO + OJO_PIE                    # 2,4 m
Z_ALTO = PISO + ALTO_PISO + OJO_PIE        # 5,6 m
OJOS = {
    "comedor, posición 1": [ventana(7.0, Z_BAJO), ventana(9.2, Z_BAJO)],
    "comedor, posición 2": [ventana(15.8, Z_BAJO), ventana(18.0, Z_BAJO)],
    "piso alto": [ventana(x, Z_ALTO) for x in (4.25, 9.75, 15.25, 20.75)],
    "toda la planta baja": [ventana(x, Z_BAJO) for x in (3.7, 7.0, 9.2, 15.8, 18.0, 21.3)]
                           + [(12.5, 1.5, Z_BAJO)],
    "poses del jardín": [(PERRON[0], PERRON[1], Z_BAJO),            # escalinata
                         (VIGNEAU[0], VIGNEAU[1], 2.0 + OJO_PIE),   # café en el vigneau
                         (3.1, 10.0, OJO_PIE)],                     # a la salida de la tonnelle
}


def dentro(pts, poli):
    """Puntos (N×2) dentro de un polígono, par-impar, vectorizado."""
    x, y = pts[:, 0], pts[:, 1]
    res = np.zeros(len(pts), bool)
    n = len(poli)
    for i in range(n):
        (x1, y1), (x2, y2) = poli[i], poli[(i + 1) % n]
        cruza = (y1 > y) != (y2 > y)
        with np.errstate(divide="ignore", invalid="ignore"):
            xc = (x2 - x1) * (y - y1) / (y2 - y1) + x1
        res ^= cruza & (x < xc)
    return res


def obstaculos(estado, sin=()):
    return [e for e in ELEMENTOS
            if e["estado"] in (estado, "ambos") and e["id"] not in sin and e["h"] > 0]


def oculto(ojo, objetivos, z_obj, obs):
    """True donde la línea del ojo al objetivo choca con algún obstáculo."""
    ex, ey, ez = ojo
    d = objetivos - np.array([ex, ey])
    tapado = np.zeros(len(objetivos), bool)
    for o in obs:
        poli = o["forma"]
        if dentro(np.array([[ex, ey]]), poli)[0]:
            continue
        tmin = np.full(len(objetivos), np.inf)
        tmax = np.full(len(objetivos), -np.inf)
        n = len(poli)
        for i in range(n):
            ax, ay = poli[i]
            bx, by = poli[(i + 1) % n]
            exx, eyy = bx - ax, by - ay
            den = d[:, 0] * eyy - d[:, 1] * exx
            with np.errstate(divide="ignore", invalid="ignore"):
                t = ((ax - ex) * eyy - (ay - ey) * exx) / den
                u = ((ax - ex) * d[:, 1] - (ay - ey) * d[:, 0]) / den
            ok = (den != 0) & (t >= 0) & (t <= 1) & (u >= 0) & (u <= 1)
            tmin = np.where(ok, np.minimum(tmin, t), tmin)
            tmax = np.where(ok, np.maximum(tmax, t), tmax)
        cruza = np.isfinite(tmin)
        if o.get("terreno"):
            # el montículo no tapa lo que está encima de él
            cruza &= ~dentro(objetivos, poli)
        za = ez + (z_obj - ez) * np.where(cruza, tmin, 0)
        zb = ez + (z_obj - ez) * np.where(cruza, tmax, 0)
        tapado |= cruza & (o["h"] >= np.minimum(za, zb))
    return tapado


def malla(paso=0.25, x0=-0.5, x1=36.5, y0=-0.5, y1=26.0):
    xs = np.arange(x0 + paso / 2, x1, paso)
    ys = np.arange(y0 + paso / 2, y1, paso)
    X, Y = np.meshgrid(xs, ys)
    return xs, ys, np.column_stack([X.ravel(), Y.ravel()])


def analisis(estado, grupo, paso=0.25, lado_tumba=2.5):
    """Zonas donde una tumba de seis pies no se ve desde ningún ojo del grupo."""
    xs, ys, P = malla(paso)
    obs = obstaculos(estado, sin=("tumba",))
    valido = np.zeros(len(P), bool)
    zona = np.full(len(P), "", object)
    for nombre, poli in ZONAS.items():
        m = dentro(P, poli) & ~valido
        zona[m] = nombre
        valido |= m
    for o in obs:
        if o.get("solido"):
            valido &= ~dentro(P, o["forma"])
    z_suelo = np.where(dentro(P, ELEMENTOS_POR_ID["vigneau"]["forma"]), 2.0, 0.0)
    z_obj = z_suelo + TUMBA_H
    escondido = np.ones(len(P), bool)
    for ojo in OJOS[grupo]:
        escondido &= oculto(ojo, P, z_obj, obs)
    escondido &= valido
    # ¿dónde cabe un cuadrado de lado_tumba todo escondido?
    H = escondido.reshape(len(ys), len(xs)).astype(int)
    k = int(round(lado_tumba / paso))
    I = np.pad(H.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    suma = I[k:, k:] - I[:-k, k:] - I[k:, :-k] + I[:-k, :-k]
    cabe = np.zeros_like(H, bool)
    cabe[k // 2: k // 2 + suma.shape[0], k // 2: k // 2 + suma.shape[1]] = suma == k * k
    return dict(xs=xs, ys=ys, escondido=escondido.reshape(H.shape), cabe=cabe,
                zona=zona.reshape(H.shape), valido=valido.reshape(H.shape), paso=paso)


ELEMENTOS_POR_ID = {e["id"]: e for e in ELEMENTOS}


def resumen(r):
    celda = r["paso"] ** 2
    out = {}
    for nombre in ZONAS:
        en = r["zona"] == nombre
        out[nombre] = dict(
            escondido_m2=round(float((r["escondido"] & en).sum() * celda), 1),
            cabe_tumba=bool((r["cabe"] & en).any()),
        )
    return out


if __name__ == "__main__":
    import json
    for estado in ("antes", "obras"):
        for grupo in OJOS:
            r = analisis(estado, grupo)
            print(estado, "|", grupo, "|", json.dumps(resumen(r), ensure_ascii=False))
