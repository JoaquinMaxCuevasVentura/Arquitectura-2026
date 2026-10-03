"""Prueba pequeña de materiales "inteligentes": máscaras procedurales que leen la geometría en el render (Cycles).

Sobre la propuesta 1 (UYUNI_DIA, letrero A y letras corten), con la luz corregida de la prueba de fotorrealismo (×0,6)
y las verticales rectas, renderiza en cada cámara:
  ANTES      los materiales actuales del modelo;
  MASCARAS   diagnóstico de las máscaras: rojo = aristas (Bevel · Normal), verde = cavidades (AO),
             azul = polvo por gravedad (caras hacia arriba y franja al pie de los muros);
  DESPUES    con el grupo UY_MASCARAS_ALTIPLANO aplicado a los materiales del edificio:
             1. metálico binario: la pintura y el óxido son dieléctricos (0) y el metal desnudo es 1;
             2. corten con pátina que responde a la geometría (caras superiores y cantos más oscuros), variación por
                plancha (Random Per Island), rugosidad difusa y rugosidad especular alta;
             3. polvo fino y salino del altiplano en cavidades, en caras hacia arriba y salpicado al pie de los muros,
                que además vuelve dieléctrico y áspero lo que cubre;
             4. revoque con rugosidad difusa (Oren-Nayar) y ondas de llana de muy baja frecuencia;
             5. listones del cielo con color, veta y rugosidad distintos en cada listón (Random Per Island);
             6. galvanizado con "spangle" (Voronoi F1) y asfalto con árido visible (Voronoi F1).
La intensidad del polvo sale de la propiedad de escena "polvo" (0 = sin polvo, 1 = el de esta prueba).

Uso: python prueba_materiales.py -- archivo.blend carpeta [camaras] [ancho] [muestras]
     camaras: lista separada por comas (por defecto CAM_06_DETALLE_CELOSIA,CAM_05_LETRERO_HORIZONTE)
"""
import json
import math
import os
import sys
import time

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
blend, salida = args[0], args[1]
camaras = args[2].split(",") if len(args) > 2 else ["CAM_06_DETALLE_CELOSIA", "CAM_05_LETRERO_HORIZONTE"]
ancho = int(args[3]) if len(args) > 3 else 1280
muestras = int(args[4]) if len(args) > 4 else 96
os.makedirs(salida, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=blend)
sc = bpy.data.scenes["UYUNI_DIA"]
sc["polvo"] = 1.0
for vl in sc.view_layers:
    vl.update()

# Parámetros de la capa de polvo (colores sRGB). Uyuni en octubre: fin de la época de vientos, polvo fino y salino.
POLVO = "#BDB3A1"          # polvo seco y salino, más claro que el suelo
SALPICADO = "#8E826E"      # tierra salpicada al pie de los muros
CORTEN_DENSO = "#3A1A0E"   # pátina densa de caras superiores y cantos
CORTEN_LOTE = "#5E2C1A"    # plancha de un lote más pardo (más oxidado, menos naranja)
# Rayos por punto sombreado. Con 96 a 384 muestras de cámara, 2 en AO y 4 en Bevel convergen igual que 8 y cuestan
# mucho menos: el ruido se promedia entre las muestras de cámara y el OIDN limpia el resto.
MUESTRAS_AO, MUESTRAS_BEVEL = 2, 4


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)


# ------------------------------------------------------------------ base común: luz ×0,6 y verticales rectas
def escalar_luz(factor):
    for ob in sc.objects:
        if ob.type == "LIGHT" and ob.data.type == "SUN":
            ob.data.energy *= factor
    w = sc.world
    for n in w.node_tree.nodes:
        if n.type == "BACKGROUND":
            n.inputs["Strength"].default_value *= factor


