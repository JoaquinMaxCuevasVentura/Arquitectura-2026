"""Corre los ensayos y dibuja las láminas.

    cd proyectos/porada-2026-mesa/instrumentos
    python3 -m mesa            # ronda 1 y ronda 2
    python3 -m mesa --ronda 1

Escribe en ../04_ensayar/resultados/ (JSON y Markdown), en ../03_proponer/laminas/ (SVG)
y, para las candidatas vigentes, en ../05_consolidar/modelos/ (OBJ + MTL).
"""
import argparse
import json
from pathlib import Path

from . import versiones
from .calculos import CH, H_REF, LIM_PIEDRA, P_REF, e11_cuna_gravedad, ensayar
from .dibujo import lamina, lamina_comparativa
from .modelo3d import exportar_obj

RAIZ = Path(__file__).resolve().parents[2]
RESULTADOS = RAIZ / "04_ensayar" / "resultados"
LAMINAS = RAIZ / "03_proponer" / "laminas"
MODELOS = RAIZ / "05_consolidar" / "modelos"

# Ronda 2: corrección común que pide E3 (ver 04_ensayar/ensayos.md). Se alarga el pie, no se mueve el caballete,
# para no quitar sitio a las rodillas en las cabeceras.
GEOMETRIA_RONDA_2 = {"a_extremo": 450, "pie_x": 180}


