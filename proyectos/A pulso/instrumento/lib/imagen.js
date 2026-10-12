/* A pulso · imagen
 * Canal, umbral, componentes, esqueleto (Zhang–Suen), grafo del esqueleto y rasterizado.
 * Trabaja sobre arreglos planos (RGBA o un canal) para poder probarse en node.
 */
(function (raiz) {
  'use strict';
  const AP = (raiz.APulso = raiz.APulso || {});

  // Vecinos en el orden de Zhang–Suen: N, NE, E, SE, S, SO, O, NO.
  const N8 = [
    [0, -1],
    [1, -1],
    [1, 0],
    [1, 1],
    [0, 1],
    [-1, 1],
    [-1, 0],
    [-1, -1],
  ];

  /**
   * Extrae un canal de una imagen RGBA. El azul es el predeterminado: la pauta impresa en cian
   * refleja el azul y desaparece, mientras que el grafito y la tinta negra quedan oscuros.
   */
  function canal(rgba, w, h, tipo) {
    const n = w * h;
    const out = new Uint8ClampedArray(n);
    for (let i = 0, j = 0; i < n; i++, j += 4) {
      const r = rgba[j];
      const g = rgba[j + 1];
      const b = rgba[j + 2];
      switch (tipo) {
        case 'rojo':
          out[i] = r;
          break;
        case 'verde':
          out[i] = g;
          break;
        case 'luminancia':
          out[i] = 0.299 * r + 0.587 * g + 0.114 * b;
          break;
        default:
          out[i] = b;
      }
    }
    return out;
  }

  /** Desenfoque de caja separable aplicado dos veces (aproxima un gaussiano). */
  function desenfocar(gris, w, h, radio) {
    let a = Float32Array.from(gris);
    const r = Math.max(0, Math.round(radio));
    if (r === 0) return a;
    let b = new Float32Array(w * h);
    for (let pasada = 0; pasada < 2; pasada++) {
      for (let y = 0; y < h; y++) {
        let s = 0;
        const fila = y * w;
        for (let x = -r; x <= r; x++) s += a[fila + Math.min(w - 1, Math.max(0, x))];
        for (let x = 0; x < w; x++) {
          b[fila + x] = s / (2 * r + 1);
          s += a[fila + Math.min(w - 1, x + r + 1)] - a[fila + Math.max(0, x - r)];
        }
      }
      for (let x = 0; x < w; x++) {
        let s = 0;
        for (let y = -r; y <= r; y++) s += b[Math.min(h - 1, Math.max(0, y)) * w + x];
        for (let y = 0; y < h; y++) {
          a[y * w + x] = s / (2 * r + 1);
          s += b[Math.min(h - 1, y + r + 1) * w + x] - b[Math.max(0, y - r) * w + x];
        }
      }
    }
    return a;
  }

  function percentil(valores, p) {
    const hist = new Uint32Array(256);
    for (let i = 0; i < valores.length; i++) hist[Math.max(0, Math.min(255, Math.round(valores[i])))]++;
    const objetivo = p * valores.length;
    let acum = 0;
    for (let v = 0; v < 256; v++) {
      acum += hist[v];
      if (acum >= objetivo) return v;
    }
    return 255;
  }

  /** 1 donde el valor es más oscuro que el umbral (tinta), 0 en el resto. */
  function binarizar(gris, umbral) {
    const m = new Uint8Array(gris.length);
    for (let i = 0; i < gris.length; i++) m[i] = gris[i] < umbral ? 1 : 0;
    return m;
  }

  /** Componentes conexas (8 vecinos). */
  function etiquetar(mask, w, h) {
    const etiquetas = new Int32Array(w * h).fill(-1);
    const componentes = [];
    const pila = [];
    for (let i = 0; i < w * h; i++) {
      if (!mask[i] || etiquetas[i] >= 0) continue;
      const id = componentes.length;
      const comp = { id, area: 0, x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity };
      etiquetas[i] = id;
      pila.push(i);
      while (pila.length) {
        const p = pila.pop();
        const x = p % w;
        const y = (p / w) | 0;
        comp.area++;
        if (x < comp.x0) comp.x0 = x;
        if (x > comp.x1) comp.x1 = x;
        if (y < comp.y0) comp.y0 = y;
        if (y > comp.y1) comp.y1 = y;
        for (const [dx, dy] of N8) {
          const X = x + dx;
          const Y = y + dy;
          if (X < 0 || Y < 0 || X >= w || Y >= h) continue;
          const q = Y * w + X;
          if (mask[q] && etiquetas[q] < 0) {
            etiquetas[q] = id;
            pila.push(q);
          }
        }
      }
      componentes.push(comp);
    }
    return { etiquetas, componentes };
  }

  /** Borra en el lugar las componentes con menos de areaMin píxeles. Devuelve las que quedan. */
  function quitarMotas(mask, w, h, areaMin) {
    const { etiquetas, componentes } = etiquetar(mask, w, h);
    const borrar = new Uint8Array(componentes.length);
    for (const c of componentes) if (c.area < areaMin) borrar[c.id] = 1;
    for (let i = 0; i < mask.length; i++) if (mask[i] && borrar[etiquetas[i]]) mask[i] = 0;
    return componentes.filter((c) => !borrar[c.id]);
  }

  /** Adelgazamiento de Zhang–Suen. Devuelve una máscara nueva de un píxel de grosor. */
  function adelgazar(mask, w, h) {
    const m = Uint8Array.from(mask);
    const v = (x, y) => (x >= 0 && y >= 0 && x < w && y < h ? m[y * w + x] : 0);
    let activos = [];
    for (let i = 0; i < m.length; i++) if (m[i]) activos.push(i);
    let cambio = true;
    while (cambio) {
      cambio = false;
      for (let paso = 0; paso < 2; paso++) {
        const borrar = [];
        for (const i of activos) {
          if (!m[i]) continue;
          const x = i % w;
          const y = (i / w) | 0;
          const P = N8.map(([dx, dy]) => v(x + dx, y + dy)); // P2..P9
          const B = P[0] + P[1] + P[2] + P[3] + P[4] + P[5] + P[6] + P[7];
          if (B < 2 || B > 6) continue;
          let A = 0;
          for (let k = 0; k < 8; k++) if (!P[k] && P[(k + 1) % 8]) A++;
          if (A !== 1) continue;
          if (paso === 0) {
            if (P[0] * P[2] * P[4] || P[2] * P[4] * P[6]) continue;
          } else if (P[0] * P[2] * P[6] || P[0] * P[4] * P[6]) continue;
          borrar.push(i);
        }
        if (borrar.length) {
          cambio = true;
          for (const i of borrar) m[i] = 0;
        }
      }
      activos = activos.filter((i) => m[i]);
    }
    return m;
  }

  /**
   * Quita los píxeles redundantes que deja el adelgazamiento (escalones y tramos diagonales de dos
   * píxeles), para que cada píxel de una línea tenga exactamente dos vecinos. Un píxel se borra si es
   * «simple» según el número de conectividad de Yokoi para 8 vecinos (borrarlo no cambia la topología)
   * y no es un extremo.
   */
  function limpiarEscalones(esq, w, h) {
    const v = (x, y) => (x >= 0 && y >= 0 && x < w && y < h ? esq[y * w + x] : 0);
    // Orden de Yokoi: E, NE, N, NO, O, SO, S, SE (índices de N8)
    const orden = [2, 1, 0, 7, 6, 5, 4, 3];
    for (let pasada = 0; pasada < 5; pasada++) {
      let borrados = 0;
      for (let y = 0; y < h; y++)
        for (let x = 0; x < w; x++) {
          const i = y * w + x;
          if (!esq[i]) continue;
          const P = N8.map(([dx, dy]) => v(x + dx, y + dy));
          let vecinos = 0;
          for (const p of P) vecinos += p;
          if (vecinos < 2) continue;
          const c = orden.map((k) => 1 - P[k]); // complemento
          let yokoi = 0;
          for (let k = 0; k < 8; k += 2) yokoi += c[k] - c[k] * c[(k + 1) % 8] * c[(k + 2) % 8];
          if (yokoi === 1) {
            esq[i] = 0;
            borrados++;
          }
        }
      if (!borrados) break;
    }
    return esq;
  }

  /**
   * Convierte un esqueleto en polilíneas (coordenadas de píxel con centro en +0,5).
   * Los ramales cortos que terminan en un extremo (espolones) se podan, y los nodos que quedan
   * con dos aristas se fusionan.
   */
  function esqueletoAPolilineas(esq, w, h, largoEspolon) {
    const vecinos = (i) => {
      const x = i % w;
      const y = (i / w) | 0;
      const out = [];
      for (const [dx, dy] of N8) {
        const X = x + dx;
        const Y = y + dy;
        if (X >= 0 && Y >= 0 && X < w && Y < h && esq[Y * w + X]) out.push(Y * w + X);
      }
      return out;
    };
    const pix = [];
    for (let i = 0; i < esq.length; i++) if (esq[i]) pix.push(i);
    const grado = new Uint8Array(w * h);
    for (const i of pix) grado[i] = vecinos(i).length;
    const esNodo = (i) => grado[i] !== 2;

    // grupos de píxeles nodo contiguos → un nodo
    const grupo = new Int32Array(w * h).fill(-1);
    const nodos = [];
    for (const i of pix) {
      if (!esNodo(i) || grupo[i] >= 0) continue;
      const id = nodos.length;
      const pila = [i];
      grupo[i] = id;
      let sx = 0;
      let sy = 0;
      let c = 0;
      while (pila.length) {
        const p = pila.pop();
        sx += (p % w) + 0.5;
        sy += ((p / w) | 0) + 0.5;
        c++;
        for (const q of vecinos(p))
          if (esNodo(q) && grupo[q] < 0) {
            grupo[q] = id;
            pila.push(q);
          }
      }
      nodos.push({ id, x: sx / c, y: sy / c, pixeles: c });
    }

    const coord = (i) => [(i % w) + 0.5, ((i / w) | 0) + 0.5];
    const visto = new Uint8Array(w * h);
    const pares = new Set();
    let aristas = [];

    for (const p of pix) {
      if (!esNodo(p)) continue;
      for (const q of vecinos(p)) {
        if (esNodo(q)) {
          if (grupo[q] !== grupo[p]) {
            const k = Math.min(grupo[p], grupo[q]) + ',' + Math.max(grupo[p], grupo[q]);
            if (!pares.has(k)) {
              pares.add(k);
              aristas.push({ a: grupo[p], b: grupo[q], pts: [[nodos[grupo[p]].x, nodos[grupo[p]].y], [nodos[grupo[q]].x, nodos[grupo[q]].y]] });
            }
          }
          continue;
        }
        if (visto[q]) continue;
        const camino = [p, q];
        visto[q] = 1;
        let prev = p;
        let cur = q;
        for (;;) {
          let sig = -1;
          for (const r of vecinos(cur)) {
            if (r === prev) continue;
            if (esNodo(r) || !visto[r]) {
              sig = r;
              break;
            }
          }
          if (sig < 0) break;
          camino.push(sig);
          if (esNodo(sig)) break;
          visto[sig] = 1;
          prev = cur;
          cur = sig;
        }
        const fin = camino[camino.length - 1];
        const pts = camino.map(coord);
        pts[0] = [nodos[grupo[p]].x, nodos[grupo[p]].y];
        let b = -1;
        if (esNodo(fin)) {
          b = grupo[fin];
          pts[pts.length - 1] = [nodos[b].x, nodos[b].y];
        }
        aristas.push({ a: grupo[p], b, pts });
      }
    }

    // lazos cerrados sin nodos (por ejemplo, una o)
    for (const i of pix) {
      if (esNodo(i) || visto[i]) continue;
      const camino = [i];
      visto[i] = 1;
      let prev = -1;
      let cur = i;
      for (;;) {
        let sig = -1;
        for (const r of vecinos(cur))
          if (r !== prev && !visto[r]) {
            sig = r;
            break;
          }
        if (sig < 0) break;
        camino.push(sig);
        visto[sig] = 1;
        prev = cur;
        cur = sig;
      }
      const pts = camino.map(coord);
      if (camino.length > 2) pts.push(pts[0].slice());
      aristas.push({ a: -1, b: -1, pts, cerrada: true });
    }

    const largo = (pts) => {
      let s = 0;
      for (let k = 1; k < pts.length; k++) s += Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]);
      return s;
    };

    const incidencias = () => {
      const g = new Map();
      for (const e of aristas) {
        if (e.a >= 0) g.set(e.a, (g.get(e.a) || 0) + 1);
        if (e.b >= 0) g.set(e.b, (g.get(e.b) || 0) + 1);
      }
      return g;
    };

    // poda de espolones y fusión de nodos de grado 2
    for (let vuelta = 0; vuelta < 50; vuelta++) {
      let g = incidencias();
      const antes = aristas.length;
      if (largoEspolon > 0) {
        // Se poda el ramal más corto de cada nodo de unión, uno por vez, para no borrar dos brazos reales.
        const candidatos = aristas
          .filter((e) => {
            if (e.cerrada) return false;
            const ga = e.a >= 0 ? g.get(e.a) : 0;
            const gb = e.b >= 0 ? g.get(e.b) : 0;
            const extremoA = e.a < 0 || ga === 1;
            const extremoB = e.b < 0 || gb === 1;
            return (extremoA && gb >= 3) || (extremoB && ga >= 3);
          })
          .filter((e) => largo(e.pts) < largoEspolon)
          .sort((x, y) => largo(x.pts) - largo(y.pts));
        const tocados = new Set();
        const quitar = new Set();
        for (const e of candidatos) {
          const union = g.get(e.a) >= 3 ? e.a : e.b;
          if (tocados.has(union)) continue;
          tocados.add(union);
          quitar.add(e);
        }
        aristas = aristas.filter((e) => !quitar.has(e));
      }
      // fusión
      let fusiono = true;
      while (fusiono) {
        fusiono = false;
        g = incidencias();
        for (const [nodo, n] of g) {
          if (n !== 2) continue;
          const inc = aristas.filter((e) => e.a === nodo || e.b === nodo);
          if (inc.length === 1) {
            // un lazo que vuelve al mismo nodo
            inc[0].cerrada = true;
            inc[0].a = inc[0].b = -1;
            fusiono = true;
            break;
          }
          if (inc.length !== 2) continue;
          let [e1, e2] = inc;
          const p1 = e1.b === nodo ? e1.pts : e1.pts.slice().reverse();
          const otro1 = e1.b === nodo ? e1.a : e1.b;
          const p2 = e2.a === nodo ? e2.pts : e2.pts.slice().reverse();
          const otro2 = e2.a === nodo ? e2.b : e2.a;
          const nueva = { a: otro1, b: otro2, pts: p1.concat(p2.slice(1)) };
          aristas = aristas.filter((e) => e !== e1 && e !== e2);
          aristas.push(nueva);
          fusiono = true;
          break;
        }
      }
      if (aristas.length === antes) break;
    }

    const polis = aristas.map((e) => e.pts);
    // nodos aislados (puntos sueltos)
    const g = incidencias();
    for (const nd of nodos) if (!g.has(nd.id) && nd.pixeles > 0) polis.push([[nd.x, nd.y]]);
    return polis;
  }

  /** Marca con 1 los píxeles a distancia ≤ radio de las polilíneas (coordenadas de píxel). */
  function rasterizarGrueso(polis, w, h, radio, destino) {
    const m = destino || new Uint8Array(w * h);
    const r = radio;
    const pintarSegmento = (a, b) => {
      const x0 = Math.max(0, Math.floor(Math.min(a[0], b[0]) - r));
      const x1 = Math.min(w - 1, Math.ceil(Math.max(a[0], b[0]) + r));
      const y0 = Math.max(0, Math.floor(Math.min(a[1], b[1]) - r));
      const y1 = Math.min(h - 1, Math.ceil(Math.max(a[1], b[1]) + r));
      const dx = b[0] - a[0];
      const dy = b[1] - a[1];
      const l2 = dx * dx + dy * dy;
      for (let y = y0; y <= y1; y++)
        for (let x = x0; x <= x1; x++) {
          const px = x + 0.5;
          const py = y + 0.5;
          let t = l2 ? ((px - a[0]) * dx + (py - a[1]) * dy) / l2 : 0;
          t = t < 0 ? 0 : t > 1 ? 1 : t;
          const ex = px - (a[0] + t * dx);
          const ey = py - (a[1] + t * dy);
          if (ex * ex + ey * ey <= r * r) m[y * w + x] = 1;
        }
    };
    for (const poli of polis) {
      if (poli.length === 1) pintarSegmento(poli[0], poli[0]);
      for (let k = 1; k < poli.length; k++) pintarSegmento(poli[k - 1], poli[k]);
    }
    return m;
  }

  /** Muestreo bilineal de una imagen RGBA; fuera de la imagen devuelve blanco. */
  function muestrear(rgba, w, h, u, v, salida, j) {
    const x = u - 0.5;
    const y = v - 0.5;
    const x0 = Math.floor(x);
    const y0 = Math.floor(y);
    if (x0 < 0 || y0 < 0 || x0 + 1 >= w || y0 + 1 >= h) {
      salida[j] = salida[j + 1] = salida[j + 2] = salida[j + 3] = 255;
      return;
    }
    const fx = x - x0;
    const fy = y - y0;
    const i00 = (y0 * w + x0) * 4;
    const i10 = i00 + 4;
    const i01 = i00 + w * 4;
    const i11 = i01 + 4;
    for (let c = 0; c < 3; c++) {
      const a = rgba[i00 + c] * (1 - fx) + rgba[i10 + c] * fx;
      const b = rgba[i01 + c] * (1 - fx) + rgba[i11 + c] * fx;
      salida[j + c] = a * (1 - fy) + b * fy;
    }
    salida[j + 3] = 255;
  }

  /**
   * Rectifica un rectángulo de la página (mm) a una imagen RGBA de pxPorMm.
   * H lleva coordenadas de página (mm) a píxeles de la imagen original.
   */
  function rectificar(rgba, w, h, H, rect, pxPorMm) {
    const ancho = Math.max(1, Math.round(rect.w * pxPorMm));
    const alto = Math.max(1, Math.round(rect.h * pxPorMm));
    const out = new Uint8ClampedArray(ancho * alto * 4);
    const ap = AP.geometria.aplicarH;
    for (let j = 0; j < alto; j++)
      for (let i = 0; i < ancho; i++) {
        const [u, v] = ap(H, rect.x + (i + 0.5) / pxPorMm, rect.y + (j + 0.5) / pxPorMm);
        muestrear(rgba, w, h, u, v, out, (j * ancho + i) * 4);
      }
    return { data: out, w: ancho, h: alto };
  }

  /**
   * Afina la posición de una marca de registro: centroide de los píxeles oscuros cerca del clic.
   * Devuelve null si en la ventana no hay contraste suficiente.
   */
  function refinarMarca(gris, w, h, x, y, radio) {
    let cx = x;
    let cy = y;
    const r = Math.max(3, Math.round(radio));
    for (let it = 0; it < 4; it++) {
      const x0 = Math.max(0, Math.round(cx - r));
      const x1 = Math.min(w - 1, Math.round(cx + r));
      const y0 = Math.max(0, Math.round(cy - r));
      const y1 = Math.min(h - 1, Math.round(cy + r));
      let min = 255;
      let max = 0;
      for (let yy = y0; yy <= y1; yy++)
        for (let xx = x0; xx <= x1; xx++) {
          const g = gris[yy * w + xx];
          if (g < min) min = g;
          if (g > max) max = g;
        }
      if (max - min < 40) return null;
      const umbral = (min + max) / 2;
      let sx = 0;
      let sy = 0;
      let n = 0;
      for (let yy = y0; yy <= y1; yy++)
        for (let xx = x0; xx <= x1; xx++) {
          if ((xx - cx) ** 2 + (yy - cy) ** 2 > r * r) continue;
          if (gris[yy * w + xx] < umbral) {
            sx += xx + 0.5;
            sy += yy + 0.5;
            n++;
          }
        }
      if (!n) return null;
      cx = sx / n;
      cy = sy / n;
    }
    return [cx, cy];
  }

  /**
   * Proceso completo de una celda rectificada: canal → desenfoque → umbral → motas → esqueleto.
   * Las distancias de las opciones van en píxeles de la celda.
   */
  function procesarCelda(rgba, w, h, op) {
    const o = Object.assign({ canal: 'azul', delta: 50, desenfoque: 1, areaMin: 40, largoEspolon: 10, umbral: null }, op || {});
    const gris = desenfocar(canal(rgba, w, h, o.canal), w, h, o.desenfoque);
    const papel = percentil(gris, 0.5);
    const umbral = o.umbral != null ? o.umbral : papel - o.delta;
    const mask = binarizar(gris, umbral);
    const componentes = quitarMotas(mask, w, h, o.areaMin);
    let areaTinta = 0;
    for (let i = 0; i < mask.length; i++) areaTinta += mask[i];
    const esq = limpiarEscalones(adelgazar(mask, w, h), w, h);
    const polis = esqueletoAPolilineas(esq, w, h, o.largoEspolon);
    let largoEsq = 0;
    for (const p of polis) largoEsq += AP.geometria.longitud(p);
    return {
      mask,
      polis,
      componentes: componentes.length,
      areaTinta,
      grosor: largoEsq > 0 ? areaTinta / largoEsq : 0,
      papel,
      umbral,
      tocaBorde: componentes.some((c) => c.x0 === 0 || c.y0 === 0 || c.x1 === w - 1 || c.y1 === h - 1),
    };
  }

  AP.imagen = {
    canal,
    desenfocar,
    percentil,
    binarizar,
    etiquetar,
    quitarMotas,
    adelgazar,
    limpiarEscalones,
    esqueletoAPolilineas,
    rasterizarGrueso,
    rectificar,
    refinarMarca,
    procesarCelda,
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = AP;
})(typeof window !== 'undefined' ? window : globalThis);
