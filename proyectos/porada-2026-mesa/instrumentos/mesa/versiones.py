"""Versiones de la mesa. Las de ronda 1 son las de 03_proponer/versiones.md; las de ronda 2 nacen de los ensayos."""
from .geometria import Mesa, Pieza
from .materiales import FRESNO, MARMOL, NOGAL

# Medidas comunes (supuestos de partida, 03_proponer/versiones.md).
L, W, H, T_TAB = 2400, 1000, 750, 40
A_EXTREMO = 450                       # del extremo al eje del caballete
XC = L / 2 - A_EXTREMO                # eje del caballete: ±750
PIE = (80, 800, 90)                   # x, y, z
MONTANTE = (60, 260)                  # x, y
CABEZAL = (80, 850, 60)
TRAV = (45, 110, 300)                 # espesor y, alto z, altura del eje
ESPIGA = (45, 90, 110)                # espesor, alto, vuelo fuera del montante
LLAVE = (28, 20, 170)                 # d (x), b (y), largo (z)

Z_TAB = H - T_TAB                     # cara inferior del tablero: 710
Z_CAB = Z_TAB - CABEZAL[2]            # 650


def configurar(a_extremo=450, pie_x=80):
    """Cambia la geometría común (posición del caballete y ancho del pie) antes de construir versiones."""
    global A_EXTREMO, XC, X_CARA, PIE
    A_EXTREMO, PIE = a_extremo, (pie_x, PIE[1], PIE[2])
    XC = L / 2 - A_EXTREMO
    X_CARA = XC + MONTANTE[0] / 2
    return {"a_extremo_mm": A_EXTREMO, "pie_mm": PIE}


def _caballetes(pie_material=NOGAL, pie=None, z_montante=None):
    pie = pie or PIE
    piezas = []
    for s, lado in ((-1, "izq"), (1, "der")):
        xc = s * XC
        piezas.append(Pieza(f"pie {lado}", pie_material, (xc - pie[0] / 2, xc + pie[0] / 2), (-pie[1] / 2, pie[1] / 2),
                            (0, pie[2]), "apoyo" if not pie_material.es_piedra else "masa"))
        z0 = pie[2] if z_montante is None else z_montante
        piezas.append(Pieza(f"montante {lado}", NOGAL, (xc - MONTANTE[0] / 2, xc + MONTANTE[0] / 2),
                            (-MONTANTE[1] / 2, MONTANTE[1] / 2), (z0, Z_CAB), "apoyo"))
        piezas.append(Pieza(f"cabezal {lado}", NOGAL, (xc - CABEZAL[0] / 2, xc + CABEZAL[0] / 2),
                            (-CABEZAL[1] / 2, CABEZAL[1] / 2), (Z_CAB, Z_TAB), "apoyo"))
    return piezas


def _tablero(vacio=0.0):
    return [Pieza("tablero", NOGAL, (-L / 2, L / 2), (-W / 2, W / 2), (Z_TAB, H), "limite", vacio)]


def _travesano(vuelo=ESPIGA[2]):
    xt = XC + MONTANTE[0] / 2 + vuelo
    return [Pieza("travesaño", NOGAL, (-xt, xt), (-TRAV[0] / 2, TRAV[0] / 2),
                  (TRAV[2] - TRAV[1] / 2, TRAV[2] + TRAV[1] / 2), "apoyo")]


def _llaves(material, x_cara):
    """Llaves verticales que atraviesan la espiga, apoyadas en la cara x_cara (distancia al centro)."""
    d, b, largo = LLAVE
    return [Pieza(f"llave {lado}", material, tuple(sorted((s * x_cara, s * (x_cara + d)))), (-b / 2, b / 2),
                  (TRAV[2] - largo / 2, TRAV[2] + largo / 2), "union")
            for s, lado in ((-1, "izq"), (1, "der"))]


def _nodo_llave(material, vuelo=ESPIGA[2]):
    return {"tipo": "llave", "llave": LLAVE, "material_llave": material,
            "espiga": (ESPIGA[0], ESPIGA[1], vuelo), "h_trav": TRAV[1], "z_trav": TRAV[2]}


X_CARA = XC + MONTANTE[0] / 2         # cara exterior del montante: 780


