"""Números y hojas de la prueba de muestreo (prueba_muestreo.py). Corre con Python común (numpy, OpenEXR, pypng, Pillow).

Mide, contra la referencia R (los ajustes de los renders finales):
  - tiempo total, preparación (sincronizar y BVH) y memoria;
  - muestras por píxel (pase Debug Sample Count): promedio, mínimo y % de píxeles que llegan al tope;
  - error estimado contra la imagen convergida, en niveles de 8 bits sobre la imagen ya con la transformación de vista:
    R y R2 solo difieren en la semilla, así que su diferencia mide el ruido que le queda a R. Las demás variantes usan
    la semilla de R y comparten sus primeras muestras: su ruido se parece al de R y la diferencia con R lo esconde.
    Por eso el error se mide contra R2, que es independiente: error(X)² ≈ rms(X - R2)² - rms(R - R2)² / 2;
  - sesgo de luminancia (lineal) por zonas, para los ajustes que quitan luz (rebotes, cáusticas, clamp);
  - vidrio: cuánto sol pasa (mancha del piso) y cuánto se ve a través (exterior visto por las dos mitades).

Uso: python hoja_muestreo.py carpeta_de_la_prueba carpeta_de_salida
"""
import json
import math
import os
import re
import sys

import numpy as np
import OpenEXR
import png
from PIL import Image, ImageDraw, ImageFont

carpeta, salida = sys.argv[1], sys.argv[2]
os.makedirs(salida, exist_ok=True)
reg = json.load(open(f"{carpeta}/registro.json"))
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fh, ft, fs, fm = (ImageFont.truetype(FB, 34), ImageFont.truetype(FB, 22), ImageFont.truetype(F, 18),
                  ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 17))
FONDO, TINTA, GRIS = (242, 241, 238), (25, 25, 25), (85, 85, 85)

# zonas de CAM_07 a 1280 × 720 (x0, y0, x1, y1)
ZONAS = {"celosía": (910, 365, 1150, 500), "portal y vidrio": (540, 350, 780, 485),
         "letrero": (420, 270, 660, 405), "cielo": (100, 40, 500, 200), "asfalto": (100, 560, 600, 715)}
DIA = ["R", "R2", "U3", "U3B", "U3SD", "RB", "SC", "PG", "R1K"]
NOMBRES = {"R": "R · referencia (finales)", "R2": "R2 · otra semilla", "U3": "U3 · umbral 0,03, tope 2048, mín. 16",
           "U3B": "U3B · umbral 0,03, tope 384", "U3SD": "U3SD · U3 sin denoise (receta de animación)", "RB": "RB · rebotes 4/2/2/4", "SC": "SC · sin cáusticas reflectivas",
           "PG": "PG · path guiding", "R1K": "R1K · tope 1024", "N0": "N0 · noche, sin clamp", "N10": "N10 · noche, clamp 10",
           "N4": "N4 · noche, clamp 4", "POLI0": "POLI0 · letras tal cual", "POLI1": "POLI1 · letras subdivididas",
           "VC1": "VC1 · vidrio, cáusticas refractivas sí", "VC0": "VC0 · vidrio, cáusticas refractivas no",
           "VC1N": "VC1N · cáusticas sí, sin clamp", "VST0": "VST0 · sombra transparente, cáusticas no",
           "VST1": "VST1 · sombra transparente, cáusticas sí", "VT": "VT · transmitancia (panel uniforme, cielo negro)"}


def hay(v):
    return v in reg and os.path.exists(f"{carpeta}/{v}.exr") and os.path.exists(f"{carpeta}/{v}.png")


def capas(v):
    """Capas del EXR multicapa, sin el nombre de la capa de vista: Combined, Noisy Image, Debug Sample Count.X..."""
    out = {}
    with OpenEXR.File(f"{carpeta}/{v}.exr") as f:
        for part in f.parts:
            for k, ch in part.channels.items():
                out[k.split(".", 1)[1] if "." in k else k] = np.asarray(ch.pixels, dtype=np.float32)
    return out


def imagen(v):
    """PNG de 16 bits (con la transformación de vista), en niveles de 8 bits y coma flotante."""
    w, h, filas, info = png.Reader(filename=f"{carpeta}/{v}.png").asDirect()
    a = np.vstack([np.asarray(f, dtype=np.float32) for f in filas]).reshape(h, w, info["planes"])[:, :, :3]
    return a * 255.0 / (2 ** info["bitdepth"] - 1)