# Lectura de cada ronda: lo que el contraste mostró (escrita después de correr, ver 04_ensayar/ensayos.md).
LECTURA = {
    1: ["E1 · V0: la barra de mármol no puede ser viga (9,9 MPa frente a 2,3; ni el mármol más resistente la salva). La madera tiene que cargarla.",
        "E2 · V2: la caja de piedra necesita 1,8 mm de holgura por lado y en seco la junta llega a 3,2 mm; hay que acuñar el montante, y «hincar» pasa a ser «encajar y acuñar».",
        "E3 · Con caballete a 450 mm y pie de 80 mm, ninguna versión resiste 2 P en el extremo sin lastre. La piedra de V0 suma +40 % y aun así no llega.",
        "      Lo resuelve la geometría: alargar el pie 50 mm hacia el extremo (pie simétrico de 180 mm) o llevar el caballete a ≤ 400 mm del extremo.",
        "E4 · V1: la llave de mármol trabaja a flexión y necesita 53-75 mm de profundidad; en la espiga caben 37. La piedra no puede ser la llave.",
        "      V3 (control): la llave de fresno cumple con 14-19 mm. El peso de la llave es ≤ 1 % del rozamiento que la sostiene: «el peso traba» se descarta.",
        "E5 · Bertonio 1612: chakhua (montón) ≠ chhakhua (piedra hincada donde se atan los palos). La pregunta cambia: unión, no lastre.",
        "→ Ronda 2: V0b (la madera carga la piedra), V4 (la piedra solo a compresión) y V3 como control, con pie de 180 mm."],
    2: ["V4 · La espiga atraviesa el collar de piedra y la llave de fresno lo aprieta contra el montante: la piedra solo trabaja a compresión (0,08-0,17 MPa).",
        "      Lo que hace: reparte el apoyo de la llave sobre el montante (0,64 → 0,08 MPa). Es real, pero la madera no lo necesita (resiste 2,3).",
        "V0b · La piedra asentada en un canal, sin cola: junta de 0,9 a 2 mm por lado. Aporta +16 % al vuelco: por el prerregistro, se retira «la piedra estabiliza».",
        "V3 · Cumple lo mismo que V4 sin piedra. En ninguna versión la piedra se justifica por la estructura:",
        "      tiene que justificarse por lo que responda E6 (nodo a 1:1, percepción y montaje), o salir.",
        "K5 · Falla en todas por el tablero (59 kg en una pieza): es un problema común, no de la piedra.",
        "→ Siguiente: E6 con V4 y V3 lado a lado; E7 (ganadores 2017-2018); decidir el mármol y el nombre (O6)."],
    3: ["E8 · B1: una tabla sola (196 × 40 mm, luz 1500) se flecha 5,8 mm bajo P. Es un escalón perceptible (límite: 2 mm).",
        "E9 · Una tabla suelta vuelca con 219 N si alguien se sienta en su punta: no puede ir solo posada, hay que trabarla.",
        "      La cuña vuelve, esta vez por el vuelco de la tabla y no por el concepto.",
        "E2b · Con tablas de 196 mm, ninguna junta queda entre 0,5 y 5 mm de 4 a 13 % de humedad: la tabla debe medir ≤ 182 mm.",
        "K5 · B1 sí cumple: la pieza más pesada es una tabla de 11,6 kg. En A, el tablero de 59 kg falla siempre.",
        "→ Ronda 4: B2 = 6 tablas de 164 mm con junta de 3 mm, clavija acuñada bajo el cabezal, lengüetas sueltas y apoyo central sobre el travesaño."],
    4: ["B2 · Cumple todos los criterios aplicables sin piedra: flecha de 1,0 mm, juntas de 0,8 a 4,8 mm, ninguna pieza de más de 9,7 kg.",
        "V4 · Cumple K1-K4 con la piedra a compresión, pero falla K5 por el tablero de una sola pieza.",
        "AB · El tablero de B2 con el collar de V4 cumple K1-K5. Las dos reglas no chocan: la madera se mueve y se arma; la piedra es lo único fijo.",
        "El cálculo no decide: si el collar se lee como parte de la unión (E6), si las juntas abiertas molestan en el uso (E10)",
        "      y si 4,6 kg de mármol justifican sumar un proveedor a la producción.",
        "→ Siguiente: E6 y E10 con maquetas 1:1; elegir con el autor entre B2 (sin piedra) y AB (con piedra) según lo que muestren."],
    5: ["E7 · Porada ya celebra «l'incontro tra legno e marmo» (Oswood, Osmose): lo original no es juntar madera y piedra, sino el modo del encuentro.",
        "AB · La piedra en la unión: collar a compresión, en un mármol de las mesas del catálogo (Nero Sahara Noir o Marrone Emperador Dark).",
        "B3 · La piedra en una tabla de servicio intercambiable: mármol asentado sin cola, junta de 1,2 mm por lado. 7 tablas de 140 mm para tener tabla central.",
        "      Responde a lo que el jurado premió en Whirl y Odette: componentes con individualidad, intercambiables, personalizables.",
        "→ Dos síntesis compatibles pero excluyentes en el argumento. Las juzgan E6 y E10 y el autor; los renders de Blender sirven como lectura visual previa."],
    6: ["E12 · En AB (y en B2) la clavija y la cuña de las dos tablas centrales caen dentro del montante: 8 cruces fuera de ensamble.",
        "      El modelo de prismas no comparaba piezas entre sí; apareció al pasar AB a planos de construcción.",
        "F1 · La clavija termina dentro del cabezal y la cuña lo atraviesa a lo largo: 0 cruces fuera de ensamble.",
        "      E8, E9 y E2b no cambian (1,0 mm; trabadas; 0,8-4,8 mm). El caballete encolado pesa 15,9 kg: K5 sigue cumpliendo.",
        "      Las cuñas asoman por los costados del cabezal: la cuña, verbo común de la mesa, queda a la vista en cada tabla.",
        "→ F1 es la propuesta final, iteración 1. La cambian E6 (si el collar se lee como adorno: B2 con la misma corrección) y E10."],
}


