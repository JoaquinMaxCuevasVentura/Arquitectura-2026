# Video con Google Flow: prompts por toma

**Objetivo:** pasar a video fotorrealista el recorrido del dron y las vistas renderizadas, con Google Flow (Veo 3.1), sin que la IA cambie el edificio.
- **Se mantiene:** el encuadre, la geometría y el diseño de cada imagen que subes.
- **Se agrega:** movimiento de cámara suave, luz real, viento, y gente y vehículos solo donde no rompen la continuidad.

Los prompts están en inglés: Veo sigue con más precisión los términos de cámara y fotografía en ese idioma.

---

## 1. Cómo funciona y cómo usarlo

### Qué hace Flow con las imágenes

- **Fotograma inicial y final** (*Frames to Video*): subes la primera y la última imagen de la toma. Veo genera el movimiento entre las dos, en un clip de 8 s.
- **Solo fotograma inicial:** Veo anima la imagen durante 8 s a partir de ella.
- **Las imágenes quedan fijas:** el clip arranca y termina exactamente en ellas. Por eso **el video no puede ser mejor que las imágenes que subes**:
  - usa fotogramas renderizados en calidad final (4K o 1080p, con GPU);
  - el borrador de 960 × 540 sirve para elegir los cuadros y revisar el ritmo, no como fotograma clave.
- **Flow no mejora un video subido** (no hay video a video). Se trabaja con fotogramas clave y prompts.

### Ajustes

| Ajuste | Valor |
|---|---|
| Modelo | **Veo 3.1 Quality** para los definitivos; *Fast* para probar |
| Formato | 16:9 |
| Pruebas | en **360p**, que cuesta menos; después la versión final en 1080p y exportación en 4K |
| Variantes | 2 a 4 por toma; quedarse con la que menos toca el edificio |
| Audio | Veo genera sonido: cada prompt pide solo viento. Si vas a poner música, quítalo en la edición |

### Control antes de aceptar un clip

Mira el clip cuadro a cuadro en la mitad, que es donde Veo inventa. Rechaza el clip si:
- cambian las letras UYUNI o su reflejo espejado bajo la línea de horizonte;
- cambia el patrón de las celosías, la cantidad de columnas o la cantidad de paños;
- se doblan los bordes de la cubierta o del parapeto;
- se deforman las jardineras, los anillos blancos, los hexágonos o los cordones amarillos del frente;
- aparecen edificios, carteles o texto que no existen.

Si una toma insiste en deformar algo, acorta el recorrido de la cámara, o agrega un fotograma clave en el medio y divide la toma en dos.

---

## 2. Recorrido del dron (`CAM_DRON`): tres tomas de 8 s

El recorrido dura 600 cuadros (25 s) con lente de 24 mm, en la escena `UYUNI_DIA` (propuesta P1). Se parte en tres tomas que **comparten sus fotogramas clave**: el final de una es el inicio de la siguiente, así empalman sin corte.

| Toma | Fotograma inicial → final | Cámara al inicio | Cámara al final |
|---|---|---|---|
| 1 | 1 → 200 | 55 m de altura, a 160 m, adelante y a la izquierda del edificio | 12 m de altura, frente al extremo izquierdo |
| 2 | 200 → 400 | 12 m | 4,5 m sobre los carriles de llegada, a mitad de la fachada |
| 3 | 400 → 600 | 4,5 m, mitad de la fachada | 36 m, sobre la calle lateral derecha, mirando todo el edificio |

### Fotogramas clave en calidad final

Son solo cuatro imágenes (cuadros 1, 200, 400 y 600). En la PC con GPU, desde la carpeta del repositorio (PowerShell):

```powershell
foreach ($f in 1,200,400,600) {
  blender --factory-startup -b --disable-autoexec 01_blender/uyuni_v2.blend -P 01_blender/herramientas/render_plan.py -- --mode drone --profile final --out 01_blender/renders_video --frame-start $f --frame-end $f
}
```

Salen en `01_blender/renders_video/codex_acf7f58/final/drone/OIDN/CAM_DRON_0001.png` (y 0200, 0400, 0600), en 4K con el mismo compositor del video.

**Gente y vehículos en el dron:** las tres tomas piden que no aparezcan. Lo que no está en los fotogramas clave aparecería y desaparecería a mitad de la toma.
- Si quieres vida, agrégala primero en los cuatro fotogramas con los prompts de imagen (`PROMPTS_IA_RENDERS.md`).
- Mantén los mismos autos en las mismas posiciones donde dos fotogramas ven la misma zona.
- Después borra la frase *"No people or vehicles appear or disappear"* de los prompts.

### Toma 1 · cuadros 1 → 200

