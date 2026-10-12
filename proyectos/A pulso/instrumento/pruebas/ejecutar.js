/* Pruebas del núcleo del instrumento. Uso: node pruebas/ejecutar.js */
'use strict';
const assert = require('assert');
const AP = require('../lib/nucleo.js');
require('../lib/geometria.js');
require('../lib/imagen.js');
require('../lib/metricas.js');
require('../lib/banco.js');
const S = require('../herramientas/sinteticos.js');

const N = AP.nucleo;
const G = AP.geometria;
const I = AP.imagen;
const M = AP.metricas;

let fallas = 0;
function prueba(nombre, fn) {
  try {
    fn();
    console.log('  ok  ' + nombre);
  } catch (e) {
    fallas++;
    console.log('  FALLA  ' + nombre + '\n        ' + (e.stack || e).toString().split('\n').slice(0, 3).join('\n        '));
  }
}
const cerca = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, (msg || '') + ' ' + a + ' ≉ ' + b + ' (±' + tol + ')');

console.log('Núcleo');
prueba('condiciones', () => {
  assert.strictEqual(N.parsearCondicion('base').codigo, 'BASE');
  assert.strictEqual(N.parsearCondicion('A2·B2').codigo, 'A2B2');
  assert.strictEqual(N.parsearCondicion('b2 a2').codigo, 'A2B2');
  assert.strictEqual(N.parsearCondicion('A0B0').codigo, 'BASE');
  assert.strictEqual(N.parsearCondicion('C3').C, 'C3');
  assert.strictEqual(N.parsearCondicion('B3').codigo, 'B3');
  assert.ok(/tablero de dibujo/.test(N.describirCondicion('BASE')), 'la base es el tablero de dibujo');
  assert.throws(() => N.parsearCondicion('A7'));
  assert.throws(() => N.parsearCondicion('muro'));
});
prueba('identificadores', () => {
  const id = N.idEnsayo({ persona: 0, sesion: 3, condicion: 'B2', gesto: 'g5', repeticion: 7 });
  assert.strictEqual(id, 'AP-P00-S03-B2-G5-R07');
  assert.deepStrictEqual(N.parsearId(id), { persona: 'P00', sesion: 'S03', condicion: 'B2', gesto: 'G5', calentamiento: false, repeticion: 7 });
  assert.strictEqual(N.idEnsayo({ persona: 'P01', sesion: 'S01', condicion: 'BASE', gesto: 'G1', repeticion: 2, calentamiento: true }), 'AP-P01-S01-BASE-G1-K02');
});
prueba('todas las pautas predefinidas son válidas y sus celdas no se tocan', () => {
  for (const pre of N.PRESETS) {
    const p = N.pautaDesdeCodigo(pre.codigo);
    assert.strictEqual(p.codigo.toUpperCase(), pre.codigo.toUpperCase());
    assert.strictEqual(p.celdas.length, p.filas * p.columnas);
    for (const c of p.celdas) {
      assert.ok(c.x >= p.grilla.x - 1e-9 && c.x + c.w <= p.grilla.x + p.grilla.w + 1e-9, pre.codigo + ' ancho');
      assert.ok(c.y >= p.grilla.y - 1e-9 && c.y + c.h <= p.grilla.y + p.grilla.h + 1e-9, pre.codigo + ' alto');
      cerca(c.base - c.alturaX, p.alturaX, 1e-9);
    }
    for (let i = 0; i < p.celdas.length; i++)
      for (let j = i + 1; j < p.celdas.length; j++) {
        const a = p.celdas[i];
        const b = p.celdas[j];
        const separadas = a.x + a.w <= b.x || b.x + b.w <= a.x || a.y + a.h <= b.y || b.y + b.h <= a.y;
        assert.ok(separadas, pre.codigo + ' celdas superpuestas');
      }
  }
  assert.throws(() => N.pautaDesdeCodigo('A4H-h30-L-5x5'));
  assert.throws(() => N.pautaDesdeCodigo('A5H-h30-L-1x1'));
});
prueba('registro CSV', () => {
  const [b] = S.bloquesPiloto(3);
  const filas = N.filasRegistro(b);
  assert.strictEqual(filas.length, 15);
  const csv = N.aCSV(filas);
  const lineas = csv.trim().split('\n');
  assert.strictEqual(lineas[0], N.COLUMNAS_REGISTRO.join(','));
  assert.strictEqual(lineas.length, 16);
  assert.ok(filas[0].duracion_s > 0);
  assert.deepStrictEqual(N.validarBloque(b), []);
  assert.strictEqual(N.nombreArchivoBloque(b), 'AP-P00-S00-O01-BASE.json');
});

