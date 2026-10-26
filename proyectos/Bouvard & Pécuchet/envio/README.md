# Envío a Astrágalo A44

Entregables del envío, armados el 26 de octubre de 2026 sobre el Borrador 0 del 24 de octubre. Todo es provisional hasta que el borrador cierre (falta el apartado 5) y nada se envió a la revista.

## Qué hay

| Archivo | Qué es | Estado |
|---|---|---|
| `docx/Lo posible y lo_Cuevas Ventura.docx` | Versión con autoría, sobre la plantilla oficial | Se regenera con `armar_docx.py` |
| `docx/Lo posible y lo_anonimo.docx` | Versión anónima para el doble ciego: sin nombre, filiación ni CV, pies sin «del autor», propiedades del archivo vacías | Ídem |
| `Resúmenes.md` | Resumen, abstract y resumo, de 229 a 240 palabras, con palabras clave del Tesauro de la UNESCO | Falta la frase del resultado del apartado 5 |
| `Declaración de uso de IA.md` | Declaración según la política de la revista (software, funciones, secciones), y una versión corta para OJS | Faltan versiones de modelos, fechas y qué reescribió el autor |
| `Referencias revisadas.md` | Revisión en Chicago autor-fecha 17.ª y lo que el borrador adoptó; la lista vive en el borrador | Faltan dos URL y ver el facsímil de Conard |
| `referencias.ris` | La misma lista para Zotero (no es obligatorio) | — |
| `Figuras - pies, créditos y permisos.md` | Pies según las normas, permisos y requisitos técnicos | Faltan las figuras redibujadas a 16 × 10 cm |
| `Datos de autor.md` | Nombre, filiación, ORCID y breve CV en tres idiomas | Faltan filiación, correo, ORCID y dos frases del CV |
| `armar_docx.py` | Arma las dos versiones desde el borrador y estos archivos | — |

## Cómo se regeneran los .docx

```sh
python3 armar_docx.py            # usa ../articulo/Borrador 0.md, la plantilla y las láminas de la carpeta del proyecto
python3 armar_docx.py BORRADOR PLANTILLA LAMINAS SALIDA
```

Hace falta `python-docx`. El programa no cambia el borrador. Lo que hace al pasar:

- Formato de las normas: A4 con márgenes de 2 y 2,5 cm (la plantilla trae 1,5 cm abajo; las normas dicen 2), Calibri 10 justificado con 6 pt después, resúmenes en 9, pies, tablas y referencias en 8, títulos sin negrita en el texto y con numeración «2.1.».
- Comillas « » → “ ”, y ‘ ’ dentro de otras (normas, §7). «(Fig. 1)» → «(Fig. 1.)».
- Las **negritas** del borrador pasan a cursiva (las normas no admiten negritas en el texto).
- Las notas de trabajo entre corchetes ([FALTA], [POSIBLE], [ESQUELETO] y los huecos de los datos) van en gris, como dice el borrador.
- Los pies de figuras y tablas salen de `Figuras - pies, créditos y permisos.md`, no del borrador. Las figuras son las láminas de trabajo, a 10 cm de alto, como marcador.
- Saca de la plantilla el encabezado «Normas de presentación», la imagen de ejemplo, la miniatura y las preferencias de Zotero que traía (de Chicago 16.ª).

## Lista de comprobación

Contra las normas y la [lista de requisitos](https://claude.ai/code/artifact/5516bebb-953b-4b6a-ba0d-ad7fc634186e).

- [x] Dos archivos .docx, con autoría y anónimo, con los nombres que piden las normas.
- [x] Formato de página, letra y párrafos de la plantilla.
- [x] Tres resúmenes de 250 palabras o menos, el del idioma del texto primero, con palabras clave (provisionales).
- [x] Declaración de uso de IA (falta completarla).
- [x] Referencias en Chicago autor-fecha 17.ª, con DOI o URL donde se pudo.
- [x] Anonimato: sin nombre, sin CV, sin autocitas, propiedades del archivo vacías.
- [ ] Apartado 5 con datos, y la frase del resultado en los tres resúmenes.
- [ ] Largo: hoy el borrador tiene unas 7.000 palabras de texto y 660 de referencias (8.950 contando las notas de trabajo). Si la revista cuenta también los resúmenes, son 700 más: preguntarlo o dejar margen.
- [ ] Figuras redibujadas a 16 × 10 cm como máximo, a 300 ppp, también aparte como `FIG1.jpg`…`FIG4.jpg`. Las Fig. 1 y 4 con las hojas del atlas a resolución completa.
- [ ] Lectura humana de la Tabla 2.
- [ ] Datos de autor completos e idénticos al perfil de OJS (con ORCID).
- [ ] Una sola variante del español en todo el texto.
- [ ] Decidir si se quitan dos pistas de autoría en el anónimo («para quien viene del diseño gráfico», «desde La Paz»).
- [ ] En OJS: registrar la cuenta, indicar el número A44, marcar la lista de comprobación y pegar la declaración de IA en los comentarios al editor.