def enderezar_camara(cam):
    d = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    pitch = math.asin(max(-1, min(1, d.z)))
    horiz = Vector((d.x, d.y, 0)).normalized()
    cam.rotation_euler = horiz.to_track_quat("-Z", "Y").to_euler()
    cam.data.shift_y += math.tan(pitch) * cam.data.lens / cam.data.sensor_width


escalar_luz(0.6)
for nombre in camaras:
    enderezar_camara(bpy.data.objects[nombre])

r, cy = sc.render, sc.cycles
r.resolution_x, r.resolution_y, r.resolution_percentage = ancho, round(ancho * 9 / 16), 100
r.image_settings.file_format, r.image_settings.color_mode, r.image_settings.quality = "JPEG", "RGB", 94
cy.device, cy.samples, cy.use_adaptive_sampling, cy.adaptive_threshold = "CPU", muestras, True, 0.01
cy.use_denoising, cy.denoiser = True, "OPENIMAGEDENOISE"
REGISTRO = f"{salida}/tiempos.json"
try:
    with open(REGISTRO) as f:
        tiempos = json.load(f)
except (OSError, ValueError):
    tiempos = {}


def render(camara, etapa):
    """Renderiza y anota el tiempo. El ANTES no cambia entre corridas: si ya está, con su tiempo, no se repite."""
    sc.camera = bpy.data.objects[camara]
    sc.render.filepath = f"{salida}/{camara}_{etapa}.jpg"
    clave = f"{camara}_{etapa}"
    if etapa == "A_ANTES" and clave in tiempos and os.path.exists(sc.render.filepath):
        print(f"[PRUEBA] {clave} ya está ({tiempos[clave]:.0f} s)", flush=True)
        return
    t = time.time()
    bpy.ops.render.render(write_still=True, scene=sc.name)
    tiempos[clave] = time.time() - t
    with open(REGISTRO, "w") as f:
        json.dump(tiempos, f, indent=1)
    print(f"[PRUEBA] {camara} {etapa} -> {tiempos[clave]:.0f} s", flush=True)


for c in camaras:
    render(c, "A_ANTES")


# ------------------------------------------------------------------ utilidades de nodos
class G:
    """Atajos para construir nodos en un árbol (material o grupo)."""

    def __init__(self, nt):
        self.nt, self.N, self.L = nt, nt.nodes, nt.links

    def n(self, tipo, **props):
        nodo = self.N.new(tipo)
        for k, v in props.items():
            setattr(nodo, k, v)
        return nodo

    def con(self, a, b):
        if isinstance(a, (int, float)):
            b.default_value = a
        elif isinstance(a, tuple):
            b.default_value = a
        else:
            self.L.new(a, b)

    def m(self, op, a, b=None, clamp=False):
        nodo = self.n("ShaderNodeMath", operation=op, use_clamp=clamp)
        self.con(a, nodo.inputs[0])
        if b is not None:
            self.con(b, nodo.inputs[1])
        return nodo.outputs[0]

    def rango(self, v, a, b, c=0.0, d=1.0, suave=True):
        nodo = self.n("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP" if suave else "LINEAR", clamp=True)
        self.con(v, nodo.inputs["Value"])
        for s, x in zip(("From Min", "From Max", "To Min", "To Max"), (a, b, c, d)):
            nodo.inputs[s].default_value = x
        return nodo.outputs["Result"]

    def mezcla(self, fac, a, b, tipo="RGBA"):
        """Nodo Mix (RGBA o FLOAT); los sockets se eligen por nombre y tipo, como Nodos.mixc/mixf del modelo."""
        nodo = self.n("ShaderNodeMix", data_type=tipo)
        st = "RGBA" if tipo == "RGBA" else "VALUE"
        self.con(fac, next(s for s in nodo.inputs if s.name == "Factor" and s.type == "VALUE"))
        self.con(a, next(s for s in nodo.inputs if s.name == "A" and s.type == st))
        self.con(b, next(s for s in nodo.inputs if s.name == "B" and s.type == st))
        return next(s for s in nodo.outputs if s.name == "Result" and s.type == st)

    def ruido(self, vec, escala, detalle=6.0, rugosidad=0.55, distorsion=0.0, tipo="FBM"):
        nodo = self.n("ShaderNodeTexNoise", noise_type=tipo)
        self.con(vec, nodo.inputs["Vector"])
        nodo.inputs["Scale"].default_value = escala
        nodo.inputs["Detail"].default_value = detalle
        nodo.inputs["Roughness"].default_value = rugosidad
        nodo.inputs["Distortion"].default_value = distorsion
        return nodo.outputs["Factor"]


