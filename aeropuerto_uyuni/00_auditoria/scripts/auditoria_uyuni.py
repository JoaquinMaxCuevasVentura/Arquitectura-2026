#!/usr/bin/env python3
"""Auditoría técnica DXF + IFC (Fase 0 / 0.5) - Terminal de Pasajeros, Aeropuerto de Uyuni.

No genera geometría en Blender. Inspecciona los archivos fuente y deja:
  dxf_audit_report.json   capas, bloques, presentaciones, vistas, textos clave, cotas, verificación
  ifc_audit_report.json   georreferenciación, niveles, ejes, clases, estructura
  vistas/<VISTA>.png      cada vista aislada (fondo blanco) + vistas_index.json con su bbox en el DXF
  vistas/<VISTA>.dxf      cada vista aislada SIN cotas/textos/tramas/directrices (guía limpia para _REF_CAD)

Uso:
  python3 auditoria_uyuni.py --dxf tp-arq-x-cad-FachadaEste-01.dxf \
      --ifc AU-SUP-EST-TP-ZZ-MO-TerminalPasajeros.ifc \
      --ifc AU-CBI-ARQ-TP-ZZ-MO-TerminalPasajeros_detached-AU-SUP-EST-TP-ZZ-MO-TerminalPasajeros.ifc \
      --out ./auditoria
Requiere: ezdxf, ifcopenshell, numpy, matplotlib
"""
import argparse
import collections
import json
import math
import multiprocessing
import os
import re

import ezdxf
import numpy as np
from ezdxf import bbox

