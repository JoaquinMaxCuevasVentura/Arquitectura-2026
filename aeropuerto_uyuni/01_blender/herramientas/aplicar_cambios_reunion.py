"""Aplica SOLO los cambios de la reunión del 3 de octubre de 2026 sobre un .blend que ya existe.

Sirve para el modelo "formal": un .blend generado con la versión anterior de uyuni_modelo.py (commit 7b19bea, el
del primer traspaso) en el que otra IA o una persona ya avanzó (contexto, assets, ajustes). No regenera el modelo:
- no toca objetos, colecciones ni materiales que no sean los de la lista de abajo;
- no purga datos huérfanos (los assets cargados y todavía sin usar quedan intactos).

Qué hace:
1. Materiales: crea los nuevos y reemplaza los viejos en todos los objetos que los usan.
   - Duralit → revoque continuo (con buñas en los paños del Lado Tierra).
   - Columnas y vigas de hormigón visto → revoque.
   - Chapa café chocolate → cubierta y parapeto según la propuesta.
   - Corten → celosía corten o blanca.
   - Perfilería negra → antracita mate.
   - Bastidor, letrero y plenum → sus versiones nuevas.
2. Geometría: quita los bolardos y reemplaza el cielo Luxalon por el listonado, el retenedor de nieve por el de 1",
   el letrero completo por el nuevo (geometrías A y B, pirámides 3D, juego sobre la salida) y la nieve del
   crepúsculo.
3. Cámaras CAM_07_PROPUESTAS y CAM_07B_CAPTURA_CLIENTE.
4. Escenas: propiedades "propuesta" y "letras_corten", escena UYUNI_DIA_P2_SALAR_LITIO (con todas las colecciones
   de UYUNI_DIA, también las que no son del script) y cielo más limpio si el mundo es el cielo procedural del script
   (un HDRI no se toca).

Se puede volver a ejecutar: borra y rehace solo lo suyo.

Uso:
  A) En Blender, con el .blend formal abierto: Scripting > Open > este archivo > Run Script, y después guardar.
     uyuni_modelo.py (versión nueva) tiene que estar en la carpeta de arriba (../uyuni_modelo.py) o en MODELO.
  B) Vía MCP: exec(open(p, encoding="utf-8").read(), {"__file__": p, "__name__": "__main__"})
  C) Sin interfaz: python aplicar_cambios_reunion.py -- formal.blend formal_actualizado.blend   (módulo bpy 5.2)
                   blender -b formal.blend -P aplicar_cambios_reunion.py -- - formal_actualizado.blend
"""
import os
import sys

import bpy

MODELO = ""   # ruta a uyuni_modelo.py (versión nueva); si queda vacía se busca junto a este archivo y al .blend

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
aqui = os.path.dirname(os.path.abspath(__file__))
candidatos = [MODELO, os.path.join(aqui, "..", "uyuni_modelo.py"), os.path.join(aqui, "uyuni_modelo.py"),
              os.path.join(os.path.dirname(bpy.data.filepath), "uyuni_modelo.py")]
MODELO = next((os.path.abspath(c) for c in candidatos if c and os.path.isfile(c)), None)
if MODELO is None:
    raise FileNotFoundError("No encuentro uyuni_modelo.py: escribe su ruta en MODELO, al principio de este script")
if args and args[0] != "-":
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(args[0]))
salida = os.path.abspath(args[1]) if len(args) > 1 else None

# --- 1. cargar parámetros y funciones del modelo nuevo sin construir nada ---
G = {"__file__": os.path.abspath(MODELO), "__name__": "uyuni_modelo_cambios"}
exec(compile(open(MODELO, encoding="utf-8").read(), MODELO, "exec"), G)
P = G["PREFIJO"]
informe = []


def escena(nombre):
    return bpy.data.scenes.get(nombre)


sc_dia = escena("UYUNI_DIA") or bpy.context.scene
C = {}
for n in G["COLECCIONES"]:
    c = bpy.data.collections.get(n)
    if c is None:
        c = bpy.data.collections.new(n)
        sc_dia.collection.children.link(c)
        informe.append(f"colección {n} creada (no existía)")
    C[n] = c


def borrar_objeto(nombre):
    ob = bpy.data.objects.get(nombre)
    if ob is None:
        return False
    datos = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    if datos is not None and datos.users == 0:
        for coleccion_datos in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
            if datos.name in coleccion_datos and coleccion_datos[datos.name] == datos:
                coleccion_datos.remove(datos)
                break
    return True


