// Genera "Estudio de costos renderizado Tupiza.docx" (Word editable).
// Uso: node reports/fuente/generar_docx.js
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  ShadingType, BorderStyle, AlignmentType, HeadingLevel, LevelFormat, Footer,
  PageNumber, TabStopType, Tab, ExternalHyperlink, VerticalAlign, TableLayoutType,
} = require("docx");

const ACCENT = "0E5A63";
const ACCENT_SOFT = "E3F0F1";
const SOFT = "F3F6F7";
const MUTED = "5D6670";
const LINE = "D9DEE3";
const WARN = "8A4B08";
const WARN_SOFT = "FBF1E3";
const FONT = "Arial";
const CONTENT_W = 9906; // A4 (11906) menos márgenes de 1000 DXA

// Convierte "texto **negrita** texto" en TextRuns.
function runs(text, opts = {}) {
  return text.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map((part) => {
    const bold = part.startsWith("**") && part.endsWith("**");
    return new TextRun({ text: bold ? part.slice(2, -2) : part, bold: bold || opts.bold, color: opts.color, size: opts.size, font: FONT });
  });
}
const p = (text, opts = {}) => new Paragraph({ children: runs(text, opts), spacing: { after: opts.after ?? 120 }, alignment: opts.align });
const small = (text) => p(text, { size: 16, color: MUTED });
const h1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(text)] });
const h2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });
const bullet = (text) => new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: runs(text), spacing: { after: 60 } });
const numbered = (ref, text) => new Paragraph({ numbering: { reference: ref, level: 0 }, children: runs(text), spacing: { after: 60 } });

const thin = { style: BorderStyle.SINGLE, size: 4, color: LINE };
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };

function cell(text, width, { header = false, right = false, fill, bold = false, color, size = 18 } = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: header ? { type: ShadingType.CLEAR, color: "auto", fill: ACCENT } : fill ? { type: ShadingType.CLEAR, color: "auto", fill } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    verticalAlign: VerticalAlign.TOP,
    borders: { top: none, left: none, right: none, bottom: header ? none : thin },
    children: String(text).split("|").map((line) => new Paragraph({
      alignment: right ? AlignmentType.RIGHT : AlignmentType.LEFT,
      children: runs(line, { bold: header || bold, color: header ? "FFFFFF" : color, size }),
    })),
  });
}

// rows: arrays de strings; "|" dentro de un texto = salto de línea en la celda.
function table(widths, header, rows, { rightCols = [], totalLast = false, mutedRows = [] } = {}) {
  const trs = [];
  if (header) {
    trs.push(new TableRow({ tableHeader: true, children: header.map((t, i) => cell(t, widths[i], { header: true, right: rightCols.includes(i) })) }));
  }
  rows.forEach((r, ri) => {
    const isTotal = totalLast && ri === rows.length - 1;
    trs.push(new TableRow({
      cantSplit: true,
      children: r.map((t, i) => cell(t, widths[i], {
        right: rightCols.includes(i), fill: isTotal ? ACCENT_SOFT : undefined, bold: isTotal,
        color: mutedRows.includes(ri) ? MUTED : undefined,
      })),
    }));
  });
  return new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED, rows: trs });
}

function tiles(items) {
  const w = [2477, 2477, 2476, 2476];
  const white = { style: BorderStyle.SINGLE, size: 24, color: "FFFFFF" };
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: w, layout: TableLayoutType.FIXED,
    rows: [new TableRow({
      children: items.map(([k, v, s], i) => new TableCell({
        width: { size: w[i], type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, color: "auto", fill: ACCENT_SOFT },
        margins: { top: 100, bottom: 100, left: 140, right: 140 },
        borders: { top: white, bottom: white, left: white, right: white },
        children: [
          new Paragraph({ children: [new TextRun({ text: k.toUpperCase(), size: 15, color: MUTED, font: FONT })] }),
          new Paragraph({ children: [new TextRun({ text: v, size: 30, bold: true, color: ACCENT, font: FONT })] }),
          new Paragraph({ children: [new TextRun({ text: s, size: 15, color: MUTED, font: FONT })] }),
        ],
      })),
    })],
  });
}

