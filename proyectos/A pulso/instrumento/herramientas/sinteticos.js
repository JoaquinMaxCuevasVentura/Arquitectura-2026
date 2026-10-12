/* A pulso · datos sintéticos (solo node)
 * Genera trazas inventadas de letra técnica (I, —, O, R) para probar el instrumento.
 * NO son ensayos: no deben usarse como evidencia.
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

function linea(a, b, n) {
  const out = [];
  for (let i = 0; i <= n; i++) out.push([a[0] + ((b[0] - a[0]) * i) / n, a[1] + ((b[1] - a[1]) * i) / n]);
  return out;
}

function elipse(cx, cy, rx, ry, desde, sentido, n) {
  const out = [];
  for (let i = 0; i <= n; i++) {
    const t = desde + (sentido * 2 * Math.PI * i) / n;
    out.push([cx + rx * Math.cos(t), cy + ry * Math.sin(t)]);
  }
  return out;
}

/**
 * Recorrido idealizado de un gesto: una lista de trazos (mm, y hacia arriba desde la línea base).
 * p: parámetros de la repetición (ver PERFILES).
 */
function recorrido(gesto, h, p, azar) {
  const x0 = p.x0;
  const w = p.ancho * h;
  switch (gesto) {
    case 'G1':
      return [linea([x0, h], [x0, 0], 40)];
    case 'G2':
      return [linea([x0, 0.5 * h], [x0 + 1.2 * h, 0.5 * h], 40)];
    case 'G3': {
      // O: empieza arriba; antihorario salvo que el perfil diga lo contrario
      const sentido = azar() < p.horario ? -1 : 1;
      return [elipse(x0 + w / 2, h / 2, w / 2, h / 2, Math.PI / 2, sentido, 80)];
    }
    case 'G5': {
      // R: asta descendente; después bucle y pierna (en uno o dos trazos)
      const asta = linea([x0, h], [x0, 0], 30);
      const j = (1 - p.bucle) * h; // altura del cierre del bucle
      const r = (h - j) / 2;
      const bucle = linea([x0, h], [x0 + w - r, h], 12).concat(
        elipse(x0 + w - r, j + r, r, r, Math.PI / 2, -1, 24).slice(1, 13),
        linea([x0 + w - r, j], [x0, j], 12).slice(1)
      );
      const pierna = linea([x0 + p.salida * w, j], [x0 + w, 0], 16);
      if (azar() < p.piernaAparte) return [asta, bucle, pierna];
      return [asta, bucle.concat(pierna.slice(1))];
    }
    default:
      throw new Error('Sin modelo sintético para ' + gesto);
  }
}

/** Aplica inclinación y ruido suave; con tiempo, agrega velocidad, presión y pausas entre trazos. */
function deformar(trazos, p, h, azar, conTiempo) {
  const G = AP.geometria;
  const tan = Math.tan((p.inclinacion * Math.PI) / 180);
  const ruido = p.ruido * h;
  const fases = [azar() * 6.28, azar() * 6.28, azar() * 6.28];
  let t = 0;
  return trazos.map((tr, k) => {
    if (k > 0) t += 120 + azar() * 120; // levantamiento
    const base = G.remuestrear(tr, Math.max(0.05, h / 120));
    let s = 0;
    return base.map((q, i) => {
      if (i > 0) s += G.dist(base[i - 1], q);
      const x = q[0] + q[1] * tan + ruido * (Math.sin(s / (0.25 * h) + fases[0]) * 0.6 + Math.sin(s / (0.08 * h) + fases[1]) * 0.4);
      const y = q[1] + ruido * 0.6 * Math.sin(s / (0.17 * h) + fases[2]);
      if (!conTiempo) return [round(x), round(y)];
      if (i > 0) {
        const v = p.velocidad * h * (0.75 + 0.25 * Math.sin(s / (0.2 * h) + fases[1]));
        t += (G.dist(base[i - 1], q) / v) * 1000;
      }
      const presion = Math.min(1, Math.max(0.05, p.presion + 0.08 * Math.sin(s / (0.13 * h) + fases[2])));
      return [round(x), round(y), round(t), round(presion), 0, 0];
    });
  });
}

function round(v) {
  return Math.round(v * 100) / 100;
}

