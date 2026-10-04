"""Vidrio de control solar en CAM_01: variantes con la misma luz (×0,6) y el mismo encuadre (verticales rectas).

  V1_HOY              metálico 0,15 y transmisión 0,8 (atajo: el reflejo toma el tinte azul de la base)
  V2_CAPA_FINA        metálico 0, transmisión 1, Thin Film de 57 nm con IOR 2,4 (capa de óxido tipo TiO2:
                      cuarto de onda a 550 nm, reflectancia ≈ 34 %, reflejo plateado neutro)
  V3_FISICO_COMPLETO  V2 con capa de 50 nm (pico a 480 nm: reflejo azul acero), tinte de transmisión más oscuro,
                      ondas de templado por paño (roller wave) y polvo fino en el perímetro de cada paño (AO -> rugosidad)
  V4_BACKFACING       la receta "unidireccional": Mix Shader con Geometry > Backfacing; por fuera, metálico 0,9 sobre
                      #0D151D sin transmisión; por dentro, vidrio transparente
  V5_FISICO_OSCURO    V3 con un tinte de transmisión oscuro (#6E808E): el aspecto de "vidrio espejo" gris azulado de
                      las fachadas corporativas, sin perder la transparencia física (la hora azul sigue funcionando)
  V6_OSCURO_BAJA_REFLEXION  la elección del cliente (4 de octubre): el tinte oscuro del V5 con una capa de baja
                      reflexión (IOR 1,8 y 67 nm: ≈ 13 % por cara en lugar de ≈ 34 %), para ver la estructura detrás
                      del vidrio. El interior de día pasa a 3500 K (Blackbody), sin el resplandor naranja

Uso: python prueba_vidrio.py -- archivo.blend carpeta [camara] [ancho] [muestras] [variantes]
     variantes: lista separada por comas (por defecto, las cinco);
     las que ya tienen su JPG en la carpeta no se repiten.
"""
import math
import os
import sys
import time

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
blend, salida = args[0], args[1]
camara = args[2] if len(args) > 2 else "CAM_01_HERO_LADO_TIERRA"
ancho = int(args[3]) if len(args) > 3 else 1280
muestras = int(args[4]) if len(args) > 4 else 64
variantes = args[5].split(",") if len(args) > 5 else ["V1_HOY", "V2_CAPA_FINA", "V3_FISICO_COMPLETO", "V4_BACKFACING",
                                                     "V5_FISICO_OSCURO", "V6_OSCURO_BAJA_REFLEXION"]
os.makedirs(salida, exist_ok=True)


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)


def preparar():
    """Abre el modelo con la luz corregida (×0,6) y la cámara con verticales rectas."""
    bpy.ops.wm.open_mainfile(filepath=blend)
    sc = bpy.data.scenes["UYUNI_DIA"]
    for ob in sc.objects:
        if ob.type == "LIGHT" and ob.data.type == "SUN":
            ob.data.energy *= 0.6
    for n in sc.world.node_tree.nodes:
        if n.type == "BACKGROUND":
            n.inputs["Strength"].default_value *= 0.6
    cam = bpy.data.objects[camara]
    d = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    pitch = math.asin(max(-1, min(1, d.z)))
    cam.rotation_euler = Vector((d.x, d.y, 0)).normalized().to_track_quat("-Z", "Y").to_euler()
    cam.data.shift_y += math.tan(pitch) * cam.data.lens / cam.data.sensor_width
    sc.camera = cam
    r, cy = sc.render, sc.cycles
    r.resolution_x, r.resolution_y, r.resolution_percentage = ancho, round(ancho * 9 / 16), 100
    r.image_settings.file_format, r.image_settings.quality = "JPEG", 94
    cy.device, cy.samples, cy.use_adaptive_sampling, cy.adaptive_threshold = "CPU", muestras, True, 0.01
    cy.use_denoising = True
    mat = bpy.data.materials["UY_VIDRIO_CONTROL_SOLAR"]
    return sc, mat, mat.node_tree, next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def capa_fina(b, espesor_nm, tinte=None, ior_capa=2.4):
    """Capa de control solar por interferencia. Reflectancia a cuarto de onda sobre vidrio (n = 1,52):
    ((1,52 − n²) / (1,52 + n²))²: n = 2,4 -> ≈ 34 %; n = 1,8 -> ≈ 13 %. El pico cae en λ = 4 · n · espesor."""
    b.inputs["Metallic"].default_value = 0.0
    b.inputs["Transmission Weight"].default_value = 1.0
    b.inputs["Thin Film Thickness"].default_value = espesor_nm
    b.inputs["Thin Film IOR"].default_value = ior_capa
    if tinte:
        b.inputs["Base Color"].default_value = srgb(tinte)