console.log('Geometría');
prueba('homografía e inversa', () => {
  const src = [[0, 0], [420, 0], [420, 297], [0, 297]];
  const dst = [[140, 120], [2490, 170], [2430, 1810], [90, 1750]];
  const H = G.homografia(src, dst);
  for (let i = 0; i < 4; i++) {
    const [u, v] = G.aplicarH(H, src[i][0], src[i][1]);
    cerca(u, dst[i][0], 1e-6);
    cerca(v, dst[i][1], 1e-6);
  }
  const inv = G.invertirH(H);
  const [x, y] = G.aplicarH(inv, ...G.aplicarH(H, 123.4, 56.7));
  cerca(x, 123.4, 1e-6);
  cerca(y, 56.7, 1e-6);
});
prueba('eje e simplificación', () => {
  const vertical = [[0, 0], [0, 10], [0, 20]];
  cerca(G.anguloEje(vertical), 0, 1e-9);
  const a = (10 * Math.PI) / 180;
  const inclinada = [0, 5, 10, 15, 20].map((s) => [s * Math.sin(a), s * Math.cos(a)]);
  cerca(G.anguloEje(inclinada), 10, 1e-6);
  const ruidosa = [];
  for (let i = 0; i <= 100; i++) ruidosa.push([i, (i % 2) * 0.01]);
  assert.strictEqual(G.simplificar(ruidosa, 0.05).length, 2);
  const r = G.remuestrear([[0, 0], [10, 0]], 1);
  assert.strictEqual(r.length, 11);
});

console.log('Imagen');
function mascaraDesde(polis, w, h, radio) {
  return I.rasterizarGrueso(polis, w, h, radio);
}
prueba('esqueleto de una recta: una polilínea', () => {
  const w = 120;
  const h = 60;
  const mask = mascaraDesde([[[10, 30], [110, 34]]], w, h, 3);
  const esq = I.limpiarEscalones(I.adelgazar(mask, w, h), w, h);
  const polis = I.esqueletoAPolilineas(esq, w, h, 8);
  assert.strictEqual(polis.length, 1, 'polilíneas: ' + polis.length);
  assert.ok(G.longitud(polis[0]) > 85);
});
prueba('esqueleto de una n: tres ramas desde una unión', () => {
  const w = 200;
  const h = 200;
  const asta = [[50, 30], [50, 170]];
  const arco = [];
  for (let k = 0; k <= 30; k++) {
    const t = (Math.PI * k) / 30;
    arco.push([95 - 45 * Math.cos(t), 100 - 60 * Math.sin(t)]);
  }
  arco.push([140, 170]);
  const mask = mascaraDesde([asta, arco], w, h, 4);
  const esq = I.limpiarEscalones(I.adelgazar(mask, w, h), w, h);
  const polis = I.esqueletoAPolilineas(esq, w, h, 12);
  assert.strictEqual(polis.length, 3, 'ramas: ' + polis.length);
});
prueba('esqueleto de una o: un lazo cerrado', () => {
  const w = 120;
  const h = 120;
  const o = [];
  for (let k = 0; k <= 60; k++) {
    const t = (2 * Math.PI * k) / 60;
    o.push([60 + 35 * Math.cos(t), 60 + 45 * Math.sin(t)]);
  }
  const mask = mascaraDesde([o], w, h, 3);
  const esq = I.limpiarEscalones(I.adelgazar(mask, w, h), w, h);
  const polis = I.esqueletoAPolilineas(esq, w, h, 8);
  assert.strictEqual(polis.length, 1, 'piezas: ' + polis.length);
  const p = polis[0];
  assert.ok(G.dist(p[0], p[p.length - 1]) < 2, 'cerrada');
});