const PERFILES = {
  // Parámetros inventados para que el tablero (BASE) y la pizarra (A2B2) se distingan en las pruebas.
  // ruido en fracciones de h; velocidad en alturas de letra por segundo.
  BASE: { ancho: 0.62, bucle: 0.5, salida: 0.45, inclinacion: 1, ruido: 0.012, jitter: 0.03, velocidad: 2.5, presion: 0.55, horario: 0, piernaAparte: 0 },
  A2B2: { ancho: 0.78, bucle: 0.56, salida: 0.35, inclinacion: 6, ruido: 0.03, jitter: 0.07, velocidad: 4.5, presion: 0.4, horario: 0.3, piernaAparte: 0.4 },
};

function parametros(condicion, azar, x0) {
  const b = PERFILES[condicion] || PERFILES.BASE;
  const j = () => 1 + (azar() * 2 - 1) * b.jitter;
  return {
    x0,
    ancho: b.ancho * j(),
    bucle: b.bucle * j(),
    salida: b.salida * j(),
    inclinacion: b.inclinacion + (azar() * 2 - 1) * 60 * b.jitter,
    ruido: b.ruido,
    velocidad: b.velocidad * j(),
    presion: b.presion * j(),
    horario: b.horario,
    piernaAparte: b.piernaAparte,
  };
}

const AVISO = 'SINTÉTICO: trazas inventadas para probar el instrumento. No son ensayos ni evidencia.';
const GESTOS_PILOTO = ['G1', 'G3', 'G5'];

/** Bloques de tableta con el orden ABBA del piloto: tablero (BASE) y pizarra (A2B2). */
function bloquesPiloto(semilla, alturaX) {
  const h = alturaX || 10;
  const azar = mulberry32(semilla || 7);
  const orden = ['BASE', 'A2B2', 'A2B2', 'BASE'];
  const contador = {};
  return orden.map((cond, k) => {
    const b = AP.nucleo.nuevoBloque({
      persona: 'P00',
      sesion: 'S00',
      condicion: cond,
      alturaX: h,
      herramienta: 'sintético',
      fecha: '2026-10-12',
      orden: k + 1,
      origen: 'sintetico',
      aviso: AVISO,
    });
    for (const gesto of GESTOS_PILOTO) {
      for (let r = 0; r < 5; r++) {
        const clave = cond + gesto;
        contador[clave] = (contador[clave] || 0) + 1;
        const p = parametros(cond, azar, 0.4 * h + azar() * 0.15 * h);
        b.ensayos.push({
          id: AP.nucleo.idEnsayo({ persona: 'P00', sesion: 'S00', condicion: cond, gesto, repeticion: contador[clave] }),
          gesto,
          repeticion: contador[clave],
          calentamiento: false,
          trazos: deformar(recorrido(gesto, h, p, azar), p, h, azar, true).map((puntos) => ({ puntos })),
        });
      }
    }
    return b;
  });
}

/**
 * Hoja escaneada sintética: pauta en cian, marcas negras y trazas de portaminas,
 * vista con perspectiva como una foto de teléfono. Devuelve la imagen y la verdad de terreno.
 */
function hojaFotografiada(opciones) {
  const o = Object.assign({ codigo: 'A4H-h10-L-3x5', semilla: 11, pxPorMm: 12, condicion: 'BASE', ancho: 2600, alto: 1900, radioTrazo: 0.25 }, opciones || {});
  const G = AP.geometria;
  const pauta = AP.nucleo.pautaDesdeCodigo(o.codigo);
  const h = pauta.alturaX;
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
  const pre = AP.nucleo.PRESETS.find((x) => x.codigo === pauta.codigo);
  const gestos = (pre && pre.filas) || GESTOS_PILOTO;
  for (const c of pauta.celdas) {
    const gesto = gestos[(c.fila - 1) % gestos.length];
    const p = parametros(o.condicion, azar, 0.3 * c.w + azar() * 0.1 * c.w);
    const trazos = deformar(recorrido(gesto, h, p, azar), p, h, azar, false);
    verdad.push({ celda: c.indice, gesto, trazos });
    const aPagina = (q) => [c.x + q[0], c.base - q[1]];
    for (const pts of trazos) for (let k = 1; k < pts.length; k++) segmento(aPagina(pts[k - 1]), aPagina(pts[k]), o.radioTrazo, [75, 75, 80]);
  }

  // Foto: las esquinas de la hoja caen en un cuadrilátero de la imagen.
  const m = Math.round(o.ancho * 0.05);
  const esquinasFoto = [
    [m + 20, m],
    [o.ancho - m, m + 40],
    [o.ancho - m - 50, o.alto - m + 10],
    [m - 20, o.alto - m - 30],
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

module.exports = { mulberry32, recorrido, bloquesPiloto, hojaFotografiada, PERFILES, AVISO, GESTOS_PILOTO };
