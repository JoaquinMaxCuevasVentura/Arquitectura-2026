#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy>=1.21", "pillow>=9.1"]
# ///
"""Revelado de serie del Aeropuerto de Uyuni: un "Lightroom a medida" que unifica el color de las fotos
generadas con IA para que parezcan tomadas por una sola persona, con una misma cámara y un mismo revelado.

Dos formas de uso (detalles en UNIFICAR_COLOR.md):
  uv run unificar_color.py --app CARPETA     abre la aplicación en el navegador: ajustes en vivo y exportación
  uv run unificar_color.py CARPETA           procesa toda la carpeta en lote, con los ajustes guardados
En Windows también se puede arrastrar la carpeta sobre Revelado_Uyuni.bat. Con numpy y Pillow ya instalados
sirve igual "python unificar_color.py ...".

Qué hace con cada foto:
  1. la clasifica por luz (día / hora azul) y mide su firma: color de la luz (bordes acromáticos), brillo de lo
     iluminado, punto negro y blanco, saturación y tono del cielo y del corten;
  2. la acerca al consenso de su grupo, o a la foto de referencia que elijas;
  3. le aplica el revelado común: temperatura, exposición, curva con hombro, saturación, vibrancia, virado,
     nitidez, grano y viñeteo;
  4. exporta las fotos, una hoja antes/después, un informe y, si se pide, LUT .cube por foto.
Los ajustes se guardan en _ajustes_revelado.json dentro de la carpeta de fotos.
"""
import argparse
import copy
import hashlib
import io
import json
import math
import sys
import threading
import unicodedata
from pathlib import Path

import numpy as np
from PIL import Image, ImageCms, ImageDraw, ImageFont, ImageOps

EXTENSIONES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}
PATRONES_NOCHE = ["CAM_03", "CREPUSC", "NOCHE", "NOCTURN", "HORA AZUL", "HORA_AZUL", "ATARDECER", "NIGHT",
                  "DUSK", "BLUE HOUR"]
ARCHIVO_AJUSTES = "_ajustes_revelado.json"

# Revelado común. L, a, b son coordenadas OKLab (L de 0 a 1; a y b, ± ~0,3).
BASE = dict(exposicion=0.0, temperatura=0.0, matiz=0.0, contraste=0.12, hombro=0.90, negro=0.012,
            saturacion=0.94, vibrancia=0.0, limite_croma=0.17, virado=1.0,
            tono_sombras=(-0.002, -0.006), tono_luces=(0.002, 0.007), nitidez=0.35, grano=0.010, vineta=0.16)
LOOKS = {
    # sobrio y elegante: contraste moderado, negros apenas levantados, luces con hombro, saturación contenida,
    # sombras levemente frías y luces levemente cálidas
    "sobrio": dict(BASE),
    # sin virado y con poco grano: solo unifica
    "neutro": dict(BASE, contraste=0.06, hombro=0.92, negro=0.0, saturacion=1.0, limite_croma=0.20, virado=0.0,
                   nitidez=0.25, grano=0.006, vineta=0.08),
    # como "sobrio", con luces más cálidas (sol de altura a media mañana)
    "calido": dict(BASE, temperatura=0.15, saturacion=0.96, limite_croma=0.18, tono_sombras=(0.0, -0.003),
                   tono_luces=(0.004, 0.012)),
}
# Controles de la aplicación: (clave, etiqueta, mínimo, máximo, paso, sección)
CONTROLES = [
    ("exposicion", "Exposición (EV)", -1.5, 1.5, 0.05, "Luz"),
    ("temperatura", "Temperatura", -1.0, 1.0, 0.01, "Luz"),
    ("matiz", "Matiz", -1.0, 1.0, 0.01, "Luz"),
    ("contraste", "Contraste", -0.2, 0.5, 0.01, "Tono"),
    ("hombro", "Altas luces (hombro)", 0.75, 1.0, 0.005, "Tono"),
    ("negro", "Negros (mate)", 0.0, 0.08, 0.002, "Tono"),
    ("saturacion", "Saturación", 0.5, 1.5, 0.01, "Color"),
    ("vibrancia", "Vibrancia", -0.5, 0.8, 0.01, "Color"),
    ("limite_croma", "Límite de saturación", 0.08, 0.32, 0.005, "Color"),
    ("virado", "Virado (sombras frías, luces cálidas)", 0.0, 3.0, 0.05, "Color"),
    ("nitidez", "Nitidez", 0.0, 1.5, 0.05, "Detalle"),
    ("grano", "Grano", 0.0, 0.04, 0.001, "Detalle"),
    ("vineta", "Viñeteo", 0.0, 0.6, 0.01, "Detalle"),
]
RANGOS = {c[0]: (c[2], c[3]) for c in CONTROLES}

# Familias de tono que delatan "cámaras distintas" (tono OKLab en grados). Medido en las vistas del modelo:
# cielo ≈ 250°, corten ≈ 31–38° (chocolate y piel quedan fuera por croma y luminancia)
FAMILIAS = {
    "cielo": dict(centro=245.0, ancho=35.0, L=(0.45, 0.97), C_min=0.025, dh_max=10.0, k=(0.85, 1.20)),
    "corten": dict(centro=40.0, ancho=25.0, L=(0.28, 0.68), C_min=0.07, dh_max=6.0, k=(0.90, 1.12)),
}

_LUM = np.array([0.2126, 0.7152, 0.0722], np.float32)
_M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                [0.2119034982, 0.6806995451, 0.1073969566],
                [0.0883024619, 0.2817188376, 0.6299787005]], np.float32)
_M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                [1.9779984951, -2.4285922050, 0.4505937099],
                [0.0259040371, 0.7827717662, -0.8086757660]], np.float32)
_M1_INV = np.linalg.inv(_M1.astype(np.float64)).astype(np.float32)
_M2_INV = np.linalg.inv(_M2.astype(np.float64)).astype(np.float32)


# =============================================================================
# Color: sRGB <-> lineal <-> OKLab
# =============================================================================
def srgb_a_lineal(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4).astype(np.float32)


def lineal_a_srgb(x):
    x = np.clip(x, 0.0, None)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055).astype(np.float32)


def lineal_a_oklab(rgb):
    return np.cbrt(np.clip(rgb @ _M1.T, 0.0, None)) @ _M2.T


def oklab_a_lineal(lab):
    return ((lab @ _M2_INV.T) ** 3) @ _M1_INV.T


def luminancia(lin):
    return lin @ _LUM


def suave(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def dif_angulo(a, b):
    """Diferencia angular a - b en grados, en (-180, 180]."""
    return (np.asarray(a) - b + 180.0) % 360.0 - 180.0


# =============================================================================
# Entrada y salida
# =============================================================================
def cargar(ruta, lado_largo=0):
    """Imagen como sRGB en coma flotante (0-1). Convierte a sRGB si trae otro perfil (p. ej. Display P3)."""
    im = ImageOps.exif_transpose(Image.open(ruta))
    icc = im.info.get("icc_profile")
    if im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        fondo = Image.new("RGB", im.size, (255, 255, 255))
        fondo.paste(im, mask=im.getchannel("A"))
        im = fondo
    elif im.mode != "RGB":
        im = im.convert("RGB")
    if icc:
        try:
            im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)),
                                           ImageCms.createProfile("sRGB"), outputMode="RGB")
        except Exception:
            pass                                    # perfil ilegible: se asume sRGB
    if lado_largo and max(im.size) > lado_largo:
        f = lado_largo / max(im.size)
        im = im.resize((max(1, round(im.width * f)), max(1, round(im.height * f))), Image.LANCZOS)
    return np.asarray(im, dtype=np.float32) / 255.0


def a_imagen(arr):
    return Image.fromarray((np.clip(arr, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8))


def reducir(arr, lado_largo):
    im = a_imagen(arr)
    if max(im.size) > lado_largo:
        f = lado_largo / max(im.size)
        im = im.resize((max(1, round(im.width * f)), max(1, round(im.height * f))), Image.LANCZOS)
    return np.asarray(im, dtype=np.float32) / 255.0


def a_jpeg(arr, calidad=88):
    buf = io.BytesIO()
    a_imagen(arr).save(buf, format="JPEG", quality=calidad)
    return buf.getvalue()


def guardar(arr, ruta, formato, calidad):
    im = a_imagen(arr)
    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    if formato == "jpg":
        im.save(ruta, quality=calidad, subsampling=0, optimize=True, icc_profile=icc)
    elif formato == "png":
        im.save(ruta, icc_profile=icc)
    else:
        im.save(ruta, compression="tiff_lzw", icc_profile=icc)


def fuente(tam):
    for ruta in ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "arial.ttf",
                 "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try:
            return ImageFont.truetype(ruta, tam)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=tam)
    except TypeError:
        return ImageFont.load_default()


