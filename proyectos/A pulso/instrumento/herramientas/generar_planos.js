/* Genera los planos del banco de escritura (SVG, A3 apaisado, unidades en mm de papel).
 * Uso: node herramientas/generar_planos.js   → ../banco/planos/*.svg
 */
'use strict';
const fs = require('fs');
const path = require('path');
const AP = require('../lib/nucleo.js');
require('../lib/banco.js');
require('../lib/dibujo.js');

const B = AP.banco.BANCO;
const SALIDA = path.join(__dirname, '..', '..', 'banco');
const FECHA = '2026-10';
const E = B.espesor;

// ---------- utilidades de dibujo ----------
class Lamina {
  constructor(numero, titulo, escalas) {
    this.W = 420;
    this.H = 297;
    this.numero = numero;
    this.titulo = titulo;
    this.escalas = escalas;
    this.s = [];
  }
  add(t) {
    this.s.push(t);
  }
  /** Devuelve una vista: transforma mm del objeto a mm de papel (y del objeto hacia arriba). */
  vista(ox, oy, escala) {
    const L = this;
    const X = (x) => ox + x * escala;
    const Y = (y) => oy - y * escala;
    const f = (v) => (Math.round(v * 100) / 100).toString();
    return {
      X,
      Y,
      escala,
      rect(x, y, w, h, o) {
        o = o || {};
        L.add('<rect x="' + f(X(x)) + '" y="' + f(Y(y + h)) + '" width="' + f(w * escala) + '" height="' + f(h * escala) + '" fill="' + (o.fill || 'none') + '" stroke="' + (o.stroke || '#111') + '" stroke-width="' + (o.sw || 0.35) + '"' + (o.dash ? ' stroke-dasharray="' + o.dash + '"' : '') + '/>');
      },
      poly(pts, o) {
        o = o || {};
        L.add('<polygon points="' + pts.map(([x, y]) => f(X(x)) + ',' + f(Y(y))).join(' ') + '" fill="' + (o.fill || 'none') + '" stroke="' + (o.stroke || '#111') + '" stroke-width="' + (o.sw || 0.35) + '"' + (o.dash ? ' stroke-dasharray="' + o.dash + '"' : '') + '/>');
      },
      line(x1, y1, x2, y2, o) {
        o = o || {};
        L.add('<line x1="' + f(X(x1)) + '" y1="' + f(Y(y1)) + '" x2="' + f(X(x2)) + '" y2="' + f(Y(y2)) + '" stroke="' + (o.stroke || '#111') + '" stroke-width="' + (o.sw || 0.25) + '"' + (o.dash ? ' stroke-dasharray="' + o.dash + '"' : '') + '/>');
      },
      circle(x, y, r, o) {
        o = o || {};
        L.add('<circle cx="' + f(X(x)) + '" cy="' + f(Y(y)) + '" r="' + f(o.rPapel || r * escala) + '" fill="' + (o.fill || 'none') + '" stroke="' + (o.stroke || '#111') + '" stroke-width="' + (o.sw || 0.25) + '"/>');
      },
      text(x, y, t, o) {
        o = o || {};
        L.add('<text x="' + f(X(x) + (o.dx || 0)) + '" y="' + f(Y(y) + (o.dy || 0)) + '" font-size="' + (o.size || 2.6) + '" text-anchor="' + (o.anchor || 'start') + '"' + (o.weight ? ' font-weight="' + o.weight + '"' : '') + ' fill="' + (o.fill || '#111') + '"' + (o.rot ? ' transform="rotate(' + o.rot + ' ' + f(X(x) + (o.dx || 0)) + ' ' + f(Y(y) + (o.dy || 0)) + ')"' : '') + '>' + t + '</text>');
      },
      /** Cota horizontal entre x1 y x2, con la línea de cota a «d» mm de papel de la altura y. */
      cotaH(x1, x2, y, d, texto) {
        const yp = Y(y) + d;
        const a = X(x1);
        const b = X(x2);
        L.add('<line x1="' + f(a) + '" y1="' + f(Y(y)) + '" x2="' + f(a) + '" y2="' + f(yp + Math.sign(d) * 1.5) + '" stroke="#555" stroke-width="0.15"/>');
        L.add('<line x1="' + f(b) + '" y1="' + f(Y(y)) + '" x2="' + f(b) + '" y2="' + f(yp + Math.sign(d) * 1.5) + '" stroke="#555" stroke-width="0.15"/>');
        L.add('<line x1="' + f(a - 1.5) + '" y1="' + f(yp) + '" x2="' + f(b + 1.5) + '" y2="' + f(yp) + '" stroke="#555" stroke-width="0.18"/>');
        for (const p of [a, b]) L.add('<line x1="' + f(p - 1) + '" y1="' + f(yp + 1) + '" x2="' + f(p + 1) + '" y2="' + f(yp - 1) + '" stroke="#111" stroke-width="0.4"/>');
        L.add('<text x="' + f((a + b) / 2) + '" y="' + f(yp - 0.9) + '" font-size="2.4" text-anchor="middle">' + (texto != null ? texto : Math.round(Math.abs(x2 - x1))) + '</text>');
      },
      /** Cota vertical entre y1 e y2, con la línea de cota a «d» mm de papel de x. */
      cotaV(y1, y2, x, d, texto) {
        const xp = X(x) + d;
        const a = Y(y1);
        const b = Y(y2);
        L.add('<line x1="' + f(X(x)) + '" y1="' + f(a) + '" x2="' + f(xp + Math.sign(d) * 1.5) + '" y2="' + f(a) + '" stroke="#555" stroke-width="0.15"/>');
        L.add('<line x1="' + f(X(x)) + '" y1="' + f(b) + '" x2="' + f(xp + Math.sign(d) * 1.5) + '" y2="' + f(b) + '" stroke="#555" stroke-width="0.15"/>');
        L.add('<line x1="' + f(xp) + '" y1="' + f(a + 1.5) + '" x2="' + f(xp) + '" y2="' + f(b - 1.5) + '" stroke="#555" stroke-width="0.18"/>');
        for (const p of [a, b]) L.add('<line x1="' + f(xp - 1) + '" y1="' + f(p + 1) + '" x2="' + f(xp + 1) + '" y2="' + f(p - 1) + '" stroke="#111" stroke-width="0.4"/>');
        const tx = xp - 1;
        const ty = (a + b) / 2;
        L.add('<text x="' + f(tx) + '" y="' + f(ty) + '" font-size="2.4" text-anchor="middle" transform="rotate(-90 ' + f(tx) + ' ' + f(ty) + ')">' + (texto != null ? texto : Math.round(Math.abs(y2 - y1))) + '</text>');
      },
    };
  }
  tituloVista(x, y, t, escala) {
    this.add('<text x="' + x + '" y="' + y + '" font-size="3.4" font-weight="bold">' + t + '</text>');
    if (escala) this.add('<text x="' + x + '" y="' + (y + 4) + '" font-size="2.4" fill="#555">escala ' + escala + '</text>');
  }
  nota(x, y, lineas, size) {
    lineas.forEach((l, i) => this.add('<text x="' + x + '" y="' + (y + i * (size || 2.6) * 1.45) + '" font-size="' + (size || 2.6) + '">' + l + '</text>'));
  }
  svg() {
    const W = this.W;
    const H = this.H;
    const r = [];
    r.push('<svg xmlns="http://www.w3.org/2000/svg" width="' + W + 'mm" height="' + H + 'mm" viewBox="0 0 ' + W + ' ' + H + '" font-family="Helvetica, Arial, sans-serif">');
    r.push('<rect width="' + W + '" height="' + H + '" fill="#fff"/>');
    r.push('<rect x="10" y="10" width="' + (W - 20) + '" height="' + (H - 20) + '" fill="none" stroke="#111" stroke-width="0.5"/>');
    // rótulo
    const rx = W - 130;
    const ry = H - 32;
    r.push('<rect x="' + rx + '" y="' + ry + '" width="120" height="22" fill="#fff" stroke="#111" stroke-width="0.35"/>');
    r.push('<line x1="' + rx + '" y1="' + (ry + 8) + '" x2="' + (rx + 120) + '" y2="' + (ry + 8) + '" stroke="#111" stroke-width="0.2"/>');
    r.push('<line x1="' + (rx + 95) + '" y1="' + ry + '" x2="' + (rx + 95) + '" y2="' + (ry + 22) + '" stroke="#111" stroke-width="0.2"/>');
    r.push('<text x="' + (rx + 2) + '" y="' + (ry + 5.5) + '" font-size="3.6" font-weight="bold">A PULSO · banco de escritura</text>');
    r.push('<text x="' + (rx + 2) + '" y="' + (ry + 13.5) + '" font-size="3.2">' + this.titulo + '</text>');
    r.push('<text x="' + (rx + 2) + '" y="' + (ry + 19) + '" font-size="2.3" fill="#555">medidas en mm · ' + this.escalas + ' en A3 · ' + FECHA + '</text>');
    r.push('<text x="' + (rx + 107.5) + '" y="' + (ry + 16) + '" font-size="9" font-weight="bold" text-anchor="middle">' + this.numero + '</text>');
    r.push(...this.s);
    r.push('</svg>');
    return r.join('\n');
  }
}

