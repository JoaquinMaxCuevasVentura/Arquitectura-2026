/* A pulso · datos sintéticos (solo node)
 * Genera trazas inventadas para probar el instrumento. NO son ensayos: no deben usarse como evidencia.
 */
'use strict';
const AP = require('../lib/nucleo.js');
require('../lib/geometria.js');

function mulberry32(semilla) {
  let a = semilla >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function bezier(p0, p1, p2, p3, n) {
  const out = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    const u = 1 - t;
    out.push([
      u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
      u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1],
    ]);
  }
  return out;
}

function linea(a, b, n) {
  const out = [];
  for (let i = 0; i <= n; i++) out.push([a[0] + ((b[0] - a[0]) * i) / n, a[1] + ((b[1] - a[1]) * i) / n]);
  return out;
}

/** Recorrido idealizado de un gesto (mm, y hacia arriba desde la línea base). */
function recorrido(gesto, h, p) {
  const x0 = p.x0;
  const j = p.union * h;
  const w = p.ancho * h;
  const arco = () =>
    bezier([x0, j], [x0 + 0.1 * w, h * (1 + 0.04 * p.radio)], [x0 + w * (0.55 + 0.25 * p.radio), h * 1.04], [x0 + w, 0.62 * h], 40).concat(
      linea([x0 + w, 0.62 * h], [x0 + w, 0], 20).slice(1)
    );
  switch (gesto) {
    case 'G1':
      return linea([x0, h], [x0, 0], 40);
    case 'G2':
      return arco();
    case 'G5':
      return linea([x0, h], [x0, 0], 30).concat(linea([x0, 0], [x0, j], 15).slice(1), arco().slice(1));
    default:
      throw new Error('Sin modelo sintético para ' + gesto);
  }
}

/** Aplica inclinación, ruido suave y tiempos de tableta. */
function deformar(puntos, p, azar, conTiempo) {
  const G = AP.geometria;
  const base = G.remuestrear(puntos, 0.25);
  const fases = [azar() * 6.28, azar() * 6.28, azar() * 6.28];
  const tan = Math.tan((p.inclinacion * Math.PI) / 180);
  let s = 0;
  let t = 0;
  const out = [];
  for (let i = 0; i < base.length; i++) {
    if (i > 0) s += G.dist(base[i - 1], base[i]);
    const ruido = p.ruido * (Math.sin(s / 7 + fases[0]) * 0.6 + Math.sin(s / 2.3 + fases[1]) * 0.4);
    const ruidoY = p.ruido * 0.6 * Math.sin(s / 5 + fases[2]);
    const x = base[i][0] + base[i][1] * tan + ruido;
    const y = base[i][1] + ruidoY;
    if (!conTiempo) {
      out.push([round(x), round(y)]);
      continue;
    }
    if (i > 0) {
      const v = p.velocidad * (0.75 + 0.25 * Math.sin(s / 6 + fases[1]));
      t += (G.dist(base[i - 1], base[i]) / v) * 1000;
    }
    const presion = Math.min(1, Math.max(0.05, p.presion + 0.08 * Math.sin(s / 4 + fases[2])));
    out.push([round(x), round(y), round(t), round(presion), 0, 0]);
  }
  return out;
}

function round(v) {
  return Math.round(v * 100) / 100;
}

const PERFILES = {
  // Parámetros inventados para que las dos condiciones se distingan en las pruebas.
  BASE: { union: 0.62, ancho: 0.78, radio: 0.2, inclinacion: 2, ruido: 0.25, jitter: 0.03, velocidad: 70, presion: 0.55 },
  A2B2: { union: 0.45, ancho: 0.95, radio: 0.8, inclinacion: 6, ruido: 0.6, jitter: 0.07, velocidad: 120, presion: 0.4 },
};

function parametros(condicion, azar, x0) {
  const b = PERFILES[condicion] || PERFILES.BASE;
  const j = () => 1 + (azar() * 2 - 1) * b.jitter;
  return {
    x0,
    union: b.union * j(),
    ancho: b.ancho * j(),
    radio: b.radio * j(),
    inclinacion: b.inclinacion + (azar() * 2 - 1) * 3 * b.jitter * 20,
    ruido: b.ruido,
    velocidad: b.velocidad * j(),
    presion: b.presion * j(),
  };
}

const AVISO = 'SINTÉTICO: trazas inventadas para probar el instrumento. No son ensayos ni evidencia.';

/** Bloques de tableta con el orden ABBA del piloto. */
function bloquesPiloto(semilla) {
  const azar = mulberry32(semilla || 7);
  const orden = ['BASE', 'A2B2', 'A2B2', 'BASE'];
  const contador = {};
  return orden.map((cond, k) => {
    const b = AP.nucleo.nuevoBloque({
      persona: 'P00',
      sesion: 'S00',
      condicion: cond,
      alturaX: 30,
      herramienta: 'sintético',
      fecha: '2026-10-12',
      orden: k + 1,
      origen: 'sintetico',
      aviso: AVISO,
    });
    for (const gesto of ['G1', 'G2', 'G5']) {
      for (let r = 0; r < 5; r++) {
        const clave = cond + gesto;
        contador[clave] = (contador[clave] || 0) + 1;
        const p = parametros(cond, azar, 12 + azar() * 4);
        b.ensayos.push({
          id: AP.nucleo.idEnsayo({ persona: 'P00', sesion: 'S00', condicion: cond, gesto, repeticion: contador[clave] }),
          gesto,
          repeticion: contador[clave],
          calentamiento: false,
          trazos: [{ puntos: deformar(recorrido(gesto, 30, p), p, azar, true) }],
        });
      }
    }
    return b;
  });
}