# =============================================================================
# Medición (sobre copias reducidas)
# =============================================================================
def validos(srgb):
    """Píxeles sin recortar: sirven para medir color."""
    return (srgb.max(axis=-1) < 0.985) & (srgb.min(axis=-1) > 0.01)


def _unidad(v):
    v = np.asarray(v, np.float32)
    return v / max(float(luminancia(v)), 1e-6)


def iluminante(lin, lab, ok):
    """Color de la luz (lineal, luminancia 1) según los bordes acromáticos de la imagen (gray-edge).

    De los estimadores probados con dominantes conocidas, es el que menos depende del encuadre, así que
    permite comparar vistas distintas. No cuenta los colores saturados (corten) ni el cielo: cuanto más cielo
    tiene una vista, más "azul" parecería su luz."""
    L, C = lab[..., 0], np.hypot(lab[..., 1], lab[..., 2])
    h = np.degrees(np.arctan2(lab[..., 2], lab[..., 1])) % 360.0
    cielo = (np.abs(dif_angulo(h, 245.0)) < 45.0) & (C > 0.02)
    m = (ok & (C < 0.08) & ~cielo & (L > 0.2) & (L < 0.95))[:-1, :-1]
    if m.sum() < 0.01 * m.size:
        return None
    gx = np.abs(np.diff(lin, axis=1))[:-1]
    gy = np.abs(np.diff(lin, axis=0))[:, :-1]
    e = np.sqrt(gx * gx + gy * gy)[m]
    return _unidad(np.sqrt((e * e).mean(axis=0)))


def nivel_exposicion(lin, ok):
    """Brillo de lo iluminado: percentil 90 de lo que no está recortado. La mediana varía ±1,6 EV con el
    encuadre; este indicador, solo ±0,2 EV en las vistas del modelo."""
    y = luminancia(lin)
    y = y[ok] if ok.sum() > 0.05 * ok.size else y.ravel()
    return float(np.percentile(y, 90))


def croma_media(L, a, b, ok):
    C = np.hypot(a, b)
    sel = ok & (L > 0.3) & (L < 0.9) & (C > 0.01)
    return float(C[sel].mean()) if sel.sum() > 0.01 * ok.size else None


def medir_familia(L, a, b, ok, spec):
    C = np.hypot(a, b)
    h = np.degrees(np.arctan2(b, a)) % 360.0
    sel = (ok & (np.abs(dif_angulo(h, spec["centro"])) < spec["ancho"]) & (C > spec["C_min"])
           & (L > spec["L"][0]) & (L < spec["L"][1]))
    if sel.sum() < 0.005 * ok.size:
        return None
    w, hr = C[sel], np.radians(h[sel])
    hm = math.degrees(math.atan2(float((w * np.sin(hr)).sum()), float((w * np.cos(hr)).sum()))) % 360.0
    return dict(h=hm, C=float(C[sel].mean()))