def v0():
    gap = 80
    piezas = [Pieza("tablero mitad izq", NOGAL, (-L / 2, L / 2), (-W / 2, -gap), (Z_TAB, H), "limite"),
              Pieza("tablero mitad der", NOGAL, (-L / 2, L / 2), (gap, W / 2), (Z_TAB, H), "limite"),
              Pieza("barra de piedra", MARMOL, (-850, 850), (-gap, gap), (Z_TAB, H), "masa")]
    piezas += _caballetes()
    return Mesa("V0", "Lastre (borrador)", "asentar", "la gravedad de la piedra sostiene la ligereza del armazón",
                piezas, {"tipo": "viga", "luz": 2 * XC, "seccion": (2 * gap, T_TAB)},
                [("barra de piedra entre las dos mitades del tablero", (W / 2 - gap), "entre_tablas")])


def v1():
    piezas = _tablero() + _caballetes() + _travesano() + _llaves(MARMOL, X_CARA)
    return Mesa("V1", "Llave (cchacuru)", "acuñar / trabar", "la madera sostiene; la piedra traba",
                piezas, _nodo_llave(MARMOL), [("llave de piedra en la caja de la espiga (ancho)", LLAVE[1], "canal")])


def v2():
    pie = (120, 800, 120)
    caja = (MONTANTE[0], MONTANTE[1], 60)
    piezas = _tablero() + _caballetes(MARMOL, pie, z_montante=pie[2] - caja[2]) + _travesano() + _llaves(FRESNO, X_CARA)
    for p in piezas:
        if p.nombre.startswith("pie"):
            p.vacio_mm3 = caja[0] * caja[1] * caja[2]
    nodo = _nodo_llave(FRESNO) | {"tipo": "caja", "caja": caja, "pie": pie}
    return Mesa("V2", "Hincada (chhakhua literal)", "hincar", "la madera se hinca en la piedra", piezas, nodo,
                [("montante en la caja de piedra (ancho, y)", MONTANTE[1], "agujero"),
                 ("montante en la caja de piedra (espesor, x)", MONTANTE[0], "agujero")])


def v3():
    piezas = _tablero() + _caballetes() + _travesano() + _llaves(FRESNO, X_CARA)
    return Mesa("V3", "Solo madera (control)", "acuñar / trabar", "la misma de V1, sin piedra", piezas, _nodo_llave(FRESNO))


# --- Ronda 2: versiones que nacen de los resultados de la ronda 1 (ver 04_ensayar/bitacora y ensayos) ---

def v0b():
    canal = (1700, 160, 20)
    piezas = _tablero(vacio=canal[0] * canal[1] * canal[2]) + _caballetes() + _travesano() + _llaves(FRESNO, X_CARA)
    piezas.append(Pieza("piedra embutida", MARMOL, (-canal[0] / 2, canal[0] / 2), (-canal[1] / 2, canal[1] / 2),
                        (H - canal[2], H), "masa"))
    return Mesa("V0b", "Lastre asentado", "asentar", "la madera carga la piedra; la piedra se asienta por su peso",
                piezas, _nodo_llave(FRESNO) | {"tipo": "embutido", "canal": canal},
                [("piedra asentada en el canal del tablero (ancho)", canal[1], "canal")], ronda=2)


def v4():
    vuelo = 140
    collar = (70, 110, 150)            # x, y, z
    agujero = (ESPIGA[0] + 2, ESPIGA[1] + 2)
    piezas = _tablero() + _caballetes() + _travesano(vuelo) + _llaves(FRESNO, X_CARA + collar[0])
    for s, lado in ((-1, "izq"), (1, "der")):
        piezas.append(Pieza(f"collar {lado}", MARMOL, tuple(sorted((s * X_CARA, s * (X_CARA + collar[0])))),
                            (-collar[1] / 2, collar[1] / 2), (TRAV[2] - collar[2] / 2, TRAV[2] + collar[2] / 2),
                            "union", collar[0] * agujero[0] * agujero[1]))
    nodo = _nodo_llave(FRESNO, vuelo) | {"tipo": "collar", "collar": collar, "agujero": agujero}
    return Mesa("V4", "Collar", "atravesar / acuñar", "la madera atraviesa la piedra; la piedra queda a compresión",
                piezas, nodo, [("espiga en el agujero del collar (alto, z)", ESPIGA[1], "agujero"),
                               ("espiga en el agujero del collar (espesor, y)", ESPIGA[0], "agujero")], ronda=2)


# --- Propuesta B: tablas sueltas posadas sobre los caballetes (03_proponer/propuesta_B.md) ---

CUNA_EN_CABEZAL = (100, 8, 15)        # cuña pasante en el cabezal (F1): largo x, ancho y, alto z