/**
 * Hoja escaneada sintética: pauta en cian, marcas negras y trazas de grafito,
 * vista con perspectiva como una foto de teléfono. Devuelve la imagen y la verdad de terreno.
 */
function hojaFotografiada(opciones) {
  const o = Object.assign({ codigo: 'A3H-h30-L-3x5', semilla: 11, pxPorMm: 6, condicion: 'BASE', ancho: 2600, alto: 1900 }, opciones || {});
  const G = AP.geometria;
  const pauta = AP.nucleo.pautaDesdeCodigo(o.codigo);
  const azar = mulberry32(o.semilla);
  const W = Math.round(pauta.W * o.pxPorMm);
  const H = Math.round(pauta.H * o.pxPorMm);
  const hoja = new Uint8ClampedArray(W * H * 4).fill(255);

  const pintar = (xmm, ymm, rmm, color) => {
    const cx = xmm * o.pxPorMm;
    const cy = ymm * o.pxPorMm;
    const r = rmm * o.pxPorMm;
    for (let y = Math.floor(cy - r); y <= Math.ceil(cy + r); y++)
      for (let x = Math.floor(cx - r); x <= Math.ceil(cx + r); x++) {
        if (x < 0 || y < 0 || x >= W || y >= H) continue;
        if ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 > r * r) continue;
        const i = (y * W + x) * 4;
        hoja[i] = Math.min(hoja[i], color[0]);
        hoja[i + 1] = Math.min(hoja[i + 1], color[1]);
        hoja[i + 2] = Math.min(hoja[i + 2], color[2]);
      }
  };
  const segmento = (a, b, rmm, color) => {
    const n = Math.max(1, Math.ceil(G.dist(a, b) * o.pxPorMm * 2));
    for (let k = 0; k <= n; k++) pintar(a[0] + ((b[0] - a[0]) * k) / n, a[1] + ((b[1] - a[1]) * k) / n, rmm, color);
  };

  const CIAN = [110, 200, 240];
  for (const c of pauta.celdas) {
    segmento([c.x, c.base], [c.x + c.w, c.base], 0.15, CIAN);
    segmento([c.x, c.alturaX], [c.x + c.w, c.alturaX], 0.12, CIAN);
    segmento([c.x, c.y], [c.x + 4, c.y], 0.1, CIAN);
    segmento([c.x, c.y], [c.x, c.y + 4], 0.1, CIAN);
  }
  for (const [mx, my] of pauta.marcas) pintar(mx, my, pauta.marcaDiametro / 2, [0, 0, 0]);

  const verdad = [];
  const gestos = ['G1', 'G2', 'G5'];
  for (const c of pauta.celdas) {
    const gesto = gestos[(c.fila - 1) % gestos.length];
    const p = parametros(o.condicion, azar, c.w * 0.3 + azar() * 6);
    const pts = deformar(recorrido(gesto, pauta.alturaX, p), p, azar, false);
    verdad.push({ celda: c.indice, gesto, puntos: pts });
    // coordenadas de la traza (y hacia arriba) → página
    const aPagina = (q) => [c.x + q[0], c.base - q[1]];
    for (let k = 1; k < pts.length; k++) segmento(aPagina(pts[k - 1]), aPagina(pts[k]), 0.35, [75, 75, 80]);
  }

  // Foto: las esquinas de la hoja caen en un cuadrilátero de la imagen.
  const esquinasFoto = [
    [140, 120],
    [o.ancho - 110, 170],
    [o.ancho - 170, o.alto - 90],
    [90, o.alto - 150],
  ];
  const Hpag = G.homografia(
    [
      [0, 0],
      [pauta.W, 0],
      [pauta.W, pauta.H],
      [0, pauta.H],
    ],
    esquinasFoto
  );
  const inv = G.invertirH(Hpag);
  const foto = new Uint8ClampedArray(o.ancho * o.alto * 4);
  for (let y = 0; y < o.alto; y++)
    for (let x = 0; x < o.ancho; x++) {
      const [xm, ym] = G.aplicarH(inv, x + 0.5, y + 0.5);
      const i = (y * o.ancho + x) * 4;
      const sx = Math.floor(xm * o.pxPorMm);
      const sy = Math.floor(ym * o.pxPorMm);
      // iluminación despareja y ruido de cámara
      const luz = 0.86 + 0.12 * (x / o.ancho) - 0.05 * (y / o.alto);
      const ruido = (azar() - 0.5) * 14;
      if (sx < 0 || sy < 0 || sx >= W || sy >= H) {
        foto[i] = 60 + ruido;
        foto[i + 1] = 55 + ruido;
        foto[i + 2] = 50 + ruido;
      } else {
        const j = (sy * W + sx) * 4;
        foto[i] = hoja[j] * luz + ruido;
        foto[i + 1] = hoja[j + 1] * luz + ruido;
        foto[i + 2] = hoja[j + 2] * luz + ruido;
      }
      foto[i + 3] = 255;
    }
  const marcasFoto = pauta.marcas.map(([mx, my]) => G.aplicarH(Hpag, mx, my));
  return { pauta, foto, ancho: o.ancho, alto: o.alto, marcasFoto, verdad, aviso: AVISO };
}

module.exports = { mulberry32, recorrido, bloquesPiloto, hojaFotografiada, PERFILES, AVISO };
