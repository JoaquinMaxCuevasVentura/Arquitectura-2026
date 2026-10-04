"""Prueba pequeña de iluminación nocturna (hora azul) en CAM_03, escena UYUNI_CREPUSCULO.

Renderiza el ANTES y el DESPUÉS, cada uno con su diagnóstico en False Color. El DESPUÉS aplica:
  1. Kelvin en todo: los emisores (interior, luminarias del alero, letrero) pasan de RGB a Blackbody, con la misma
     temperatura que las luces que los acompañan (alero 3000 K, interior 3500 K, letrero LED 4000 K).
  2. Luz práctica bien armada: la luminaria del alero se ve (cámara y reflejos) pero no ilumina; ilumina el Spot que ya
     tiene adentro (Emission Sampling = None y sin visibilidad difusa). Sin luces duplicadas ni ruido de emisores chicos.
  3. Interior con profundidad: la caja emisiva pareja se apaga casi del todo y la ilumina una grilla de Area Lights
     de techo (3500 K, con Spread) sobre paredes claras, con mostradores simples. Charcos de luz y gradientes en vez de
     ventanas quemadas.
  4. Exposición medida: con False Color, cielo entre -1 y 0 EV, muros con barridos de luz entre +1 y +2, interior
     entre +2 y +3 y solo las fuentes por encima de +5. Se ajusta como en una cámara (exposición), sin tocar las
     proporciones entre luces.
  5. Óptica nocturna en el compositor: halo suave (Fog Glow) en las fuentes, viñeteo y grano aditivo de ±0,4 %
     (en lineal: en una imagen oscura se nota más que el ±0,6 % del día, como el grano de un ISO alto).

Uso: python prueba_noche.py -- archivo.blend carpeta [ancho] [muestras] [exposicion_despues]
"""
import math
import os
import sys
import time

import bpy
import bmesh                # con el módulo bpy, bmesh existe recién después de importar bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
blend, salida = args[0], args[1]
ancho = int(args[2]) if len(args) > 2 else 1280
muestras = int(args[3]) if len(args) > 3 else 128
exposicion_despues = float(args[4]) if len(args) > 4 else 1.1
os.makedirs(salida, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=blend)
sc = bpy.data.scenes["UYUNI_CREPUSCULO"]
cam = sc.camera
for vl in sc.view_layers:
    vl.update()


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)


# verticales rectas, igual en el antes y en el después
d = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
pitch = math.asin(max(-1, min(1, d.z)))
cam.rotation_euler = Vector((d.x, d.y, 0)).normalized().to_track_quat("-Z", "Y").to_euler()
cam.data.shift_y += math.tan(pitch) * cam.data.lens / cam.data.sensor_width
print(f"[NOCHE] {cam.name}: inclinación {math.degrees(pitch):.2f}° -> shift_y {cam.data.shift_y:.3f}", flush=True)
spots = [o for o in sc.objects if o.type == "LIGHT" and o.data.type == "SPOT"]
print("[NOCHE] spots:", len(spots), "radio", {round(o.data.shadow_soft_size, 3) for o in spots},
      "cono", {round(math.degrees(o.data.spot_size), 1) for o in spots}, "exposición actual", sc.view_settings.exposure, flush=True)

r, cy = sc.render, sc.cycles
cy.device, cy.use_adaptive_sampling, cy.adaptive_threshold = "CPU", True, 0.01
cy.use_denoising, cy.denoiser = True, "OPENIMAGEDENOISE"
r.image_settings.file_format, r.image_settings.color_mode, r.image_settings.quality = "JPEG", "RGB", 94
tiempos = {}


