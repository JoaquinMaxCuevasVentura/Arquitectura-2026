# Upscale con IA de los renders de las dos propuestas

**Objetivo:** llevar los renders de `CAM_07_PROPUESTAS` (4K, 16 bits) a ×2 (7680 × 4320) con un modelo de red neuronal.
- **Se agrega:** microdetalle fotográfico.
- **No se cambia nada del diseño:** geometría, colores, letrero ni encuadre.

Los mismos prompts sirven para los primeros planos del letrero (`CAM_05_LETRERO_HORIZONTE`).

Los prompts están en inglés porque los upscalers siguen mejor los términos fotográficos en ese idioma. Agregar gente, vehículos o nubes es otra pasada, con `PROMPTS_IA_RENDERS.md`, y conviene hacerla **después** del upscale.

## Datos de los renders (para que la IA no contradiga la luz)

| Dato | Valor |
|---|---|
| Cámara | 28 mm, a 6,0 m de altura y 43 m del frente, cámara horizontal (verticales rectas) |
| Luz | Sol del 4 de octubre a las 09:30 (elevación 46,5°), **arriba a la izquierda y apenas detrás de la cámara**: las sombras de letras, columnas y celosías caen hacia la derecha y hacia abajo |
| Cielo | Altiplano a 3667 m, despejado, azul profundo arriba y más claro en el horizonte |
| Calle | Vacía a propósito (los proxies de vehículos y personas no se renderizan) |

## Ajustes por herramienta

| Herramienta | Ajustes |
|---|---|
| **Magnific** (Freepik) | ×2 · *Optimized for* **3D Renders** · motor **Sharpy** · Creativity **0 a +1** · HDR **+1** · Resemblance **+5 a +7** · Fractality **−1**. Si inventa detalles, baja Creativity a −2 antes de tocar el prompt. |
| **Topaz Gigapixel** | Modelo **High Fidelity** (no generativo) o **Redefine** con Creativity **1–2** y Texture **1**. El prompt solo se usa en Redefine. |
| **Krea Enhance** | ×2 · fuerza de IA **≤ 0,2** · *resemblance* alto · nitidez media. |
| **ComfyUI** (SUPIR o Flux + ControlNet Tile) | **SUPIR:** CFG 4 y 30–50 pasos. **Flux:** Ultimate SD Upscale en mosaicos de 1024 px con 128 de solape, denoise **0,25–0,35** y ControlNet Tile **0,7**. Prompt positivo y negativo de abajo. |
| **Leonardo** (Universal Upscaler) | Creatividad **baja** · detalle medio · estilo **Realistic**. |

**Siempre:**
- Exporta en PNG o TIFF, nunca en JPG intermedio.
- Escala las dos propuestas con exactamente los mismos ajustes, para que la comparación sea justa.

## Prompt base (las dos propuestas)

> Este prompt es para los renders de las propuestas del 3 y 4 de octubre, que tienen la carpintería antracita. Desde la noche del 4 de octubre la carpintería es **negro mate**: para los renders nuevos, cambia "matte anthracite aluminum window and door frames" por "matte black powder-coated aluminum window and door frames".

```
Faithful 2x upscale of an architectural photograph: a new single-story airport passenger terminal on the Bolivian Altiplano (Uyuni, 3,660 m). Keep every line, proportion, color, object and the framing exactly as in the input; only add true photographic micro-detail and clarity.
Clear, dry morning at 9:30. Crisp high-altitude sunlight from the upper left, slightly behind the camera; sharp natural shadows falling to the right. Deep cobalt-blue sky that grades lighter toward the horizon, clean and cloudless.
Full-frame camera, 28 mm lens, f/8, ISO 100, tripod, straight verticals, natural micro-contrast, very fine film grain, true-to-life color.
Refine the materials: continuous sand-float cement plaster on walls and columns (fine aggregate texture, subtle hand-applied variation, one thin horizontal reveal at beam level, no panel joints); standing-seam metal roof and parapet with straight, crisp vertical ribs; matte anthracite aluminum window and door frames; solar-control double glazing with soft sky reflections and a hint of interior depth; asphalt with fine aggregate, crisp white lane paint and faint tire marks; broom-finish concrete sidewalk and curb; dry beige altiplano ground at the edges.
```

