# Aeropuerto de Uyuni: visualización de la Terminal de Pasajeros

> **¿Vas a continuar el proyecto?** Empieza por [`TRASPASO.md`](TRASPASO.md), que reúne el estado, las coordenadas, las decisiones del cliente, los puntos abiertos y los pendientes. Para pasárselo a otra IA hay una instrucción lista en [`PROMPT_CONTINUACION.md`](PROMPT_CONTINUACION.md).

| Carpeta | Contenido |
|---|---|
| `00_auditoria/` | Auditoría técnica del DXF y los IFC (Fases 0 y 0.5): `AUDITORIA.md`, informes JSON, 16 vistas aisladas (PNG + DXF limpio), decisiones confirmadas y el script de auditoría. |
| `01_blender/` | Modelo paramétrico: `uyuni_modelo.py` (fuente), `uyuni_v2.blend` (ya generado) e `inventario_escena.json` (qué hay en la escena y dónde). |
| `01_blender/previews/` | Vistas previas de las cámaras CAM_01 a CAM_06. |
| `01_blender/verificacion/` | El modelo superpuesto al CAD (en rojo): 4 alzados y 2 cortes. |
| `01_blender/herramientas/` | Scripts sin interfaz para generar el `.blend`, renderizar vistas previas, verificar contra el CAD e inventariar la escena. |
| `02_postproduccion/` | `PROMPTS_IA_RENDERS.md`: prompts por vista para postproducir los renders con IA, con el flujo de trabajo y el control de calidad. `PROMPT_UPSCALE_PROPUESTAS.md`: prompts y ajustes para escalar ×2 con IA los renders de las dos propuestas. `unificar_color.py`: "Lightroom a medida" que unifica el color de las fotos generadas con IA, con una aplicación en el navegador y un modo por lotes (ver `UNIFICAR_COLOR.md`). |

## Cómo usarlo en Blender 5.2

**Opción 1: abrir el modelo ya generado.** Abre `01_blender/uyuni_v2.blend`. Contiene tres escenas:

| Escena | Luz | Cámaras |
|---|---|---|
| `UYUNI_DIA` | Mañana: sol calculado para Uyuni el 4 de octubre a las 09:30. Propuesta 1 "Patrimonio Ferroviario" | CAM_01, CAM_02, CAM_02B, CAM_04, CAM_05, CAM_06, CAM_07, CAM_07B, CAM_DRON |
| `UYUNI_DIA_P2_SALAR_LITIO` | La misma mañana con la propuesta 2 "Salar & Litio" | CAM_07 |
| `UYUNI_CREPUSCULO` | Hora azul: interior, alero y letrero encendidos; piso mojado; nieve en el borde | CAM_03 |

**Propuestas y letrero:**
- La propiedad `propuesta` de la escena elige la paleta: 0 es P1 y 1 es P2. Los colores están en `PALETA`.
- La propiedad `letras_corten` elige el material del letrero: 1 es corten y 0 es blanco.
- La geometría del letrero tiene dos colecciones: `LETRERO_A_SOBRESALE` (la visible) y `LETRERO_B_CONTENIDO`.
- Para renderizar las variantes sin interfaz, usa `herramientas/render_propuestas.py`.

**Opción 2: regenerar desde el script** (por ejemplo, después de cambiar un parámetro): Scripting > Open > `01_blender/uyuni_modelo.py` > Run Script. Al volver a ejecutarlo, borra y vuelve a crear solo sus propias colecciones.

**Opción 3: vía MCP**, desde una sesión de Claude Code **en tu PC** con el MCP de Blender conectado. Se ejecuta con `execute_blender_code`:

```python
p = r"C:\RUTA\Arquitectura-2026\aeropuerto_uyuni\01_blender\uyuni_modelo.py"
exec(open(p, encoding="utf-8").read(), {"__file__": p, "__name__": "__main__"})
```

Si se pasa `__file__`, el script también carga las vistas del CAD como planos de referencia en `_REF_CAD` (no salen en el render).

## Render

- Cycles, AgX con look Medium High Contrast.
- 4K (3840 × 2160) al 50 %, 256 muestras con eliminación de ruido.
- Para una entrega final:
  1. Sube la resolución al 100 %.
  2. Activa la GPU en *Preferences > System > Cycles Render Devices* (OptiX o CUDA).
- Recorrido de dron: cámara `CAM_DRON`, 600 cuadros a 24 fps (25 s). Formato de salida sugerido: FFmpeg, H.264, MP4.

## Parámetros clave

