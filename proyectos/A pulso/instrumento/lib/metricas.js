/* A pulso · métricas
 * Métricas por ensayo, densidad de repeticiones, trazo mediano y dispersión.
 * Coordenadas de los ensayos: mm, origen en la celda sobre la línea base, y hacia arriba.
 */
(function (raiz) {
  'use strict';
  const AP = (raiz.APulso = raiz.APulso || {});
  const G = () => AP.geometria;
  const I = () => AP.imagen;

  const UMBRAL_PAUSA_MM_S = 5; // por debajo de esta velocidad la herramienta está casi detenida
  const PAUSA_MIN_MS = 100;

  function polilineas(ensayo) {
    return ensayo.trazos.map((t) => t.puntos.map((p) => [p[0], p[1]]));
  }

  function desplazar(polis, dx, dy) {
    return polis.map((poli) => poli.map((p) => [p[0] + dx, p[1] + (dy || 0)]));
  }

  /**
   * Desplazamiento horizontal para comparar repeticiones.
   * 'celda': como se escribió · 'izquierda': borde izquierdo de la caja en 0 · 'centroide': centroide en 0.
   * La vertical se conserva: la línea base es una referencia que la mano intenta respetar.
   */
  function alinear(polis, modo) {
    if (modo === 'celda' || !polis.length) return polis;
    if (modo === 'izquierda') return desplazar(polis, -G().caja(polis).x0, 0);
    const pts = [];
    for (const poli of polis) for (const p of G().remuestrear(poli, 0.5)) pts.push(p);
    const mx = pts.reduce((s, p) => s + p[0], 0) / (pts.length || 1);
    return desplazar(polis, -mx, 0);
  }

  /** Métricas de una repetición. Las de tiempo y presión existen solo para trazas de tableta. */
  function metricasEnsayo(ensayo, alturaX) {
    const polis = polilineas(ensayo);
    const c = G().caja(polis);
    const largo = polis.reduce((s, p) => s + G().longitud(p), 0);
    const puntos = [];
    for (const poli of polis) for (const p of G().remuestrear(poli, 0.5)) puntos.push(p);
    const m = {
      ancho_mm: c.w,
      alto_mm: c.h,
      ancho_h: c.w / alturaX,
      alto_h: c.h / alturaX,
      bajo_base_mm: -c.y0, // cuánto baja por debajo de la línea base
      sobre_altura_x_mm: c.y1 - alturaX, // cuánto sobrepasa la altura x
      recorrido_mm: largo,
      inclinacion_grados: inclinacion(polis, alturaX),
      eje_grados: alargamiento(puntos) >= 1.8 ? G().anguloEje(puntos) : null,
      piezas: polis.length,
    };
    if (ensayo.grosor_mm) m.grosor_mm = ensayo.grosor_mm;
    if (ensayo.componentes != null) m.componentes = ensayo.componentes;

    const conTiempo = ensayo.trazos.every((t) => t.puntos.length && t.puntos[0].length > 2);
    if (conTiempo) {
      m.levantamientos = Math.max(0, ensayo.trazos.length - 1);
      let tMin = Infinity;
      let tMax = -Infinity;
      let enContacto = 0;
      let pausas = 0;
      let presiones = [];
      for (const t of ensayo.trazos) {
        const p = t.puntos;
        tMin = Math.min(tMin, p[0][2]);
        tMax = Math.max(tMax, p[p.length - 1][2]);
        enContacto += p[p.length - 1][2] - p[0][2];
        for (const q of p) if (q.length > 3 && q[3] > 0) presiones.push(q[3]);
        pausas += contarPausas(p);
      }
      m.duracion_s = (tMax - tMin) / 1000;
      m.en_aire_s = Math.max(0, m.duracion_s - enContacto / 1000);
      m.velocidad_mm_s = enContacto > 0 ? largo / (enContacto / 1000) : 0;
      m.pausas = pausas;
      if (presiones.length) {
        const media = presiones.reduce((s, v) => s + v, 0) / presiones.length;
        m.presion_media = media;
        m.presion_de = Math.sqrt(presiones.reduce((s, v) => s + (v - media) ** 2, 0) / presiones.length);
      }
    }
    return m;
  }

  /**
   * Inclinación tipográfica: dirección dominante de los tramos casi verticales (a menos de 30° de la
   * vertical). Se toma el pico del histograma de ángulos ponderado por el largo, y se promedian los
   * tramos a ±5° del pico; así las astas mandan y las diagonales (la pierna de la R, los lados de la A)
   * no arrastran la medida. Positiva si la parte superior va hacia la derecha.
   * Devuelve null si los tramos casi verticales suman menos de 0,3 h.
   */
  function inclinacion(polis, alturaX) {
    const tramos = [];
    let total = 0;
    for (const poli of polis) {
      const r = G().remuestrear(poli, Math.max(0.1, alturaX / 60));
      for (let i = 1; i < r.length; i++) {
        let dx = r[i][0] - r[i - 1][0];
        let dy = r[i][1] - r[i - 1][1];
        const l = Math.hypot(dx, dy);
        if (!l) continue;
        if (dy < 0) {
          dx = -dx;
          dy = -dy;
        }
        const ang = (Math.atan2(dx, dy) * 180) / Math.PI;
        if (Math.abs(ang) > 30) continue;
        tramos.push([ang, l]);
        total += l;
      }
    }
    if (total < 0.3 * alturaX) return null;
    const hist = new Float64Array(61);
    for (const [a, l] of tramos) hist[Math.round(a) + 30] += l;
    let pico = 0;
    let mejor = -1;
    for (let i = 0; i < 61; i++) {
      let v = 0;
      for (let k = -3; k <= 3; k++) if (i + k >= 0 && i + k < 61) v += hist[i + k];
      if (v > mejor) {
        mejor = v;
        pico = i - 30;
      }
    }
    let sa = 0;
    let sl = 0;
    for (const [a, l] of tramos)
      if (Math.abs(a - pico) <= 5) {
        sa += a * l;
        sl += l;
      }
    return sl ? sa / sl : pico;
  }

  /** Razón entre los ejes mayor y menor de la nube de puntos (1 = redonda). */
  function alargamiento(puntos) {
    const n = puntos.length;
    if (n < 3) return 1;
    let mx = 0;
    let my = 0;
    for (const p of puntos) {
      mx += p[0];
      my += p[1];
    }
    mx /= n;
    my /= n;
    let a = 0;
    let b = 0;
    let c = 0;
    for (const p of puntos) {
      a += (p[0] - mx) ** 2;
      b += (p[0] - mx) * (p[1] - my);
      c += (p[1] - my) ** 2;
    }
    const tr = a + c;
    const disc = Math.sqrt(Math.max(0, ((a - c) / 2) ** 2 + b * b));
    const l1 = tr / 2 + disc;
    const l2 = Math.max(1e-9, tr / 2 - disc);
    return Math.sqrt(l1 / l2);
  }

  const FLECHAS = ['→', '↗', '↑', '↖', '←', '↙', '↓', '↘'];

  /**
   * Dirección de un trazo (y hacia arriba): una de ocho flechas según la cuerda del primer al último
   * punto, o un sentido de giro (↺ antihorario, ↻ horario) si el trazo vuelve cerca de donde empezó.
   */
  function direccionTrazo(puntos) {
    const pts = puntos.map((p) => [p[0], p[1]]);
    const largo = G().longitud(pts);
    if (pts.length < 2 || largo < 0.3) return '·';
    const a = pts[0];
    const b = pts[pts.length - 1];
    if (G().dist(a, b) < 0.35 * largo) {
      let area = 0;
      for (let i = 0; i < pts.length; i++) {
        const p = pts[i];
        const q = pts[(i + 1) % pts.length];
        area += p[0] * q[1] - q[0] * p[1];
      }
      return area > 0 ? '↺' : '↻';
    }
    const ang = Math.atan2(b[1] - a[1], b[0] - a[0]);
    const k = ((Math.round(ang / (Math.PI / 4)) % 8) + 8) % 8;
    return FLECHAS[k];
  }

  /**
   * Partitura de una repetición: el orden y la dirección de sus trazos, por ejemplo «↓ ↺».
   * Solo existe con datos de tableta, que conservan el orden de trazado.
   */
  function partitura(ensayo) {
    const conTiempo = ensayo.trazos.length && ensayo.trazos.every((t) => t.puntos.length && t.puntos[0].length > 2);
    if (!conTiempo) return null;
    return ensayo.trazos.map((t) => direccionTrazo(t.puntos)).join(' ');
  }

  /** Cuenta intervalos de al menos PAUSA_MIN_MS en que la velocidad suavizada queda bajo el umbral. */
  function contarPausas(p) {
    if (p.length < 3) return 0;
    const v = [];
    for (let i = 1; i < p.length; i++) {
      const dt = p[i][2] - p[i - 1][2];
      v.push({ t: p[i][2], v: dt > 0 ? Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]) / (dt / 1000) : null });
    }
    // media móvil en una ventana de 30 ms
    const suave = v.map((a, i) => {
      let s = 0;
      let n = 0;
      for (let k = i; k >= 0 && a.t - v[k].t <= 30; k--)
        if (v[k].v != null) {
          s += v[k].v;
          n++;
        }
      return { t: a.t, v: n ? s / n : 0 };
    });
    let pausas = 0;
    let inicio = null;
    for (const s of suave) {
      if (s.v < UMBRAL_PAUSA_MM_S) {
        if (inicio == null) inicio = s.t;
      } else {
        if (inicio != null && s.t - inicio >= PAUSA_MIN_MS) pausas++;
        inicio = null;
      }
    }
    if (inicio != null && suave[suave.length - 1].t - inicio >= PAUSA_MIN_MS) pausas++;
    return pausas;
  }

  /**
   * Densidad: en cada píxel, cuántas repeticiones pasan a una distancia ≤ tolerancia.
   * Devuelve la rejilla y su ubicación en mm (x0 a la izquierda, y1 arriba).
   */
  function densidad(listaPolis, opciones) {
    const o = Object.assign({ pxPorMm: 5, tolerancia: 1.5, margen: 4, caja: null }, opciones || {});
    let c = o.caja || G().caja([].concat(...listaPolis));
    if (!Number.isFinite(c.x0)) c = { x0: 0, y0: 0, x1: 1, y1: 1 };
    const x0 = Math.floor(c.x0 - o.margen - o.tolerancia);
    const y0 = Math.floor(c.y0 - o.margen - o.tolerancia);
    const x1 = Math.ceil(c.x1 + o.margen + o.tolerancia);
    const y1 = Math.ceil(c.y1 + o.margen + o.tolerancia);
    const w = Math.max(1, Math.round((x1 - x0) * o.pxPorMm));
    const h = Math.max(1, Math.round((y1 - y0) * o.pxPorMm));
    const conteo = new Uint16Array(w * h);
    const aPx = (p) => [(p[0] - x0) * o.pxPorMm, (y1 - p[1]) * o.pxPorMm];
    for (const polis of listaPolis) {
      const m = I().rasterizarGrueso(
        polis.map((poli) => poli.map(aPx)),
        w,
        h,
        o.tolerancia * o.pxPorMm
      );
      for (let i = 0; i < m.length; i++) conteo[i] += m[i];
    }
    return { conteo, w, h, x0, y1, pxPorMm: o.pxPorMm, n: listaPolis.length, tolerancia: o.tolerancia };
  }

  /** Región por la que pasa al menos la fracción indicada de las repeticiones. */
  function mascaraMediana(den, fraccion) {
    const f = fraccion == null ? 0.5 : fraccion;
    const minimo = Math.max(1, Math.ceil(den.n * f));
    const suave = I().desenfocar(den.conteo, den.w, den.h, 1);
    const mask = new Uint8Array(den.w * den.h);
    for (let i = 0; i < mask.length; i++) mask[i] = suave[i] >= minimo - 0.25 ? 1 : 0;
    I().quitarMotas(mask, den.w, den.h, Math.max(4, Math.round((den.tolerancia * den.pxPorMm) ** 2)));
    return mask;
  }

  /**
   * Trazo mediano: esqueleto de la región por la que pasa al menos la mitad de las repeticiones.
   * No necesita que las repeticiones tengan el mismo orden ni la misma dirección de trazado.
   */
  function trazoMediano(den, fraccion) {
    const mask = mascaraMediana(den, fraccion);
    const esq = I().limpiarEscalones(I().adelgazar(mask, den.w, den.h), den.w, den.h);
    const polisPx = I().esqueletoAPolilineas(esq, den.w, den.h, 2.5 * den.tolerancia * den.pxPorMm);
    const aMm = (p) => [den.x0 + p[0] / den.pxPorMm, den.y1 - p[1] / den.pxPorMm];
    const polis = polisPx
      .map((poli) => G().simplificar(G().suavizar(poli, 5), 0.3).map(aMm))
      .filter((poli) => poli.length > 1 && G().longitud(poli) > den.tolerancia);
    return polis;
  }

  /**
   * ¿Se cortó el mediano? Compara las piezas de la región mediana con las piezas de una repetición típica
   * (dibujadas con el mismo grosor de tolerancia). Una R tiene una pieza; «PLANTA 1:50», varias.
   */
  function piezasMediano(den, listaPolis) {
    const piezas = I().etiquetar(mascaraMediana(den), den.w, den.h).componentes.length;
    const aPx = (p) => [(p[0] - den.x0) * den.pxPorMm, (den.y1 - p[1]) * den.pxPorMm];
    const porRep = listaPolis
      .map((polis) => {
        const m = I().rasterizarGrueso(polis.map((poli) => poli.map(aPx)), den.w, den.h, den.tolerancia * den.pxPorMm);
        return I().etiquetar(m, den.w, den.h).componentes.length;
      })
      .sort((a, b) => a - b);
    const tipicas = porRep.length ? porRep[Math.floor(porRep.length / 2)] : 0;
    return { piezas, tipicas, cortado: piezas > tipicas };
  }

  /** Distancia media (mm) de una repetición al trazo mediano. */
  function dispersion(polis, mediano) {
    if (!mediano.length) return null;
    let s = 0;
    let n = 0;
    for (const poli of polis)
      for (const p of G().remuestrear(poli, 0.5)) {
        s += G().distPuntoPolilineas(p, mediano);
        n++;
      }
    return n ? s / n : null;
  }

  function mediaDE(valores) {
    const v = valores.filter((x) => x != null && Number.isFinite(x));
    if (!v.length) return null;
    const media = v.reduce((s, x) => s + x, 0) / v.length;
    const de = v.length > 1 ? Math.sqrt(v.reduce((s, x) => s + (x - media) ** 2, 0) / (v.length - 1)) : 0;
    return { media, de, n: v.length };
  }

  /**
   * Resumen de un grupo de repeticiones (una condición y un gesto).
   * opciones: { alineacion, tolerancia, pxPorMm, caja }
   */
  function resumenGrupo(todos, alturaX, opciones) {
    const o = Object.assign({ alineacion: 'centroide', tolerancia: 1.5, pxPorMm: 5 }, opciones || {});
    // una repetición sin puntos no aporta forma: se deja fuera del grupo
    const ensayos = todos.filter((e) => e.trazos && e.trazos.some((t) => t.puntos && t.puntos.length));
    const lista = ensayos.map((e) => alinear(polilineas(e), o.alineacion));
    const den = densidad(lista, { tolerancia: o.tolerancia, pxPorMm: o.pxPorMm, caja: o.caja });
    const mediano = lista.length ? trazoMediano(den) : [];
    const porEnsayo = ensayos.map((e, i) => {
      const m = metricasEnsayo(e, alturaX);
      m.dispersion_mm = dispersion(lista[i], mediano);
      return m;
    });
    // partituras: cuántas repeticiones siguen cada orden de trazos
    const cuenta = new Map();
    for (const e of ensayos) {
      const p = partitura(e);
      if (p != null) cuenta.set(p, (cuenta.get(p) || 0) + 1);
    }
    const partituras = [...cuenta.entries()].map(([secuencia, n]) => ({ secuencia, n })).sort((x, y) => y.n - x.n);
    ensayos.forEach((e, i) => (porEnsayo[i].partitura = partitura(e)));
    const claves = new Set();
    for (const m of porEnsayo) for (const k of Object.keys(m)) claves.add(k);
    const resumen = {};
    for (const k of claves) if (k !== 'partitura') resumen[k] = mediaDE(porEnsayo.map((m) => m[k]));
    const conPartitura = partituras.reduce((t, p) => t + p.n, 0);
    resumen.consistencia_partitura = conPartitura ? { media: (100 * partituras[0].n) / conPartitura, de: 0, n: conPartitura } : null;
    const corte = lista.length ? piezasMediano(den, lista) : { piezas: 0, tipicas: 0, cortado: false };
    return { n: ensayos.length, ensayos, partituras, alineadas: lista, densidad: den, mediano, porEnsayo, resumen, corte };
  }

  /** Nombres legibles de las métricas para tablas y láminas. */
  const ETIQUETAS = {
    ancho_mm: 'Ancho (mm)',
    alto_mm: 'Alto (mm)',
    ancho_h: 'Ancho / h',
    alto_h: 'Alto / h',
    bajo_base_mm: 'Bajo la línea base (mm)',
    sobre_altura_x_mm: 'Sobre la altura h (mm)',
    recorrido_mm: 'Recorrido (mm)',
    inclinacion_grados: 'Inclinación de las astas (°)',
    eje_grados: 'Eje de la forma alargada (°)',
    piezas: 'Piezas del trazo',
    componentes: 'Manchas separadas',
    grosor_mm: 'Grosor estimado (mm)',
    levantamientos: 'Levantamientos',
    duracion_s: 'Duración (s)',
    en_aire_s: 'Tiempo en el aire (s)',
    velocidad_mm_s: 'Velocidad media (mm/s)',
    pausas: 'Pausas (≥100 ms)',
    presion_media: 'Presión media',
    presion_de: 'Variación de presión (DE)',
    dispersion_mm: 'Dispersión respecto del mediano (mm)',
    consistencia_partitura: 'Repeticiones con la partitura más frecuente (%)',
  };

  AP.metricas = {
    polilineas,
    alinear,
    metricasEnsayo,
    inclinacion,
    alargamiento,
    direccionTrazo,
    partitura,
    contarPausas,
    densidad,
    trazoMediano,
    piezasMediano,
    dispersion,
    mediaDE,
    resumenGrupo,
    ETIQUETAS,
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = AP;
})(typeof window !== 'undefined' ? window : globalThis);
