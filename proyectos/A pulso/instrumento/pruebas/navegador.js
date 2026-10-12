/* Pruebas de las páginas en un navegador real (Chromium con Playwright).
 * Uso: node pruebas/navegador.js [--capturas carpeta]
 */
'use strict';
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { pathToFileURL } = require('url');

function cargarPlaywright() {
  for (const ruta of ['playwright', '/opt/node22/lib/node_modules/playwright']) {
    try {
      return require(ruta);
    } catch (e) {
      /* siguiente */
    }
  }
  throw new Error('No encontré Playwright.');
}

const RAIZ = path.join(__dirname, '..');
const EJEMPLOS = path.join(RAIZ, 'datos_ejemplo');
const iCap = process.argv.indexOf('--capturas');
const CAPTURAS = iCap > 0 ? process.argv[iCap + 1] : null;
const url = (archivo) => pathToFileURL(path.join(RAIZ, archivo)).href;

let fallas = 0;
async function prueba(nombre, fn) {
  try {
    await fn();
    console.log('  ok  ' + nombre);
  } catch (e) {
    fallas++;
    console.log('  FALLA  ' + nombre + '\n        ' + String(e.stack || e).split('\n').slice(0, 4).join('\n        '));
  }
}

async function nuevaPagina(navegador, ancho, alto) {
  const ctx = await navegador.newContext({ viewport: { width: ancho || 1400, height: alto || 1000 }, acceptDownloads: true });
  const pagina = await ctx.newPage();
  const errores = [];
  pagina.on('pageerror', (e) => errores.push(e.message));
  pagina.on('console', (m) => m.type() === 'error' && errores.push(m.text()));
  pagina.errores = errores;
  return pagina;
}

async function descargaJSON(pagina, accion) {
  const [d] = await Promise.all([pagina.waitForEvent('download'), accion()]);
  const ruta = await d.path();
  return { nombre: d.suggestedFilename(), datos: JSON.parse(fs.readFileSync(ruta, 'utf8')) };
}

