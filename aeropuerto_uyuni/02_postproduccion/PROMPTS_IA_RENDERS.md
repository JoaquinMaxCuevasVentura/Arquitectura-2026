# Postproducción con IA: prompts por vista

**Objetivo:** convertir las 7 vistas del modelo en fotografías creíbles para la reunión, sin rediseñar el edificio.
- **Se mantiene:** la composición, la geometría y el diseño.
- **Se agrega:** cámara real, materiales, cielo, paisaje, gente y vehículos.

Los prompts están en inglés: la mayoría de los modelos de imagen siguen con más precisión los términos fotográficos en ese idioma.

---

## 1. Cómo sacarles el máximo

1. **Partir de la mejor base posible.**
   - Usa los renders finales en 4K con GPU: la IA amplifica el ruido de las vistas previas de 1280 px y 24 muestras.
   - Si solo tienes las vistas previas, escálalas primero ×2 con un upscaler de creatividad baja.
2. **Trabajar en tres pasadas, no en una.**
   - **Pasada 1, realismo global:** prompt completo con fuerza baja.
   - **Pasada 2, agregados por zonas:** personas, vehículos y paisaje, con máscara o inpainting.
   - **Pasada 3, terminación:** escalado ×2 con creatividad baja y la misma corrección de color para las 7 imágenes.
   - Si en la pasada 1 la IA toca la arquitectura, quita el párrafo **Add** y pásalo como una segunda edición.
3. **Ajustes de referencia.**
   - **Editores por instrucciones** (edición de imagen de ChatGPT, Gemini u otros): sube la imagen y pega el prompt. Si cambia algo del edificio, repite con *"Only make these changes; everything else must stay pixel-identical"*.
   - **Difusión con ControlNet** (Krea, ComfyUI con Flux o SDXL):
     - pasada global: denoise 0,30–0,40 · ControlNet Depth 0,6–0,8 + Lineart/Canny 0,5–0,7 · CFG 4–6;
     - inpainting de personas y vehículos: denoise 0,60–0,75, solo dentro de la máscara.
   - **Upscalers:** creatividad mínima y parecido (*resemblance*) alto.
   - **Photoshop:** con el Relleno generativo, selecciona solo el suelo, el cielo o la acera para insertar gente y autos. Al final aplica la misma corrección en Camera Raw a las 7 imágenes: perfil, temperatura, curvas suaves y grano de 10 a 15.
4. **Control antes de presentar.** Pon el resultado sobre el render original en modo **Diferencia**: cualquier cambio en el edificio aparece de inmediato. Revisa en especial:
   - las letras UYUNI y su reflejo espejado;
   - el patrón andino de las celosías;
   - la cantidad de columnas y de paños;
   - los rombos y las barras retenedoras.

### Prompt negativo (para las herramientas que lo aceptan)

```
CGI, 3D render look, video game, cartoon, plastic or clay textures, oversaturated colors, HDR halos, over-sharpening, warped or bent lines, changed architecture, extra or missing columns, extra windows, changed mullion layout, altered or misspelled letters, corrected or flipped mirrored text, simplified or changed panel pattern, melted geometry, deformed people, extra limbs, duplicated people, crowd, people at wrong scale, floating or distorted vehicles, snowstorm, fog, lens flare, heavy vignette, fisheye, tilt-shift miniature effect, watermark, logo, text overlay
```

## 2. Luz y cámara de cada vista

Los datos salen del modelo:
- **Día:** sol del 4 de octubre a las 09:30, con azimut 73,6° y elevación 46,5°.
- **Crepúsculo:** atardecer al oeste (azimut 264°).

Así, las sombras que agregue la IA coinciden con las del render.

| Vista | Lente (como en Blender) | De dónde viene la luz | Gente y vehículos |
|---|---|---|---|
| CAM_01 Hero | 32 mm, altura de ojos (1,65 m) | Sol a la izquierda y algo adelante, a 45° | Viajeros bajo el alero; minibús y Land Cruiser junto al bordillo; otro 4x4 en el carril lejano |
| CAM_02 Alero | 35 mm, desde 10 m | Sol detrás de la cámara, a la derecha | Pocas personas abajo, vistas desde arriba |
| CAM_02B Cielo | 21–22 mm, mirando hacia arriba | Sol detrás, a la derecha; el cielo raso en sombra | Un viajero entrando por el borde inferior izquierdo |
| CAM_03 Hora azul | 24 mm, trípode, 6 s | Resplandor del atardecer abajo, a la derecha | Viajeros "fantasma"; 4x4 a la izquierda; minibús; estelas de luz |
| CAM_04 Aérea | 35 mm equivalentes, dron | Sol casi exactamente detrás del dron | Vehículos en el estacionamiento y personas diminutas |
| CAM_05 Letrero | 40 mm, desde 4 m | Sol detrás, a la izquierda | **Sin gente**: el cuadro empieza a ≈ 3,4 m de altura |
| CAM_06 Celosía | 28 mm, a 2 m | Sol casi exactamente detrás de la cámara | Un viajero pasando, sin tapar el rombo central |

