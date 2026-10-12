/* A pulso · banco de escritura
 * Medidas del banco y alturas de montaje de cada plano a partir del cuerpo de quien escribe.
 * B0 tablero de dibujo a 15° (cuña) · B1 mesa horizontal · B2 pizarra vertical (montantes) · B3 atril a 45°.
 * Todas las medidas en mm. Ver banco/Banco de escritura.md.
 */
(function (raiz) {
  'use strict';
  const AP = (raiz.APulso = raiz.APulso || {});

  const BANCO = {
    espesor: 18, // terciado o multilaminado
    tablero: { ancho: 600, alto: 600 },
    liston: { ancho: 42, margen: 20 }, // listones traseros: a 20 mm de los bordes; 42 = dos pasos de 25 menos los pasadores Ø8
    hoja: { centroDesdeArriba: 200, ancho: 420, alto: 297 }, // A3 apaisada o A4, siempre centrada en el mismo punto del tablero
    // bordeInferior: altura aproximada del borde inferior del tablero sobre la mesa
    cuna: { catetoH: 600, catetoV: 161, despunte: 20, angulo: 15, bordeInferior: 40 },
    atril: { cateto: 460, despunte: 30, angulo: 45, bordeInferior: 55 },
    muro: { montanteLargo: 750, montanteAncho: 90, separacion: 420, bordeInferior: 1250, primerAgujero: 50, paso: 25, agujeros: 27, pasador: [8, 32] },
  };

  // Criterios del proyecto (no son normas): ver el protocolo.
  const CRITERIOS = {
    B0: 'el codo queda 30 mm por encima del borde inferior del tablero a 15°, con el antebrazo apoyado: el puesto clásico de dibujo',
    B1: 'el codo queda 30 mm por encima del plano de la mesa, con el antebrazo apoyado',
    B2: 'el centro de la hoja queda a la altura del hombro, de pie, como en la pizarra',
    B3: 'el codo queda 20 mm por encima del borde inferior del tablero a 45°: el antebrazo descansa en la pendiente',
  };

  /** Plano inclinado sobre la mesa: altura del borde, centro de la hoja y asiento necesario. */
  function inclinado(apoyo, sobreBorde, m) {
    const rad = (apoyo.angulo * Math.PI) / 180;
    const borde = m.mesa + apoyo.bordeInferior;
    const distanciaCentro = BANCO.tablero.alto - BANCO.hoja.centroDesdeArriba; // desde el borde inferior, sobre la pendiente
    const asiento = borde + sobreBorde - m.codoSobreAsiento;
    const r = {
      angulo: apoyo.angulo,
      bordeInferior: borde,
      codoActual: m.asiento + m.codoSobreAsiento,
      codoObjetivo: borde + sobreBorde,
      asientoNecesario: asiento,
      ajusteAsiento: asiento - m.asiento,
      centroHoja: borde + distanciaCentro * Math.sin(rad),
      distanciaCodoCentro: distanciaCentro,
      avisos: [],
    };
    // alcance: la punta de la herramienta queda cerca de 0,85 del largo codo–dedos
    if (m.codoDedos * 0.85 < distanciaCentro - 60) r.avisos.push('El centro de la hoja queda lejos del alcance con el codo en el borde: baja la hoja en el tablero o anota el cambio.');
    return r;
  }

  /**
   * medidas: { codoSobreAsiento, hombroDePie, mesa, asiento, codoDedos }
   * Devuelve, para cada plano, la altura objetivo, el ajuste necesario y advertencias.
   */
  function calcularMontaje(medidas) {
    const m = Object.assign({ codoSobreAsiento: 230, hombroDePie: 1350, mesa: 720, asiento: 450, codoDedos: 450 }, medidas || {});
    const e = BANCO.espesor;
    const codo = m.asiento + m.codoSobreAsiento;
    const res = {};

    // B0: tablero de dibujo a 15° sobre la cuña
    res.B0 = inclinado(BANCO.cuna, 30, m);

    // B1: tablero plano sobre la mesa, apoyado en sus listones
    const planoB1 = m.mesa + 2 * e;
    const asientoB1 = planoB1 + 30 - m.codoSobreAsiento;
    res.B1 = {
      plano: planoB1,
      codoActual: codo,
      codoObjetivo: planoB1 + 30,
      asientoNecesario: asientoB1,
      ajusteAsiento: asientoB1 - m.asiento,
      centroHoja: planoB1,
      avisos: [],
    };

    // B3: tablero sobre el atril de 45°
    res.B3 = inclinado(BANCO.atril, 20, m);

    // B2: tablero colgado de dos pasadores en los montantes del muro
    const l = BANCO.liston;
    // del eje del pasador al borde superior del tablero: radio del pasador + ancho del listón + margen
    const sobrePasador = BANCO.muro.pasador[0] / 2 + l.ancho + l.margen;
    const pasadorObjetivo = m.hombroDePie + BANCO.hoja.centroDesdeArriba - sobrePasador;
    const mu = BANCO.muro;
    const primero = mu.bordeInferior + mu.primerAgujero;
    let k = Math.round((pasadorObjetivo - primero) / mu.paso);
    // los pasadores de traba van dos agujeros más arriba: el de apoyo no puede pasar del antepenúltimo
    const fuera = k < 0 || k > mu.agujeros - 3;
    k = Math.max(0, Math.min(mu.agujeros - 3, k));
    const pasador = primero + k * mu.paso;
    const centroB2 = pasador + sobrePasador - BANCO.hoja.centroDesdeArriba;
    res.B2 = {
      pasadorObjetivo,
      agujero: k + 1, // pasadores de apoyo, contados desde abajo
      agujeroTraba: k + 3, // pasadores de traba, sobre el listón
      pasador,
      centroHoja: centroB2,
      error: centroB2 - m.hombroDePie,
      avisos: fuera ? ['La altura del hombro queda fuera del rango de los montantes: muévelos o usa una tarima.'] : [],
    };

    for (const b of ['B0', 'B1', 'B3']) {
      const s = res[b].asientoNecesario;
      if (s > 620) res[b].avisos.push('El asiento quedaría a ' + Math.round(s) + ' mm: usa una mesa más baja o un taburete alto con reposapiés.');
      if (s < 380) res[b].avisos.push('El asiento quedaría a ' + Math.round(s) + ' mm: usa una mesa más alta o suplementa el tablero.');
    }
    return res;
  }

  AP.banco = { BANCO, CRITERIOS, calcularMontaje };
  if (typeof module !== 'undefined' && module.exports) module.exports = AP;
})(typeof window !== 'undefined' ? window : globalThis);
