"""Ensayos E1-E4 y criterios K1-K5. Unidades: mm, N, MPa (N/mm2), kg.

Cada función devuelve un dict plano para volcarlo a JSON y a la tabla de resultados.
Los modelos son deliberadamente simples: sirven para comparar versiones bajo los mismos supuestos,
no para dimensionar la pieza final (ver «qué no demuestra» en 04_ensayar/ensayos.md).
"""
import math
from math import sqrt

from .materiales import MARMOL, NOGAL
from .versiones import CABEZAL, H, L, W

G = 9.81

# Supuestos comunes (04_ensayar/ensayos.md, fijados antes de calcular).
P_REF = 1000.0          # N, vertical en el punto más desfavorable
H_REF = 300.0           # N, horizontal a la altura del tablero
MU_SUELO = 0.4          # rozamiento madera-suelo, para saber si desliza antes de volcar
CH = (8.0, 4.0, 13.0)   # % de contenido de humedad: fabricación, mínimo, máximo
JUNTA_MAX = 3.0         # mm por lado (K3)
PESO_MAX = 25.0         # kg por pieza (K5)
MADERA_MIN = 0.85       # fracción de volumen en madera (K1)
LIM_PIEDRA = MARMOL.diseno(MARMOL.mor)   # 2,33 MPa (K2)
FLECHA_MAX = 2.0        # mm bajo P sobre una tabla (E8, propuesta B)
JUNTA_TABLAS = (0.5, 5.0)  # mm, rango admisible de la junta entre tablas (E2b)
N_LENGUETAS = 3         # supuesto: con lengüetas, una carga la reparten tres tablas


def e1_viga_piedra(mesa, P=P_REF):
    """Barra de piedra biapoyada: peso propio + carga puntual en el centro."""
    n = mesa.nodo
    if n.get("tipo") != "viga":
        return None
    b, h = n["seccion"]
    luz = n["luz"]
    q = MARMOL.densidad * G * b * h * 1e-9          # N/mm
    S = b * h ** 2 / 6
    sig_q = q * luz ** 2 / 8 / S
    sig_p = P * luz / 4 / S
    total = sig_q + sig_p
    return {"luz_mm": luz, "seccion_mm": f"{b:.0f} × {h:.0f}", "sigma_peso": sig_q, "sigma_P": sig_p,
            "sigma_total": total, "limite_diseno": LIM_PIEDRA, "cumple": total <= LIM_PIEDRA,
            "algun_marmol_la_salva": total <= MARMOL.mor_alto / 3,
            "P_admisible_N": max(0.0, (LIM_PIEDRA - sig_q) * S * 4 / luz)}


def e2_movimiento(mesa, ch=CH, coef=NOGAL.ct):
    """Holguras por lado para cada junta piedra-madera (coeficiente tangencial: peor caso)."""
    fab, mn, mx = ch
    filas = []
    for desc, ancho, tipo in mesa.juntas:
        seca, humeda = ancho * coef * (fab - mn), ancho * coef * (mx - fab)
        if tipo == "canal":            # la madera que forma el canal lo estrecha al secarse
            holgura, maxima = seca / 2, (seca + humeda) / 2
            nota = "se fija la piedra a la humedad mínima o se deja holgura de fabricación"
        elif tipo == "agujero":        # la madera se hincha dentro de la piedra
            holgura, maxima = humeda / 2, (seca + humeda) / 2
            nota = "sin holgura, la madera hinchada abre la piedra"
        else:                          # entre_tablas: depende de dónde se fija cada mitad del tablero
            holgura, maxima = humeda, seca + humeda
            nota = ("si cada mitad se fija junto a la piedra, la junta casi no cambia; "
                    "si se fija en el borde exterior, la junta varía lo indicado")
        filas.append({"junta": desc, "ancho_mm": ancho, "holgura_fabricacion_por_lado": holgura,
                      "junta_maxima_por_lado": maxima, "cumple": maxima <= JUNTA_MAX, "nota": nota})
    tablero = {"extremos_4_13": W * coef * (mx - mn), "estacional_6_11": W * coef * 5}
    return {"juntas": filas, "ancho_tablero_mm": tablero, "encolado_a_contraveta": False}


def _vuelco(mesa, sin_piedra, P, Hh, mu):
    m = mesa.masa(sin_piedra)
    peso = m * G
    xg, yg, _ = mesa.cdg(sin_piedra)
    pies = mesa.piezas_de("pie ")
    x_eje = max(p.x[1] for p in pies)
    y_eje = max(p.y[1] for p in pies)
    f_ext = peso * (x_eje - xg) / (L / 2 - x_eje)
    f_lat = peso * (y_eje - yg) / (W / 2 - y_eje) if W / 2 > y_eje else float("inf")
    f_h = peso * (y_eje - yg) / H
    return {"masa_kg": m, "vuelco_extremo_N": f_ext, "vuelco_borde_N": f_lat, "vuelco_horizontal_N": f_h,
            "desliza_antes_de_volcar": mu * peso < f_h, "x_eje": x_eje, "peso_N": peso, "xg": xg}


