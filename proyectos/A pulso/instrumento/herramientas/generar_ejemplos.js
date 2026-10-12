/* Genera los datos de ejemplo SINTÉTICOS de datos_ejemplo/.
 * Uso: node herramientas/generar_ejemplos.js
 * Requiere Playwright (para codificar las fotos como JPEG).
 */
'use strict';
const fs = require('fs');
const path = require('path');
const os = require('os');
const { pathToFileURL } = require('url');
const AP = require('../lib/nucleo.js');
const S = require('./sinteticos.js');
const { codificarPNG } = require('./png.js');

const RAIZ = path.join(__dirname, '..');
const SALIDA = path.join(RAIZ, 'datos_ejemplo');

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

(async () => {
  fs.mkdirSync(SALIDA, { recursive: true });
  const bloques = S.bloquesPiloto(7);
  for (const b of bloques) {
    const nombre = 'SINTETICO_' + AP.nucleo.nombreArchivoBloque(b);
    fs.writeFileSync(path.join(SALIDA, nombre), JSON.stringify(b));
    console.log('bloque', nombre, b.ensayos.length, 'repeticiones');
  }

  const { chromium } = cargarPlaywright();
  const navegador = await chromium.launch();
  const pagina = await navegador.newPage();
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'apulso-'));
  const marcas = {};
  for (const [cond, semilla] of [['BASE', 21], ['A2B2', 22]]) {
    const f = S.hojaFotografiada({ condicion: cond, semilla, ancho: 2200, alto: 1600 });
    const png = path.join(tmp, cond + '.png');
    fs.writeFileSync(png, codificarPNG(f.foto, f.ancho, f.alto));
    await pagina.goto(pathToFileURL(png).href);
    const datos = await pagina.evaluate(() => {
      const im = document.querySelector('img');
      const c = document.createElement('canvas');
      c.width = im.naturalWidth;
      c.height = im.naturalHeight;
      c.getContext('2d').drawImage(im, 0, 0);
      return c.toDataURL('image/jpeg', 0.88);
    });
    const nombre = 'SINTETICO_hoja_' + f.pauta.codigo + '_' + cond + '.jpg';
    fs.writeFileSync(path.join(SALIDA, nombre), Buffer.from(datos.split(',')[1], 'base64'));
    marcas[nombre] = f.marcasFoto.map(([x, y]) => [Math.round(x * 10) / 10, Math.round(y * 10) / 10]);
    console.log('foto', nombre);
  }
  fs.writeFileSync(path.join(SALIDA, 'SINTETICO_marcas.json'), JSON.stringify({ aviso: S.AVISO, marcas_px: marcas }, null, 1));
  await navegador.close();
  fs.rmSync(tmp, { recursive: true, force: true });
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