Todos están al inicio de `uyuni_modelo.py`:
- `H_VANO = 5.51`
- `Z_ANTEPECHO = (6.612, 9.012)`
- `Y_ANTEPECHO_EXT = -1.632` (volado de 2,0 m)
- `CUMBRERA_Z = 13.02` (las fachadas NE/SO marcan +13,43; sin confirmar)
- `NERVIO_PASO = 0.30`
- `RETENEDOR_DIST_BORDE = 0.40`
- `CELOSIAS` (posición y variante de cada celosía)
- `FECHA_DIA` y `FECHA_CREPUSCULO`

Las propiedades `humedad`, `nieve`, `luz_interior`, `luz_alero` y `luz_letrero` de cada escena controlan los materiales: piso mojado, nieve en el suelo y luces.

## Letrero "línea de horizonte" (v2)

Va sobre el antepecho de chapa (continuación de la cubierta). Es blanco o de acero corten, según la propuesta:
- Letras UYUNI de 1,50 m sobre el horizonte (+7,764), de 8 cm de espesor, y su reflejo en contorno debajo.
- Montículos de sal: **pirámides facetadas en 3D**, con dos caras triangulares que el sol separa en luz y penumbra, y su reflejo en marcos triangulares.
- Línea de horizonte de X 40,976 a 72,252.
- Juego de 3 pirámides sin texto (grande + 2 chicas) sobre la puerta de salida, con su tramo de horizonte de X 13,30 a 20,30.

Todo el conjunto flota despegado 12 cm de la chapa sobre pernos ocultos, para que la sombra propia se separe de las piezas.

La modulación sale del CAD. Hay dos geometrías para probar:
- **A:** como en el dibujo. Las letras sobresalen 0,25 m por encima del antepecho y el reflejo 0,35 m por debajo.
- **B:** contenida en los 2,40 m, reescalada al 72 % y centrada.

## Celosías corten

Hay dos módulos de 5,00 × 6,00 m:
- **PT1:** rectangular.
- **PT2:** con remate en zigzag. Tiene tres variantes según la fachada, tomadas del DXF:
  - `PT2A`: picos en 0-2-4 m;
  - `PT2B`: picos en 1-3-5 m;
  - `PT2R`: rampa a 45° desde 2,0 m hasta 6,0 m. Es el primer módulo del grupo derecho del Lado Tierra.

Construcción de cada módulo:
- **Planchas:** 15 de 1,00 × 2,00 m (1 mm) con juntas de 5 mm.
- **Calados:** las tramas grises del CAD son los vacíos.
- **Bastidor:** tubos de 40 × 40 detrás de las planchas, siguiendo las líneas salmón del CAD (verticales cada 1,00 m, horizontales cada 2,00 m y el borde superior). Queda separado 0,12 m de su fondo.

Ubicación:

| Fachada | Módulos |
|---|---|
| Lado Tierra | 2 en el extremo izquierdo (desde X −0,469) y 3 en el derecho (desde X 67,932, 15,0 m en total) |
| Lado Aire | 2, en el extremo del anexo, con rombos ME-3 detrás |
| Cada lateral | 2: PT1 en la OESTE (testero del eje 1) y PT2 en la ESTE (testero del eje 20), en el extremo del Lado Tierra |

## Elementos de los alzados laterales

- **Fachada OESTE (testero del eje 1):**
  - Rombo de 1,96 m de lado sobre el ME-3, con su centro a +5,65. Lleva marco blanco y chapa blanca perforada sobre un fondo oscuro.
  - Bloque bajo del Lado Aire con mástil (base de 0,20 m hasta +8,88 y fuste de 0,10 m hasta +10,38).
  - Volumen saliente de +3,45 a +6,15 y descanso de 0,45 m con escalones. El alzado no da su posición en X; se ubicaron junto al eje 1.
- **Fachada ESTE (testero del eje 20):** franja de chapa nervada (nervios cada 0,30 m), del color del parapeto, de +4,41 a +6,21, en todo el ancho.

## Pendiente

El detalle está en `TRASPASO.md`: los puntos por revisar contra el DXF, en la sección 6, y los pendientes con su especificación, en la sección 8. En resumen:
- **Vehículos 4x4, minibús y turistas:** hoy son cajas de ubicación en `07_ASSETS/PROXIES_COLOCACION`, visibles solo en el visor. Hay que reemplazarlas por modelos reales.
- **Contexto:** paisaje de altiplano, vegetación y variante de cielo nublado.
- **Contra el DXF:**
  - puertas y vanos del testero del eje 20 (FACHADA ESTE);
  - volumen saliente y elemento vertical de la esquina del eje 1 / Lado Aire;
  - carpinterías del Lado Aire.
- **Cumbrera:** se usó +13,02 (alzados laterales); las fachadas NE y SO marcan +13,43.
- **Renders finales y video del dron:** se renderizan en la PC con GPU.