def e3_vuelco(mesa, P=P_REF, Hh=H_REF, mu=MU_SUELO):
    con = _vuelco(mesa, False, P, Hh, mu)
    sin = _vuelco(mesa, True, P, Hh, mu)
    aporte = {k: (con[k] / sin[k] - 1) for k in ("vuelco_extremo_N", "vuelco_borde_N", "vuelco_horizontal_N")}
    # Distancia máxima del extremo al eje del caballete para resistir 2P sin piedra.
    ancho_pie = 2 * (sin["x_eje"] - max(p.centro[0] for p in mesa.piezas_de("pie ")))
    u = sin["peso_N"] * (L / 2 - sin["xg"]) / (2 * P + sin["peso_N"])
    # Alternativa sin mover el caballete: alargar el pie hacia el extremo hasta esta arista.
    x_eje_2p = (2 * P * L / 2 + sin["peso_N"] * sin["xg"]) / (2 * P + sin["peso_N"])
    sin_ok = (sin["vuelco_extremo_N"] >= 2 * P and sin["vuelco_borde_N"] >= 2 * P
              and (sin["desliza_antes_de_volcar"] or sin["vuelco_horizontal_N"] >= 2 * Hh))
    return {"con_piedra": con, "sin_piedra": sin, "aporte_piedra": aporte,
            "sin_piedra_ya_resiste_2x": sin_ok, "a_max_para_2P_mm": u + ancho_pie / 2,
            "alargar_pie_para_2P_mm": max(0.0, x_eje_2p - sin["x_eje"]),
            "retirar_frase_estabiliza": sin_ok and max(aporte.values()) < 0.25}


def _traccion_espiga(n, Hh):
    """Tracción en la llave por balanceo longitudinal. Dos modelos de pórtico (ver instrumentos/README.md)."""
    brazo = n["h_trav"] / 2
    return {"a": Hh * H / 2 / brazo, "b": Hh * H / 4 / brazo}


def e4_union(mesa, Hh=H_REF, mu=MU_SUELO):
    n = mesa.nodo
    if "llave" not in n:
        return None
    d, b, largo = n["llave"]
    e_esp, h_esp, vuelo = n["espiga"]
    mat = n["material_llave"]
    lim = mat.diseno(mat.mor)
    apoyo = (largo - h_esp) / 2
    coef_m = (h_esp + apoyo) / 4 - h_esp / 8          # viga corta con carga repartida en el alto de la espiga
    S = b * d ** 2 / 6
    union = n.get("tipo_union", n["tipo"])
    x_llave = n["collar"][0] if union == "collar" else 0.0
    peso_llave = mat.densidad * d * b * largo * 1e-9 * G
    out = {"material_llave": mat.nombre, "limite_llave": lim, "modelos": {}}
    for modelo, T in _traccion_espiga(n, Hh).items():
        d_min = sqrt(6 * T * coef_m / (lim * b))
        r = {"T_N": T, "sigma_llave": T * coef_m / S, "cumple_llave": T * coef_m / S <= lim,
             "d_min_mm": d_min, "d_max_que_cabe_mm": vuelo / 3, "b_max_que_cabe_mm": e_esp / 2,
             "cabe": d_min <= vuelo / 3 and b <= e_esp / 2,
             "apoyo_llave_MPa": T / (2 * apoyo * b),
             "corte_cabeza_espiga_MPa": T / (2 * (vuelo - x_llave - d) * h_esp),
             "peso_llave_sobre_rozamiento": peso_llave / (mu * T)}
        if union == "collar":
            cx, cy, cz = n["collar"]
            ax, az = n["agujero"]
            r["compresion_collar_MPa"] = T / (cy * cz - ax * az)
            r["apoyo_montante_con_collar_MPa"] = r["compresion_collar_MPa"]
            r["apoyo_montante_sin_collar_MPa"] = r["apoyo_llave_MPa"]
        if n["tipo"] == "caja":
            prof = n["caja"][2]
            pared = (n["pie"][0] - n["caja"][0]) / 2
            M = Hh * H / (2 if modelo == "a" else 4)
            m_lineal = M / (2 / 3 * prof) * (2 / 3 * prof) / n["caja"][1]
            r["sigma_pared_caja"] = m_lineal / (pared ** 2 / 6)
            r["cumple_pared"] = r["sigma_pared_caja"] <= LIM_PIEDRA
        out["modelos"][modelo] = r
    return out