def _tablas(n, junta, trabadas, cuna="bajo"):
    """n tablas a lo largo, separadas por juntas; cada una ubicada por una clavija en cada cabezal.

    cuna="bajo": la clavija asoma 40 mm bajo el cabezal y la cuña la atraviesa ahí (B2, AB, B3).
    cuna="cabezal": la clavija termina dentro del cabezal y la cuña lo atraviesa a lo largo de x (F1, de E12)."""
    b = (W - (n - 1) * junta) / n
    piezas = []
    for i in range(n):
        y0 = -W / 2 + i * (b + junta)
        piezas.append(Pieza(f"tabla {i + 1}", NOGAL, (-L / 2, L / 2), (y0, y0 + b), (Z_TAB, H), "limite"))
        for s, lado in ((-1, "izq"), (1, "der")):
            yc = y0 + b / 2
            if not trabadas:
                z0 = Z_CAB + 10
            else:
                z0 = Z_CAB - 40 if cuna == "bajo" else Z_CAB + 10
            piezas.append(Pieza(f"clavija {i + 1} {lado}", FRESNO, (s * XC - 10, s * XC + 10), (yc - 10, yc + 10),
                                (z0, H - 10), "union"))
            if trabadas and cuna == "bajo":
                piezas.append(Pieza(f"cuña {i + 1} {lado}", FRESNO, (s * XC - 30, s * XC + 30), (yc - 4, yc + 4),
                                    (Z_CAB - 30, Z_CAB - 15), "union"))
            elif trabadas:
                lx, ly, lz = CUNA_EN_CABEZAL
                zc = Z_CAB + 25
                piezas.append(Pieza(f"cuña {i + 1} {lado}", FRESNO, (s * XC - lx / 2, s * XC + lx / 2),
                                    (yc - ly / 2, yc + ly / 2), (zc - lz / 2, zc + lz / 2), "union"))
    return piezas, b


def _nodo_tablas(n, junta, b, trabadas, lenguetas, apoyo_central, vuelo=ESPIGA[2]):
    return _nodo_llave(FRESNO, vuelo) | {"tipo": "tablas", "tablas": (n, b, T_TAB), "junta": junta, "luz": 2 * XC,
                                         "trabadas": trabadas, "lenguetas": lenguetas, "apoyo_central": apoyo_central,
                                         "trav_seccion": (TRAV[0], TRAV[1])}


def b1():
    n, junta = 5, 5.0
    tablas, b = _tablas(n, junta, trabadas=False)
    piezas = tablas + _caballetes() + _travesano() + _llaves(FRESNO, X_CARA)
    return Mesa("B1", "Tablas posadas", "posar / clavijar", "cada tabla se mueve sola; la mesa muestra la estación",
                piezas, _nodo_tablas(n, junta, b, False, False, False), ronda=3)


def _apoyo_central():
    z_trav = TRAV[2] + TRAV[1] / 2
    return [Pieza("puntal central", NOGAL, (-30, 30), (-50, 50), (z_trav, Z_CAB), "apoyo"),
            Pieza("cabezal central", NOGAL, (-CABEZAL[0] / 2, CABEZAL[0] / 2), (-CABEZAL[1] / 2, CABEZAL[1] / 2),
                  (Z_CAB, Z_TAB), "apoyo")]


def _lenguetas(n, junta, b):
    piezas = []
    for i in range(n - 1):
        yj = -W / 2 + (i + 1) * b + i * junta + junta / 2
        piezas.append(Pieza(f"lengüeta {i + 1}", FRESNO, (-L / 2 + 10, L / 2 - 10), (yj - 15, yj + 15),
                            (Z_TAB + 16, Z_TAB + 24), "union"))
    return piezas


def b2():
    n, junta = 6, 3.0          # de E2b: tablas ≤ 182 mm para que la junta quede entre 0,5 y 5 mm
    tablas, b = _tablas(n, junta, trabadas=True)
    piezas = tablas + _lenguetas(n, junta, b) + _caballetes() + _travesano() + _llaves(FRESNO, X_CARA) + _apoyo_central()
    return Mesa("B2", "Tablas clavijadas", "posar / clavijar / acuñar",
                "cada tabla se mueve sola; la mesa muestra la estación", piezas,
                _nodo_tablas(n, junta, b, True, True, True), ronda=4)


