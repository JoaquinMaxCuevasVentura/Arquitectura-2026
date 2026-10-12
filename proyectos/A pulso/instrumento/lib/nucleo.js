/* A pulso · núcleo
 * Vocabulario del protocolo, identificadores, geometría de las pautas y formato de datos.
 * Funciona en el navegador (window.APulso) y en node (module.exports).
 * Unidades: milímetros. En la página, origen arriba a la izquierda y y hacia abajo.
 * En los ensayos, origen en el borde izquierdo de la celda sobre la línea base y y hacia arriba.
 * h («altura_x_mm» en los datos) es la altura de la letra de referencia: la mayúscula en la letra técnica.
 */
(function (raiz) {
  'use strict';
  const AP = (raiz.APulso = raiz.APulso || {});

  const FORMATO = 'a-pulso.bloque';
  const VERSION_FORMATO = 1;

  // Situación: el tablero de dibujo y la letra técnica del arquitecto.
  // La condición base (todos los niveles en 0) es el puesto clásico: tablero a 15°, antebrazo apoyado,
  // líneas guía y portaminas.
  const VARIABLES = {
    A: {
      nombre: 'Apoyo',
      niveles: {
        A0: 'antebrazo apoyado',
        A1: 'solo el canto de la mano',
        A2: 'brazo suspendido',
      },
    },
    B: {
      nombre: 'Plano',
      niveles: {
        B0: 'tablero de dibujo a 15°, sentado',
        B1: 'mesa horizontal, sentado',
        B2: 'pizarra vertical a la altura del hombro, de pie',
        B3: 'atril a 45°, sentado (opcional)',
      },
    },
    C: {
      nombre: 'Guía',
      niveles: {
        C0: 'líneas guía, a pulso',
        C1: 'sin líneas guía',
        C2: 'regla T y escuadra',
        C3: 'plantilla de rotulación (normógrafo)',
      },
    },
    D: {
      nombre: 'Herramienta',
      niveles: {
        D0: 'portaminas 0,5 HB sobre bond',
        D1: 'estilógrafo sobre bond',
        D2: 'portaminas sobre papel vegetal (calco)',
      },
    },
  };

  // Repertorio de la letra técnica: mayúsculas de palo seco y un rótulo de plano.
  // En este repertorio, h es la altura de la mayúscula.
  const GESTOS = {
    G1: 'asta vertical (I)',
    G2: 'trazo horizontal',
    G3: 'O',
    G4: 'A',
    G5: 'R',
    G6: 'rótulo «PLANTA 1:50»',
  };

  const GESTOS_CORTOS = { G1: 'I', G2: 'horizontal', G3: 'O', G4: 'A', G5: 'R', G6: 'PLANTA 1:50' };

  const CONDICIONES_SERIE = ['BASE', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'C3', 'D1', 'D2'];

  // Alturas nominales de la norma ISO 3098 (mm).
  const ALTURAS_ISO = [2.5, 3.5, 5, 7, 10, 14, 20];

  // ---------- condiciones ----------

  function parsearCondicion(codigo) {
    const limpio = String(codigo || '')
      .toUpperCase()
      .replace(/[\s·.\-_+]/g, '');
    const vars = { A: 'A0', B: 'B0', C: 'C0', D: 'D0' };
    if (limpio === '' || limpio === 'BASE') return { codigo: 'BASE', ...vars };
    const re = /([ABCD])(\d)/g;
    let m;
    let consumido = '';
    while ((m = re.exec(limpio))) {
      const nivel = m[1] + m[2];
      if (!VARIABLES[m[1]].niveles[nivel]) {
        throw new Error('Nivel desconocido: ' + nivel);
      }
      vars[m[1]] = nivel;
      consumido += m[0];
    }
    if (consumido !== limpio) {
      throw new Error('Condición no válida: «' + codigo + '». Usa BASE o niveles como A2B2.');
    }
    return { codigo: codigoCondicion(vars), ...vars };
  }

  function codigoCondicion(vars) {
    const partes = ['A', 'B', 'C', 'D'].map((k) => vars[k] || k + '0').filter((n) => n[1] !== '0');
    return partes.length ? partes.join('') : 'BASE';
  }

  function describirCondicion(codigo) {
    const c = parsearCondicion(codigo);
    return ['A', 'B', 'C', 'D']
      .map((k) => VARIABLES[k].nombre + ': ' + VARIABLES[k].niveles[c[k]])
      .join(' · ');
  }

  // ---------- identificadores ----------

  function dosDigitos(n) {
    const v = parseInt(n, 10);
    if (!Number.isFinite(v) || v < 0) throw new Error('Número no válido: ' + n);
    return String(v).padStart(2, '0');
  }

  function normalizarPersona(p) {
    const s = String(p == null ? '' : p).trim().toUpperCase();
    const m = s.match(/^P?(\d+)$/);
    if (!m) throw new Error('Persona no válida: «' + p + '». Usa P00, P01…');
    return 'P' + dosDigitos(m[1]);
  }

  function normalizarSesion(s) {
    const t = String(s == null ? '' : s).trim().toUpperCase();
    const m = t.match(/^S?(\d+)$/);
    if (!m) throw new Error('Sesión no válida: «' + s + '». Usa S01, S02…');
    return 'S' + dosDigitos(m[1]);
  }

  function normalizarGesto(g) {
    const t = String(g == null ? '' : g).trim().toUpperCase();
    const m = t.match(/^G?(\d)$/);
    if (!m || !GESTOS['G' + m[1]]) throw new Error('Gesto no válido: «' + g + '». Usa G1…G6.');
    return 'G' + m[1];
  }

  /** AP-P00-S03-B2-G5-R07; las repeticiones de calentamiento llevan K en lugar de R. */
  function idEnsayo(o) {
    return [
      'AP',
      normalizarPersona(o.persona),
      normalizarSesion(o.sesion),
      parsearCondicion(o.condicion).codigo,
      normalizarGesto(o.gesto),
      (o.calentamiento ? 'K' : 'R') + dosDigitos(o.repeticion),
    ].join('-');
  }

  function parsearId(id) {
    const m = String(id).match(/^AP-(P\d+)-(S\d+)-([A-Z0-9]+)-(G\d)-([RK])(\d+)$/);
    if (!m) throw new Error('Identificador no válido: ' + id);
    return {
      persona: m[1],
      sesion: m[2],
      condicion: m[3],
      gesto: m[4],
      calentamiento: m[5] === 'K',
      repeticion: parseInt(m[6], 10),
    };
  }

  // ---------- pautas ----------

  const PAPELES = { A3: [420, 297], A4: [297, 210] };
  const MARCA_INSET = 12; // centro de cada marca de registro, desde los bordes
  const MARCA_DIAMETRO = 6;
  const ENCABEZADO_Y = 19;
  const ENCABEZADO_ALTO = 14;
  const GRILLA_IZQ = 20;
  const GRILLA_DER = 20;
  const GRILLA_SUP = 38;
  const GRILLA_INF = 22;
  const SEPARACION_COL = 10;
  const SEPARACION_FILA_MAX = 12;

  // Proporciones de la celda respecto de la altura x (h).
  const CELDA = {
    L: { alto: 1.7, bajoBase: 0.35 }, // letras sueltas: sin ascendentes
    P: { alto: 2.4, bajoBase: 0.45, ascendente: 1.75 }, // palabras: ascendentes y tildes
  };

  const PRESETS = [
    { codigo: 'A4H-h10-L-3x5', nombre: 'Piloto · A4 · I, O, R × 5 · h 10 mm', filas: ['G1', 'G3', 'G5'] },
    { codigo: 'A4H-h10-L-4x5', nombre: 'Serie · A4 · letras · 20 celdas · h 10 mm' },
    { codigo: 'A4H-h10-L-5x2', nombre: 'Serie · A4 · rótulo «PLANTA 1:50» · 10 celdas', filas: ['G6', 'G6', 'G6', 'G6', 'G6'] },
    { codigo: 'A4H-h5-L-6x8', nombre: 'Escala · A4 · h 5 mm · 48 celdas' },
    { codigo: 'A4H-h20-L-3x4', nombre: 'Escala · A4 · h 20 mm · 12 celdas' },
    { codigo: 'A3H-h30-L-3x5', nombre: 'Títulos · A3 · h 30 mm · 15 celdas' },
  ];

  const RE_PAUTA = /^(A3|A4)([HV])-H(\d+(?:[.,]\d+)?)-([LP])-(\d+)X(\d+)$/;

  function pautaDesdeCodigo(codigo) {
    const m = String(codigo || '').trim().toUpperCase().match(RE_PAUTA);
    if (!m) throw new Error('Código de pauta no válido: «' + codigo + '». Ejemplo: A3H-h30-L-3x5');
    const papel = m[1];
    const orientacion = m[2];
    const h = parseFloat(m[3].replace(',', '.'));
    const tipo = m[4];
    const filas = parseInt(m[5], 10);
    const columnas = parseInt(m[6], 10);
    let [W, H] = PAPELES[papel];
    if (orientacion === 'V') [W, H] = [H, W];
    if (!(h > 0) || filas < 1 || columnas < 1) throw new Error('Pauta sin celdas: ' + codigo);

    const prop = CELDA[tipo];
    const gx0 = GRILLA_IZQ;
    const gy0 = GRILLA_SUP;
    const gw = W - GRILLA_IZQ - GRILLA_DER;
    const gh = H - GRILLA_SUP - GRILLA_INF;
    const ch = prop.alto * h;
    const cw = (gw - (columnas - 1) * SEPARACION_COL) / columnas;
    const anchoMin = tipo === 'L' ? 1.3 * h : 4 * h;
    if (cw < anchoMin) {
      throw new Error('Demasiadas columnas para una altura x de ' + h + ' mm en ' + papel + orientacion);
    }
    let sepFila = 0;
    if (filas > 1) {
      sepFila = Math.min(SEPARACION_FILA_MAX, (gh - filas * ch) / (filas - 1));
      if (sepFila < 4) throw new Error('Demasiadas filas para una altura x de ' + h + ' mm en ' + papel + orientacion);
    } else if (ch > gh) {
      throw new Error('La celda no cabe en ' + papel + orientacion);
    }

    // la grilla se centra en la vertical del espacio disponible
    const yInicio = gy0 + (gh - (filas * ch + (filas - 1) * sepFila)) / 2;
    const celdas = [];
    for (let f = 0; f < filas; f++) {
      for (let c = 0; c < columnas; c++) {
        const x = gx0 + c * (cw + SEPARACION_COL);
        const y = yInicio + f * (ch + sepFila);
        const base = y + ch - prop.bajoBase * h;
        const celda = {
          indice: f * columnas + c + 1,
          fila: f + 1,
          columna: c + 1,
          x,
          y,
          w: cw,
          h: ch,
          base, // y de la línea base en la página
          alturaX: base - h, // y de la línea de altura x en la página
        };
        if (prop.ascendente) celda.ascendente = base - prop.ascendente * h;
        celdas.push(celda);
      }
    }

    const i = MARCA_INSET;
    return {
      codigo: papel + orientacion + '-h' + fmt(h) + '-' + tipo + '-' + filas + 'x' + columnas,
      papel,
      orientacion,
      W,
      H,
      alturaX: h,
      tipo,
      filas,
      columnas,
      celdas,
      marcas: [
        [i, i],
        [W - i, i],
        [W - i, H - i],
        [i, H - i],
      ],
      marcaDiametro: MARCA_DIAMETRO,
      encabezado: { x: GRILLA_IZQ, y: ENCABEZADO_Y, w: gw, h: ENCABEZADO_ALTO },
      grilla: { x: gx0, y: gy0, w: gw, h: gh },
    };
  }

  /** Distancia de la parte superior de la celda a la línea base, en mm. */
  function baseEnCelda(celda) {
    return celda.base - celda.y;
  }

  function fmt(n) {
    return Number.isInteger(n) ? String(n) : String(Math.round(n * 100) / 100);
  }

  // ---------- bloques ----------

  /**
   * Un bloque reúne las trazas de una condición escritas seguidas en una sesión.
   * meta: { persona, sesion, condicion, alturaX, herramienta, fecha, orden, pauta, nota, origen }
   */
  function nuevoBloque(meta) {
    const cond = parsearCondicion(meta.condicion);
    return {
      formato: FORMATO,
      version: VERSION_FORMATO,
      creado: new Date().toISOString(),
      origen: meta.origen || 'tableta',
      aviso: meta.aviso || undefined,
      bloque: {
        persona: normalizarPersona(meta.persona),
        sesion: normalizarSesion(meta.sesion),
        condicion: cond.codigo,
        variables: { A: cond.A, B: cond.B, C: cond.C, D: cond.D },
        altura_x_mm: Number(meta.alturaX) || 30,
        herramienta: meta.herramienta || '',
        superficie: meta.superficie || '',
        fecha: meta.fecha || new Date().toISOString().slice(0, 10),
        orden_en_sesion: meta.orden != null && meta.orden !== '' ? Number(meta.orden) : null,
        pauta: meta.pauta || '',
        nota: meta.nota || '',
      },
      ensayos: [],
    };
  }

  function validarBloque(obj) {
    const errores = [];
    if (!obj || obj.formato !== FORMATO) errores.push('No es un bloque de A pulso (falta formato).');
    else {
      if (obj.version > VERSION_FORMATO) errores.push('Versión de formato más nueva que este instrumento.');
      if (!obj.bloque) errores.push('Falta el encabezado del bloque.');
      if (!Array.isArray(obj.ensayos)) errores.push('Falta la lista de ensayos.');
      else
        obj.ensayos.forEach((e, i) => {
          try {
            parsearId(e.id);
          } catch (err) {
            errores.push('Ensayo ' + (i + 1) + ': ' + err.message);
          }
          if (!Array.isArray(e.trazos)) errores.push('Ensayo ' + (e.id || i + 1) + ': sin trazos.');
        });
    }
    return errores;
  }

  function nombreArchivoBloque(b) {
    const k = b.bloque;
    const orden = k.orden_en_sesion != null ? '-O' + dosDigitos(k.orden_en_sesion) : '';
    return ['AP', k.persona, k.sesion].join('-') + orden + '-' + k.condicion + '.json';
  }

  // ---------- registro CSV ----------

  const COLUMNAS_REGISTRO = [
    'id', 'fecha', 'persona', 'sesion', 'orden_en_sesion', 'condicion', 'apoyo', 'plano', 'limite',
    'resistencia', 'altura_x_mm', 'gesto', 'repeticion', 'herramienta', 'archivo_traza', 'archivo_video',
    'articulacion_dominante', 'levantamientos', 'duracion_s', 'seleccionada', 'regla', 'nota',
  ];

  function filasRegistro(b, nombreArchivo) {
    const k = b.bloque;
    const archivo = nombreArchivo || nombreArchivoBloque(b);
    return b.ensayos
      .filter((e) => !e.calentamiento)
      .map((e) => {
        let duracion = '';
        let levantamientos = '';
        if (b.origen !== 'escaneo') {
          levantamientos = Math.max(0, e.trazos.length - 1);
          const ts = [];
          for (const t of e.trazos) for (const p of t.puntos) if (p.length > 2) ts.push(p[2]);
          if (ts.length) duracion = ((Math.max(...ts) - Math.min(...ts)) / 1000).toFixed(2);
        }
        return {
          id: e.id,
          fecha: k.fecha,
          persona: k.persona,
          sesion: k.sesion,
          orden_en_sesion: k.orden_en_sesion == null ? '' : k.orden_en_sesion,
          condicion: k.condicion,
          apoyo: k.variables.A,
          plano: k.variables.B,
          limite: k.variables.C,
          resistencia: k.variables.D,
          altura_x_mm: k.altura_x_mm,
          gesto: e.gesto,
          repeticion: 'R' + dosDigitos(e.repeticion),
          herramienta: k.herramienta,
          archivo_traza: archivo + '#' + e.id,
          archivo_video: '',
          articulacion_dominante: '',
          levantamientos,
          duracion_s: duracion,
          seleccionada: 'no',
          regla: '',
          nota: e.nota || '',
        };
      });
  }

  function csvCelda(v) {
    const s = v == null ? '' : String(v);
    return /[",\n;]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }

  function aCSV(filas, columnas, conEncabezado) {
    const cols = columnas || COLUMNAS_REGISTRO;
    const lineas = filas.map((f) => cols.map((c) => csvCelda(f[c])).join(','));
    if (conEncabezado !== false) lineas.unshift(cols.join(','));
    return lineas.join('\n') + '\n';
  }

  AP.nucleo = {
    FORMATO,
    VERSION_FORMATO,
    VARIABLES,
    GESTOS,
    GESTOS_CORTOS,
    CONDICIONES_SERIE,
    ALTURAS_ISO,
    PRESETS,
    COLUMNAS_REGISTRO,
    parsearCondicion,
    codigoCondicion,
    describirCondicion,
    normalizarPersona,
    normalizarSesion,
    normalizarGesto,
    dosDigitos,
    idEnsayo,
    parsearId,
    pautaDesdeCodigo,
    baseEnCelda,
    nuevoBloque,
    validarBloque,
    nombreArchivoBloque,
    filasRegistro,
    aCSV,
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = AP;
})(typeof window !== 'undefined' ? window : globalThis);
