"""Prueba de fotorrealismo: aplica técnicas de cámara, luz, materiales y óptica sobre una copia del modelo y
renderiza ANTES / DESPUÉS con su diagnóstico de exposición en False Color. No modifica el .blend de entrada.

Técnicas (ver 02_postproduccion/FOTORREALISMO_BLENDER.md):
  1. verticales rectas: cámara horizontal (sin inclinación) y encuadre con shift Y;
  2. exposición por la luz, no por la cámara: sol y cielo escalados por FACTOR_LUZ (0,6 = −0,7 EV);
  3. microbisel en el shader (nodo Bevel) en chapas, letrero, revoque, perfiles, hormigón y listones;
  4. rugosidad variable en metales (ruido de baja amplitud);
  5. vidrio DVH levemente abombado ("pillowing"): ondulación de baja frecuencia en las normales;
  6. albedos físicos: blanco del letrero 0,78 lineal; negros (plenum, sellos) 0,03;
  7. óptica de cámara en el compositor de Blender 5.x (grupo de nodos): bloom suave, distorsión y aberración
     cromática mínimas, viñeteo y grano fino.

Uso:
  python prueba_fotorrealismo.py -- modelo.blend carpeta [camara] [escena] [factor_luz] [ancho] [muestras]
  Por defecto: CAM_01_HERO_LADO_TIERRA, UYUNI_DIA, 0.6, 1280 px, 96 muestras.
Salida: <camara>_ANTES.jpg, <camara>_ANTES_FALSE_COLOR.jpg, <camara>_DESPUES.jpg, <camara>_DESPUES_FALSE_COLOR.jpg
y prueba_fotorrealismo.blend (la copia con todo aplicado, para inspeccionar los nodos).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
blend, salida = args[0], args[1]
camara = args[2] if len(args) > 2 else "CAM_01_HERO_LADO_TIERRA"
escena = args[3] if len(args) > 3 else "UYUNI_DIA"
FACTOR_LUZ = float(args[4]) if len(args) > 4 else 0.6
ancho = int(args[5]) if len(args) > 5 else 1280
muestras = int(args[6]) if len(args) > 6 else 96

BISEL = {"CHAPA_CUBIERTA": 0.004, "CHAPA_ANTEPECHO_REMATES": 0.004, "LETRERO_BLANCO_O_CORTEN": 0.006,
         "REVOQUE_CONTINUO": 0.008, "REVOQUE_FACHADA_BUNAS": 0.008, "ALUMINIO_ANTRACITA_MATE": 0.002,
         "HORMIGON_VISTO": 0.005, "ACERO_GALVANIZADO": 0.002, "CIELO_LISTONES": 0.003}          # radio (m)
RUGOSIDAD = {"CHAPA_CUBIERTA": (0.07, 2.5), "CHAPA_ANTEPECHO_REMATES": (0.07, 2.5),
             "ALUMINIO_ANTRACITA_MATE": (0.05, 6.0), "ACERO_GALVANIZADO": (0.06, 6.0)}            # (amplitud, escala)

bpy.ops.wm.open_mainfile(filepath=blend)
sc = bpy.data.scenes[escena]
cam = bpy.data.objects[camara]
sc.camera = cam
os.makedirs(salida, exist_ok=True)


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)


def render(nombre, falso_color=False):
    r, cy = sc.render, sc.cycles
    r.resolution_x = ancho // 2 if falso_color else ancho
    r.resolution_y, r.resolution_percentage = round(r.resolution_x * 9 / 16), 100
    r.image_settings.file_format, r.image_settings.color_mode, r.image_settings.quality = "JPEG", "RGB", 94
    cy.device, cy.use_adaptive_sampling, cy.adaptive_threshold = "CPU", True, 0.01
    cy.samples = max(16, muestras // 3) if falso_color else muestras
    cy.use_denoising, cy.denoiser = True, "OPENIMAGEDENOISE"
    vista, comp = sc.view_settings.view_transform, sc.compositing_node_group
    if falso_color:                       # el diagnóstico se mide sin compositor
        sc.view_settings.view_transform, sc.compositing_node_group = "False Color", None
    r.filepath = os.path.join(salida, f"{camara}_{nombre}.jpg")
    bpy.ops.render.render(write_still=True, scene=sc.name)
    sc.view_settings.view_transform, sc.compositing_node_group = vista, comp
    print("[OK]", r.filepath)


def bsdf(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def enderezar_camara(cam):
    """Rotación X = 90° (cámara horizontal) y shift Y que conserva el encuadre: verticales paralelas."""
    d = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    inclinacion = math.asin(max(-1.0, min(1.0, d.z)))
    cam.rotation_euler = Vector((d.x, d.y, 0)).normalized().to_track_quat("-Z", "Y").to_euler()
    cam.data.shift_y += math.tan(inclinacion) * cam.data.lens / cam.data.sensor_width
    print(f"{cam.name}: inclinación {math.degrees(inclinacion):.2f}° -> shift_y {cam.data.shift_y:.3f}")


def escalar_luz(sc, factor):
    for ob in bpy.data.objects:
        if ob.type == "LIGHT" and ob.data.type == "SUN" and sc.name in [s.name for s in ob.users_scene]:
            ob.data.energy *= factor
    for n in sc.world.node_tree.nodes:
        if n.type == "BACKGROUND":
            n.inputs["Strength"].default_value *= factor


def bisel(mat, radio):
    nt, b = mat.node_tree, bsdf(mat)
    bev = nt.nodes.new("ShaderNodeBevel")
    bev.samples = 8
    bev.inputs["Radius"].default_value = radio
    entrada = b.inputs["Normal"]
    if entrada.is_linked and entrada.links[0].from_node.type == "BUMP":   # encadenar: bisel -> bump -> BSDF
        nt.links.new(bev.outputs["Normal"], entrada.links[0].from_node.inputs["Normal"])
    elif not entrada.is_linked:
        nt.links.new(bev.outputs["Normal"], entrada)


def rugosidad_variable(mat, amplitud, escala):
    nt, b = mat.node_tree, bsdf(mat)
    entrada = b.inputs["Roughness"]
    if entrada.is_linked:
        origen = entrada.links[0].from_socket
    else:
        v = nt.nodes.new("ShaderNodeValue")
        v.outputs[0].default_value = entrada.default_value
        origen = v.outputs[0]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value, nz.inputs["Detail"].default_value = escala, 8.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    var = nt.nodes.new("ShaderNodeMath"); var.operation = "MULTIPLY_ADD"          # (ruido · 2a) − a
    nt.links.new(nz.outputs["Fac"], var.inputs[0])
    var.inputs[1].default_value, var.inputs[2].default_value = 2 * amplitud, -amplitud
    suma = nt.nodes.new("ShaderNodeMath"); suma.operation = "ADD"; suma.use_clamp = True
    nt.links.new(origen, suma.inputs[0]); nt.links.new(var.outputs[0], suma.inputs[1])
    nt.links.new(suma.outputs[0], entrada)


def vidrio_abombado(mat, escala=0.35, fuerza=0.04, distancia=0.05):
    nt, b = mat.node_tree, bsdf(mat)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value, nz.inputs["Detail"].default_value = escala, 0.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value, bump.inputs["Distance"].default_value = fuerza, distancia
    nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])


def albedos_fisicos():
    let = bpy.data.materials.get("UY_LETRERO_BLANCO_O_CORTEN")
    if let:
        for n in let.node_tree.nodes:
            if n.type == "MIX" and n.data_type == "RGBA":
                for s in n.inputs:
                    if s.name == "A" and s.type == "RGBA" and not s.is_linked and min(s.default_value[:3]) > 0.85:
                        s.default_value = srgb("#E5E5E1")                          # 0,78 lineal
    for nombre in ("UY_PLENUM_NEGRO_MATE", "UY_SELLO_ESTRUCTURAL_NEGRO", "UY_NEUMATICO"):
        m = bpy.data.materials.get(nombre)
        if m:
            bsdf(m).inputs["Base Color"].default_value = srgb("#303030")          # 0,03 lineal


def compositor_optica(sc):
    """Blender 5.x: el compositor es un grupo de nodos asignado a la escena y sale por Group Output."""
    ng = bpy.data.node_groups.new("UY_OPTICA_CAMARA", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    sc.compositing_node_group = ng
    sc.render.compositor_device = "CPU"           # en la nube no hay EGL; con GPU en la PC puede ir en "GPU"
    sc.render.compositor_precision = "FULL"
    N, L = ng.nodes, ng.links
    def sock(nodo, nombre, tipo, salida=False):
        return next(s for s in (nodo.outputs if salida else nodo.inputs) if s.name == nombre and s.type == tipo)
    rl = N.new("CompositorNodeRLayers")
    gl = N.new("CompositorNodeGlare")                               # resplandor solo en reflejos muy intensos
    gl.inputs["Type"].default_value = "Bloom"
    gl.inputs["Threshold"].default_value, gl.inputs["Strength"].default_value, gl.inputs["Size"].default_value = 1.2, 0.12, 0.55
    L.new(rl.outputs["Image"], gl.inputs["Image"])
    ld = N.new("CompositorNodeLensdist")                            # barril mínimo y aberración cromática lateral
    ld.inputs["Distortion"].default_value, ld.inputs["Dispersion"].default_value = -0.008, 0.006
    ld.inputs["Fit"].default_value = True
    L.new(gl.outputs["Image"], ld.inputs["Image"])
    el = N.new("CompositorNodeEllipseMask")                         # viñeteo: elipse difuminada multiplicada al 30 %
    el.inputs["Size"].default_value = (1.15, 1.15)
    bl = N.new("CompositorNodeBlur")
    bl.inputs["Size"].default_value = (300, 300)
    L.new(el.outputs["Mask"], bl.inputs["Image"])
    vg = N.new("ShaderNodeMix"); vg.data_type, vg.blend_type = "RGBA", "MULTIPLY"
    sock(vg, "Factor", "VALUE").default_value = 0.30
    L.new(ld.outputs["Image"], sock(vg, "A", "RGBA")); L.new(bl.outputs["Image"], sock(vg, "B", "RGBA"))
    co = N.new("CompositorNodeImageCoordinates")                    # grano: ruido blanco por píxel, ±0,6 % lineal
    L.new(rl.outputs["Image"], co.inputs["Image"])
    wn = N.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "2D"
    L.new(co.outputs["Pixel"], wn.inputs["Vector"])
    gr = N.new("ShaderNodeMath"); gr.operation = "MULTIPLY_ADD"
    L.new(wn.outputs["Value"], gr.inputs[0]); gr.inputs[1].default_value, gr.inputs[2].default_value = 0.012, -0.006
    su = N.new("ShaderNodeMix"); su.data_type, su.blend_type = "RGBA", "ADD"
    sock(su, "Factor", "VALUE").default_value = 1.0
    L.new(sock(vg, "Result", "RGBA", True), sock(su, "A", "RGBA")); L.new(gr.outputs[0], sock(su, "B", "RGBA"))
    L.new(sock(su, "Result", "RGBA", True), N.new("NodeGroupOutput").inputs["Image"])


render("ANTES")
render("ANTES_FALSE_COLOR", falso_color=True)
enderezar_camara(cam)
escalar_luz(sc, FACTOR_LUZ)
for nombre, radio in BISEL.items():
    if bpy.data.materials.get("UY_" + nombre):
        bisel(bpy.data.materials["UY_" + nombre], radio)
for nombre, (amp, esc) in RUGOSIDAD.items():
    if bpy.data.materials.get("UY_" + nombre):
        rugosidad_variable(bpy.data.materials["UY_" + nombre], amp, esc)
if bpy.data.materials.get("UY_VIDRIO_CONTROL_SOLAR"):
    vidrio_abombado(bpy.data.materials["UY_VIDRIO_CONTROL_SOLAR"])
albedos_fisicos()
compositor_optica(sc)
render("DESPUES")
render("DESPUES_FALSE_COLOR", falso_color=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(salida, "prueba_fotorrealismo.blend"), compress=True)