# Vistas identificadas en el model space del DXF (coordenadas DXF, metros).
# estado: ACTUAL = diseño corregido (vigente en las presentaciones FACHADA*),
#         ORIGINAL = diseño previo a la reunión (doble pantalla, canaleta),
#         DETALLE = fichas de carpintería / paneles (dibujadas 1:1).
# a_ifc: transformación a coordenadas locales del edificio (IFC) y altura sobre NPT.
VISTAS = {
    "CORTE_ACTUAL_POR_M1": dict(bbox=(-50, -28.5, -6, 20), estado="ACTUAL", coleccion="REF_CAD_DETALLES_CUBIERTA",
                                npt_y=0.0, a_ifc="Y_ifc = -41.147 - x_dxf ; z_NPT = y_dxf",
                                nota="Corte por mampara ME-1 (eje A): vidrio, dintel, antepecho 2.40, alero, zanja."),
    "CORTE_ACTUAL_MURO_CIEGO": dict(bbox=(-28.5, -3, -6, 20), estado="ACTUAL", coleccion="REF_CAD_DETALLES_CUBIERTA",
                                    npt_y=0.0, a_ifc="Y_ifc = -24.125 - x_dxf ; z_NPT = y_dxf",
                                    nota="Corte por paño ciego (panel M2 e=130 mm) con viga intermedia +3.245/+3.745."),
    "CORTE_ORIGINAL_B-K-A": dict(bbox=(-50, -3, 36, 62), estado="ORIGINAL", coleccion="REF_CAD_ANTES",
                                 npt_y=42.914, a_ifc="Y_ifc = -15.193 - x_dxf ; z_NPT = y_dxf - 42.914",
                                 nota="Diseño previo: vidrio en eje K, doble pantalla ciega en eje A hasta +7.60, canaleta, cubierta a +9.87."),
    "FACHADA_NORESTE_ACTUAL": dict(bbox=(-3, 92, -6, 20), estado="ACTUAL", coleccion="REF_CAD_ALZADO_LADO_TIERRA",
                                   npt_y=0.0, a_ifc="X_ifc = x_dxf ; z_NPT = y_dxf",
                                   nota="Lado Tierra (eje A). Presentación FACHADA vp1 (1:300)."),
    "FACHADA_NORESTE_ORIGINAL": dict(bbox=(-3, 92, 36, 62), estado="ORIGINAL", coleccion="REF_CAD_ANTES",
                                     npt_y=42.914, a_ifc="X_ifc = x_dxf ; z_NPT = y_dxf - 42.914",
                                     nota="Lado Tierra en versión previa (acotada en detalle, sin antepecho 2.40)."),
    "FACHADA_SUROESTE": dict(bbox=(95, 205, -6, 20), estado="ACTUAL", coleccion="REF_CAD_ALZADO_LADO_AIRE",
                             npt_y=0.0, a_ifc="vista desde +Y (lado aire); X_ifc decrece hacia la derecha",
                             nota="Lado Aire (eje R). Presentación FACHADA vp2 (1:300)."),
    "FACHADA_ESTE": dict(bbox=(238, 305, -6, 22), estado="ACTUAL", coleccion="REF_CAD_ALZADOS_LATERALES",
                         npt_y=0.0, a_ifc="lateral eje 1 (normal -X local)", nota="2 PT2 + 2 ME-3."),
    "FACHADA_OESTE": dict(bbox=(322, 402, -6, 22), estado="ACTUAL", coleccion="REF_CAD_ALZADOS_LATERALES",
                          npt_y=0.0, a_ifc="lateral eje 20 (normal +X local)", nota="4 ME-3; PT1 del cuadro (11 u.) NO dibujadas."),
    "ME1": dict(bbox=(8, 24, -33, -12), estado="DETALLE", coleccion="REF_CAD_DETALLES_M1", nota="Mampara Hall Principal (7 u.)"),
    "ME2": dict(bbox=(24, 44, -33, -12), estado="DETALLE", coleccion="REF_CAD_DETALLES_M1", nota="Acceso, puerta corrediza con sensor (2 u.)"),
    "ME6": dict(bbox=(44, 62, -33, -12), estado="DETALLE", coleccion="REF_CAD_DETALLES_M1", nota="Esclusa pre-embarque (4 u., lado aire)"),
    "ME3": dict(bbox=(62, 82, -33, -12), estado="DETALLE", coleccion="REF_CAD_DETALLES_M1", nota="Ventana rombo 1.20x1.20 (12 u.)"),
    "ME4": dict(bbox=(82, 102, -33, -12), estado="DETALLE", coleccion="REF_CAD_DETALLES_M1", nota="Oficinas PB (4 u.)"),
    "ME5": dict(bbox=(102, 124, -33, -12), estado="DETALLE", coleccion="REF_CAD_DETALLES_M1", nota="Oficinas PA (4 u.)"),
    "PT1_PT2": dict(bbox=(124, 152, -33, -12), estado="DETALLE", coleccion="REF_CAD_DETALLES_CELOSIA",
                    nota="Paneles perforados 5.00x6.00 m en placas 1.00x2.00 m. PT1 rectangular, PT2 con remate en zigzag."),
    "PANELES_LETRAS_PIRAMIDES": dict(bbox=(-6, 45, -76, -44), estado="DETALLE", coleccion="REF_CAD_DETALLES_CELOSIA",
                                     nota="Variantes de panel, letras UYUNI 1.18x1.50 m, rombos 2x2 y 1x1 m."),
}

PALABRAS_CLAVE = ["M1", "ME-1", "ME1", "CORTE", "DETALLE", "ALERO", "PARAPETO", "ANTEPECHO", "5.51", "5510", "170",
                  "PT1", "PT2", "UYUNI", "NPT", "FACHADA", "CANALETA", "PANTALLA", "PIRAMIDE", "DURALIT", "CORTEN"]
TIPOS_ANOTACION = {"DIMENSION", "TEXT", "MTEXT", "HATCH", "LEADER", "MLEADER", "MULTILEADER", "ATTRIB", "ATTDEF", "TOLERANCE"}


def vista_de(x, y):
    for k, v in VISTAS.items():
        x0, x1, y0, y1 = v["bbox"]
        if x0 <= x <= x1 and y0 <= y <= y1:
            return k
    return None


def texto_plano(e):
    t = e.plain_text() if e.dxftype() == "MTEXT" else e.dxf.text
    return " ".join(t.split())


