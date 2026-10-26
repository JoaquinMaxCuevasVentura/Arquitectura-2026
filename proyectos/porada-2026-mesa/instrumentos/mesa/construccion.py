"""El modelo constructivo de F1: cada pieza con sus espigas, cajas, ranuras y agujeros, para dibujar los planos.

El instrumento (versiones.py) mide con prismas; aquí los prismas se detallan como se fabrican. Las medidas salen de
versiones.py; lo que no sale de un ensayo es una *decisión de dibujo* y lleva `decision=True` y su porqué.
Ejes: x a lo largo, y a lo ancho, z hacia arriba; mm. Una caja es ((x0, x1), (y0, y1), (z0, z1)).
"""
from dataclasses import dataclass, field

from . import versiones as v

# decisiones de dibujo (no ensayadas): ver 05_consolidar/propuesta_final.md
HOLGURA = 0.5                 # por lado, en cajas y ranuras de piezas sueltas
ESPIGA_CAB = (20, 110)        # espiga montante → cabezal: espesor x, ancho y (una, centrada: libra las clavijas)
ESPIGA_PIE = (20, 80, 30)     # espigas montante → pie: espesor x, ancho y, separación al eje (dos)
REBAJE_PIE = (5, 500)         # el pie apoya en dos puntos: rebaje de 5 mm en los 500 mm centrales (suelo irregular)
HORQUILLA = 40                # el puntal se monta a horcajadas del travesaño: profundidad de la horquilla
RANURA = (8 + 2 * HOLGURA, 15)  # ranura de la lengüeta: alto z, profundidad desde el canto
CHAFLAN_COLLAR = 3
AHUSADO_LLAVE = 40            # la llave pasa de 28 a 28 − 170/40 ≈ 24 mm


def caja(x, y, z):
    return tuple(tuple(sorted(e)) for e in (x, y, z))


@dataclass
class Solido:
    nombre: str
    marca: int                    # número de pieza en el despiece y en las láminas
    material: str                 # "nogal", "fresno", "piedra"
    cajas: list                   # partes positivas
    vacios: list = field(default_factory=list)     # cajas, ranuras y agujeros
    veta: str = "x"               # dirección de la fibra
    grupo: str = ""               # piezas que se arman juntas (para el despiece axonométrico)
    paso: int = 0                 # paso de montaje
    nota: str = ""

    @property
    def envolvente(self):
        return tuple((min(c[i][0] for c in self.cajas), max(c[i][1] for c in self.cajas)) for i in range(3))