def _f(v, nd=1):
    return "—" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def notas(r):
    n = []
    if r["E8"]:
        e = r["E8"]
        n.append(f"E8 · flecha bajo P: {e['flecha_total_mm']:.1f} mm (tabla sola {e['flecha_tabla_sola_mm']:.1f}; "
                 f"límite 2)")
    if r["E9"]:
        e = r["E9"]
        n.append(f"E9 · una tabla suelta vuelca con {e['vuelco_tabla_suelta_N']:.0f} N"
                 + (" → trabada con clavija y cuña" if e["trabadas"] else " → hay que trabarla"))
    if r["E2b"]:
        e = r["E2b"]
        n.append(f"E2b · junta entre tablas {e['junta_humeda_mm']:.1f}-{e['junta_seca_mm']:.1f} mm "
                 f"(tabla {e['ancho_tabla_mm']:.0f}; máx. {e['ancho_tabla_max_mm']:.0f})")
    if r["E1"]:
        e = r["E1"]
        n.append(f"E1 · barra a flexión: {e['sigma_total']:.1f} MPa (límite {e['limite_diseno']:.1f}); "
                 f"P admisible {e['P_admisible_N']:.0f} N")
    if r["E4"]:
        b = r["E4"]["modelos"]["b"]
        if r["E4"]["material_llave"].startswith("mármol"):
            n.append(f"E4 · llave de piedra: {b['sigma_llave']:.1f} MPa; necesita d ≥ {b['d_min_mm']:.0f} mm "
                     f"(cabe ≤ {b['d_max_que_cabe_mm']:.0f}) → {'cabe' if b['cabe'] else 'NO CABE'}")
        if "compresion_collar_MPa" in b:
            n.append(f"E4 · collar a compresión: {b['compresion_collar_MPa']:.2f} MPa; apoyo en el montante "
                     f"{b['apoyo_montante_sin_collar_MPa']:.2f} → {b['apoyo_montante_con_collar_MPa']:.2f} MPa")
        if "sigma_pared_caja" in b:
            a = r["E4"]["modelos"]["a"]
            n.append(f"E4 · paredes de la caja: {b['sigma_pared_caja']:.1f} MPa (b) / {a['sigma_pared_caja']:.1f} MPa (a)")
    e12 = r["E12"]
    if e12["errores"] or e12["grupos_kg"]:
        n.append(f"E12 · {len(e12['errores'])} cruces fuera de ensamble"
                 + "".join(f" · {g.split(' (')[0]} {m:.1f} kg" for g, m in e12["grupos_kg"].items() if "izq" in g))
    e3 = r["E3"]
    n.append(f"E3 · vuelco en extremo sin/con piedra: {e3['sin_piedra']['vuelco_extremo_N']:.0f} / "
             f"{e3['con_piedra']['vuelco_extremo_N']:.0f} N (aporte {e3['aporte_piedra']['vuelco_extremo_N']:+.0%})")
    for j in r["E2"]["juntas"][:1]:
        n.append(f"E2 · {j['junta']}: {j['junta_maxima_por_lado']:.1f} mm/lado")
    return n