def es_noche(nombre, srgb):
    """Hora azul / noche: por el nombre o porque la franja superior (el cielo) y el conjunto son oscuros."""
    if any(p in nombre.upper() for p in PATRONES_NOCHE):
        return True
    y = luminancia(srgb_a_lineal(srgb))
    return float(np.median(y[: max(1, y.shape[0] // 5)])) < 0.12 and float(np.median(y)) < 0.10


def firma(srgb):
    """Lo que se mide en una foto, tal cual."""
    lin = srgb_a_lineal(srgb)
    lab = lineal_a_oklab(lin)
    ok = validos(srgb)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    return dict(luz=iluminante(lin, lab, ok), brillo=nivel_exposicion(lin, ok),
                niveles=tuple(float(v) for v in np.percentile(L, [0.5, 99.5])),
                croma=croma_media(L, a, b, ok),
                familias={k: medir_familia(L, a, b, ok, s) for k, s in FAMILIAS.items()})


def consenso(firmas):
    """Firma "promedio" de un grupo: el punto al que se acercan todas sus fotos."""
    luces = [f["luz"] for f in firmas if f["luz"] is not None]
    cromas = [f["croma"] for f in firmas if f["croma"]]
    res = dict(luz=_unidad(np.exp(np.mean(np.log(np.maximum(luces, 1e-6)), axis=0))) if luces else None,
               brillo=float(np.median([f["brillo"] for f in firmas])),
               niveles=(float(np.median([f["niveles"][0] for f in firmas])),
                        float(np.median([f["niveles"][1] for f in firmas]))),
               croma=float(np.median(cromas)) if cromas else None, familias={})
    for k in FAMILIAS:
        ms = [f["familias"][k] for f in firmas if f["familias"].get(k)]
        if ms:
            hr = np.radians([m["h"] for m in ms])
            res["familias"][k] = dict(h=math.degrees(math.atan2(float(np.sin(hr).mean()),
                                                                float(np.cos(hr).mean()))) % 360.0,
                                      C=float(np.median([m["C"] for m in ms])))
    return res


def identidad():
    return dict(ganancias=[1.0, 1.0, 1.0], ev=0.0, niveles=None, sat=1.0, familias={})


def ganancias_bb(luz_img, luz_ref, fuerza):
    """Ganancias RGB que llevan la luz estimada de la foto a la del objetivo, sin cambiar la luminancia."""
    if luz_img is None or luz_ref is None:
        return np.ones(3, np.float32)
    g = np.clip((luz_ref / np.maximum(luz_img, 1e-6)) ** fuerza, 0.80, 1.25)
    return (g / float(luminancia(g * luz_img))).astype(np.float32)


def ajustar(srgb, obj, fuerza):
    """Parámetros que acercan una foto (copia reducida) a su objetivo, etapa por etapa, con indicadores que
    dependen poco del encuadre."""
    f = dict(bb=fuerza, ev=0.6 * fuerza, niveles=0.6 * fuerza, sat=0.6 * fuerza, familias=0.8 * fuerza)
    ok = validos(srgb)
    lin = srgb_a_lineal(srgb)
    g = ganancias_bb(iluminante(lin, lineal_a_oklab(lin), ok), obj["luz"], f["bb"])
    lin = lin * g
    brillo, ev = nivel_exposicion(lin, ok), 0.0
    if brillo > 1e-4 and obj["brillo"] > 1e-4:
        ev = float(np.clip(f["ev"] * math.log2(obj["brillo"] / brillo), -0.8, 0.8))
    lab = lineal_a_oklab(lin * np.float32(2.0 ** ev))
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    lo, hi = (float(v) for v in np.percentile(L, [0.5, 99.5]))
    niveles = (lo, hi, obj["niveles"][0], obj["niveles"][1], f["niveles"])
    L = aplicar_niveles(L, niveles)
    # saturación global: por la croma de los tonos comparables entre vistas (cielo, corten); si no hay, la media
    razones = []
    for nombre, spec in FAMILIAS.items():
        m, r = medir_familia(L, a, b, ok, spec), obj["familias"].get(nombre)
        if m and r:
            razones.append(r["C"] / m["C"])
    if razones:
        base, fs = math.exp(float(np.mean(np.log(razones)))), f["sat"]
    else:
        c = croma_media(L, a, b, ok)
        base, fs = ((obj["croma"] / c) if c and obj["croma"] else 1.0), 0.3 * fuerza
    sat = float(np.clip(base ** fs, 0.80, 1.25))
    a, b = a * sat, b * sat
    familias = {}
    for nombre, spec in FAMILIAS.items():
        m, r = medir_familia(L, a, b, ok, spec), obj["familias"].get(nombre)
        if m and r:
            dh = float(np.clip(dif_angulo(r["h"], m["h"]) * f["familias"], -spec["dh_max"], spec["dh_max"]))
            k = float(np.clip((r["C"] / m["C"]) ** f["familias"], *spec["k"]))
            familias[nombre] = dict(centro=m["h"], ancho=spec["ancho"], C_min=spec["C_min"], dh=dh, k=k)
    return dict(ganancias=[float(v) for v in g], ev=ev, niveles=niveles, sat=sat, familias=familias)


# =============================================================================
# Revelado
# =============================================================================
def aplicar_niveles(L, niveles):
    """Lleva el punto negro y el blanco (percentiles 0,5 y 99,5) hacia los del objetivo."""
    if not niveles:
        return L
    lo_i, hi_i, lo_r, hi_r, f = niveles
    pendiente = float(np.clip((hi_r - lo_r) / max(hi_i - lo_i, 1e-3), 0.80, 1.30))
    return L + f * ((lo_r + (L - lo_i) * pendiente) - L)


def aplicar_familias(L, a, b, familias):
    """Gira el tono y escala la croma solo dentro de cada familia (cielo, corten), con bordes suaves."""
    if not familias:
        return a, b
    C = np.hypot(a, b)
    h = np.arctan2(b, a)
    giro = np.zeros_like(C)
    escala = np.ones_like(C)
    for fam in familias.values():
        d = dif_angulo(np.degrees(h), fam["centro"])
        w = np.where(np.abs(d) < fam["ancho"], np.cos(np.pi / 2 * d / fam["ancho"]) ** 2, 0.0)
        w = w * suave(0.5 * fam["C_min"], 1.5 * fam["C_min"], C)
        giro += w * math.radians(fam["dh"])
        escala *= 1.0 + w * (fam["k"] - 1.0)
    C, h = C * escala, h + giro
    return (C * np.cos(h)).astype(np.float32), (C * np.sin(h)).astype(np.float32)


def ganancias_look(look):
    """Temperatura (+ cálido) y matiz (+ magenta) como ganancias RGB que no cambian el brillo."""
    t, m = look["temperatura"], look["matiz"]
    g = np.array([1.0 + 0.10 * t, 1.0 - 0.06 * m, 1.0 - 0.10 * t], np.float32)
    return g / float(luminancia(g))


def curva_tono(L, look):
    """Curva en S alrededor del gris medio, hombro suave en las altas luces y negro apenas levantado."""
    g, p = 1.0 + look["contraste"], 0.56
    x = np.clip(L, 0.0, None)
    xa = np.clip(x, 0.0, 1.0)
    s = np.where(xa < p, p * np.power(xa / p, g), 1.0 - (1.0 - p) * np.power((1.0 - xa) / (1.0 - p), g))
    s = s + np.maximum(x - 1.0, 0.0)                # lo que pasa de 1 sigue al hombro
    k = min(look["hombro"], 0.999)
    s = np.where(s > k, k + (1.0 - k) * np.tanh((s - k) / (1.0 - k)), s)
    return look["negro"] + (1.0 - look["negro"]) * s


def limitar_croma(a, b, rodilla, maximo=0.34):
    """Compresión suave de los colores más saturados: iguala los excesos típicos de cada herramienta."""
    C = np.hypot(a, b)
    C2 = np.where(C > rodilla, rodilla + (maximo - rodilla) * np.tanh((C - rodilla) / (maximo - rodilla)), C)
    f = np.where(C > 1e-6, C2 / np.maximum(C, 1e-6), 1.0)
    return a * f, b * f


def virar(L, a, b, look):
    ws = (1.0 - suave(0.15, 0.60, L)) * look["virado"]
    wl = suave(0.55, 0.95, L) * look["virado"]
    (sa, sb), (la, lb) = look["tono_sombras"], look["tono_luces"]
    return a + ws * sa + wl * la, b + ws * sb + wl * lb


def _caja(x, r, eje):
    """Desenfoque de caja de radio r a lo largo de un eje (sumas acumuladas)."""
    if r < 1:
        return x
    pad = [(0, 0)] * x.ndim
    pad[eje] = (r + 1, r)
    c = np.cumsum(np.pad(x, pad, mode="edge"), axis=eje, dtype=np.float64)
    n = x.shape[eje]
    alto = [slice(None)] * x.ndim
    bajo = [slice(None)] * x.ndim
    alto[eje], bajo[eje] = slice(2 * r + 1, 2 * r + 1 + n), slice(0, n)
    return ((c[tuple(alto)] - c[tuple(bajo)]) / (2 * r + 1)).astype(np.float32)


def desenfoque(x, sigma):
    """Aproximación gaussiana con tres desenfoques de caja (sin depender de scipy)."""
    if sigma < 0.3:
        return x
    w = math.sqrt(12 * sigma * sigma / 3 + 1)
    wl = int(w) - (1 - int(w) % 2)
    m = round((12 * sigma * sigma - 3 * wl * wl - 12 * wl - 9) / (-4 * wl - 4))
    for i in range(3):
        r = ((wl if i < m else wl + 2) - 1) // 2
        x = _caja(_caja(x, r, 0), r, 1)
    return x


def nitidez(L, cantidad, sigma):
    if cantidad <= 0:
        return L
    detalle = L - desenfoque(L, sigma)
    detalle = detalle * suave(0.002, 0.006, np.abs(detalle))    # umbral: no realza el ruido plano
    return L + cantidad * detalle


def grano(L, intensidad, sigma, semilla):
    """Grano de luminancia con el mismo carácter en todas las fotos (más en los medios tonos)."""
    if intensidad <= 0:
        return L
    ruido = np.random.default_rng(semilla).standard_normal(L.shape).astype(np.float32)
    if sigma >= 0.3:
        ruido = desenfoque(ruido, sigma)
        ruido /= max(float(ruido.std()), 1e-6)
    peso = 0.35 + 0.65 * 4.0 * np.clip(L, 0, 1) * (1.0 - np.clip(L, 0, 1))
    return L + intensidad * peso * ruido


def vineta(lin, k):
    if k <= 0:
        return lin
    h, w = lin.shape[:2]
    y, x = np.ogrid[:h, :w]
    r = np.hypot((x - (w - 1) / 2) / (w / 2), (y - (h - 1) / 2) / (h / 2)) / math.sqrt(2)
    return lin * (1.0 - k * suave(0.45, 1.15, r)).astype(np.float32)[..., None]


def revelar(srgb, p, look, semilla=0, efectos=True):
    """Igualación de la foto (parámetros p) + revelado común (look). Sin efectos es solo color (sirve de LUT)."""
    g = np.asarray(p["ganancias"], np.float32) * ganancias_look(look)
    lin = srgb_a_lineal(srgb) * g * np.float32(2.0 ** (p["ev"] + look["exposicion"]))
    lab = lineal_a_oklab(lin)
    L, a, b = lab[..., 0].copy(), lab[..., 1].copy(), lab[..., 2].copy()
    del lin, lab
    L = aplicar_niveles(L, p["niveles"])
    a, b = a * np.float32(p["sat"]), b * np.float32(p["sat"])
    a, b = aplicar_familias(L, a, b, p["familias"])
    L = curva_tono(L, look)
    a, b = a * np.float32(look["saturacion"]), b * np.float32(look["saturacion"])
    if look["vibrancia"]:
        k = 1.0 + look["vibrancia"] * (1.0 - suave(0.0, 0.18, np.hypot(a, b)))
        a, b = a * k, b * k
    a, b = limitar_croma(a, b, look["limite_croma"])
    a, b = virar(L, a, b, look)
    if efectos:
        ancho = srgb.shape[1]
        L = nitidez(L, look["nitidez"], max(0.6, ancho / 2400))
        L = grano(L, look["grano"], 0.25 * ancho / 1280, semilla)
    lin = oklab_a_lineal(np.stack([L, a, b], axis=-1).astype(np.float32))
    if efectos:
        lin = vineta(lin, look["vineta"])
    return np.clip(lineal_a_srgb(lin), 0.0, 1.0)


def exportar_cube(ruta, p, look, titulo, n=33):
    """LUT 3D (.cube) con la parte de color del revelado, para Photoshop, DaVinci, etc."""
    t = np.linspace(0.0, 1.0, n, dtype=np.float32)
    b, g, r = np.meshgrid(t, t, t, indexing="ij")              # el rojo varía más rápido (norma .cube)
    rejilla = np.stack([r, g, b], axis=-1).reshape(n, n * n, 3)
    salida = revelar(rejilla, p, look, efectos=False).reshape(-1, 3)
    titulo = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode("ascii").replace('"', "'")
    with open(ruta, "w", encoding="ascii", newline="\n") as f:
        f.write(f'TITLE "{titulo}"\nLUT_3D_SIZE {n}\nDOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n')
        np.savetxt(f, salida, fmt="%.6f")


# =============================================================================
# Serie: fotos, grupos, objetivos y ajustes (lo comparten la aplicación y el modo por lotes)
# =============================================================================
def semilla(nombre):
    return int(hashlib.md5(nombre.encode("utf-8")).hexdigest()[:8], 16)


class Serie:
    LADO_MEDIR, LADO_VISTA, LADO_MINI = 600, 1600, 360

    def __init__(self, carpeta):
        self.carpeta = Path(carpeta)
        rutas = sorted((p for p in self.carpeta.iterdir()
                        if p.is_file() and p.suffix.lower() in EXTENSIONES and not p.name.startswith("_")),
                       key=lambda p: p.name.lower())
        self.fotos = [dict(ruta=r, nombre=r.name, grupo=None, ev=0.0, saturacion=1.0) for r in rutas]
        self.preset = "sobrio"
        self.look = dict(LOOKS["sobrio"])
        self.fuerza = 0.7
        self.referencia = {"dia": None, "noche": None}          # nombre de archivo, o None = consenso
        self.exportacion = dict(formato="jpg", calidad=95, lado_largo=0, lut=False)
        self._cache = {}
        self._params = None
        self._candado = threading.RLock()
        self.cargar_ajustes()

    # ---- copias en memoria (uint8) ------------------------------------------
    def _copia(self, i, lado):
        clave = (i, lado)
        if clave not in self._cache:
            arr = cargar(self.fotos[i]["ruta"], lado)
            self._cache[clave] = (arr * 255.0 + 0.5).astype(np.uint8)
        return self._cache[clave].astype(np.float32) / 255.0

    def medir(self, i):
        return self._copia(i, self.LADO_MEDIR)

    def vista(self, i):
        return self._copia(i, self.LADO_VISTA)

    def mini(self, i):
        return self._copia(i, self.LADO_MINI)

    # ---- grupos y parámetros ------------------------------------------------
    def grupo_auto(self, i):
        clave = ("grupo", i)
        if clave not in self._cache:
            self._cache[clave] = "noche" if es_noche(self.fotos[i]["nombre"], self.medir(i)) else "dia"
        return self._cache[clave]

    def grupo(self, i):
        return self.fotos[i]["grupo"] or self.grupo_auto(i)

    def firma(self, i):
        clave = ("firma", i)
        if clave not in self._cache:
            self._cache[clave] = firma(self.medir(i))
        return self._cache[clave]

    def invalidar(self):
        with self._candado:
            self._params = None

    def parametros(self):
        with self._candado:
            if self._params is None:
                params = {}
                for g in ("dia", "noche"):
                    ids = [i for i in range(len(self.fotos)) if self.grupo(i) == g]
                    if not ids:
                        continue
                    ref = next((i for i in ids if self.fotos[i]["nombre"] == self.referencia.get(g)), None)
                    obj = self.firma(ref) if ref is not None else consenso([self.firma(i) for i in ids])
                    for i in ids:
                        params[i] = identidad() if (i == ref or len(ids) == 1) else ajustar(self.medir(i), obj,
                                                                                           self.fuerza)
                self._params = params
            return self._params

    def params_foto(self, i):
        p = copy.deepcopy(self.parametros()[i])
        p["ev"] += float(self.fotos[i]["ev"])
        p["sat"] *= float(self.fotos[i]["saturacion"])
        return p

    def revelar(self, i, srgb, efectos=True):
        return revelar(srgb, self.params_foto(i), self.look, semilla(self.fotos[i]["nombre"]), efectos)

    # ---- ajustes -------------------------------------------------------------
    def cambiar_look(self, cambios):
        if "preset" in cambios and cambios["preset"] in LOOKS:
            self.preset = cambios["preset"]
            self.look = dict(LOOKS[self.preset])
        for clave, valor in (cambios.get("look") or {}).items():
            if clave in RANGOS and isinstance(valor, (int, float)):
                lo, hi = RANGOS[clave]
                self.look[clave] = float(min(max(valor, lo), hi))
        if isinstance(cambios.get("fuerza"), (int, float)):
            nueva = float(min(max(cambios["fuerza"], 0.0), 1.0))
            if nueva != self.fuerza:
                self.fuerza = nueva
                self.invalidar()
        for clave in ("formato", "calidad", "lado_largo", "lut"):
            if clave in (cambios.get("exportacion") or {}):
                self.exportacion[clave] = cambios["exportacion"][clave]

    def cambiar_foto(self, i, cambios):
        foto = self.fotos[i]
        if "grupo" in cambios and cambios["grupo"] in (None, "dia", "noche"):
            foto["grupo"] = cambios["grupo"]
            self.invalidar()
        if "referencia" in cambios:
            g = self.grupo(i)
            self.referencia[g] = foto["nombre"] if cambios["referencia"] else None
            self.invalidar()
        if isinstance(cambios.get("ev"), (int, float)):
            foto["ev"] = float(min(max(cambios["ev"], -1.5), 1.5))
        if isinstance(cambios.get("saturacion"), (int, float)):
            foto["saturacion"] = float(min(max(cambios["saturacion"], 0.5), 1.5))

    def estado(self):
        return dict(carpeta=str(self.carpeta.resolve()), preset=self.preset, presets=sorted(LOOKS), look=self.look,
                    fuerza=self.fuerza, referencia=self.referencia, exportacion=self.exportacion,
                    controles=CONTROLES,
                    fotos=[dict(id=i, nombre=f["nombre"], grupo=self.grupo(i), grupo_manual=f["grupo"],
                                referencia=self.referencia.get(self.grupo(i)) == f["nombre"],
                                ev=f["ev"], saturacion=f["saturacion"]) for i, f in enumerate(self.fotos)])

    def guardar_ajustes(self):
        datos = dict(preset=self.preset, look=self.look, fuerza=self.fuerza, referencia=self.referencia,
                     exportacion=self.exportacion,
                     fotos={f["nombre"]: dict(grupo=f["grupo"], ev=f["ev"], saturacion=f["saturacion"])
                            for f in self.fotos if f["grupo"] or f["ev"] or f["saturacion"] != 1.0})
        (self.carpeta / ARCHIVO_AJUSTES).write_text(json.dumps(datos, ensure_ascii=False, indent=1),
                                                    encoding="utf-8")

    def cargar_ajustes(self):
        ruta = self.carpeta / ARCHIVO_AJUSTES
        if not ruta.exists():
            return
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        self.cambiar_look(dict(preset=datos.get("preset", "sobrio")))
        for clave in ("tono_sombras", "tono_luces"):
            if clave in (datos.get("look") or {}):
                self.look[clave] = tuple(datos["look"][clave])
        self.cambiar_look(dict(look=datos.get("look") or {}, fuerza=datos.get("fuerza", self.fuerza),
                               exportacion=datos.get("exportacion") or {}))
        self.referencia.update({k: v for k, v in (datos.get("referencia") or {}).items() if k in self.referencia})
        por_nombre = {f["nombre"]: f for f in self.fotos}
        for nombre, extra in (datos.get("fotos") or {}).items():
            if nombre in por_nombre:
                por_nombre[nombre].update({k: v for k, v in extra.items() if k in ("grupo", "ev", "saturacion")})

    # ---- exportación ---------------------------------------------------------
    def exportar(self, salida=None, progreso=None):
        opc = self.exportacion
        formato = opc.get("formato", "jpg") if opc.get("formato") in ("jpg", "png", "tif") else "jpg"
        salida = Path(salida) if salida else self.carpeta / "serie_unificada"
        salida.mkdir(parents=True, exist_ok=True)
        if opc.get("lut"):
            (salida / "luts").mkdir(exist_ok=True)
            exportar_cube(salida / "luts" / f"_look_{self.preset}.cube", identidad(), self.look,
                          f"UYUNI look {self.preset}")
        ext = {"jpg": ".jpg", "png": ".png", "tif": ".tif"}[formato]
        filas, informe = [], []
        for i, foto in enumerate(self.fotos):
            srgb = cargar(foto["ruta"], int(opc.get("lado_largo") or 0))
            out = self.revelar(i, srgb)
            guardar(out, salida / (foto["ruta"].stem + ext), formato, int(opc.get("calidad") or 95))
            if opc.get("lut"):
                exportar_cube(salida / "luts" / (foto["ruta"].stem + ".cube"), self.params_foto(i), self.look,
                              f"UYUNI {foto['ruta'].stem}")
            antes, despues = self.medir(i), reducir(out, self.LADO_MEDIR)
            filas.append((foto["nombre"], antes, despues))
            p = self.params_foto(i)
            informe.append(dict(archivo=foto["nombre"], grupo=self.grupo(i),
                                referencia=self.referencia.get(self.grupo(i)) or "consenso del grupo",
                                ganancias_rgb=[round(v, 4) for v in p["ganancias"]], ev=round(p["ev"], 3),
                                saturacion=round(p["sat"], 3),
                                familias={k: dict(giro_grados=round(v["dh"], 2), croma=round(v["k"], 3))
                                          for k, v in p["familias"].items()},
                                antes=indicadores(antes), despues=indicadores(despues)))
            if progreso:
                progreso(i + 1, len(self.fotos))
        resumen = {}
        for g in ("dia", "noche"):
            fg = [r for r in informe if r["grupo"] == g]
            if len(fg) > 1:
                resumen[g] = dict(antes=dispersion([r["antes"] for r in fg]),
                                  despues=dispersion([r["despues"] for r in fg]))
        (salida / "_informe.json").write_text(
            json.dumps(dict(preset=self.preset, look=self.look, fuerza=self.fuerza, resumen_dispersion=resumen,
                            fotos=informe), ensure_ascii=False, indent=1), encoding="utf-8")
        hoja_comparacion(filas, salida / "_comparacion.jpg",
                         f"Revelado de serie · look {self.preset} · igualación {self.fuerza:.2f}")
        return salida, resumen


# =============================================================================
# Informe y hoja de comparación
# =============================================================================
def indicadores(srgb):
    """Lo que delata cámaras distintas: color de la luz, brillo de lo iluminado y tono del cielo."""
    lin = srgb_a_lineal(srgb)
    lab = lineal_a_oklab(lin)
    ok = validos(srgb)
    luz = iluminante(lin, lab, ok)
    luz_ab = lineal_a_oklab(luz[None, :])[0, 1:] if luz is not None else None
    cielo = medir_familia(lab[..., 0], lab[..., 1], lab[..., 2], ok, FAMILIAS["cielo"])
    return dict(luz_ab=[round(float(v), 4) for v in luz_ab] if luz_ab is not None else None,
                brillo_ev=round(math.log2(max(nivel_exposicion(lin, ok), 1e-5)), 3),
                cielo_tono=round(cielo["h"], 1) if cielo else None)


def dispersion(medidas):
    """Cuánto difieren entre sí las fotos de un grupo (luz en milésimas OKLab, brillo en EV, cielo en grados)."""
    ab = np.array([m["luz_ab"] for m in medidas if m["luz_ab"]])
    ev = np.array([m["brillo_ev"] for m in medidas])
    cielo = np.radians([m["cielo_tono"] for m in medidas if m["cielo_tono"] is not None])
    res = dict(balance_blancos=round(float(np.sqrt(ab.var(axis=0).sum())) * 1000, 2) if len(ab) > 1 else None,
               exposicion_ev=round(float(ev.std()), 3) if len(ev) > 1 else None, tono_cielo_grados=None)
    if len(cielo) > 1:
        r = math.hypot(float(np.cos(cielo).mean()), float(np.sin(cielo).mean()))
        res["tono_cielo_grados"] = round(math.degrees(math.sqrt(max(-2 * math.log(max(r, 1e-9)), 0.0))), 2)
    return res


def hoja_comparacion(filas, ruta, titulo, ancho=560):
    f_tit, f_txt = fuente(26), fuente(18)
    m, cab = 16, 34
    miniaturas = []
    for nombre, antes, despues in filas:
        par = []
        for arr in (antes, despues):
            im = a_imagen(arr)
            par.append(im.resize((ancho, max(1, round(im.height * ancho / im.width))), Image.LANCZOS))
        miniaturas.append((nombre, par))
    alto = 70 + sum(max(p[0].height, p[1].height) + cab + m for _, p in miniaturas) + m
    hoja = Image.new("RGB", (2 * ancho + 3 * m, alto), (238, 238, 236))
    d = ImageDraw.Draw(hoja)
    d.text((m, 18), titulo, fill=(20, 20, 20), font=f_tit)
    y = 70
    for nombre, (a, b) in miniaturas:
        d.text((m, y + 6), f"{nombre}  ·  antes", fill=(60, 60, 60), font=f_txt)
        d.text((2 * m + ancho, y + 6), "después", fill=(60, 60, 60), font=f_txt)
        hoja.paste(a, (m, y + cab))
        hoja.paste(b, (2 * m + ancho, y + cab))
        y += max(a.height, b.height) + cab + m
    hoja.save(ruta, quality=88)


# =============================================================================
# Aplicación en el navegador ("Lightroom a medida")
# =============================================================================
PAGINA = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Uyuni · Revelado de serie</title>
<style>
:root{--fondo:#151515;--barra:#1c1c1c;--panel:#202020;--panel2:#2a2a2a;--borde:#333;--texto:#dedede;--suave:#9a9a9a;--acento:#d4823c}
*{box-sizing:border-box}html,body{height:100%;margin:0}
body{background:var(--fondo);color:var(--texto);font:13px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
 display:grid;grid-template-rows:46px minmax(0,1fr);grid-template-columns:210px minmax(0,1fr) 330px;
 grid-template-areas:"cab cab cab" "tira visor panel";overflow:hidden}
header{grid-area:cab;display:flex;align-items:center;gap:14px;padding:0 14px;background:var(--barra);border-bottom:1px solid var(--borde)}
header h1{font-size:14px;font-weight:600;margin:0 8px 0 0;white-space:nowrap}
header h1 b{color:var(--acento);font-weight:600}
header .ruta{color:var(--suave);font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;min-width:0}
.seg{display:inline-flex;border:1px solid var(--borde);border-radius:6px;overflow:hidden;flex:none}
.seg button{background:transparent;color:var(--suave);border:0;padding:5px 11px;cursor:pointer;font:inherit}
.seg button+button{border-left:1px solid var(--borde)}
.seg button.on{background:var(--panel2);color:var(--texto)}
#tira{grid-area:tira;overflow-y:auto;background:var(--barra);border-right:1px solid var(--borde);padding:8px}
.mini{position:relative;margin-bottom:9px;cursor:pointer;border:2px solid transparent;border-radius:5px;overflow:hidden;background:#111}
.mini.sel{border-color:var(--acento)}
.mini img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover}
.mini .nom{font-size:11px;color:var(--suave);padding:3px 5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.etq{position:absolute;top:5px;left:5px;font-size:10px;padding:1px 6px;border-radius:3px;background:rgba(0,0,0,.7);color:#eee}
.etq.noche{background:rgba(30,50,110,.85)}
.estrella{position:absolute;top:2px;right:6px;color:#ffcf4a;font-size:15px;text-shadow:0 0 3px #000}
#visor{grid-area:visor;position:relative;overflow:hidden;background:#111}
#foto{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding:14px}
#marco{position:relative;line-height:0;max-width:100%;max-height:100%}
#imgDespues{display:block;max-width:100%;max-height:calc(100vh - 74px);user-select:none}
#imgAntes{position:absolute;inset:0;width:100%;height:100%;user-select:none;pointer-events:none}
#divisor{position:absolute;top:0;bottom:0;width:2px;background:#fff;box-shadow:0 0 4px #000;cursor:ew-resize}
#divisor::after{content:"";position:absolute;top:50%;left:-9px;width:20px;height:20px;margin-top:-10px;border-radius:50%;background:#fff;box-shadow:0 0 4px #000}
.rot{position:absolute;bottom:10px;font-size:11px;background:rgba(0,0,0,.6);padding:2px 7px;border-radius:3px;line-height:1.4}
#rotA{left:10px}#rotD{right:10px}
#visor.cargando #imgDespues{opacity:.75;transition:opacity .2s}
#serie{position:absolute;inset:0;overflow-y:auto;padding:14px;display:none;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));grid-auto-rows:max-content;gap:12px;align-content:start}
#serie .tarjeta{cursor:pointer;background:#1b1b1b;border-radius:5px;overflow:hidden;border:2px solid transparent}
#serie .tarjeta.sel{border-color:var(--acento)}
#serie img{display:block;width:100%;aspect-ratio:16/9;object-fit:contain;background:#0c0c0c}
#serie .nom{font-size:11px;color:var(--suave);padding:4px 6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#panel{grid-area:panel;overflow-y:auto;background:var(--panel);border-left:1px solid var(--borde)}
details{border-bottom:1px solid var(--borde)}
summary{cursor:pointer;padding:10px 14px;font-weight:600;font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:#cfcfcf;list-style:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"▸";display:inline-block;width:14px;color:var(--suave)}
details[open] summary::before{content:"▾"}
.cuerpo{padding:2px 14px 14px}
.sub{font-size:11px;color:var(--suave);text-transform:uppercase;letter-spacing:.05em;margin:12px 0 4px}
.ctl{margin:7px 0}
.ctl .fila{display:flex;justify-content:space-between;font-size:12px;color:#c8c8c8}
.ctl .val{color:var(--suave);font-variant-numeric:tabular-nums;cursor:pointer}
input[type=range]{width:100%;accent-color:var(--acento);margin:3px 0 0}
select,input[type=number]{background:var(--panel2);color:var(--texto);border:1px solid var(--borde);border-radius:4px;padding:4px 6px;font:inherit}
.boton{background:var(--panel2);color:var(--texto);border:1px solid var(--borde);border-radius:5px;padding:6px 10px;cursor:pointer;font:inherit}
.boton:hover{border-color:#555}
.boton.primario{background:var(--acento);border-color:var(--acento);color:#1a1209;font-weight:600;width:100%;padding:8px}
.boton:disabled{opacity:.5;cursor:default}
.nota{font-size:11.5px;color:var(--suave);margin:6px 0}
.linea{display:flex;gap:8px;align-items:center;margin:8px 0}
.linea label{flex:1;font-size:12px;color:#c8c8c8}
#barra{height:6px;background:var(--panel2);border-radius:3px;overflow:hidden;margin:10px 0 4px}
#barra div{height:100%;width:0;background:var(--acento);transition:width .2s}
kbd{background:var(--panel2);border:1px solid var(--borde);border-radius:3px;padding:0 4px;font-size:11px}
</style></head><body>
<header>
 <h1>Uyuni · <b>Revelado de serie</b></h1>
 <div class="seg" id="segVista"><button data-v="foto" class="on">Foto</button><button data-v="serie">Serie</button></div>
 <div class="seg" id="segComp"><button data-c="antes">Antes</button><button data-c="dividido" class="on">Dividido</button><button data-c="despues">Después</button></div>
 <div class="ruta" id="ruta"></div>
</header>
<nav id="tira"></nav>
<main id="visor">
 <div id="foto"><div id="marco"><img id="imgDespues" alt=""><img id="imgAntes" alt=""><div id="divisor"></div>
  <span class="rot" id="rotA">Antes</span><span class="rot" id="rotD">Después</span></div></div>
 <div id="serie"></div>
</main>
<aside id="panel">
 <details open><summary>Igualación de la serie</summary><div class="cuerpo">
  <div class="ctl"><div class="fila"><span>Fuerza de igualación</span><span class="val" id="vFuerza"></span></div>
   <input type="range" id="fuerza" min="0" max="1" step="0.05"></div>
  <p class="nota" id="txtRef"></p>
  <div class="sub">Esta foto</div>
  <div class="linea"><label>Grupo de luz</label>
   <div class="seg" id="segGrupo"><button data-g="">Auto</button><button data-g="dia">Día</button><button data-g="noche">Hora azul</button></div></div>
  <div class="linea"><button class="boton" id="btnRef" style="flex:1"></button></div>
  <div class="ctl"><div class="fila"><span>Exposición de esta foto (EV)</span><span class="val" id="vEv"></span></div>
   <input type="range" id="evFoto" min="-1.5" max="1.5" step="0.05"></div>
  <div class="ctl"><div class="fila"><span>Saturación de esta foto</span><span class="val" id="vSat"></span></div>
   <input type="range" id="satFoto" min="0.5" max="1.5" step="0.01"></div>
 </div></details>
 <details open><summary>Revelado común (todas las fotos)</summary><div class="cuerpo">
  <div class="linea"><label>Preset</label><select id="preset"></select><button class="boton" id="btnReset" title="Vuelve a los valores del preset">Restablecer</button></div>
  <div id="controles"></div>
  <p class="nota">Doble clic en un valor lo devuelve al del preset.</p>
 </div></details>
 <details open><summary>Exportar</summary><div class="cuerpo">
  <div class="linea"><label>Formato</label><select id="formato"><option value="jpg">JPG</option><option value="png">PNG</option><option value="tif">TIFF</option></select></div>
  <div class="linea"><label>Calidad JPG</label><input type="number" id="calidad" min="60" max="100" style="width:70px"></div>
  <div class="linea"><label>Lado largo en px (0 = original)</label><input type="number" id="lado" min="0" max="12000" step="100" style="width:80px"></div>
  <div class="linea"><label><input type="checkbox" id="lut"> LUT .cube por foto</label></div>
  <button class="boton primario" id="btnExportar">Exportar serie</button>
  <div id="barra"><div></div></div><p class="nota" id="txtExport"></p>
  <p class="nota">Atajos: <kbd>←</kbd> <kbd>→</kbd> cambiar de foto · <kbd>\</kbd> antes/después · <kbd>G</kbd> vista de serie.<br>Los ajustes se guardan solos en la carpeta (_ajustes_revelado.json).</p>
 </div></details>
</aside>
<script>
const $ = s => document.querySelector(s);
let E = null, sel = 0, vista = 'foto', comp = 'dividido', version = 0, divisor = 0.5, presetBase = {};
async function api(ruta, datos) {
  const op = datos === undefined ? {} : {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(datos)};
  const r = await fetch(ruta, op);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
const num = (v, d) => Number(v).toFixed(d);
const decimales = paso => Math.max(0, (String(paso).split('.')[1] || '').length);
let temporizadores = {};
function programar(clave, fn, ms = 180) { clearTimeout(temporizadores[clave]); temporizadores[clave] = setTimeout(fn, ms); }

async function iniciar() {
  E = await api('/api/estado');
  $('#ruta').textContent = E.carpeta + ' · ' + E.fotos.length + ' fotos';
  $('#preset').innerHTML = E.presets.map(p => `<option>${p}</option>`).join('');
  presetBase = await api('/api/preset?nombre=' + E.preset);
  construirControles(); construirTira(); refrescarPanel(); mostrar();
  $('#formato').value = E.exportacion.formato; $('#calidad').value = E.exportacion.calidad;
  $('#lado').value = E.exportacion.lado_largo; $('#lut').checked = !!E.exportacion.lut;
}
function construirControles() {
  let html = '', seccion = '';
  for (const [clave, etiqueta, min, max, paso, sec] of E.controles) {
    if (sec !== seccion) { html += `<div class="sub">${sec}</div>`; seccion = sec; }
    html += `<div class="ctl"><div class="fila"><span>${etiqueta}</span><span class="val" data-k="${clave}"></span></div>
      <input type="range" data-k="${clave}" min="${min}" max="${max}" step="${paso}"></div>`;
  }
  $('#controles').innerHTML = html;
  for (const [clave, , , , paso] of E.controles) {
    const r = $(`input[data-k="${clave}"]`), v = $(`.val[data-k="${clave}"]`);
    r.value = E.look[clave]; v.textContent = num(E.look[clave], decimales(paso));
    r.addEventListener('input', () => { E.look[clave] = parseFloat(r.value); v.textContent = num(r.value, decimales(paso)); programar('look', enviarLook); });
    v.addEventListener('dblclick', () => { if (clave in presetBase) { E.look[clave] = presetBase[clave]; r.value = presetBase[clave]; v.textContent = num(presetBase[clave], decimales(paso)); enviarLook(); } });
  }
  $('#preset').value = E.preset; $('#fuerza').value = E.fuerza; $('#vFuerza').textContent = num(E.fuerza, 2);
}
function construirTira() {
  $('#tira').innerHTML = E.fotos.map(f => `<div class="mini${f.id === sel ? ' sel' : ''}" data-id="${f.id}">
    <img loading="lazy" src="/api/miniatura?id=${f.id}&v=${version}" alt="">
    <span class="etq${f.grupo === 'noche' ? ' noche' : ''}">${f.grupo === 'noche' ? 'Hora azul' : 'Día'}</span>
    ${f.referencia ? '<span class="estrella">★</span>' : ''}<div class="nom" title="${f.nombre}">${f.nombre}</div></div>`).join('');
  document.querySelectorAll('.mini').forEach(d => d.addEventListener('click', () => elegir(+d.dataset.id)));
  if (vista === 'serie') construirSerie();
}
function construirSerie() {
  $('#serie').innerHTML = E.fotos.map(f => `<div class="tarjeta${f.id === sel ? ' sel' : ''}" data-id="${f.id}">
    <img src="/api/miniatura?id=${f.id}&v=${version}" alt=""><div class="nom">${f.grupo === 'noche' ? '☾ ' : ''}${f.referencia ? '★ ' : ''}${f.nombre}</div></div>`).join('');
  document.querySelectorAll('.tarjeta').forEach(d => d.addEventListener('click', () => { elegir(+d.dataset.id); cambiarVista('foto'); }));
}
function elegir(id) {
  if (id < 0 || id >= E.fotos.length) return;
  sel = id;
  document.querySelectorAll('.mini').forEach(d => d.classList.toggle('sel', +d.dataset.id === sel));
  document.querySelector(`.mini[data-id="${sel}"]`)?.scrollIntoView({block: 'nearest'});
  refrescarPanel(); mostrar();
}
function refrescarPanel() {
  const f = E.fotos[sel];
  document.querySelectorAll('#segGrupo button').forEach(b => b.classList.toggle('on', b.dataset.g === (f.grupo_manual || '')));
  $('#btnRef').textContent = f.referencia ? '★ Es la referencia de su grupo (quitar)' : '☆ Usar esta foto como referencia';
  const ref = E.referencia[f.grupo];
  $('#txtRef').textContent = `Grupo "${f.grupo === 'noche' ? 'hora azul' : 'día'}": cada foto se acerca ` + (ref ? `a la referencia ★ ${ref}.` : 'al consenso del grupo (sin referencia elegida).');
  $('#evFoto').value = f.ev; $('#vEv').textContent = num(f.ev, 2);
  $('#satFoto').value = f.saturacion; $('#vSat').textContent = num(f.saturacion, 2);
}
function mostrar() { if (vista === 'foto') cargarFoto(); else construirSerie(); }
function cargarFoto() {
  const id = sel, v = version;
  $('#visor').classList.add('cargando');
  const img = new Image();
  img.onload = () => { if (id === sel && v === version) { $('#imgDespues').src = img.src; $('#visor').classList.remove('cargando'); aplicarComparacion(); } };
  img.src = `/api/vista?id=${id}&modo=despues&v=${v}`;
  $('#imgAntes').src = `/api/vista?id=${id}&modo=antes`;
}
function aplicarComparacion() {
  const antes = $('#imgAntes'), div = $('#divisor');
  $('#rotA').style.display = comp === 'despues' ? 'none' : '';
  $('#rotD').style.display = comp === 'antes' ? 'none' : '';
  if (comp === 'antes') { antes.style.clipPath = 'none'; antes.style.display = ''; div.style.display = 'none'; }
  else if (comp === 'despues') { antes.style.display = 'none'; div.style.display = 'none'; }
  else { antes.style.display = ''; antes.style.clipPath = `inset(0 ${100 - divisor * 100}% 0 0)`; div.style.display = ''; div.style.left = `calc(${divisor * 100}% - 1px)`; }
}
function refrescarTodo() {
  version++;
  if (vista === 'foto') cargarFoto(); else construirSerie();
  document.querySelectorAll('.mini img').forEach((im, i) => { im.src = `/api/miniatura?id=${i}&v=${version}`; });
}
async function enviarLook() { await api('/api/ajustes', {look: E.look}); refrescarTodo(); }
async function enviarFoto(cambios) {
  E = Object.assign(E, await api('/api/foto', Object.assign({id: sel}, cambios)));
  construirTira(); refrescarPanel(); refrescarTodo();
}
function cambiarVista(v) {
  vista = v;
  document.querySelectorAll('#segVista button').forEach(b => b.classList.toggle('on', b.dataset.v === v));
  $('#foto').style.display = v === 'foto' ? 'flex' : 'none';
  $('#serie').style.display = v === 'serie' ? 'grid' : 'none';
  $('#segComp').style.visibility = v === 'foto' ? 'visible' : 'hidden';
  mostrar();
}
function cambiarComp(c) { comp = c; document.querySelectorAll('#segComp button').forEach(b => b.classList.toggle('on', b.dataset.c === c)); aplicarComparacion(); }

document.querySelectorAll('#segVista button').forEach(b => b.addEventListener('click', () => cambiarVista(b.dataset.v)));
document.querySelectorAll('#segComp button').forEach(b => b.addEventListener('click', () => cambiarComp(b.dataset.c)));
document.querySelectorAll('#segGrupo button').forEach(b => b.addEventListener('click', () => enviarFoto({grupo: b.dataset.g || null})));
$('#btnRef').addEventListener('click', () => enviarFoto({referencia: !E.fotos[sel].referencia}));
$('#evFoto').addEventListener('input', e => { $('#vEv').textContent = num(e.target.value, 2); E.fotos[sel].ev = parseFloat(e.target.value); programar('foto', () => enviarFoto({ev: E.fotos[sel].ev})); });
$('#satFoto').addEventListener('input', e => { $('#vSat').textContent = num(e.target.value, 2); E.fotos[sel].saturacion = parseFloat(e.target.value); programar('foto', () => enviarFoto({saturacion: E.fotos[sel].saturacion})); });
$('#fuerza').addEventListener('input', e => { $('#vFuerza').textContent = num(e.target.value, 2); programar('fuerza', async () => { await api('/api/ajustes', {fuerza: parseFloat(e.target.value)}); refrescarTodo(); }, 300); });
$('#preset').addEventListener('change', async e => { const r = await api('/api/ajustes', {preset: e.target.value}); E.look = r.look; E.preset = r.preset; presetBase = await api('/api/preset?nombre=' + E.preset); construirControles(); refrescarTodo(); });
$('#btnReset').addEventListener('click', async () => { const r = await api('/api/ajustes', {preset: E.preset}); E.look = r.look; construirControles(); refrescarTodo(); });
['formato', 'calidad', 'lado', 'lut'].forEach(id => $('#' + id).addEventListener('change', () => api('/api/ajustes', {exportacion: opcionesExport()})));
function opcionesExport() { return {formato: $('#formato').value, calidad: parseInt($('#calidad').value) || 95, lado_largo: parseInt($('#lado').value) || 0, lut: $('#lut').checked}; }
$('#btnExportar').addEventListener('click', async () => {
  $('#btnExportar').disabled = true; $('#txtExport').textContent = 'Exportando…';
  await api('/api/exportar', opcionesExport());
  const sondeo = setInterval(async () => {
    const p = await api('/api/progreso');
    $('#barra div').style.width = (p.total ? 100 * p.hechas / p.total : 0) + '%';
    if (p.error) { clearInterval(sondeo); $('#btnExportar').disabled = false; $('#txtExport').textContent = 'Error: ' + p.error; }
    else if (!p.activa && p.hechas === p.total && p.total) { clearInterval(sondeo); $('#btnExportar').disabled = false;
      $('#txtExport').textContent = `Listo: ${p.total} fotos en ${p.carpeta} (con _comparacion.jpg e _informe.json).`; }
    else $('#txtExport').textContent = `Exportando ${p.hechas} de ${p.total}…`;
  }, 600);
});
(function arrastrarDivisor() {
  let arrastrando = false;
  const mover = x => { const r = $('#marco').getBoundingClientRect(); divisor = Math.min(1, Math.max(0, (x - r.left) / r.width)); aplicarComparacion(); };
  $('#marco').addEventListener('mousedown', e => { if (comp === 'dividido') { arrastrando = true; mover(e.clientX); e.preventDefault(); } });
  window.addEventListener('mousemove', e => { if (arrastrando) mover(e.clientX); });
  window.addEventListener('mouseup', () => { arrastrando = false; });
})();
document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT' && e.target.type !== 'range') return;
  if (e.key === 'ArrowRight') { elegir(sel + 1); e.preventDefault(); }
  else if (e.key === 'ArrowLeft') { elegir(sel - 1); e.preventDefault(); }
  else if (e.key === '\\') cambiarComp(comp === 'antes' ? 'despues' : 'antes');
  else if (e.key === 'g' || e.key === 'G') cambiarVista(vista === 'foto' ? 'serie' : 'foto');
});
iniciar().catch(err => { document.body.innerHTML = '<p style="padding:20px">No pude iniciar: ' + err.message + '</p>'; });
</script></body></html>
"""


def aplicacion(serie, puerto=8765, abrir=True):
    """Servidor local (solo en este equipo) con la interfaz de revelado."""
    import webbrowser
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from urllib.parse import parse_qs, urlparse

    estado_export = dict(activa=False, hechas=0, total=0, carpeta="", error="")

    def exportar_en_segundo_plano():
        try:
            def progreso(hechas, total):
                estado_export.update(hechas=hechas, total=total)
            salida, _ = serie.exportar(progreso=progreso)
            estado_export.update(carpeta=str(salida))
        except Exception as e:                      # se informa en la interfaz
            estado_export.update(error=str(e))
        finally:
            estado_export.update(activa=False)

    class Manejador(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _enviar(self, datos, tipo, codigo=200):
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(datos)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(datos)

        def _json(self, obj, codigo=200):
            self._enviar(json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", codigo)

        def _id(self, valor):
            try:
                i = int(valor)
            except (TypeError, ValueError):
                return None
            return i if 0 <= i < len(serie.fotos) else None

        def do_GET(self):
            u = urlparse(self.path)
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            try:
                if u.path == "/":
                    self._enviar(PAGINA.encode("utf-8"), "text/html; charset=utf-8")
                elif u.path == "/api/estado":
                    self._json(serie.estado())
                elif u.path == "/api/preset":
                    self._json({k: v for k, v in LOOKS.get(q.get("nombre"), LOOKS["sobrio"]).items() if k in RANGOS})
                elif u.path in ("/api/vista", "/api/miniatura"):
                    i = self._id(q.get("id"))
                    if i is None:
                        return self._json({"error": "foto inexistente"}, 404)
                    srgb = serie.vista(i) if u.path == "/api/vista" else serie.mini(i)
                    if q.get("modo") != "antes":
                        srgb = serie.revelar(i, srgb)
                    self._enviar(a_jpeg(srgb, 90 if u.path == "/api/vista" else 82), "image/jpeg")
                elif u.path == "/api/progreso":
                    self._json(estado_export)
                else:
                    self._json({"error": "no encontrado"}, 404)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_POST(self):
            u = urlparse(self.path)
            try:
                datos = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            except ValueError:
                return self._json({"error": "JSON inválido"}, 400)
            if u.path == "/api/ajustes":
                serie.cambiar_look(datos)
                serie.guardar_ajustes()
                self._json(dict(look=serie.look, preset=serie.preset, fuerza=serie.fuerza))
            elif u.path == "/api/foto":
                i = self._id(datos.get("id"))
                if i is None:
                    return self._json({"error": "foto inexistente"}, 404)
                serie.cambiar_foto(i, datos)
                serie.guardar_ajustes()
                e = serie.estado()
                self._json(dict(fotos=e["fotos"], referencia=e["referencia"]))
            elif u.path == "/api/exportar":
                if estado_export["activa"]:
                    return self._json({"error": "ya hay una exportación en curso"}, 409)
                serie.cambiar_look(dict(exportacion=datos))
                serie.guardar_ajustes()
                estado_export.update(activa=True, hechas=0, total=len(serie.fotos), carpeta="", error="")
                threading.Thread(target=exportar_en_segundo_plano, daemon=True).start()
                self._json({"ok": True})
            else:
                self._json({"error": "no encontrado"}, 404)

    servidor = None
    for p in range(puerto, puerto + 20):
        try:
            servidor = ThreadingHTTPServer(("127.0.0.1", p), Manejador)
            break
        except OSError:
            continue
    if servidor is None:
        sys.exit("No encontré un puerto libre para la aplicación.")
    url = f"http://127.0.0.1:{servidor.server_address[1]}/"
    print(f"Revelado de serie: {len(serie.fotos)} fotos de {serie.carpeta}")
    print(f"Abre {url} en el navegador (Ctrl+C para salir).")
    if abrir:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nAplicación cerrada. Los ajustes quedaron guardados en la carpeta.")


# =============================================================================
# Programa
# =============================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Revelado de serie: unifica el color de las fotos para que parezcan de un mismo fotógrafo.")
    ap.add_argument("carpeta", help="carpeta con las fotos (jpg, png, tif, webp)")
    ap.add_argument("--app", action="store_true", help="abre la aplicación en el navegador")
    ap.add_argument("--puerto", type=int, default=8765)
    ap.add_argument("--no-abrir", action="store_true", help="no abre el navegador (solo con --app)")
    ap.add_argument("-o", "--salida", help="carpeta de salida (por defecto CARPETA/serie_unificada)")
    ap.add_argument("--preset", choices=sorted(LOOKS), help="revelado común (por defecto: sobrio o el guardado)")
    ap.add_argument("--fuerza", type=float, help="cuánto se iguala cada foto a su grupo, 0-1 (por defecto 0,7)")
    ap.add_argument("--referencia", help="foto de referencia del día (parte del nombre); si no, el consenso")
    ap.add_argument("--referencia-noche", help="foto de referencia de la hora azul")
    for clave in RANGOS:
        ap.add_argument(f"--{clave.replace('_', '-')}", dest=clave, type=float, help=f"valor de '{clave}'")
    ap.add_argument("--formato", choices=["jpg", "png", "tif"])
    ap.add_argument("--calidad", type=int)
    ap.add_argument("--lado-largo", type=int, help="redimensiona el lado largo al exportar (0 = sin cambio)")
    ap.add_argument("--lut", action="store_true", help="exporta LUT .cube por foto y la del look común")
    args = ap.parse_args(argv)

    carpeta = Path(args.carpeta)
    if not carpeta.is_dir():
        sys.exit(f"No existe la carpeta: {carpeta}")
    serie = Serie(carpeta)
    if not serie.fotos:
        sys.exit(f"No hay fotos (jpg, png, tif, webp) en {carpeta}")
    if args.preset:
        serie.cambiar_look(dict(preset=args.preset))
    serie.cambiar_look(dict(look={k: getattr(args, k) for k in RANGOS if getattr(args, k) is not None},
                            fuerza=args.fuerza,
                            exportacion={k: v for k, v in dict(formato=args.formato, calidad=args.calidad,
                                                               lado_largo=args.lado_largo).items() if v is not None}))
    if args.lut:
        serie.exportacion["lut"] = True
    for grupo, parte in (("dia", args.referencia), ("noche", args.referencia_noche)):
        if parte:
            nombre = next((f["nombre"] for f in serie.fotos if parte.lower() in f["nombre"].lower()), None)
            if nombre is None:
                print(f"aviso: no encontré '{parte}'; se usa el consenso del grupo")
            serie.referencia[grupo] = nombre

    if args.app:
        serie.guardar_ajustes()
        aplicacion(serie, args.puerto, abrir=not args.no_abrir)
        return
    print(f"Revelando {len(serie.fotos)} fotos · preset {serie.preset} · igualación {serie.fuerza:.2f}")
    for i, f in enumerate(serie.fotos):
        print(f"  {f['nombre'][:60]:60s} {'hora azul' if serie.grupo(i) == 'noche' else 'día'}")
    salida, resumen = serie.exportar(args.salida, progreso=lambda h, t: print(f"  exportadas {h}/{t}", end="\r"))
    print()
    for grupo, res in resumen.items():
        print(f"Diferencias entre fotos del grupo '{grupo}' (antes -> después): "
              f"luz {res['antes']['balance_blancos']} -> {res['despues']['balance_blancos']} | "
              f"brillo {res['antes']['exposicion_ev']} -> {res['despues']['exposicion_ev']} EV | "
              f"cielo {res['antes']['tono_cielo_grados']} -> {res['despues']['tono_cielo_grados']}°")
    print(f"Listo: fotos, _comparacion.jpg e _informe.json en {salida}")


if __name__ == "__main__":
    main()