# ------------------------------------------------------------------ grupo de máscaras (uno para todo el modelo)
def grupo_mascaras():
    ng = bpy.data.node_groups.new("UY_MASCARAS_ALTIPLANO", "ShaderNodeTree")
    I = ng.interface
    for nombre, valor in (("Radio arista", 0.01), ("Distancia AO", 0.30), ("Altura salpicado", 0.30)):
        s = I.new_socket(nombre, in_out="INPUT", socket_type="NodeSocketFloat")
        s.default_value, s.min_value, s.max_value = valor, 0.0, 10.0
    for nombre in ("Arista", "Cavidad", "Arriba", "Pie", "Ruptura", "Grano"):
        I.new_socket(nombre, in_out="OUTPUT", socket_type="NodeSocketFloat")
    g = G(ng)
    gi, go = g.n("NodeGroupInput"), g.n("NodeGroupOutput")
    geo = g.n("ShaderNodeNewGeometry")
    P, Nn = geo.outputs["Position"], geo.outputs["Normal"]     # en coordenadas del mundo: continuas entre objetos
    # Ruptura: manchas grandes (fBM con distorsión = domain warping) por manchas finas. Evita bordes de máscara rectos.
    grande = g.rango(g.ruido(P, 0.9, 6.0, 0.55, 0.4), 0.40, 0.62)
    fina = g.rango(g.ruido(P, 9.0, 4.0, 0.6), 0.30, 0.70)
    g.con(g.m("MULTIPLY", grande, g.m("ADD", 0.6, g.m("MULTIPLY", fina, 0.4))), go.inputs["Ruptura"])
    # Grano del polvo (relieve positivo, se usa en el Bump de cada material)
    g.con(g.ruido(P, 420.0, 3.0, 0.5), go.inputs["Grano"])
    # Arista: producto punto entre la normal biselada y la normal real. En una arista de 90°, en el filo la normal
    # biselada está a 45° -> cos 45° = 0,707; en la cara plana -> 1. El radio varía con ruido (ancho irregular).
    radio = g.m("MULTIPLY", gi.outputs["Radio arista"], g.rango(g.ruido(P, 6.0, 3.0), 0.3, 0.7, 0.35, 1.0))
    bev = g.n("ShaderNodeBevel", samples=MUESTRAS_BEVEL)
    g.con(radio, bev.inputs["Radius"])
    dot = g.n("ShaderNodeVectorMath", operation="DOT_PRODUCT")
    g.L.new(bev.outputs["Normal"], dot.inputs[0])
    g.L.new(Nn, dot.inputs[1])
    g.con(g.rango(dot.outputs["Value"], 0.70, 0.995, 1.0, 0.0, suave=False), go.inputs["Arista"])
    # Cavidad: AO con otros objetos (no solo local) -> rincones, juntas, encuentros muro/vereda, valles de nervios
    ao = g.n("ShaderNodeAmbientOcclusion", samples=MUESTRAS_AO, only_local=False, inside=False)
    g.L.new(gi.outputs["Distancia AO"], ao.inputs["Distance"])
    g.con(g.rango(g.m("SUBTRACT", 1.0, ao.outputs["AO"]), 0.10, 0.55), go.inputs["Cavidad"])
    # Arriba: caras que miran al cielo (componente Z de la normal del mundo)
    sep = g.n("ShaderNodeSeparateXYZ")
    g.L.new(Nn, sep.inputs[0])
    g.con(g.rango(sep.outputs["Z"], 0.55, 0.95), go.inputs["Arriba"])
    # Pie: franja al pie de las caras verticales; la altura se deforma con ruido (salpicado irregular, no una línea)
    psep = g.n("ShaderNodeSeparateXYZ")
    g.L.new(P, psep.inputs[0])
    z = g.m("ADD", psep.outputs["Z"], g.m("MULTIPLY", g.m("SUBTRACT", g.ruido(P, 3.0, 4.0, 0.6), 0.5), 0.18))
    altura = g.n("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP", clamp=True)
    g.con(z, altura.inputs["Value"])
    altura.inputs["From Min"].default_value = 0.0
    g.L.new(gi.outputs["Altura salpicado"], altura.inputs["From Max"])
    altura.inputs["To Min"].default_value, altura.inputs["To Max"].default_value = 1.0, 0.0
    vertical = g.rango(g.m("ABSOLUTE", sep.outputs["Z"]), 0.45, 0.70, 1.0, 0.0)
    g.con(g.m("MULTIPLY", altura.outputs["Result"], vertical), go.inputs["Pie"])
    return ng


