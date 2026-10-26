"""Corre los ensayos y dibuja las láminas.

    cd proyectos/porada-2026-mesa/instrumentos
    python3 -m mesa            # ronda 1 y ronda 2
    python3 -m mesa --ronda 1

Escribe en ../04_ensayar/resultados/ (JSON y Markdown) y en ../03_proponer/laminas/ (SVG).
"""
import argparse
import json
from pathlib import Path

from . import versiones
from .calculos import CH, H_REF, LIM_PIEDRA, P_REF, ensayar
from .dibujo import lamina, lamina_comparativa

RAIZ = Path(__file__).resolve().parents[2]
RESULTADOS = RAIZ / "04_ensayar" / "resultados"
LAMINAS = RAIZ / "03_proponer" / "laminas"

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
}


def _f(v, nd=1):
    return "—" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def notas(r):
    n = []
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


def correr(ronda):
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    LAMINAS.mkdir(parents=True, exist_ok=True)
    if ronda == 1:
        geometria = versiones.configurar()
        fabricas = versiones.RONDA_1
        titulo = "Ronda 1 · versiones iniciales"
    else:
        geometria = versiones.configurar(**GEOMETRIA_RONDA_2)
        fabricas = (versiones.v3,) + versiones.RONDA_2
        titulo = "Ronda 2 · control y versiones derivadas, con la corrección común de E3"
    mesas = [f() for f in fabricas]
    for m in mesas:
        m.ronda = ronda
    res = [ensayar(m) for m in mesas]
    sufijo = f"r{ronda}"
    for m, r in zip(mesas, res):
        (LAMINAS / f"{m.codigo}_{sufijo}.svg").write_text(lamina(m, r, notas(r)), encoding="utf-8")
    (LAMINAS / f"comparativa_{sufijo}.svg").write_text(lamina_comparativa(mesas, res, titulo, LECTURA[ronda]),
                                                        encoding="utf-8")
    texto_geo = f"caballete a {geometria['a_extremo_mm']:.0f} mm del extremo, pie de {geometria['pie_mm'][0]:.0f} mm"
    (RESULTADOS / f"ronda{ronda}.md").write_text(tabla_md(res, titulo, texto_geo), encoding="utf-8")
    serial = json.loads(json.dumps(res, default=lambda o: getattr(o, "nombre", str(o))))
    (RESULTADOS / f"ronda{ronda}.json").write_text(json.dumps({"geometria": geometria, "resultados": serial},
                                                              ensure_ascii=False, indent=1), encoding="utf-8")
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ronda", type=int, choices=(1, 2))
    args = ap.parse_args()
    for ronda in ([args.ronda] if args.ronda else [1, 2]):
        res = correr(ronda)
        print(f"ronda {ronda}: " + ", ".join(f"{r['codigo']} {sum(1 for k in r['K'].values() if k['cumple'])}/5" for r in res))


if __name__ == "__main__":
    main()
