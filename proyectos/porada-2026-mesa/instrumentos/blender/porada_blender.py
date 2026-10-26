"""Mesa Porada en Blender: un árbol de Geometry Nodes paramétrico, materiales procedurales y renders (Cycles, CPU).

    pip install bpy==5.2.3                       # Blender como módulo de Python (Python 3.13)
    python porada_blender.py                     # construye la escena, guarda el .blend y renderiza todas las tomas
    python porada_blender.py --solo-blend        # solo la escena (para abrirla en Blender y mover parámetros)
    python porada_blender.py --muestras 32 --tomas nodo_AB nodo_B2

Escribe ../../05_consolidar/blender/mesa_porada.blend y ../../05_consolidar/renders/*.png.
Las medidas son las del instrumento (instrumentos/mesa/versiones.py), en metros.
"""
import argparse
import math
import time
from pathlib import Path

import bpy
import addon_utils  # disponible después de importar bpy
from mathutils import Vector

RAIZ = Path(__file__).resolve().parents[2]
SALIDA_BLEND = RAIZ / "05_consolidar" / "blender"
SALIDA_RENDER = RAIZ / "05_consolidar" / "renders"

COMUN = dict(largo=2.4, ancho=1.0, alto=0.75, espesor=0.04, extremo=0.45, pie_x=0.18, junta=0.003, apoyo_central=True)
VERSIONES = {
    "B2": dict(COMUN, n_tablas=6, collar=False, servicio=False),
    "AB": dict(COMUN, n_tablas=6, collar=True, servicio=False),
    "B3": dict(COMUN, n_tablas=7, collar=False, servicio=True),
}
# Familia del sistema B (E7, «assortment»): las tablas siguen ≤ 182 mm (E2b).
FAMILIA = {
    "banco": dict(VERSIONES["B2"], largo=1.8, ancho=0.36, alto=0.45, extremo=0.30, n_tablas=2, apoyo_central=False),
    "consola": dict(VERSIONES["B2"], largo=1.8, ancho=0.45, alto=0.75, extremo=0.30, n_tablas=3, apoyo_central=False),
    "mesa": VERSIONES["B3"],
}


# ----------------------------------------------------------------------------------------------------------------
# Geometry Nodes: un ayudante pequeño para escribir el árbol como expresiones
# ----------------------------------------------------------------------------------------------------------------