## Añadido para la propuesta 1: Patrimonio Ferroviario

```
Perforated weathering-steel (Cor-Ten) screens with an Andean geometric cut pattern: warm rust-orange to copper patina, mottled oxidation, slightly darker run-off streaks at the lower edges, matte surface, razor-clean cut edges.
"UYUNI" sign in Cor-Ten 3D letters floating 12 cm off a matte dark anthracite ribbed parapet, casting sharp detached shadows on the ribs; faceted Cor-Ten salt-mound pyramids (one face lit, one in shade) sitting on a thin horizontal horizon bar, with the upside-down mirrored outline reflection of the word and of the triangles below it.
Warm wood-look aluminum slatted soffit over a black void. Charcoal-anthracite standing-seam roof. Light neutral concrete-colored plaster walls.
```

## Añadido para la propuesta 2: Salar & Litio

```
Pearl-white powder-coated perforated screens with the same Andean geometric cut pattern, clean edges, very subtle satin sheen, no rust.
White ribbed parapet with white 3D letters "UYUNI" floating 12 cm off it, legible through their crisp cast shadows; faceted white salt-mound pyramids (one face lit, one in shade) on a thin horizon bar, with the upside-down mirrored outline reflection of the word and of the triangles below it.
White slatted soffit over a black void. Light silver-grey standing-seam roof. Walls and columns in a continuous neutral mid-grey plaster that makes the white elements stand out.
```

## Cierre (pegar siempre al final)

```
Do not change: the word "UYUNI" and its upside-down mirrored outline reflection (do not correct, flip or re-letter it), the number and position of the salt-mound pyramids, the horizon bar, every column, window, door and mullion, the perforation pattern of the screens, the camera angle and the empty street. Do not add people, vehicles, trees, clouds or text.
```

## Prompt negativo (si la herramienta lo acepta)

```
CGI look, plastic, clay, cartoon, painting, oversharpening, halos, HDR glow, noise, blotchy textures, warped or curved lines, melted edges, changed architecture, extra or missing columns or windows, altered or misspelled letters, corrected or flipped mirrored text, extra pyramids, distorted perforation pattern, people, cars, trees, clouds, lens flare, watermark, text overlay
```

## Versión corta (herramientas con límite de caracteres)

Propuesta 1:
```
Faithful 2x upscale, architectural photo, airport terminal on the Bolivian Altiplano, clear 9:30 morning, sun upper left, deep blue sky, 28 mm f/8, straight verticals. Fine plaster texture, crisp standing-seam ribs, rusty Cor-Ten perforated screens and Cor-Ten 3D letters "UYUNI" floating over a dark anthracite parapet with sharp shadows. Keep all geometry, text and colors unchanged.
```

Propuesta 2:
```
Faithful 2x upscale, architectural photo, airport terminal on the Bolivian Altiplano, clear 9:30 morning, sun upper left, deep blue sky, 28 mm f/8, straight verticals. Fine grey plaster texture, crisp standing-seam ribs, pearl-white perforated screens and white 3D letters "UYUNI" floating over a white parapet, read through sharp shadows. Keep all geometry, text and colors unchanged.
```

## Control antes de presentar

1. Reduce la imagen escalada al 50 %, colócala sobre el render original en modo **Diferencia** y revisa que el edificio quede en negro. Lo que cambió aparece en claro.
2. Revisa con zoom al 100 %:
   - las letras UYUNI y su reflejo invertido;
   - las pirámides: tres sobre la puerta de salida y el resto en el letrero principal;
   - el patrón de las celosías;
   - las columnas, los paños de vidrio y los marcos;
   - el retenedor de nieve, que es un doble tubo fino.
3. Compara las dos propuestas lado a lado: deben diferir **solo** en los colores y materiales que define cada una.