def e8_flecha_tablas(mesa, P=P_REF):
    """Flecha de una tabla bajo P en el centro de su vano; con apoyo central, viga continua de dos vanos."""
    n = mesa.nodo
    if n.get("tipo") != "tablas":
        return None
    _, b, t = n["tablas"]
    luz = n["luz"]
    EI = NOGAL.moe * b * t ** 3 / 12
    S = b * t ** 2 / 6
    if n["apoyo_central"]:
        l = luz / 2
        flecha = 0.015 * P * l ** 3 / EI                    # dos vanos iguales, carga en el centro de uno
        momento = 0.203 * P * l
        R = 0.6875 * P                                      # reacción en el apoyo central
        bt, ht = n["trav_seccion"]
        asiento = R * luz ** 3 / (48 * NOGAL.moe * bt * ht ** 3 / 12)   # el travesaño cede bajo el puntal
    else:
        flecha, momento, asiento = P * luz ** 3 / (48 * EI), P * luz / 4, 0.0
    reparto = N_LENGUETAS if n["lenguetas"] else 1
    total = flecha / reparto + asiento
    sig_trav = (R * luz / 4) / (bt * ht ** 2 / 6) if n["apoyo_central"] else 0.0
    return {"flecha_tabla_sola_mm": flecha, "asiento_apoyo_central_mm": asiento, "reparto_lenguetas": reparto,
            "sigma_travesano": sig_trav,
            "flecha_total_mm": total, "escalon_entre_tablas_mm": 0.0 if n["lenguetas"] else flecha,
            "sigma_tabla": momento / S, "limite_tabla": NOGAL.diseno(NOGAL.mor), "cumple": total <= FLECHA_MAX}


def e9_vuelco_tabla(mesa, P=P_REF):
    """Una tabla sola, sin trabar, como balancín sobre la arista exterior del cabezal."""
    n = mesa.nodo
    if n.get("tipo") != "tablas":
        return None
    tabla = mesa.piezas_de("tabla ")[0]
    cab = max(p.x[1] for p in mesa.piezas_de("cabezal "))
    f = tabla.masa_kg * G * (cab - tabla.centro[0]) / (L / 2 - cab)
    return {"masa_tabla_kg": tabla.masa_kg, "vuelco_tabla_suelta_N": f, "trabadas": n["trabadas"],
            "cumple": n["trabadas"] or f >= 2 * P}


def e2b_juntas_tablas(mesa, ch=CH, coef=NOGAL.ct):
    """Cada tabla, clavijada en su eje, crece hacia los dos lados: cada junta cambia b·C·ΔCH."""
    n = mesa.nodo
    if n.get("tipo") != "tablas":
        return None
    fab, mn, mx = ch
    _, b, _ = n["tablas"]
    g = n["junta"]
    humeda, seca = g - b * coef * (mx - fab), g + b * coef * (fab - mn)
    lo, hi = JUNTA_TABLAS
    return {"ancho_tabla_mm": b, "junta_nominal_mm": g, "junta_humeda_mm": humeda, "junta_seca_mm": seca,
            "estacional_6_11_mm": b * coef * 5, "ancho_tabla_max_mm": (hi - lo) / (coef * (mx - mn)),
            "junta_nominal_admisible_mm": (lo + b * coef * (mx - fab), hi - b * coef * (fab - mn)),
            "cumple": humeda >= lo and seca <= hi}


def e11_cuna_gravedad(masas_kg=(5.0, 18.0, 29.4), angulo=15.0, rozamientos=(0.0, 0.2, 0.4, 0.5),
                      asiento_mm=150.0, ch=CH, coef=NOGAL.ct, Hh=H_REF):
    """Piedra asentada en una cuña de ángulo α respecto de la vertical, que empuja dos tirantes por su peso.

    Equilibrio a punto de bajar (el rozamiento se opone): W = 2N(sen α + μ cos α); empuje por lado H = N(cos α − μ sen α).
    Con μ ≥ cot α la piedra no baja: se queda colgada y el empuje lo da el apriete inicial, no la gravedad.
    """
    a = math.radians(angulo)
    T = _traccion_espiga({"h_trav": 110.0}, Hh)            # misma demanda que E4
    filas = []
    for m in masas_kg:
        W = m * G
        for mu in rozamientos:
            N = W / (2 * (math.sin(a) + mu * math.cos(a)))
            filas.append({"masa_kg": m, "mu": mu, "empuje_N": max(0.0, N * (math.cos(a) - mu * math.sin(a)))})
    def masa_necesaria(mu, T_obj):
        return T_obj * 2 * (math.sin(a) + mu * math.cos(a)) / (math.cos(a) - mu * math.sin(a)) / G
    fab, mn, mx = ch
    recorrido = asiento_mm * coef * (mx - mn) / (2 * math.tan(a))     # la cuña amplifica el cambio de ancho
    return {"angulo_grados": angulo, "T_b_N": T["b"], "T_a_N": T["a"], "filas": filas,
            "masa_necesaria_kg": {mu: masa_necesaria(mu, T["b"]) for mu in rozamientos},
            "empuje_max_29kg_N": max(f["empuje_N"] for f in filas if f["masa_kg"] == max(masas_kg)),
            "recorrido_vertical_mm": recorrido, "cambio_ancho_asiento_mm": asiento_mm * coef * (mx - mn),
            "cumple_a": max(f["empuje_N"] for f in filas if f["masa_kg"] == max(masas_kg)) >= T["b"],
            "cumple_b": recorrido <= 2.0}