# --- 2. materiales nuevos (si ya existen de una pasada anterior, se rehacen y se reasignan) ---
def material_nuevo(nombre, fabrica):
    viejo = bpy.data.materials.get(P + nombre)
    if viejo:
        viejo.name = P + nombre + "_ANTERIOR"
    nuevo = fabrica()
    if viejo:
        viejo.user_remap(nuevo)
        bpy.data.materials.remove(viejo)
    return nuevo


def material_existente(nombre, fabrica):
    return bpy.data.materials.get(P + nombre) or fabrica()


M = dict(
    cubierta=material_nuevo("CHAPA_CUBIERTA", lambda: G["mat_propuesta"]("CHAPA_CUBIERTA", "cubierta")),
    antepecho=material_nuevo("CHAPA_ANTEPECHO_REMATES", lambda: G["mat_propuesta"]("CHAPA_ANTEPECHO_REMATES", "antepecho")),
    celosia=material_nuevo("CELOSIA_CORTEN_O_BLANCA", G["mat_celosia"]),
    perfil=material_nuevo("ALUMINIO_ANTRACITA_MATE",
                          lambda: G["mat_simple"]("ALUMINIO_ANTRACITA_MATE", G["PERFIL_COLOR"], metal=0.25, rug=0.55)),
    muro=material_nuevo("REVOQUE_CONTINUO", lambda: G["mat_revoque"]("REVOQUE_CONTINUO")),
    muro_buna=material_nuevo("REVOQUE_FACHADA_BUNAS", lambda: G["mat_revoque"]("REVOQUE_FACHADA_BUNAS", bunas=G["VIGA_1"])),
    cielo=material_nuevo("CIELO_LISTONES", G["mat_cielo"]),
    plenum=material_nuevo("PLENUM_NEGRO_MATE", lambda: G["mat_simple"]("PLENUM_NEGRO_MATE", "#030303", rug=1.0)),
    bastidor=material_nuevo("BASTIDOR_CELOSIAS", lambda: G["mat_propuesta"]("BASTIDOR_CELOSIAS", "bastidor")),
    letrero=material_nuevo("LETRERO_BLANCO_O_CORTEN", G["mat_letrero"]),
    galvanizado=material_existente("ACERO_GALVANIZADO",
                                   lambda: G["mat_simple"]("ACERO_GALVANIZADO", "#9DA1A5", metal=0.9, rug=0.35)),
    luminaria=material_existente("LUMINARIA_ALERO",
                                 lambda: G["mat_emisor"]("LUMINARIA_ALERO", "#FFC27A", "luz_alero", 40.0)),
    nieve=material_existente("NIEVE", lambda: G["mat_simple"]("NIEVE", "#F4F6FA", rug=0.45, Subsurface_Weight=0.2)),
)


def reasignar(viejo_nombre, reglas, resto):
    """Cambia el material viejo por el nuevo: por prefijo de nombre de objeto (reglas) y, al final, en todo lo demás."""
    viejo = bpy.data.materials.get(P + viejo_nombre)
    if viejo is None:
        return
    for ob in bpy.data.objects:
        for slot in ob.material_slots:
            if slot.material == viejo:
                for prefijo, nuevo in reglas:
                    if ob.name.startswith(P + prefijo):
                        slot.material = nuevo
                        break
    if resto is not None:
        viejo.user_remap(resto)
    if viejo.users == 0:
        bpy.data.materials.remove(viejo)
        informe.append(f"material {viejo_nombre} reemplazado")
    else:
        informe.append(f"material {viejo_nombre} conservado en {viejo.users} usos (hormigón de zanja, bordillo, etc.)")


reasignar("CHAPA_CAFE_CHOCOLATE_ACERGAL", [("CUBIERTA_", M["cubierta"]), ("ANTEPECHO_", M["antepecho"]),
                                           ("GOTERON_", M["antepecho"]), ("FRANJA_ESTE_", M["antepecho"])], M["cubierta"])
reasignar("DURALIT_FIBROCEMENTO", [("MURO_NE_", M["muro_buna"])], M["muro"])
reasignar("HORMIGON_VISTO", [("COLUMNAS_EJE_A", M["muro"]), ("VIGAS_DINTEL", M["muro_buna"])], None)
reasignar("CORTEN_OXIDADO", [], M["celosia"])
reasignar("ALUMINIO_ANODIZADO_NEGRO_MATE", [], M["perfil"])
reasignar("BASTIDOR_ACERO_NEGRO", [], M["bastidor"])
reasignar("LETRERO_BLANCO", [], M["letrero"])
reasignar("PLENUM_NEGRO", [], M["plenum"])
reasignar("LUXALON_ALUMINIO_CHAMPAGNE", [], M["cielo"])