const HUECO = '#e9e4d8'; // relleno del terciado en planta y alzado
const CORTE = '#c9bfa8'; // relleno en sección

// ---------- B-01 · tablero ----------
function laminaTablero() {
  const L = new Lamina('B-01', 'Tablero de escritura', 'esc. 1:5');
  const k = 1 / 5;
  const T = B.tablero;
  const l = B.liston;
  const h = B.hoja;

  // frente
  L.tituloVista(22, 24, 'Frente (cara de escritura)', '1:5');
  const v = L.vista(30, 40 + T.alto * k, k);
  v.rect(0, 0, T.ancho, T.alto, { fill: HUECO, sw: 0.5 });
  const hx = (T.ancho - h.ancho) / 2;
  const hy = T.alto - h.centroDesdeArriba - h.alto / 2;
  v.rect(hx, hy, h.ancho, h.alto, { dash: '1.5 1', stroke: '#1593c7', sw: 0.3 });
  v.text(T.ancho / 2, hy + h.alto / 2, 'hoja A3 apaisada', { anchor: 'middle', fill: '#1593c7', size: 2.6 });
  v.line(T.ancho / 2 - 6, T.alto - h.centroDesdeArriba, T.ancho / 2 + 6, T.alto - h.centroDesdeArriba, { stroke: '#1593c7' });
  v.line(T.ancho / 2, T.alto - h.centroDesdeArriba - 6, T.ancho / 2, T.alto - h.centroDesdeArriba + 6, { stroke: '#1593c7' });
  v.text(T.ancho / 2, hy - 18, 'zona del antebrazo (A0)', { anchor: 'middle', size: 2.4, fill: '#555' });
  v.text(-3, T.alto / 2, 'canto de la regla T', { rot: -90, anchor: 'middle', size: 2.3, fill: '#555' });
  v.cotaH(0, T.ancho, 0, 7);
  v.cotaV(0, T.alto, 0, -7);
  v.cotaV(T.alto - h.centroDesdeArriba, T.alto, T.ancho, 7, h.centroDesdeArriba);
  v.cotaH(0, hx, hy + h.alto, -4, Math.round(hx));
  v.cotaV(hy + h.alto, T.alto, 0, -14, '51,5');

  // dorso
  L.tituloVista(168, 24, 'Dorso (listones)', '1:5');
  const d = L.vista(176, 40 + T.alto * k, k);
  d.rect(0, 0, T.ancho, T.alto, { fill: HUECO, sw: 0.5 });
  const ySup = T.alto - l.margen - l.ancho;
  d.rect(0, ySup, T.ancho, l.ancho, { fill: CORTE });
  d.rect(0, l.margen, T.ancho, l.ancho, { fill: CORTE });
  for (const y0 of [ySup, l.margen])
    for (const xs of [40, 150, 450, 560]) d.circle(xs, y0 + l.ancho / 2, 0, { rPapel: 0.5, fill: '#111' });
  d.text(T.ancho / 2, ySup + l.ancho / 2, 'listón superior 600 × 42 × 18', { anchor: 'middle', dy: 0.9, size: 2.4 });
  d.text(T.ancho / 2, l.margen + l.ancho / 2, 'listón inferior 600 × 42 × 18', { anchor: 'middle', dy: 0.9, size: 2.4 });
  d.cotaV(ySup + l.ancho, T.alto, T.ancho, 7, l.margen);
  d.cotaV(ySup, ySup + l.ancho, T.ancho, 7, l.ancho);
  d.cotaV(0, l.margen, T.ancho, 7, l.margen);
  d.text(T.ancho / 2, T.alto / 2, 'tornillos 4 × 30 desde los listones; cola vinílica', { anchor: 'middle', size: 2.3, fill: '#555' });

  // sección
  L.tituloVista(318, 24, 'Sección A–A', '1:5');
  const s = L.vista(345, 40 + T.alto * k, k);
  s.rect(0, 0, E, T.alto, { fill: CORTE, sw: 0.5 });
  s.rect(E, T.alto - l.margen - l.ancho, E, l.ancho, { fill: CORTE, sw: 0.5 });
  s.rect(E, l.margen, E, l.ancho, { fill: CORTE, sw: 0.5 });
  s.text(-3, T.alto / 2, 'cara de escritura', { rot: -90, anchor: 'middle', size: 2.3 });
  s.cotaH(0, 2 * E, 0, 7, 36);
  s.cotaH(0, E, T.alto, -6, 18);

  L.nota(22, 205, [
    '<tspan font-weight="bold">Material:</tspan> terciado o multilaminado de 18 mm, cara de escritura lisa, lijada (grano 180) y con un sellador mate.',
    'Sin tornillos ni marcas en la cara de escritura. Cantos redondeados (r ≈ 2 mm).',
    'La hoja se fija siempre en el mismo lugar: centro a 200 mm del borde superior y centrada en el ancho.',
    'Marcar sus cuatro esquinas en la cara con lápiz suave o un grabado muy leve.',
    'Los dos listones son los apoyos del tablero en las cuatro posiciones:',
    '· B0, sobre la cuña de 15° (tablero de dibujo) y B3, sobre el atril de 45°: los listones descansan en las cartelas.',
    '· B1, sobre la mesa: el tablero queda plano y elevado 18 mm.',
    '· B2, en el muro (pizarra): el listón superior queda trabado entre dos pares de pasadores.',
    'El canto izquierdo del tablero debe quedar recto y liso: sobre él corre la regla T (condiciones C2 y C3).',
  ]);
  return L;
}