MASC = grupo_mascaras()


# ------------------------------------------------------------------ inserción en los materiales
def bsdf(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def fuente(g, sock):
    """Socket que hoy alimenta 'sock' (o un nodo con su valor fijo)."""
    if sock.is_linked:
        return sock.links[0].from_socket
    if sock.type == "RGBA":
        nodo = g.n("ShaderNodeRGB")
        nodo.outputs[0].default_value = sock.default_value
    else:
        nodo = g.n("ShaderNodeValue")
        nodo.outputs[0].default_value = sock.default_value
    return nodo.outputs[0]


def mascaras(g, radio=0.01, dist_ao=0.30, salpicado=0.30):
    nodo = g.n("ShaderNodeGroup")
    nodo.node_tree = MASC
    nodo.inputs["Radio arista"].default_value = radio
    nodo.inputs["Distancia AO"].default_value = dist_ao
    nodo.inputs["Altura salpicado"].default_value = salpicado
    return nodo.outputs


def metalico_binario(mat, valor_p1):
    """La rama P1 de la mezcla de paletas pasa al valor físico (0 pintura/óxido, 1 metal desnudo)."""
    b = bsdf(mat)
    s = b.inputs["Metallic"]
    if s.is_linked and s.links[0].from_node.type == "MIX":
        mix = s.links[0].from_node
        a = next(x for x in mix.inputs if x.name == "A" and x.type == "VALUE")
        if not a.is_linked:
            a.default_value = valor_p1
    elif not s.is_linked:
        s.default_value = valor_p1


def capa_polvo(mat, w_cav=0.5, w_arr=0.6, w_pie=0.0, opacidad=0.5, radio=0.01, dist_ao=0.30, alto_pie=0.30,
               rug_polvo=0.92, solo_horizontal_cav=True, pelicula=0.0):
    """Polvo del altiplano sobre el material: mezcla color, rugosidad, metálico y relieve con las máscaras.
    pelicula: velo de polvo en toda la superficie (en lo oscuro se nota: nada queda negro puro en un lugar polvoriento)."""
    nt = mat.node_tree
    g = G(nt)
    b = bsdf(mat)
    M = mascaras(g, radio, dist_ao, alto_pie)
    k = g.n("ShaderNodeAttribute", attribute_type="VIEW_LAYER", attribute_name="polvo").outputs["Fac"]
    # el polvo se asienta sobre todo en lo que mira hacia arriba: en cavidades verticales pesa un 35 %
    cav = M["Cavidad"]
    if solo_horizontal_cav:
        cav = g.m("MULTIPLY", cav, g.m("ADD", 0.35, g.m("MULTIPLY", M["Arriba"], 0.65)))
    polvo = g.m("MULTIPLY", g.m("MAXIMUM", g.m("MULTIPLY", cav, w_cav), g.m("MULTIPLY", M["Arriba"], w_arr)), M["Ruptura"])
    if pelicula:
        polvo = g.m("MAXIMUM", polvo, g.m("MULTIPLY", g.m("ADD", 0.4, g.m("MULTIPLY", M["Ruptura"], 0.6)), pelicula))
    polvo = g.m("MULTIPLY", polvo, g.m("MULTIPLY", k, opacidad), clamp=True)
    pie = g.m("MULTIPLY", g.m("MULTIPLY", M["Pie"], w_pie), g.m("MULTIPLY", k, g.m("ADD", 0.45, g.m("MULTIPLY", M["Ruptura"], 0.55))), clamp=True)
    total = g.m("MAXIMUM", polvo, pie)
    color = g.mezcla(polvo, fuente(g, b.inputs["Base Color"]), srgb(POLVO))
    color = g.mezcla(pie, color, srgb(SALPICADO))
    g.L.new(color, b.inputs["Base Color"])
    g.L.new(g.mezcla(total, fuente(g, b.inputs["Roughness"]), rug_polvo, "FLOAT"), b.inputs["Roughness"])
    g.L.new(g.m("MULTIPLY", fuente(g, b.inputs["Metallic"]), g.m("SUBTRACT", 1.0, total)), b.inputs["Metallic"])
    # relieve positivo del polvo (la suciedad se deposita encima): Bump encadenado al relieve que ya hubiera
    bump = g.n("ShaderNodeBump")
    bump.inputs["Strength"].default_value, bump.inputs["Distance"].default_value = 0.25, 0.0004
    g.L.new(g.m("MULTIPLY", total, M["Grano"]), bump.inputs["Height"])
    if b.inputs["Normal"].is_linked:
        g.L.new(b.inputs["Normal"].links[0].from_socket, bump.inputs["Normal"])
    g.L.new(bump.outputs["Normal"], b.inputs["Normal"])
    return g, M


def rugosidad_difusa(mat, valor):
    bsdf(mat).inputs["Diffuse Roughness"].default_value = valor


def ruido_rugosidad(mat, amplitud, escala):
    nt = mat.node_tree
    g = G(nt)
    b = bsdf(mat)
    geo = g.n("ShaderNodeNewGeometry")
    var = g.m("MULTIPLY", g.m("SUBTRACT", g.ruido(geo.outputs["Position"], escala, 6.0), 0.5), 2 * amplitud)
    g.L.new(g.m("ADD", fuente(g, b.inputs["Roughness"]), var, clamp=True), b.inputs["Roughness"])


def corten_inteligente(mat, fac_corten, variacion=0.30):
    """Pátina que responde a la geometría. fac_corten: socket 0..1 que dice dónde el material es corten
    (la rama P1 de la celosía o la propiedad letras_corten del letrero). variacion: diferencia de valor entre piezas
    (0,30 = ±15 % en las planchas; en las letras, menos, para que no parezca un defecto)."""
    nt = mat.node_tree
    g = G(nt)
    b = bsdf(mat)
    M = mascaras(g, radio=0.004, dist_ao=0.15)
    geo = g.n("ShaderNodeNewGeometry")
    # 1. variación por plancha (cada plancha de 1 x 2 m es una isla), como lotes distintos de acero:
    #    ±15 % de valor y, en parte de las planchas, un tono más pardo
    isla = geo.outputs["Random Per Island"]
    lote = g.m("ADD", 1.0 - variacion / 2, g.m("MULTIPLY", isla, variacion))
    base = fuente(g, b.inputs["Base Color"])
    vm = g.n("ShaderNodeVectorMath", operation="SCALE")
    g.L.new(base, vm.inputs[0])
    g.con(g.mezcla(fac_corten, 1.0, lote, "FLOAT"), vm.inputs["Scale"])
    pardo = g.m("MULTIPLY", g.rango(g.m("FRACT", g.m("MULTIPLY", isla, 7.31)), 0.55, 1.0, 0.0, 1.5 * variacion), fac_corten)
    color = g.mezcla(pardo, vm.outputs["Vector"], srgb(CORTEN_LOTE))
    # 2. caras superiores (retienen humedad y depósitos) y cantos: pátina más densa y oscura
    denso = g.m("MAXIMUM", g.m("MULTIPLY", M["Arriba"], 0.65), g.m("MULTIPLY", M["Arista"], 0.40))
    denso = g.m("MULTIPLY", g.m("MULTIPLY", denso, g.m("ADD", 0.5, g.m("MULTIPLY", M["Ruptura"], 0.5))), fac_corten)
    color = g.mezcla(denso, color, srgb(CORTEN_DENSO))
    g.L.new(color, b.inputs["Base Color"])
    # 3. rugosidad: alta y con más rugosidad donde la pátina es densa; rugosidad difusa del óxido
    rug = g.m("ADD", fuente(g, b.inputs["Roughness"]), g.m("MULTIPLY", denso, 0.08), clamp=True)
    g.L.new(rug, b.inputs["Roughness"])
    dif = g.mezcla(fac_corten, 0.0, 0.5, "FLOAT")
    g.L.new(dif, b.inputs["Diffuse Roughness"])


def p1_de(mat):
    """Factor 'es P1' (1 - propuesta) para materiales de dos paletas."""
    g = G(mat.node_tree)
    p = g.n("ShaderNodeAttribute", attribute_type="VIEW_LAYER", attribute_name="propuesta").outputs["Fac"]
    return g.m("SUBTRACT", 1.0, p)


def listones_por_isla(mat):
    nt = mat.node_tree
    g = G(nt)
    b = bsdf(mat)
    geo = g.n("ShaderNodeNewGeometry")
    isla = geo.outputs["Random Per Island"]
    onda = next(n for n in nt.nodes if n.type == "TEX_WAVE")
    g.con(g.m("MULTIPLY", isla, 6.2832), onda.inputs["Phase Offset"])      # veta distinta en cada listón
    vm = g.n("ShaderNodeVectorMath", operation="SCALE")
    g.L.new(fuente(g, b.inputs["Base Color"]), vm.inputs[0])
    g.con(g.m("ADD", 0.92, g.m("MULTIPLY", isla, 0.16)), vm.inputs["Scale"])  # ±8 % de valor por listón
    g.L.new(vm.outputs["Vector"], b.inputs["Base Color"])
    g.L.new(g.m("ADD", fuente(g, b.inputs["Roughness"]), g.m("MULTIPLY", g.m("SUBTRACT", isla, 0.5), 0.12), clamp=True),
            b.inputs["Roughness"])


def galvanizado_spangle(mat):
    nt = mat.node_tree
    g = G(nt)
    b = bsdf(mat)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Base Color"].default_value = srgb("#B4B8BA")
    geo = g.n("ShaderNodeNewGeometry")
    vor = g.n("ShaderNodeTexVoronoi", feature="F1")
    g.L.new(geo.outputs["Position"], vor.inputs["Vector"])
    vor.inputs["Scale"].default_value = 60.0                  # cristales de zinc de 1-2 cm
    celda = g.n("ShaderNodeSeparateColor")
    g.L.new(vor.outputs["Color"], celda.inputs[0])
    g.L.new(g.m("ADD", 0.30, g.m("MULTIPLY", celda.outputs[0], 0.16)), b.inputs["Roughness"])
    vm = g.n("ShaderNodeVectorMath", operation="SCALE")
    g.con(srgb("#B4B8BA")[:3], vm.inputs[0])
    g.con(g.m("ADD", 0.92, g.m("MULTIPLY", celda.outputs[1], 0.16)), vm.inputs["Scale"])
    g.L.new(vm.outputs["Vector"], b.inputs["Base Color"])


def asfalto_arido(mat):
    nt = mat.node_tree
    g = G(nt)
    b = bsdf(mat)
    geo = g.n("ShaderNodeNewGeometry")
    vor = g.n("ShaderNodeTexVoronoi", feature="F1")
    g.L.new(geo.outputs["Position"], vor.inputs["Vector"])
    vor.inputs["Scale"].default_value = 160.0                 # árido de 4 a 8 mm
    celda = g.n("ShaderNodeSeparateColor")
    g.L.new(vor.outputs["Color"], celda.inputs[0])
    piedra = g.m("MULTIPLY", g.m("GREATER_THAN", celda.outputs[0], 0.82), g.m("LESS_THAN", vor.outputs["Distance"], 0.32))
    g.L.new(g.mezcla(g.m("MULTIPLY", piedra, 0.55), fuente(g, b.inputs["Base Color"]), srgb("#77736C")), b.inputs["Base Color"])
    g.L.new(g.mezcla(piedra, fuente(g, b.inputs["Roughness"]), 0.6, "FLOAT"), b.inputs["Roughness"])
    rugosidad_difusa(mat, 0.6)


def revoque_llana(mat):
    """Ondas de llana: un relieve de muy baja frecuencia sumado al grano del mortero."""
    nt = mat.node_tree
    g = G(nt)
    bump = next(n for n in nt.nodes if n.type == "BUMP")
    h = bump.inputs["Height"]
    geo = g.n("ShaderNodeNewGeometry")
    onda = g.ruido(geo.outputs["Position"], 1.4, 2.0, 0.5)
    g.L.new(g.m("ADD", h.links[0].from_socket, g.m("MULTIPLY", onda, 1.2)), h)


def mat(nombre):
    return bpy.data.materials["UY_" + nombre]


t0 = time.time()
# 1. metálico binario (rama P1)
for nombre, valor in (("CHAPA_CUBIERTA", 0.0), ("CHAPA_ANTEPECHO_REMATES", 0.0), ("BASTIDOR_CELOSIAS", 0.0),
                      ("CELOSIA_CORTEN_O_BLANCA", 0.0)):
    metalico_binario(mat(nombre), valor)
bsdf(mat("ALUMINIO_ANTRACITA_MATE")).inputs["Metallic"].default_value = 0.0
let = bsdf(mat("LETRERO_BLANCO_O_CORTEN")).inputs["Metallic"]
if let.is_linked and let.links[0].from_node.type == "MIX":
    next(x for x in let.links[0].from_node.inputs if x.name == "B" and x.type == "VALUE").default_value = 0.0
# 2. corten inteligente (celosías en P1 y letras corten)
corten_inteligente(mat("CELOSIA_CORTEN_O_BLANCA"), p1_de(mat("CELOSIA_CORTEN_O_BLANCA")))
gl = G(mat("LETRERO_BLANCO_O_CORTEN").node_tree)
corten_inteligente(mat("LETRERO_BLANCO_O_CORTEN"),
                   gl.n("ShaderNodeAttribute", attribute_type="VIEW_LAYER", attribute_name="letras_corten").outputs["Fac"],
                   variacion=0.10)
# 3. polvo del altiplano
for nombre in ("REVOQUE_CONTINUO", "REVOQUE_FACHADA_BUNAS"):
    revoque_llana(mat(nombre))
    rugosidad_difusa(mat(nombre), 0.8)
    capa_polvo(mat(nombre), w_cav=0.45, w_arr=0.6, w_pie=0.85, opacidad=0.55)
for nombre in ("CHAPA_ANTEPECHO_REMATES", "CHAPA_CUBIERTA"):
    ruido_rugosidad(mat(nombre), 0.06, 2.5)
    capa_polvo(mat(nombre), w_cav=0.6, w_arr=0.55, opacidad=0.60, dist_ao=0.06, pelicula=0.12)
capa_polvo(mat("ALUMINIO_ANTRACITA_MATE"), w_cav=0.5, w_arr=0.7, w_pie=0.6, opacidad=0.60, dist_ao=0.10, pelicula=0.08)
capa_polvo(mat("BASTIDOR_CELOSIAS"), w_cav=0.4, w_arr=0.6, opacidad=0.50, dist_ao=0.10, pelicula=0.08)
galvanizado_spangle(mat("ACERO_GALVANIZADO"))
capa_polvo(mat("ACERO_GALVANIZADO"), w_cav=0.3, w_arr=0.7, opacidad=0.55, dist_ao=0.05, pelicula=0.10)
capa_polvo(mat("CELOSIA_CORTEN_O_BLANCA"), w_cav=0.0, w_arr=0.0, w_pie=0.7, opacidad=0.4)
capa_polvo(mat("HORMIGON_FRATASADO"), w_cav=0.9, w_arr=0.0, opacidad=0.6, dist_ao=0.35, solo_horizontal_cav=False)
rugosidad_difusa(mat("HORMIGON_FRATASADO"), 0.7)
rugosidad_difusa(mat("HORMIGON_VISTO"), 0.7)
capa_polvo(mat("HORMIGON_VISTO"), w_cav=0.5, w_arr=0.5, w_pie=0.6, opacidad=0.5)
listones_por_isla(mat("CIELO_LISTONES"))
asfalto_arido(mat("ASFALTO"))
print(f"[PRUEBA] materiales modificados en {time.time() - t0:.1f} s", flush=True)

# ------------------------------------------------------------------ diagnóstico de máscaras (override de material)
diag = bpy.data.materials.new("UY_DIAG_MASCARAS")
if diag.node_tree is None:
    diag.use_nodes = True
gd = G(diag.node_tree)
for n in list(diag.node_tree.nodes):
    if n.type != "OUTPUT_MATERIAL":
        diag.node_tree.nodes.remove(n)
Md = mascaras(gd, radio=0.01, dist_ao=0.10)     # AO de 0,10 m: lee nervios, juntas y encuentros sin saturar
cc = gd.n("ShaderNodeCombineColor")
gd.L.new(Md["Arista"], cc.inputs[0])
gd.L.new(Md["Cavidad"], cc.inputs[1])
gd.L.new(gd.m("MAXIMUM", Md["Arriba"], Md["Pie"]), cc.inputs[2])
em = gd.n("ShaderNodeEmission")
gd.L.new(cc.outputs[0], em.inputs["Color"])
gd.L.new(em.outputs[0], next(n for n in diag.node_tree.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
vl = sc.view_layers[0]
vt, look = sc.view_settings.view_transform, sc.view_settings.look
vl.material_override = diag
sc.view_settings.view_transform, sc.view_settings.look = "Standard", "None"
r.resolution_x, r.resolution_y = ancho * 3 // 4, round(ancho * 3 // 4 * 9 / 16)
cy.samples = max(24, muestras // 3)
for c in camaras:
    render(c, "B_MASCARAS")
vl.material_override = None
sc.view_settings.view_transform, sc.view_settings.look = vt, look
r.resolution_x, r.resolution_y = ancho, round(ancho * 9 / 16)
cy.samples = muestras
for c in camaras:
    render(c, "C_DESPUES")
for c in camaras:
    a, d = tiempos[f"{c}_A_ANTES"], tiempos[f"{c}_C_DESPUES"]
    print(f"[COSTO] {c}: antes {a:.0f} s, después {d:.0f} s ({100 * (d / a - 1):+.0f} %)", flush=True)
bpy.ops.wm.save_as_mainfile(filepath=f"{salida}/prueba_materiales.blend", compress=True)