def tension_max_piedra(mesa, e1, e4, modelo):
    """Mayor tensión de flexión en piezas de piedra (K2). Las piedras asentadas o a compresión dan ~0."""
    valores = [0.0]
    if e1:
        valores.append(e1["sigma_total"])
    if e4:
        r = e4["modelos"][modelo]
        if mesa.nodo["material_llave"].es_piedra:
            valores.append(r["sigma_llave"])
        if "sigma_pared_caja" in r:
            valores.append(r["sigma_pared_caja"])
    return max(valores)


def criterios(mesa, e1, e2, e3, e4, e9=None, e2b=None):
    v_madera, v_piedra = mesa.volumen(False), mesa.volumen(True)
    frac = v_madera / (v_madera + v_piedra)
    pesada = mesa.pieza_mas_pesada()
    piedras = [p for p in mesa.piezas if p.material.es_piedra]
    piedra_pesada = max(piedras, key=lambda p: p.masa_kg) if piedras else None
    hay_piedra = v_piedra > 0
    k2 = {m: tension_max_piedra(mesa, e1, e4, m) for m in ("a", "b")}
    return {
        "K1": {"valor": frac, "cumple": frac >= MADERA_MIN, "texto": f"madera {frac:.1%} del volumen"},
        "K2": {"valor": k2, "cumple": (k2["b"] <= LIM_PIEDRA) if hay_piedra else None,
               "robusto": (k2["a"] <= LIM_PIEDRA) if hay_piedra else None,
               "texto": (f"flexión máx. en piedra {k2['b']:.1f} MPa (modelo b) / {k2['a']:.1f} MPa (modelo a)"
                         if hay_piedra else "sin piedra")},
        "K3": {"cumple": (all(j["cumple"] for j in e2["juntas"]) and not e2["encolado_a_contraveta"]
                          and (e2b is None or e2b["cumple"])),
               "texto": ((f"junta máx. {max(j['junta_maxima_por_lado'] for j in e2['juntas']):.1f} mm/lado"
                          if e2["juntas"] else "sin juntas piedra-madera")
                         + (f" · entre tablas {e2b['junta_humeda_mm']:.1f}-{e2b['junta_seca_mm']:.1f} mm" if e2b else ""))},
        "K4": {"cumple": e3["sin_piedra_ya_resiste_2x"] and (e9 is None or e9["cumple"]),
               "texto": f"vuelco en extremo sin piedra {e3['sin_piedra']['vuelco_extremo_N']:.0f} N "
                        f"({e3['sin_piedra']['vuelco_extremo_N'] / P_REF:.2f} × P)"
                        + (f" · tabla suelta {e9['vuelco_tabla_suelta_N']:.0f} N" if e9 and not e9["trabadas"] else "")},
        "K5": {"valor": pesada.masa_kg, "cumple": pesada.masa_kg <= PESO_MAX,
               "piedra_cumple": piedra_pesada.masa_kg <= PESO_MAX if piedra_pesada else None,
               "texto": f"más pesada: {pesada.nombre} {pesada.masa_kg:.1f} kg"
                        + (f" · piedra: {piedra_pesada.nombre} {piedra_pesada.masa_kg:.1f} kg" if piedra_pesada else "")},
    }


def ensayar(mesa):
    e1 = e1_viga_piedra(mesa)
    e2 = e2_movimiento(mesa)
    e3 = e3_vuelco(mesa)
    e4 = e4_union(mesa)
    e8, e9, e2b = e8_flecha_tablas(mesa), e9_vuelco_tabla(mesa), e2b_juntas_tablas(mesa)
    return {"codigo": mesa.codigo, "nombre": mesa.nombre, "accion": mesa.accion, "relacion": mesa.relacion,
            "ronda": mesa.ronda, "masa_total_kg": mesa.masa(), "masa_piedra_kg": mesa.masa() - mesa.masa(True),
            "E1": e1, "E2": e2, "E3": e3, "E4": e4, "E8": e8, "E9": e9, "E2b": e2b,
            "K": criterios(mesa, e1, e2, e3, e4, e9, e2b)}