// ---------- B-02 y B-03 · cuña de 15° y atril de 45° ----------
/**
 * Lámina de un apoyo inclinado: dos cartelas triangulares (catetos lh × lv, despuntadas d en el vértice
 * agudo) con el tablero apoyado por sus listones sobre las hipotenusas.
 */
function laminaApoyo(numero, titulo, apoyo, piezas, notas) {
  const L = new Lamina(numero, titulo, 'esc. 1:5');
  const k = 1 / 5;
  const ang = (apoyo.angulo * Math.PI) / 180;
  const lh = apoyo.catetoH || apoyo.cateto;
  const lv = apoyo.catetoV || apoyo.cateto;
  const dp = apoyo.despunte;
  const T = B.tablero;
  const l = B.liston;
  const co = Math.cos(ang);
  const si = Math.sin(ang);
  const y0 = dp * Math.tan(ang);
  const alturaTravesano = Math.min(70, Math.round(lv * 0.45));

  L.tituloVista(22, 24, 'Alzado lateral con el tablero', '1:5');
  const v = L.vista(45, 40 + 135, k);
  v.poly([[dp, 0], [lh, 0], [lh, lv], [dp, y0]], { fill: HUECO, sw: 0.5 });
  // marco de la pendiente: s a lo largo de la hipotenusa desde (dp, y0); n normal hacia arriba
  const P = (s, n) => [dp + s * co - n * si, y0 + s * si + n * co];
  const banda = (s0, s1, n0, n1, o) => v.poly([P(s0, n0), P(s1, n0), P(s1, n1), P(s0, n1)], o);
  banda(0, 30, 0, E, { fill: CORTE, sw: 0.4 }); // tope transversal
  banda(30, 30 + l.ancho, 0, E, { fill: CORTE, sw: 0.4 }); // listón inferior
  banda(30 - l.margen, 30 - l.margen + T.alto, E, 2 * E, { fill: '#cfe8f3', stroke: '#1593c7', sw: 0.5 }); // tablero
  const sSup = 30 - l.margen + T.alto - l.margen - l.ancho;
  banda(sSup, sSup + l.ancho, 0, E, { fill: CORTE, sw: 0.4 }); // listón superior
  v.rect(lh - E, 0, E, alturaTravesano, { fill: CORTE, sw: 0.4 }); // travesaño trasero
  v.line(-20, 0, lh + 40, 0, { sw: 0.6 });
  v.text(lh + 40, 0, 'mesa', { dy: -1, size: 2.4, anchor: 'end' });
  v.cotaH(dp, lh, 0, 8, lh - dp);
  v.cotaH(0, dp, 0, 8, dp);
  v.cotaV(0, lv, lh, 8, lv);
  const [tx, ty] = P(T.alto - 200 + 30 - l.margen, 2 * E);
  v.circle(tx, ty, 0, { rPapel: 0.9, fill: '#1593c7', stroke: '#1593c7' });
  v.text(tx, ty, 'centro de la hoja', { dx: -3, dy: -2, size: 2.4, anchor: 'end', fill: '#1593c7' });
  v.text(dp + 90, 8, apoyo.angulo + '°', { size: 3 });
  const [bx, by] = P(30 - l.margen, 2 * E);
  v.cotaV(0, by, bx, -10, '≈ ' + Math.round(by));

  L.tituloVista(250, 24, 'Frente (sin tablero)', '1:5');
  const f = L.vista(262, 40 + 135, k);
  const ancho = T.ancho;
  f.rect(0, 0, E, lv, { fill: CORTE, sw: 0.5 });
  f.rect(ancho - E, 0, E, lv, { fill: CORTE, sw: 0.5 });
  f.rect(E, 0, ancho - 2 * E, alturaTravesano, { fill: HUECO, sw: 0.35, dash: '1.5 1' });
  f.rect(0, y0, ancho, 30 * si + E * co, { fill: HUECO, sw: 0.4 });
  const topeArriba = y0 + 30 * si + E * co;
  const yTravesano = topeArriba + 6 < alturaTravesano ? (topeArriba + alturaTravesano) / 2 : y0 / 2;
  f.text(ancho / 2, yTravesano, 'travesaño trasero 564 × ' + alturaTravesano + ' (detrás)', { anchor: 'middle', size: 2.3, dy: 0.8 });
  f.text(ancho / 2, y0 + (30 * si + E * co) / 2, 'tope transversal 600 × 30', { anchor: 'middle', size: 2.3, dy: 0.8 });
  f.cotaH(0, ancho, 0, 8);
  f.cotaV(0, lv, ancho, 8, lv);

  L.nota(22, 205, ['<tspan font-weight="bold">Piezas:</tspan> ' + piezas].concat(notas));
  return L;
}

