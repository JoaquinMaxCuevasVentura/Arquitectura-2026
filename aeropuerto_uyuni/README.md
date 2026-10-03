# Aeropuerto de Uyuni: visualización de la Terminal de Pasajeros

| Carpeta | Contenido |
|---|---|
| `00_auditoria/` | Auditoría técnica del DXF y los IFC (Fases 0 y 0.5): `AUDITORIA.md`, informes JSON, 16 vistas aisladas (PNG + DXF limpio), decisiones confirmadas y el script de auditoría. |
| `01_blender/` | Modelo paramétrico: `uyuni_modelo.py` (fuente), `uyuni_v1.blend` (ya generado) y renders de prueba en `previews/`. |

## Cómo usarlo en Blender 5.2

**Opción 1: abrir el modelo ya generado.** Abre `01_blender/uyuni_v1.blend`. Contiene dos escenas:

| Escena | Luz | Cámaras |
|---|---|---|
| `UYUNI_DIA` | Mañana: sol calculado para Uyuni el 4 de octubre a las 09:30 | CAM_01, CAM_02, CAM_02B, CAM_04, CAM_DRON |
| `UYUNI_CREPUSCULO` | Hora azul, interior encendido, piso mojado | CAM_03 |

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
- `NERVIO_PASO = 0.30`
- `RETENEDOR_DIST_BORDE = 0.40`
- `CELOSIAS` (posiciones de las celosías)
- `FECHA_DIA` y `FECHA_CREPUSCULO`

Las propiedades `humedad`, `nieve`, `luz_interior` y `luz_alero` de cada escena controlan los materiales: piso mojado, nieve en el suelo y luces.

## Pendiente

- **Vehículos 4x4, minibús y turistas:** hoy son cajas de ubicación en `07_ASSETS/PROXIES_COLOCACION`, visibles solo en el visor. Hay que reemplazarlas por modelos reales (Sketchfab o BlenderKit).
- **Lado Aire e interiores:** están simplificados, según el brief.
- **Cumbrera:** se usó +13,02 (alzados laterales); las fachadas NE y SO marcan +13,43.