def ab():
    """Síntesis candidata: el tablero de B2 y el collar de piedra de V4."""
    n, junta = 6, 3.0
    vuelo = 140
    collar = (70, 110, 150)
    agujero = (ESPIGA[0] + 2, ESPIGA[1] + 2)
    tablas, b = _tablas(n, junta, trabadas=True)
    piezas = (tablas + _lenguetas(n, junta, b) + _caballetes() + _travesano(vuelo)
              + _llaves(FRESNO, X_CARA + collar[0]) + _apoyo_central())
    for s, lado in ((-1, "izq"), (1, "der")):
        piezas.append(Pieza(f"collar {lado}", MARMOL, tuple(sorted((s * X_CARA, s * (X_CARA + collar[0])))),
                            (-collar[1] / 2, collar[1] / 2), (TRAV[2] - collar[2] / 2, TRAV[2] + collar[2] / 2),
                            "union", collar[0] * agujero[0] * agujero[1]))
    nodo = _nodo_tablas(n, junta, b, True, True, True, vuelo) | {"tipo_union": "collar", "collar": collar,
                                                                "agujero": agujero}
    return Mesa("AB", "Síntesis candidata", "posar / atravesar / acuñar",
                "la madera se mueve y se arma; la piedra es lo único fijo", piezas, nodo,
                [("espiga en el agujero del collar (alto, z)", ESPIGA[1], "agujero"),
                 ("espiga en el agujero del collar (espesor, y)", ESPIGA[0], "agujero")], ronda=4)


def b3():
    """B2 con una tabla de servicio intercambiable: mármol asentado sin cola en la tabla central (de E7)."""
    n, junta = 7, 3.0          # 7 tablas de 140 mm: hay tabla central y E2b sigue cumpliendo
    canal = (1400, 100, 20)
    tablas, b = _tablas(n, junta, trabadas=True)
    central = [p for p in tablas if p.nombre == f"tabla {n // 2 + 1}"][0]
    central.nombre += " (de servicio)"
    central.vacio_mm3 = canal[0] * canal[1] * canal[2]
    yc = central.centro[1]
    piezas = tablas + _lenguetas(n, junta, b) + _caballetes() + _travesano() + _llaves(FRESNO, X_CARA) + _apoyo_central()
    piezas.append(Pieza("mármol asentado", MARMOL, (-canal[0] / 2, canal[0] / 2), (yc - canal[1] / 2, yc + canal[1] / 2),
                        (H - canal[2], H), "masa"))
    return Mesa("B3", "Tablas con tabla de servicio", "posar / clavijar / asentar",
                "cada tabla se mueve sola; una se cambia por otra según el uso", piezas,
                _nodo_tablas(n, junta, b, True, True, True),
                [("mármol asentado en el canal de la tabla central (ancho)", canal[1], "canal")], ronda=5)


def f1():
    """Propuesta final, iteración 1: AB con la cuña pasante en el cabezal (E12) y el caballete encolado."""
    n, junta = 6, 3.0
    vuelo = 140
    collar = (70, 110, 150)
    agujero = (ESPIGA[0] + 2, ESPIGA[1] + 2)
    tablas, b = _tablas(n, junta, trabadas=True, cuna="cabezal")
    piezas = (tablas + _lenguetas(n, junta, b) + _caballetes() + _travesano(vuelo)
              + _llaves(FRESNO, X_CARA + collar[0]) + _apoyo_central())
    for s, lado in ((-1, "izq"), (1, "der")):
        piezas.append(Pieza(f"collar {lado}", MARMOL, tuple(sorted((s * X_CARA, s * (X_CARA + collar[0])))),
                            (-collar[1] / 2, collar[1] / 2), (TRAV[2] - collar[2] / 2, TRAV[2] + collar[2] / 2),
                            "union", collar[0] * agujero[0] * agujero[1]))
    nodo = _nodo_tablas(n, junta, b, True, True, True, vuelo) | {"tipo_union": "collar", "collar": collar,
                                                                "agujero": agujero}
    grupos = {f"caballete {lado} (pie, montante y cabezal encolados)": [f"pie {lado}", f"montante {lado}",
                                                                      f"cabezal {lado}"]
              for lado in ("izq", "der")}
    grupos["apoyo central (puntal y cabezal encolados)"] = ["puntal central", "cabezal central"]
    return Mesa("F1", "Propuesta final", "posar / atravesar / acuñar",
                "la madera se mueve y se arma; lo único fijo es la piedra donde se traba", piezas, nodo,
                [("espiga en el agujero del collar (alto, z)", ESPIGA[1], "agujero"),
                 ("espiga en el agujero del collar (espesor, y)", ESPIGA[0], "agujero")], ronda=6, grupos=grupos)


RONDA_1 = (v0, v1, v2, v3)
RONDA_2 = (v0b, v4)