def render(nombre, false_color=False):
    vt, lk = sc.view_settings.view_transform, sc.view_settings.look
    usa_comp = sc.compositing_node_group
    if false_color:
        sc.view_settings.view_transform, sc.view_settings.look = "False Color", "None"
        sc.compositing_node_group = None          # medir sin óptica de compositor
        r.resolution_x, r.resolution_y, cy.samples = ancho // 2, round(ancho // 2 * 9 / 16), max(32, muestras // 3)
    else:
        r.resolution_x, r.resolution_y, cy.samples = ancho, round(ancho * 9 / 16), muestras
    r.resolution_percentage = 100
    r.filepath = f"{salida}/{nombre}.jpg"
    t = time.time()
    bpy.ops.render.render(write_still=True, scene=sc.name)
    tiempos[nombre] = time.time() - t
    print(f"[NOCHE] {nombre} -> {tiempos[nombre]:.0f} s", flush=True)
    sc.view_settings.view_transform, sc.view_settings.look = vt, lk
    sc.compositing_node_group = usa_comp


render("A_ANTES")
render("A_ANTES_FALSE_COLOR", false_color=True)


# ------------------------------------------------------------------ 1. emisores en Kelvin
def emision_kelvin(nombre_mat, kelvin):
    mat = bpy.data.materials["UY_" + nombre_mat]
    nt = mat.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bb = nt.nodes.new("ShaderNodeBlackbody")
    bb.inputs["Temperature"].default_value = kelvin
    nt.links.new(bb.outputs["Color"], b.inputs["Emission Color"])
    return mat


emision_kelvin("LUMINARIA_ALERO", 3000)
emision_kelvin("LETRERO_BLANCO_O_CORTEN", 4000)
interior = emision_kelvin("INTERIOR_LUZ_CALIDA", 3500)

# ------------------------------------------------------------------ 2. luminaria del alero: se ve, no ilumina
lum = bpy.data.materials["UY_LUMINARIA_ALERO"]
# sin muestreo de luz: ilumina el Spot que tiene adentro (Material > Settings > Emission Sampling)
lum.cycles.emission_sampling = "NONE"
ob_lum = bpy.data.objects["UY_LUMINARIAS_ALERO"]
ob_lum.visible_diffuse = False

# ------------------------------------------------------------------ 3. interior con profundidad
ENERGIA_TECHO = 1000.0       # W por Area Light de techo (calibrado con False Color: interior entre +2 y +3 EV)
FACTOR_SPOTS_ALERO = 1.6     # barridos de luz en los muros: el centro entre +1 y +2 EV
for o in spots:
    if "ALERO" in o.name:
        o.data.energy *= FACTOR_SPOTS_ALERO
sc["luz_interior"] = 0.25                            # la caja queda como un resplandor tenue de fondo
bi = next(n for n in interior.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
bi.inputs["Base Color"].default_value = srgb("#B8B2A8")   # paredes y techo claros (0,45)
col = bpy.data.collections.new("12_INTERIOR_PRUEBA")
sc.collection.children.link(col)
# grilla de Area Lights de techo: dos filas a lo largo de la fachada, a 6,5 m, una por vano de 4,8 m
n_luces = 0
for i in range(15):
    x = 2.4 + i * 4.8
    for y in (3.2, 6.8):
        ld = bpy.data.lights.new(f"UY_TECHO_INTERIOR_{i:02d}_{y:.1f}", "AREA")
        ld.shape, ld.size, ld.size_y = "RECTANGLE", 1.2, 0.6
        ld.energy, ld.use_temperature, ld.temperature = ENERGIA_TECHO, True, 3500.0
        ld.spread = math.radians(110)
        ob = bpy.data.objects.new(ld.name, ld)
        ob.location = (x, y, 6.5)
        col.objects.link(ob)
        n_luces += 1
# mostradores simples de check-in (cajas claras) para que el interior tenga algo que iluminar
me = bpy.data.meshes.new("UY_MOSTRADORES_PRUEBA")
bm = bmesh.new()
for i in range(7):
    x0 = 4.0 + i * 9.6
    m = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(2.4, 0.8, 1.1), verts=m["verts"])
    bmesh.ops.translate(bm, vec=(x0, 5.6, 0.55), verts=m["verts"])
bm.to_mesh(me)
bm.free()
mm = bpy.data.materials.new("UY_MOSTRADOR_PRUEBA")
if mm.node_tree is None:
    mm.use_nodes = True