```
Smooth, continuous drone flight in one unbroken take. It starts with a high aerial view of a modern airport terminal on the Bolivian altiplano, seen from the front-left about 55 m up, and glides steadily forward and down toward the left end of the terminal's front, finishing exactly on the end frame about 12 m up. Constant speed with a gentle ease-out, level horizon, no shake, no zoom.
Crisp, dry high-altitude morning light at 9:30 a.m., deep blue sky, clear air with slight haze over the distant ochre mountains; tufts of dry golden grass sway lightly in the wind.
Keep the architecture and the site exactly as in both frames: the long roof, the parapet sign with the UYUNI letters and their mirrored outline below the horizon line, the glazing with black mullions, the rust corten screens, the dark-soil planters with white raised rims, the white hexagonal rims, the yellow curbs and zigzag markings, the roads, the apron and the two parked aircraft. Do not add, remove, bend or redesign anything. No people or vehicles appear or disappear. No new buildings, no text, no cuts, no morphing.
Photorealistic aerial cinematography, natural colors, fine detail, no CGI look. Audio: soft high-altitude wind only.
```

### Toma 2 · cuadros 200 → 400

```
Continuous drone flight that continues the previous shot without a cut. The drone keeps descending until it is about 5 m above the arrival lanes in front of the terminal, then tracks smoothly to the right, parallel to the glazed landside facade, looking diagonally toward it. The dark-soil planters with their white raised rims slide by in the foreground and the canopy, columns and sign pass beyond. Ends exactly on the end frame. Constant speed, perfectly level horizon, no shake, no zoom.
Crisp morning sun at 9:30 a.m., hard natural shadows, deep blue sky, dry clear air; a light breeze moves the dust very slightly.
Keep the architecture and the site exactly as in both frames: the UYUNI letters and their mirrored outline below the horizon line, the column rhythm, the glazing with black mullions, the diamond windows, the rust corten screens, the planters, white rims, yellow curbs and road markings. Do not add, remove, bend or redesign anything. No people or vehicles appear or disappear. No new buildings, no text, no cuts, no morphing.
Photorealistic architectural cinematography, natural colors, fine detail, no CGI look. Audio: soft wind only.
```

### Toma 3 · cuadros 400 → 600

```
Continuous drone flight that continues the previous shot without a cut. Still about 5 m above the arrival lanes, the drone passes the right end of the facade with its tall rust corten screens, then rises smoothly, swings out over the side road and turns back to reveal the whole terminal: the long roof, the landside front with its planters and parking plaza, and behind it the apron with two Boeing 737s in BoA livery parked at the jet bridges, with the flat altiplano and distant mountains beyond. Ends exactly on the end frame, about 36 m up. Smooth crane-up with a gentle ease-in and ease-out, no shake, no zoom.
Crisp morning light at 9:30 a.m., deep blue sky, clear dry air, faint haze on the horizon.
Keep the architecture, the aircraft and the site exactly as in both frames. Do not add, remove, bend or redesign anything. No people or vehicles appear or disappear. No new buildings, no text, no cuts, no morphing.
Photorealistic aerial cinematography, natural colors, fine detail, no CGI look. Audio: soft wind only.
```

**Para armar el video:** pon los tres clips seguidos y quita el primer cuadro de las tomas 2 y 3 (repite el último de la anterior).

---

## 3. Vistas renderizadas como tomas (opcional)

Con **solo el fotograma inicial** (la vista final, ya postproducida si la mejoraste con IA), cada vista da un clip de 8 s. Como no hay fotograma final, aquí sí se puede agregar gente y vehículos en movimiento.

**Regla:** movimientos de cámara cortos y lentos. Cuanto más se mueve la cámara, más inventa Veo en los bordes del cuadro.

Frase de cierre para pegar al final de todos los prompts de esta sección:

```
Keep the architecture exactly as in the image: same geometry, colors, materials, sign letters and their mirrored outline, screen pattern, column rhythm and glazing. Do not add, remove, bend or redesign anything. No new buildings, no text, no cuts, no morphing. Photorealistic architectural cinematography, natural colors, no CGI look. Audio: ambient wind only.
```

### CAM_01 · Hero del Lado Tierra (32 mm, altura de ojos)

```
Slow forward dolly of about two meters at eye level along the edge of the arrival lane, smooth and steady, toward the glazed front of the airport terminal on the Bolivian altiplano. Morning sun at 9:30 a.m. from the left, crisp shadows, deep blue sky. A few travelers with rolling suitcases and trekking backpacks, in down jackets and beanies, walk under the canopy toward the entrances; a white tourist minibus slowly pulls into the drop-off bay; a white Toyota Land Cruiser with a loaded roof rack passes in the far lane. People and vehicles at true scale, natural walking pace.
```

### CAM_02 · Detalle del alero (35 mm, desde 10 m)