function laminaCuna() {
  const c = B.cuna;
  return laminaApoyo('B-02', 'Cuña de 15° · tablero de dibujo (condición base, B0)', c,
    '2 cartelas (triángulos rectángulos de catetos ' + c.catetoH + ' × ' + c.catetoV + ', despuntados ' + c.despunte + '), 1 travesaño trasero 564 × 70, 1 tope transversal 600 × 30.',
    [
      'Las dos cartelas salen de un rectángulo de ' + c.catetoH + ' × ' + c.catetoV + ' cortado en diagonal: la hipotenusa es la superficie de apoyo y debe quedar recta.',
      'El tablero inclinado a 15° es el puesto clásico del dibujo técnico: es la condición base de toda la serie.',
      'Si las entrevistas muestran que los participantes formados en tablero usaban otro ángulo, se cambia el cateto vertical',
      '(cateto = ' + c.catetoH + ' × tan del ángulo) antes de la serie y se anota en el protocolo.',
      'Verificar el ángulo con un inclinómetro sobre la cara del tablero y anotarlo en la ficha. Fieltro antideslizante bajo las cartelas.',
    ]);
}

function laminaAtril() {
  const a = B.atril;
  return laminaApoyo('B-03', 'Atril de 45° (condición B3, opcional)', a,
    '2 cartelas (triángulos rectángulos de catetos ' + a.cateto + ', despuntados ' + a.despunte + '), 1 travesaño trasero 564 × 70, 1 tope transversal 600 × 30.',
    [
      'Las dos cartelas salen de un cuadrado de ' + a.cateto + ' × ' + a.cateto + ' cortado en diagonal.',
      'Es la condición extrema del plano inclinado: se ensaya solo si la Decisión 2 lo pide.',
      'Verificar 45° ± 1° con un inclinómetro y anotarlo en la ficha.',
    ]);
}