# --- 3. geometría: quitar lo viejo (y lo de una pasada anterior de este parche) y rehacer ---
quitar = ["BOLARDOS", "CIELO_PLENUM", "CIELO_LUXALON_LAMAS", "LUMINARIAS_ALERO", "RETENEDOR_ABRAZADERAS",
          "RETENEDOR_BARRAS_TUBULARES", "NIEVE_BORDE_CUBIERTA", "CIELO_PLENUM_NEGRO", "CIELO_LISTONES",
          "RETENEDOR_TUBOS_1PULG"]
for n in quitar:
    if borrar_objeto(P + n):
        informe.append(f"quitado {P + n}")
camaras_previas = {sc.name: sc.camera.name for sc in bpy.data.scenes                  # escenas que ya las usaban
                   if sc.camera and sc.camera.name in ("CAM_07_PROPUESTAS", "CAM_07B_CAPTURA_CLIENTE")}
for n in ("CAM_07_PROPUESTAS", "CAM_07B_CAPTURA_CLIENTE"):
    borrar_objeto(n)
mat_bolardo = bpy.data.materials.get(P + "BOLARDO_ACERO_GRAFITO")
if mat_bolardo and mat_bolardo.users == 0:
    bpy.data.materials.remove(mat_bolardo)

letrero = bpy.data.collections.get("LETRERO_HORIZONTE_UYUNI")
if letrero:
    n_obj = len(letrero.all_objects)
    for ob in list(letrero.all_objects):
        borrar_objeto(ob.name)
    for hija in list(letrero.children_recursive):
        bpy.data.collections.remove(hija)
    informe.append(f"letrero anterior quitado ({n_obj} objetos)")

G["cielo_alero"](C, M)
G["retenedor_nieve"](C, M)
G["letrero"](C, M)
cams = G["camaras_propuestas"](C["08_CAMERAS_LIGHTS"])
for nombre_escena, nombre_camara in camaras_previas.items():
    bpy.data.scenes[nombre_escena].camera = cams[nombre_camara]
col_nieve = bpy.data.collections.get("09_NIEVE_CREPUSCULO")
if col_nieve:
    G["nieve_crepusculo"](col_nieve, M)
informe.append("creados: cielo listonado, retenedor de 1\", letrero A/B, CAM_07_PROPUESTAS y CAM_07B_CAPTURA_CLIENTE")

# --- 4. escenas y cielo ---
if escena("UYUNI_DIA") and not escena("UYUNI_DIA_P2_SALAR_LITIO"):
    luz_dia = bpy.data.collections.get("08_LUZ_DIA") or bpy.data.collections.new("08_LUZ_DIA")
    sc3 = G["escena_propuesta_2"](sc_dia, C, luz_dia, cams["CAM_07_PROPUESTAS"], 256)
    for hija in sc_dia.collection.children:            # también las colecciones que agregó otra IA (contexto, assets)
        if hija.name not in sc3.collection.children:
            sc3.collection.children.link(hija)
    informe.append("escena UYUNI_DIA_P2_SALAR_LITIO creada")
elif escena("UYUNI_DIA_P2_SALAR_LITIO") and escena("UYUNI_DIA_P2_SALAR_LITIO").camera is None:
    escena("UYUNI_DIA_P2_SALAR_LITIO").camera = cams["CAM_07_PROPUESTAS"]
for sc in bpy.data.scenes:
    G["propiedades_escena"](sc)
    G["geometria_letrero"](sc, "A")
for w in bpy.data.worlds:
    if w.name.startswith(P) and w.node_tree:
        for nodo in w.node_tree.nodes:
            if nodo.type == "TEX_SKY":
                for k, v in G["CIELO_ATMOSFERA"].items():
                    if hasattr(nodo, k):
                        setattr(nodo, k, v)
                informe.append(f"cielo de {w.name} actualizado")

print("[CAMBIOS 3 OCT] " + "\n[CAMBIOS 3 OCT] ".join(informe))
if salida:
    bpy.ops.wm.save_as_mainfile(filepath=salida, compress=True)
    print("[CAMBIOS 3 OCT] guardado", salida)
else:
    print("[CAMBIOS 3 OCT] listo: revisa la escena y guarda el archivo")
