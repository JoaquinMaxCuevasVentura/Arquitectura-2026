"""Une las franjas de render_banda.py en un PNG de 16 bits y un JPG de 8 bits con difuminado.

En el solape, las franjas se funden con una rampa lineal: así no se nota la costura del eliminador de ruido, que trabaja
cada franja por separado. Corre con Python común (numpy, pypng y Pillow).

Uso: python unir_bandas.py salida_sin_extension n_bandas solape_px
"""
import os
import sys

import numpy as np
import png
from PIL import Image

base, n, solape = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])


def leer(p):
    w, h, filas, info = png.Reader(filename=p).asDirect()
    return np.vstack([np.asarray(f, dtype=np.float64) for f in filas]).reshape(h, w, info["planes"])


bandas = [leer(f"{base}_banda{i}.png") for i in range(n)]
H, W = bandas[0].shape[:2]
paso = H / n
acum, peso = np.zeros((H, W, 3)), np.zeros((H, 1, 1))
y = np.arange(H)
for i, b in enumerate(bandas):
    ini, fin = max(0, i * paso - solape), min(H, (i + 1) * paso + solape)
    w = np.clip(np.minimum(y - ini, fin - y) / (2 * solape), 0, 1)       # rampa en los bordes de la franja
    if i == 0:                                                            # sin rampa en el borde de la imagen
        w[y < paso] = np.where(y[y < paso] < paso - solape, 1, w[y < paso])
    if i == n - 1:
        w[y >= H - paso] = np.where(y[y >= H - paso] > H - paso + solape, 1, w[y >= H - paso])
    w = w * ((y >= ini) & (y < fin))
    acum += b[:, :, :3] * w[:, None, None]
    peso += w[:, None, None]
img = acum / np.maximum(peso, 1e-9)

out16 = np.clip(np.round(img), 0, 65535).astype(np.uint16)
png.from_array(out16.reshape(H, W * 3), "RGB;16").save(f"{base}_tmp.png")
os.replace(f"{base}_tmp.png", f"{base}.png")
img8 = img / 257.0 + np.random.default_rng(7).uniform(-0.5, 0.5, img.shape)     # difuminado: sin bandas en el cielo
Image.fromarray(np.clip(np.round(img8), 0, 255).astype(np.uint8)).save(f"{base}_tmp.jpg", quality=95, subsampling=0)
os.replace(f"{base}_tmp.jpg", f"{base}.jpg")
print("[UNIDA]", base, W, H, "peso mínimo", float(peso.min()))