class Arbol:
    def __init__(self, nombre):
        self.ng = bpy.data.node_groups.new(nombre, "GeometryNodeTree")
        self.nodes, self.links = self.ng.nodes, self.ng.links
        self.entrada = self.nodes.new("NodeGroupInput")
        self.salida = self.nodes.new("NodeGroupOutput")
        self.marco, self.col = None, {}
        self.ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        self.ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

    def parametro(self, nombre, tipo, valor, mini=None, maxi=None, panel=None):
        s = self.ng.interface.new_socket(nombre, in_out="INPUT", socket_type=tipo, parent=panel)
        if valor is not None and hasattr(s, "default_value"):
            s.default_value = valor
        if mini is not None:
            s.min_value, s.max_value = mini, maxi
        return s

    def panel(self, nombre):
        return self.ng.interface.new_panel(nombre)

    def __getitem__(self, nombre):
        return self.entrada.outputs[nombre]

    def seccion(self, nombre):
        """Agrupa los nodos siguientes en un marco con nombre (para leer el árbol en Blender)."""
        self.marco = self.nodes.new("NodeFrame")
        self.marco.label = nombre
        self.col[nombre] = 0
        self._y = -600 * (len(self.col) - 1)
        return self.marco

    def nodo(self, tipo, **props):
        n = self.nodes.new(tipo)
        for k, v in props.items():
            setattr(n, k, v)
        if self.marco is not None:
            n.parent = self.marco
            i = self.col[self.marco.label]
            n.location = (200 * (i // 6), self._y - 110 * (i % 6))
            self.col[self.marco.label] += 1
        return n

    def _a(self, socket, valor):
        if hasattr(valor, "is_output") or isinstance(valor, bpy.types.NodeSocket):
            self.links.new(valor, socket)
        elif valor is not None:
            socket.default_value = valor

    def m(self, op, a, b=None):
        n = self.nodo("ShaderNodeMath", operation=op)
        self._a(n.inputs[0], a)
        if b is not None:
            self._a(n.inputs[1], b)
        return n.outputs[0]

    def suma(self, a, b): return self.m("ADD", a, b)
    def resta(self, a, b): return self.m("SUBTRACT", a, b)
    def mult(self, a, b): return self.m("MULTIPLY", a, b)
    def div(self, a, b): return self.m("DIVIDE", a, b)
    def minimo(self, a, b): return self.m("MINIMUM", a, b)

    def vec(self, x=0.0, y=0.0, z=0.0):
        n = self.nodo("ShaderNodeCombineXYZ")
        for s, v in zip(n.inputs, (x, y, z)):
            self._a(s, v)
        return n.outputs[0]

    def cubo(self, tam, centro):
        c = self.nodo("GeometryNodeMeshCube")
        self._a(c.inputs["Size"], tam)
        t = self.nodo("GeometryNodeTransform")
        self.links.new(c.outputs["Mesh"], t.inputs["Geometry"])
        self._a(t.inputs["Translation"], centro)
        return t.outputs["Geometry"]

    def linea(self, n, inicio, paso):
        ln = self.nodo("GeometryNodeMeshLine", mode="OFFSET")
        self._a(ln.inputs["Count"], n)
        self._a(ln.inputs["Start Location"], inicio)
        self._a(ln.inputs["Offset"], paso)
        return ln.outputs["Mesh"]

    def instanciar(self, puntos, geom, seleccion=None):
        i = self.nodo("GeometryNodeInstanceOnPoints")
        self.links.new(puntos, i.inputs["Points"])
        self.links.new(geom, i.inputs["Instance"])
        if seleccion is not None:
            self.links.new(seleccion, i.inputs["Selection"])
        r = self.nodo("GeometryNodeRealizeInstances")
        self.links.new(i.outputs["Instances"], r.inputs["Geometry"])
        return r.outputs["Geometry"]

    def unir(self, *geoms):
        j = self.nodo("GeometryNodeJoinGeometry")
        for g in reversed(geoms):
            self.links.new(g, j.inputs["Geometry"])
        return j.outputs["Geometry"]

    def segun(self, condicion, si_no, si_si, tipo="GEOMETRY"):
        s = self.nodo("GeometryNodeSwitch", input_type=tipo)
        self._a(s.inputs["Switch"], condicion)
        self._a(s.inputs["False"], si_no)
        self._a(s.inputs["True"], si_si)
        return s.outputs[0]

    def vaciar(self, malla, cortador):
        b = self.nodo("GeometryNodeMeshBoolean", operation="DIFFERENCE", solver="EXACT")
        self.links.new(malla, b.inputs["Mesh 1"])
        self.links.new(cortador, b.inputs["Mesh 2"])
        return b.outputs["Mesh"]

    def veta(self, geom, direccion):
        """Guarda la dirección de la fibra (0 X, 1 Y, 2 Z) para que el material la oriente pieza por pieza."""
        n = self.nodo("GeometryNodeStoreNamedAttribute", data_type="FLOAT", domain="POINT")
        self.links.new(geom, n.inputs["Geometry"])
        n.inputs["Name"].default_value = "veta"
        n.inputs["Value"].default_value = float(direccion)
        return n.outputs["Geometry"]

    def material(self, geom, mat):
        n = self.nodo("GeometryNodeSetMaterial")
        self.links.new(geom, n.inputs["Geometry"])
        self._a(n.inputs["Material"], mat)
        return n.outputs["Geometry"]


def arbol_mesa():
    """El árbol «Mesa Porada»: todas las versiones y la familia salen de los mismos parámetros."""
    a = Arbol("Mesa Porada")
    p_med = a.panel("Medidas")
    a.parametro("Largo", "NodeSocketFloat", 2.4, 0.6, 4.0, p_med)
    a.parametro("Ancho", "NodeSocketFloat", 1.0, 0.3, 1.4, p_med)
    a.parametro("Alto", "NodeSocketFloat", 0.75, 0.35, 1.1, p_med)
    a.parametro("Espesor", "NodeSocketFloat", 0.04, 0.02, 0.06, p_med)
    p_tab = a.panel("Tablas (propuesta B)")
    a.parametro("N tablas", "NodeSocketInt", 6, 1, 12, p_tab)
    a.parametro("Junta", "NodeSocketFloat", 0.003, 0.0, 0.01, p_tab)
    a.parametro("Tabla de servicio", "NodeSocketBool", False, panel=p_tab)
    p_cab = a.panel("Caballetes")
    a.parametro("Extremo a caballete", "NodeSocketFloat", 0.45, 0.1, 0.8, p_cab)
    a.parametro("Ancho del pie", "NodeSocketFloat", 0.18, 0.06, 0.3, p_cab)
    a.parametro("Apoyo central", "NodeSocketBool", True, panel=p_cab)
    p_uni = a.panel("Unión (propuesta A)")
    a.parametro("Collar de piedra", "NodeSocketBool", False, panel=p_uni)
    p_mat = a.panel("Materiales")
    for nombre in ("Madera", "Fresno", "Piedra"):
        a.parametro(nombre, "NodeSocketMaterial", None, panel=p_mat)

    L, W, H, t = a["Largo"], a["Ancho"], a["Alto"], a["Espesor"]
    n, g = a["N tablas"], a["Junta"]

    a.seccion("Medidas derivadas")
    xc = a.resta(a.div(L, 2), a["Extremo a caballete"])               # eje del caballete
    zt = a.resta(H, t)                                                  # cara inferior del tablero
    zc = a.resta(zt, 0.06)                                              # cara inferior del cabezal
    b = a.div(a.resta(W, a.mult(a.resta(n, 1), g)), n)                  # ancho de tabla
    zs = a.minimo(0.30, a.mult(H, 0.4))                                 # eje del travesaño
    vuelo = a.suma(0.11, a.mult(a["Collar de piedra"], 0.03))           # la espiga crece si hay collar
    y0 = a.suma(a.mult(W, -0.5), a.mult(b, 0.5))
    paso_y = a.vec(0, a.suma(b, g), 0)

    a.seccion("Tablas sueltas (B)")
    puntos_tablas = a.linea(n, a.vec(0, y0, 0), paso_y)
    idx = a.nodo("GeometryNodeInputIndex").outputs[0]
    cmp = a.nodo("FunctionNodeCompare", data_type="INT", operation="EQUAL")
    a.links.new(idx, cmp.inputs["A"])
    a._a(cmp.inputs["B"], a.m("FLOOR", a.div(n, 2)))
    no_servicio = a.nodo("FunctionNodeBooleanMath", operation="NAND")
    a.links.new(cmp.outputs[0], no_servicio.inputs[0])
    a.links.new(a["Tabla de servicio"], no_servicio.inputs[1])
    tabla = a.veta(a.cubo(a.vec(L, b, t), a.vec(0, 0, a.suma(zt, a.mult(t, 0.5)))), 0)
    tablas = a.instanciar(puntos_tablas, tabla, no_servicio.outputs[0])

    a.seccion("Tabla de servicio con mármol asentado (B3)")
    canal = a.vec(1.4, 0.1, 0.02)
    yc_serv = a.suma(y0, a.mult(a.m("FLOOR", a.div(n, 2)), a.suma(b, g)))
    tabla_serv = a.cubo(a.vec(L, b, t), a.vec(0, yc_serv, a.suma(zt, a.mult(t, 0.5))))
    cortador = a.cubo(a.vec(1.4, 0.1, 0.03), a.vec(0, yc_serv, a.resta(H, 0.005)))
    tabla_serv = a.veta(a.vaciar(tabla_serv, cortador), 0)
    marmol_serv = a.cubo(canal, a.vec(0, yc_serv, a.resta(H, 0.01)))
    vacio = a.nodo("GeometryNodeJoinGeometry").outputs[0]
    tabla_serv = a.segun(a["Tabla de servicio"], vacio, tabla_serv)
    marmol_serv = a.segun(a["Tabla de servicio"], vacio, marmol_serv)

    a.seccion("Caballetes")
    pie = a.veta(a.cubo(a.vec(a["Ancho del pie"], a.mult(W, 0.8), 0.09), a.vec(0, 0, 0.045)), 1)
    montante = a.veta(a.cubo(a.vec(0.06, a.minimo(0.26, a.mult(W, 0.5)), a.resta(zc, 0.09)),
                             a.vec(0, 0, a.mult(a.suma(zc, 0.09), 0.5))), 2)
    cabezal = a.veta(a.cubo(a.vec(0.08, a.mult(W, 0.85), 0.06), a.vec(0, 0, a.suma(zc, 0.03))), 1)
    puntos_cab = a.linea(2, a.vec(a.mult(xc, -1), 0, 0), a.vec(a.mult(xc, 2), 0, 0))
    caballetes = a.instanciar(puntos_cab, a.unir(pie, montante, cabezal))

    a.seccion("Travesaño, llaves y collar (A)")
    xt = a.suma(xc, a.suma(0.03, vuelo))
    travesano = a.veta(a.cubo(a.vec(a.mult(xt, 2), 0.045, 0.11), a.vec(0, 0, zs)), 0)
    xk = a.suma(xc, a.suma(0.044, a.mult(a["Collar de piedra"], 0.07)))
    llaves = a.instanciar(a.linea(2, a.vec(a.mult(xk, -1), 0, zs), a.vec(a.mult(xk, 2), 0, 0)),
                          a.veta(a.cubo(a.vec(0.028, 0.02, 0.17), a.vec(0, 0, 0)), 2))
    xcol = a.suma(xc, 0.065)
    collares = a.instanciar(a.linea(2, a.vec(a.mult(xcol, -1), 0, zs), a.vec(a.mult(xcol, 2), 0, 0)),
                            a.cubo(a.vec(0.07, 0.11, 0.15), a.vec(0, 0, 0)))
    collares = a.segun(a["Collar de piedra"], vacio, collares)

    a.seccion("Clavijas y cuñas (E9)")
    z_clav = a.resta(zc, 0.04)
    clavija = a.veta(a.cubo(a.vec(0.02, 0.02, a.resta(a.resta(H, 0.01), z_clav)),
                            a.vec(0, 0, a.mult(a.suma(a.resta(H, 0.01), z_clav), 0.5))), 2)
    cuna = a.veta(a.cubo(a.vec(0.06, 0.008, 0.015), a.vec(0, 0, a.resta(zc, 0.0225))), 0)
    puntos_clav = a.unir(a.linea(n, a.vec(a.mult(xc, -1), y0, 0), paso_y), a.linea(n, a.vec(xc, y0, 0), paso_y))
    clavijas = a.instanciar(puntos_clav, a.unir(clavija, cuna))

    a.seccion("Apoyo central (E8)")
    z_bajo = a.suma(zs, 0.055)
    puntal = a.veta(a.cubo(a.vec(0.06, 0.10, a.resta(zc, z_bajo)), a.vec(0, 0, a.mult(a.suma(zc, z_bajo), 0.5))), 2)
    cab_central = a.veta(a.cubo(a.vec(0.08, a.mult(W, 0.85), 0.06), a.vec(0, 0, a.suma(zc, 0.03))), 1)
    central = a.segun(a["Apoyo central"], vacio, a.unir(puntal, cab_central))

    a.seccion("Materiales y salida")
    madera = a.material(a.unir(tablas, tabla_serv, caballetes, travesano, central), a["Madera"])
    fresno = a.material(a.unir(llaves, clavijas), a["Fresno"])
    piedra = a.material(a.unir(collares, marmol_serv), a["Piedra"])
    a.links.new(a.unir(madera, fresno, piedra), a.salida.inputs[0])
    a.entrada.location, a.salida.location = (-400, 0), (2600, 0)
    return a.ng


# ----------------------------------------------------------------------------------------------------------------
# Materiales procedurales
# ----------------------------------------------------------------------------------------------------------------

def _rampa(nodos, paradas):
    r = nodos.new("ShaderNodeValToRGB")
    els = r.color_ramp.elements
    while len(els) > len(paradas):
        els.remove(els[-1])
    while len(els) < len(paradas):
        els.new(0.5)
    for e, (pos, col) in zip(els, paradas):
        e.position, e.color = pos, (*col, 1.0)
    return r


def material_madera(nombre, oscuro, medio, claro, veta=(0.25, 9.0, 9.0), rugosidad=0.42):
    """Veta alargada en X: ondas (anillos) deformadas por ruido; el aceite deja una rugosidad satinada."""
    mat = bpy.data.materials.new(nombre)
    nt = mat.node_tree
    nd, ln = nt.nodes, nt.links
    bsdf = nd["Principled BSDF"]
    coord = nd.new("ShaderNodeTexCoord")
    sep = nd.new("ShaderNodeSeparateXYZ")
    ln.new(coord.outputs["Object"], sep.inputs["Vector"])
    ejes = []
    for orden in ((0, 1, 2), (1, 0, 2), (2, 1, 0)):            # la fibra va por el primer eje
        c = nd.new("ShaderNodeCombineXYZ")
        for i, j in enumerate(orden):
            ln.new(sep.outputs[j], c.inputs[i])
        ejes.append(c.outputs[0])
    atr = nd.new("ShaderNodeAttribute")
    atr.attribute_name = "veta"
    vec = ejes[0]
    for k, eje in ((1, ejes[1]), (2, ejes[2])):
        es = nd.new("ShaderNodeMath")
        es.operation = "COMPARE"
        ln.new(atr.outputs["Fac"], es.inputs[0])
        es.inputs[1].default_value, es.inputs[2].default_value = float(k), 0.1
        mx = nd.new("ShaderNodeMix")
        mx.data_type = "VECTOR"
        ln.new(es.outputs[0], mx.inputs["Factor"])
        ln.new(vec, mx.inputs["A"])
        ln.new(eje, mx.inputs["B"])
        vec = mx.outputs["Result"]
    mapa = nd.new("ShaderNodeMapping")
    mapa.inputs["Scale"].default_value = veta
    ln.new(vec, mapa.inputs["Vector"])
    ruido = nd.new("ShaderNodeTexNoise")
    ruido.inputs["Scale"].default_value, ruido.inputs["Detail"].default_value = 4.0, 8.0
    ln.new(mapa.outputs["Vector"], ruido.inputs["Vector"])
    onda = nd.new("ShaderNodeTexWave")
    onda.wave_type, onda.bands_direction = "BANDS", "Y"
    onda.inputs["Scale"].default_value, onda.inputs["Distortion"].default_value = 0.9, 6.0
    onda.inputs["Detail"].default_value = 4.0
    ln.new(mapa.outputs["Vector"], onda.inputs["Vector"])
    mezcla = nd.new("ShaderNodeMix")
    mezcla.data_type, mezcla.blend_type = "FLOAT", "MIX"
    mezcla.inputs["Factor"].default_value = 0.6
    ln.new(onda.outputs["Fac"], mezcla.inputs["A"])
    ln.new(ruido.outputs["Fac"], mezcla.inputs["B"])
    rampa = _rampa(nd, [(0.25, oscuro), (0.55, medio), (0.85, claro)])
    ln.new(mezcla.outputs["Result"], rampa.inputs["Fac"])
    ln.new(rampa.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rugosidad
    relieve = nd.new("ShaderNodeBump")
    relieve.inputs["Strength"].default_value, relieve.inputs["Distance"].default_value = 0.08, 0.0005
    ln.new(mezcla.outputs["Result"], relieve.inputs["Height"])
    ln.new(relieve.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def material_marmol(nombre, fondo, fondo2, veta, rugosidad=0.14):
    """Fondo con nubes suaves y vetas finas: ruido distorsionado → rampa con una banda estrecha."""
    mat = bpy.data.materials.new(nombre)
    nt = mat.node_tree
    nd, ln = nt.nodes, nt.links
    bsdf = nd["Principled BSDF"]
    coord = nd.new("ShaderNodeTexCoord")
    nubes = nd.new("ShaderNodeTexNoise")
    nubes.inputs["Scale"].default_value, nubes.inputs["Detail"].default_value = 18.0, 4.0
    ln.new(coord.outputs["Object"], nubes.inputs["Vector"])
    vetas = nd.new("ShaderNodeTexNoise")
    vetas.inputs["Scale"].default_value, vetas.inputs["Detail"].default_value = 9.0, 12.0
    vetas.inputs["Distortion"].default_value = 3.0
    ln.new(coord.outputs["Object"], vetas.inputs["Vector"])
    base = _rampa(nd, [(0.3, fondo), (0.7, fondo2)])
    ln.new(nubes.outputs["Fac"], base.inputs["Fac"])
    banda = _rampa(nd, [(0.485, (0, 0, 0)), (0.5, (1, 1, 1)), (0.515, (0, 0, 0))])
    ln.new(vetas.outputs["Fac"], banda.inputs["Fac"])
    mezcla = nd.new("ShaderNodeMix")
    mezcla.data_type = "RGBA"
    ln.new(banda.outputs["Color"], mezcla.inputs["Factor"])
    ln.new(base.outputs["Color"], mezcla.inputs["A"])
    mezcla.inputs["B"].default_value = (*veta, 1.0)
    ln.new(mezcla.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rugosidad
    return mat


def material_liso(nombre, color, rugosidad):
    mat = bpy.data.materials.new(nombre)
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rugosidad
    return mat


def materiales():
    return {
        "nogal": material_madera("Nogal canaleta", (0.022, 0.012, 0.008), (0.048, 0.027, 0.017), (0.085, 0.05, 0.031)),
        "fresno": material_madera("Fresno", (0.30, 0.22, 0.14), (0.42, 0.32, 0.21), (0.55, 0.44, 0.30),
                                  veta=(0.3, 12.0, 12.0), rugosidad=0.5),
        # Mármoles que ya usan las mesas de Porada (E7): aproximaciones procedurales, no muestras.
        "nero": material_marmol("Mármol Nero Sahara Noir", (0.012, 0.012, 0.013), (0.03, 0.028, 0.026), (0.75, 0.72, 0.66)),
        "emperador": material_marmol("Mármol Marrone Emperador Dark", (0.045, 0.026, 0.016), (0.09, 0.055, 0.035),
                                     (0.55, 0.45, 0.33)),
        "estudio": material_liso("Estudio", (0.62, 0.61, 0.59), 0.85),
    }


# ----------------------------------------------------------------------------------------------------------------
# Escena
# ----------------------------------------------------------------------------------------------------------------

def mesa(nombre, arbol, mats, params, piedra="nero", posicion=(0, 0, 0)):
    me = bpy.data.meshes.new(nombre)
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = posicion
    mod = ob.modifiers.new("Mesa Porada", "NODES")
    mod.node_group = arbol
    bisel = ob.modifiers.new("Bisel", "BEVEL")
    bisel.width, bisel.segments, bisel.limit_method = 0.0012, 2, "ANGLE"
    bisel.harden_normals = True
    ajustar(ob, mats, params, piedra)
    return ob


def ajustar(ob, mats, params, piedra="nero"):
    mod = ob.modifiers["Mesa Porada"]
    ids = {it.name: it.identifier for it in mod.node_group.interface.items_tree if getattr(it, "in_out", "") == "INPUT"}
    nombres = {"largo": "Largo", "ancho": "Ancho", "alto": "Alto", "espesor": "Espesor", "n_tablas": "N tablas",
               "junta": "Junta", "servicio": "Tabla de servicio", "extremo": "Extremo a caballete",
               "pie_x": "Ancho del pie", "apoyo_central": "Apoyo central", "collar": "Collar de piedra"}
    entradas = mod.properties.inputs                 # API de Blender 5: cada entrada tiene .value

    def poner(nombre, valor):
        getattr(entradas, ids[nombre]).value = valor

    for k, v in params.items():
        poner(nombres[k], v)
    poner("Madera", mats["nogal"])
    poner("Fresno", mats["fresno"])
    poner("Piedra", mats[piedra])
    ob.update_tag()


def estudio(mats):
    """Ciclorama gris claro, luz de ventana grande y relleno suave: neutral, como las láminas ganadoras (E7)."""
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    suelo = bpy.context.object
    suelo.name = "Suelo"
    suelo.data.materials.append(mats["estudio"])
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 6, 15), rotation=(math.pi / 2, 0, 0))
    fondo = bpy.context.object
    fondo.name = "Fondo"
    fondo.data.materials.append(mats["estudio"])
    for nombre, loc, energia, tam in (("Ventana", (-3.0, -2.5, 3.2), 420, 3.0), ("Relleno", (3.5, -1.0, 2.0), 110, 4.0),
                                      ("Contra", (1.0, 3.5, 3.0), 160, 2.0)):
        luz = bpy.data.lights.new(nombre, "AREA")
        luz.energy, luz.size = energia, tam
        ob = bpy.data.objects.new(nombre, luz)
        bpy.context.scene.collection.objects.link(ob)
        ob.location = loc
        mirar(ob, Vector((0, 0, 0.5)))
    mundo = bpy.data.worlds.new("Mundo")
    mundo.node_tree.nodes["Background"].inputs["Color"].default_value = (0.82, 0.82, 0.80, 1)
    mundo.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25
    bpy.context.scene.world = mundo


def mirar(ob, objetivo):
    ob.rotation_euler = (objetivo - ob.location).to_track_quat("-Z", "Y").to_euler()


def camara(loc, objetivo, focal):
    cam = bpy.data.objects.get("Cámara")
    if cam is None:
        cam = bpy.data.objects.new("Cámara", bpy.data.cameras.new("Cámara"))
        bpy.context.scene.collection.objects.link(cam)
        bpy.context.scene.camera = cam
    cam.location = Vector(loc)
    cam.data.lens = focal
    mirar(cam, Vector(objetivo))
    return cam


def configurar_render(muestras):
    addon_utils.enable("cycles", default_set=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = muestras
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
        sc.view_settings.view_transform = "AgX"
    except TypeError:
        pass
    sc.render.film_transparent = False


# Tomas: (versión o parámetros, cámara, objetivo, focal, resolución). Las de E6a y E10a comparten cámara y luz.
XC = 2.4 / 2 - 0.45
TOMAS = {
    "general_B2": ("B2", (3.1, -3.4, 1.75), (0, 0, 0.42), 45, (1600, 1000)),
    "general_AB": ("AB", (3.1, -3.4, 1.75), (0, 0, 0.42), 45, (1600, 1000)),
    "general_B3": ("B3", (3.1, -3.4, 1.75), (0, 0, 0.42), 45, (1600, 1000)),
    "nodo_AB": ("AB", (XC + 0.42, -0.62, 0.42), (XC + 0.07, 0, 0.30), 60, (1200, 1200)),       # E6a (i)
    "nodo_B2": ("B2", (XC + 0.42, -0.62, 0.42), (XC + 0.07, 0, 0.30), 60, (1200, 1200)),       # E6a (ii)
    "junta_0p75": (dict(VERSIONES["B2"], junta=0.00075), (0.25, -0.62, 1.02), (0.0, -0.17, 0.75), 70, (1200, 900)),
    "junta_3p00": (dict(VERSIONES["B2"], junta=0.003), (0.25, -0.62, 1.02), (0.0, -0.17, 0.75), 70, (1200, 900)),
    "junta_4p80": (dict(VERSIONES["B2"], junta=0.0048), (0.25, -0.62, 1.02), (0.0, -0.17, 0.75), 70, (1200, 900)),
    "servicio_B3": ("B3", (0.9, -1.0, 1.25), (0.0, 0.0, 0.74), 55, (1600, 1000)),
    "familia": ("familia", (4.6, -5.6, 2.3), (0.6, 0, 0.35), 42, (1800, 900)),
}


def construir(muestras):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    configurar_render(muestras)
    mats = materiales()
    arbol = arbol_mesa()
    estudio(mats)
    principal = mesa("Mesa", arbol, mats, VERSIONES["B3"])
    familia = {}
    for i, (k, p) in enumerate(FAMILIA.items()):
        familia[k] = mesa(f"Familia · {k}", arbol, mats, p, posicion=(-2.4 + i * 2.6, 4.0, 0))
        familia[k].hide_render = familia[k].hide_viewport = True
    return mats, principal, familia


def renderizar(tomas, mats, principal, familia):
    SALIDA_RENDER.mkdir(parents=True, exist_ok=True)
    sc = bpy.context.scene
    for nombre in tomas:
        version, loc, objetivo, focal, (rx, ry) = TOMAS[nombre]
        es_familia = version == "familia"
        principal.hide_render = es_familia
        for ob in familia.values():
            ob.hide_render = not es_familia
        if es_familia:
            for i, ob in enumerate(familia.values()):
                ob.location = (-2.4 + i * 2.4, 0, 0)
        else:
            ajustar(principal, mats, VERSIONES[version] if isinstance(version, str) else version)
        camara(loc, objetivo, focal)
        sc.render.resolution_x, sc.render.resolution_y = rx, ry
        sc.render.filepath = str(SALIDA_RENDER / f"{nombre}.png")
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"render {nombre}: {time.time() - t0:.0f} s")
    # Deja la escena como se abre: la mesa B3 a la vista, la familia oculta.
    principal.hide_render = False
    ajustar(principal, mats, VERSIONES["B3"])
    for i, ob in enumerate(familia.values()):
        ob.hide_render = True
        ob.location = (-2.4 + i * 2.6, 4.0, 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--muestras", type=int, default=64)
    ap.add_argument("--tomas", nargs="*", default=list(TOMAS), choices=list(TOMAS))
    ap.add_argument("--solo-blend", action="store_true")
    args = ap.parse_args()
    mats, principal, familia = construir(args.muestras)
    if not args.solo_blend:
        renderizar(args.tomas, mats, principal, familia)
    camara(*TOMAS["general_B3"][1:4])
    SALIDA_BLEND.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SALIDA_BLEND / "mesa_porada.blend"), compress=True)
    print("guardado", SALIDA_BLEND / "mesa_porada.blend")


if __name__ == "__main__":
    main()