function packages(cols) {
  const w = [4953, 4953];
  const box = { style: BorderStyle.SINGLE, size: 6, color: LINE };
  const gap = { style: BorderStyle.SINGLE, size: 36, color: "FFFFFF" };
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: w, layout: TableLayoutType.FIXED,
    rows: [new TableRow({
      cantSplit: true,
      children: cols.map(({ title, price, usd, items, note }, i) => new TableCell({
        width: { size: w[i], type: WidthType.DXA },
        margins: { top: 120, bottom: 120, left: 160, right: 160 },
        borders: { top: box, bottom: box, left: i === 0 ? box : gap, right: i === 0 ? gap : box },
        children: [
          new Paragraph({ children: [new TextRun({ text: title, bold: true, color: ACCENT, size: 20, font: FONT })] }),
          new Paragraph({ spacing: { after: 80 }, children: [
            new TextRun({ text: price, bold: true, color: ACCENT, size: 32, font: FONT }),
            new TextRun({ text: `  (${usd})`, color: MUTED, size: 16, font: FONT }),
          ] }),
          ...items.map((t) => new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: runs(t, { size: 17 }), spacing: { after: 40 } })),
          new Paragraph({ spacing: { before: 60 }, children: runs(note, { size: 16, color: MUTED }) }),
        ],
      })),
    })],
  });
}

function callout(children, { color = ACCENT, fill = SOFT } = {}) {
  return children.map((c, i) => new Paragraph({
    children: c,
    shading: { type: ShadingType.CLEAR, color: "auto", fill },
    border: { left: { style: BorderStyle.SINGLE, size: 24, color, space: 8 } },
    indent: { left: 160, right: 80 },
    spacing: { before: i === 0 ? 120 : 0, after: 120 },
  }));
}

function link(label, url) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 }, spacing: { after: 30 },
    children: [
      new TextRun({ text: `${label}: `, size: 15, color: MUTED, font: FONT }),
      new ExternalHyperlink({ link: url, children: [new TextRun({ text: url, size: 15, color: ACCENT, font: FONT })] }),
    ],
  });
}