(async () => {
  const { chromium } = cargarPlaywright();
  const navegador = await chromium.launch();
  if (CAPTURAS) fs.mkdirSync(CAPTURAS, { recursive: true });
  const captura = async (pagina, nombre, opciones) => CAPTURAS && pagina.screenshot(Object.assign({ path: path.join(CAPTURAS, nombre + '.png'), fullPage: true }, opciones || {}));

  await prueba('inicio y pautas se dibujan sin errores', async () => {
    const p = await nuevaPagina(navegador);
    await p.goto(url('index.html'));
    await p.goto(url('pautas.html'));
    await p.waitForSelector('#vista svg');
    const celdas = await p.$$eval('#vista svg circle', (c) => c.length);
    assert.strictEqual(celdas, 4, 'cuatro marcas');
    await p.selectOption('#preset', 'A4H-h10-L-5x2');
    const filas = await p.$$eval('#filas select', (s) => s.length);
    assert.strictEqual(filas, 5);
    const conGuias = await p.$$eval('#vista svg line[stroke-dasharray]', (l) => l.length);
    await p.check('#sin-guias');
    const sinGuias = await p.$$eval('#vista svg line[stroke-dasharray]', (l) => l.length);
    assert.ok(conGuias >= 10 && sinGuias === 0, 'la pauta sin guías no dibuja la línea de altura: ' + conGuias + ' / ' + sinGuias);
    await p.uncheck('#sin-guias');
    await p.fill('#codigo', 'A4H-h30-L-9x9');
    const err = await p.textContent('#estado');
    assert.ok(/Demasiadas/.test(err), 'muestra el error: ' + err);
    await p.selectOption('#preset', 'A4H-h10-L-3x5');
    await captura(p, 'pautas');
    assert.deepStrictEqual(p.errores, []);
    await p.context().close();
  });

  await prueba('captura: secuencia con calentamiento, trazos con ratón y descarga del bloque', async () => {
    const p = await nuevaPagina(navegador, 1200, 900);
    await p.goto(url('captura.html'));
    await p.fill('#plan', 'G1:2, G5:2');
    await p.fill('#calentamiento', '1');
    await p.fill('#condicion', 'a2 b2');
    await p.click('#empezar');
    await p.waitForSelector('#lienzo');
    const caja = await p.$eval('#lienzo', (c) => { const r = c.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; });
    const cx = caja.x + caja.w / 2;
    const cy = caja.y + caja.h / 2;
    for (let paso = 0; paso < 6; paso++) {
      await p.mouse.move(cx - 30, cy - 50);
      await p.mouse.down();
      for (let k = 1; k <= 20; k++) await p.mouse.move(cx - 30 + k, cy - 50 + k * 5);
      await p.mouse.up();
      await p.click('#siguiente');
    }
    const ind = await p.textContent('#indicacion');
    assert.ok(/completo/.test(ind), ind);
    p.on('dialog', (d) => d.accept());
    const { nombre, datos } = await descargaJSON(p, () => p.click('#terminar'));
    assert.strictEqual(nombre, 'AP-P00-S01-O01-A2B2.json');
    assert.strictEqual(datos.ensayos.length, 6);
    assert.deepStrictEqual(datos.ensayos.map((e) => e.id), [
      'AP-P00-S01-A2B2-G1-K01', 'AP-P00-S01-A2B2-G5-K01', 'AP-P00-S01-A2B2-G1-R01', 'AP-P00-S01-A2B2-G1-R02', 'AP-P00-S01-A2B2-G5-R01', 'AP-P00-S01-A2B2-G5-R02',
    ]);
    const pts = datos.ensayos[2].trazos[0].puntos;
    assert.ok(pts.length >= 10, 'puntos: ' + pts.length);
    assert.strictEqual(pts[0].length, 6);
    assert.ok(pts[pts.length - 1][2] > pts[0][2], 'el tiempo avanza');
    assert.deepStrictEqual(p.errores, []);
    await p.context().close();
  });

  await prueba('digitalizar: foto sintética → 15 repeticiones con identificador', async () => {
    const datosMarcas = JSON.parse(fs.readFileSync(path.join(EJEMPLOS, 'SINTETICO_marcas.json'), 'utf8'));
    const marcas = datosMarcas.marcas_px;
    const nombreFoto = 'SINTETICO_hoja_A4H-h10-L-3x5_A2B2.jpg';
    const p = await nuevaPagina(navegador, 1500, 1100);
    await p.goto(url('digitalizar.html'));
    await p.setInputFiles('#archivo', path.join(EJEMPLOS, nombreFoto));
    await p.waitForFunction(() => /marca 1/.test(document.querySelector('#estado').textContent));
    const info = await p.$eval('#imagen', (c) => { const r = c.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height, cw: c.width }; });
    const escala = info.w / datosMarcas.tamano_px[nombreFoto][0];
    for (const [mx, my] of marcas[nombreFoto]) {
      await p.mouse.click(info.x + (mx + 3) * escala, info.y + (my - 2) * escala);
    }
    await p.waitForFunction(() => /Registro listo/.test(document.querySelector('#estado').textContent));
    await p.fill('#condicion', 'A2B2');
    await p.click('#procesar');
    await p.waitForSelector('#celdas .celda');
    const n = await p.$$eval('#celdas .celda:not(.vacia)', (c) => c.length);
    assert.strictEqual(n, 15, 'celdas con tinta: ' + n);
    await captura(p, 'digitalizar');
    const { nombre, datos } = await descargaJSON(p, () => p.click('#descargar'));
    assert.strictEqual(nombre, 'AP-P00-S01-O01-A2B2.json');
    assert.strictEqual(datos.origen, 'escaneo');
    assert.strictEqual(datos.ensayos.length, 15);
    assert.strictEqual(datos.ensayos[0].id, 'AP-P00-S01-A2B2-G1-R01');
    assert.strictEqual(datos.ensayos[14].id, 'AP-P00-S01-A2B2-G5-R05');
    assert.strictEqual(datos.ensayos[5].gesto, 'G3', 'la segunda fila del piloto es la O');
    assert.ok(datos.ensayos.every((e) => e.tinta && e.tinta.startsWith('data:image/png')));
    const g5 = datos.ensayos[14];
    const ys = [].concat(...g5.trazos.map((t) => t.puntos.map((q) => q[1])));
    assert.ok(Math.min(...ys) > -1 && Math.min(...ys) < 1, 'la R se apoya en la línea base: ' + Math.min(...ys));
    assert.ok(Math.max(...ys) > 9 && Math.max(...ys) < 11.5, 'y llega a la altura de la letra: ' + Math.max(...ys));
    fs.writeFileSync(path.join(require('os').tmpdir(), 'apulso_digitalizado.json'), JSON.stringify(datos));
    assert.deepStrictEqual(p.errores, []);
    await p.context().close();
  });

  await prueba('superponer: paneles, métricas, medida, lámina y exportaciones', async () => {
    const p = await nuevaPagina(navegador, 1500, 1100);
    await p.goto(url('superponer.html'));
    const archivos = fs.readdirSync(EJEMPLOS).filter((f) => /^SINTETICO_AP-.*\.json$/.test(f)).map((f) => path.join(EJEMPLOS, f));
    await p.setInputFiles('#archivos', archivos);
    await p.waitForSelector('#paneles canvas');
    await p.selectOption('#gesto', 'G5');
    await p.waitForTimeout(300);
    const paneles = await p.$$eval('#paneles canvas', (c) => c.length);
    assert.strictEqual(paneles, 3, 'BASE, A2B2 y comparación');
    const aviso = await p.isVisible('#aviso');
    assert.ok(aviso, 'avisa que los datos son sintéticos');
    const filas = await p.$$eval('#metricas tr', (t) => t.length);
    assert.ok(filas > 10, 'filas de métricas: ' + filas);
    const subt = await p.$$eval('.tarjeta-panel h4', (h) => h.map((x) => x.textContent));
    assert.ok(subt.some((t) => /n = 10/.test(t)), subt.join(' | '));
    const c = await p.$('#paneles canvas');
    const b = await c.boundingBox();
    await p.mouse.click(b.x + b.width * 0.3, b.y + b.height * 0.4);
    const lectura = await p.textContent('#lectura');
    assert.ok(/altura de la letra/.test(lectura), lectura);
    await p.fill('#nombre-medida', 'unión');
    await p.click('#guardar-medida');
    assert.strictEqual(await p.$$eval('#medidas tr', (t) => t.length), 2);
    await captura(p, 'superponer');
    const [d1] = await Promise.all([p.waitForEvent('download'), p.click('#svg')]);
    assert.ok(fs.readFileSync(await d1.path(), 'utf8').startsWith('<svg'));
    const [d2] = await Promise.all([p.waitForEvent('download'), p.click('#csv')]);
    assert.ok(fs.readFileSync(await d2.path(), 'utf8').split('\n').length > 20);
    await p.click('#ver-lamina');
    await p.waitForSelector('#contenido-lamina canvas');
    const lamina = await p.$$eval('#contenido-lamina canvas', (c) => c.length);
    assert.strictEqual(lamina, 9, 'tres gestos × (dos condiciones + comparación)');
    await captura(p, 'lamina');
    // con el bloque digitalizado de la foto se puede mezclar escaneo y tableta
    const dig = path.join(require('os').tmpdir(), 'apulso_digitalizado.json');
    if (fs.existsSync(dig)) {
      await p.click('#cerrar-lamina');
      await p.setInputFiles('#archivos', dig);
      await p.waitForTimeout(300);
      await p.selectOption('#persona', 'P00');
      await p.check('#ver-tinta');
      await p.waitForTimeout(500);
    }
    assert.deepStrictEqual(p.errores, []);
    await p.context().close();
  });

  await prueba('banco y fichas se dibujan sin errores', async () => {
    const p = await nuevaPagina(navegador);
    await p.goto(url('banco.html'));
    await p.waitForSelector('#planos svg');
    assert.strictEqual(await p.$$eval('#planos section', (s) => s.length), 4);
    await p.fill('#hombroDePie', '1500');
    const texto = await p.textContent('#planos');
    assert.ok(/agujero 14/.test(texto), 'agujero para un hombro de 1500');
    await captura(p, 'banco');
    await p.goto(url('ficha.html'));
    assert.strictEqual(await p.$$eval('.hoja', (h) => h.length), 5);
    assert.deepStrictEqual(p.errores, []);
    await p.context().close();
  });

  await navegador.close();
  console.log(fallas ? '\n' + fallas + ' prueba(s) fallaron' : '\nTodas las pruebas del navegador pasaron');
  process.exit(fallas ? 1 : 0);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