## 3. Prompts

Cada vista tiene una versión completa, para editores por instrucciones y Flux, y una versión corta, para herramientas con límite de texto o upscalers.

### CAM_01_HERO_LADO_TIERRA

```
Transform this 3D render into a real architectural photograph. Keep the exact composition, viewpoint and perspective, and do not alter the architecture: building volume, column rhythm, glazing with black mullions, the diamond window, the chocolate-brown ribbed parapet with the white UYUNI letters and the mirrored outline letters below them (intentional reflection, do not correct), the white perforated triangles on the thin horizon line, and the rust corten screens on the right with their exact Andean cut-out pattern and zigzag top.
Uyuni airport, Bolivian altiplano at 3,667 m, October, 9:30 a.m.: dry, crystal-clear air, deep blue sky with a few thin high cirrus, hard sunlight from the left at about 45°, crisp shadows; the screens cast their perforated pattern onto the wall behind them.
Full-frame camera on a tripod, 32 mm lens, eye level, perfectly vertical lines, f/11, ISO 64, 1/30 s with ND filter, 5600 K: architecture tack-sharp, walking people with slight natural motion blur.
Real materials: satin pre-painted brown steel with fine dust, weathered corten with uneven patina and faint rust streaks, cream fiber-cement panels with crisp joints, exposed concrete columns with subtle formwork marks, blue-silver solar-control glass reflecting the sky with a warm, softly lit check-in hall behind, brushed concrete sidewalk, asphalt with fine aggregate and tire marks.
Add: a few travelers walking under the canopy toward the entrances with rolling suitcases and trekking backpacks, in down jackets, beanies and scarves; a guide with a small group; a staff member in a hi-vis vest; two local women in everyday traditional Andean dress (pollera, bowler hat, aguayo), natural and respectful. At the curb in the middle distance, a white tourist minibus unloading luggage and a white Toyota Land Cruiser 4x4 with a roof rack loaded with luggage under a blue tarp; another Land Cruiser approaching in the far lane. Keep the corten screens unobstructed. Beyond the building's left end: flat altiplano with pale gravel, golden paja brava grass tufts and distant ochre mountains in light haze.
Sober, elegant editorial architecture photography, natural colors, fine film grain, no HDR look.
```

Versión corta:
```
photorealistic architectural photograph, airport terminal in the Bolivian altiplano, chocolate-brown metal parapet with white UYUNI letters and mirrored outline letters, rust corten perforated screens, glass facade, 9:30 am hard sun from the left, deep blue sky, travelers with suitcases, white Land Cruiser with roof rack, 32mm f/11, natural colors
```

### CAM_02_DETALLE_ALERO

```
Transform this 3D render into a real close-range construction photograph taken from a lift about 10 m high. Keep the exact composition and perspective and do not alter any geometry: the chocolate-brown standing-seam roof with seams every 30 cm, the double galvanized snow-guard tubes and their clamps along the edge, the drip edge, the vertical-ribbed brown parapet, the columns and glazing below and the white sign at the far end.
Uyuni, Bolivian altiplano at 3,667 m, October, 9:30 a.m.: sun behind the camera on the right, clear deep blue sky, hard light; thin specular highlights along every seam, satin sheen with fine dust and faint water marks on the steel.
Subtle weather detail: remnants of last night's light snowfall, thin crusts of snow and frost caught against the snow-guard bars and in the seam valleys, a few small icicles on the drip edge, slightly melting. No falling snow, no fog.
Full-frame camera, 35 mm, f/11, ISO 100, 1/500 s, sharp from front to back with gentle atmospheric falloff toward the far end.
Below, on the sidewalk, a few small travelers with suitcases seen from above, the black bollards and the edge of the corten screen.
Precise, elegant construction-detail photograph, natural colors, true metal textures, no CGI look.
```