def tabla_md(resultados, titulo, geometria):
    lin = [f"# {titulo}", "",
           f"Generado por `python3 -m mesa` (instrumentos/). Supuestos: P = {P_REF:.0f} N, H = {H_REF:.0f} N, "
           f"CH {CH[1]:.0f}-{CH[2]:.0f} % (fabricación {CH[0]:.0f} %), límite de flexión de la piedra {LIM_PIEDRA:.2f} MPa. "
           f"Geometría común: {geometria}.", "",
           "| Versión | Masa (kg) | Piedra (kg) | K1 madera | K2 piedra a compresión | K3 movimientos | K4 estable sin lastre | K5 ≤ 25 kg |",
           "|---|---|---|---|---|---|---|---|"]
    m = lambda d: "—" if d["cumple"] is None else ("✓" if d["cumple"] else "✗")
    for r in resultados:
        k = r["K"]
        lin.append(f"| **{r['codigo']}** {r['nombre']} | {r['masa_total_kg']:.1f} | {r['masa_piedra_kg']:.1f} | "
                   f"{m(k['K1'])} {k['K1']['valor']:.1%} | {m(k['K2'])} {k['K2']['texto']} | {m(k['K3'])} | "
                   f"{m(k['K4'])} {k['K4']['texto']} | {m(k['K5'])} {k['K5']['texto']} |")
    if any(r["E8"] for r in resultados):
        lin += ["", "## E8 · E9 · E2b · Tablas (propuesta B)", ""]
        for r in resultados:
            if not r["E8"]:
                continue
            e8, e9, e2b = r["E8"], r["E9"], r["E2b"]
            lin.append(f"- **{r['codigo']}** · E8: flecha bajo P {e8['flecha_total_mm']:.2f} mm (tabla sola "
                       f"{e8['flecha_tabla_sola_mm']:.2f}; asiento del apoyo central {e8['asiento_apoyo_central_mm']:.2f}; "
                       f"reparto por lengüetas ÷{e8['reparto_lenguetas']}) → {'✓' if e8['cumple'] else '✗'}; "
                       f"flexión en la tabla {e8['sigma_tabla']:.1f} MPa (límite {e8['limite_tabla']:.1f})"
                       + (f"; en el travesaño {e8['sigma_travesano']:.1f} MPa" if e8["sigma_travesano"] else "") + ". "
                       f"E9: una tabla suelta vuelca con {e9['vuelco_tabla_suelta_N']:.0f} N "
                       f"({'trabada' if e9['trabadas'] else 'sin trabar'}) → {'✓' if e9['cumple'] else '✗'}. "
                       f"E2b: tabla de {e2b['ancho_tabla_mm']:.0f} mm, junta {e2b['junta_nominal_mm']:.1f} mm al 8 % → "
                       f"{e2b['junta_humeda_mm']:.2f} mm al 13 % y {e2b['junta_seca_mm']:.2f} mm al 4 % "
                       f"(varía {e2b['estacional_6_11_mm']:.1f} mm entre 6 y 11 %); ancho máximo de tabla "
                       f"{e2b['ancho_tabla_max_mm']:.0f} mm → {'✓' if e2b['cumple'] else '✗'}.")
    lin += ["", "## E12 · Interferencias (cruces de piezas fuera de los ensambles previstos)", ""]
    for r in resultados:
        e = r["E12"]
        txt = f"- **{r['codigo']}**: {e['previstos']} cruces previstos (ensambles), **{len(e['errores'])} fuera de ensamble**"
        if e["errores"]:
            txt += ": " + "; ".join(f"{x['a']} × {x['b']} ({' × '.join(f'{c:g}' for c in x['cruce_mm'])} mm)"
                                    for x in e["errores"])
        if e["grupos_kg"]:
            txt += ". Piezas encoladas: " + "; ".join(f"{g} {m:.1f} kg" for g, m in e["grupos_kg"].items())
        lin.append(txt + ".")
    lin += ["", "## E1 · Piedra como viga", ""]
    if not any(r["E1"] for r in resultados):
        lin.append("No aplica en esta ronda: ninguna versión usa la piedra como viga.")
    for r in resultados:
        if r["E1"]:
            e = r["E1"]
            lin.append(f"- **{r['codigo']}**: luz {e['luz_mm']:.0f} mm, sección {e['seccion_mm']} mm → σ peso propio "
                       f"{e['sigma_peso']:.2f} MPa + σ por P {e['sigma_P']:.2f} MPa = **{e['sigma_total']:.2f} MPa** "
                       f"(límite {e['limite_diseno']:.2f}). ¿Lo salva el mármol más resistente (15/3 = 5 MPa)? "
                       f"**{'sí' if e['algun_marmol_la_salva'] else 'no'}**. Carga puntual admisible: {e['P_admisible_N']:.0f} N.")
    lin += ["", "## E2 · Movimiento de la madera frente a la piedra", ""]
    for r in resultados:
        for j in r["E2"]["juntas"]:
            lin.append(f"- **{r['codigo']}** · {j['junta']}: holgura de fabricación {j['holgura_fabricacion_por_lado']:.2f} mm/lado; "
                       f"junta máxima {j['junta_maxima_por_lado']:.2f} mm/lado → {'✓' if j['cumple'] else '✗'}. {j['nota'][0].upper() + j['nota'][1:]}.")
    t = resultados[0]["E2"]["ancho_tablero_mm"]
    lin.append(f"- Todas: el ancho del tablero (1000 mm) varía {t['extremos_4_13']:.1f} mm entre 4 y 13 % "
               f"y {t['estacional_6_11']:.1f} mm entre 6 y 11 %.")
    lin += ["", "## E3 · Vuelco con y sin piedra (N)", "",
            "| Versión | Extremo sin / con | Borde sin / con | Horizontal sin / con | ¿Desliza antes? | Aporte piedra | Caballete a ≤ (mm) | o alargar pie (mm) | ¿Retirar «estabiliza»? |",
            "|---|---|---|---|---|---|---|---|---|"]
    for r in resultados:
        e = r["E3"]
        s, c = e["sin_piedra"], e["con_piedra"]
        lin.append(f"| {r['codigo']} | {s['vuelco_extremo_N']:.0f} / {c['vuelco_extremo_N']:.0f} | {s['vuelco_borde_N']:.0f} / "
                   f"{c['vuelco_borde_N']:.0f} | {s['vuelco_horizontal_N']:.0f} / {c['vuelco_horizontal_N']:.0f} | "
                   f"{'sí' if s['desliza_antes_de_volcar'] else 'no'} | {e['aporte_piedra']['vuelco_extremo_N']:+.0%} | "
                   f"{e['a_max_para_2P_mm']:.0f} | {e['alargar_pie_para_2P_mm']:.0f} | {'sí' if e['retirar_frase_estabiliza'] else 'no'} |")
    lin += ["", "## E4 · La unión (modelo b; entre paréntesis, modelo a, más conservador)", ""]
    for r in resultados:
        if not r["E4"]:
            continue
        a, b = r["E4"]["modelos"]["a"], r["E4"]["modelos"]["b"]
        txt = (f"- **{r['codigo']}** · llave de {r['E4']['material_llave']}: T = {b['T_N']:.0f} N ({a['T_N']:.0f}); "
               f"flexión en la llave {b['sigma_llave']:.1f} MPa ({a['sigma_llave']:.1f}) frente a un límite de {r['E4']['limite_llave']:.1f}; "
               f"profundidad mínima {b['d_min_mm']:.0f} mm ({a['d_min_mm']:.0f}), cabe hasta {b['d_max_que_cabe_mm']:.0f} → "
               f"{'cabe' if b['cabe'] else 'no cabe'} ({'cabe' if a['cabe'] else 'no cabe'}); "
               f"apoyo en el montante {b['apoyo_llave_MPa']:.2f} MPa; peso de la llave / rozamiento = {b['peso_llave_sobre_rozamiento']:.3f}.")
        if "compresion_collar_MPa" in b:
            txt += (f" Collar: compresión {b['compresion_collar_MPa']:.2f} MPa ({a['compresion_collar_MPa']:.2f}); "
                    f"el apoyo en el montante baja de {b['apoyo_montante_sin_collar_MPa']:.2f} a {b['apoyo_montante_con_collar_MPa']:.2f} MPa.")
        if "sigma_pared_caja" in b:
            txt += f" Paredes de la caja: {b['sigma_pared_caja']:.2f} MPa ({a['sigma_pared_caja']:.2f}) frente a {LIM_PIEDRA:.2f}."
        lin.append(txt)
    return "\n".join(lin) + "\n"