const children = [
  new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("Estudio de costos de renderizado")] }),
  p("Terminal de buses de Tupiza (Potosí) · proyecto presentado por CBI · precios de entrada para un primer trabajo profesional", { size: 23, color: MUTED, after: 80 }),
  new Paragraph({
    border: { top: { style: BorderStyle.SINGLE, size: 4, color: LINE, space: 4 }, bottom: { style: BorderStyle.SINGLE, size: 4, color: LINE, space: 4 } },
    spacing: { after: 200 },
    children: runs("La Paz, 1 de octubre de 2026 · Flujo de trabajo: Revit → D5 Render → postproducción en Photoshop → mejora de realismo con IA · Tipo de cambio de referencia: **Bs 12,02 por USD** (oficial BCB, 30-09-2026)", { size: 16, color: MUTED }),
  }),

  h1("1. Resumen"),
  p("Como es tu primer trabajo profesional, los precios de este documento se ubican en el **piso del mercado boliviano**. Quedan muy por debajo del precio comercial estimado para un estudio establecido, pero siguen cubriendo tus gastos y pagan tu tiempo por encima del salario mínimo."),
  tiles([
    ["Paquete completo", "Bs 10.000", "≈ USD 832 · 8 imágenes + 3 min"],
    ["Por imagen 4K", "Bs 500", "≈ USD 42"],
    ["Por minuto de video", "Bs 2.000", "≈ USD 166"],
    ["Precio mínimo", "Bs 7.500", "No bajar de aquí (paquete completo)"],
  ]),
  p("", { after: 60 }),
  bullet("**62 % menos** que el precio comercial estimado para el mismo paquete (≈ Bs 26.550)."),
  bullet("Prácticamente igual al único precio boliviano publicado: un paquete para tesis de Santa Cruz a **USD 750–900 (Bs 9.015–10.818)**."),
  bullet("Con ≈ 187 horas de trabajo, te queda ≈ **Bs 32 por hora** después de impuestos y gastos, equivalente a ≈ Bs 5.150 al mes. Es un ingreso coherente con el de un arquitecto junior en Bolivia."),
  bullet("Por debajo de **Bs 7.500** ganarías menos que el salario mínimo por hora (Bs 3.300 al mes ≈ Bs 20,6 por hora)."),

  h1("2. Precios propuestos"),
  table([4806, 1500, 1000, 2600], ["Entregable", "Tu precio (Bs)", "≈ USD", "Precio comercial de referencia (Bs)"], [
    ["Imagen 4K estándar, exterior o interior (D5 + Photoshop + IA, 2 rondas de cambios)", "500", "42", "1.100 – 1.900"],
    ["Vista aérea de conjunto", "700", "58", "1.500 – 2.850"],
    ["Variante nocturna de una vista ya montada", "350", "29", "825 – 1.710"],
    ["Video recorrido, por minuto (Full HD 1080p, 30 fps, edición y música incluidas)", "2.000", "166", "4.000 – 7.000"],
    ["Panorámica 360° (opcional)", "600", "50", "≈ 1.800 – 2.300"],
    ["Cambios fuera de lo incluido (por hora)", "40", "3", "80 – 120"],
  ], { rightCols: [1, 2, 3] }),
  small("El precio comercial de referencia es el que correspondería a un estudio establecido, con factura. Sale del estudio de mercado previo. La panorámica 360° se cotiza en la región entre USD 152 y 190."),

  h2("Dos opciones de paquete para presentar a CBI"),
  packages([
    { title: "Opción A · Completo", price: "Bs 10.000", usd: "≈ USD 832",
      items: ["6 imágenes 4K estándar (6 × Bs 500)", "1 vista aérea de conjunto (Bs 700)", "1 variante nocturna (Bs 350)", "Video recorrido de 3 minutos (3 × Bs 2.000)"],
      note: "Suma de partidas: Bs 10.050, redondeado a Bs 10.000." },
    { title: "Opción B · Reducido", price: "Bs 7.500", usd: "≈ USD 624",
      items: ["4 imágenes 4K estándar", "1 vista aérea de conjunto", "1 variante nocturna", "Video recorrido de 2 minutos"],
      note: "Suma de partidas: Bs 7.050. Se suben Bs 450 porque la preparación de la escena cuesta lo mismo aunque haya menos entregables." },
  ]),
  p("", { after: 60 }),
  p("**Vistas sugeridas (a confirmar con CBI según el modelo):** aérea de conjunto; fachada y plaza de acceso de día; la misma vista de noche; andenes con buses; hall de boleterías; sala de espera; zona de locales o servicios; acceso peatonal desde la calle."),

  h1("3. De dónde salen los números"),
  h2("Horas de trabajo estimadas (Opción A)"),
  table([8406, 1500], ["Tarea", "Horas"], [
    ["Preparación de la escena en D5, una sola vez: materiales, terreno, vegetación, buses, personas, cielo", "36"],
    ["8 imágenes × 6 h (cámara, luz, render, Photoshop, IA)", "48"],
    ["3 minutos de video × 24 h (rutas de cámara, animación, render, edición)", "72"],
    ["Reserva para revisiones (20 %)", "31"],
    ["Total (≈ 5 semanas a tiempo completo)", "≈ 187"],
  ], { rightCols: [1], totalLast: true }),

  h2("Gastos del proyecto"),
  table([8406, 1500], ["Concepto", "Bs"], [
    ["D5 Render Pro, 2 meses (USD 38 al mes)", "914"],
    ["Photoshop, 2 meses (USD 22,99 al mes)", "553"],
    ["Krea Basic para la mejora con IA, 2 meses (USD 9 al mes, uso comercial incluido)", "216"],
    ["Electricidad (≈ Bs 0,85 por hora de equipo)", "160"],
    ["Desgaste del equipo (PC de Bs 18.000–25.000 a 4 años, ≈ Bs 3,1 por hora)", "580"],
    ["Total de gastos", "≈ 2.423"],
  ], { rightCols: [1], totalLast: true }),
  small("DaVinci Resolve (edición de video) es gratuito. Se asume que ya tienes acceso a Revit para abrir el modelo de CBI."),

  h2("Lo que te queda con el paquete de Bs 10.000"),
  table([8406, 1500], null, [
    ["Precio cotizado a CBI", "10.000"],
    ["− Retención de impuestos si no hay factura (15,5 %)", "− 1.550"],
    ["Lo que recibes", "8.450"],
    ["− Gastos del proyecto", "− 2.423"],
    ["Pago por tu trabajo (≈ Bs 32 por hora en 187 h)", "≈ 6.027"],
  ], { rightCols: [1], totalLast: true, mutedRows: [1, 3] }),
  p("", { after: 60 }),
  p("Si trabajas más rápido (≈ 120 horas y un solo mes de licencias), tu pago sube a ≈ **Bs 60 por hora**. Si tardas mucho más de 187 horas, el paquete deja de ser rentable. Por eso es clave limitar los cambios (ver sección 6)."),
  p("**Precio mínimo:** 187 horas pagadas al salario mínimo (Bs 20,6 por hora), más los gastos y la retención, dan ≈ **Bs 7.440**. Para el paquete completo no conviene bajar de **Bs 7.500**."),

  h1("4. Qué cobra el mercado"),
  table([3300, 2600, 4006], ["Referencia", "Precio", "Comentario"], [
    ["Estudios de La Paz y El Alto (HOME TEC, Estudio Vértice, ARQA Studio)", "No publican", "Cotizan por WhatsApp o mensaje privado"],
    ["ARQUINEX, Santa Cruz: paquete para tesis", "USD 750–900|Bs 9.015–10.818", "9–13 imágenes, modelado y 1,5–2 min de video; solo vistas de día. Es el piso boliviano."],
    ["Freelancers en Bolivia (Freelancer.com)", "≈ USD 8 por hora", "Promedio; confianza baja"],
    ["Estudios de Argentina, Chile, Colombia, México y Ecuador", "USD 90–350 por imagen|USD 1.000–1.700 por 1 min de video", "Gama media; motores en tiempo real"],
    ["Precio comercial estimado en Bolivia, con factura", "≈ Bs 26.550 por el paquete A", "Estudio establecido; resultado del informe de mercado previo"],
  ]),
  p("", { after: 60 }),
  p("Tu precio de Bs 10.000 se ubica en el piso boliviano. Para un primer trabajo tiene sentido: la ganancia más grande de este proyecto es el **portafolio** y la relación con una constructora. Ningún proveedor boliviano encontrado anuncia D5 Render con mejora por IA, así que tu flujo de trabajo es un diferenciador aunque no se cobre aparte."),

  h1("5. Impuestos y forma de pago"),
  bullet("**Sin factura:** CBI debe retener impuestos del pago. Según la fuente, la retención es de **15,5 %** (IUE 12,5 % + IT 3 %) o de **16 %** (RC-IVA 13 % + IT 3 %). De Bs 10.000 recibirías Bs 8.400–8.450."),
  bullet("**Con factura** (necesitas NIT): pagas IVA 13 % + IT 3 %. Para recibir lo mismo facturarías ≈ Bs 10.060, es decir, el mismo precio de Bs 10.000. A CBI le conviene la factura porque recupera el 13 % como crédito fiscal."),
  bullet("**Ley 1733 (IVA por fuera):** cambia el IVA a 13 % sumado al precio, pero recién rige cuando salga su decreto reglamentario. Confírmalo antes de facturar."),
  bullet("**Moneda:** cotiza en **bolivianos**, con el equivalente en dólares solo como referencia. El dólar oficial ahora flota: en septiembre de 2026 varió entre Bs 11,53 y Bs 12,64. Pon una **validez de 15 días** a la cotización."),

  h1("6. Condiciones recomendadas para tu primer trabajo"),
  numbered("cond", "**Anticipo del 50 %** al firmar y el saldo contra la entrega final. Es lo habitual en la región."),
  numbered("cond", "**Dos rondas de cambios** incluidas por imagen: color, materiales y encuadre. Los cambios de proyecto, es decir, modificaciones al modelo Revit, se cobran aparte a Bs 40 por hora."),
  numbered("cond", "**Guion de cámaras aprobado antes del video.** Envía a CBI una versión rápida de baja calidad (animatic) y renderiza el video final solo cuando esté aprobada. Cada cambio posterior obliga a renderizar de nuevo."),
  numbered("cond", "**Plazo de 5 a 6 semanas** desde la entrega del modelo Revit. Al ser la primera vez, deja margen."),
  numbered("cond", "**Derecho a portafolio:** pide por escrito permiso para mostrar las imágenes y el video en tu portafolio y redes. Para un primer trabajo vale tanto como el pago."),
  numbered("cond", "**Precio de lanzamiento visible:** conviene presentar el precio como \"precio especial de primer proyecto\". Por ejemplo: precio de lista Bs 13.000, descuento de lanzamiento del 23 %, total Bs 10.000. Así tu siguiente cotización no parte de Bs 10.000."),
  numbered("cond", "**Fidelidad al proyecto:** usa la IA solo en texturas, vegetación, cielo y personas. Revisa cada imagen contra el modelo Revit y guarda la versión sin IA."),
  numbered("cond", "**No incluido:** archivos fuente (escena D5, PSD por capas) y cambios de diseño del proyecto. La música debe ser de una biblioteca con licencia comercial."),
  ...callout([[
    new TextRun({ text: "Licencia de D5 Render. ", bold: true, color: WARN, font: FONT }),
    ...runs("Según D5, la versión gratuita (Community) no permite trabajo comercial ni remunerado. Además, las fuentes no coinciden sobre si limita la salida a 1080p, y los recursos de la biblioteca Pro dejan marca de agua. Los gastos de la sección 3 ya incluyen **2 meses de D5 Pro (Bs 914)**. Si usas Community, ahorras ese monto pero asumes el riesgo de incumplir la licencia en un proyecto que CBI presentará públicamente."),
  ]], { color: WARN, fill: WARN_SOFT }),

  h1("7. Antes de enviar la cotización, verifica"),
  numbered("verif", "Licencia y límites de salida de D5 Community en d5render.com/pricing."),
  numbered("verif", "El tipo de cambio oficial del día en el sitio del BCB (bcb.gob.bo)."),
  numbered("verif", "Con un contador: si la retención es de 15,5 % o 16 %, y si ya rige la Ley 1733."),
  numbered("verif", "**Haz una prueba con el modelo real:** cronometra una imagen completa y 20 segundos de video. Si una imagen te toma mucho más de 6 horas, ajusta el precio o el número de vistas."),
  numbered("verif", "Con CBI: número exacto de vistas, duración del video, si necesitan factura y la fecha límite de presentación."),
  ...callout([runs("**Nota de método.** Este documento es un resumen orientado a un primer trabajo; el estudio completo está en el repositorio. La red bloqueó la lectura directa de casi todas las páginas consultadas, así que la mayoría de las cifras salen de resúmenes de buscadores que apuntan a las fuentes citadas. Las horas de trabajo, el precio del equipo y los márgenes son estimaciones propias, no datos publicados.", { size: 16 })]),

  h2("Fuentes principales"),
  link("ARQUINEX, paquetes de renders para tesis", "https://enixnicole.wixsite.com/arquinex-bo/post/servicio-de-renders-proceso-de-trabajo"),
  link("D5 Render, planes y precios 2026", "https://www.d5render.com/posts/render-pricing-d5-plans"),
  link("D5 Render, uso comercial de Community", "https://forum.d5render.com/t/community-liscence-commercial-use/27606"),
  link("Banco Central de Bolivia, tipo de cambio al 30-09-2026", "https://x.com/BancoCentralBO/status/2105276469060735163"),
  link("Salario mínimo 2026 (DS 5516)", "https://unitel.bo/noticias/economia/decreto-el-salario-minimo-sube-a-bs-3300-su-aplicacion-es-obligatoria-y-rige-desde-el-2-de-enero-de-2026-CM18639182"),
  link("Sueldos de arquitecto junior en Bolivia (Paylab)", "https://www.paylab.com/bo/salarios/construccion-e-inmobiliaria/arquitecto-junior?lang=es"),
  link("Freelancers de 3D rendering en Bolivia", "https://www.freelancer.com/job-search/online-3d-rendering-jobs-bolivia/"),
  link("Estudio LAT, Argentina", "https://www.estudiolatarq.com/precios/"),
  link("Arca Digital, Colombia", "https://arquitectura.arcadigital.co/precios/"),
  link("Crossmind, Chile", "https://www.crossmind.cl/post/cuanto-cuesta-un-render-3d"),
  link("Retenciones por servicios sin factura", "https://boliviaimpuestos.com/retenciones-por-servicios-ejemplo-practico/"),
  link("RC-IVA e IUE para profesionales", "https://boliviaimpuestos.com/rc-iva-iue-profesionales/"),
  link("Ley 1733, IVA por fuera", "https://boliviaimpuestos.com/iva-por-fuera-ley-1733/"),
  link("Krea, precios y licencia comercial", "https://www.krea.ai/pricing"),
];

