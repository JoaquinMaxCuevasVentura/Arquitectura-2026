# Consolidar: entregables, dependencias y calendario

Cierre: **31-01-2027, 24:00**. Hoy es 26-10-2026: quedan unas 14 semanas. Bases en [`../00_encargo/bases.md`](../00_encargo/bases.md).

## De dónde sale cada entregable

| Entregable | Contenido pedido | Sale de | Falta |
|---|---|---|---|
| **Informe** (A4, ≤ 3000 caracteres, IT/EN, sin imágenes) | motivaciones, concepto, materiales | la regla de [`../03_proponer/sintesis.md`](../03_proponer/sintesis.md), el fichero (F01, F08, F09, F11) y los resultados de los ensayos | elegir versión y frase; nombre (O6); traducción al italiano |
| **Lámina 1** | panorama, escenarios, modos de uso, mood board, concepto, fuentes | capturas de dominio público ([`../01_reunir/capturas/`](../01_reunir/capturas/)): Viollet-le-Duc (mesa que se arma), Semper (*Gestell*), Squier (Tiwanaku), Bertonio (*chhakhua*); escenarios: armar, reparar, la junta que cambia con la estación | ⚠️ las 5 referencias visuales tienen **autoría sin verificar**: no usarlas sin averiguarla; mejor fotos propias de las maquetas |
| **Lámina 2** | plantas, alzados, secciones, axonometrías, despieces, planos acotados, detalles de material | láminas SVG del instrumento ([`../03_proponer/laminas/`](../03_proponer/laminas/)), redibujadas sobre la plantilla oficial | **despiece axonométrico**; cotas de construcción finales; detalle 1:1 de clavija y cuña y de collar y llave |
| **Lámina 3** | renders y fotos de maqueta | **modelo paramétrico de Blender** ([`blender/`](blender/), [`renders/`](renders/), generado por [`../instrumentos/blender/`](../instrumentos/blender/README.md), también en GitHub Actions); fotos de las maquetas de E6 y E10 | renders finales a 128 muestras o más, con ambiente interior (como las láminas ganadoras, E7); detalle de las espigas en el modelo |
| **Vista previa** (JPG ≤ 1 MB) | imagen síntesis | el mejor render o la foto del nodo | — |

## Dependencias (lo que bloquea a lo demás)

1. **Visibilidad del repositorio** (bases: inédito y anónimo). Bloquea publicar cualquier cosa del diseño.
2. **E6 (nodo 1:1) y E10 (3 tablas, una semana de uso)**. Deciden entre B2 y AB y si la junta queda vista.
3. **E7 (compendios 2017-2018 y catálogo de Porada)**. Puede obligar a cambiar la unión o el argumento.
4. **Registro en el portal**. Da acceso a la plantilla de láminas: conviene diseñar sobre ella desde el principio.
5. **Consulta a los organizadores**: categoría (neolaureato o profesional) y uso de piedra fuera del catálogo.
6. **Mármol**: muestra y ficha EN 12372 (MOR real). Afecta a K2 si se elige AB.

## Calendario propuesto

| Semanas | Fechas | Movimiento | Hecho cuando… |
|---|---|---|---|
| 1-2 | 27 oct – 9 nov | decidir visibilidad · registrarse · escribir a los organizadores · E7 · encargar retazos de mármol y madera | hay plantilla, respuestas y retazos |
| 3-4 | 10 – 23 nov | construir y probar **E6** y **E10** · leer Bertonio 2011, p. 330 | E6 y E10 respondidos según su prerregistro |
| 5 | 24 – 30 nov | **decidir** B2 o AB, la frase del concepto y el nombre | entrada en la bitácora |
| 6-8 | 1 – 21 dic | desarrollo técnico: cotas, tolerancias, despiece, secuencia de armado, acabados en dos caras | lámina 2 en borrador |
| 9-10 | 22 dic – 4 ene | modelo, renders y fotos de maqueta | láminas 1 y 3 en borrador |
| 11-12 | 5 – 18 ene | informe (IT/EN), vista previa, revisión cruzada contra los criterios del jurado | todo en borrador completo |
| 13 | 19 – 25 ene | control final (lista de abajo) y **subida** | confirmación por correo |
| 14 | 26 – 31 ene | margen. **No dejar la subida para el último día** | — |

## Control final (antes de subir)

- [ ] Código de 6 cifras: sin cifras repetidas más de dos veces, sin secuencias, con prefijo P o S.
- [ ] Nombres de archivo: `report_[código].pdf`, `boards_[código].pdf`, `preview_[código].jpg`.
- [ ] **Ningún nombre** en los materiales: revisar textos, rótulos y **metadatos** (autor en las propiedades del PDF, EXIF del JPG). Por ejemplo: `exiftool -all= archivo`.
- [ ] Láminas: exactamente 3 A3 horizontales en un solo PDF ≤ 5 MB. Vista previa ≤ 1 MB. Informe ≤ 3000 caracteres.
- [ ] Cada afirmación del informe tiene su ficha en el fichero o su ensayo. Nada de lo marcado ⬜ o «a verificar» entra como hecho.
- [ ] Revisión cruzada con los 5 criterios del jurado y la Mención Allievi (artesanía + diseño en el desarrollo estructural).