RONDAS = {
    1: ("Ronda 1 · propuesta A, versiones iniciales", {}, lambda: versiones.RONDA_1),
    2: ("Ronda 2 · propuesta A, derivadas, con la corrección común de E3", GEOMETRIA_RONDA_2,
        lambda: (versiones.v3,) + versiones.RONDA_2),
    3: ("Ronda 3 · propuesta B, versión inicial (con el control V3)", GEOMETRIA_RONDA_2,
        lambda: (versiones.v3, versiones.b1)),
    4: ("Ronda 4 · A frente a B, y síntesis candidata", GEOMETRIA_RONDA_2,
        lambda: (versiones.v4, versiones.b2, versiones.ab, versiones.v3)),
    5: ("Ronda 5 · mejoras desde los precedentes (E7): las dos síntesis posibles", GEOMETRIA_RONDA_2,
        lambda: (versiones.b2, versiones.ab, versiones.b3)),
    6: ("Ronda 6 · propuesta final, iteración 1: AB corregida por E12", GEOMETRIA_RONDA_2,
        lambda: (versiones.ab, versiones.f1)),
}


def correr(ronda):
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    LAMINAS.mkdir(parents=True, exist_ok=True)
    titulo, geo, fabricas = RONDAS[ronda]
    geometria = versiones.configurar(**geo)
    fabricas = fabricas()
    mesas = [f() for f in fabricas]
    for m in mesas:
        m.ronda = ronda
    res = [ensayar(m) for m in mesas]
    sufijo = f"r{ronda}"
    for m, r in zip(mesas, res):
        (LAMINAS / f"{m.codigo}_{sufijo}.svg").write_text(lamina(m, r, notas(r)), encoding="utf-8")
        if ronda >= 4 and m.codigo in ("V4", "B2", "AB", "B3", "F1"):   # candidatas vigentes → modelo 3D base
            exportar_obj(m, MODELOS)
    (LAMINAS / f"comparativa_{sufijo}.svg").write_text(lamina_comparativa(mesas, res, titulo, LECTURA.get(ronda, ())),
                                                        encoding="utf-8")
    texto_geo = f"caballete a {geometria['a_extremo_mm']:.0f} mm del extremo, pie de {geometria['pie_mm'][0]:.0f} mm"
    (RESULTADOS / f"ronda{ronda}.md").write_text(tabla_md(res, titulo, texto_geo), encoding="utf-8")
    serial = json.loads(json.dumps(res, default=lambda o: getattr(o, "nombre", str(o))))
    (RESULTADOS / f"ronda{ronda}.json").write_text(json.dumps({"geometria": geometria, "resultados": serial},
                                                              ensure_ascii=False, indent=1), encoding="utf-8")
    return res