Versión corta:
```
photorealistic construction detail photo, chocolate-brown standing-seam metal roof edge with double galvanized snow-guard bars, thin snow and frost remnants on the bars, ribbed brown parapet, morning sun from behind, deep blue sky, 35mm f/11, natural colors
```

### CAM_02B_DETALLE_CIELO

```
Transform this 3D render into a real architectural photograph looking up from the sidewalk. Keep the exact strong upward wide-angle perspective and framing, and do not alter any element: the champagne aluminum linear-slat soffit under the 2 m canopy with its small recessed downlights, the exposed concrete columns, the full-height glazing with black matte mullions and transoms, the chocolate-brown ribbed parapet edge and the sky.
Uyuni, Bolivian altiplano, October, 9:30 a.m.: sun behind the camera on the right, deep blue sky; the soffit in soft open shade with warm light bounced from the sidewalk.
Real materials: smooth cast-in-place concrete with subtle formwork marks and a slightly darker, dusty base; slats with fine linear reflections and real joints; cream fiber-cement panels with crisp joints; solar-control glass with a slight blue-silver tint reflecting the sky and the street, and behind it a warm, softly lit check-in hall with travelers, counters and pendant lights.
Full-frame camera, 21 mm rectilinear lens, f/8, ISO 100, 1/60 s, everything sharp; one traveler pulling a suitcase partly entering the lower left edge, slightly motion-blurred.
Crisp, elegant detail photograph, natural colors, true-to-life reflections, no CGI look, no HDR.
```

Versión corta:
```
photorealistic worm's-eye architectural photo, champagne aluminum linear slat soffit, exposed concrete columns, tall glass facade with black mullions, warm lit check-in hall inside, deep blue sky, 21mm f/8, natural colors
```

### CAM_03_CREPUSCULAR_NIEVE

```
Transform this 3D render into a real blue-hour architectural photograph. Keep the exact frontal composition, perspective, facade layout and light pattern: the warm glowing glazed bays, the warm downlights under the canopy, the white UYUNI letters with the mirrored outline letters below them (intentional reflection, do not correct), the white perforated triangles on the horizon line, and the corten screens on the right washed with warm light from below.
Uyuni airport, Bolivian altiplano at 3,667 m, early October, about 20 minutes after sunset: clear, cold, deep cobalt sky with a last warm glow low on the right horizon.
The concept is the mirror of the Salar: wet asphalt and shallow puddles after melting snow reflect the lit facade like a mirror, exactly where the input shows reflections. Thin snow remnants along the curbs, on the roof edge and snow guards, and on the roofs of parked cars.
Tripod, full-frame camera, 24 mm, f/8, ISO 100, 6 s exposure, white balance 4300 K: travelers with suitcases under the canopy as soft motion-blurred ghosts; a white Toyota Land Cruiser 4x4 with a loaded roof rack parked at the left edge of the frame; a white minibus with a lit interior at the curb near the entrance; faint red and white light trails of a vehicle passing on the road; faint exhaust vapor in the cold air.
Calm, elegant, natural night photography; warm interior against the black exterior profiles; no extra light sources, no lens flare, no oversaturation.
```

Versión corta:
```
photorealistic blue hour architectural photograph, airport terminal, warm glowing glass facade, white UYUNI sign with mirrored outline letters, wet asphalt mirror reflections, thin snow remnants, travelers motion blur, white Land Cruiser, 24mm f/8 6s, cobalt sky, natural colors
```

### CAM_04_AEREA_GENERAL

```
Transform this 3D render into a real aerial drone photograph. Keep the exact composition, height and angle, and do not alter the architecture: the long chocolate-brown standing-seam roof with its edge snow guards, the ribbed brown parapet with the white sign, the glazed landside facade, the rust corten screens at both ends, the lower annex, the road with its lane line, the curb, sidewalk, bollards and the parking with white stall lines.
Replace the flat beige ground with the real altiplano around Uyuni at 3,667 m: a wide, flat plain of pale gravel and dusty ochre soil with scattered golden paja brava tufts, a few dirt tracks and faint whitish salt-crust patches, plus a simple perimeter fence; behind the building, the concrete airside apron. The plain continues to the top edge of the frame: no sky, no other tall buildings.
Life at true scale: white Toyota Land Cruiser 4x4s with loaded roof racks and two white tourist minibuses parked in the lot and at the curb, one vehicle driving on the road, and small travelers with luggage near the entrances.
October, 9:30 a.m., sun almost directly behind the drone, crystal-clear air with slight haze in the distance, crisp shadows falling away from the camera.
Drone camera, 35 mm equivalent, f/5.6, ISO 100, 1/1000 s, sharp throughout; the roof shows real metal sheen and fine dust.
Clean, sober overview photograph, natural colors, no miniature or tilt-shift effect, no fisheye.
```