def ondas_de_templado(nt, b, fuerza=0.03):
    """Roller wave: ondas paralelas de ~0,33 m que deja el horno de templado. Cada paño (una isla de la malla) tiene
    su propia fase. Solo mueve la normal: los reflejos se ondulan sin tocar la geometría."""
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    onda = nt.nodes.new("ShaderNodeTexWave")
    onda.wave_type, onda.bands_direction = "BANDS", "Z"
    onda.inputs["Scale"].default_value = 0.95          # período 2π / 20 / 0,95 ≈ 0,33 m
    onda.inputs["Distortion"].default_value = 0.6
    onda.inputs["Detail"].default_value = 0.0
    nt.links.new(geo.outputs["Position"], onda.inputs["Vector"])
    fase = nt.nodes.new("ShaderNodeMath")
    fase.operation = "MULTIPLY"
    nt.links.new(geo.outputs["Random Per Island"], fase.inputs[0])
    fase.inputs[1].default_value = 6.2832
    nt.links.new(fase.outputs[0], onda.inputs["Phase Offset"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value, bump.inputs["Distance"].default_value = fuerza, 0.003
    nt.links.new(onda.outputs["Fac"], bump.inputs["Height"])
    return bump.outputs["Normal"]


def polvo_perimetral(nt, b, rug_centro=0.02, rug_borde=0.18):
    """Polvo fino junto a la perfilería: AO corto (con los demás objetos) -> rugosidad. No entra en ningún Bump."""
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.samples, ao.only_local = 2, False
    ao.inputs["Distance"].default_value = 0.12
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(ao.outputs["AO"], inv.inputs[1])
    rango = nt.nodes.new("ShaderNodeMapRange")
    rango.interpolation_type, rango.clamp = "SMOOTHSTEP", True
    nt.links.new(inv.outputs[0], rango.inputs["Value"])
    rango.inputs["From Min"].default_value, rango.inputs["From Max"].default_value = 0.10, 0.50
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    ruido = nt.nodes.new("ShaderNodeTexNoise")
    ruido.inputs["Scale"].default_value, ruido.inputs["Detail"].default_value = 14.0, 4.0
    nt.links.new(geo.outputs["Position"], ruido.inputs["Vector"])
    rompe = nt.nodes.new("ShaderNodeMath")
    rompe.operation = "MULTIPLY"
    nt.links.new(rango.outputs["Result"], rompe.inputs[0])
    nt.links.new(ruido.outputs["Factor"], rompe.inputs[1])
    mezcla = nt.nodes.new("ShaderNodeMapRange")
    mezcla.clamp = True
    nt.links.new(rompe.outputs[0], mezcla.inputs["Value"])
    mezcla.inputs["From Min"].default_value, mezcla.inputs["From Max"].default_value = 0.0, 0.6
    mezcla.inputs["To Min"].default_value, mezcla.inputs["To Max"].default_value = rug_centro, rug_borde
    nt.links.new(mezcla.outputs["Result"], b.inputs["Roughness"])


def receta_backfacing(nt, b):
    """La receta del texto, tal cual: Mix Shader por Backfacing; exterior metálico casi negro, interior transparente."""
    salida_mat = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    ext = b
    ext.inputs["Base Color"].default_value = srgb("#0D151D")
    ext.inputs["Metallic"].default_value = 0.9
    ext.inputs["Roughness"].default_value = 0.03
    ext.inputs["Transmission Weight"].default_value = 0.0
    ext.inputs["IOR"].default_value = 1.52
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    ruido = nt.nodes.new("ShaderNodeTexNoise")
    ruido.inputs["Scale"].default_value, ruido.inputs["Detail"].default_value = 2.0, 1.0
    ruido.inputs["Roughness"].default_value = 0.2
    nt.links.new(geo.outputs["Position"], ruido.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value, bump.inputs["Distance"].default_value = 0.03, 0.005
    nt.links.new(ruido.outputs["Factor"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], ext.inputs["Normal"])
    inte = nt.nodes.new("ShaderNodeBsdfPrincipled")
    inte.inputs["Base Color"].default_value = (1, 1, 1, 1)
    inte.inputs["Transmission Weight"].default_value = 1.0
    inte.inputs["Roughness"].default_value = 0.0
    inte.inputs["IOR"].default_value = 1.52
    inte.inputs["Thin Wall"].default_value = True
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(geo.outputs["Backfacing"], mix.inputs["Fac"])
    nt.links.new(ext.outputs["BSDF"], mix.inputs[1])
    nt.links.new(inte.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], salida_mat.inputs["Surface"])


for v in variantes:
    archivo = f"{salida}/{camara}_{v}.jpg"
    if os.path.exists(archivo):
        print(f"[VIDRIO] {v} ya está", flush=True)
        continue
    sc, mat, nt, b = preparar()
    if v == "V2_CAPA_FINA":
        capa_fina(b, 57.0)
    elif v in ("V3_FISICO_COMPLETO", "V5_FISICO_OSCURO"):
        capa_fina(b, 50.0, tinte="#A9BCCB" if v == "V3_FISICO_COMPLETO" else "#6E808E")
        nt.links.new(ondas_de_templado(nt, b), b.inputs["Normal"])
        polvo_perimetral(nt, b)
    elif v == "V4_BACKFACING":
        receta_backfacing(nt, b)
    elif v == "V6_OSCURO_BAJA_REFLEXION":
        capa_fina(b, 67.0, tinte="#6E808E", ior_capa=1.8)          # pico a 482 nm: reflejo azul acero tenue
        nt.links.new(ondas_de_templado(nt, b), b.inputs["Normal"])
        polvo_perimetral(nt, b)
        interior = bpy.data.materials["UY_INTERIOR_LUZ_CALIDA"].node_tree
        bb = interior.nodes.new("ShaderNodeBlackbody")
        bb.inputs["Temperature"].default_value = 3500.0
        nt_b = next(n for n in interior.nodes if n.type == "BSDF_PRINCIPLED")
        interior.links.new(bb.outputs["Color"], nt_b.inputs["Emission Color"])
    sc.render.filepath = archivo
    t = time.time()
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print(f"[VIDRIO] {v} -> {time.time() - t:.0f} s", flush=True)