pb = next(n for n in mm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
pb.inputs["Base Color"].default_value = srgb("#D2CEC6")
pb.inputs["Roughness"].default_value = 0.35
me.materials.append(mm)
col.objects.link(bpy.data.objects.new("UY_MOSTRADORES_PRUEBA", me))
print(f"[NOCHE] interior: {n_luces} Area Lights de techo, 7 mostradores", flush=True)

# ------------------------------------------------------------------ 4. letrero sin quemar
sc["luz_letrero"] = 0.9
if exposicion_despues is not None:
    sc.view_settings.exposure = exposicion_despues

# ------------------------------------------------------------------ 5. óptica nocturna en el compositor
ng = bpy.data.node_groups.new("UY_OPTICA_NOCHE", "CompositorNodeTree")
ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
sc.compositing_node_group = ng
r.compositor_device, r.compositor_precision = "CPU", "FULL"
N, L = ng.nodes, ng.links
rl = N.new("CompositorNodeRLayers")
rl.scene = sc                 # si no se indica, toma la escena activa (UYUNI_DIA) y la renderiza también
gl = N.new("CompositorNodeGlare")
gl.inputs["Type"].default_value = "Fog Glow"
gl.inputs["Threshold"].default_value, gl.inputs["Strength"].default_value, gl.inputs["Size"].default_value = 1.5, 0.08, 0.5
L.new(rl.outputs["Image"], gl.inputs["Image"])
el = N.new("CompositorNodeEllipseMask")
el.inputs["Size"].default_value = (1.15, 1.15)
bl = N.new("CompositorNodeBlur")
bl.inputs["Size"].default_value = (300, 300)
L.new(el.outputs["Mask"], bl.inputs["Image"])
vg = N.new("ShaderNodeMix")
vg.data_type, vg.blend_type = "RGBA", "MULTIPLY"
next(s for s in vg.inputs if s.name == "Factor" and s.type == "VALUE").default_value = 0.30
L.new(gl.outputs["Image"], next(s for s in vg.inputs if s.name == "A" and s.type == "RGBA"))
L.new(bl.outputs["Image"], next(s for s in vg.inputs if s.name == "B" and s.type == "RGBA"))
co = N.new("CompositorNodeImageCoordinates")
L.new(rl.outputs["Image"], co.inputs["Image"])
wn = N.new("ShaderNodeTexWhiteNoise")
wn.noise_dimensions = "2D"
L.new(co.outputs["Pixel"], wn.inputs["Vector"])
gr = N.new("ShaderNodeMath")
gr.operation = "MULTIPLY_ADD"
L.new(wn.outputs["Value"], gr.inputs[0])
gr.inputs[1].default_value, gr.inputs[2].default_value = 0.008, -0.004      # ±0,4 % en lineal: se nota en las sombras
add = N.new("ShaderNodeMix")
add.data_type, add.blend_type = "RGBA", "ADD"
next(s for s in add.inputs if s.name == "Factor" and s.type == "VALUE").default_value = 1.0
L.new(next(s for s in vg.outputs if s.name == "Result" and s.type == "RGBA"), next(s for s in add.inputs if s.name == "A" and s.type == "RGBA"))
L.new(gr.outputs[0], next(s for s in add.inputs if s.name == "B" and s.type == "RGBA"))
out = N.new("NodeGroupOutput")
L.new(next(s for s in add.outputs if s.name == "Result" and s.type == "RGBA"), out.inputs["Image"])

render("B_DESPUES_FALSE_COLOR", false_color=True)
render("B_DESPUES")
print(f"[COSTO] antes {tiempos['A_ANTES']:.0f} s, después {tiempos['B_DESPUES']:.0f} s "
      f"({100 * (tiempos['B_DESPUES'] / tiempos['A_ANTES'] - 1):+.0f} %)", flush=True)
bpy.ops.wm.save_as_mainfile(filepath=f"{salida}/prueba_noche.blend", compress=True)