// ---------- B-04 · muro ----------
function laminaMuro() {
  const L = new Lamina('B-04', 'Montantes de muro · pizarra (condición B2)', 'esc. 1:10 y 1:2');
  const k = 1 / 10;
  const mu = B.muro;
  const T = B.tablero;
  const l = B.liston;
  const ejemploHombro = 1350;
  const r = AP.banco.calcularMontaje({ hombroDePie: ejemploHombro });

  L.tituloVista(22, 24, 'Alzado del muro', '1:10');
  const v = L.vista(60, 270, k);
  v.line(-150, 0, 900, 0, { sw: 0.6 });
  v.text(-150, 0, 'piso', { dy: -1, size: 2.4 });
  const x0 = 100;
  const xs = [x0, x0 + mu.separacion];
  for (const xm of xs) {
    v.rect(xm - mu.montanteAncho / 2, mu.bordeInferior, mu.montanteAncho, mu.montanteLargo, { fill: HUECO, sw: 0.45 });
    for (let i = 0; i < mu.agujeros; i++) {
      const y = mu.bordeInferior + mu.primerAgujero + i * mu.paso;
      v.circle(xm, y, 0, { rPapel: 0.35, fill: '#111' });
      if (xm === xs[0] && (i === 0 || (i + 1) % 5 === 0)) v.text(xm - mu.montanteAncho / 2, y, String(i + 1), { dx: -1.5, dy: 0.8, size: 2, anchor: 'end' });
    }
  }
  // tablero colgado (ejemplo)
  const top = r.B2.pasador + mu.pasador[0] / 2 + l.ancho + l.margen;
  const xt = x0 + mu.separacion / 2 - T.ancho / 2;
  v.rect(xt, top - T.alto, T.ancho, T.alto, { stroke: '#1593c7', dash: '2 1.2', sw: 0.4 });
  for (const xm of xs) {
    v.circle(xm, r.B2.pasador, 0, { rPapel: 0.9, fill: '#c8433a', stroke: '#c8433a' });
    v.circle(xm, r.B2.pasador + 2 * mu.paso, 0, { rPapel: 0.9, fill: '#c8433a', stroke: '#c8433a' });
  }
  v.line(xt - 40, ejemploHombro, xt + T.ancho + 40, ejemploHombro, { stroke: '#c8433a', dash: '2 1', sw: 0.25 });
  v.text(xt + T.ancho + 42, ejemploHombro, 'hombro ' + ejemploHombro + ' (ejemplo)', { dy: 0.8, size: 2.3, fill: '#c8433a' });
  v.text(xt + T.ancho + 42, r.B2.pasador, 'pasadores en los agujeros ' + r.B2.agujero + ' y ' + r.B2.agujeroTraba, { dy: 0.8, size: 2.3, fill: '#c8433a' });
  v.cotaV(0, mu.bordeInferior, xs[1] + mu.montanteAncho / 2, 10);
  v.cotaV(mu.bordeInferior, mu.bordeInferior + mu.montanteLargo, xs[1] + mu.montanteAncho / 2, 10);
  v.cotaH(xs[0], xs[1], mu.bordeInferior + mu.montanteLargo, -6, mu.separacion);
  v.cotaV(mu.bordeInferior, mu.bordeInferior + mu.primerAgujero, xs[0] - mu.montanteAncho / 2, -12, mu.primerAgujero);

  L.tituloVista(225, 24, 'Detalle: pasador y listón superior', '1:2');
  const dk = 1 / 2;
  const d = L.vista(255, 140, dk);
  // muro a la izquierda (x negativo), montante 18, pasador, listón y tablero
  d.rect(-30, -60, 30, 160, { fill: '#ddd', sw: 0.4 });
  d.text(-15, 105, 'muro', { anchor: 'middle', size: 2.4 });
  d.rect(0, -60, E, 160, { fill: CORTE, sw: 0.5 });
  d.text(E / 2, -66, 'montante', { anchor: 'middle', size: 2.3 });
  d.rect(E - 15, -4, 15 + 17, 8, { fill: '#888', sw: 0.3 });
  d.text(E + 17, -4, 'pasador Ø8 × 32', { dx: 22, dy: 6, size: 2.3 });
  d.line(E + 8, 0, E + 17 + 40, -16, { sw: 0.15 });
  d.rect(E, 4, E, l.ancho, { fill: CORTE, sw: 0.5 });
  d.text(E * 1.5, 4 + l.ancho / 2, 'listón', { anchor: 'middle', size: 2.2, rot: -90 });
  d.rect(E - 15, 46, 15 + 17, 8, { fill: '#888', sw: 0.3 });
  d.text(E + 17, 54, 'pasador de traba (2 agujeros más arriba)', { dx: 22, dy: -6, size: 2.3 });
  d.line(E + 8, 50, E + 17 + 40, 66, { sw: 0.15 });
  d.cotaV(0, 50, -30, -6, 50);
  d.rect(2 * E, -60 + 10, E, 150, { fill: '#cfe8f3', stroke: '#1593c7', sw: 0.5 });
  d.text(2.5 * E + 8, 30, 'tablero', { size: 2.3, rot: -90, anchor: 'middle' });
  d.cotaH(E - 15, E, -4, 8, 15);
  d.cotaH(E, E + 17, -4, 8, 17);

  L.nota(225, 200, [
    '<tspan font-weight="bold">Montantes:</tspan> 2 piezas de 90 × 750 × 18, a plomo, con 420 mm entre ejes',
    'y el borde inferior a 1250 mm del piso. Fijación: 3 tornillos 5 × 60 con tarugos Ø8 por montante.',
    'Agujeros Ø8,5 de 15 mm de profundidad cada 25 mm sobre el eje: 27 agujeros, del 1 (abajo) al 27.',
    'Numerar con lápiz cada 5 agujeros. Pasadores: varilla lisa de acero Ø8 × 32 (15 mm dentro, 17 mm fuera),',
    'así no tocan el dorso del tablero. El listón superior (42 mm) se apoya en dos pasadores y queda atrapado por otros dos',
    'puestos dos agujeros más arriba: el tablero no se levanta con los trazos ascendentes. El listón inferior toca los montantes.',
    'Elegir el agujero con la calculadora del banco: el centro de la hoja queda a la altura del hombro (±12 mm).',
    'Si no se puede perforar el muro: atornillar los montantes a un tablero de 600 × 1200 apoyado en el muro',
    'y trabado al piso con un listón.',
  ]);
  return L;
}