console.log('Digitalización de una foto sintética');
prueba('rectificar, umbral y esqueleto recuperan letras de 10 mm (error < 0,15 mm)', () => {
  const foto = S.hojaFotografiada({ semilla: 5 });
  const gris = I.canal(foto.foto, foto.ancho, foto.alto, 'luminancia');
  // clics imprecisos, afinados sobre las marcas
  const marcas = foto.marcasFoto.map(([x, y], k) => {
    const r = I.refinarMarca(gris, foto.ancho, foto.alto, x + (k % 2 ? 5 : -4), y + (k < 2 ? 4 : -5), 30);
    assert.ok(r, 'marca ' + k + ' no encontrada');
    cerca(r[0], x, 1.5, 'marca x');
    cerca(r[1], y, 1.5, 'marca y');
    return r;
  });
  const H = G.homografia(foto.pauta.marcas, marcas);
  const r = 16;
  let peor = 0;
  for (const c of foto.pauta.celdas) {
    const img = I.rectificar(foto.foto, foto.ancho, foto.alto, H, c, r);
    const res = I.procesarCelda(img.data, img.w, img.h, { largoEspolon: 1.2 * r, areaMin: 0.1 * r * r });
    const base = N.baseEnCelda(c);
    const polis = res.polis.map((poli) => G.simplificar(G.suavizar(poli, 5), 0.8).map(([px, py]) => [px / r, base - py / r]));
    const trazosVerdad = foto.verdad.find((v) => v.celda === c.indice).trazos;
    const verdad = [].concat(...trazosVerdad);
    // de la verdad a lo recuperado
    let s = 0;
    for (const p of verdad) s += G.distPuntoPolilineas(p, polis);
    const media = s / verdad.length;
    // de lo recuperado a la verdad
    let s2 = 0;
    let n2 = 0;
    for (const poli of polis)
      for (const p of G.remuestrear(poli, 0.5)) {
        s2 += G.distPuntoPolilineas(p, trazosVerdad);
        n2++;
      }
    peor = Math.max(peor, media, s2 / n2);
    assert.ok(res.grosor / r > 0.3 && res.grosor / r < 0.9, 'grosor ' + (res.grosor / r).toFixed(2));
  }
  assert.ok(peor < 0.15, 'error medio máximo ' + peor.toFixed(3) + ' mm');
  console.log('        error medio máximo: ' + peor.toFixed(3) + ' mm');
});

console.log('Métricas');
prueba('las dos condiciones sintéticas se distinguen', () => {
  const bloques = S.bloquesPiloto(9);
  const juntar = (cond, gesto) => [].concat(...bloques.filter((b) => b.bloque.condicion === cond).map((b) => b.ensayos.filter((e) => e.gesto === gesto)));
  const base = M.resumenGrupo(juntar('BASE', 'G5'), 10);
  const muro = M.resumenGrupo(juntar('A2B2', 'G5'), 10);
  assert.strictEqual(base.n, 10);
  assert.ok(base.mediano.length >= 1, 'hay mediano');
  assert.ok(muro.resumen.ancho_h.media > base.resumen.ancho_h.media, 'más ancho en el muro');
  assert.ok(muro.resumen.dispersion_mm.media > base.resumen.dispersion_mm.media, 'más disperso en el muro');
  assert.ok(muro.resumen.inclinacion_grados.media > base.resumen.inclinacion_grados.media + 2, 'más inclinado en la pizarra');
  assert.strictEqual(base.resumen.eje_grados, null, 'una R no tiene eje de forma alargada');
  const astas = M.resumenGrupo(juntar('BASE', 'G1'), 10);
  assert.ok(Math.abs(astas.resumen.eje_grados.media - astas.resumen.inclinacion_grados.media) < 1.5, 'en un asta, eje e inclinación coinciden');
  assert.ok(muro.resumen.velocidad_mm_s.media > base.resumen.velocidad_mm_s.media, 'más rápido en el muro');
  assert.strictEqual(base.resumen.levantamientos.media, 1, 'la R del tablero se escribe en dos trazos');
  assert.ok(Math.abs(base.resumen.inclinacion_grados.media - 1) < 2, 'la pierna de la R no arrastra la inclinación: ' + base.resumen.inclinacion_grados.media.toFixed(1));
  assert.ok(Math.abs(muro.resumen.inclinacion_grados.media - 6) < 2.5, 'inclinación en la pizarra: ' + muro.resumen.inclinacion_grados.media.toFixed(1));
  assert.strictEqual(base.corte.cortado, false, 'el mediano de la R no está cortado');
  const estrecho = M.resumenGrupo(juntar('A2B2', 'G5'), 10, { tolerancia: 0.12, pxPorMm: 20 });
  assert.strictEqual(estrecho.corte.cortado, true, 'con una tolerancia mínima el mediano se corta');
  const largoMed = base.mediano.reduce((s, p) => s + G.longitud(p), 0);
  assert.ok(largoMed > 20, 'el mediano recorre la R: ' + largoMed.toFixed(1));
});
prueba('partitura: orden y dirección de los trazos', () => {
  assert.strictEqual(M.direccionTrazo([[0, 10], [0, 0]]), '↓');
  assert.strictEqual(M.direccionTrazo([[0, 5], [10, 5]]), '→');
  assert.strictEqual(M.direccionTrazo([[0, 10], [7, 0]]), '↘');
  const o = [];
  for (let k = 0; k <= 40; k++) o.push([5 * Math.cos(Math.PI / 2 + (2 * Math.PI * k) / 40), 5 * Math.sin(Math.PI / 2 + (2 * Math.PI * k) / 40)]);
  assert.strictEqual(M.direccionTrazo(o), '↺', 'antihorario con y hacia arriba');
  assert.strictEqual(M.direccionTrazo(o.slice().reverse()), '↻');
  const bloques = S.bloquesPiloto(9);
  const juntar = (cond) => [].concat(...bloques.filter((b) => b.bloque.condicion === cond).map((b) => b.ensayos.filter((e) => e.gesto === 'G5')));
  const base = M.resumenGrupo(juntar('BASE'), 10);
  assert.deepStrictEqual(base.partituras, [{ secuencia: '↓ ↘', n: 10 }]);
  assert.strictEqual(base.resumen.consistencia_partitura.media, 100);
  const muro = M.resumenGrupo(juntar('A2B2'), 10);
  assert.ok(muro.resumen.consistencia_partitura.media < 100, 'en la pizarra la partitura varía');
  assert.strictEqual(M.partitura({ trazos: [{ puntos: [[0, 0], [1, 1]] }] }), null, 'sin tiempo no hay partitura');
});
prueba('una repetición vacía no rompe el grupo', () => {
  const [b] = S.bloquesPiloto(4);
  const ens = b.ensayos.filter((e) => e.gesto === 'G1');
  const r = M.resumenGrupo(ens.concat([{ id: 'x', gesto: 'G1', trazos: [] }]), 10);
  assert.strictEqual(r.n, ens.length);
  assert.ok(Number.isFinite(r.resumen.ancho_mm.media));
  assert.strictEqual(M.resumenGrupo([], 30).n, 0);
});
prueba('pausas', () => {
  const p = [];
  let t = 0;
  for (let i = 0; i < 50; i++) p.push([i * 0.5, 0, (t += 10)]);
  for (let i = 0; i < 20; i++) p.push([25, 0, (t += 10)]); // 200 ms quieto
  for (let i = 0; i < 50; i++) p.push([25 + i * 0.5, 0, (t += 10)]);
  assert.strictEqual(M.contarPausas(p), 1);
});

