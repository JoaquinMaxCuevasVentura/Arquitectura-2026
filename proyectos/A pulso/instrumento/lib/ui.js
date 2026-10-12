/* A pulso · utilidades de interfaz (solo navegador) */
(function (raiz) {
  'use strict';
  const AP = (raiz.APulso = raiz.APulso || {});

  // Colores para distinguir condiciones en las superposiciones.
  const COLORES = ['#2f6db3', '#c8433a', '#2a8a5f', '#c98a12', '#7a55a8', '#3b8fa0'];

  function $(sel, ctx) {
    return (ctx || document).querySelector(sel);
  }

  function el(tag, attrs, hijos) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null || v === false) continue;
      if (k === 'texto') e.textContent = v;
      else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? '' : v);
    }
    for (const h of [].concat(hijos || [])) if (h != null) e.append(h);
    return e;
  }

  function descargar(nombre, datos, tipo) {
    const blob = datos instanceof Blob ? datos : new Blob([datos], { type: tipo || 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = el('a', { href: url, download: nombre });
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }

  function leerTexto(archivo) {
    return new Promise((ok, mal) => {
      const r = new FileReader();
      r.onload = () => ok(r.result);
      r.onerror = () => mal(r.error);
      r.readAsText(archivo);
    });
  }

  // El almacenamiento local es solo un respaldo: puede no estar disponible.
  function guardarLocal(clave, valor) {
    try {
      localStorage.setItem('apulso.' + clave, JSON.stringify(valor));
      return true;
    } catch (e) {
      return false;
    }
  }
  function leerLocal(clave, defecto) {
    try {
      const v = localStorage.getItem('apulso.' + clave);
      return v == null ? defecto : JSON.parse(v);
    } catch (e) {
      return defecto;
    }
  }

  /** Número con coma decimal. */
  function num(v, dec) {
    if (v == null || !Number.isFinite(v)) return '—';
    return v.toLocaleString('es', { minimumFractionDigits: dec == null ? 1 : dec, maximumFractionDigits: dec == null ? 1 : dec });
  }

  function estado(nodo, texto, tipo) {
    nodo.textContent = texto;
    nodo.className = 'estado' + (tipo ? ' ' + tipo : '');
    nodo.hidden = !texto;
  }

  AP.ui = { COLORES, $, el, descargar, leerTexto, guardarLocal, leerLocal, num, estado };
})(window);