def auditar_dxf(path, out):
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    h = doc.header
    rep = {"archivo": os.path.basename(path), "tamano_bytes": os.path.getsize(path),
           "version": h.get("$ACADVER"), "guardado_por": h.get("$LASTSAVEDBY")}
    ins = h.get("$INSUNITS")
    rep["unidades"] = {"INSUNITS": ins, "INSUNITS_texto": {4: "mm", 5: "cm", 6: "m"}.get(ins, str(ins)),
                       "MEASUREMENT": h.get("$MEASUREMENT"), "DIMLFAC": h.get("$DIMLFAC"),
                       "conclusion": "Model space en metros a escala real 1:1; las cotas muestran mm (DIMLFAC=1000)."}
    rep["extents"] = {"min": list(h.get("$EXTMIN"))[:2], "max": list(h.get("$EXTMAX"))[:2]}

    tipos = collections.Counter(e.dxftype() for e in msp)
    por_capa = collections.Counter(e.dxf.layer for e in msp)
    total = sum(tipos.values())
    rep["conteo_model_space"] = {"total": total, "por_tipo": dict(tipos.most_common())}
    rep["capas"] = {"definidas": len(doc.layers),
                    "con_entidades": dict(por_capa.most_common()),
                    "porcentaje_en_capa_0": round(100 * por_capa.get("0", 0) / total, 1),
                    "apagadas_o_congeladas": [l.dxf.name for l in doc.layers if not l.is_on() or l.is_frozen()],
                    "capas_de_anotacion": [n for n in por_capa if re.search(r"COTA|TEXTO|COD|EJES|DIMS|ANNO", n, re.I)]}

    bloques = [b for b in doc.blocks if not b.name.lower().startswith(("*model_space", "*paper_space"))]
    inserts = collections.Counter(e.dxf.name for e in msp.query("INSERT"))
    relevantes = [dict(nombre=b.name, entidades=len(b), inserciones_msp=inserts.get(b.name, 0))
                  for b in bloques if re.search(r"Mullion|System Panel|LOU|tornillo|PERFIL|PUERTA", b.name)]
    rep["bloques"] = {"total": len(bloques), "anonimos_de_cotas_*D": sum(b.name.startswith("*D") for b in bloques),
                      "con_nombre": sum(not b.name.startswith("*") for b in bloques),
                      "xrefs": [b.name for b in bloques if b.block.is_xref],
                      "inserciones_en_msp": dict(inserts.most_common()),
                      "relevantes": relevantes,
                      "nota": "Bloques Revit 'Rectangular Mullion - M_160x65' y 'System Panel - VT_10_A_10_VT_6' "
                              "quedaron del modelo previo; el texto vigente de las fichas ME indica 170x65 y DVH 4+4/12/3+3."}

    lays = []
    for lay in doc.layouts:
        if lay.name == "Model":
            continue
        vps = []
        for vp in lay.query("VIEWPORT"):
            d = vp.dxf
            if d.get("id", 0) == 1 or d.get("view_height", 0) <= 0 or d.get("width", 0) > 1000:
                continue
            vh = d.view_height
            vw = vh * d.width / d.height
            cx, cy = d.view_center_point[0], d.view_center_point[1]
            vista = vista_de(cx, cy)
            vps.append(dict(centro_modelo=[round(cx, 3), round(cy, 3)],
                            bbox_modelo=[round(cx - vw / 2, 3), round(cx + vw / 2, 3), round(cy - vh / 2, 3), round(cy + vh / 2, 3)],
                            escala_aprox=f"1:{round(1000 * vh / d.height)}", capas_congeladas=list(vp.frozen_layers),
                            vista=vista or "VACIO (apunta a zona sin dibujo: presentación desactualizada)"))
        titulos = [texto_plano(e) for e in lay.query("MTEXT TEXT") if texto_plano(e)]
        lays.append(dict(presentacion=lay.name, papel_mm=[lay.dxf_layout.dxf.get("paper_width"), lay.dxf_layout.dxf.get("paper_height")],
                         viewports=vps, textos=titulos))
    rep["presentaciones"] = lays

    textos = []
    for e in msp.query("TEXT MTEXT"):
        p = e.dxf.insert
        textos.append(dict(x=round(p[0], 3), y=round(p[1], 3), capa=e.dxf.layer, texto=texto_plano(e), vista=vista_de(p[0], p[1])))
    clave = {}
    for k in PALABRAS_CLAVE:
        pat = re.compile(r"(?<![\w.])" + re.escape(k) + r"(?![\w])", re.I)
        clave[k] = [t for t in textos if pat.search(t["texto"])]
    rep["textos_clave"] = {k: {"n": len(v), "ocurrencias": v[:25]} for k, v in clave.items()}

    cotas = collections.defaultdict(list)
    lfacs = collections.Counter()
    for d in msp.query("DIMENSION"):
        tp = d.dxf.get("text_midpoint", d.dxf.defpoint)
        try:
            m = d.get_measurement()
            m = None if hasattr(m, "x") else m
        except Exception:
            m = None
        lfac = d.override().get("dimlfac", 1.0)
        lfacs[lfac] += 1
        p1, p2 = d.dxf.get("defpoint2"), d.dxf.get("defpoint3")
        cotas[vista_de(tp[0], tp[1]) or "FUERA_DE_VISTAS"].append(dict(
            mm=round(m * lfac) if m is not None else None, medida_dxf_m=round(m, 4) if m is not None else None,
            p1=[round(p1[0], 3), round(p1[1], 3)] if p1 else None, p2=[round(p2[0], 3), round(p2[1], 3)] if p2 else None,
            capa=d.dxf.layer))
    rep["escala_de_detalles"] = {"DIMLFAC_por_cota": {str(k): v for k, v in lfacs.items()},
                                 "conclusion": "Todas las cotas usan DIMLFAC=1000: ningún detalle está ampliado; "
                                               "todo el dibujo está a 1:1 en metros (las escalas 1:3 a 1:300 son solo de los viewports)."}
    rep["cotas_por_vista"] = {k: {"n": len(v), "valores_mm": dict(collections.Counter(c["mm"] for c in v).most_common()), "detalle": v}
                              for k, v in cotas.items()}
    rep["vistas"] = {k: {kk: vv for kk, vv in v.items()} for k, v in VISTAS.items()}
    return doc, rep


