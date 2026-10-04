"""Aplica SOLO las decisiones del cliente del 4 de octubre de 2026 sobre un .blend que ya existe.

Sirve para el modelo "formal" con avance propio, después de aplicar_cambios_reunion.py (cambios del 3 de octubre). No
regenera el modelo ni toca nada que no esté en esta lista; no purga datos huérfanos.

Qué hace:
1. Letrero: en P2 las letras, pirámides y horizonte van en gris casi negro (LETRAS_GRIS) sobre el parapeto blanco. Rehace
   el material del letrero con la propiedad nueva "letras_gris" y la escribe en las tres escenas.
2. Muros de P2 (y el bastidor de las celosías, que va igual que el muro): casi negro (PALETA["muro"]).
3. Vidrio elegido: DVH con control solar, tono oscuro y poca reflexión (VIDRIO; MATERIALES_INTELIGENTES.md, sección 4,
   variante 6).
4. Interior: el emisor pasa de RGB naranja a 3500 K (Blackbody) con el mismo brillo.
5. Geometría del letrero: la A (tamaño original, sin reducción) queda activa en las tres escenas. La B se conserva.

Se puede volver a ejecutar: rehace solo lo suyo.

Uso (igual que aplicar_cambios_reunion.py):
  A) En Blender, con el .blend abierto: Scripting > Open > este archivo > Run Script, y después guardar.
     uyuni_modelo.py (versión del 4 de octubre) tiene que estar en ../uyuni_modelo.py o en MODELO.
  B) Vía MCP: exec(open(p, encoding="utf-8").read(), {"__file__": p, "__name__": "__main__"})
  C) Sin interfaz: python aplicar_cambios_4oct.py -- formal.blend formal_4oct.blend   (módulo bpy 5.2)
"""
import os
import sys

import bpy

MODELO = ""   # ruta a uyuni_modelo.py (versión del 4 de octubre); si queda vacía se busca junto a este archivo

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

G = {"__file__": os.path.abspath(MODELO), "__name__": "uyuni_modelo_cambios"}
exec(compile(open(MODELO, encoding="utf-8").read(), MODELO, "exec"), G)
if "LETRAS_GRIS" not in G or "VIDRIO" not in G:
    raise RuntimeError("uyuni_modelo.py no es la versión del 4 de octubre (le faltan LETRAS_GRIS y VIDRIO)")
P = G["PREFIJO"]
informe = []


def material_nuevo(nombre, fabrica):
    """Crea el material con la función del modelo y lo pone en lugar del anterior en todos sus usos."""
    viejo = bpy.data.materials.get(P + nombre)
    if viejo:
        viejo.name = P + nombre + "_ANTERIOR"
    nuevo = fabrica()
    if viejo:
        viejo.user_remap(nuevo)
        bpy.data.materials.remove(viejo)
        informe.append(f"material {nombre} rehecho")
    else:
        informe.append(f"material {nombre} creado (no existía: asígnalo a mano si hace falta)")
    return nuevo


material_nuevo("LETRERO_BLANCO_O_CORTEN", G["mat_letrero"])
material_nuevo("REVOQUE_CONTINUO", lambda: G["mat_revoque"]("REVOQUE_CONTINUO"))
material_nuevo("REVOQUE_FACHADA_BUNAS", lambda: G["mat_revoque"]("REVOQUE_FACHADA_BUNAS", bunas=G["VIGA_1"]))
material_nuevo("BASTIDOR_CELOSIAS", lambda: G["mat_propuesta"]("BASTIDOR_CELOSIAS", "bastidor"))
material_nuevo("VIDRIO_CONTROL_SOLAR", G["mat_vidrio"])
material_nuevo("INTERIOR_LUZ_CALIDA", lambda: G["mat_emisor"]("INTERIOR_LUZ_CALIDA", "#FFB46B", "luz_interior", kelvin=3500))

for sc in bpy.data.scenes:
    G["propiedades_escena"](sc)
    if "letras_gris" not in sc:          # escenas propias de la otra IA: letras como las de su propuesta
        sc["letras_gris"] = 1 if sc.get("propuesta", 0) == 1 and not sc.get("letras_corten", 0) else 0
    G["geometria_letrero"](sc, "A")
    informe.append(f"escena {sc.name}: propuesta {sc.get('propuesta')}, letras_corten {sc.get('letras_corten')}, "
                   f"letras_gris {sc.get('letras_gris')}, letrero A")

print("[CAMBIOS 4 OCT] " + "\n[CAMBIOS 4 OCT] ".join(informe))
if salida:
    bpy.ops.wm.save_as_mainfile(filepath=salida, compress=True)
    print("[CAMBIOS 4 OCT] guardado", salida)
else:
    print("[CAMBIOS 4 OCT] listo: revisa la escena y guarda el archivo")