Versión corta:
```
photorealistic aerial drone photo, airport terminal with long chocolate-brown standing-seam roof, white sign on brown parapet, rust corten screens, altiplano plain with pale gravel and golden grass tufts, parking with white Land Cruisers and minibuses, morning sun behind camera, 35mm f/5.6, natural colors
```

### CAM_05_LETRERO_HORIZONTE

```
Transform this 3D render into a real architectural photograph of the sign. Keep the exact frontal composition and scale and do not alter any element: the chocolate-brown vertical-ribbed metal parapet; the white UYUNI letters and, below the thin white horizon line, their mirrored outline letters (intentional reflection concept: do not correct, flip or re-letter them); the three white diamond motifs, each a perforated triangle above the line and its outline reflection below; the canopy edge, columns and glazing below; the snow-guard bars along the roof edge at the top.
Uyuni, Bolivian altiplano, October, 9:30 a.m.: sun behind the camera on the left, deep blue sky with a few thin cirrus; the letters stand 10 cm off the panel and cast crisp shadows on the ribs.
Real materials: white powder-coated aluminum letters with clean edges and a slight satin sheen; perforated white triangles showing the brown panel through the round holes; brown pre-painted steel with fine ribs and light dust; glass below reflecting the sky with a warm interior behind.
Full-frame camera, 40 mm lens from a lift at 4 m, perfectly frontal, parallel verticals, f/8, ISO 100, 1/250 s, everything sharp.
Crisp, elegant signage photograph, natural colors, no glow on the letters in daylight, no people.
```

Versión corta:
```
photorealistic frontal photo of a building sign, white UYUNI letters with mirrored outline letters below a thin horizon line, white perforated triangles, chocolate-brown ribbed metal parapet, crisp letter shadows, morning sun, deep blue sky, 40mm f/8, natural colors
```

### CAM_06_DETALLE_CELOSIA

```
Transform this 3D render into a real architectural detail photograph. Keep the exact composition and perspective and do not alter any element: the rust corten perforated screen with its exact Andean cut-out pattern (circles, triangles, nested diamonds) and zigzag top, mounted 12 cm in front of the wall on a dark steel frame; the black-framed diamond window on the cream fiber-cement wall at left; the concrete column; the brown parapet above; the black bollards and the sidewalk.
Uyuni, Bolivian altiplano, October, 9:30 a.m.: hard sun almost directly behind the camera, deep blue sky; the perforations project a sharp pattern of light spots onto the cream wall behind the screen.
Real materials: weathered corten with uneven orange-to-dark-brown patina and slight roughness, visible plate joints on the 1 x 2 m grid, faint rust run-off stains on the concrete sidewalk below the screen; cream fiber-cement panels with crisp joints; smooth concrete column; matte black steel bollards with light dust.
Full-frame camera, 28 mm, f/8, ISO 100, 1/60 s, focus on the screen, the nearest bollard slightly soft; one traveler with a trekking backpack walking past the left part of the screen, slightly motion-blurred, at true scale (the screen is 6 m tall), not covering the central diamond motif.
Tactile, elegant material close-up, natural colors, no CGI look.
```

Versión corta:
```
photorealistic close-up architectural photo, weathered corten steel perforated screen with Andean geometric cut-outs and zigzag top, light pattern projected on cream wall, black-framed diamond window, black bollards, morning sun, deep blue sky, 28mm f/8, natural colors
```

## 4. Lista de control final

- [ ] La composición coincide con el render: superposición en modo Diferencia sin cambios en el edificio.
- [ ] UYUNI se lee bien y el reflejo inferior sigue espejado.
- [ ] El patrón de las celosías y su borde en zigzag no cambiaron.
- [ ] Sombras coherentes con la tabla de la sección 2. En CAM_03, el resplandor queda a la derecha.
- [ ] Personas y vehículos a escala: persona ≈ 1,7 m, Land Cruiser ≈ 4,9 m de largo. Ninguno tapa las celosías ni el letrero.
- [ ] Las 7 imágenes tienen el mismo cielo, la misma hora, los mismos vehículos y la misma gradación de color.
