"""Continúa el modelo aprobado sin editar sus volúmenes ni sus dos paletas.

El frente del Lado Tierra (calzada, jardineras y plaza) ya sale de la fuente (uyuni_modelo.frente_lado_tierra, restituido
de las capturas del cliente): este paso no lo toca.
"""
import json
from pathlib import Path

import bpy
from . import materiales, camaras, contexto, storyboard
from herramientas import render_plan

# True: el contexto (vegetación, vehículos y personas genéricos) se agrega con IA sobre los renders; en el render solo
# quedan la arquitectura, el sitio y los assets locales de alta calidad (variable UYUNI_ASSETS_LOCALES=1). Los objetos
# ocultos siguen en el archivo y se recuperan con hide_render = False (ver CONTINUACION_CODEX.md).
CONTEXTO_IA = True


def configurar(sc, animado=False):
    night = "CREPUSCULO" in sc.name
    render_plan.apply_profile(sc, "drone" if animado else ("final_night" if night else "final_day"),
                              device="GPU", transparent_bounces=16,
                              animated=animado, motion_blur=animado)
    sc.render.resolution_x, sc.render.resolution_y = 3840, 2160
    sc.render.resolution_percentage = 100
    sc.render.fps = 24
    render_plan.set_image(sc)
    sc.compositing_node_group = render_plan.make_optics(sc, night=night, width=3840, animated=animado)


def aplicar(fuente):
    letrero_A=fuente["geometria_letrero"]
    original = list(bpy.data.scenes)
    report = {"base": "acf7f58", "propuestas": ["Patrimonio Ferroviario", "Salar & Litio"]}
    report["fachada_trasera"]={"paños_opacos_y_ME4":"Enrasados con pilastras",
                               "avance_m":.7,"cara_exterior_m":fuente["Y_MURO_RAS_AIRE"],
                               "nichos":"Solo crujías con grandes ME5/ME6",
                               "entrada_pequeña":"Puerta frontal alineada de 1,00 x 2,10 m"}
    report["exteriores"] = "Frente según las capturas del cliente: uyuni_modelo.frente_lado_tierra"
    report["materiales"] = materiales.aplicar()
    report["camaras_luz"] = camaras.aplicar({"camera_night_height": 1.5})
    report["suelo"] = contexto.suelo_pbr()
    report["matas_secas"] = contexto.vegetacion(original)
    report["assets"] = contexto.vehiculos_personas(original)
    report["contexto_ia"] = contexto.limpiar_para_ia() if CONTEXTO_IA else "desactivado"
    cloudy = contexto.cielo_nublado()
    for sc in original + [cloudy]:
        configurar(sc)
        letrero_A(sc, "A")
    data = json.loads((Path(__file__).resolve().parents[1] / "guion/storyboard.json").read_text(encoding="utf-8"))
    report["storyboard"] = storyboard.aplicar(data, configurar, letrero_A)
    # El archivo abre preparado para animar sin el coste de AO/Bevel en shaders.
    # render_plan activa ESTUDIO al producir imágenes finales.
    materiales.aplicar({"profile":"DRON"})
    report["perfil_shaders_guardado"]="DRON; ESTUDIO disponible para renders fijos"
    report["decisiones_pendientes"] = [
        "Vidrio alternativo #A9BCCB: conservar #6E808E hasta aprobación comparativa",
        "Letrero nocturno: comparar halo/bañadores antes de cambiar el esquema",
        "Cubierta P2: se conserva el acabado actual",
        "IFC interior: requiere registro y selección validados antes de integrar",
    ]
    oculto = " (oculto en el render: contexto con IA)" if CONTEXTO_IA else ""
    if not report["assets"]["vehiculos_locales"]:
        report["decisiones_pendientes"].append("SUV público provisional" + oculto + "; el Land Cruiser se incorpora con UYUNI_ASSETS_LOCALES=1")
    if not report["assets"]["transfer_local"]:
        report["decisiones_pendientes"].append("Transfer genérico provisional" + oculto + "; pendiente un modelo de pasajeros con acceso autorizado")
    text = bpy.data.texts.get("CONTINUACION_CODEX.json") or bpy.data.texts.new("CONTINUACION_CODEX.json")
    text.clear(); text.write(json.dumps(report, ensure_ascii=False, indent=2))
    print("[CODEX]", json.dumps({"matas": report["matas_secas"], "assets": report["assets"],
                                "storyboard": report["storyboard"]}, ensure_ascii=False))
    return report