def informe_e11():
    r = e11_cuna_gravedad()
    lin = ["# E11 · Piedra en cuña que tensa el caballete por su peso", "",
           f"Generado por `python3 -m mesa`. Cuña de {r['angulo_grados']:.0f}° respecto de la vertical; demanda de E4: "
           f"T = {r['T_b_N']:.0f} N (modelo b) / {r['T_a_N']:.0f} N (modelo a). Prerregistro en `../ensayos.md`.", "",
           "| Piedra (kg) | μ = 0 | μ = 0,2 | μ = 0,4 | μ = 0,5 |", "|---|---|---|---|---|"]
    for m in sorted({f["masa_kg"] for f in r["filas"]}):
        celdas = [f"{f['empuje_N']:.0f} N" for f in r["filas"] if f["masa_kg"] == m]
        lin.append(f"| {m:.1f} | " + " | ".join(celdas) + " |")
    lin += ["", "**Masa de piedra necesaria** para llegar a T (modelo b): "
            + ", ".join(f"μ = {mu:.1f}: {kg:.0f} kg" for mu, kg in r["masa_necesaria_kg"].items()) + ".", "",
            f"**(a)** Empuje máximo con 29,4 kg: {r['empuje_max_29kg_N']:.0f} N frente a {r['T_b_N']:.0f} N → "
            f"{'cumple' if r['cumple_a'] else 'NO cumple'}.",
            f"**(b)** Con un asiento de madera de 150 mm, su ancho cambia {r['cambio_ancho_asiento_mm']:.1f} mm entre 4 y 13 %; "
            f"la cuña lo convierte en {r['recorrido_vertical_mm']:.1f} mm de recorrido vertical de la piedra → "
            f"{'cumple' if r['cumple_b'] else 'NO cumple'} (límite 2 mm)."]
    (RESULTADOS / "e11.md").write_text("\n".join(lin) + "\n", encoding="utf-8")
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ronda", type=int, choices=tuple(RONDAS))
    args = ap.parse_args()
    r11 = informe_e11()
    print(f"E11: empuje máx. {r11['empuje_max_29kg_N']:.0f} N frente a T {r11['T_b_N']:.0f} N; "
          f"recorrido {r11['recorrido_vertical_mm']:.1f} mm")
    for ronda in ([args.ronda] if args.ronda else list(RONDAS)):
        res = correr(ronda)
        print(f"ronda {ronda}: " + ", ".join(
            f"{r['codigo']} {sum(1 for k in r['K'].values() if k['cumple'])}/{sum(1 for k in r['K'].values() if k['cumple'] is not None)}"
            for r in res) + "  (criterios cumplidos / aplicables)")


if __name__ == "__main__":
    main()