```
Very slow sideways tracking shot from a lift about 10 m high, moving parallel to the roof edge, revealing the standing-seam roof, the double snow-guard tubes, the drip edge and the ribbed parapet with fine parallax. Hard morning sun, deep blue sky, thin specular highlights sliding along the seams. Below, a few tiny travelers walk on the sidewalk.
```

### CAM_02B · Cielo raso bajo la marquesina (22 mm, mirando hacia arriba)

```
Locked-off camera looking up from the sidewalk with a barely perceptible tilt upward. The slatted soffit, the concrete columns and the full-height glazing stay perfectly still; warm light glows from the check-in hall behind the glass. One traveler pulling a suitcase crosses the lower left edge of the frame, slightly motion-blurred.
```

### CAM_03 · Hora azul con nieve (24 mm, trípode)

```
Locked-off tripod shot at blue hour, about 20 minutes after sunset, cold and clear, a last warm glow low on the right horizon. The terminal's warm interior light and canopy downlights stay steady. Soft motion: travelers under the canopy as gentle motion blur, one vehicle passing on the road leaving faint red and white light trails, a little breath vapor and drifting powder snow at ground level, reflections in the wet asphalt rippling very slightly. No flicker, no extra light sources.
```

### CAM_04 · Aérea general (35 mm, dron)

```
Slow drone orbit to the right around the terminal, with a slight push in, at constant height. The sun is almost behind the drone, crisp shadows fall away from the camera, the flat altiplano with golden grass tufts and pale gravel extends to the horizon. A white 4x4 drives slowly along the arrival lanes; small travelers near the entrances.
```

### CAM_05 · Letrero (40 mm, frontal, desde 4 m)

```
Very slow sideways slide, perfectly frontal and level, so the sign letters standing off the ribbed parapet show subtle parallax against their crisp shadows. Morning sun, deep blue sky. No people. The UYUNI letters and their mirrored outline below the thin horizon line stay perfectly legible and unchanged.
```

### CAM_06 · Detalle de la celosía (28 mm, a 2 m)

```
Slow push-in toward the perforated screen at walking height. Hard morning sun projects the cut-out pattern as sharp light spots on the wall behind it. One traveler with a trekking backpack walks past the left part of the screen, at true scale against the 6 m tall screen, without covering its central motif.
```

### CAM_07 · Las dos propuestas (28 mm, desde 6 m)

Usa el mismo prompt para P1 y P2, para que la comparación sea justa.

```
Slow, smooth crane-down of about one meter combined with a slight push in, keeping the verticals perfectly straight, framing the whole landside facade of the terminal with the planters and white raised rims in the foreground. Morning sun at 9:30 a.m., deep blue sky. Travelers with suitcases walk along the sidewalk and under the canopy; a white minibus waits in the drop-off bay; a white Land Cruiser drives slowly along the outer lane.
```

### CAM_08 · Lado Aire (28 mm, aérea)

```
Slow drone orbit to the left at constant height over the airside apron. The two Boeing 737s in BoA livery stay parked at the jet bridges; a baggage tractor with carts and a ground crew member in a hi-vis vest move slowly beside the nearest aircraft. Crisp morning light, deep blue sky, the altiplano beyond. The aircraft livery and the jet bridges stay unchanged.
```

### CAM_09 · Manga y 737 (30 mm, desde 30 m)

```
Slow descending push toward the jet bridge connected to the Boeing 737 in BoA livery. Ground crew in hi-vis vests near the nose gear, a baggage cart moving slowly toward the hold, a faint heat shimmer over the apron. Crisp morning light, deep blue sky. The aircraft, its livery and the jet bridge stay unchanged.
```

### CAM_10 · Pista y horizonte (30 mm, desde 90 m)

```
Very slow forward glide high above the far end of the runway, looking across the airfield toward the terminal and the distant hills. Light cloud shadows drift across the plain, a faint heat shimmer over the runway, crisp dry air with slight haze on the horizon. The runway markings, the terminal and the parked aircraft stay unchanged.
```

---

## 4. Lista de control final

- [ ] Las tomas del dron empalman sin salto: el último cuadro de una toma coincide con el primero de la siguiente.
- [ ] En ningún cuadro cambian las letras UYUNI, su reflejo espejado, las celosías ni el ritmo de columnas y paños.
- [ ] Jardineras, anillos blancos, hexágonos, separador amarillo y espiga del frente iguales a los del render.
- [ ] Gente y vehículos a escala: persona ≈ 1,7 m, Land Cruiser ≈ 4,9 m de largo. Ninguno aparece ni desaparece de golpe.
- [ ] Mismo cielo, misma hora y misma gradación de color en todos los clips. Si hace falta, corrige el color al final con `unificar_color.py`, sobre los cuadros exportados.