console.log('Banco');
prueba('montaje: criterios de altura y rango de los montantes', () => {
  const r = AP.banco.calcularMontaje({ codoSobreAsiento: 230, hombroDePie: 1350, mesa: 720, asiento: 450 });
  cerca(r.B0.codoObjetivo - r.B0.bordeInferior, 30, 1e-9);
  cerca(r.B0.asientoNecesario + 230, r.B0.codoObjetivo, 1e-9);
  assert.strictEqual(r.B0.angulo, 15);
  cerca(r.B1.codoObjetivo - r.B1.plano, 30, 1e-9);
  cerca(r.B3.codoObjetivo - r.B3.bordeInferior, 20, 1e-9);
  assert.ok(r.B3.centroHoja > r.B0.centroHoja, 'a 45° la hoja queda más alta que a 15°');
  assert.ok(Math.abs(r.B2.error) <= 12.5, 'error B2 ' + r.B2.error);
  assert.strictEqual(r.B2.agujeroTraba, r.B2.agujero + 2);
  const bajo = AP.banco.calcularMontaje({ hombroDePie: 1166 });
  assert.deepStrictEqual(bajo.B2.avisos, []);
  assert.ok(AP.banco.calcularMontaje({ hombroDePie: 1100 }).B2.avisos.length, 'fuera de rango por abajo');
  assert.ok(AP.banco.calcularMontaje({ hombroDePie: 1800 }).B2.avisos.length, 'fuera de rango por arriba');
  assert.ok(AP.banco.calcularMontaje({ hombroDePie: 1766 }).B2.avisos.length === 0, 'límite superior');
  // el listón queda atrapado: dos pasos de 25 = pasador + listón + pasador
  const B = AP.banco.BANCO;
  assert.strictEqual(2 * B.muro.paso, B.muro.pasador[0] + B.liston.ancho);
});

console.log(fallas ? '\n' + fallas + ' prueba(s) fallaron' : '\nTodas las pruebas pasaron');
process.exit(fallas ? 1 : 0);