// ---------- B-05 · despiece ----------
function laminaDespiece() {
  const L = new Lamina('B-05', 'Despiece en medio tablero de 1220 × 1220 × 18', 'esc. 1:10');
  const k = 1 / 10;
  const v = L.vista(30, 30 + 122, k);
  v.rect(0, 0, 1220, 1220, { fill: '#f7f4ec', sw: 0.5 });
  // y hacia arriba en la vista: colocamos piezas desde arriba (1220 - y)
  const pieza = (x, y, w, h, nombre, o) => {
    v.rect(x, 1220 - y - h, w, h, Object.assign({ fill: HUECO, sw: 0.4 }, o || {}));
    v.text(x + w / 2, 1220 - y - h / 2, nombre, { anchor: 'middle', dy: 0.8, size: 2.1 });
  };
  pieza(0, 0, 600, 600, '1 · tablero 600 × 600');
  v.poly([[604, 1220], [1064, 1220], [1064, 760]], { fill: HUECO, sw: 0.4 });
  v.poly([[604, 1220], [604, 760], [1064, 760]], { fill: HUECO, sw: 0.4 });
  v.text(940, 1110, '3a', { size: 2.3 });
  v.text(700, 840, '3b', { size: 2.3 });
  v.text(834, 1235, '3 · cartelas del atril: cuadrado 460 × 460 en diagonal', { anchor: 'middle', size: 2.1, dy: -1 });
  // cuña de 15°: rectángulo 600 × 161 cortado en diagonal
  v.poly([[0, 1220 - 878], [600, 1220 - 878], [600, 1220 - 878 - 161]], { fill: HUECO, sw: 0.4 });
  v.poly([[0, 1220 - 878], [0, 1220 - 878 - 161], [600, 1220 - 878 - 161]], { fill: HUECO, sw: 0.4 });
  v.text(300, 1220 - 878 - 80, '7 · cartelas de la cuña: 600 × 161 en diagonal', { anchor: 'middle', size: 2.1, dy: 0.8 });
  pieza(0, 1043, 564, 70, '8 · travesaño de la cuña 564 × 70');
  pieza(0, 1117, 600, 30, '9 · tope de la cuña 600 × 30');
  pieza(0, 604, 600, 42, '2 · listón 600 × 42');
  pieza(0, 650, 600, 42, '2 · listón 600 × 42');
  pieza(0, 696, 600, 30, '5 · tope 600 × 30');
  pieza(0, 730, 564, 70, '4 · travesaño 564 × 70');
  pieza(0, 804, 564, 70, '4 · travesaño 564 × 70');
  for (const xm of [604, 698]) {
    v.rect(xm, 1220 - 464 - 750, 90, 750, { fill: HUECO, sw: 0.4 });
    v.text(xm + 45, 1220 - 464 - 375, '6 · montante 90 × 750', { anchor: 'middle', size: 2.1, rot: -90, dx: 0.8 });
  }
  v.cotaH(0, 1220, 0, 8);
  v.cotaV(0, 1220, 1220, 8);

  L.tituloVista(185, 24, 'Lista de piezas', null);
  const filas = [
    ['N.º', 'Pieza', 'Cant.', 'Medidas (mm)', 'Uso'],
    ['1', 'Tablero de escritura', '1', '600 × 600 × 18', 'todas'],
    ['2', 'Listón del tablero', '2', '600 × 42 × 18', 'apoyo en todas'],
    ['3', 'Cartela del atril', '2', 'triángulo 460 × 460, despunte 30', 'B3'],
    ['4', 'Travesaño del atril', '2', '564 × 70 × 18', 'B3'],
    ['5', 'Tope del atril', '1', '600 × 30 × 18', 'B3'],
    ['6', 'Montante de muro', '2', '90 × 750 × 18', 'B2'],
    ['7', 'Cartela de la cuña', '2', 'triángulo 600 × 161, despunte 20', 'B0'],
    ['8', 'Travesaño de la cuña', '1', '564 × 70 × 18', 'B0'],
    ['9', 'Tope de la cuña', '1', '600 × 30 × 18', 'B0'],
  ];
  let y = 36;
  const cols = [185, 196, 240, 254, 300];
  filas.forEach((f, i) => {
    f.forEach((t, j) => L.add('<text x="' + cols[j] + '" y="' + y + '" font-size="2.6"' + (i === 0 ? ' font-weight="bold"' : '') + '>' + t + '</text>'));
    L.add('<line x1="185" y1="' + (y + 1.6) + '" x2="400" y2="' + (y + 1.6) + '" stroke="#999" stroke-width="0.15"/>');
    y += 6;
  });
  L.tituloVista(185, y + 6, 'Herrajes y materiales', null);
  L.nota(185, y + 13, [
    '· Medio tablero de terciado o multilaminado de 18 mm (1220 × 1220), una cara lisa.',
    '· 4 pasadores: varilla lisa de acero Ø8 × 32 (dos de apoyo y dos de traba).',
    '· 6 tarugos Ø8 y 6 tornillos 5 × 60 (montantes al muro).',
    '· 30 tornillos para madera 4 × 30 y cola vinílica.',
    '· Instrumentos de dibujo (C2, C3): regla T de 60 cm, escuadras de 45° y de 30/60°,',
    '  plantilla de rotulación ISO 3098 de 10 mm y estilógrafo de 1,0 (tipo B: trazo = h/10).',
    '· Herramientas (D): portaminas 0,5 HB (base), estilógrafo 0,35 o 0,5, papel vegetal A4.',
    '· Cinta de papel, fieltro antideslizante, inclinómetro (aplicación del teléfono).',
    '',
    'Ancho de corte supuesto: 4 mm. Verificar las medidas reales del tablero',
    'antes de cortar; listones, travesaños y topes pueden salir de recortes.',
  ]);
  return L;
}

