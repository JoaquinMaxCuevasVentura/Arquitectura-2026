/* Genera los PDF imprimibles: pautas, fichas y planos del banco.
 * Uso: node herramientas/generar_imprimibles.js   (requiere Playwright)
 * Salida: ../imprimibles/*.pdf y ../banco/Banco de escritura - planos.pdf
 */
'use strict';
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const AP = require('../lib/nucleo.js');
require('../lib/dibujo.js');

const RAIZ = path.join(__dirname, '..');
const PROYECTO = path.join(RAIZ, '..');
const IMPRIMIBLES = path.join(PROYECTO, 'imprimibles');

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

const G6 = ['G6', 'G6', 'G6', 'G6', 'G6'];
// [archivo, código, gestos por fila, con líneas guía]
const PAUTAS = [
  ['pauta_piloto_A4H-h10-L-3x5.pdf', 'A4H-h10-L-3x5', ['G1', 'G3', 'G5'], true],
  ['pauta_serie_letras_A4H-h10-L-4x5.pdf', 'A4H-h10-L-4x5', null, true],
  ['pauta_serie_letras_sin-guias_A4H-h10-L-4x5.pdf', 'A4H-h10-L-4x5', null, false],
  ['pauta_serie_rotulo_A4H-h10-L-5x2.pdf', 'A4H-h10-L-5x2', G6, true],
  ['pauta_serie_rotulo_sin-guias_A4H-h10-L-5x2.pdf', 'A4H-h10-L-5x2', G6, false],
  ['pauta_escala_A4H-h5-L-6x8.pdf', 'A4H-h5-L-6x8', null, true],
  ['pauta_escala_A4H-h20-L-3x4.pdf', 'A4H-h20-L-3x4', null, true],
  ['pauta_titulos_A3H-h30-L-3x5.pdf', 'A3H-h30-L-3x5', null, true],
];

const FICHAS = [
  ['ficha_de_ensayo.pdf', 'ficha'],
  ['medidas_y_montaje.pdf', 'medidas'],
  ['lista_del_piloto.pdf', 'piloto'],
  ['hoja_de_sesion.pdf', 'sesion'],
  ['consentimiento_informado.pdf', 'consentimiento'],
];

function paginaSVG(svgs, W, H) {
  return (
    '<!doctype html><html><head><meta charset="utf-8"><style>@page { size: ' + W + 'mm ' + H + 'mm; margin: 0 } html, body { margin: 0 } ' +
    '.p { width: ' + W + 'mm; height: ' + H + 'mm; page-break-after: always; overflow: hidden } .p:last-child { page-break-after: auto } .p svg { display: block; width: ' + W + 'mm; height: ' + H + 'mm }</style></head><body>' +
    svgs.map((s) => '<div class="p">' + s + '</div>').join('') +
    '</body></html>'
  );
}

(async () => {
  fs.mkdirSync(IMPRIMIBLES, { recursive: true });
  const { chromium } = cargarPlaywright();
  const navegador = await chromium.launch();
  const pagina = await navegador.newPage();

  for (const f of fs.readdirSync(IMPRIMIBLES)) if (f.endsWith('.pdf')) fs.unlinkSync(path.join(IMPRIMIBLES, f));
  for (const [nombre, codigo, filas, guias] of PAUTAS) {
    const pauta = AP.nucleo.pautaDesdeCodigo(codigo);
    const svg = AP.dibujo.svgPauta(pauta, { filas, guias });
    await pagina.setContent(paginaSVG([svg], pauta.W, pauta.H));
    await pagina.pdf({ path: path.join(IMPRIMIBLES, nombre), preferCSSPageSize: true, printBackground: true });
    console.log('pauta', nombre);
  }

  for (const [nombre, id] of FICHAS) {
    await pagina.goto(pathToFileURL(path.join(RAIZ, 'ficha.html')).href);
    await pagina.evaluate((id) => {
      document.querySelectorAll('.hoja').forEach((h) => h.classList.toggle('oculta', h.id !== id));
    }, id);
    await pagina.emulateMedia({ media: 'print' });
    await pagina.pdf({ path: path.join(IMPRIMIBLES, nombre), preferCSSPageSize: true, printBackground: true });
    await pagina.emulateMedia({ media: 'screen' });
    console.log('ficha', nombre);
  }

  const dirPlanos = path.join(PROYECTO, 'banco', 'planos');
  const planos = fs.readdirSync(dirPlanos).filter((f) => f.endsWith('.svg')).sort().map((f) => fs.readFileSync(path.join(dirPlanos, f), 'utf8'));
  await pagina.setContent(paginaSVG(planos, 420, 297));
  await pagina.pdf({ path: path.join(PROYECTO, 'banco', 'Banco de escritura - planos.pdf'), preferCSSPageSize: true, printBackground: true });
  console.log('planos', planos.length, 'láminas');

  await navegador.close();
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