def lum(rgb):
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def rms(a, b, zona=None):
    if zona:
        x0, y0, x1, y1 = zona
        a, b = a[y0:y1, x0:x1], b[y0:y1, x0:x1]
    return float(np.sqrt(np.mean((a - b) ** 2)))


def c(s):
    """Coma decimal en los textos de las hojas."""
    return re.sub(r"(\d)\.(\d)", r"\1,\2", s)


def a8(a):
    return Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8))


def mapa_dif(a, b, ganancia=8.0):
    """Diferencia firmada en luminancia: rojo = más claro que la referencia, azul = más oscuro."""
    d = (lum(a) - lum(b)) * ganancia
    out = np.full(a.shape, 128.0)
    out[..., 0] += np.clip(d, 0, 127)
    out[..., 1] -= np.clip(np.abs(d), 0, 127) * 0.6
    out[..., 2] += np.clip(-d, 0, 127)
    out[..., 0] -= np.clip(-d, 0, 127)
    return a8(out)


def mapa_muestras(frac):
    """Muestras de cada píxel sobre el tope: negro (pocas) -> amarillo -> rojo (llega al tope)."""
    t = np.clip(frac, 0, 1)
    rgb = np.stack([np.clip(t * 2, 0, 1), np.clip(2 - t * 2, 0, 1) * np.clip(t * 2, 0, 1), np.zeros_like(t)], -1)
    rgb[t > 0.999] = (1.0, 0.0, 0.0)
    return a8(rgb * 255)


res = {}
# ------------------------------------------------------------------ día: muestreo, rebotes, cáusticas, guiding
if hay("R"):
    R, cR = imagen("R"), capas("R")
    piso = rms(R, imagen("R2")) / math.sqrt(2) if hay("R2") else None
    pisoz = {z: rms(R, imagen("R2"), c) / math.sqrt(2) for z, c in ZONAS.items()} if hay("R2") else {}
    for v in DIA:
        if not hay(v):
            continue
        X, cX = imagen(v), capas(v)
        tope = reg[v]["ajustes"]["samples"]
        frac = cX["Debug Sample Count.X"]
        spp = frac * tope
        d = dict(tiempo=reg[v]["tiempo"], preparacion=reg[v]["preparacion"], tope=tope,
                 spp_media=float(spp.mean()), spp_min=float(spp.min()), spp_p50=float(np.median(spp)),
                 al_tope=float((frac > 0.999).mean()), memoria_mb=reg[v]["memoria_pico_proceso_mb"])
        if v == "R":
            d["error"] = piso
            d["error_zonas"] = pisoz
        elif v == "R2":
            d["error"] = piso
        else:
            R2 = imagen("R2")      # semilla independiente (ver el encabezado)
            d["error"] = math.sqrt(max(rms(X, R2) ** 2 - piso ** 2, 0))
            d["error_zonas"] = {z: math.sqrt(max(rms(X, R2, c) ** 2 - pisoz[z] ** 2, 0)) for z, c in ZONAS.items()}
            yX, yR = lum(cX["Combined"][..., :3]), lum(cR["Combined"][..., :3])
            d["sesgo_zonas"] = {z: float(yX[c[1]:c[3], c[0]:c[2]].mean() / yR[c[1]:c[3], c[0]:c[2]].mean() - 1)
                                for z, c in ZONAS.items()}
            d["sesgo_total"] = float(yX.mean() / yR.mean() - 1)
        res[v] = d

# ------------------------------------------------------------------ poligonaje
if hay("POLI0") and hay("POLI1"):
    for v in ("POLI0", "POLI1"):
        g = reg[v]
        res[v] = dict(tiempo=g["tiempo"], preparacion=g["preparacion"], render=g["tiempo"] - g["preparacion"],
                      triangulos=g["triangulos"], memoria_mb=g["memoria_pico_proceso_mb"],
                      memoria_cycles_mb=g.get("memoria_cycles_mb"))
    res["POLI1"]["dif_rms"] = rms(imagen("POLI1"), imagen("POLI0"))
    res["POLI1"]["nivel"] = reg["POLI1"].get("nivel_subdivision")