// ---------- B-06 · cuatro posiciones ----------
function laminaPosiciones() {
  const L = new Lamina('B-06', 'Las cuatro posiciones del plano (B0–B3)', 'esc. 1:25');
  const k = 1 / 25;
  const m = { codoSobreAsiento: 230, hombroDePie: 1350, mesa: 720, asiento: 450 };
  const r = AP.banco.calcularMontaje(m);
  const piso = 250;
  const marcos = [
    ['B0 · tablero a 15° (base)', 22],
    ['B1 · mesa horizontal', 120],
    ['B2 · pizarra, de pie', 218],
    ['B3 · atril a 45°', 316],
  ];
  marcos.forEach(([t, x]) => L.tituloVista(x, 30, t, '1:25'));
  const mesaYasiento = (v, asiento) => {
    v.line(-100, 0, 2100, 0, { sw: 0.5 });
    v.rect(900, m.mesa - 30, 800, 30, { fill: '#e8e3d7' });
    v.rect(950, 0, 30, m.mesa - 30, { fill: '#e8e3d7' });
    v.rect(1620, 0, 30, m.mesa - 30, { fill: '#e8e3d7' });
    v.rect(300, asiento - 30, 400, 30, { fill: '#e8e3d7' });
    v.line(500, 0, 500, asiento - 30, { sw: 0.5 });
    v.cotaV(0, asiento, 300, -4, Math.round(asiento));
  };
  const lineaCota = (v, h, texto, color) => {
    v.line(0, h, 1900, h, { stroke: color, dash: '1.2 0.8' });
    v.text(0, h, texto + ' ' + Math.round(h), { dy: -0.8, size: 2.1, fill: color });
  };
  const inclinado = (v, apoyo, rb) => {
    const a = (apoyo.angulo * Math.PI) / 180;
    const lh = apoyo.catetoH || apoyo.cateto;
    const lv = apoyo.catetoV || apoyo.cateto;
    const xa = 1000;
    v.poly([[xa + 20, m.mesa], [xa + lh, m.mesa], [xa + lh, m.mesa + lv]], { fill: '#e8e3d7' });
    const b = [xa, rb.bordeInferior];
    const t = [xa + 600 * Math.cos(a), rb.bordeInferior + 600 * Math.sin(a)];
    const n = [-36 * Math.sin(a), 36 * Math.cos(a)];
    v.poly([b, t, [t[0] + n[0], t[1] + n[1]], [b[0] + n[0], b[1] + n[1]]], { fill: '#cfe8f3', stroke: '#1593c7' });
    lineaCota(v, rb.codoObjetivo, 'codo', '#c8433a');
    lineaCota(v, rb.centroHoja, 'centro de la hoja', '#1593c7');
  };
  // B0
  let v = L.vista(22, piso, k);
  mesaYasiento(v, r.B0.asientoNecesario);
  inclinado(v, B.cuna, r.B0);
  // B1
  v = L.vista(120, piso, k);
  mesaYasiento(v, r.B1.asientoNecesario);
  v.rect(1000, m.mesa, 600, 2 * E, { fill: '#cfe8f3', stroke: '#1593c7' });
  lineaCota(v, r.B1.codoObjetivo, 'codo', '#c8433a');
  // B2
  v = L.vista(218, piso, k);
  v.line(-100, 0, 1900, 0, { sw: 0.5 });
  v.rect(1400, 0, 60, 2100, { fill: '#ddd', sw: 0.3 });
  const mu = B.muro;
  v.rect(1400 - E, mu.bordeInferior, E, mu.montanteLargo, { fill: '#e8e3d7' });
  const top = r.B2.pasador + mu.pasador[0] / 2 + B.liston.ancho + B.liston.margen;
  v.rect(1400 - 3 * E, top - 600, 2 * E, 600, { fill: '#cfe8f3', stroke: '#1593c7' });
  lineaCota(v, m.hombroDePie, 'hombro', '#c8433a');
  v.cotaV(0, r.B2.pasador, 1400, 4, Math.round(r.B2.pasador));
  // B3
  v = L.vista(316, piso, k);
  mesaYasiento(v, r.B3.asientoNecesario);
  inclinado(v, B.atril, r.B3);

  L.nota(22, 262, [
    'Ejemplo con codo sobre el asiento 230, hombro de pie 1350 y mesa 720. Para cada persona, usar la calculadora del banco (instrumento/banco.html).',
    'Criterios del proyecto: B0, codo 30 mm sobre el borde inferior del tablero a 15°; B1, codo 30 mm sobre la mesa; B2, centro de la hoja a la altura del hombro;',
    'B3, codo 20 mm sobre el borde inferior del tablero a 45°.',
  ]);
  return L;
}

function main() {
  fs.mkdirSync(path.join(SALIDA, 'planos'), { recursive: true });
  for (const f of fs.readdirSync(path.join(SALIDA, 'planos'))) if (f.endsWith('.svg')) fs.unlinkSync(path.join(SALIDA, 'planos', f));
  const laminas = [
    ['B-01_tablero.svg', laminaTablero()],
    ['B-02_cuna_15.svg', laminaCuna()],
    ['B-03_atril_45.svg', laminaAtril()],
    ['B-04_muro.svg', laminaMuro()],
    ['B-05_despiece.svg', laminaDespiece()],
    ['B-06_posiciones.svg', laminaPosiciones()],
  ];
  for (const [nombre, L] of laminas) {
    fs.writeFileSync(path.join(SALIDA, 'planos', nombre), L.svg());
    console.log('plano', nombre);
  }
}

main();
