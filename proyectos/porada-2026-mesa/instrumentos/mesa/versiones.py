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


RONDA_1 = (v0, v1, v2, v3)
RONDA_2 = (v0b, v4)