# ------------------------------------------------------------------ noche: clamp
# referencia: sin clamp (N0) si está; si no, clamp 10. Las zonas, por brillo de la referencia: las más claras son las
# ventanas encendidas y sus reflejos en el piso mojado
BANDAS_NOCHE = {"oscuro (< 0,05)": (0, 0.05), "medio (0,05 a 0,2)": (0.05, 0.2), "claro (> 0,2)": (0.2, 1e9)}
if hay("N10") and hay("N4"):
    ref = "N0" if hay("N0") else "N10"
    yr = lum(capas(ref)["Combined"][..., :3])
    for v in ("N0", "N10", "N4"):
        if not hay(v):
            continue
        y = lum(capas(v)["Combined"][..., :3])
        res[v] = dict(tiempo=reg[v]["tiempo"], referencia=ref, sesgo_total=float(y.mean() / yr.mean() - 1),
                      sesgo_bandas={b: float(y[(yr >= lo) & (yr < hi)].mean() / yr[(yr >= lo) & (yr < hi)].mean() - 1)
                                    for b, (lo, hi) in BANDAS_NOCHE.items()},
                      pixeles_bandas={b: float(((yr >= lo) & (yr < hi)).mean()) for b, (lo, hi) in BANDAS_NOCHE.items()},
                      dif_rms=rms(imagen(v), imagen(ref)))

# ------------------------------------------------------------------ vidrio y sol
for v in ("VC1", "VC0", "VC1N", "VST0", "VST1", "VT"):
    if not hay(v):
        continue
    cv, pts = capas(v), reg[v]["puntos"]
    y = lum(cv["Noisy Image"][..., :3])          # sin denoise: el promedio de la ventana no tiene sesgo

    def med(k, r=7):
        x, yy = (int(round(t)) for t in pts[k])
        return float(y[yy - r:yy + r + 1, x - r:x + r + 1].mean())
    pv, pa, ps, vv, va = (med(k) for k in ("piso_vidrio", "piso_abierto", "piso_sombra", "vista_vidrio", "vista_abierta"))
    if v == "VT":         # sin sol: solo vale la vista a través, que es la transmitancia
        res[v] = dict(tiempo=reg[v]["tiempo"], transmitancia=vv / va, vista_vidrio=vv, vista_abierta=va)
        continue
    res[v] = dict(tiempo=reg[v]["tiempo"], sol_que_pasa=(pv - ps) / (pa - ps), vista_a_traves=vv / va,
                  piso_vidrio=pv, piso_abierto=pa, piso_sombra=ps)
# El piso detrás del vidrio recibe otro cielo que el punto a la sombra del muro. Por eso la base "sin sol" es VC1, donde
# el sol no pasa: lo que suma el sol detrás del vidrio es la diferencia con VC1, sobre lo que suma en la mitad abierta.
if "VC1" in res:
    for v in ("VC1", "VC0", "VC1N", "VST0", "VST1"):
        if v in res:
            d = res[v]
            d["sol_que_pasa"] = (d["piso_vidrio"] - res["VC1"]["piso_vidrio"]) / (d["piso_abierto"] - d["piso_sombra"])

json.dump(res, open(f"{salida}/resultados_muestreo.json", "w"), indent=1, ensure_ascii=False)


# ------------------------------------------------------------------ tabla en texto
def f(x, fmt="{:.0f}"):
    return "—" if x is None else fmt.format(x)


lineas = []
if "R" in res:
    t0 = res["R"]["tiempo"]
    lineas.append(f"{'variante':<40}{'tiempo':>8}{'×R':>7}{'spp medio':>11}{'al tope':>9}{'error':>8}{'sesgo':>8}")
    for v in DIA:
        if v in res:
            d = res[v]
            lineas.append(f"{NOMBRES[v]:<40}{d['tiempo']:>7.0f}s{d['tiempo'] / t0:>7.2f}{d['spp_media']:>11.0f}"
                          f"{100 * d['al_tope']:>8.0f}%{f(d.get('error'), '{:.2f}'):>8}"
                          f"{f(100 * d['sesgo_total'] if 'sesgo_total' in d else None, '{:+.1f}%'):>8}")
for k in ("POLI0", "POLI1"):
    if k in res:
        d = res[k]
        lineas.append(f"{NOMBRES[k]:<40}{d['tiempo']:>7.0f}s  prep {d['preparacion']:.0f}s  render {d['render']:.0f}s  "
                      f"{d['triangulos'] / 1e6:.2f} M tri  {d['memoria_mb']:.0f} MB")
