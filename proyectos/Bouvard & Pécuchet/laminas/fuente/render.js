// Pasa una lámina (SVG o HTML) a PDF y PNG con el Chromium instalado.
// Uso: node render.js entrada.svg salida_sin_extension ancho_mm alto_mm [escala_png]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [, , entrada, salida, anchoMm, altoMm, escala] = process.argv;
  const W = Number(anchoMm), H = Number(altoMm);
  const abs = path.resolve(entrada);
  let url = 'file://' + abs;
  let temporal = null;
  if (abs.endsWith('.svg')) {
    temporal = abs.replace(/\.svg$/, '.tmp.html');
    fs.writeFileSync(temporal,
      `<!doctype html><html><head><meta charset="utf-8"><style>` +
      `@page{size:${W}mm ${H}mm;margin:0}html,body{margin:0;padding:0;background:#fff}` +
      `svg{display:block;width:${W}mm;height:${H}mm}</style></head>` +
      `<body>${fs.readFileSync(abs, 'utf8')}</body></html>`);
    url = 'file://' + temporal;
  }
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: Number(escala || 3) });
  await page.setViewportSize({ width: Math.round(W / 25.4 * 96), height: Math.round(H / 25.4 * 96) });
  await page.goto(url, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  await page.pdf({ path: salida + '.pdf', width: W + 'mm', height: H + 'mm', printBackground: true, pageRanges: '1' });
  await page.screenshot({ path: salida + '.png' });
  await browser.close();
  if (temporal) fs.unlinkSync(temporal);
})();