def modelo():
    """Los sólidos de F1, en su posición armada."""
    v.configurar(a_extremo=450, pie_x=180)
    L, W, H = v.L, v.W, v.H
    XC, ZC, ZT = v.XC, v.Z_CAB, v.Z_TAB
    mx, my = v.MONTANTE
    px, py, pz = v.PIE
    cx, cy, cz = v.CABEZAL_F1
    te, th, tz = v.TRAV
    ee, eh, _ = v.ESPIGA
    vuelo = 140
    collar = (70, 110, 150)
    d, b, largo = v.LLAVE
    n, junta = 6, 3.0
    bt = (W - (n - 1) * junta) / n
    x_cara = XC + mx / 2
    s = []

    # --- tablas, con su clavija, su cuña y las lengüetas entre ellas
    yc = []
    for i in range(n):
        y0 = -W / 2 + i * (bt + junta)
        yc.append(y0 + bt / 2)
        vacios = []
        if i > 0:                 # ranura en el canto de abajo (y0)
            vacios.append(caja((-L / 2, L / 2), (y0, y0 + RANURA[1]), (ZT + 20 - RANURA[0] / 2, ZT + 20 + RANURA[0] / 2)))
        if i < n - 1:
            vacios.append(caja((-L / 2, L / 2), (y0 + bt - RANURA[1], y0 + bt),
                               (ZT + 20 - RANURA[0] / 2, ZT + 20 + RANURA[0] / 2)))
        for sg in (-1, 1):        # agujero ciego de la clavija, desde abajo
            vacios.append(caja((sg * XC - 10, sg * XC + 10), (yc[i] - 10, yc[i] + 10), (ZT, H - 10)))
        s.append(Solido(f"tabla {i + 1}", 1, "nogal", [caja((-L / 2, L / 2), (y0, y0 + bt), (ZT, H))], vacios,
                        veta="x", grupo=f"tabla {i + 1}", paso=6))
        for sg, lado in ((-1, "izq"), (1, "der")):
            z_cuna = ZC + 25
            s.append(Solido(f"clavija {i + 1} {lado}", 3, "fresno",
                            [caja((sg * XC - 10, sg * XC + 10), (yc[i] - 10, yc[i] + 10), (ZC + 10, H - 10))],
                            [caja((sg * XC - 10, sg * XC + 10), (yc[i] - 4 - HOLGURA, yc[i] + 4 + HOLGURA),
                                  (z_cuna - 7.5, z_cuna + 7.5))],
                            veta="z", grupo=f"tabla {i + 1}", paso=6, nota="encolada en la tabla"))
            s.append(Solido(f"cuña {i + 1} {lado}", 4, "fresno",
                            [caja((sg * XC - 50, sg * XC + 50), (yc[i] - 4, yc[i] + 4), (z_cuna - 7.5, z_cuna + 7.5))],
                            veta="x", grupo=f"cuña {i + 1} {lado}", paso=8))
    for j in range(n - 1):
        yj = -W / 2 + (j + 1) * bt + j * junta + junta / 2
        s.append(Solido(f"lengüeta {j + 1}", 2, "fresno",
                        [caja((-L / 2 + 10, L / 2 - 10), (yj - 15, yj + 15), (ZT + 16, ZT + 24))],
                        veta="x", grupo=f"lengüeta {j + 1}", paso=7))

    # --- caballetes: pie, montante y cabezal encolados
    for sg, lado in ((-1, "izq"), (1, "der")):
        xc = sg * XC
        g = f"caballete {lado}"
        mort_trav = caja((xc - mx / 2, xc + mx / 2), (-ee / 2, ee / 2), (tz - eh / 2, tz + eh / 2))
        s.append(Solido(f"pie {lado}", 5, "nogal",
                        [caja((xc - px / 2, xc + px / 2), (-py / 2, py / 2), (REBAJE_PIE[0], pz)),
                         caja((xc - px / 2, xc + px / 2), (-py / 2, -REBAJE_PIE[1] / 2), (0, REBAJE_PIE[0])),
                         caja((xc - px / 2, xc + px / 2), (REBAJE_PIE[1] / 2, py / 2), (0, REBAJE_PIE[0]))],
                        [caja((xc - ESPIGA_PIE[0] / 2, xc + ESPIGA_PIE[0] / 2), (sy * ESPIGA_PIE[2], sy * (ESPIGA_PIE[2] + ESPIGA_PIE[1])), (REBAJE_PIE[0], pz))
                         for sy in (-1, 1)],
                        veta="y", grupo=g, paso=1))
        s.append(Solido(f"montante {lado}", 6, "nogal",
                        [caja((xc - mx / 2, xc + mx / 2), (-my / 2, my / 2), (pz, ZC))]
                        + [caja((xc - ESPIGA_PIE[0] / 2, xc + ESPIGA_PIE[0] / 2),
                                tuple(sorted((sy * ESPIGA_PIE[2], sy * (ESPIGA_PIE[2] + ESPIGA_PIE[1])))), (REBAJE_PIE[0], pz))
                           for sy in (-1, 1)]
                        + [caja((xc - ESPIGA_CAB[0] / 2, xc + ESPIGA_CAB[0] / 2), (-ESPIGA_CAB[1] / 2, ESPIGA_CAB[1] / 2),
                                (ZC, ZT))],
                        [mort_trav], veta="z", grupo=g, paso=1))
        vac_cab = [caja((xc - ESPIGA_CAB[0] / 2, xc + ESPIGA_CAB[0] / 2), (-ESPIGA_CAB[1] / 2, ESPIGA_CAB[1] / 2), (ZC, ZT))]
        for y in yc:
            vac_cab.append(caja((xc - 10 - HOLGURA, xc + 10 + HOLGURA), (y - 10 - HOLGURA, y + 10 + HOLGURA), (ZC + 10, ZT)))
            vac_cab.append(caja((xc - cx / 2, xc + cx / 2), (y - 4 - HOLGURA, y + 4 + HOLGURA), (ZC + 25 - 7.5, ZC + 25 + 7.5)))
        s.append(Solido(f"cabezal {lado}", 7, "nogal",
                        [caja((xc - cx / 2, xc + cx / 2), (-cy / 2, cy / 2), (ZC, ZT))], vac_cab, veta="y", grupo=g, paso=1))

    # --- travesaño con sus espigas pasantes y la ranura de la llave
    x_llave = x_cara + collar[0]
    trav = [caja((-(XC - mx / 2), XC - mx / 2), (-te / 2, te / 2), (tz - th / 2, tz + th / 2))]
    ranuras = []
    for sg in (-1, 1):
        trav.append(caja(tuple(sorted((sg * (XC - mx / 2), sg * (x_cara + vuelo)))), (-ee / 2, ee / 2), (tz - eh / 2, tz + eh / 2)))
        ranuras.append(caja(tuple(sorted((sg * x_llave, sg * (x_llave + d + HOLGURA)))), (-b / 2 - HOLGURA, b / 2 + HOLGURA),
                            (tz - eh / 2, tz + eh / 2)))
    s.append(Solido("travesaño", 8, "nogal", trav, ranuras, veta="x", grupo="travesaño", paso=2))

    # --- collares de piedra y llaves de fresno
    for sg, lado in ((-1, "izq"), (1, "der")):
        x0, x1 = sorted((sg * x_cara, sg * (x_cara + collar[0])))
        s.append(Solido(f"collar {lado}", 11, "piedra",
                        [caja((x0, x1), (-collar[1] / 2, collar[1] / 2), (tz - collar[2] / 2, tz + collar[2] / 2))],
                        [caja((x0, x1), (-ee / 2 - 1, ee / 2 + 1), (tz - eh / 2 - 1, tz + eh / 2 + 1))],
                        veta="", grupo=f"collar {lado}", paso=3, nota=f"aristas achaflanadas {CHAFLAN_COLLAR} mm"))
        k0, k1 = sorted((sg * x_llave, sg * (x_llave + d)))
        s.append(Solido(f"llave {lado}", 12, "fresno",
                        [caja((k0, k1), (-b / 2, b / 2), (tz - largo / 2, tz + largo / 2))],
                        veta="z", grupo=f"llave {lado}", paso=4, nota=f"ahusada 1:{AHUSADO_LLAVE}"))

    # --- apoyo central: puntal a horcajadas del travesaño, encolado al cabezal central
    z_trav = tz + th / 2
    s.append(Solido("puntal central", 9, "nogal",
                    [caja((-30, 30), (-50, 50), (z_trav - HORQUILLA, ZC)), caja((-10, 10), (-40, 40), (ZC, ZT))],
                    [caja((-30, 30), (-te / 2 - HOLGURA, te / 2 + HOLGURA), (z_trav - HORQUILLA, z_trav))],
                    veta="z", grupo="apoyo central", paso=5))
    s.append(Solido("cabezal central", 10, "nogal", [caja((-cx / 2, cx / 2), (-cy / 2, cy / 2), (ZC, ZT))],
                    [caja((-10, 10), (-40, 40), (ZC, ZT))], veta="y", grupo="apoyo central", paso=5))
    return s