for v in ("N0", "N10", "N4"):
    if v in res:
        d = res[v]
        lineas.append(f"{NOMBRES[v]:<40}{d['tiempo']:>7.0f}s  contra {d['referencia']}: luminancia {100 * d['sesgo_total']:+.1f}%  "
                      + "  ".join(f"{b} {100 * x:+.1f}%" for b, x in d["sesgo_bandas"].items()))
if "VT" in res:
    lineas.append(f"{NOMBRES['VT']:<44} transmitancia del vidrio {100 * res['VT']['transmitancia']:.1f}%")
for v in ("VC1", "VC0", "VC1N", "VST0", "VST1"):
    if v in res:
        d = res[v]
        lineas.append(f"{NOMBRES[v]:<44} sol que pasa {100 * d['sol_que_pasa']:5.1f}%   {d['tiempo']:.0f}s")
open(f"{salida}/resultados_muestreo.txt", "w").write("\n".join(lineas) + "\n")
print("\n".join(lineas))
if "R" in res and "error_zonas" in res["R"]:
    print("\nerror por zona (niveles de 8 bits):")
    print(f"{'':<8}" + "".join(f"{z:>17}" for z in ZONAS))
    for v in DIA:
        if v in res and "error_zonas" in res[v]:
            print(f"{v:<8}" + "".join(f"{res[v]['error_zonas'][z]:>17.2f}" for z in ZONAS))
    print("\nsesgo de luminancia por zona:")
    for v in DIA:
        if v in res and "sesgo_zonas" in res[v]:
            print(f"{v:<8}" + "".join(f"{100 * res[v]['sesgo_zonas'][z]:>+16.1f}%" for z in ZONAS))


# ------------------------------------------------------------------ hoja 1: día
def recorte(img, zona, escala=2):
    x0, y0, x1, y1 = zona
    return a8(img[y0:y1, x0:x1]).resize(((x1 - x0) * escala, (y1 - y0) * escala), Image.NEAREST)


if "R" in res:
    filas = [v for v in DIA if v in res and v != "R2"]
    zA, zB = ZONAS["celosía"], ZONAS["portal y vidrio"]
    wA, hA = (zA[2] - zA[0]) * 2, (zA[3] - zA[1]) * 2
    wm, hm = 480, 270
    m = 20
    W = 370 + 2 * (wA + m) + 2 * (wm + m)
    H = 230 + len(filas) * (hA + m) + 60
    hoja = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(hoja)
    d.text((m, 20), "Muestreo y caminos de luz en CAM_07 (P2, 1280 × 720): qué paga y qué no", font=fh, fill=TINTA)
    d.text((m, 72), "Recortes al 200 %: celosía y portal con vidrio. Mapa de muestras: negro pocas, amarillo la mitad del "
                    "tope, rojo en el tope. Diferencia ×8 (rojo más claro, azul más oscuro): contra R2 en el muestreo, "
                    "contra R en rebotes y cáusticas.", font=fs, fill=GRIS)
    d.text((m, 100), "Error: estimado contra la imagen convergida, en niveles de 8 bits (R2, otra semilla, da el ruido "
                     "que le queda a R).", font=fs, fill=GRIS)
    x_cols = [370, 370 + wA + m, 370 + 2 * (wA + m), 370 + 2 * (wA + m) + wm + m]
    for x, t in zip(x_cols, ["celosía", "portal y vidrio", "muestras por píxel", "diferencia ×8"]):
        d.text((x, 190), t, font=ft, fill=TINTA)
    y = 230
    for v in filas:
        X, cX = imagen(v), capas(v)
        r = res[v]
        clave, _, desc = NOMBRES[v].partition(" · ")
        d.text((m, y), clave, font=ft, fill=TINTA)
        info = [desc, f"{r['tiempo']:.0f} s (×{r['tiempo'] / res['R']['tiempo']:.2f})",
                f"{r['spp_media']:.0f} spp medio, {100 * r['al_tope']:.0f} % al tope",
                f"error {f(r.get('error'), '{:.2f}')}"]
        if v in ("RB", "SC"):          # en el resto la luminancia no cambia (±0,1 %)
            info.append(f"luminancia {100 * r['sesgo_total']:+.1f} %")
        for i, t in enumerate(info):
            d.text((m, y + 34 + 26 * i), c(t), font=fs, fill=GRIS)
        hoja.paste(recorte(X, zA), (x_cols[0], y))
        hoja.paste(recorte(X, zB), (x_cols[1], y))
        hoja.paste(mapa_muestras(cX["Debug Sample Count.X"]).resize((wm, hm), Image.BILINEAR), (x_cols[2], y))
        if v != "R":       # lo sistemático, contra R (misma semilla); el ruido, contra R2 (semilla independiente)
            hoja.paste(mapa_dif(X, R if v in ("RB", "SC") else imagen("R2")).resize((wm, hm), Image.BILINEAR),
                       (x_cols[3], y))
        y += hA + m
    hoja.save(f"{salida}/Prueba_muestreo_CAM07.jpg", quality=90)
    print("hoja", f"{salida}/Prueba_muestreo_CAM07.jpg", hoja.size)

