// Mide con Chromium el ancho de cada carácter en las fuentes de las láminas,
// para que los scripts de Python puedan cortar líneas y poner resaltados.
// Uso: node medir_anchos.js carpeta_fuentes salida.json
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const FUENTES = {
  g400: ['Garamond', 'normal', 400, 'eb-garamond-latin-400-normal.woff2'],
  gi400: ['Garamond', 'italic', 400, 'eb-garamond-latin-400-italic.woff2'],
  g600: ['Garamond', 'normal', 600, 'eb-garamond-latin-600-normal.woff2'],
  p400: ['Plex', 'normal', 400, 'ibm-plex-sans-condensed-latin-400-normal.woff2'],
  p500: ['Plex', 'normal', 500, 'ibm-plex-sans-condensed-latin-500-normal.woff2'],
};

(async () => {
  const [, , carpeta, salida] = process.argv;
  let caras = '';
  for (const [, [fam, est, peso, archivo]] of Object.entries(FUENTES)) {
    const datos = fs.readFileSync(path.join(carpeta, archivo)).toString('base64');
    caras += `@font-face{font-family:'${fam}';font-style:${est};font-weight:${peso};` +
      `src:url(data:font/woff2;base64,${datos}) format('woff2');}`;
  }
  let chars = '';
  for (let c = 32; c < 127; c++) chars += String.fromCharCode(c);
  for (let c = 160; c < 256; c++) chars += String.fromCharCode(c);
  chars += '«»‘’“”…–—œŒæÆ•·×→←↑↓≈≤≥°';
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${caras}</style></head><body></body></html>`);
  const res = await page.evaluate(async ({ fuentes, chars }) => {
    const out = {};
    const cv = document.createElement('canvas');
    const ctx = cv.getContext('2d');
    for (const [clave, [fam, est, peso]] of Object.entries(fuentes)) {
      await document.fonts.load(`${est} ${peso} 100px '${fam}'`);
      ctx.font = `${est} ${peso} 1000px '${fam}'`;
      out[clave] = {};
      for (const ch of chars) out[clave][ch] = Math.round(ctx.measureText(ch).width) / 1000;
    }
    return out;
  }, { fuentes: FUENTES, chars });
  await browser.close();
  fs.writeFileSync(salida, JSON.stringify(res));
})();
