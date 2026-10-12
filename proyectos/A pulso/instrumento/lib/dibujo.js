/* A pulso · dibujo de pautas y plantillas de topes como SVG (unidades: mm).
 * La misma geometría (nucleo.pautaDesdeCodigo) sirve para imprimir, cortar y digitalizar.
 */
(function (raiz) {
  'use strict';
  const AP = (raiz.APulso = raiz.APulso || {});

  // Cian claro: desaparece en el canal azul del escaneo. Los trazos deben hacerse con grafito o tinta negra.
  const CIAN = '#6cc5ee';
  const GRIS = '#555555';

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
  }
  function n(v) {
    return Math.round(v * 1000) / 1000;
  }

  /**
   * opciones: { filas: ['G1', 'G2', 'G5'], encabezado: { bloque, fecha, persona, sesion, condicion, herramienta, orden } }
   */
  function svgPauta(pauta, opciones) {
    const o = opciones || {};
    const G = AP.nucleo.GESTOS_CORTOS;
    const enc = o.encabezado || {};
    const p = [];
    p.push(
      '<svg xmlns="http://www.w3.org/2000/svg" width="' + pauta.W + 'mm" height="' + pauta.H + 'mm" viewBox="0 0 ' + pauta.W + ' ' + pauta.H + '" font-family="Helvetica, Arial, sans-serif">'
    );
    p.push('<rect width="' + pauta.W + '" height="' + pauta.H + '" fill="#fff"/>');

    // marcas de registro
    pauta.marcas.forEach(([x, y], k) => {
      p.push('<circle cx="' + x + '" cy="' + y + '" r="' + pauta.marcaDiametro / 2 + '" fill="#000"/>');
      const dx = k === 0 || k === 3 ? 6 : -6;
      const ancla = dx > 0 ? 'start' : 'end';
      p.push('<text x="' + (x + dx) + '" y="' + (y + 1.2) + '" font-size="3.2" fill="' + CIAN + '" text-anchor="' + ancla + '">' + (k + 1) + '</text>');
    });

    // encabezado
    const e = pauta.encabezado;
    const campos = [
      ['Bloque', enc.bloque, 26],
      ['Fecha', enc.fecha, 30],
      ['Persona', enc.persona, 18],
      ['Sesión', enc.sesion, 16],
      ['Orden', enc.orden, 12],
      ['Condición', enc.condicion, 26],
      ['Herramienta', enc.herramienta, 34],
    ];
    let x = e.x;
    const yTexto = e.y + 5;
    p.push('<text x="' + x + '" y="' + yTexto + '" font-size="4" font-weight="bold" fill="' + CIAN + '">A PULSO</text>');
    x += 22;
    const disponible = e.w - 22 - 46;
    const total = campos.reduce((s, c) => s + c[2] + c[0].length * 1.9 + 4, 0);
    const k = Math.min(1, disponible / total);
    for (const [etq, valor, ancho] of campos) {
      const largoEtq = etq.length * 1.9 * k + 1.5;
      p.push('<text x="' + n(x) + '" y="' + yTexto + '" font-size="' + n(3 * Math.max(0.8, k)) + '" fill="' + CIAN + '">' + esc(etq) + '</text>');
      const x0 = x + largoEtq;
      const x1 = x0 + ancho * k;
      p.push('<line x1="' + n(x0) + '" y1="' + (yTexto + 0.8) + '" x2="' + n(x1) + '" y2="' + (yTexto + 0.8) + '" stroke="' + CIAN + '" stroke-width="0.2"/>');
      if (valor != null && valor !== '') {
        p.push('<text x="' + n(x0 + 1) + '" y="' + (yTexto - 0.2) + '" font-size="3.4" fill="' + GRIS + '">' + esc(valor) + '</text>');
      }
      x = x1 + 4 * k;
    }
    p.push('<text x="' + (e.x + e.w) + '" y="' + yTexto + '" font-size="3" fill="' + CIAN + '" text-anchor="end">pauta ' + esc(pauta.codigo) + '</text>');
    p.push(
      '<text x="' + e.x + '" y="' + (e.y + 11) + '" font-size="2.6" fill="' + CIAN + '">Escribe con grafito o tinta negra. No escribas sobre las marcas negras ni fuera de las celdas. Altura x: ' +
        pauta.alturaX +
        ' mm.</text>'
    );

    // celdas
    const filasEtiquetadas = {};
    for (const c of pauta.celdas) {
      const t = 4;
      const lineaCorta = (x1, y1, x2, y2) => p.push('<line x1="' + n(x1) + '" y1="' + n(y1) + '" x2="' + n(x2) + '" y2="' + n(y2) + '" stroke="' + CIAN + '" stroke-width="0.2"/>');
      lineaCorta(c.x, c.y, c.x + t, c.y);
      lineaCorta(c.x, c.y, c.x, c.y + t);
      lineaCorta(c.x + c.w - t, c.y, c.x + c.w, c.y);
      lineaCorta(c.x + c.w, c.y, c.x + c.w, c.y + t);
      lineaCorta(c.x, c.y + c.h, c.x + t, c.y + c.h);
      lineaCorta(c.x, c.y + c.h - t, c.x, c.y + c.h);
      lineaCorta(c.x + c.w - t, c.y + c.h, c.x + c.w, c.y + c.h);
      lineaCorta(c.x + c.w, c.y + c.h - t, c.x + c.w, c.y + c.h);
      p.push('<line x1="' + n(c.x) + '" y1="' + n(c.base) + '" x2="' + n(c.x + c.w) + '" y2="' + n(c.base) + '" stroke="' + CIAN + '" stroke-width="0.3"/>');
      p.push(
        '<line x1="' + n(c.x) + '" y1="' + n(c.alturaX) + '" x2="' + n(c.x + c.w) + '" y2="' + n(c.alturaX) + '" stroke="' + CIAN + '" stroke-width="0.25" stroke-dasharray="2 1.2"/>'
      );
      if (c.ascendente != null) {
        p.push(
          '<line x1="' + n(c.x) + '" y1="' + n(c.ascendente) + '" x2="' + n(c.x + c.w) + '" y2="' + n(c.ascendente) + '" stroke="' + CIAN + '" stroke-width="0.2" stroke-dasharray="0.4 1.2"/>'
        );
      }
      p.push('<text x="' + n(c.x + 1) + '" y="' + n(c.y + 3.2) + '" font-size="2.4" fill="' + CIAN + '">' + c.indice + '</text>');
      if (!filasEtiquetadas[c.fila]) {
        filasEtiquetadas[c.fila] = true;
        const g = o.filas && o.filas[c.fila - 1];
        const etiqueta = g ? g + ' · ' + (G[g] || '') : 'G__';
        const cx = c.x - 4;
        const cy = c.y + c.h / 2;
        p.push(
          '<text x="' + n(cx) + '" y="' + n(cy) + '" font-size="2.8" fill="' + CIAN + '" text-anchor="middle" transform="rotate(-90 ' + n(cx) + ' ' + n(cy) + ')">' + esc(etiqueta) + '</text>'
        );
      }
    }

    // escala de control de impresión
    const ex = pauta.W / 2 - 50;
    const ey = pauta.H - 9;
    p.push('<line x1="' + ex + '" y1="' + ey + '" x2="' + (ex + 100) + '" y2="' + ey + '" stroke="' + GRIS + '" stroke-width="0.3"/>');
    for (let i = 0; i <= 10; i++) {
      const largo = i % 5 === 0 ? 2.5 : 1.2;
      p.push('<line x1="' + (ex + i * 10) + '" y1="' + ey + '" x2="' + (ex + i * 10) + '" y2="' + (ey - largo) + '" stroke="' + GRIS + '" stroke-width="0.25"/>');
    }
    p.push('<text x="' + (ex + 50) + '" y="' + (ey + 4) + '" font-size="2.6" fill="' + CIAN + '" text-anchor="middle">100 mm · imprime a tamaño real (100 %) y verifica esta medida</text>');
    p.push('</svg>');
    return p.join('\n');
  }

  /** Plantilla para corte láser: contorno y ventanas en rojo (corte), textos en azul (grabado). */
  function svgPlantillaTopes(pauta, nivel) {
    const ventanas = AP.nucleo.ventanasTopes(pauta, nivel);
    const corte = 'fill="none" stroke="#ff0000" stroke-width="0.1"';
    const p = [];
    p.push('<svg xmlns="http://www.w3.org/2000/svg" width="' + pauta.W + 'mm" height="' + pauta.H + 'mm" viewBox="0 0 ' + pauta.W + ' ' + pauta.H + '" font-family="Helvetica, Arial, sans-serif">');
    p.push('<rect x="0" y="0" width="' + pauta.W + '" height="' + pauta.H + '" ' + corte + '/>');
    for (const [x, y] of pauta.marcas) p.push('<circle cx="' + x + '" cy="' + y + '" r="6" ' + corte + '/>');
    for (const v of ventanas) p.push('<rect x="' + n(v.x) + '" y="' + n(v.y) + '" width="' + n(v.w) + '" height="' + n(v.h) + '" ' + corte + '/>');
    const desc = AP.nucleo.VARIABLES.C.niveles[nivel];
    p.push(
      '<text x="' + pauta.W / 2 + '" y="' + (pauta.H - 8) + '" font-size="4" fill="#0000ff" text-anchor="middle">A PULSO · topes ' + nivel + ' (' + esc(desc) + ') · pauta ' + esc(pauta.codigo) + ' · esta cara hacia arriba</text>'
    );
    p.push('</svg>');
    return p.join('\n');
  }

  AP.dibujo = { CIAN, svgPauta, svgPlantillaTopes };
  if (typeof module !== 'undefined' && module.exports) module.exports = AP;
})(typeof window !== 'undefined' ? window : globalThis);