# ------------------------------------------------------------------ hoja 2: vidrio y sol, noche, poligonaje
bloques = []
vid = [v for v in ("VC1", "VC0", "VC1N", "VST0", "VST1", "VT") if v in res]
if vid:
    bloques.append(("Vidrio y sol: ¿pasa el sol por el vidrio del modelo? (mitad izquierda de la ventana abierta, "
                    "mitad derecha con vidrio)", [(v, a8(imagen(v)).resize((480, 270), Image.LANCZOS),
                                                    [f"transmitancia {100 * res[v]['transmitancia']:.1f} %"] if v == "VT" else
                                                    [f"sol que pasa {100 * res[v]['sol_que_pasa']:.1f} %"]) for v in vid]))
if "N4" in res:
    ref = res["N4"]["referencia"]
    fila = []
    for v in ("N0", "N10", "N4"):
        if v in res:
            info = [f"{res[v]['tiempo']:.0f} s"]
            if v != ref:
                info.append(f"luminancia {100 * res[v]['sesgo_total']:+.1f} %, en lo claro "
                            f"{100 * res[v]['sesgo_bandas']['claro (> 0,2)']:+.1f} %")
            fila.append((v, a8(imagen(v)).resize((560, 315), Image.LANCZOS), info))
    for v in ("N10", "N4"):
        if v != ref:
            fila.append((f"dif_{v}", mapa_dif(imagen(v), imagen(ref)).resize((560, 315), Image.BILINEAR),
                         [f"{v} contra {ref}, ×8 (azul: más oscuro)"]))
    bloques.append((f"Noche (CAM_03): clamp indirecto {'sin clamp, ' if ref == 'N0' else ''}10 y 4", fila))
if "POLI1" in res:
    p0, p1 = res["POLI0"], res["POLI1"]
    bloques.append(("Poligonaje: letras tal cual y subdivididas (la misma forma)", [
        ("POLI0", a8(imagen("POLI0")).resize((640, 360), Image.LANCZOS),
         [f"{p0['triangulos'] / 1e6:.2f} M triángulos", f"{p0['tiempo']:.0f} s (prep. {p0['preparacion']:.0f} s)",
          f"{p0['memoria_mb']:.0f} MB"]),
        ("POLI1", a8(imagen("POLI1")).resize((640, 360), Image.LANCZOS),
         [f"{p1['triangulos'] / 1e6:.2f} M triángulos", f"{p1['tiempo']:.0f} s (prep. {p1['preparacion']:.0f} s)",
          f"{p1['memoria_mb']:.0f} MB"])]))
if bloques:
    m = 24
    W = max(sum(im.width + m for _, im, _ in imgs) + m for _, imgs in bloques)
    H = 90 + sum(60 + max(im.height for _, im, _ in imgs) + 90 for _, imgs in bloques)
    hoja = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(hoja)
    d.text((m, 20), "Vidrio y sol, clamp de noche y poligonaje", font=fh, fill=TINTA)
    y = 90
    for titulo, imgs in bloques:
        d.text((m, y), titulo, font=ft, fill=TINTA)
        y += 40
        x = m
        for v, im, info in imgs:
            hoja.paste(im, (x, y))
            d.text((x, y + im.height + 6), NOMBRES.get(v, "diferencia" if v.startswith("dif") else v), font=fs, fill=TINTA)
            for i, t in enumerate(info):
                d.text((x, y + im.height + 30 + 22 * i), c(t), font=fs, fill=GRIS)
            x += im.width + m
        y += max(im.height for _, im, _ in imgs) + 110
    hoja.save(f"{salida}/Prueba_vidrio_sol_noche_poligonos.jpg", quality=90)
    print("hoja", f"{salida}/Prueba_vidrio_sol_noche_poligonos.jpg", hoja.size)