const doc = new Document({
  creator: "Estudio de costos",
  title: "Estudio de costos de renderizado – Terminal de buses de Tupiza",
  styles: {
    default: { document: { run: { font: FONT, size: 19, color: "1D2329" }, paragraph: { spacing: { line: 276 } } } },
    paragraphStyles: [
      { id: "PiePagina", name: "Pie de página", basedOn: "Normal", run: { font: FONT, size: 15, color: "7A7F85" } },
      { id: "Title", name: "Title", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 40, bold: true, color: ACCENT }, paragraph: { spacing: { after: 80 } } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 25, bold: true, color: ACCENT },
        paragraph: { spacing: { before: 320, after: 120 }, keepNext: true, outlineLevel: 0,
          border: { bottom: { style: BorderStyle.SINGLE, size: 10, color: ACCENT, space: 3 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 21, bold: true, color: "1D2329" },
        paragraph: { spacing: { before: 200, after: 80 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 360, hanging: 240 } } } }] },
      ...["cond", "verif"].map((reference) => ({ reference, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 360, hanging: 300 } } } }] })),
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1000, bottom: 1000, left: 1000, right: 1000, footer: 500 } } },
    footers: {
      default: new Footer({ children: [new Paragraph({
        style: "PiePagina",
        tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }],
        children: [
          new TextRun({ text: "Estudio de costos de renderizado · Terminal de buses de Tupiza", size: 15, color: "7A7F85", font: FONT }),
          new TextRun({ children: [new Tab(), "Pág. "], size: 15, color: "7A7F85", font: FONT }),
          new TextRun({ children: [PageNumber.CURRENT], size: 15, color: "7A7F85", font: FONT }),
          new TextRun({ text: " de ", size: 15, color: "7A7F85", font: FONT }),
          new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 15, color: "7A7F85", font: FONT }),
        ],
      })] }),
    },
    children,
  }],
});

const out = path.join(__dirname, "..", "Estudio de costos renderizado Tupiza.docx");
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log("Escrito:", out); });
