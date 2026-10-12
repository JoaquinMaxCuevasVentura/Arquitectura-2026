/* A pulso · geometría
 * Homografía, polilíneas, simplificación, distancias y ejes.
 */
(function (raiz) {
  'use strict';
  const AP = (raiz.APulso = raiz.APulso || {});

  // ---------- homografía ----------

  /** Resuelve A·x = b por eliminación gaussiana con pivoteo parcial. */
  function resolver(A, b) {
    const n = b.length;
    const M = A.map((fila, i) => fila.concat([b[i]]));
    for (let c = 0; c < n; c++) {
      let piv = c;
      for (let f = c + 1; f < n; f++) if (Math.abs(M[f][c]) > Math.abs(M[piv][c])) piv = f;
      if (Math.abs(M[piv][c]) < 1e-12) throw new Error('Sistema singular: revisa que las cuatro marcas no estén alineadas.');
      [M[c], M[piv]] = [M[piv], M[c]];
      for (let f = c + 1; f < n; f++) {
        const k = M[f][c] / M[c][c];
        for (let j = c; j <= n; j++) M[f][j] -= k * M[c][j];
      }
    }
    const x = new Array(n).fill(0);
    for (let f = n - 1; f >= 0; f--) {
      let s = M[f][n];
      for (let j = f + 1; j < n; j++) s -= M[f][j] * x[j];
      x[f] = s / M[f][f];
    }
    return x;
  }

  /** Homografía H que lleva cuatro puntos de origen a cuatro de destino. */
  function homografia(origen, destino) {
    if (origen.length !== 4 || destino.length !== 4) throw new Error('La homografía necesita cuatro pares de puntos.');
    const A = [];
    const b = [];
    for (let i = 0; i < 4; i++) {
      const [x, y] = origen[i];
      const [u, v] = destino[i];
      A.push([x, y, 1, 0, 0, 0, -u * x, -u * y]);
      b.push(u);
      A.push([0, 0, 0, x, y, 1, -v * x, -v * y]);
      b.push(v);
    }
    const h = resolver(A, b);
    return [
      [h[0], h[1], h[2]],
      [h[3], h[4], h[5]],
      [h[6], h[7], 1],
    ];
  }

  function aplicarH(H, x, y) {
    const w = H[2][0] * x + H[2][1] * y + H[2][2];
    return [(H[0][0] * x + H[0][1] * y + H[0][2]) / w, (H[1][0] * x + H[1][1] * y + H[1][2]) / w];
  }

  function invertirH(H) {
    const [[a, b, c], [d, e, f], [g, h, i]] = H;
    const A = e * i - f * h;
    const B = -(d * i - f * g);
    const C = d * h - e * g;
    const det = a * A + b * B + c * C;
    if (Math.abs(det) < 1e-15) throw new Error('Homografía no invertible');
    const inv = [
      [A, -(b * i - c * h), b * f - c * e],
      [B, a * i - c * g, -(a * f - c * d)],
      [C, -(a * h - b * g), a * e - b * d],
    ].map((fila) => fila.map((v) => v / det));
    const k = inv[2][2];
    return inv.map((fila) => fila.map((v) => v / k));
  }

  // ---------- polilíneas ----------

  function dist(a, b) {
    return Math.hypot(a[0] - b[0], a[1] - b[1]);
  }

  function longitud(poli) {
    let s = 0;
    for (let i = 1; i < poli.length; i++) s += dist(poli[i - 1], poli[i]);
    return s;
  }

  function distPuntoSegmento(p, a, b) {
    const dx = b[0] - a[0];
    const dy = b[1] - a[1];
    const l2 = dx * dx + dy * dy;
    let t = l2 ? ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2 : 0;
    t = Math.max(0, Math.min(1, t));
    return Math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy));
  }

  /** Distancia mínima de un punto a un conjunto de polilíneas. */
  function distPuntoPolilineas(p, polis) {
    let min = Infinity;
    for (const poli of polis) {
      if (poli.length === 1) min = Math.min(min, dist(p, poli[0]));
      for (let i = 1; i < poli.length; i++) {
        const d = distPuntoSegmento(p, poli[i - 1], poli[i]);
        if (d < min) min = d;
      }
    }
    return min;
  }

  /** Simplificación de Ramer–Douglas–Peucker, iterativa. */
  function simplificar(poli, eps) {
    if (poli.length < 3) return poli.slice();
    const conservar = new Uint8Array(poli.length);
    conservar[0] = conservar[poli.length - 1] = 1;
    const pila = [[0, poli.length - 1]];
    while (pila.length) {
      const [i0, i1] = pila.pop();
      let dmax = 0;
      let imax = -1;
      for (let i = i0 + 1; i < i1; i++) {
        const d = distPuntoSegmento(poli[i], poli[i0], poli[i1]);
        if (d > dmax) {
          dmax = d;
          imax = i;
        }
      }
      if (dmax > eps && imax > 0) {
        conservar[imax] = 1;
        pila.push([i0, imax], [imax, i1]);
      }
    }
    return poli.filter((_, i) => conservar[i]);
  }

  /** Media móvil que conserva los extremos. Si la polilínea es cerrada, también suaviza el cierre. */
  function suavizar(poli, ventana) {
    const n = poli.length;
    const r = Math.floor(ventana / 2);
    if (n < 3 || r < 1) return poli.map((p) => p.slice());
    const cerrada = n > 3 && dist(poli[0], poli[n - 1]) < 1e-9;
    const out = [];
    for (let i = 0; i < n; i++) {
      if (!cerrada && (i === 0 || i === n - 1)) {
        out.push(poli[i].slice());
        continue;
      }
      let sx = 0;
      let sy = 0;
      let c = 0;
      const rr = cerrada ? r : Math.min(r, i, n - 1 - i);
      for (let k = -rr; k <= rr; k++) {
        let j = i + k;
        if (cerrada) j = ((j % (n - 1)) + (n - 1)) % (n - 1);
        sx += poli[j][0];
        sy += poli[j][1];
        c++;
      }
      out.push([sx / c, sy / c]);
    }
    if (cerrada) out[n - 1] = out[0].slice();
    return out;
  }

  /** Remuestrea una polilínea con puntos separados por «paso» a lo largo del recorrido. */
  function remuestrear(poli, paso) {
    if (poli.length < 2) return poli.map((p) => p.slice(0, 2));
    const out = [poli[0].slice(0, 2)];
    let resto = paso;
    for (let i = 1; i < poli.length; i++) {
      let a = poli[i - 1];
      const b = poli[i];
      let d = dist(a, b);
      while (d >= resto) {
        const t = resto / d;
        const p = [a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])];
        out.push(p);
        a = p;
        d = dist(a, b);
        resto = paso;
      }
      resto -= d;
    }
    const ult = poli[poli.length - 1];
    if (dist(out[out.length - 1], ult) > paso * 0.25) out.push(ult.slice(0, 2));
    return out;
  }

  function caja(polis) {
    let x0 = Infinity;
    let y0 = Infinity;
    let x1 = -Infinity;
    let y1 = -Infinity;
    for (const poli of polis)
      for (const p of poli) {
        if (p[0] < x0) x0 = p[0];
        if (p[0] > x1) x1 = p[0];
        if (p[1] < y0) y0 = p[1];
        if (p[1] > y1) y1 = p[1];
      }
    return { x0, y0, x1, y1, w: x1 - x0, h: y1 - y0 };
  }

  /**
   * Eje principal de un conjunto de puntos (y hacia arriba).
   * Devuelve el ángulo respecto de la vertical en grados: positivo si la parte superior se inclina a la derecha.
   */
  function anguloEje(puntos) {
    const n = puntos.length;
    if (n < 2) return 0;
    let mx = 0;
    let my = 0;
    for (const p of puntos) {
      mx += p[0];
      my += p[1];
    }
    mx /= n;
    my /= n;
    let sxx = 0;
    let syy = 0;
    let sxy = 0;
    for (const p of puntos) {
      const dx = p[0] - mx;
      const dy = p[1] - my;
      sxx += dx * dx;
      syy += dy * dy;
      sxy += dx * dy;
    }
    const theta = 0.5 * Math.atan2(2 * sxy, sxx - syy); // ángulo del eje mayor respecto del eje x
    let vx = Math.cos(theta);
    let vy = Math.sin(theta);
    if (vy < 0) {
      vx = -vx;
      vy = -vy;
    }
    return (Math.atan2(vx, vy) * 180) / Math.PI;
  }

  AP.geometria = {
    resolver,
    homografia,
    aplicarH,
    invertirH,
    dist,
    longitud,
    distPuntoSegmento,
    distPuntoPolilineas,
    simplificar,
    suavizar,
    remuestrear,
    caja,
    anguloEje,
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = AP;
})(typeof window !== 'undefined' ? window : globalThis);