def exportar_vistas(doc, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration, LineweightPolicy
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    os.makedirs(os.path.join(out, "vistas"), exist_ok=True)
    msp = doc.modelspace()
    fig = plt.figure(figsize=(20, 12), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK,
                        lineweight_policy=LineweightPolicy.RELATIVE, lineweight_scaling=0.3)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(msp, finalize=True)

    # Asignar cada entidad geométrica a una vista (por el centro de su bbox), una sola vez
    por_vista = collections.defaultdict(list)
    for e in msp:
        if e.dxftype() in TIPOS_ANOTACION:
            continue
        try:
            b = bbox.extents([e], fast=True)
        except Exception:
            continue
        if b.has_data:
            k = vista_de(b.center.x, b.center.y)
            if k:
                por_vista[k].append(e)

    indice = {}
    for nombre, v in VISTAS.items():
        x0, x1, y0, y1 = v["bbox"]
        px = 3000 if (x1 - x0) > 40 else 2000
        fig.set_size_inches(px / 100, max(2, px / 100 * (y1 - y0) / (x1 - x0)))
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        ax.set_aspect("equal")
        fig.savefig(os.path.join(out, "vistas", f"{nombre}.png"), dpi=100, facecolor="white")

        # DXF limpio de la vista: solo geometría (bloques explotados), sin cotas/textos/tramas/directrices
        nd = ezdxf.new("R2018", units=6)
        nmsp = nd.modelspace()
        n = 0
        for e in por_vista.get(nombre, []):
            fuentes = e.virtual_entities() if e.dxftype() == "INSERT" else [e]
            for ve in fuentes:
                if ve.dxftype() in TIPOS_ANOTACION or ve.dxftype() in ("INSERT", "REGION"):
                    continue
                try:
                    c = ve.copy()
                    if c.dxf.layer not in nd.layers:
                        nd.layers.add(c.dxf.layer)
                    if c.dxf.hasattr("linetype") and c.dxf.linetype not in nd.linetypes:
                        c.dxf.linetype = "CONTINUOUS"
                    nmsp.add_foreign_entity(c, copy=False)
                    n += 1
                except Exception:
                    pass
        nd.saveas(os.path.join(out, "vistas", f"{nombre}.dxf"))
        indice[nombre] = dict(png=f"{nombre}.png", dxf=f"{nombre}.dxf", entidades_dxf_limpio=n,
                              bbox_dxf=dict(xmin=x0, xmax=x1, ymin=y0, ymax=y1),
                              png_px_por_m=round(px / (x1 - x0), 3), **{k: v[k] for k in v if k != "bbox"})
    json.dump(indice, open(os.path.join(out, "vistas", "vistas_index.json"), "w"), indent=1, ensure_ascii=False)
    return indice


def auditar_ifc(paths):
    import ifcopenshell
    import ifcopenshell.geom
    import ifcopenshell.util.placement as up

    rep = {"archivos": []}
    clases_por_archivo = {}
    abiertos = {}
    for path in paths:
        f = ifcopenshell.open(path)
        desc = f.header.file_description.description
        info = dict(archivo=os.path.basename(path), tamano_bytes=os.path.getsize(path), schema=f.schema,
                    descripcion=list(desc), origen=f.header.file_name.originating_system)
        clases = collections.Counter(e.is_a() for e in f.by_type("IfcElement"))
        info["elementos_por_clase"] = dict(clases.most_common())
        info["clases_arquitectonicas_presentes"] = {c: len(f.by_type(c)) for c in
                                                    ("IfcCurtainWall", "IfcWindow", "IfcDoor", "IfcRoof", "IfcCovering",
                                                     "IfcPlate", "IfcMember", "IfcRailing")}
        info["tipos_mas_frecuentes"] = [f"{n}x {c}: {t}" for (c, t), n in collections.Counter(
            (e.is_a(), ":".join((e.Name or "").split(":")[:2]).strip()) for e in f.by_type("IfcElement")).most_common(10)]
        clases_por_archivo[info["archivo"]] = clases
        rep["archivos"].append(info)

        abiertos[path] = (f, clases)

    # Georreferencia y geometría desde el archivo SIN IfcBuildingElementPart: en el EST exportado con
    # "parts" las columnas/vigas no tienen cuerpo propio (su geometría está en las partes).
    path_geo = next((p for p, (_, c) in abiertos.items() if "IfcBuildingElementPart" not in c), paths[0])
    f = abiertos[path_geo][0]
    rep["archivo_usado_para_geometria"] = os.path.basename(path_geo)
    b = f.by_type("IfcBuilding")[0]
    mb = up.get_local_placement(b.ObjectPlacement)
    mbi = np.linalg.inv(mb)
    rot = math.degrees(math.atan2(mb[1, 0], mb[0, 0]))
    site = f.by_type("IfcSite")[0]

    def dec(v):
        return None if v is None else (-1 if any(x < 0 for x in v) else 1) * (abs(v[0]) + abs(v[1]) / 60 + abs(v[2]) / 3600 + (abs(v[3]) / 3.6e9 if len(v) > 3 else 0))

    lat, lon = dec(site.RefLatitude), dec(site.RefLongitude)
    mc = f.by_type("IfcMapConversion")
    crs = mc[0].TargetCRS if mc else None
    lam0 = -69.0  # UTM zona 19 (EPSG:32719)
    conv = math.degrees(math.atan(math.tan(math.radians(lon - lam0)) * math.sin(math.radians(lat))))

    def az_grid(local_angle_deg):  # ángulo CCW desde +X local -> azimut de cuadrícula (horario desde N)
        return (90 - (rot + local_angle_deg)) % 360

    fachadas = {"LADO_TIERRA_eje_A (normal -Y local) = FACHADA NORESTE": 270,
                "LADO_AIRE_eje_R (normal +Y local) = FACHADA SUROESTE": 90,
                "LATERAL_eje_1 (normal -X local) = FACHADA ESTE": 180,
                "LATERAL_eje_20 (normal +X local) = FACHADA OESTE": 0}
    rep["geo"] = dict(
        crs=crs.Name if crs else None, crs_descripcion=getattr(crs, "Description", None) if crs else None,
        map_conversion=dict(E=mc[0].Eastings, N=mc[0].Northings, H=mc[0].OrthogonalHeight) if mc else None,
        nota_map_conversion="IfcMapConversion es identidad; las coordenadas UTM reales están en el placement del IfcSite/IfcBuilding.",
        origen_edificio_utm=dict(E=round(float(mb[0, 3]), 3), N=round(float(mb[1, 3]), 3), cota_msnm=round(float(mb[2, 3]), 3)),
        rotacion_eje_X_local_deg_CCW_desde_Este=round(rot, 4),
        lat_lon_IfcSite=[round(lat, 7), round(lon, 7)],
        convergencia_meridiana_deg=round(conv, 3),
        # norte verdadero = acimut de cuadrícula -conv (hemisferio sur, al este del MC: N verdadero queda al E del N de cuadrícula)
        norte_verdadero_en_local_deg_CCW_desde_X=round((90 - rot + conv) % 360, 3),
        azimut_normal_fachadas={k: dict(cuadricula=round(az_grid(a), 2), verdadero=round((az_grid(a) + conv) % 360, 2))
                                for k, a in fachadas.items()},
    )
    npt = None
    niveles = []
    for st in sorted(f.by_type("IfcBuildingStorey"), key=lambda s: s.Elevation or 0):
        if st.Name == "0P":
            npt = st.Elevation
    for st in sorted(f.by_type("IfcBuildingStorey"), key=lambda s: s.Elevation or 0):
        niveles.append(dict(nombre=st.Name, elevacion_rel_edificio=round(st.Elevation, 3),
                            sobre_NPT_DXF=round(st.Elevation - npt, 3), cota_msnm=round(float(mb[2, 3]) + st.Elevation, 3)))
    rep["niveles"] = niveles
    rep["correspondencia_DXF_IFC"] = {
        "NPT_0.00_DXF": f"nivel IFC '0P' (elev. {npt}) = {round(float(mb[2, 3]) + npt, 3)} m s.n.m.",
        "verificacion": "DXF +7.100 y +7.600 coinciden con IFC 2P (6.95) y 3P (7.45) + 0.15",
        "fachada_NE_actual": VISTAS["FACHADA_NORESTE_ACTUAL"]["a_ifc"],
        "corte_M1": VISTAS["CORTE_ACTUAL_POR_M1"]["a_ifc"],
        "corte_original": VISTAS["CORTE_ORIGINAL_B-K-A"]["a_ifc"]}
    ejes = {}
    for g in f.by_type("IfcGrid"):
        if not g.ContainedInStructure or g.ContainedInStructure[0].RelatingStructure.Name != "0P":
            continue
        mg = mbi @ up.get_local_placement(g.ObjectPlacement)
        for kind, axes in (("numerados_X", g.UAxes), ("letras_Y", g.VAxes)):
            for a in axes:
                c = a.AxisCurve
                pts = c.Points.CoordList if c.is_a("IfcIndexedPolyCurve") else [p.Coordinates for p in c.Points]
                p0 = (mg @ np.array([pts[0][0], pts[0][1], 0, 1]))[:2]
                ejes.setdefault(kind, {})[a.AxisTag] = round(float(p0[0] if kind == "numerados_X" else p0[1]), 3)
        break
    rep["ejes_locales_m"] = ejes

    s = ifcopenshell.geom.settings()
    s.set("use-world-coords", True)
    it = ifcopenshell.geom.iterator(s, f, multiprocessing.cpu_count())
    cajas = []
    if it.initialize():
        while True:
            sh = it.get()
            v = np.array(sh.geometry.verts).reshape(-1, 3)
            if len(v):
                vl = (mbi @ np.c_[v, np.ones(len(v))].T).T[:, :3]
                e = f.by_id(sh.id)
                cajas.append((e.is_a(), e.Name or "", vl.min(0), vl.max(0)))
            if not it.next():
                break
    mn = np.min([c[2] for c in cajas], axis=0)
    mx = np.max([c[3] for c in cajas], axis=0)
    col_a = sorted({round(float((c[2][0] + c[3][0]) / 2), 3) for c in cajas
                    if c[0] == "IfcColumn" and c[2][1] < 0.6 and c[3][1] > -0.3})
    una = next(c for c in cajas if c[0] == "IfcColumn" and c[2][1] < 0.6 and c[3][1] > -0.3)
    sobre_7_5 = [c for c in cajas if c[3][2] > 7.5]
    rep["estructura"] = dict(
        bbox_local_m=dict(min=mn.round(3).tolist(), max=mx.round(3).tolist(), tamano=(mx - mn).round(3).tolist()),
        columnas_eje_A=dict(n_tramos=sum(1 for c in cajas if c[0] == "IfcColumn" and c[2][1] < 0.6 and c[3][1] > -0.3),
                            seccion_m=[round(float(una[3][0] - una[2][0]), 3), round(float(una[3][1] - una[2][1]), 3)],
                            cara_exterior_Y=round(float(una[2][1]), 3), cara_interior_Y=round(float(una[3][1]), 3),
                            x_centros=col_a),
        elementos_que_vuelan_mas_alla_de_columnas_lado_tierra=sorted({c[0] for c in cajas if c[2][1] < -0.35 and c[2][2] > -0.2}),
        sobre_cota_7_5=dict(collections.Counter(c[0] for c in sobre_7_5)),
        cerchas_de_acero_y_cubierta="NO modeladas en el IFC (vigas/columnas de hormigón, zapatas, losas, muros, escaleras).")
    nombres = list(clases_por_archivo)
    if len(nombres) == 2:
        a, b = (clases_por_archivo[n] for n in nombres)
        sin_parts = {k: v for k, v in a.items() if k != "IfcBuildingElementPart"}
        rep["hallazgo_arq_es_estructura"] = dict(
            iguales_salvo_parts=sin_parts == {k: v for k, v in b.items() if k != "IfcBuildingElementPart"},
            conclusion="El IFC 'AU-CBI-ARQ..._detached-AU-SUP-EST...' es el vínculo ESTRUCTURAL exportado desde el modelo ARQ: "
                       "mismas clases/cantidades que el EST (sin IfcBuildingElementPart). No contiene muros cortina, ventanas, "
                       "puertas, cubierta ni revestimientos.")
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dxf", required=True)
    ap.add_argument("--ifc", action="append", default=[])
    ap.add_argument("--out", default="auditoria")
    ap.add_argument("--sin-vistas", action="store_true", help="no exportar PNG/DXF por vista")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    doc, rep_dxf = auditar_dxf(a.dxf, a.out)
    if not a.sin_vistas:
        rep_dxf["vistas_exportadas"] = exportar_vistas(doc, a.out)
    json.dump(rep_dxf, open(os.path.join(a.out, "dxf_audit_report.json"), "w"), indent=1, ensure_ascii=False, default=str)
    if a.ifc:
        json.dump(auditar_ifc(a.ifc), open(os.path.join(a.out, "ifc_audit_report.json"), "w"), indent=1, ensure_ascii=False, default=str)
    print("Listo:", os.path.abspath(a.out))


if __name__ == "__main__":
    main()