# Pares que pueden cruzarse en el modelo constructivo: los de E12 y los ensambles del caballete y del apoyo central
ENSAMBLES = {frozenset(p) for p in (("travesaño", "montante"), ("travesaño", "collar"), ("llave", "travesaño"),
                                     ("clavija", "tabla"), ("clavija", "cabezal"), ("cuña", "clavija"),
                                     ("cuña", "cabezal"), ("lengüeta", "tabla"), ("montante", "pie"),
                                     ("montante", "cabezal"), ("puntal", "travesaño"), ("puntal", "cabezal"))}


def _cruce(a, b):
    return [min(a[i][1], b[i][1]) - max(a[i][0], b[i][0]) for i in range(3)]


def _dentro(caja_a, vacios):
    """¿La caja cabe en alguno de los vacíos (con 0,1 mm de tolerancia)?"""
    return any(all(v[i][0] - 0.1 <= caja_a[i][0] and caja_a[i][1] <= v[i][1] + 0.1 for i in range(3)) for v in vacios)


def interferencias(solidos=None):
    """E12 sobre el modelo constructivo: dos cruces son error si el par no es un ensamble previsto, o si siéndolo
    la parte que entra no cabe en un vacío de la otra pieza (la espiga sin su caja)."""
    solidos = solidos or modelo()
    errores, previstos = [], 0
    for i, a in enumerate(solidos):
        for b in solidos[i + 1:]:
            for ca in a.cajas:
                for cb in b.cajas:
                    c = _cruce(ca, cb)
                    if min(c) <= 0.1:
                        continue
                    par = frozenset((a.nombre.split()[0], b.nombre.split()[0]))
                    inter = tuple((max(ca[k][0], cb[k][0]), min(ca[k][1], cb[k][1])) for k in range(3))
                    if par in ENSAMBLES and (_dentro(inter, a.vacios) or _dentro(inter, b.vacios)):
                        previstos += 1
                    else:
                        errores.append((a.nombre, b.nombre, tuple(round(x, 1) for x in c)))
    return {"previstos": previstos, "errores": errores}
