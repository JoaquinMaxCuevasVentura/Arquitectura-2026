"""AEROPUERTO DE UYUNI - Terminal de Pasajeros: modelo paramétrico para Blender 5.2 (Cycles).

Genera el modelo completo, con medidas tomadas de la auditoría (00_auditoria/AUDITORIA.md).
No calca el DXF: toda la geometría sale de las cotas.

Cómo ejecutarlo:
  A) Blender > Scripting > Open > uyuni_modelo.py > Run Script
  B) Vía MCP (sesión local con el MCP de Blender), con execute_blender_code:
       p = r"C:/ruta/al/repo/aeropuerto_uyuni/01_blender/uyuni_modelo.py"
       exec(open(p, encoding="utf-8").read(), {"__file__": p, "__name__": "__main__"})
  C) Sin interfaz: herramientas/construir_blend.py (ver TRASPASO.md)
  Se puede volver a ejecutar: borra y regenera solo las colecciones que crea.

Sistema de coordenadas (el mismo del IFC, en coordenadas locales del edificio):
  X = ejes 1 -> 20 (eje 1 en X = 0)
  Y = ejes A -> R (Lado Tierra hacia -Y; eje A en Y = 0,192)
  Z = metros sobre el NPT ±0,00 (= nivel IFC 0P = 3666,593 m s.n.m.)
Georreferencia: UTM 19S (EPSG:32719), origen E 724956,439 / N 7737860,959, X local rotado 148,2058° (antihorario desde el Este).
Norte verdadero en coordenadas locales: 301,043° (antihorario desde +X). El Lado Tierra mira al NNE (azimut 31°).

Escenas (la propiedad "propuesta" de cada escena elige la paleta: 0 = P1 Patrimonio Ferroviario, 1 = P2 Salar & Litio):
  UYUNI_DIA                 luz de mañana (sol calculado para Uyuni), P1 - CAM_01, CAM_02, CAM_02B, CAM_04, CAM_05,
                            CAM_06, CAM_07, CAM_07B, CAM_08 y CAM_09 (Lado Aire), CAM_10 (pista), CAM_DRON
  UYUNI_DIA_P2_SALAR_LITIO  la misma mañana con la paleta P2 - CAM_07
  UYUNI_CREPUSCULO          hora azul: interior y alero encendidos, piso mojado, nieve - CAM_03
"""
import json
import math
import os
import random
import warnings

import bmesh
import bpy
from mathutils import Matrix, Vector

warnings.filterwarnings("ignore", category=DeprecationWarning)

# =============================================================================
# 1. PARÁMETROS (cotas de la reunión, el CAD y el IFC: ver AUDITORIA.md)
# =============================================================================
EJES_X = {"1": 0.0, "2": 4.8, "3": 9.6, "4": 14.4, "5": 19.2, "6": 24.0, "7": 28.8, "8": 33.6, "9": 38.4,
          "10": 43.2, "11": 48.0, "11'": 48.5, "13": 53.23, "14": 58.03, "15": 62.83, "16": 67.63,
          "17": 72.36, "18": 72.81, "19": 77.66, "20": 82.51}
EJES_Y = {"A": 0.192, "K": 4.213, "B": 9.282, "C": 15.192, "M": 19.147, "E": 22.571, "F": 27.742,
          "G": 28.862, "O": 31.967, "P": 34.492, "H": 35.892, "Q": 39.142, "I": 44.042, "R": 48.321}

COL_ANCHO = 0.40                  # columnas HºAº 0,40 (X) x 1,00 (Y) sobre el eje A
Y_COL_EXT, Y_COL_INT = -0.308, 0.692
Z_COL_TOPE = 7.60
Y_MURO_EXT = 0.392                # plano exterior del muro, las vigas y el panel M2 (e = 130 mm)
E_MURO = 0.130
Y_VIDRIO = (0.479, 0.506)         # DVH 4+4 / 12 / 3+3 = 26,8 mm, retirado 87 mm del plano del muro
Y_PERFIL = (0.522, 0.692)         # perfil de aluminio 170 x 65, hacia el interior
H_VANO = 5.51                     # altura de la mampara M1 (ME-1 / ME-2)
Z_TRAVESANO = (2.400, 2.465)      # travesaño 65 x 65
PERFIL_CARA = 0.065
VIGA_1 = (5.51, 6.01)             # viga HºAº 300 x 500 (dintel recto)
VIGA_2 = (7.10, 7.60)
Z_ANTEPECHO = (6.612, 9.012)      # antepecho de 2,40 m
Y_ANTEPECHO_EXT = -1.632          # cara exterior del antepecho (volado de 2,0 m desde el muro)
E_ANTEPECHO = 0.15
Z_CIELO = 6.635                   # cara inferior del cielo falso del alero
# Cielo falso tipo parrilla / listonado (pedido del 3 de octubre, antecedente del Rectorado): listones de 40 x 100
# perpendiculares a la fachada cada 0,15 m, sobre un plenum negro mate que impide ver el interior del alero
CIELO_LISTON = dict(ancho=0.040, alto=0.100, paso=0.150, plenum=0.18)
X_ALERO = (-0.23, 72.56)          # extensión del antepecho y la cubierta principal (fachada NE)
NERVIO_ANTEPECHO = 0.040          # el antepecho es continuación de la chapa de la cubierta (nervios verticales)
# Letrero "línea de horizonte": montículos de sal sobre el horizonte (+7,764) y su reflejo debajo (marcos y letras en
# contorno). Modulación del CAD: 1446 | rombo 2000 | rombo 1000 | 2717 | 3 x 1000 | 1184 | UYUNI 5576 | 5952 | rombo 2000 | 6401 | 308
# Desde el 3 de octubre todo el conjunto (letras, pirámides y horizonte) flota despegado de la chapa sobre pernos
# ocultos: su dorso queda a 12 cm de la chapa (8 cm delante de los nervios de 4 cm), así la sombra propia se separa
# de la pieza. Letras de 8 cm de espesor (cara frontal a 20 cm de la chapa) y montículos como pirámides facetadas en 3D.
LETRERO_SEP = 0.08                # separación entre el dorso del letrero y los nervios del antepecho
LETRERO_FONDO = dict(letras=0.08, reflejo=0.05, marcos=0.05, horizonte=0.05)
PIRAMIDE_FONDO = dict(grande=0.15, chica=0.10)   # saliente de la arista frontal, en la base
# Dos geometrías para la reunión: A sobresale del antepecho como en el CAD; B queda dentro de sus 2,40 m, centrada,
# con este margen libre arriba y abajo (escala resultante: 72 %). Ver variantes_letrero().
LETRERO_B_MARGEN = 0.12
# Juego asimétrico sin texto sobre la puerta de salida (ME-2 del eje 4-5, centro X 16,80): grande + 2 chicas
LETRERO_SALIDA = dict(x0=14.80, piezas=("grande", "chica", "chica"), horizonte=(13.30, 20.30))

# Perfil de cubierta (Y, Z cara superior): corte del DXF + alzados laterales; cumbrera sobre los ejes F/G
CUMBRERA_Z = 13.02                # las laterales marcan +13,02 y las fachadas NE/SO +13,43 (sin confirmar)
PERFIL_CUBIERTA = [(-1.672, 9.14), (16.30, 11.77), (28.28, CUMBRERA_Z), (37.73, 10.96), (45.875, 7.98), (48.68, 7.98)]
E_CUBIERTA = 0.10
NERVIO_PASO = 0.30                # chapa engrapada con nervios cada 0,30 m
NERVIO_SECCION = (0.025, 0.045)
# Retenedor de nieve según el detalle del cliente (4 de octubre): abrazadera de chapa de 174 mm de alto y 113 mm de
# base, perpendicular a la chapa y en el plano del nervio, con dos orejas de 38 mm que muerden el nervio y tres
# agujeros de 23 mm (centros a 48,5, 92,5 y 137,5 mm de la base); un tubo por agujero. Su eje queda a 1398 mm del
# borde de la cubierta, medido sobre la pendiente, encima de la primera correa (sobre la línea de las columnas).
# Abrazaderas cada 2 nervios. El tubo es de 21,3 mm (1/2" de cañería): uno de 1" (25,4 mm) no entra en el agujero.
RETENEDOR = dict(dist_borde=1.398, alto=0.174, base=0.113, oreja=(0.038, 0.035), espesor=0.006, cabeza_r=0.014,
                 agujero_d=0.023, agujeros=(0.0485, 0.0925, 0.1375), tubo_d=0.0213, paso=0.60)

# --- Lado Aire (fachada SUROESTE): alzado SO, planta baja A111 e IFC (4 de octubre). Las X del alzado SO van corridas
# 2,6 cm respecto de la planta y del IFC: todo va en coordenadas de la planta. Solo el bloque de los ejes 1-5 llega al
# eje R (cara a 48,601); entre los ejes 5 y 17 la fachada es el muro del eje I (cara a 43,872) con pilastras.
Y_FACHADA_AIRE = {"principal_izq": 48.601, "principal_der": 43.872}  # cara exterior: bloque (eje R) | muro del eje I
X_CAMBIO_AIRE = 19.33             # cara este del bloque del eje R (su muro lateral, sobre la marquesina)
E_MURO_AIRE = 0.16                # panel de 100 mm con revoque de 30 mm a cada lado (planta)
Y_PILASTRA_AIRE = 44.572          # cara de las columnas C40x100 (43,542-44,542) revocadas; ahí termina la cubierta
# Revisión del cliente: los paños opacos y las ventanas pequeñas se enrasan
# con las pilastras. Solo las dos crujías con grandes ME-5/ME-6 forman nichos.
Y_MURO_RAS_AIRE = Y_PILASTRA_AIRE
PILASTRAS_AIRE = [19.2, 24.0, 28.8, 33.6, 38.4, 48.5, 53.23, 58.03, 62.83, 67.63, 72.36]   # ejes con columna a la vista
Z_PILASTRA = 7.01
BUNAS_AIRE = (3.26, 3.76, 6.51, 7.01)    # vigas de borde V30x50 (+3,20 y +6,45) enrasadas en el revoque: solo buñas
# Carpinterías del muro del eje I (X0, X1) y alturas, del alzado SO corrido a la planta
ME4_AIRE = [(53.46, 55.955), (58.26, 60.755), (63.062, 65.557), (67.86, 70.355)]   # dos paños, marco de 65 mm
ME4_Z = (4.82, 6.51)
ME5_AIRE = [(33.83, 38.17, 3.76, 6.51), (38.63, 42.97, 3.76, 6.51), (33.83, 38.17, 0.0, 2.66)]   # tres paños
ME6_AIRE = [(38.659, 42.94)]      # corrediza: fijos de 1,103, dos hojas de 0,938 (+2,192) y cabezal de +2,242 a +2,362
ME6_Z = 2.362
ENROLLABLES_AIRE = [(22.285, 23.77), (24.521, 26.021), (55.807, 57.307), (58.28, 59.78), (61.455, 62.60)]  # PR-11 y PR-10
Z_ENROLLABLE = 1.60
PUERTA_P01_AIRE = (69.775, 70.775, 2.10)                     # batiente de 1,00 x 2,10
NICHO_AIRE = dict(x=(29.03, 30.23), y=(42.66, 43.872), z=3.20, puerta_y=(42.69, 43.69))   # entrada con puerta lateral
PUERTA_FRONTAL_AIRE = (NICHO_AIRE["x"][0] + .10, NICHO_AIRE["x"][1] - .10, 2.10)
MARQUESINA_AIRE = dict(x=(19.33, 28.95), y=(43.872, 46.786), losa=(3.65, 3.70), viga=(3.20, 3.70), borde_y=46.486,
                       vigas_x=[(23.85, 24.15), (28.65, 28.95)], vigueta=(0.10, 3.45, 3.65), paso=0.50)
VESTIBULO_AIRE = dict(x=(42.97, 48.23), y=(43.872, 46.894), z=7.325, puerta_y=(44.554, 46.529), puerta_z=2.362)
# Puertas de embarque del nivel 1P (+3,85): cajas vidriadas de 2,00 x 2,30 del alzado SO, en el bloque y en el vestíbulo
EMBARQUE_Z = (3.82, 6.12)
CAJA_VESTIBULO = dict(x=(45.887, 47.887))
# Bloque del eje R hacia la pista: vano libre a una galería cubierta (al fondo, la ME-5 del muro del eje I) y una
# abertura con antepecho de 0,40; entre el bloque y la galería, un muro vidriado con puerta doble en X 8,0
BLOQUE_AIRE = dict(vano=(9.80, 14.20, 0.0, 3.26), abertura=(14.50, 17.84, 0.40, 3.26), galeria_x=(8.0, 19.17),
                   me5=(9.83, 14.17, 0.0, 2.66), puerta_y=(45.312, 47.392))
BAJANTE_OESTE = dict(x=-0.306, y=48.45, d=0.10, z=(0.30, 7.98),
                     abrazaderas=(0.315, 0.54, 1.228, 1.681, 2.575, 3.469, 3.882, 4.213, 4.732, 5.052, 5.238, 5.463,
                                  6.15, 6.604, 7.498))
ANEXO = dict(x=(72.81, 82.71), y=(Y_COL_EXT, 43.624), z=6.30)       # bloque bajo, ejes 18-20 (cara aire: planta)
Y_CELOSIA_SO = 43.88              # plano de las PT2 delante del anexo (planta: 43,782-43,882)
# Testero del eje 20 (FACHADA ESTE): puertas dobles con rejilla encima, puertas simples con sobreluz de rejilla y
# la boca de un patio techado (retirado al eje X 77,9) dividida por la columna del eje E
PUERTAS_DOBLES_ESTE = [(3.039, 4.889), (7.114, 8.964), (11.48, 13.33)]   # marco: hojas de 0,80 x 2,00, rejilla +2,07..2,79
PUERTAS_SIMPLES_ESTE = [(15.978, 16.978)]                                  # hoja de 0,97 x 2,01, rejilla +2,02..2,30
PATIO_ESTE = dict(bocas=[(18.703, 22.421), (22.721, 27.248)], z=3.21, x_fondo=77.90, puerta_fondo=(25.628, 26.628),
                  puerta_lado=(80.20, 81.20))

# --- Lado Tierra: vereda y cordón de la planta baja A111 (capa A-FLOR, aplicada el 4 de octubre). La vereda llega a
# 8,8 m del muro, con dos dársenas de ascenso y descenso de 2,10 m de fondo (tramo recto de 7,17 m y rampas a 45° con
# curvas de r 1,0); la esquina oeste dobla en una curva de r 4,021 y la este en una de r 1,0. Los cordones laterales
# siguen hacia el Lado Aire (cordon_aire).
ZANJA = dict(y=(-1.965, -1.465), prof=0.20)                          # bajo la línea de goteo del alero
BORDILLO_DESNIVEL = 0.15
Y_CORDON_TIERRA = -8.413
DARSENAS_TIERRA = (20.975, 62.96)       # X donde el cordón deja la línea de -8,413 para entrar en cada dársena
DARSENA = dict(fondo=2.10, recto=7.171, r=1.0)
X_CORDON_LATERAL = (-3.57, 85.515)      # cordones de las veredas laterales (testeros de los ejes 1 y 20)
# Frente del Lado Tierra (circulaciones y jardineras): no está en la A111. Restituido por fotogrametría de las capturas
# del modelo del cliente (DALUX, 4 de octubre): cámaras calibradas con aristas del edificio (cubierta, anexo, celosías)
# y rectas de fuga; las plantas sacadas de capturas distintas coinciden en ±0,5 m y todo queda paralelo a la fachada.
# De norte a sur: cordón A111 con una línea amarilla a 0,5 m; dos carriles de llegada (línea blanca discontinua en
# -13,5); jardineras A y B (tierra oscura con cordón de hormigón y anillos elevados blancos); carriles de salida;
# separador amarillo L1 y la plaza de estacionamiento (hexágonos elevados, espiga en zigzag y andén del bus).
# La calzada sigue al oeste hacia Uyuni (acceso) y al sur por la calle del eje 20. Las calles de los testeros y la
# vereda con sus dársenas quedan como estaban.
CALLE_ANCHO = 7.0                                     # calles de los testeros (ejes 1 y 20) hasta la plataforma: sin cambios
FRENTE = dict(
    y_l1=-32.6, ancho_l1=0.6, x_l1=(-27.0, 78.0),     # separador amarillo (cordón bajo pintado) frente a la plaza
    oeste=dict(x=(-3000.0, -37.0), y_norte=-9.2, y_sur=-23.0),   # acceso hacia Uyuni y ensanche hasta L1
    via_este=dict(x_sur=(90.0, 98.8), y_sur=-400.0, r=12.0, empalme=(-14.0, -26.0)),   # calle del eje 20 al sur del frente
    plaza=[(-4.5, -33.15), (-4.5, -52.0), (-3.8, -58.8), (6.0, -58.8), (3.3, -55.4), (76.0, -55.4), (77.4, -54.0),
           (77.4, -33.15)],                           # contorno antihorario, con la cuña (rampa) del sudoeste
    carril=dict(y=-13.5, trazo=2.0, paso=9.6, x0=64.7, x=(-27.0, 84.0)),    # discontinua blanca de los carriles de llegada
    me2=dict(margen=1.0, fondo=4.0),                  # recuadro claro con borde blanco frente a cada ME-2 (paso peatonal)
    linea_cordon=[(1.43, -8.9), (84.5, -8.9)],      # línea amarilla a 0,5 m del cordón, frente al edificio
)
# Jardineras: tierra con cordón de hormigón; anillos elevados blancos (centro X, centro Y, largo, ancho) de 0,20 x 0,45;
# hexágonos elevados de la plaza (centro X, centro Y, radio al vértice); línea amarilla a 0,7 m del borde sur de la B
JARDINERAS = dict(cordon=0.15, linea_b=0.7, anillo=dict(espesor=0.20, alto=0.45),
                  anillos=[(-19.5, -22.4, 7.4, 1.5), (9.0, -25.3, 4.8, 1.3), (44.25, -22.4, 5.5, 1.4),
                           (73.55, -24.0, 10.1, 2.2)],
                  hexagonos=[(3.8, -41.4, 3.6), (68.4, -40.7, 3.6)])
# Espiga de la plaza: dos líneas en zigzag a 45° (tramos de 2,59 m) entre el andén y el hexágono este; cordones bajos
ESPIGA = dict(paso=3.66, amplitud=1.83, sup=(47.5, -36.97, 50.63, -40.13, 4), inf=(47.67, -43.03, 5), x_fin=64.5)
ANDENES = [(40.5, 48.0, -26.2, -23.6), (40.0, 47.5, -37.6, -33.15)]     # andenes del bus (X0, X1, Y0, Y1), +0,15
CEBRA = dict(x=(77.5, 81.0), y=(-32.6, -26.4), franja=0.5, paso=1.0)     # cruce peatonal en el extremo este
DISCOS = [(56.5, -28.9), (42.1, -29.5), (31.5, -37.5), (82.84, -29.3), (84.9, -27.3), (84.94, -31.8)]   # tapas amarillas
COLUMNAS = dict(pos=[(83.2, -44.4), (85.2, -42.4)], diametro=0.9, alto=3.5)   # columnas amarillas de la isla sudeste

# Celosías corten: módulos de 5,00 x 6,00 m (placas de 1,00 x 2,00 m de 1 mm), a 0,12 m de su fondo
CELOSIA_SEP = 0.12
JUNTA_ESQUINA_NO = 0.003         # junta entre las dos chapas, sin prolongarlas a través del plano perpendicular
CELOSIAS = [  # (fachada, variante, inicio, fin) - en NE/SO son X; en laterales son Y. Variante según el DXF:
    # PT1 rectangular | PT2A picos en 0-2-4 m | PT2B picos en 1-3-5 m | PT2R rampa a 45° (de 2,0 a 6,0 m) + zigzag
    ("NE", "PT2B", -0.469, 4.531), ("NE", "PT2A", 4.531, 9.531),
    ("NE", "PT2R", 67.932, 72.932), ("NE", "PT2B", 72.932, 77.932), ("NE", "PT2A", 77.932, 82.932),
    ("SO", "PT2B", 72.94, 77.94), ("SO", "PT2A", 77.94, 82.94),
    # OESTE: dos PT1 más y un módulo en rampa (DXF del 4 de octubre)
    ("EJE1", "PT1", -0.579, 4.421), ("EJE1", "PT1", 4.421, 9.421), ("EJE1", "PT1", 9.421, 14.421),
    ("EJE1", "PT1", 14.421, 19.421), ("EJE1", "PT1R", 19.421, 24.421),
    ("EJE20", "PT2A", -0.388, 4.612), ("EJE20", "PT2B", 4.612, 9.612),
]
# borde superior de cada variante (u, v) - la estructura (líneas salmón del CAD) lo sigue
BORDE_SUPERIOR = {"PT1": [(0, 6.0), (5, 6.0)],
                  "PT2A": [(u, 6.0 if u % 2 == 0 else 5.0) for u in range(6)],
                  "PT2B": [(u, 6.0 if u % 2 == 1 else 5.0) for u in range(6)],
                  "PT2R": [(0, 2.0), (4, 6.0), (5, 5.0)],
                  "PT1R": [(0, 6.0), (1, 6.0), (5, 2.0)]}      # PT1 con bajada a 45° (OESTE, de 6,0 a 2,0 m)
Z_CELOSIA = 0.20
Z_CELOSIA_FACHADA = {"EJE1": 0.11}   # el alzado OESTE las apoya a +0,11

# Mamparas del Lado Tierra (X inicial, X final) - centradas en sus vanos
ME1 = [(10.925, 13.075), (20.525, 22.675), (30.125, 32.275), (34.925, 37.075), (39.725, 41.875),
       (49.800, 51.950), (59.355, 61.505)]
ME2 = [(14.660, 18.940), (53.490, 57.770)]
ME3_NE = [(2.03, 2.068), (7.03, 2.068), (65.43, 2.278), (70.43, 2.278)]     # (X centro, Z centro); rombo de 1,20
ME3_EJE1 = [(41.32, 1.86), (36.81, 1.86), (6.84, 1.86), (2.04, 1.86)]        # (Y centro, Z centro)
ME3_EJE20 = [(33.28, 1.86), (39.16, 1.86)]
ME3_SO = [(75.435, 1.862), (80.435, 1.862)]                                 # (X centro, Z centro) detrás de las PT2 del Lado Aire
# Fachada OESTE (testero del eje 1): rombo perforado sobre el ME-3 (lado 1,96; interior 1,36), bloque bajo con mástil
ROMBO_OESTE = dict(y=36.815, z=5.65, semi_ext=1.389, semi_int=0.965, semi_placa=0.93)
MASTIL_OESTE = dict(x=0.6, y=48.37, z_base=7.98, z_cambio=8.88, z_tope=10.38)
# caja de la puerta de embarque del bloque: sobresale 1,91 m hacia la pista (alzado OESTE); X del alzado SO
CAJA_OESTE = dict(x=(0.83, 2.83), y=(48.601, 50.51), z=(3.45, 6.15))
PLATAFORMA_OESTE = dict(x=(0.3, 2.8), y=(48.601, 49.777), z=0.45)      # descanso de 0,45 m con 3 escalones (alzado OESTE)
# Fachada ESTE (testero del eje 20): franja de chapa nervada (color del parapeto), en todo el ancho
FRANJA_ESTE = dict(y=(-0.308, 43.474), z=(4.41, 6.21))
# Entorno del Lado Aire: cordón de la planta baja A111 (capa A-FLOR, en cordon_aire) y camino de servicio de la vista
# aérea del cliente (la banda azul), paralelo a la fachada entre la vereda y los puestos de las aeronaves
CAMINO_AIRE_Y = (55.0, 65.0)
PLATAFORMA_AIRE = dict(x=(-110.0, 200.0), y=(40.0, 130.0))   # la calle de rodaje de la plataforma más 28 m
CALLE_RODAJE_Y = 102.0            # eje amarillo de la calle de rodaje de la plataforma, detrás de los puestos
# --- Contexto del aeropuerto (4 de octubre). Pista 13/31 de 4000 x 45 m de asfalto (datos publicados del aeródromo
# SLUY): llevadas a coordenadas locales con la georreferencia del IFC, sus cabeceras caen en X -1034,5 (31) y
# X 2962,6 (13) y la pista queda paralela al eje X, como el edificio. Esa misma georreferencia la pone 55 m del lado
# tierra, lo que no es posible (el origen del IFC no está en el sitio real de la terminal): se mantienen las X y la
# orientación, y el eje va del Lado Aire a una distancia supuesta. Con 330 m, la plataforma queda fuera de la franja
# (150 m) y las colas de los 737 y la cumbrera quedan bajo la superficie de transición 1:7. A confirmar con el plano
# de sitio del cliente.
PISTA = dict(x=(-1034.5, 2962.6), y=330.0, ancho=45.0, sobrepaso=60.0, nombres=("31", "13"))
RODAJE = dict(x=150.0, ancho=23.0, r_plataforma=30.0, r_pista=45.0, espera=90.0)   # calle de rodaje a la pista
MANGA_VIENTO = (230.0, 250.0)
# Terreno: altiplano plano alrededor del aeropuerto, curvatura de la Tierra (radio efectivo con refracción) desde
# 3,5 km y cordones de cerros en el horizonte; al oeste y noroeste, el Salar de Uyuni (blanco y plano) desde 18 km.
TERRENO = dict(radio=45000.0, r_plano=3500.0, r_tierra=7.43e6, centro=(41.0, 22.0), azimutes=240)
CERROS = [  # (azimut verdadero °, semiancho °, distancia km, altura m): cordillera de Chichas al este, lomas al sur
    (28.0, 14.0, 26.0, 250.0), (58.0, 18.0, 17.0, 390.0), (88.0, 14.0, 14.0, 480.0), (112.0, 12.0, 19.0, 420.0),
    (138.0, 16.0, 23.0, 350.0), (163.0, 12.0, 30.0, 290.0), (192.0, 18.0, 34.0, 230.0), (222.0, 12.0, 40.0, 260.0),
    (352.0, 16.0, 40.0, 230.0), (8.0, 10.0, 36.0, 190.0)]
SALAR = dict(azimut=(238.0, 332.0), desde=15000.0)   # sin lomas delante: desde 26 m de altura se ve como franja blanca
# Paja brava (Festuca orthophylla): matas de 0,3 a 0,8 m dispersas en el suelo libre y en las islas del estacionamiento
PAJA_BRAVA = dict(radio=650.0, densidad=0.045, semilla=7, margen=1.5)
# Librea de Boliviana de Aviación (BoA) en los dos 737-800 (pedido del cliente, 4 de octubre), aproximada: fuselaje
# blanco, deriva y winglets azul BoA, franjas rojo-amarillo-verde de la bandera en la deriva y el nombre en azul.
LIBREA_BOA = dict(azul="#1C3F94", rojo="#D52B1E", amarillo="#F4D000", verde="#007934",
                  # (texto, x de inicio desde la nariz, base sobre el eje del fuselaje, alto): sobre y bajo las ventanillas
                  titulo=("BoA", -6.0, 0.66, 1.10), subtitulo=("Boliviana de Aviación", -6.3, -0.08, 0.20))
# Mangas (puentes de embarque) en las dos puertas del nivel 1P y dos Boeing 737-800 (con la librea de BoA desde el 4
# de octubre), estacionados como en la captura del modelo del cliente: casi paralelos a la fachada, nariz hacia el eje 1
MANGAS = [dict(x=sum(CAJA_OESTE["x"]) / 2, y_frente=CAJA_OESTE["y"][1]), dict(x=46.887, y_frente=46.894)]
MANGA = dict(z_piso=3.85, y_rotonda=52.6, r_rotonda=1.8, tunel_a=(2.5, 3.0), tunel_b=(2.75, 3.25),
             cabina=(3.2, 3.4, 3.1))
AVION_RUMBO = 200.0               # grados desde +X: nariz hacia el eje 1 y 20° hacia el edificio
AVION_PUERTA_L1 = (-4.0, 2.70)    # puerta delantera izquierda: 4,0 m detrás de la nariz, umbral a +2,70 del piso
PUERTA_DESDE_ROTONDA = (3.5, 15.9)   # posición de la puerta L1 de cada avión respecto de la rotonda de su manga

# Luz: Uyuni, fecha/hora del hero shot (mañana) y de la hora azul
LAT, LON, UTC_OFFSET = -20.4461546, -66.8497209, -4.0
NORTE_LOCAL_DEG = 301.043         # norte verdadero, antihorario desde +X local
FECHA_DIA = (2026, 10, 4, 9.50)   # 09:30
FECHA_CREPUSCULO = (2026, 10, 4, 18.65)
ALTITUD_MSNM = 3666.6
# aire seco y limpio del altiplano: pocos aerosoles y algo más de ozono para un azul más profundo
CIELO_ATMOSFERA = dict(air_density=0.9, aerosol_density=0.02, dust_density=0.02, ozone_density=3.0)

# Propuestas de color para la decisión de gerencia (reunión del 3 de octubre). La propiedad "propuesta" de cada
# escena elige la paleta: 0 = P1 "Patrimonio Ferroviario" (corten y tonos oscuros), 1 = P2 "Salar & Litio" (blanco
# integral). Cada rol tiene (color sRGB, metálico, rugosidad) para P1 y para P2.
PALETA = {
    "cubierta":  (("#373C40", 0.35, 0.45), ("#C3C6C8", 0.55, 0.35)),   # P1 antracita RAL 7016 | P2 gris claro aluminio
    "antepecho": (("#373C40", 0.15, 0.55), ("#ECEBE6", 0.0, 0.50)),    # parapeto y remates: antracita mate | blanco perla
    "muro":      (("#B9B5AD", 0.0, 0.92), ("#36393B", 0.0, 0.90)),     # revoque continuo: hormigón claro | casi negro (4 oct)
    "cielo":     (("#8C5A34", 0.0, 0.55), ("#EDECE8", 0.0, 0.50)),     # listones: símil madera | blanco
    "celosia":   (("#8E4524", 0.20, 0.80), ("#EFEEE9", 0.0, 0.50)),    # corten oxidado (color medio) | blanco perla
    "bastidor":  (("#232323", 0.60, 0.50), ("#36393B", 0.0, 0.80)),    # oscuro | igual al muro (se pierde detrás)
}
# Carpintería (perfiles, puertas, viga y operador de la ME-2), en las dos propuestas: aluminio con pintura en polvo
# negro mate (pedido del 4 de octubre; antes antracita #3A3E41). Sin metálico y rugosa, como una pintura mate real;
# #2E2F31 es ≈ 0,027 de luminancia lineal, el negro más oscuro que no se vuelve un hueco sin forma en el render.
PERFIL_COLOR = "#2E2F31"
PERFIL_RUGOSIDAD = 0.60
# Revisión del 4 de octubre: en P2 (parapeto blanco) las letras y pirámides van en un gris casi negro, no en blanco,
# igual que los muros; propiedad "letras_gris" de la escena (1 en P2). Letras del tamaño original: geometría A.
# #2E3133 es ≈ 0,03 de luminancia lineal, el piso de albedo de la guía (como el asfalto nuevo); el muro, #36393B, ≈ 0,04.
LETRAS_GRIS = "#2E3133"
# Vidrio elegido el 4 de octubre: DVH con laminado incoloro 3+3 adentro, cámara y 4 mm con control solar afuera. Tono
# oscuro y poca reflexión, para que la fachada no sea un espejo ciego (MATERIALES_INTELIGENTES.md, sección 4, variante 6).
# El reflejo sale de una capa fina: a cuarto de onda sobre vidrio, IOR 1,8 da ≈ 13 % por cara, con pico en 4·n·d ≈ 482 nm.
VIDRIO = dict(tinte="#6E808E", capa_nm=67.0, capa_ior=1.8, onda_paso=0.33, polvo_ao=0.12)

PREFIJO = "UY_"
COLECCIONES = ["_REF_CAD", "01_ESTRUCTURA", "02_ENVOLVENTE", "03_CARPINTERIAS_M1", "04_CUBIERTA_INDUSTRIAL",
               "05_CELOSIAS_CORTEN", "06_ENTORNO_SITE", "07_ASSETS", "08_CAMERAS_LIGHTS", "10_MANGAS_AERONAVES",
               "11_CONTEXTO_AEROPUERTO"]

# Chapas de las celosías ya resueltas (contorno menos calados andinos): PT1, PT2A (picos en 0-2-4 m) y PT2B
# (picos en 1-3-5 m), con origen en la esquina inferior izquierda del módulo; y letras UYUNI en coordenadas de la
# fachada NE (x = X, y = Z). Extraídos de las tramas del DXF (ver 00_auditoria).
DATOS_GEOM = json.loads(r"""{"UYUNI":[{"ext":[[55.0503,8.3141],[55.0562,8.2754],[55.0789,8.2022],[55.1149,8.1359],[55.1625,8.0782],[55.2202,8.0306],[55.2865,7.9946],[55.3597,7.9719],[55.3985,7.9659],[55.4383,7.9639],[55.4782,7.9659],[55.517,7.9719],[55.5902,7.9946],[55.6564,8.0306],[55.7142,8.0782],[55.7618,8.1359],[55.7978,8.2022],[55.8205,8.2754],[55.8264,8.3141],[55.8284,8.354],[55.8284,9.2639],[56.0284,9.2639],[56.2284,9.2639],[57.0086,8.0958],[57.0086,9.2639],[57.2086,9.2639],[57.2086,7.7639],[57.0086,7.7639],[56.2284,8.9321],[56.2284,7.7639],[56.0284,7.7639],[56.0284,8.354],[56.0254,8.2937],[56.0164,8.2351],[56.0019,8.1786],[55.9821,8.1243],[55.9572,8.0728],[55.9277,8.0241],[55.8937,7.9787],[55.8556,7.9368],[55.8137,7.8987],[55.7683,7.8647],[55.7196,7.8352],[55.668,7.8103],[55.6138,7.7905],[55.5573,7.7759],[55.4987,7.767],[55.4383,7.7639],[55.378,7.767],[55.3194,7.7759],[55.2629,7.7905],[55.2086,7.8103],[55.1571,7.8352],[55.1084,7.8647],[55.063,7.8987],[55.0211,7.9368],[54.983,7.9787],[54.949,8.0241],[54.9195,8.0728],[54.8946,8.1243],[54.8748,8.1786],[54.8602,8.2351],[54.8513,8.2937],[54.8482,8.354],[54.8482,9.2639],[55.0482,9.2639],[55.0482,8.354]],"holes":[]},{"ext":[[54.2756,7.7639],[54.0756,7.7639],[54.0756,8.3611],[53.5029,9.2639],[53.7397,9.2639],[54.1756,8.5768],[54.6114,9.2639],[54.8482,9.2639],[54.2756,8.3611]],"holes":[]},{"ext":[[57.6987,7.7639],[57.6987,9.2639],[57.8987,9.2639],[57.8987,7.7639]],"holes":[]},{"ext":[[52.5306,8.2754],[52.5533,8.2022],[52.5893,8.1359],[52.6369,8.0782],[52.6947,8.0306],[52.7609,7.9946],[52.8342,7.9719],[52.8729,7.9659],[52.9128,7.9639],[52.9527,7.9659],[52.9914,7.9719],[53.0646,7.9946],[53.1309,8.0306],[53.1886,8.0782],[53.2362,8.1359],[53.2722,8.2022],[53.2949,8.2754],[53.3009,8.3141],[53.3029,8.354],[53.3029,9.2639],[53.5029,9.2639],[53.5029,8.354],[53.4998,8.2937],[53.4909,8.2351],[53.4763,8.1786],[53.4565,8.1243],[53.4316,8.0728],[53.4021,8.0241],[53.3681,7.9787],[53.33,7.9368],[53.2881,7.8987],[53.2427,7.8647],[53.194,7.8352],[53.1425,7.8103],[53.0882,7.7905],[53.0317,7.7759],[52.9731,7.767],[52.9128,7.7639],[52.8524,7.767],[52.7938,7.7759],[52.7373,7.7905],[52.6831,7.8103],[52.6315,7.8352],[52.5828,7.8647],[52.5374,7.8987],[52.4955,7.9368],[52.4574,7.9787],[52.4235,8.0241],[52.3939,8.0728],[52.3691,8.1243],[52.3492,8.1786],[52.3347,8.2351],[52.3257,8.2937],[52.3227,8.354],[52.3227,9.2639],[52.5227,9.2639],[52.5227,8.354],[52.5247,8.3141]],"holes":[]}],"UYUNI_nota":"coordenadas absolutas de la fachada NE: x = X_ifc, y = z sobre NPT","PT1":[{"ext":[[4.0025,0.0],[4.0025,0.9439],[4.5081,1.4495],[4.0025,1.955],[4.0025,1.9975],[4.1543,1.9975],[4.8926,1.2592],[4.9742,1.3408],[4.3175,1.9975],[4.4009,1.9975],[4.9392,1.4591],[4.9392,1.5566],[4.4984,1.9975],[4.5817,1.9975],[4.9392,1.64],[4.9392,1.7643],[4.706,1.9975],[4.7894,1.9975],[4.9392,1.8477],[4.9392,1.9975],[5.0,1.9975],[5.0,0.8218],[4.2784,0.1001],[5.0,0.1001],[5.0,0.0]],"holes":[[[4.1889,0.6124],[4.1661,0.6146],[4.1433,0.6124],[4.122,0.6058],[4.1028,0.5953],[4.086,0.5814],[4.0721,0.5647],[4.0616,0.5455],[4.055,0.5242],[4.0528,0.5013],[4.055,0.4785],[4.0616,0.4572],[4.0721,0.438],[4.086,0.4212],[4.1028,0.4073],[4.122,0.3969],[4.1433,0.3903],[4.1661,0.388],[4.1889,0.3903],[4.2102,0.3969],[4.2294,0.4073],[4.2462,0.4212],[4.2601,0.438],[4.2706,0.4572],[4.2771,0.4785],[4.2794,0.5013],[4.2771,0.5242],[4.2706,0.5455],[4.2601,0.5647],[4.2462,0.5814],[4.2294,0.5953],[4.2102,0.6058]]]},{"ext":[[3.0025,0.0],[3.0025,0.8385],[3.9975,1.8335],[3.9975,1.3398],[3.602,1.3398],[3.9975,0.9443],[3.9975,0.0]],"holes":[]},{"ext":[[2.0025,0.0],[2.0025,0.8326],[2.406,0.4291],[2.3896,0.3928],[2.3873,0.3527],[2.399,0.3143],[2.4244,0.2815],[2.46,0.2601],[2.4995,0.253],[2.5391,0.2601],[2.5747,0.2815],[2.6001,0.3143],[2.6118,0.3527],[2.6094,0.3928],[2.5931,0.4291],[2.9975,0.8335],[2.9975,0.0]],"holes":[]},{"ext":[[1.0025,0.0],[1.0025,0.9452],[1.3971,1.3398],[1.0025,1.3398],[1.0025,1.8326],[1.9975,0.8376],[1.9975,0.0]],"holes":[]},{"ext":[[0.0,0.0],[0.0,0.1001],[0.6164,0.1001],[0.0,0.7166],[0.0,1.9975],[0.0602,1.9975],[0.0602,1.8498],[0.2079,1.9975],[0.321,1.9975],[0.0602,1.7367],[0.0602,1.6421],[0.4156,1.9975],[0.5216,1.9975],[0.0602,1.5362],[0.0602,1.4416],[0.6162,1.9975],[0.7348,1.9975],[0.0602,1.3229],[0.0602,1.213],[0.8447,1.9975],[0.9975,1.9975],[0.9975,1.9559],[0.491,1.4495],[0.9975,0.943],[0.9975,0.0]],"holes":[[[0.8327,0.6146],[0.8098,0.6124],[0.7885,0.6058],[0.7693,0.5953],[0.7525,0.5814],[0.7387,0.5647],[0.7282,0.5455],[0.7216,0.5242],[0.7193,0.5013],[0.7216,0.4785],[0.7282,0.4572],[0.7387,0.438],[0.7525,0.4212],[0.7693,0.4073],[0.7885,0.3969],[0.8098,0.3903],[0.8327,0.388],[0.8555,0.3903],[0.8768,0.3969],[0.896,0.4073],[0.9128,0.4212],[0.9266,0.438],[0.9371,0.4572],[0.9437,0.4785],[0.946,0.5013],[0.9437,0.5242],[0.9371,0.5455],[0.9266,0.5647],[0.9128,0.5814],[0.896,0.5953],[0.8768,0.6058],[0.8555,0.6124]]]},{"ext":[[0.0,3.4463],[0.0348,3.4498],[0.0676,3.4599],[0.0971,3.476],[0.1229,3.4973],[0.1442,3.5231],[0.1603,3.5527],[0.1705,3.5854],[0.174,3.6205],[0.1705,3.6556],[0.1603,3.6883],[0.1442,3.7179],[0.1229,3.7437],[0.0971,3.765],[0.0676,3.7811],[0.0348,3.7912],[0.0,3.7947],[0.0,3.9975],[0.8245,3.9975],[0.8159,3.988],[0.7851,3.9468],[0.7583,3.9029],[0.7359,3.8561],[0.7179,3.807],[0.7047,3.7558],[0.6966,3.7028],[0.6938,3.6461],[0.9975,3.6461],[0.9975,3.5949],[0.6938,3.5949],[0.6985,3.5221],[0.7124,3.4535],[0.7348,3.3877],[0.7655,3.3257],[0.8038,3.2682],[0.8495,3.2159],[0.9021,3.1696],[0.961,3.1302],[0.9975,3.1122],[0.9975,2.2205],[0.8469,2.2205],[0.9975,2.0699],[0.9975,2.0025],[0.8497,2.0025],[0.9335,2.0863],[0.0602,2.9596],[0.0602,2.8497],[0.8236,2.0863],[0.7398,2.0025],[0.6212,2.0025],[0.7216,2.1029],[0.0602,2.7643],[0.0602,2.6697],[0.627,2.1029],[0.5266,2.0025],[0.4206,2.0025],[0.521,2.1029],[0.0602,2.5637],[0.0602,2.4691],[0.4264,2.1029],[0.326,2.0025],[0.2129,2.0025],[0.3133,2.1029],[0.0602,2.356],[0.0602,2.0025],[0.0,2.0025]],"holes":[]},{"ext":[[0.0,4.3305],[0.3438,4.669],[0.0,4.669],[0.0,5.0312],[0.7207,5.0312],[0.0,5.7519],[0.0,6.0],[0.9975,6.0],[0.9975,5.5106],[0.9747,5.5294],[0.9436,5.5423],[0.9101,5.5453],[0.8765,5.5381],[0.8466,5.5212],[0.8235,5.4966],[0.8088,5.4664],[0.8036,5.4324],[0.8088,5.3984],[0.8235,5.3682],[0.8465,5.3436],[0.8765,5.3266],[0.9101,5.3195],[0.9436,5.3225],[0.9747,5.3353],[0.9975,5.3541],[0.9975,4.669],[0.4888,4.669],[0.833,4.3301],[0.9975,4.4921],[0.9975,4.1295],[0.9734,4.118],[0.9294,4.0912],[0.8883,4.0604],[0.8504,4.0259],[0.8291,4.0025],[0.0,4.0025]],"holes":[]},{"ext":[[1.9975,6.0],[1.9975,4.669],[1.3221,4.669],[1.6663,4.3301],[1.9975,4.6562],[1.9975,4.0025],[1.6272,4.0025],[1.6059,4.0259],[1.568,4.0604],[1.5268,4.0912],[1.4829,4.118],[1.4361,4.1404],[1.387,4.1584],[1.3358,4.1716],[1.2828,4.1797],[1.2281,4.1824],[1.1735,4.1797],[1.1205,4.1716],[1.0693,4.1584],[1.0202,4.1404],[1.0025,4.1319],[1.0025,4.497],[1.1772,4.669],[1.0025,4.669],[1.0025,5.359],[1.0134,5.3739],[1.0224,5.3922],[1.0279,5.4118],[1.0298,5.4324],[1.0279,5.4529],[1.0224,5.4726],[1.0134,5.4909],[1.0025,5.5058],[1.0025,6.0]],"holes":[]},{"ext":[[2.9975,6.0],[2.9975,5.9393],[2.9159,5.9393],[2.52,5.5435],[2.4995,5.5455],[2.479,5.5435],[2.0832,5.9393],[2.0025,5.9393],[2.0025,6.0]],"holes":[[[2.4995,5.6342],[2.8046,5.9393],[2.6382,5.9393],[2.4995,5.8006],[2.3608,5.9393],[2.1945,5.9393]]]},{"ext":[[3.9975,6.0],[3.9975,5.5066],[3.986,5.4909],[3.977,5.4726],[3.9715,5.4529],[3.9697,5.4324],[3.9715,5.4118],[3.977,5.3922],[3.986,5.3739],[3.9975,5.3582],[3.9975,4.669],[3.8219,4.669],[3.9975,4.4961],[3.9975,4.1308],[3.9745,4.1422],[3.9081,4.1645],[3.84,4.178],[3.771,4.1824],[3.7019,4.178],[3.6338,4.1645],[3.5674,4.1422],[3.5038,4.1108],[3.4449,4.0714],[3.3924,4.0251],[3.3726,4.0025],[3.0025,4.0025],[3.0025,4.6553],[3.3328,4.3301],[3.677,4.669],[3.0025,4.669],[3.0025,6.0]],"holes":[]},{"ext":[[5.0,6.0],[5.0,5.7525],[4.2787,5.0312],[5.0,5.0312],[5.0,4.669],[4.655,4.669],[5.0,4.3293],[5.0,4.0025],[4.1693,4.0025],[4.1495,4.0251],[4.097,4.0714],[4.0381,4.1108],[4.0025,4.1284],[4.0025,4.4912],[4.1661,4.3301],[4.5103,4.669],[4.0025,4.669],[4.0025,5.3536],[4.0247,5.3353],[4.0558,5.3225],[4.0893,5.3195],[4.1229,5.3266],[4.1529,5.3436],[4.1759,5.3682],[4.1906,5.3984],[4.1959,5.4324],[4.1906,5.4664],[4.1759,5.4966],[4.1528,5.5212],[4.1229,5.5381],[4.0893,5.5453],[4.0558,5.5423],[4.0247,5.5294],[4.0025,5.5111],[4.0025,6.0]],"holes":[]},{"ext":[[5.0,3.7944],[4.9647,3.7909],[4.932,3.7808],[4.9025,3.7647],[4.8768,3.7434],[4.8555,3.7177],[4.8395,3.6882],[4.8294,3.6555],[4.8259,3.6205],[4.8294,3.5855],[4.8395,3.5528],[4.8555,3.5233],[4.8768,3.4976],[4.9025,3.4763],[4.932,3.4602],[4.9647,3.4501],[5.0,3.4466],[5.0,2.0025],[4.9392,2.0025],[4.9392,2.5659],[4.5801,2.2068],[4.7844,2.0025],[4.701,2.0025],[4.4967,2.2068],[4.9392,2.6493],[4.9392,2.7468],[4.3858,2.1934],[4.5767,2.0025],[4.4934,2.0025],[4.3025,2.1934],[4.9392,2.8302],[4.9392,2.9],[4.9092,2.93],[4.1888,2.2096],[4.3959,2.0025],[4.3125,2.0025],[4.1471,2.1679],[4.0655,2.0863],[4.1493,2.0025],[4.0025,2.0025],[4.0025,2.0708],[4.1522,2.2205],[4.0025,2.2205],[4.0025,3.1119],[4.0257,3.123],[4.0697,3.1498],[4.1108,3.1806],[4.1487,3.2151],[4.1832,3.253],[4.214,3.2942],[4.2408,3.3382],[4.2632,3.3849],[4.2812,3.434],[4.2944,3.4852],[4.3025,3.5382],[4.3053,3.5949],[4.0025,3.5949],[4.0025,3.6461],[4.3053,3.6461],[4.3005,3.7189],[4.2867,3.7875],[4.2643,3.8533],[4.2336,3.9153],[4.1953,3.9728],[4.1737,3.9975],[5.0,3.9975]],"holes":[]},{"ext":[[4.3869,1.4495],[4.2773,1.3398],[4.0025,1.3398],[4.0025,1.8339]],"holes":[]},{"ext":[[3.0025,0.9597],[3.0025,1.0708],[3.1299,1.1982],[3.0467,1.2814],[3.0025,1.2372],[3.0025,1.5187],[3.3096,1.8258],[3.1379,1.9975],[3.4194,1.9975],[3.5911,1.8258],[3.0845,1.3192],[3.1677,1.236],[3.9292,1.9975],[3.9975,1.9975],[3.9975,1.9546]],"holes":[]},{"ext":[[2.52,0.4772],[2.4995,0.4794],[2.479,0.4772],[2.0025,0.9537],[2.0025,1.0649],[2.4995,0.5679],[2.9975,1.0658],[2.9975,0.9547]],"holes":[]},{"ext":[[1.0025,1.9537],[1.0025,1.9975],[1.0699,1.9975],[1.8314,1.236],[1.9146,1.3192],[1.408,1.8258],[1.5797,1.9975],[1.8612,1.9975],[1.6895,1.8258],[1.9975,1.5178],[1.9975,1.2363],[1.9524,1.2814],[1.8692,1.1982],[1.9975,1.0699],[1.9975,0.9587]],"holes":[]},{"ext":[[0.7218,1.3398],[0.6122,1.4495],[0.9975,1.8348],[0.9975,1.3398]],"holes":[]},{"ext":[[3.3466,3.9728],[3.3083,3.9153],[3.2776,3.8533],[3.2552,3.7875],[3.2414,3.7189],[3.2366,3.6461],[3.6693,3.6461],[3.6843,3.679],[3.7073,3.7035],[3.737,3.7194],[3.771,3.7251],[3.8049,3.7194],[3.8346,3.7035],[3.8576,3.679],[3.8726,3.6461],[3.9975,3.6461],[3.9975,3.5949],[3.8726,3.5949],[3.8576,3.562],[3.8346,3.5375],[3.8049,3.5216],[3.771,3.5159],[3.737,3.5216],[3.7073,3.5375],[3.6843,3.562],[3.6693,3.5949],[3.2366,3.5949],[3.2394,3.5382],[3.2475,3.4852],[3.2607,3.434],[3.2787,3.3849],[3.3011,3.3382],[3.3279,3.2942],[3.3587,3.253],[3.3932,3.2151],[3.4311,3.1806],[3.4723,3.1498],[3.5162,3.123],[3.563,3.1006],[3.6121,3.0826],[3.6633,3.0694],[3.7163,3.0613],[3.771,3.0586],[3.8256,3.0613],[3.8786,3.0694],[3.9298,3.0826],[3.9789,3.1006],[3.9975,3.1095],[3.9975,2.2205],[3.3667,2.2205],[3.7594,2.6133],[3.0025,2.6133],[3.0025,2.6851],[3.0457,2.6851],[3.3667,3.0061],[3.0025,3.0061],[3.0025,3.9975],[3.3682,3.9975]],"holes":[]},{"ext":[[3.9975,2.0658],[3.9975,2.0025],[3.9342,2.0025]],"holes":[]},{"ext":[[2.8036,2.6133],[2.9975,2.4194],[2.9975,2.1379],[2.4995,2.6359],[2.0025,2.1388],[2.0025,2.4203],[2.1955,2.6133],[2.0025,2.6133],[2.0025,2.6851],[2.2673,2.6851],[2.4995,2.9173],[2.7318,2.6851],[2.9975,2.6851],[2.9975,2.6133]],"holes":[]},{"ext":[[3.4144,2.0025],[3.1329,2.0025],[3.0025,2.1329],[3.0025,2.4144]],"holes":[]},{"ext":[[2.9975,4.6602],[2.9975,4.0025],[2.0025,4.0025],[2.0025,4.6611],[2.0105,4.669],[2.0025,4.669],[2.0025,5.8989],[2.406,5.4954],[2.3896,5.4592],[2.3873,5.4191],[2.399,5.3806],[2.4245,5.3479],[2.46,5.3265],[2.4995,5.3194],[2.5391,5.3265],[2.5746,5.3479],[2.6001,5.3806],[2.6118,5.4191],[2.6094,5.4592],[2.5931,5.4954],[2.9975,5.8998],[2.9975,4.669],[2.9886,4.669]],"holes":[[[2.4995,4.3301],[2.8437,4.669],[2.1554,4.669]]]},{"ext":[[2.5844,3.0061],[2.8971,3.3187],[2.102,3.3187],[2.4147,3.0061],[2.0025,3.0061],[2.0025,3.9975],[2.9975,3.9975],[2.9975,3.0061]],"holes":[[[2.4318,3.4602],[2.4645,3.4501],[2.4995,3.4466],[2.5346,3.4501],[2.5672,3.4602],[2.5967,3.4763],[2.6225,3.4976],[2.6438,3.5233],[2.6598,3.5528],[2.6699,3.5855],[2.6734,3.6205],[2.6699,3.6555],[2.6598,3.6882],[2.6438,3.7177],[2.6225,3.7434],[2.5967,3.7647],[2.5672,3.7808],[2.5346,3.7909],[2.4995,3.7944],[2.4645,3.7909],[2.4318,3.7808],[2.4024,3.7647],[2.3766,3.7434],[2.3553,3.7177],[2.3393,3.6882],[2.3292,3.6555],[2.3257,3.6205],[2.3292,3.5855],[2.3393,3.5528],[2.3553,3.5233],[2.3766,3.4976],[2.4024,3.4763]]]},{"ext":[[1.6324,3.0061],[1.9534,2.6851],[1.9975,2.6851],[1.9975,2.6133],[1.2397,2.6133],[1.6324,2.2205],[1.0025,2.2205],[1.0025,3.1097],[1.0246,3.0988],[1.091,3.0765],[1.1591,3.0631],[1.2281,3.0586],[1.2972,3.0631],[1.3653,3.0765],[1.4317,3.0988],[1.4953,3.1302],[1.5542,3.1696],[1.6067,3.2159],[1.6525,3.2682],[1.6908,3.3257],[1.7215,3.3877],[1.7439,3.4535],[1.7577,3.5221],[1.7625,3.5949],[1.3298,3.5949],[1.3148,3.562],[1.2918,3.5375],[1.2621,3.5216],[1.2281,3.5159],[1.1942,3.5216],[1.1645,3.5375],[1.1415,3.562],[1.1265,3.5949],[1.0025,3.5949],[1.0025,3.6461],[1.1265,3.6461],[1.1415,3.679],[1.1645,3.7035],[1.1942,3.7194],[1.2281,3.7251],[1.2621,3.7194],[1.2918,3.7035],[1.3148,3.679],[1.3298,3.6461],[1.7625,3.6461],[1.7597,3.7028],[1.7516,3.7558],[1.7384,3.807],[1.7204,3.8561],[1.698,3.9029],[1.6712,3.9468],[1.6404,3.988],[1.6318,3.9975],[1.9975,3.9975],[1.9975,3.0061]],"holes":[]},{"ext":[[2.9975,1.5137],[2.9975,1.2322],[2.4995,0.7343],[2.0025,1.2313],[2.0025,1.5128],[2.4995,1.0157]],"holes":[]},{"ext":[[1.8662,2.0025],[1.5847,2.0025],[1.9975,2.4153],[1.9975,2.1338]],"holes":[]},{"ext":[[1.0649,2.0025],[1.0025,2.0025],[1.0025,2.0649]],"holes":[]}],"PT2A":[{"ext":[[4.0025,0.0],[4.0025,0.9433],[4.5086,1.4495],[4.0025,1.9556],[4.0025,1.9975],[4.155,1.9975],[4.9394,1.213],[4.9394,1.3229],[4.2649,1.9975],[4.3835,1.9975],[4.9394,1.4416],[4.9394,1.5362],[4.4781,1.9975],[4.584,1.9975],[4.9394,1.6421],[4.9394,1.7367],[4.6786,1.9975],[4.7917,1.9975],[4.9394,1.8498],[4.9394,1.9975],[5.0,1.9975],[5.0,0.7169],[4.3832,0.1001],[5.0,0.1001],[5.0,0.0]],"holes":[[[4.073,0.5647],[4.0626,0.5455],[4.056,0.5242],[4.0537,0.5013],[4.056,0.4785],[4.0626,0.4572],[4.073,0.438],[4.0869,0.4212],[4.1037,0.4073],[4.1229,0.3969],[4.1442,0.3903],[4.167,0.388],[4.1898,0.3903],[4.2111,0.3969],[4.2303,0.4073],[4.2471,0.4212],[4.261,0.438],[4.2715,0.4572],[4.2781,0.4785],[4.2803,0.5013],[4.2781,0.5242],[4.2715,0.5455],[4.261,0.5647],[4.2471,0.5814],[4.2303,0.5953],[4.2111,0.6058],[4.1898,0.6124],[4.167,0.6146],[4.1442,0.6124],[4.1229,0.6058],[4.1037,0.5953],[4.0869,0.5814]]]},{"ext":[[3.0025,0.0],[3.0025,0.8379],[3.9975,1.8329],[3.9975,1.3398],[3.6025,1.3398],[3.9975,0.9449],[3.9975,0.0]],"holes":[]},{"ext":[[2.0025,0.0],[2.0025,0.8332],[2.4066,0.4291],[2.3902,0.3928],[2.3879,0.3527],[2.3996,0.3143],[2.425,0.2815],[2.4606,0.2601],[2.5001,0.253],[2.5397,0.2601],[2.5752,0.2815],[2.6006,0.3143],[2.6124,0.3527],[2.61,0.3928],[2.5937,0.4291],[2.9975,0.8329],[2.9975,0.0]],"holes":[]},{"ext":[[1.0025,0.0],[1.0025,0.9446],[1.3977,1.3398],[1.0025,1.3398],[1.0025,1.8332],[1.9975,0.8382],[1.9975,0.0]],"holes":[]},{"ext":[[0.0,0.0],[0.0,0.1001],[0.7213,0.1001],[0.0,0.8214],[0.0,1.9975],[0.0604,1.9975],[0.0604,1.8477],[0.2102,1.9975],[0.2936,1.9975],[0.0604,1.7643],[0.0604,1.64],[0.4179,1.9975],[0.5013,1.9975],[0.0604,1.5566],[0.0604,1.4591],[0.5988,1.9975],[0.6822,1.9975],[0.0255,1.3408],[0.1071,1.2592],[0.8454,1.9975],[0.9975,1.9975],[0.9975,1.9553],[0.4916,1.4495],[0.9975,0.9436],[0.9975,0.0]],"holes":[[[0.7396,0.5647],[0.7291,0.5455],[0.7225,0.5242],[0.7203,0.5013],[0.7225,0.4785],[0.7291,0.4572],[0.7396,0.438],[0.7535,0.4212],[0.7702,0.4073],[0.7894,0.3969],[0.8107,0.3903],[0.8336,0.388],[0.8564,0.3903],[0.8777,0.3969],[0.8969,0.4073],[0.9137,0.4212],[0.9276,0.438],[0.938,0.4572],[0.9446,0.4785],[0.9469,0.5013],[0.9446,0.5242],[0.938,0.5455],[0.9276,0.5647],[0.9137,0.5814],[0.8969,0.5953],[0.8777,0.6058],[0.8564,0.6124],[0.8336,0.6146],[0.8107,0.6124],[0.7894,0.6058],[0.7702,0.5953],[0.7535,0.5814]]]},{"ext":[[0.0,3.4466],[0.035,3.4501],[0.0676,3.4602],[0.0971,3.4763],[0.1229,3.4976],[0.1441,3.5233],[0.1602,3.5528],[0.1703,3.5855],[0.1738,3.6205],[0.1703,3.6555],[0.1602,3.6882],[0.1441,3.7177],[0.1229,3.7434],[0.0971,3.7647],[0.0676,3.7808],[0.035,3.7909],[0.0,3.7944],[0.0,3.9975],[0.826,3.9975],[0.8044,3.9728],[0.766,3.9153],[0.7353,3.8533],[0.713,3.7875],[0.6991,3.7189],[0.6943,3.6461],[0.9975,3.6461],[0.9975,3.5949],[0.6943,3.5949],[0.6972,3.5382],[0.7053,3.4852],[0.7185,3.434],[0.7365,3.3849],[0.7589,3.3382],[0.7856,3.2942],[0.8165,3.253],[0.8509,3.2151],[0.8888,3.1806],[0.93,3.1498],[0.974,3.123],[0.9975,3.1117],[0.9975,2.2205],[0.8475,2.2205],[0.9975,2.0705],[0.9975,2.0025],[0.8504,2.0025],[0.9342,2.0863],[0.8526,2.1679],[0.6872,2.0025],[0.6038,2.0025],[0.8109,2.2096],[0.0904,2.93],[0.0604,2.9],[0.0604,2.8302],[0.6972,2.1934],[0.5063,2.0025],[0.4229,2.0025],[0.6138,2.1934],[0.0604,2.7468],[0.0604,2.6493],[0.5029,2.2068],[0.2986,2.0025],[0.2152,2.0025],[0.4195,2.2068],[0.0604,2.5659],[0.0604,2.0025],[0.0,2.0025]],"holes":[]},{"ext":[[0.0,4.3296],[0.3446,4.669],[0.0,4.669],[0.0,6.0],[0.9975,5.0025],[0.9975,4.669],[0.4894,4.669],[0.8336,4.3301],[0.9975,4.4915],[0.9975,4.1285],[0.9616,4.1108],[0.9027,4.0714],[0.8501,4.0251],[0.8304,4.0025],[0.0,4.0025]],"holes":[]},{"ext":[[1.9975,5.9975],[1.9975,4.669],[1.3227,4.669],[1.6668,4.3301],[1.9975,4.6557],[1.9975,4.0025],[1.627,4.0025],[1.6073,4.0251],[1.5548,4.0714],[1.4958,4.1108],[1.4322,4.1422],[1.3659,4.1645],[1.2978,4.178],[1.2287,4.1824],[1.1596,4.178],[1.0916,4.1645],[1.0252,4.1422],[1.0025,4.131],[1.0025,4.4964],[1.1778,4.669],[1.0025,4.669],[1.0025,5.0025]],"holes":[]},{"ext":[[2.9975,5.0025],[2.9975,4.669],[2.9892,4.669],[2.9975,4.6608],[2.9975,4.0025],[2.0025,4.0025],[2.0025,4.6606],[2.011,4.669],[2.0025,4.669],[2.0025,5.9975]],"holes":[[[2.5001,4.3301],[2.8443,4.669],[2.1559,4.669]]]},{"ext":[[3.9975,5.9975],[3.9975,4.669],[3.8225,4.669],[3.9975,4.4967],[3.9975,4.1318],[3.9795,4.1404],[3.9304,4.1584],[3.8792,4.1716],[3.8261,4.1797],[3.7715,4.1824],[3.7169,4.1797],[3.6639,4.1716],[3.6126,4.1584],[3.5635,4.1404],[3.5168,4.118],[3.4728,4.0912],[3.4316,4.0604],[3.3938,4.0259],[3.3725,4.0025],[3.0025,4.0025],[3.0025,4.6559],[3.3334,4.3301],[3.6776,4.669],[3.0025,4.669],[3.0025,5.0025]],"holes":[]},{"ext":[[5.0,5.0],[5.0,4.669],[4.6559,4.669],[5.0,4.3301],[5.0,4.0025],[4.1705,4.0025],[4.1493,4.0259],[4.1114,4.0604],[4.0702,4.0912],[4.0262,4.118],[4.0025,4.1294],[4.0025,4.4918],[4.1667,4.3301],[4.5108,4.669],[4.0025,4.669],[4.0025,5.9975]],"holes":[]},{"ext":[[5.0,3.7947],[4.9648,3.7912],[4.9321,3.7811],[4.9025,3.765],[4.8767,3.7437],[4.8554,3.7179],[4.8393,3.6883],[4.8292,3.6556],[4.8257,3.6205],[4.8292,3.5854],[4.8393,3.5527],[4.8554,3.5231],[4.8767,3.4973],[4.9025,3.476],[4.9321,3.4599],[4.9648,3.4498],[5.0,3.4463],[5.0,2.0025],[4.9394,2.0025],[4.9394,2.356],[4.6863,2.1029],[4.7867,2.0025],[4.6736,2.0025],[4.5732,2.1029],[4.9394,2.4691],[4.9394,2.5637],[4.4786,2.1029],[4.579,2.0025],[4.4731,2.0025],[4.3727,2.1029],[4.9394,2.6697],[4.9394,2.7643],[4.2781,2.1029],[4.3785,2.0025],[4.2599,2.0025],[4.1761,2.0863],[4.9394,2.8497],[4.9394,2.9596],[4.0662,2.0863],[4.15,2.0025],[4.0025,2.0025],[4.0025,2.0702],[4.1528,2.2205],[4.0025,2.2205],[4.0025,3.1123],[4.0387,3.1302],[4.0976,3.1696],[4.1501,3.2159],[4.1958,3.2682],[4.2342,3.3257],[4.2649,3.3877],[4.2873,3.4535],[4.3011,3.5221],[4.3059,3.5949],[4.0025,3.5949],[4.0025,3.6461],[4.3059,3.6461],[4.303,3.7028],[4.295,3.7558],[4.2818,3.807],[4.2638,3.8561],[4.2414,3.9029],[4.2146,3.9468],[4.1837,3.988],[4.1751,3.9975],[5.0,3.9975]],"holes":[]},{"ext":[[4.3875,1.4495],[4.2779,1.3398],[4.0025,1.3398],[4.0025,1.8345]],"holes":[]},{"ext":[[3.0025,0.9591],[3.0025,1.0702],[3.1305,1.1982],[3.0473,1.2814],[3.0025,1.2366],[3.0025,1.5181],[3.3102,1.8258],[3.1385,1.9975],[3.4199,1.9975],[3.5916,1.8258],[3.085,1.3192],[3.1682,1.236],[3.9298,1.9975],[3.9975,1.9975],[3.9975,1.954]],"holes":[]},{"ext":[[2.5206,0.4772],[2.5001,0.4794],[2.4796,0.4772],[2.0025,0.9543],[2.0025,1.0655],[2.5001,0.5679],[2.9975,1.0652],[2.9975,0.9541]],"holes":[]},{"ext":[[1.0025,1.9543],[1.0025,1.9975],[1.0705,1.9975],[1.832,1.236],[1.9152,1.3192],[1.4086,1.8258],[1.5803,1.9975],[1.8618,1.9975],[1.6901,1.8258],[1.9975,1.5184],[1.9975,1.2369],[1.953,1.2814],[1.8698,1.1982],[1.9975,1.0705],[1.9975,0.9593]],"holes":[]},{"ext":[[0.7223,1.3398],[0.6127,1.4495],[0.9975,1.8342],[0.9975,1.3398]],"holes":[]},{"ext":[[3.9087,3.0765],[3.9751,3.0988],[3.9975,3.1099],[3.9975,2.2205],[3.3672,2.2205],[3.76,2.6133],[3.0025,2.6133],[3.0025,2.6851],[3.0463,2.6851],[3.3672,3.0061],[3.0025,3.0061],[3.0025,3.9975],[3.3679,3.9975],[3.3593,3.988],[3.3285,3.9468],[3.3017,3.9029],[3.2793,3.8561],[3.2613,3.807],[3.2481,3.7558],[3.24,3.7028],[3.2372,3.6461],[3.6699,3.6461],[3.6848,3.679],[3.7079,3.7035],[3.7375,3.7194],[3.7715,3.7251],[3.8055,3.7194],[3.8352,3.7035],[3.8582,3.679],[3.8732,3.6461],[3.9975,3.6461],[3.9975,3.5949],[3.8732,3.5949],[3.8582,3.562],[3.8352,3.5375],[3.8055,3.5216],[3.7715,3.5159],[3.7375,3.5216],[3.7079,3.5375],[3.6848,3.562],[3.6699,3.5949],[3.2372,3.5949],[3.2419,3.5221],[3.2558,3.4535],[3.2781,3.3877],[3.3089,3.3257],[3.3472,3.2682],[3.3929,3.2159],[3.4455,3.1696],[3.5044,3.1302],[3.568,3.0988],[3.6344,3.0765],[3.7025,3.0631],[3.7715,3.0586],[3.8406,3.0631]],"holes":[]},{"ext":[[2.8041,2.6133],[2.9975,2.4199],[2.9975,2.1385],[2.5001,2.6359],[2.0025,2.1382],[2.0025,2.4197],[2.1961,2.6133],[2.0025,2.6133],[2.0025,2.6851],[2.2679,2.6851],[2.5001,2.9173],[2.7323,2.6851],[2.9975,2.6851],[2.9975,2.6133]],"holes":[]},{"ext":[[3.4149,2.0025],[3.1335,2.0025],[3.0025,2.1335],[3.0025,2.4149]],"holes":[]},{"ext":[[3.9975,2.0652],[3.9975,2.0025],[3.9348,2.0025]],"holes":[]},{"ext":[[1.9975,2.6851],[1.9975,2.6133],[1.2402,2.6133],[1.633,2.2205],[1.0025,2.2205],[1.0025,3.1093],[1.0207,3.1006],[1.0698,3.0826],[1.121,3.0694],[1.1741,3.0613],[1.2287,3.0586],[1.2833,3.0613],[1.3364,3.0694],[1.3876,3.0826],[1.4367,3.1006],[1.4834,3.123],[1.5274,3.1498],[1.5686,3.1806],[1.6065,3.2151],[1.6409,3.253],[1.6718,3.2942],[1.6985,3.3382],[1.721,3.3849],[1.7389,3.434],[1.7522,3.4852],[1.7602,3.5382],[1.7631,3.5949],[1.3304,3.5949],[1.3154,3.562],[1.2924,3.5375],[1.2627,3.5216],[1.2287,3.5159],[1.1947,3.5216],[1.165,3.5375],[1.142,3.562],[1.1271,3.5949],[1.0025,3.5949],[1.0025,3.6461],[1.1271,3.6461],[1.142,3.679],[1.165,3.7035],[1.1947,3.7194],[1.2287,3.7251],[1.2627,3.7194],[1.2924,3.7035],[1.3154,3.679],[1.3304,3.6461],[1.7631,3.6461],[1.7583,3.7189],[1.7445,3.7875],[1.7221,3.8533],[1.6914,3.9153],[1.653,3.9728],[1.6314,3.9975],[1.9975,3.9975],[1.9975,3.0061],[1.633,3.0061],[1.954,2.6851]],"holes":[]},{"ext":[[2.585,3.0061],[2.8977,3.3187],[2.1026,3.3187],[2.4152,3.0061],[2.0025,3.0061],[2.0025,3.9975],[2.9975,3.9975],[2.9975,3.0061]],"holes":[[[2.6604,3.5528],[2.6705,3.5855],[2.674,3.6205],[2.6705,3.6555],[2.6604,3.6882],[2.6443,3.7177],[2.623,3.7434],[2.5973,3.7647],[2.5678,3.7808],[2.5352,3.7909],[2.5001,3.7944],[2.4651,3.7909],[2.4324,3.7808],[2.4029,3.7647],[2.3772,3.7434],[2.3559,3.7177],[2.3399,3.6882],[2.3297,3.6555],[2.3263,3.6205],[2.3297,3.5855],[2.3399,3.5528],[2.3559,3.5233],[2.3772,3.4976],[2.4029,3.4763],[2.4324,3.4602],[2.4651,3.4501],[2.5001,3.4466],[2.5352,3.4501],[2.5678,3.4602],[2.5973,3.4763],[2.623,3.4976],[2.6443,3.5233]]]},{"ext":[[1.8668,2.0025],[1.5853,2.0025],[1.9975,2.4147],[1.9975,2.1332]],"holes":[]},{"ext":[[2.5001,1.0157],[2.9975,1.5131],[2.9975,1.2316],[2.5001,0.7343],[2.0025,1.2319],[2.0025,1.5134]],"holes":[]},{"ext":[[1.0655,2.0025],[1.0025,2.0025],[1.0025,2.0655]],"holes":[]}],"PT2B":[{"ext":[[4.0025,0.0],[4.0025,0.9436],[4.5084,1.4495],[4.0025,1.9553],[4.0025,1.9975],[4.1546,1.9975],[4.8929,1.2592],[4.9745,1.3408],[4.3178,1.9975],[4.4012,1.9975],[4.9396,1.4591],[4.9396,1.5566],[4.4987,1.9975],[4.5821,1.9975],[4.9396,1.64],[4.9396,1.7643],[4.7064,1.9975],[4.7898,1.9975],[4.9396,1.8477],[4.9396,1.9975],[5.0,1.9975],[5.0,0.8214],[4.2787,0.1001],[5.0,0.1001],[5.0,0.0]],"holes":[[[4.1893,0.6124],[4.1664,0.6146],[4.1436,0.6124],[4.1223,0.6058],[4.1031,0.5953],[4.0863,0.5814],[4.0724,0.5647],[4.062,0.5455],[4.0554,0.5242],[4.0531,0.5013],[4.0554,0.4785],[4.062,0.4572],[4.0724,0.438],[4.0863,0.4212],[4.1031,0.4073],[4.1223,0.3969],[4.1436,0.3903],[4.1664,0.388],[4.1893,0.3903],[4.2106,0.3969],[4.2298,0.4073],[4.2465,0.4212],[4.2604,0.438],[4.2709,0.4572],[4.2775,0.4785],[4.2797,0.5013],[4.2775,0.5242],[4.2709,0.5455],[4.2604,0.5647],[4.2465,0.5814],[4.2298,0.5953],[4.2106,0.6058]]]},{"ext":[[3.0025,0.0],[3.0025,0.8382],[3.9975,1.8332],[3.9975,1.3398],[3.6023,1.3398],[3.9975,0.9446],[3.9975,0.0]],"holes":[]},{"ext":[[2.0025,0.0],[2.0025,0.8329],[2.4063,0.4291],[2.39,0.3928],[2.3876,0.3527],[2.3994,0.3143],[2.4248,0.2815],[2.4603,0.2601],[2.4999,0.253],[2.5394,0.2601],[2.575,0.2815],[2.6004,0.3143],[2.6121,0.3527],[2.6098,0.3928],[2.5934,0.4291],[2.9975,0.8332],[2.9975,0.0]],"holes":[]},{"ext":[[1.0025,0.0],[1.0025,0.9449],[1.3975,1.3398],[1.0025,1.3398],[1.0025,1.8329],[1.9975,0.8379],[1.9975,0.0]],"holes":[]},{"ext":[[0.0,0.0],[0.0,0.1001],[0.6168,0.1001],[0.0,0.7169],[0.0,1.9975],[0.0606,1.9975],[0.0606,1.8498],[0.2083,1.9975],[0.3214,1.9975],[0.0606,1.7367],[0.0606,1.6421],[0.416,1.9975],[0.5219,1.9975],[0.0606,1.5362],[0.0606,1.4416],[0.6165,1.9975],[0.7351,1.9975],[0.0606,1.3229],[0.0606,1.213],[0.845,1.9975],[0.9975,1.9975],[0.9975,1.9556],[0.4914,1.4495],[0.9975,0.9433],[0.9975,0.0]],"holes":[[[0.8558,0.6124],[0.833,0.6146],[0.8102,0.6124],[0.7889,0.6058],[0.7697,0.5953],[0.7529,0.5814],[0.739,0.5647],[0.7285,0.5455],[0.7219,0.5242],[0.7197,0.5013],[0.7219,0.4785],[0.7285,0.4572],[0.739,0.438],[0.7529,0.4212],[0.7697,0.4073],[0.7889,0.3969],[0.8102,0.3903],[0.833,0.388],[0.8558,0.3903],[0.8771,0.3969],[0.8963,0.4073],[0.9131,0.4212],[0.927,0.438],[0.9374,0.4572],[0.944,0.4785],[0.9463,0.5013],[0.944,0.5242],[0.9374,0.5455],[0.927,0.5647],[0.9131,0.5814],[0.8963,0.5953],[0.8771,0.6058]]]},{"ext":[[0.0,3.4463],[0.0352,3.4498],[0.0679,3.4599],[0.0975,3.476],[0.1233,3.4973],[0.1446,3.5231],[0.1607,3.5527],[0.1708,3.5854],[0.1743,3.6205],[0.1708,3.6556],[0.1607,3.6883],[0.1446,3.7179],[0.1233,3.7437],[0.0975,3.765],[0.0679,3.7811],[0.0352,3.7912],[0.0,3.7947],[0.0,3.9975],[0.8249,3.9975],[0.8163,3.988],[0.7854,3.9468],[0.7586,3.9029],[0.7362,3.8561],[0.7182,3.807],[0.705,3.7558],[0.697,3.7028],[0.6941,3.6461],[0.9975,3.6461],[0.9975,3.5949],[0.6941,3.5949],[0.6989,3.5221],[0.7127,3.4535],[0.7351,3.3877],[0.7658,3.3257],[0.8042,3.2682],[0.8499,3.2159],[0.9024,3.1696],[0.9613,3.1302],[0.9975,3.1123],[0.9975,2.2205],[0.8472,2.2205],[0.9975,2.0702],[0.9975,2.0025],[0.85,2.0025],[0.9338,2.0863],[0.0606,2.9596],[0.0606,2.8497],[0.8239,2.0863],[0.7401,2.0025],[0.6215,2.0025],[0.7219,2.1029],[0.0606,2.7643],[0.0606,2.6697],[0.6273,2.1029],[0.5269,2.0025],[0.421,2.0025],[0.5214,2.1029],[0.0606,2.5637],[0.0606,2.4691],[0.4268,2.1029],[0.3264,2.0025],[0.2133,2.0025],[0.3137,2.1029],[0.0606,2.356],[0.0606,2.0025],[0.0,2.0025]],"holes":[]},{"ext":[[0.0,4.3301],[0.3441,4.669],[0.0,4.669],[0.0,5.0],[0.9975,5.9975],[0.9975,4.669],[0.4892,4.669],[0.8333,4.3301],[0.9975,4.4918],[0.9975,4.1294],[0.9738,4.118],[0.9298,4.0912],[0.8886,4.0604],[0.8507,4.0259],[0.8295,4.0025],[0.0,4.0025]],"holes":[]},{"ext":[[1.9975,5.0025],[1.9975,4.669],[1.3224,4.669],[1.6666,4.3301],[1.9975,4.6559],[1.9975,4.0025],[1.6275,4.0025],[1.6062,4.0259],[1.5684,4.0604],[1.5272,4.0912],[1.4832,4.118],[1.4365,4.1404],[1.3874,4.1584],[1.3361,4.1716],[1.2831,4.1797],[1.2285,4.1824],[1.1739,4.1797],[1.1208,4.1716],[1.0696,4.1584],[1.0205,4.1404],[1.0025,4.1318],[1.0025,4.4967],[1.1775,4.669],[1.0025,4.669],[1.0025,5.9975]],"holes":[]},{"ext":[[2.9975,5.9975],[2.9975,4.669],[2.989,4.669],[2.9975,4.6606],[2.9975,4.0025],[2.0025,4.0025],[2.0025,4.6608],[2.0108,4.669],[2.0025,4.669],[2.0025,5.0025]],"holes":[[[2.8441,4.669],[2.1557,4.669],[2.4999,4.3301]]]},{"ext":[[3.9975,5.0025],[3.9975,4.669],[3.8222,4.669],[3.9975,4.4964],[3.9975,4.131],[3.9748,4.1422],[3.9084,4.1645],[3.8404,4.178],[3.7713,4.1824],[3.7022,4.178],[3.6341,4.1645],[3.5678,4.1422],[3.5042,4.1108],[3.4452,4.0714],[3.3927,4.0251],[3.373,4.0025],[3.0025,4.0025],[3.0025,4.6557],[3.3332,4.3301],[3.6773,4.669],[3.0025,4.669],[3.0025,5.9975]],"holes":[]},{"ext":[[5.0,6.0],[5.0,4.669],[4.6554,4.669],[5.0,4.3296],[5.0,4.0025],[4.1696,4.0025],[4.1499,4.0251],[4.0973,4.0714],[4.0384,4.1108],[4.0025,4.1285],[4.0025,4.4915],[4.1664,4.3301],[4.5106,4.669],[4.0025,4.669],[4.0025,5.0025]],"holes":[]},{"ext":[[5.0,3.7944],[4.965,3.7909],[4.9324,3.7808],[4.9029,3.7647],[4.8771,3.7434],[4.8559,3.7177],[4.8398,3.6882],[4.8297,3.6555],[4.8262,3.6205],[4.8297,3.5855],[4.8398,3.5528],[4.8559,3.5233],[4.8771,3.4976],[4.9029,3.4763],[4.9324,3.4602],[4.965,3.4501],[5.0,3.4466],[5.0,2.0025],[4.9396,2.0025],[4.9396,2.5659],[4.5805,2.2068],[4.7848,2.0025],[4.7014,2.0025],[4.4971,2.2068],[4.9396,2.6493],[4.9396,2.7468],[4.3862,2.1934],[4.5771,2.0025],[4.4937,2.0025],[4.3028,2.1934],[4.9396,2.8302],[4.9396,2.9],[4.9096,2.93],[4.1891,2.2096],[4.3962,2.0025],[4.3128,2.0025],[4.1474,2.1679],[4.0658,2.0863],[4.1496,2.0025],[4.0025,2.0025],[4.0025,2.0705],[4.1525,2.2205],[4.0025,2.2205],[4.0025,3.1117],[4.026,3.123],[4.07,3.1498],[4.1112,3.1806],[4.1491,3.2151],[4.1835,3.253],[4.2144,3.2942],[4.2411,3.3382],[4.2635,3.3849],[4.2815,3.434],[4.2947,3.4852],[4.3028,3.5382],[4.3057,3.5949],[4.0025,3.5949],[4.0025,3.6461],[4.3057,3.6461],[4.3009,3.7189],[4.287,3.7875],[4.2647,3.8533],[4.234,3.9153],[4.1956,3.9728],[4.174,3.9975],[5.0,3.9975]],"holes":[]},{"ext":[[4.3873,1.4495],[4.2777,1.3398],[4.0025,1.3398],[4.0025,1.8342]],"holes":[]},{"ext":[[3.0025,0.9593],[3.0025,1.0705],[3.1302,1.1982],[3.047,1.2814],[3.0025,1.2369],[3.0025,1.5184],[3.3099,1.8258],[3.1382,1.9975],[3.4197,1.9975],[3.5914,1.8258],[3.0848,1.3192],[3.168,1.236],[3.9295,1.9975],[3.9975,1.9975],[3.9975,1.9543]],"holes":[]},{"ext":[[2.5204,0.4772],[2.4999,0.4794],[2.4794,0.4772],[2.0025,0.9541],[2.0025,1.0652],[2.4999,0.5679],[2.9975,1.0655],[2.9975,0.9543]],"holes":[]},{"ext":[[1.0025,1.954],[1.0025,1.9975],[1.0702,1.9975],[1.8318,1.236],[1.915,1.3192],[1.4084,1.8258],[1.5801,1.9975],[1.8615,1.9975],[1.6898,1.8258],[1.9975,1.5181],[1.9975,1.2366],[1.9527,1.2814],[1.8695,1.1982],[1.9975,1.0702],[1.9975,0.9591]],"holes":[]},{"ext":[[0.7221,1.3398],[0.6125,1.4495],[0.9975,1.8345],[0.9975,1.3398]],"holes":[]},{"ext":[[3.347,3.9728],[3.3086,3.9153],[3.2779,3.8533],[3.2555,3.7875],[3.2417,3.7189],[3.2369,3.6461],[3.6696,3.6461],[3.6846,3.679],[3.7076,3.7035],[3.7373,3.7194],[3.7713,3.7251],[3.8053,3.7194],[3.835,3.7035],[3.858,3.679],[3.8729,3.6461],[3.9975,3.6461],[3.9975,3.5949],[3.8729,3.5949],[3.858,3.562],[3.835,3.5375],[3.8053,3.5216],[3.7713,3.5159],[3.7373,3.5216],[3.7076,3.5375],[3.6846,3.562],[3.6696,3.5949],[3.2369,3.5949],[3.2398,3.5382],[3.2478,3.4852],[3.2611,3.434],[3.279,3.3849],[3.3015,3.3382],[3.3282,3.2942],[3.3591,3.253],[3.3935,3.2151],[3.4314,3.1806],[3.4726,3.1498],[3.5166,3.123],[3.5633,3.1006],[3.6124,3.0826],[3.6636,3.0694],[3.7167,3.0613],[3.7713,3.0586],[3.8259,3.0613],[3.879,3.0694],[3.9302,3.0826],[3.9793,3.1006],[3.9975,3.1093],[3.9975,2.2205],[3.367,2.2205],[3.7598,2.6133],[3.0025,2.6133],[3.0025,2.6851],[3.046,2.6851],[3.367,3.0061],[3.0025,3.0061],[3.0025,3.9975],[3.3686,3.9975]],"holes":[]},{"ext":[[3.9975,2.0655],[3.9975,2.0025],[3.9345,2.0025]],"holes":[]},{"ext":[[2.8039,2.6133],[2.9975,2.4197],[2.9975,2.1382],[2.4999,2.6359],[2.0025,2.1385],[2.0025,2.4199],[2.1959,2.6133],[2.0025,2.6133],[2.0025,2.6851],[2.2677,2.6851],[2.4999,2.9173],[2.7321,2.6851],[2.9975,2.6851],[2.9975,2.6133]],"holes":[]},{"ext":[[3.4147,2.0025],[3.1332,2.0025],[3.0025,2.1332],[3.0025,2.4147]],"holes":[]},{"ext":[[2.8974,3.3187],[2.1023,3.3187],[2.415,3.0061],[2.0025,3.0061],[2.0025,3.9975],[2.9975,3.9975],[2.9975,3.0061],[2.5848,3.0061]],"holes":[[[2.4322,3.4602],[2.4648,3.4501],[2.4999,3.4466],[2.5349,3.4501],[2.5676,3.4602],[2.5971,3.4763],[2.6228,3.4976],[2.6441,3.5233],[2.6601,3.5528],[2.6703,3.5855],[2.6737,3.6205],[2.6703,3.6555],[2.6601,3.6882],[2.6441,3.7177],[2.6228,3.7434],[2.5971,3.7647],[2.5676,3.7808],[2.5349,3.7909],[2.4999,3.7944],[2.4648,3.7909],[2.4322,3.7808],[2.4027,3.7647],[2.377,3.7434],[2.3557,3.7177],[2.3396,3.6882],[2.3295,3.6555],[2.326,3.6205],[2.3295,3.5855],[2.3396,3.5528],[2.3557,3.5233],[2.377,3.4976],[2.4027,3.4763]]]},{"ext":[[1.6328,3.0061],[1.9537,2.6851],[1.9975,2.6851],[1.9975,2.6133],[1.24,2.6133],[1.6328,2.2205],[1.0025,2.2205],[1.0025,3.1099],[1.0249,3.0988],[1.0913,3.0765],[1.1594,3.0631],[1.2285,3.0586],[1.2975,3.0631],[1.3656,3.0765],[1.432,3.0988],[1.4956,3.1302],[1.5545,3.1696],[1.6071,3.2159],[1.6528,3.2682],[1.6911,3.3257],[1.7219,3.3877],[1.7442,3.4535],[1.7581,3.5221],[1.7628,3.5949],[1.3301,3.5949],[1.3152,3.562],[1.2921,3.5375],[1.2625,3.5216],[1.2285,3.5159],[1.1945,3.5216],[1.1648,3.5375],[1.1418,3.562],[1.1268,3.5949],[1.0025,3.5949],[1.0025,3.6461],[1.1268,3.6461],[1.1418,3.679],[1.1648,3.7035],[1.1945,3.7194],[1.2285,3.7251],[1.2625,3.7194],[1.2921,3.7035],[1.3152,3.679],[1.3301,3.6461],[1.7628,3.6461],[1.76,3.7028],[1.7519,3.7558],[1.7387,3.807],[1.7207,3.8561],[1.6983,3.9029],[1.6715,3.9468],[1.6407,3.988],[1.6321,3.9975],[1.9975,3.9975],[1.9975,3.0061]],"holes":[]},{"ext":[[2.9975,1.5134],[2.9975,1.2319],[2.4999,0.7343],[2.0025,1.2316],[2.0025,1.5131],[2.4999,1.0157]],"holes":[]},{"ext":[[1.8665,2.0025],[1.5851,2.0025],[1.9975,2.4149],[1.9975,2.1335]],"holes":[]},{"ext":[[1.0652,2.0025],[1.0025,2.0025],[1.0025,2.0652]],"holes":[]}],"LETRERO":{"horizonte_z":7.764,"horizonte_x":[40.976,72.252],"letras":[{"ext":[[52.5893,8.1359],[52.6369,8.0782],[52.6947,8.0306],[52.7609,7.9946],[52.8342,7.9719],[52.8729,7.9659],[52.9128,7.9639],[52.9527,7.9659],[52.9914,7.9719],[53.0646,7.9946],[53.1309,8.0306],[53.1886,8.0782],[53.2362,8.1359],[53.2722,8.2022],[53.2949,8.2754],[53.3009,8.3141],[53.3029,8.354],[53.3029,9.2639],[53.5029,9.2639],[53.5029,8.354],[53.4998,8.2937],[53.4909,8.2351],[53.4763,8.1786],[53.4565,8.1243],[53.4316,8.0728],[53.4021,8.0241],[53.3681,7.9787],[53.33,7.9368],[53.2881,7.8987],[53.2427,7.8647],[53.194,7.8352],[53.1425,7.8103],[53.0882,7.7905],[53.0317,7.7759],[52.9731,7.767],[52.9128,7.7639],[52.8524,7.767],[52.7938,7.7759],[52.7373,7.7905],[52.6831,7.8103],[52.6315,7.8352],[52.5828,7.8647],[52.5374,7.8987],[52.4955,7.9368],[52.4574,7.9787],[52.4235,8.0241],[52.3939,8.0728],[52.3691,8.1243],[52.3492,8.1786],[52.3347,8.2351],[52.3257,8.2937],[52.3227,8.354],[52.3227,9.2639],[52.5227,9.2639],[52.5227,8.354],[52.5247,8.3141],[52.5306,8.2754],[52.5533,8.2022]],"holes":[]},{"ext":[[54.0756,8.3611],[53.5029,9.2639],[53.7397,9.2639],[54.1756,8.5768],[54.6114,9.2639],[54.8482,9.2639],[54.2756,8.3611],[54.2756,7.7639],[54.0756,7.7639]],"holes":[]},{"ext":[[55.0789,8.2022],[55.1149,8.1359],[55.1625,8.0782],[55.2202,8.0306],[55.2865,7.9946],[55.3597,7.9719],[55.3985,7.9659],[55.4383,7.9639],[55.4782,7.9659],[55.517,7.9719],[55.5902,7.9946],[55.6564,8.0306],[55.7142,8.0782],[55.7618,8.1359],[55.7978,8.2022],[55.8205,8.2754],[55.8264,8.3141],[55.8284,8.354],[55.8284,9.2639],[56.0284,9.2639],[56.2284,9.2639],[57.0086,8.0958],[57.0086,9.2639],[57.2086,9.2639],[57.2086,7.7639],[57.0086,7.7639],[56.2284,8.9321],[56.2284,7.7639],[56.0284,7.7639],[56.0284,8.354],[56.0254,8.2937],[56.0164,8.2351],[56.0019,8.1786],[55.9821,8.1243],[55.9572,8.0728],[55.9277,8.0241],[55.8937,7.9787],[55.8556,7.9368],[55.8137,7.8987],[55.7683,7.8647],[55.7196,7.8352],[55.668,7.8103],[55.6138,7.7905],[55.5573,7.7759],[55.4987,7.767],[55.4383,7.7639],[55.378,7.767],[55.3194,7.7759],[55.2629,7.7905],[55.2086,7.8103],[55.1571,7.8352],[55.1084,7.8647],[55.063,7.8987],[55.0211,7.9368],[54.983,7.9787],[54.949,8.0241],[54.9195,8.0728],[54.8946,8.1243],[54.8748,8.1786],[54.8602,8.2351],[54.8513,8.2937],[54.8482,8.354],[54.8482,9.2639],[55.0482,9.2639],[55.0482,8.354],[55.0503,8.3141],[55.0562,8.2754]],"holes":[]},{"ext":[[57.8987,9.2639],[57.8987,7.7639],[57.6987,7.7639],[57.6987,9.2639]],"holes":[]}],"reflejo":[{"ext":[[53.3029,6.2641],[53.3029,7.174],[53.3009,7.2139],[53.2949,7.2526],[53.2722,7.3258],[53.2362,7.3921],[53.1886,7.4498],[53.1309,7.4974],[53.0646,7.5334],[52.9914,7.5561],[52.9527,7.5621],[52.9128,7.5641],[52.8729,7.5621],[52.8342,7.5561],[52.7609,7.5334],[52.6947,7.4974],[52.6369,7.4498],[52.5893,7.3921],[52.5533,7.3258],[52.5306,7.2526],[52.5247,7.2139],[52.5227,7.174],[52.5227,6.2641],[52.3227,6.2641],[52.3227,7.174],[52.3257,7.2343],[52.3347,7.2929],[52.3492,7.3494],[52.3691,7.4037],[52.3939,7.4552],[52.4235,7.5039],[52.4574,7.5493],[52.4955,7.5912],[52.5374,7.6293],[52.5828,7.6633],[52.6315,7.6928],[52.6831,7.7177],[52.7373,7.7375],[52.7938,7.7521],[52.8524,7.761],[52.9128,7.7641],[52.9731,7.761],[53.0317,7.7521],[53.0882,7.7375],[53.1425,7.7177],[53.194,7.6928],[53.2427,7.6633],[53.2881,7.6293],[53.33,7.5912],[53.3681,7.5493],[53.4021,7.5039],[53.4316,7.4552],[53.4565,7.4037],[53.4763,7.3494],[53.4909,7.2929],[53.4998,7.2343],[53.5029,7.174],[53.5029,6.2641]],"holes":[[[52.612,7.4747],[52.675,7.5265],[52.7472,7.5658],[52.8263,7.5903],[52.8693,7.597],[52.9128,7.5991],[52.9563,7.597],[52.9993,7.5903],[53.0783,7.5658],[53.1506,7.5265],[53.2135,7.4747],[53.2653,7.4118],[53.3046,7.3395],[53.3291,7.2605],[53.3358,7.2175],[53.3379,7.1749],[53.3379,6.2991],[53.4679,6.2991],[53.4679,7.1731],[53.4649,7.2308],[53.4566,7.2859],[53.4428,7.339],[53.4242,7.3901],[53.4008,7.4385],[53.3731,7.4843],[53.3411,7.527],[53.3052,7.5664],[53.2658,7.6023],[53.2231,7.6343],[53.1773,7.662],[53.1289,7.6854],[53.0778,7.704],[53.0247,7.7178],[52.9696,7.7261],[52.9128,7.7291],[52.8559,7.7261],[52.8008,7.7178],[52.7477,7.704],[52.6967,7.6854],[52.6482,7.662],[52.6024,7.6343],[52.5597,7.6023],[52.5203,7.5664],[52.4844,7.527],[52.4525,7.4843],[52.4247,7.4385],[52.4014,7.3901],[52.3827,7.339],[52.369,7.2859],[52.3606,7.2308],[52.3577,7.1731],[52.3577,6.2991],[52.4877,6.2991],[52.4877,7.1749],[52.4898,7.2174],[52.4964,7.2605],[52.5209,7.3395],[52.5602,7.4118]]]},{"ext":[[54.0756,7.1669],[54.0756,7.7641],[54.2756,7.7641],[54.2756,7.1669],[54.8482,6.2641],[54.6114,6.2641],[54.1756,6.9512],[53.7397,6.2641],[53.5029,6.2641]],"holes":[[[53.5666,6.2991],[53.7205,6.2991],[54.1756,7.0165],[54.6306,6.2991],[54.7846,6.2991],[54.2406,7.1567],[54.2406,7.7291],[54.1106,7.7291],[54.1106,7.1567]]]},{"ext":[[54.8482,7.174],[54.8513,7.2343],[54.8602,7.2929],[54.8748,7.3494],[54.8946,7.4037],[54.9195,7.4552],[54.949,7.5039],[54.983,7.5493],[55.0211,7.5912],[55.063,7.6293],[55.1084,7.6633],[55.1571,7.6928],[55.2086,7.7177],[55.2629,7.7375],[55.3194,7.7521],[55.378,7.761],[55.4383,7.7641],[55.4987,7.761],[55.5573,7.7521],[55.6138,7.7375],[55.668,7.7177],[55.7196,7.6928],[55.7683,7.6633],[55.8137,7.6293],[55.8556,7.5912],[55.8937,7.5493],[55.9277,7.5039],[55.9572,7.4552],[55.9821,7.4037],[56.0019,7.3494],[56.0164,7.2929],[56.0254,7.2343],[56.0284,7.174],[56.0284,7.7641],[56.2284,7.7641],[56.2284,6.5959],[57.0086,7.7641],[57.2086,7.7641],[57.2086,6.2641],[57.0086,6.2641],[57.0086,7.4322],[56.2284,6.2641],[56.0284,6.2641],[55.8284,6.2641],[55.8284,7.174],[55.8264,7.2139],[55.8205,7.2526],[55.7978,7.3258],[55.7618,7.3921],[55.7142,7.4498],[55.6564,7.4974],[55.5902,7.5334],[55.517,7.5561],[55.4782,7.5621],[55.4383,7.5641],[55.3985,7.5621],[55.3597,7.5561],[55.2865,7.5334],[55.2202,7.4974],[55.1625,7.4498],[55.1149,7.3921],[55.0789,7.3258],[55.0562,7.2526],[55.0503,7.2139],[55.0482,7.174],[55.0482,6.2641],[54.8482,6.2641]],"holes":[[[55.0858,7.4118],[55.1376,7.4747],[55.2005,7.5265],[55.2728,7.5658],[55.3518,7.5903],[55.3949,7.597],[55.4383,7.5991],[55.4818,7.597],[55.5249,7.5903],[55.6039,7.5658],[55.6761,7.5265],[55.7391,7.4747],[55.7909,7.4118],[55.8302,7.3395],[55.8547,7.2605],[55.8613,7.2174],[55.8634,7.1749],[55.8634,6.2991],[56.2097,6.2991],[57.0436,7.5476],[57.0436,6.2991],[57.1736,6.2991],[57.1736,7.7291],[57.0273,7.7291],[56.1934,6.4805],[56.1934,7.7291],[56.0634,7.7291],[56.0634,6.9998],[56.0021,6.9983],[55.9905,7.2308],[55.9821,7.2859],[55.9684,7.339],[55.9498,7.3901],[55.9264,7.4385],[55.8987,7.4843],[55.8667,7.527],[55.8308,7.5664],[55.7914,7.6023],[55.7487,7.6343],[55.7029,7.662],[55.6544,7.6854],[55.6034,7.704],[55.5503,7.7178],[55.4952,7.7261],[55.4383,7.7291],[55.3815,7.7261],[55.3264,7.7178],[55.2733,7.704],[55.2222,7.6854],[55.1738,7.662],[55.128,7.6343],[55.0853,7.6023],[55.0459,7.5664],[55.01,7.527],[54.978,7.4843],[54.9503,7.4385],[54.9269,7.3901],[54.9083,7.339],[54.8945,7.2859],[54.8862,7.2308],[54.8832,7.1731],[54.8832,6.2991],[55.0132,6.2991],[55.0132,7.1749],[55.0154,7.2175],[55.022,7.2605],[55.0465,7.3395]]]},{"ext":[[57.6987,6.2641],[57.6987,7.7641],[57.8987,7.7641],[57.8987,6.2641]],"holes":[[[57.8637,7.7291],[57.7337,7.7291],[57.7337,6.2991],[57.8637,6.2991]]]}],"rombos_sup":[{"ext":[[43.417,8.759],[43.417,7.764],[42.422,7.764]],"holes":[[[42.6989,7.8264],[42.708,7.8173],[42.7205,7.8139],[42.733,7.8173],[42.7422,7.8264],[42.7455,7.8389],[42.7422,7.8514],[42.733,7.8606],[42.7205,7.8639],[42.708,7.8606],[42.6989,7.8514],[42.6955,7.8389]],[[42.5815,7.8389],[42.5849,7.8264],[42.594,7.8173],[42.6065,7.8139],[42.619,7.8173],[42.6282,7.8264],[42.6315,7.8389],[42.6282,7.8514],[42.619,7.8606],[42.6065,7.8639],[42.594,7.8606],[42.5849,7.8514]],[[43.0375,7.8389],[43.0408,7.8264],[43.05,7.8173],[43.0625,7.8139],[43.075,7.8173],[43.0841,7.8264],[43.0875,7.8389],[43.0841,7.8514],[43.075,7.8606],[43.0625,7.8639],[43.05,7.8606],[43.0408,7.8514]],[[42.8095,7.8389],[42.8128,7.8264],[42.822,7.8173],[42.8345,7.8139],[42.847,7.8173],[42.8562,7.8264],[42.8595,7.8389],[42.8562,7.8514],[42.847,7.8606],[42.8345,7.8639],[42.822,7.8606],[42.8128,7.8514]],[[42.9235,7.8389],[42.9268,7.8264],[42.936,7.8173],[42.9485,7.8139],[42.961,7.8173],[42.9701,7.8264],[42.9735,7.8389],[42.9701,7.8514],[42.961,7.8606],[42.9485,7.8639],[42.936,7.8606],[42.9268,7.8514]],[[42.6385,7.8959],[42.6419,7.8834],[42.651,7.8743],[42.6635,7.8709],[42.676,7.8743],[42.6852,7.8834],[42.6885,7.8959],[42.6852,7.9084],[42.676,7.9176],[42.6635,7.9209],[42.651,7.9176],[42.6419,7.9084]],[[42.9805,7.8959],[42.9838,7.8834],[42.993,7.8743],[43.0055,7.8709],[43.018,7.8743],[43.0271,7.8834],[43.0305,7.8959],[43.0271,7.9084],[43.018,7.9176],[43.0055,7.9209],[42.993,7.9176],[42.9838,7.9084]],[[42.7559,7.8834],[42.765,7.8743],[42.7775,7.8709],[42.79,7.8743],[42.7992,7.8834],[42.8025,7.8959],[42.7992,7.9084],[42.79,7.9176],[42.7775,7.9209],[42.765,7.9176],[42.7559,7.9084],[42.7525,7.8959]],[[42.8665,7.8959],[42.8698,7.8834],[42.879,7.8743],[42.8915,7.8709],[42.904,7.8743],[42.9131,7.8834],[42.9165,7.8959],[42.9131,7.9084],[42.904,7.9176],[42.8915,7.9209],[42.879,7.9176],[42.8698,7.9084]],[[43.0375,7.9529],[43.0408,7.9404],[43.05,7.9313],[43.0625,7.9279],[43.075,7.9313],[43.0841,7.9404],[43.0875,7.9529],[43.0841,7.9654],[43.075,7.9746],[43.0625,7.9779],[43.05,7.9746],[43.0408,7.9654]],[[42.9235,7.9529],[42.9268,7.9404],[42.936,7.9313],[42.9485,7.9279],[42.961,7.9313],[42.9701,7.9404],[42.9735,7.9529],[42.9701,7.9654],[42.961,7.9746],[42.9485,7.9779],[42.936,7.9746],[42.9268,7.9654]],[[42.8095,7.9529],[42.8128,7.9404],[42.822,7.9313],[42.8345,7.9279],[42.847,7.9313],[42.8562,7.9404],[42.8595,7.9529],[42.8562,7.9654],[42.847,7.9746],[42.8345,7.9779],[42.822,7.9746],[42.8128,7.9654]],[[42.6955,7.9529],[42.6989,7.9404],[42.708,7.9313],[42.7205,7.9279],[42.733,7.9313],[42.7422,7.9404],[42.7455,7.9529],[42.7422,7.9654],[42.733,7.9746],[42.7205,7.9779],[42.708,7.9746],[42.6989,7.9654]],[[42.8665,8.0099],[42.8698,7.9974],[42.879,7.9883],[42.8915,7.9849],[42.904,7.9883],[42.9131,7.9974],[42.9165,8.0099],[42.9131,8.0224],[42.904,8.0316],[42.8915,8.0349],[42.879,8.0316],[42.8698,8.0224]],[[43.0978,7.9974],[43.107,7.9883],[43.1195,7.9849],[43.132,7.9883],[43.1411,7.9974],[43.1445,8.0099],[43.1411,8.0224],[43.132,8.0316],[43.1195,8.0349],[43.107,8.0316],[43.0978,8.0224],[43.0945,8.0099]],[[42.7525,8.0099],[42.7559,7.9974],[42.765,7.9883],[42.7775,7.9849],[42.79,7.9883],[42.7992,7.9974],[42.8025,8.0099],[42.7992,8.0224],[42.79,8.0316],[42.7775,8.0349],[42.765,8.0316],[42.7559,8.0224]],[[42.9805,8.0099],[42.9838,7.9974],[42.993,7.9883],[43.0055,7.9849],[43.018,7.9883],[43.0271,7.9974],[43.0305,8.0099],[43.0271,8.0224],[43.018,8.0316],[43.0055,8.0349],[42.993,8.0316],[42.9838,8.0224]],[[43.0375,8.0669],[43.0408,8.0544],[43.05,8.0453],[43.0625,8.0419],[43.075,8.0453],[43.0841,8.0544],[43.0875,8.0669],[43.0841,8.0794],[43.075,8.0886],[43.0625,8.0919],[43.05,8.0886],[43.0408,8.0794]],[[42.9235,8.0669],[42.9268,8.0544],[42.936,8.0453],[42.9485,8.0419],[42.961,8.0453],[42.9701,8.0544],[42.9735,8.0669],[42.9701,8.0794],[42.961,8.0886],[42.9485,8.0919],[42.936,8.0886],[42.9268,8.0794]],[[42.8095,8.0669],[42.8128,8.0544],[42.822,8.0453],[42.8345,8.0419],[42.847,8.0453],[42.8562,8.0544],[42.8595,8.0669],[42.8562,8.0794],[42.847,8.0886],[42.8345,8.0919],[42.822,8.0886],[42.8128,8.0794]],[[42.9805,8.1239],[42.9838,8.1114],[42.993,8.1023],[43.0055,8.0989],[43.018,8.1023],[43.0271,8.1114],[43.0305,8.1239],[43.0271,8.1364],[43.018,8.1456],[43.0055,8.1489],[42.993,8.1456],[42.9838,8.1364]],[[42.8698,8.1114],[42.879,8.1023],[42.8915,8.0989],[42.904,8.1023],[42.9131,8.1114],[42.9165,8.1239],[42.9131,8.1364],[42.904,8.1456],[42.8915,8.1489],[42.879,8.1456],[42.8698,8.1364],[42.8665,8.1239]],[[43.0375,8.1809],[43.0408,8.1684],[43.05,8.1592],[43.0625,8.1559],[43.075,8.1592],[43.0841,8.1684],[43.0875,8.1809],[43.0841,8.1934],[43.075,8.2026],[43.0625,8.2059],[43.05,8.2026],[43.0408,8.1934]],[[42.9235,8.1809],[42.9268,8.1684],[42.936,8.1592],[42.9485,8.1559],[42.961,8.1592],[42.9701,8.1684],[42.9735,8.1809],[42.9701,8.1934],[42.961,8.2026],[42.9485,8.2059],[42.936,8.2026],[42.9268,8.1934]],[[42.9805,8.2379],[42.9838,8.2254],[42.993,8.2162],[43.0055,8.2129],[43.018,8.2162],[43.0271,8.2254],[43.0305,8.2379],[43.0271,8.2504],[43.018,8.2595],[43.0055,8.2629],[42.993,8.2595],[42.9838,8.2504]],[[43.0945,8.2379],[43.0978,8.2254],[43.107,8.2162],[43.1195,8.2129],[43.132,8.2162],[43.1411,8.2254],[43.1445,8.2379],[43.1411,8.2504],[43.132,8.2595],[43.1195,8.2629],[43.107,8.2595],[43.0978,8.2504]],[[43.0375,8.2949],[43.0408,8.2824],[43.05,8.2732],[43.0625,8.2699],[43.075,8.2732],[43.0841,8.2824],[43.0875,8.2949],[43.0841,8.3074],[43.075,8.3165],[43.0625,8.3199],[43.05,8.3165],[43.0408,8.3074]],[[43.0945,8.3519],[43.0978,8.3394],[43.107,8.3302],[43.1195,8.3269],[43.132,8.3302],[43.1411,8.3394],[43.1445,8.3519],[43.1411,8.3644],[43.132,8.3735],[43.1195,8.3769],[43.107,8.3735],[43.0978,8.3644]],[[43.2688,7.8264],[43.278,7.8173],[43.2905,7.8139],[43.303,7.8173],[43.3121,7.8264],[43.3155,7.8389],[43.3121,7.8514],[43.303,7.8606],[43.2905,7.8639],[43.278,7.8606],[43.2688,7.8514],[43.2655,7.8389]],[[43.1515,7.8389],[43.1548,7.8264],[43.164,7.8173],[43.1765,7.8139],[43.189,7.8173],[43.1981,7.8264],[43.2015,7.8389],[43.1981,7.8514],[43.189,7.8606],[43.1765,7.8639],[43.164,7.8606],[43.1548,7.8514]],[[43.0945,7.8959],[43.0978,7.8834],[43.107,7.8743],[43.1195,7.8709],[43.132,7.8743],[43.1411,7.8834],[43.1445,7.8959],[43.1411,7.9084],[43.132,7.9176],[43.1195,7.9209],[43.107,7.9176],[43.0978,7.9084]],[[43.3225,7.8959],[43.3258,7.8834],[43.335,7.8743],[43.3475,7.8709],[43.36,7.8743],[43.3691,7.8834],[43.3725,7.8959],[43.3691,7.9084],[43.36,7.9176],[43.3475,7.9209],[43.335,7.9176],[43.3258,7.9084]],[[43.2085,7.8959],[43.2118,7.8834],[43.221,7.8743],[43.2335,7.8709],[43.246,7.8743],[43.2551,7.8834],[43.2585,7.8959],[43.2551,7.9084],[43.246,7.9176],[43.2335,7.9209],[43.221,7.9176],[43.2118,7.9084]],[[43.2655,7.9529],[43.2688,7.9404],[43.278,7.9313],[43.2905,7.9279],[43.303,7.9313],[43.3121,7.9404],[43.3155,7.9529],[43.3121,7.9654],[43.303,7.9746],[43.2905,7.9779],[43.278,7.9746],[43.2688,7.9654]],[[43.1515,7.9529],[43.1548,7.9404],[43.164,7.9313],[43.1765,7.9279],[43.189,7.9313],[43.1981,7.9404],[43.2015,7.9529],[43.1981,7.9654],[43.189,7.9746],[43.1765,7.9779],[43.164,7.9746],[43.1548,7.9654]],[[43.3258,7.9974],[43.335,7.9883],[43.3475,7.9849],[43.36,7.9883],[43.3691,7.9974],[43.3725,8.0099],[43.3691,8.0224],[43.36,8.0316],[43.3475,8.0349],[43.335,8.0316],[43.3258,8.0224],[43.3225,8.0099]],[[43.2085,8.0099],[43.2118,7.9974],[43.221,7.9883],[43.2335,7.9849],[43.246,7.9883],[43.2551,7.9974],[43.2585,8.0099],[43.2551,8.0224],[43.246,8.0316],[43.2335,8.0349],[43.221,8.0316],[43.2118,8.0224]],[[43.1515,8.0669],[43.1548,8.0544],[43.164,8.0453],[43.1765,8.0419],[43.189,8.0453],[43.1981,8.0544],[43.2015,8.0669],[43.1981,8.0794],[43.189,8.0886],[43.1765,8.0919],[43.164,8.0886],[43.1548,8.0794]],[[43.2655,8.0669],[43.2688,8.0544],[43.278,8.0453],[43.2905,8.0419],[43.303,8.0453],[43.3121,8.0544],[43.3155,8.0669],[43.3121,8.0794],[43.303,8.0886],[43.2905,8.0919],[43.278,8.0886],[43.2688,8.0794]],[[43.2085,8.1239],[43.2118,8.1114],[43.221,8.1023],[43.2335,8.0989],[43.246,8.1023],[43.2551,8.1114],[43.2585,8.1239],[43.2551,8.1364],[43.246,8.1456],[43.2335,8.1489],[43.221,8.1456],[43.2118,8.1364]],[[43.0945,8.1239],[43.0978,8.1114],[43.107,8.1023],[43.1195,8.0989],[43.132,8.1023],[43.1411,8.1114],[43.1445,8.1239],[43.1411,8.1364],[43.132,8.1456],[43.1195,8.1489],[43.107,8.1456],[43.0978,8.1364]],[[43.3225,8.1239],[43.3258,8.1114],[43.335,8.1023],[43.3475,8.0989],[43.36,8.1023],[43.3691,8.1114],[43.3725,8.1239],[43.3691,8.1364],[43.36,8.1456],[43.3475,8.1489],[43.335,8.1456],[43.3258,8.1364]],[[43.1548,8.1684],[43.164,8.1592],[43.1765,8.1559],[43.189,8.1592],[43.1981,8.1684],[43.2015,8.1809],[43.1981,8.1934],[43.189,8.2026],[43.1765,8.2059],[43.164,8.2026],[43.1548,8.1934],[43.1515,8.1809]],[[43.2655,8.1809],[43.2688,8.1684],[43.278,8.1592],[43.2905,8.1559],[43.303,8.1592],[43.3121,8.1684],[43.3155,8.1809],[43.3121,8.1934],[43.303,8.2026],[43.2905,8.2059],[43.278,8.2026],[43.2688,8.1934]],[[43.2085,8.2379],[43.2118,8.2254],[43.221,8.2162],[43.2335,8.2129],[43.246,8.2162],[43.2551,8.2254],[43.2585,8.2379],[43.2551,8.2504],[43.246,8.2595],[43.2335,8.2629],[43.221,8.2595],[43.2118,8.2504]],[[43.3225,8.2379],[43.3258,8.2254],[43.335,8.2162],[43.3475,8.2129],[43.36,8.2162],[43.3691,8.2254],[43.3725,8.2379],[43.3691,8.2504],[43.36,8.2595],[43.3475,8.2629],[43.335,8.2595],[43.3258,8.2504]],[[43.2655,8.2949],[43.2688,8.2824],[43.278,8.2732],[43.2905,8.2699],[43.303,8.2732],[43.3121,8.2824],[43.3155,8.2949],[43.3121,8.3074],[43.303,8.3165],[43.2905,8.3199],[43.278,8.3165],[43.2688,8.3074]],[[43.1515,8.2949],[43.1548,8.2824],[43.164,8.2732],[43.1765,8.2699],[43.189,8.2732],[43.1981,8.2824],[43.2015,8.2949],[43.1981,8.3074],[43.189,8.3165],[43.1765,8.3199],[43.164,8.3165],[43.1548,8.3074]],[[43.3225,8.3519],[43.3258,8.3394],[43.335,8.3302],[43.3475,8.3269],[43.36,8.3302],[43.3691,8.3394],[43.3725,8.3519],[43.3691,8.3644],[43.36,8.3735],[43.3475,8.3769],[43.335,8.3735],[43.3258,8.3644]],[[43.2118,8.3394],[43.221,8.3302],[43.2335,8.3269],[43.246,8.3302],[43.2551,8.3394],[43.2585,8.3519],[43.2551,8.3644],[43.246,8.3735],[43.2335,8.3769],[43.221,8.3735],[43.2118,8.3644],[43.2085,8.3519]],[[43.1515,8.4089],[43.1548,8.3964],[43.164,8.3872],[43.1765,8.3839],[43.189,8.3872],[43.1981,8.3964],[43.2015,8.4089],[43.1981,8.4214],[43.189,8.4305],[43.1765,8.4339],[43.164,8.4305],[43.1548,8.4214]],[[43.2655,8.4089],[43.2688,8.3964],[43.278,8.3872],[43.2905,8.3839],[43.303,8.3872],[43.3121,8.3964],[43.3155,8.4089],[43.3121,8.4214],[43.303,8.4305],[43.2905,8.4339],[43.278,8.4305],[43.2688,8.4214]],[[43.2085,8.4659],[43.2118,8.4534],[43.221,8.4442],[43.2335,8.4409],[43.246,8.4442],[43.2551,8.4534],[43.2585,8.4659],[43.2551,8.4784],[43.246,8.4875],[43.2335,8.4909],[43.221,8.4875],[43.2118,8.4784]],[[43.3225,8.4659],[43.3258,8.4534],[43.335,8.4442],[43.3475,8.4409],[43.36,8.4442],[43.3691,8.4534],[43.3725,8.4659],[43.3691,8.4784],[43.36,8.4875],[43.3475,8.4909],[43.335,8.4875],[43.3258,8.4784]],[[43.2655,8.5229],[43.2688,8.5104],[43.278,8.5012],[43.2905,8.4979],[43.303,8.5012],[43.3121,8.5104],[43.3155,8.5229],[43.3121,8.5354],[43.303,8.5445],[43.2905,8.5479],[43.278,8.5445],[43.2688,8.5354]],[[43.3225,8.5799],[43.3258,8.5674],[43.335,8.5582],[43.3475,8.5549],[43.36,8.5582],[43.3691,8.5674],[43.3725,8.5799],[43.3691,8.5924],[43.36,8.6015],[43.3475,8.6049],[43.335,8.6015],[43.3258,8.5924]]]},{"ext":[[43.427,8.759],[44.422,7.764],[43.427,7.764]],"holes":[[[43.5328,7.8264],[43.5419,7.8173],[43.5544,7.8139],[43.5669,7.8173],[43.5761,7.8264],[43.5794,7.8389],[43.5761,7.8514],[43.5669,7.8606],[43.5544,7.8639],[43.5419,7.8606],[43.5328,7.8514],[43.5294,7.8389]],[[43.6434,7.8389],[43.6468,7.8264],[43.6559,7.8173],[43.6684,7.8139],[43.6809,7.8173],[43.6901,7.8264],[43.6934,7.8389],[43.6901,7.8514],[43.6809,7.8606],[43.6684,7.8639],[43.6559,7.8606],[43.6468,7.8514]],[[43.7004,7.8959],[43.7038,7.8834],[43.7129,7.8743],[43.7254,7.8709],[43.7379,7.8743],[43.7471,7.8834],[43.7504,7.8959],[43.7471,7.9084],[43.7379,7.9176],[43.7254,7.9209],[43.7129,7.9176],[43.7038,7.9084]],[[43.5864,7.8959],[43.5898,7.8834],[43.5989,7.8743],[43.6114,7.8709],[43.6239,7.8743],[43.6331,7.8834],[43.6364,7.8959],[43.6331,7.9084],[43.6239,7.9176],[43.6114,7.9209],[43.5989,7.9176],[43.5898,7.9084]],[[43.4725,7.8959],[43.4758,7.8834],[43.485,7.8743],[43.4975,7.8709],[43.51,7.8743],[43.5191,7.8834],[43.5225,7.8959],[43.5191,7.9084],[43.51,7.9176],[43.4975,7.9209],[43.485,7.9176],[43.4758,7.9084]],[[43.6434,7.9529],[43.6468,7.9404],[43.6559,7.9313],[43.6684,7.9279],[43.6809,7.9313],[43.6901,7.9404],[43.6934,7.9529],[43.6901,7.9654],[43.6809,7.9746],[43.6684,7.9779],[43.6559,7.9746],[43.6468,7.9654]],[[43.5294,7.9529],[43.5328,7.9404],[43.5419,7.9313],[43.5544,7.9279],[43.5669,7.9313],[43.5761,7.9404],[43.5794,7.9529],[43.5761,7.9654],[43.5669,7.9746],[43.5544,7.9779],[43.5419,7.9746],[43.5328,7.9654]],[[43.4758,7.9974],[43.485,7.9883],[43.4975,7.9849],[43.51,7.9883],[43.5191,7.9974],[43.5225,8.0099],[43.5191,8.0224],[43.51,8.0316],[43.4975,8.0349],[43.485,8.0316],[43.4758,8.0224],[43.4725,8.0099]],[[43.7004,8.0099],[43.7038,7.9974],[43.7129,7.9883],[43.7254,7.9849],[43.7379,7.9883],[43.7471,7.9974],[43.7504,8.0099],[43.7471,8.0224],[43.7379,8.0316],[43.7254,8.0349],[43.7129,8.0316],[43.7038,8.0224]],[[43.5864,8.0099],[43.5898,7.9974],[43.5989,7.9883],[43.6114,7.9849],[43.6239,7.9883],[43.6331,7.9974],[43.6364,8.0099],[43.6331,8.0224],[43.6239,8.0316],[43.6114,8.0349],[43.5989,8.0316],[43.5898,8.0224]],[[43.6434,8.0669],[43.6468,8.0544],[43.6559,8.0453],[43.6684,8.0419],[43.6809,8.0453],[43.6901,8.0544],[43.6934,8.0669],[43.6901,8.0794],[43.6809,8.0886],[43.6684,8.0919],[43.6559,8.0886],[43.6468,8.0794]],[[43.5294,8.0669],[43.5328,8.0544],[43.5419,8.0453],[43.5544,8.0419],[43.5669,8.0453],[43.5761,8.0544],[43.5794,8.0669],[43.5761,8.0794],[43.5669,8.0886],[43.5544,8.0919],[43.5419,8.0886],[43.5328,8.0794]],[[43.4725,8.1239],[43.4758,8.1114],[43.485,8.1023],[43.4975,8.0989],[43.51,8.1023],[43.5191,8.1114],[43.5225,8.1239],[43.5191,8.1364],[43.51,8.1456],[43.4975,8.1489],[43.485,8.1456],[43.4758,8.1364]],[[43.5864,8.1239],[43.5898,8.1114],[43.5989,8.1023],[43.6114,8.0989],[43.6239,8.1023],[43.6331,8.1114],[43.6364,8.1239],[43.6331,8.1364],[43.6239,8.1456],[43.6114,8.1489],[43.5989,8.1456],[43.5898,8.1364]],[[43.6468,8.1684],[43.6559,8.1592],[43.6684,8.1559],[43.6809,8.1592],[43.6901,8.1684],[43.6934,8.1809],[43.6901,8.1934],[43.6809,8.2026],[43.6684,8.2059],[43.6559,8.2026],[43.6468,8.1934],[43.6434,8.1809]],[[43.5294,8.1809],[43.5328,8.1684],[43.5419,8.1592],[43.5544,8.1559],[43.5669,8.1592],[43.5761,8.1684],[43.5794,8.1809],[43.5761,8.1934],[43.5669,8.2026],[43.5544,8.2059],[43.5419,8.2026],[43.5328,8.1934]],[[43.5864,8.2379],[43.5898,8.2254],[43.5989,8.2162],[43.6114,8.2129],[43.6239,8.2162],[43.6331,8.2254],[43.6364,8.2379],[43.6331,8.2504],[43.6239,8.2595],[43.6114,8.2629],[43.5989,8.2595],[43.5898,8.2504]],[[43.4725,8.2379],[43.4758,8.2254],[43.485,8.2162],[43.4975,8.2129],[43.51,8.2162],[43.5191,8.2254],[43.5225,8.2379],[43.5191,8.2504],[43.51,8.2595],[43.4975,8.2629],[43.485,8.2595],[43.4758,8.2504]],[[43.5294,8.2949],[43.5328,8.2824],[43.5419,8.2732],[43.5544,8.2699],[43.5669,8.2732],[43.5761,8.2824],[43.5794,8.2949],[43.5761,8.3074],[43.5669,8.3165],[43.5544,8.3199],[43.5419,8.3165],[43.5328,8.3074]],[[43.6434,8.2949],[43.6468,8.2824],[43.6559,8.2732],[43.6684,8.2699],[43.6809,8.2732],[43.6901,8.2824],[43.6934,8.2949],[43.6901,8.3074],[43.6809,8.3165],[43.6684,8.3199],[43.6559,8.3165],[43.6468,8.3074]],[[43.5864,8.3519],[43.5898,8.3394],[43.5989,8.3302],[43.6114,8.3269],[43.6239,8.3302],[43.6331,8.3394],[43.6364,8.3519],[43.6331,8.3644],[43.6239,8.3735],[43.6114,8.3769],[43.5989,8.3735],[43.5898,8.3644]],[[43.4758,8.3394],[43.485,8.3302],[43.4975,8.3269],[43.51,8.3302],[43.5191,8.3394],[43.5225,8.3519],[43.5191,8.3644],[43.51,8.3735],[43.4975,8.3769],[43.485,8.3735],[43.4758,8.3644],[43.4725,8.3519]],[[43.5294,8.4089],[43.5328,8.3964],[43.5419,8.3872],[43.5544,8.3839],[43.5669,8.3872],[43.5761,8.3964],[43.5794,8.4089],[43.5761,8.4214],[43.5669,8.4305],[43.5544,8.4339],[43.5419,8.4305],[43.5328,8.4214]],[[43.6434,8.4089],[43.6468,8.3964],[43.6559,8.3872],[43.6684,8.3839],[43.6809,8.3872],[43.6901,8.3964],[43.6934,8.4089],[43.6901,8.4214],[43.6809,8.4305],[43.6684,8.4339],[43.6559,8.4305],[43.6468,8.4214]],[[43.5864,8.4659],[43.5898,8.4534],[43.5989,8.4442],[43.6114,8.4409],[43.6239,8.4442],[43.6331,8.4534],[43.6364,8.4659],[43.6331,8.4784],[43.6239,8.4875],[43.6114,8.4909],[43.5989,8.4875],[43.5898,8.4784]],[[43.4725,8.4659],[43.4758,8.4534],[43.485,8.4442],[43.4975,8.4409],[43.51,8.4442],[43.5191,8.4534],[43.5225,8.4659],[43.5191,8.4784],[43.51,8.4875],[43.4975,8.4909],[43.485,8.4875],[43.4758,8.4784]],[[43.5294,8.5229],[43.5328,8.5104],[43.5419,8.5012],[43.5544,8.4979],[43.5669,8.5012],[43.5761,8.5104],[43.5794,8.5229],[43.5761,8.5354],[43.5669,8.5445],[43.5544,8.5479],[43.5419,8.5445],[43.5328,8.5354]],[[43.4725,8.5799],[43.4758,8.5674],[43.485,8.5582],[43.4975,8.5549],[43.51,8.5582],[43.5191,8.5674],[43.5225,8.5799],[43.5191,8.5924],[43.51,8.6015],[43.4975,8.6049],[43.485,8.6015],[43.4758,8.5924]],[[44.2167,7.8264],[44.2259,7.8173],[44.2384,7.8139],[44.2509,7.8173],[44.26,7.8264],[44.2634,7.8389],[44.26,7.8514],[44.2509,7.8606],[44.2384,7.8639],[44.2259,7.8606],[44.2167,7.8514],[44.2134,7.8389]],[[43.7574,7.8389],[43.7608,7.8264],[43.7699,7.8173],[43.7824,7.8139],[43.7949,7.8173],[43.8041,7.8264],[43.8074,7.8389],[43.8041,7.8514],[43.7949,7.8606],[43.7824,7.8639],[43.7699,7.8606],[43.7608,7.8514]],[[43.9854,7.8389],[43.9887,7.8264],[43.9979,7.8173],[44.0104,7.8139],[44.0229,7.8173],[44.0321,7.8264],[44.0354,7.8389],[44.0321,7.8514],[44.0229,7.8606],[44.0104,7.8639],[43.9979,7.8606],[43.9887,7.8514]],[[43.8714,7.8389],[43.8748,7.8264],[43.8839,7.8173],[43.8964,7.8139],[43.9089,7.8173],[43.9181,7.8264],[43.9214,7.8389],[43.9181,7.8514],[43.9089,7.8606],[43.8964,7.8639],[43.8839,7.8606],[43.8748,7.8514]],[[44.0994,7.8389],[44.1027,7.8264],[44.1119,7.8173],[44.1244,7.8139],[44.1369,7.8173],[44.146,7.8264],[44.1494,7.8389],[44.146,7.8514],[44.1369,7.8606],[44.1244,7.8639],[44.1119,7.8606],[44.1027,7.8514]],[[43.8144,7.8959],[43.8178,7.8834],[43.8269,7.8743],[43.8394,7.8709],[43.8519,7.8743],[43.8611,7.8834],[43.8644,7.8959],[43.8611,7.9084],[43.8519,7.9176],[43.8394,7.9209],[43.8269,7.9176],[43.8178,7.9084]],[[43.9284,7.8959],[43.9318,7.8834],[43.9409,7.8743],[43.9534,7.8709],[43.9659,7.8743],[43.9751,7.8834],[43.9784,7.8959],[43.9751,7.9084],[43.9659,7.9176],[43.9534,7.9209],[43.9409,7.9176],[43.9318,7.9084]],[[44.0457,7.8834],[44.0549,7.8743],[44.0674,7.8709],[44.0799,7.8743],[44.089,7.8834],[44.0924,7.8959],[44.089,7.9084],[44.0799,7.9176],[44.0674,7.9209],[44.0549,7.9176],[44.0457,7.9084],[44.0424,7.8959]],[[44.1564,7.8959],[44.1597,7.8834],[44.1689,7.8743],[44.1814,7.8709],[44.1939,7.8743],[44.203,7.8834],[44.2064,7.8959],[44.203,7.9084],[44.1939,7.9176],[44.1814,7.9209],[44.1689,7.9176],[44.1597,7.9084]],[[43.9854,7.9529],[43.9887,7.9404],[43.9979,7.9313],[44.0104,7.9279],[44.0229,7.9313],[44.0321,7.9404],[44.0354,7.9529],[44.0321,7.9654],[44.0229,7.9746],[44.0104,7.9779],[43.9979,7.9746],[43.9887,7.9654]],[[43.7574,7.9529],[43.7608,7.9404],[43.7699,7.9313],[43.7824,7.9279],[43.7949,7.9313],[43.8041,7.9404],[43.8074,7.9529],[43.8041,7.9654],[43.7949,7.9746],[43.7824,7.9779],[43.7699,7.9746],[43.7608,7.9654]],[[44.0994,7.9529],[44.1027,7.9404],[44.1119,7.9313],[44.1244,7.9279],[44.1369,7.9313],[44.146,7.9404],[44.1494,7.9529],[44.146,7.9654],[44.1369,7.9746],[44.1244,7.9779],[44.1119,7.9746],[44.1027,7.9654]],[[43.8714,7.9529],[43.8748,7.9404],[43.8839,7.9313],[43.8964,7.9279],[43.9089,7.9313],[43.9181,7.9404],[43.9214,7.9529],[43.9181,7.9654],[43.9089,7.9746],[43.8964,7.9779],[43.8839,7.9746],[43.8748,7.9654]],[[44.0424,8.0099],[44.0457,7.9974],[44.0549,7.9883],[44.0674,7.9849],[44.0799,7.9883],[44.089,7.9974],[44.0924,8.0099],[44.089,8.0224],[44.0799,8.0316],[44.0674,8.0349],[44.0549,8.0316],[44.0457,8.0224]],[[43.8178,7.9974],[43.8269,7.9883],[43.8394,7.9849],[43.8519,7.9883],[43.8611,7.9974],[43.8644,8.0099],[43.8611,8.0224],[43.8519,8.0316],[43.8394,8.0349],[43.8269,8.0316],[43.8178,8.0224],[43.8144,8.0099]],[[43.9284,8.0099],[43.9318,7.9974],[43.9409,7.9883],[43.9534,7.9849],[43.9659,7.9883],[43.9751,7.9974],[43.9784,8.0099],[43.9751,8.0224],[43.9659,8.0316],[43.9534,8.0349],[43.9409,8.0316],[43.9318,8.0224]],[[43.8714,8.0669],[43.8748,8.0544],[43.8839,8.0453],[43.8964,8.0419],[43.9089,8.0453],[43.9181,8.0544],[43.9214,8.0669],[43.9181,8.0794],[43.9089,8.0886],[43.8964,8.0919],[43.8839,8.0886],[43.8748,8.0794]],[[43.9854,8.0669],[43.9887,8.0544],[43.9979,8.0453],[44.0104,8.0419],[44.0229,8.0453],[44.0321,8.0544],[44.0354,8.0669],[44.0321,8.0794],[44.0229,8.0886],[44.0104,8.0919],[43.9979,8.0886],[43.9887,8.0794]],[[43.7574,8.0669],[43.7608,8.0544],[43.7699,8.0453],[43.7824,8.0419],[43.7949,8.0453],[43.8041,8.0544],[43.8074,8.0669],[43.8041,8.0794],[43.7949,8.0886],[43.7824,8.0919],[43.7699,8.0886],[43.7608,8.0794]],[[43.9284,8.1239],[43.9318,8.1114],[43.9409,8.1023],[43.9534,8.0989],[43.9659,8.1023],[43.9751,8.1114],[43.9784,8.1239],[43.9751,8.1364],[43.9659,8.1456],[43.9534,8.1489],[43.9409,8.1456],[43.9318,8.1364]],[[43.8144,8.1239],[43.8178,8.1114],[43.8269,8.1023],[43.8394,8.0989],[43.8519,8.1023],[43.8611,8.1114],[43.8644,8.1239],[43.8611,8.1364],[43.8519,8.1456],[43.8394,8.1489],[43.8269,8.1456],[43.8178,8.1364]],[[43.7038,8.1114],[43.7129,8.1023],[43.7254,8.0989],[43.7379,8.1023],[43.7471,8.1114],[43.7504,8.1239],[43.7471,8.1364],[43.7379,8.1456],[43.7254,8.1489],[43.7129,8.1456],[43.7038,8.1364],[43.7004,8.1239]],[[43.8714,8.1809],[43.8748,8.1684],[43.8839,8.1592],[43.8964,8.1559],[43.9089,8.1592],[43.9181,8.1684],[43.9214,8.1809],[43.9181,8.1934],[43.9089,8.2026],[43.8964,8.2059],[43.8839,8.2026],[43.8748,8.1934]],[[43.7574,8.1809],[43.7608,8.1684],[43.7699,8.1592],[43.7824,8.1559],[43.7949,8.1592],[43.8041,8.1684],[43.8074,8.1809],[43.8041,8.1934],[43.7949,8.2026],[43.7824,8.2059],[43.7699,8.2026],[43.7608,8.1934]],[[43.7004,8.2379],[43.7038,8.2254],[43.7129,8.2162],[43.7254,8.2129],[43.7379,8.2162],[43.7471,8.2254],[43.7504,8.2379],[43.7471,8.2504],[43.7379,8.2595],[43.7254,8.2629],[43.7129,8.2595],[43.7038,8.2504]],[[43.8144,8.2379],[43.8178,8.2254],[43.8269,8.2162],[43.8394,8.2129],[43.8519,8.2162],[43.8611,8.2254],[43.8644,8.2379],[43.8611,8.2504],[43.8519,8.2595],[43.8394,8.2629],[43.8269,8.2595],[43.8178,8.2504]],[[43.7574,8.2949],[43.7608,8.2824],[43.7699,8.2732],[43.7824,8.2699],[43.7949,8.2732],[43.8041,8.2824],[43.8074,8.2949],[43.8041,8.3074],[43.7949,8.3165],[43.7824,8.3199],[43.7699,8.3165],[43.7608,8.3074]],[[43.7004,8.3519],[43.7038,8.3394],[43.7129,8.3302],[43.7254,8.3269],[43.7379,8.3302],[43.7471,8.3394],[43.7504,8.3519],[43.7471,8.3644],[43.7379,8.3735],[43.7254,8.3769],[43.7129,8.3735],[43.7038,8.3644]]]},{"ext":[[44.917,8.259],[44.917,7.764],[44.422,7.764]],"holes":[[[44.5442,7.79],[44.5567,7.7933],[44.5658,7.8025],[44.5692,7.815],[44.5658,7.8275],[44.5567,7.8366],[44.5442,7.84],[44.5317,7.8366],[44.5225,7.8275],[44.5192,7.815],[44.5225,7.8025],[44.5317,7.7933]],[[44.663,7.7933],[44.6755,7.79],[44.688,7.7933],[44.6971,7.8025],[44.7005,7.815],[44.6971,7.8275],[44.688,7.8366],[44.6755,7.84],[44.663,7.8366],[44.6538,7.8275],[44.6505,7.815],[44.6538,7.8025]],[[44.7943,7.7933],[44.8068,7.79],[44.8193,7.7933],[44.8284,7.8025],[44.8318,7.815],[44.8284,7.8275],[44.8193,7.8366],[44.8068,7.84],[44.7943,7.8366],[44.7851,7.8275],[44.7818,7.815],[44.7851,7.8025]],[[44.6098,7.8556],[44.6223,7.859],[44.6315,7.8681],[44.6348,7.8806],[44.6315,7.8931],[44.6223,7.9023],[44.6098,7.9056],[44.5973,7.9023],[44.5882,7.8931],[44.5848,7.8806],[44.5882,7.8681],[44.5973,7.859]],[[44.7286,7.859],[44.7411,7.8556],[44.7536,7.859],[44.7628,7.8681],[44.7661,7.8806],[44.7628,7.8931],[44.7536,7.9023],[44.7411,7.9056],[44.7286,7.9023],[44.7195,7.8931],[44.7161,7.8806],[44.7195,7.8681]],[[44.86,7.859],[44.8725,7.8556],[44.885,7.859],[44.8941,7.8681],[44.8975,7.8806],[44.8941,7.8931],[44.885,7.9023],[44.8725,7.9056],[44.86,7.9023],[44.8508,7.8931],[44.8475,7.8806],[44.8508,7.8681]],[[44.6755,7.9213],[44.688,7.9246],[44.6971,7.9338],[44.7005,7.9463],[44.6971,7.9588],[44.688,7.9679],[44.6755,7.9713],[44.663,7.9679],[44.6538,7.9588],[44.6505,7.9463],[44.6538,7.9338],[44.663,7.9246]],[[44.7943,7.9246],[44.8068,7.9213],[44.8193,7.9246],[44.8284,7.9338],[44.8318,7.9463],[44.8284,7.9588],[44.8193,7.9679],[44.8068,7.9713],[44.7943,7.9679],[44.7851,7.9588],[44.7818,7.9463],[44.7851,7.9338]],[[44.7286,7.9903],[44.7411,7.9869],[44.7536,7.9903],[44.7628,7.9994],[44.7661,8.0119],[44.7628,8.0244],[44.7536,8.0336],[44.7411,8.0369],[44.7286,8.0336],[44.7195,8.0244],[44.7161,8.0119],[44.7195,7.9994]],[[44.8725,7.9869],[44.885,7.9903],[44.8941,7.9994],[44.8975,8.0119],[44.8941,8.0244],[44.885,8.0336],[44.8725,8.0369],[44.86,8.0336],[44.8508,8.0244],[44.8475,8.0119],[44.8508,7.9994],[44.86,7.9903]],[[44.7943,8.0559],[44.8068,8.0526],[44.8193,8.0559],[44.8284,8.0651],[44.8318,8.0776],[44.8284,8.0901],[44.8193,8.0992],[44.8068,8.1026],[44.7943,8.0992],[44.7851,8.0901],[44.7818,8.0776],[44.7851,8.0651]],[[44.86,8.1216],[44.8725,8.1182],[44.885,8.1216],[44.8941,8.1307],[44.8975,8.1432],[44.8941,8.1557],[44.885,8.1649],[44.8725,8.1682],[44.86,8.1649],[44.8508,8.1557],[44.8475,8.1432],[44.8508,8.1307]]]},{"ext":[[44.927,8.259],[45.422,7.764],[44.927,7.764]],"holes":[[[45.0381,7.79],[45.0506,7.7933],[45.0598,7.8025],[45.0631,7.815],[45.0598,7.8275],[45.0506,7.8366],[45.0381,7.84],[45.0256,7.8366],[45.0165,7.8275],[45.0131,7.815],[45.0165,7.8025],[45.0256,7.7933]],[[45.1569,7.7933],[45.1694,7.79],[45.1819,7.7933],[45.1911,7.8025],[45.1944,7.815],[45.1911,7.8275],[45.1819,7.8366],[45.1694,7.84],[45.1569,7.8366],[45.1478,7.8275],[45.1444,7.815],[45.1478,7.8025]],[[45.2882,7.7933],[45.3007,7.79],[45.3132,7.7933],[45.3224,7.8025],[45.3257,7.815],[45.3224,7.8275],[45.3132,7.8366],[45.3007,7.84],[45.2882,7.8366],[45.2791,7.8275],[45.2757,7.815],[45.2791,7.8025]],[[44.9725,7.8556],[44.985,7.859],[44.9941,7.8681],[44.9975,7.8806],[44.9941,7.8931],[44.985,7.9023],[44.9725,7.9056],[44.96,7.9023],[44.9508,7.8931],[44.9475,7.8806],[44.9508,7.8681],[44.96,7.859]],[[45.0913,7.859],[45.1038,7.8556],[45.1163,7.859],[45.1254,7.8681],[45.1288,7.8806],[45.1254,7.8931],[45.1163,7.9023],[45.1038,7.9056],[45.0913,7.9023],[45.0821,7.8931],[45.0788,7.8806],[45.0821,7.8681]],[[45.2226,7.859],[45.2351,7.8556],[45.2476,7.859],[45.2567,7.8681],[45.2601,7.8806],[45.2567,7.8931],[45.2476,7.9023],[45.2351,7.9056],[45.2226,7.9023],[45.2134,7.8931],[45.2101,7.8806],[45.2134,7.8681]],[[45.0381,7.9213],[45.0506,7.9246],[45.0598,7.9338],[45.0631,7.9463],[45.0598,7.9588],[45.0506,7.9679],[45.0381,7.9713],[45.0256,7.9679],[45.0165,7.9588],[45.0131,7.9463],[45.0165,7.9338],[45.0256,7.9246]],[[45.1569,7.9246],[45.1694,7.9213],[45.1819,7.9246],[45.1911,7.9338],[45.1944,7.9463],[45.1911,7.9588],[45.1819,7.9679],[45.1694,7.9713],[45.1569,7.9679],[45.1478,7.9588],[45.1444,7.9463],[45.1478,7.9338]],[[44.96,7.9903],[44.9725,7.9869],[44.985,7.9903],[44.9941,7.9994],[44.9975,8.0119],[44.9941,8.0244],[44.985,8.0336],[44.9725,8.0369],[44.96,8.0336],[44.9508,8.0244],[44.9475,8.0119],[44.9508,7.9994]],[[45.1038,7.9869],[45.1163,7.9903],[45.1254,7.9994],[45.1288,8.0119],[45.1254,8.0244],[45.1163,8.0336],[45.1038,8.0369],[45.0913,8.0336],[45.0821,8.0244],[45.0788,8.0119],[45.0821,7.9994],[45.0913,7.9903]],[[45.0256,8.0559],[45.0381,8.0526],[45.0506,8.0559],[45.0598,8.0651],[45.0631,8.0776],[45.0598,8.0901],[45.0506,8.0992],[45.0381,8.1026],[45.0256,8.0992],[45.0165,8.0901],[45.0131,8.0776],[45.0165,8.0651]],[[44.96,8.1216],[44.9725,8.1182],[44.985,8.1216],[44.9941,8.1307],[44.9975,8.1432],[44.9941,8.1557],[44.985,8.1649],[44.9725,8.1682],[44.96,8.1649],[44.9508,8.1557],[44.9475,8.1432],[44.9508,8.1307]]]},{"ext":[[48.634,8.259],[48.634,7.764],[48.139,7.764]],"holes":[[[48.2608,7.79],[48.2733,7.7933],[48.2825,7.8025],[48.2858,7.815],[48.2825,7.8275],[48.2733,7.8366],[48.2608,7.84],[48.2483,7.8366],[48.2392,7.8275],[48.2358,7.815],[48.2392,7.8025],[48.2483,7.7933]],[[48.3796,7.7933],[48.3921,7.79],[48.4046,7.7933],[48.4138,7.8025],[48.4171,7.815],[48.4138,7.8275],[48.4046,7.8366],[48.3921,7.84],[48.3796,7.8366],[48.3705,7.8275],[48.3671,7.815],[48.3705,7.8025]],[[48.5109,7.7933],[48.5234,7.79],[48.5359,7.7933],[48.5451,7.8025],[48.5484,7.815],[48.5451,7.8275],[48.5359,7.8366],[48.5234,7.84],[48.5109,7.8366],[48.5018,7.8275],[48.4984,7.815],[48.5018,7.8025]],[[48.3265,7.8556],[48.339,7.859],[48.3481,7.8681],[48.3515,7.8806],[48.3481,7.8931],[48.339,7.9023],[48.3265,7.9056],[48.314,7.9023],[48.3048,7.8931],[48.3015,7.8806],[48.3048,7.8681],[48.314,7.859]],[[48.4453,7.859],[48.4578,7.8556],[48.4703,7.859],[48.4794,7.8681],[48.4828,7.8806],[48.4794,7.8931],[48.4703,7.9023],[48.4578,7.9056],[48.4453,7.9023],[48.4361,7.8931],[48.4328,7.8806],[48.4361,7.8681]],[[48.5766,7.859],[48.5891,7.8556],[48.6016,7.859],[48.6107,7.8681],[48.6141,7.8806],[48.6107,7.8931],[48.6016,7.9023],[48.5891,7.9056],[48.5766,7.9023],[48.5674,7.8931],[48.5641,7.8806],[48.5674,7.8681]],[[48.3921,7.9213],[48.4046,7.9246],[48.4138,7.9338],[48.4171,7.9463],[48.4138,7.9588],[48.4046,7.9679],[48.3921,7.9713],[48.3796,7.9679],[48.3705,7.9588],[48.3671,7.9463],[48.3705,7.9338],[48.3796,7.9246]],[[48.5109,7.9246],[48.5234,7.9213],[48.5359,7.9246],[48.5451,7.9338],[48.5484,7.9463],[48.5451,7.9588],[48.5359,7.9679],[48.5234,7.9713],[48.5109,7.9679],[48.5018,7.9588],[48.4984,7.9463],[48.5018,7.9338]],[[48.4453,7.9903],[48.4578,7.9869],[48.4703,7.9903],[48.4794,7.9994],[48.4828,8.0119],[48.4794,8.0244],[48.4703,8.0336],[48.4578,8.0369],[48.4453,8.0336],[48.4361,8.0244],[48.4328,8.0119],[48.4361,7.9994]],[[48.5891,7.9869],[48.6016,7.9903],[48.6107,7.9994],[48.6141,8.0119],[48.6107,8.0244],[48.6016,8.0336],[48.5891,8.0369],[48.5766,8.0336],[48.5674,8.0244],[48.5641,8.0119],[48.5674,7.9994],[48.5766,7.9903]],[[48.5109,8.0559],[48.5234,8.0526],[48.5359,8.0559],[48.5451,8.0651],[48.5484,8.0776],[48.5451,8.0901],[48.5359,8.0992],[48.5234,8.1026],[48.5109,8.0992],[48.5018,8.0901],[48.4984,8.0776],[48.5018,8.0651]],[[48.5766,8.1216],[48.5891,8.1182],[48.6016,8.1216],[48.6107,8.1307],[48.6141,8.1432],[48.6107,8.1557],[48.6016,8.1649],[48.5891,8.1682],[48.5766,8.1649],[48.5674,8.1557],[48.5641,8.1432],[48.5674,8.1307]]]},{"ext":[[48.644,8.259],[49.139,7.764],[48.644,7.764]],"holes":[[[48.7548,7.79],[48.7673,7.7933],[48.7764,7.8025],[48.7798,7.815],[48.7764,7.8275],[48.7673,7.8366],[48.7548,7.84],[48.7423,7.8366],[48.7331,7.8275],[48.7298,7.815],[48.7331,7.8025],[48.7423,7.7933]],[[48.8736,7.7933],[48.8861,7.79],[48.8986,7.7933],[48.9077,7.8025],[48.9111,7.815],[48.9077,7.8275],[48.8986,7.8366],[48.8861,7.84],[48.8736,7.8366],[48.8644,7.8275],[48.8611,7.815],[48.8644,7.8025]],[[49.0049,7.7933],[49.0174,7.79],[49.0299,7.7933],[49.039,7.8025],[49.0424,7.815],[49.039,7.8275],[49.0299,7.8366],[49.0174,7.84],[49.0049,7.8366],[48.9957,7.8275],[48.9924,7.815],[48.9957,7.8025]],[[48.6891,7.8556],[48.7016,7.859],[48.7107,7.8681],[48.7141,7.8806],[48.7107,7.8931],[48.7016,7.9023],[48.6891,7.9056],[48.6766,7.9023],[48.6674,7.8931],[48.6641,7.8806],[48.6674,7.8681],[48.6766,7.859]],[[48.8079,7.859],[48.8204,7.8556],[48.8329,7.859],[48.8421,7.8681],[48.8454,7.8806],[48.8421,7.8931],[48.8329,7.9023],[48.8204,7.9056],[48.8079,7.9023],[48.7988,7.8931],[48.7954,7.8806],[48.7988,7.8681]],[[48.9392,7.859],[48.9517,7.8556],[48.9642,7.859],[48.9734,7.8681],[48.9767,7.8806],[48.9734,7.8931],[48.9642,7.9023],[48.9517,7.9056],[48.9392,7.9023],[48.9301,7.8931],[48.9267,7.8806],[48.9301,7.8681]],[[48.7548,7.9213],[48.7673,7.9246],[48.7764,7.9338],[48.7798,7.9463],[48.7764,7.9588],[48.7673,7.9679],[48.7548,7.9713],[48.7423,7.9679],[48.7331,7.9588],[48.7298,7.9463],[48.7331,7.9338],[48.7423,7.9246]],[[48.8736,7.9246],[48.8861,7.9213],[48.8986,7.9246],[48.9077,7.9338],[48.9111,7.9463],[48.9077,7.9588],[48.8986,7.9679],[48.8861,7.9713],[48.8736,7.9679],[48.8644,7.9588],[48.8611,7.9463],[48.8644,7.9338]],[[48.6766,7.9903],[48.6891,7.9869],[48.7016,7.9903],[48.7107,7.9994],[48.7141,8.0119],[48.7107,8.0244],[48.7016,8.0336],[48.6891,8.0369],[48.6766,8.0336],[48.6674,8.0244],[48.6641,8.0119],[48.6674,7.9994]],[[48.8204,7.9869],[48.8329,7.9903],[48.8421,7.9994],[48.8454,8.0119],[48.8421,8.0244],[48.8329,8.0336],[48.8204,8.0369],[48.8079,8.0336],[48.7988,8.0244],[48.7954,8.0119],[48.7988,7.9994],[48.8079,7.9903]],[[48.7423,8.0559],[48.7548,8.0526],[48.7673,8.0559],[48.7764,8.0651],[48.7798,8.0776],[48.7764,8.0901],[48.7673,8.0992],[48.7548,8.1026],[48.7423,8.0992],[48.7331,8.0901],[48.7298,8.0776],[48.7331,8.0651]],[[48.6766,8.1216],[48.6891,8.1182],[48.7016,8.1216],[48.7107,8.1307],[48.7141,8.1432],[48.7107,8.1557],[48.7016,8.1649],[48.6891,8.1682],[48.6766,8.1649],[48.6674,8.1557],[48.6641,8.1432],[48.6674,8.1307]]]},{"ext":[[49.634,8.259],[49.634,7.764],[49.139,7.764]],"holes":[[[49.2608,7.79],[49.2733,7.7933],[49.2825,7.8025],[49.2858,7.815],[49.2825,7.8275],[49.2733,7.8366],[49.2608,7.84],[49.2483,7.8366],[49.2392,7.8275],[49.2358,7.815],[49.2392,7.8025],[49.2483,7.7933]],[[49.3796,7.7933],[49.3921,7.79],[49.4046,7.7933],[49.4138,7.8025],[49.4171,7.815],[49.4138,7.8275],[49.4046,7.8366],[49.3921,7.84],[49.3796,7.8366],[49.3705,7.8275],[49.3671,7.815],[49.3705,7.8025]],[[49.5109,7.7933],[49.5234,7.79],[49.5359,7.7933],[49.5451,7.8025],[49.5484,7.815],[49.5451,7.8275],[49.5359,7.8366],[49.5234,7.84],[49.5109,7.8366],[49.5018,7.8275],[49.4984,7.815],[49.5018,7.8025]],[[49.3265,7.8556],[49.339,7.859],[49.3481,7.8681],[49.3515,7.8806],[49.3481,7.8931],[49.339,7.9023],[49.3265,7.9056],[49.314,7.9023],[49.3048,7.8931],[49.3015,7.8806],[49.3048,7.8681],[49.314,7.859]],[[49.4453,7.859],[49.4578,7.8556],[49.4703,7.859],[49.4794,7.8681],[49.4828,7.8806],[49.4794,7.8931],[49.4703,7.9023],[49.4578,7.9056],[49.4453,7.9023],[49.4361,7.8931],[49.4328,7.8806],[49.4361,7.8681]],[[49.5766,7.859],[49.5891,7.8556],[49.6016,7.859],[49.6107,7.8681],[49.6141,7.8806],[49.6107,7.8931],[49.6016,7.9023],[49.5891,7.9056],[49.5766,7.9023],[49.5674,7.8931],[49.5641,7.8806],[49.5674,7.8681]],[[49.3921,7.9213],[49.4046,7.9246],[49.4138,7.9338],[49.4171,7.9463],[49.4138,7.9588],[49.4046,7.9679],[49.3921,7.9713],[49.3796,7.9679],[49.3705,7.9588],[49.3671,7.9463],[49.3705,7.9338],[49.3796,7.9246]],[[49.5109,7.9246],[49.5234,7.9213],[49.5359,7.9246],[49.5451,7.9338],[49.5484,7.9463],[49.5451,7.9588],[49.5359,7.9679],[49.5234,7.9713],[49.5109,7.9679],[49.5018,7.9588],[49.4984,7.9463],[49.5018,7.9338]],[[49.4453,7.9903],[49.4578,7.9869],[49.4703,7.9903],[49.4794,7.9994],[49.4828,8.0119],[49.4794,8.0244],[49.4703,8.0336],[49.4578,8.0369],[49.4453,8.0336],[49.4361,8.0244],[49.4328,8.0119],[49.4361,7.9994]],[[49.5891,7.9869],[49.6016,7.9903],[49.6107,7.9994],[49.6141,8.0119],[49.6107,8.0244],[49.6016,8.0336],[49.5891,8.0369],[49.5766,8.0336],[49.5674,8.0244],[49.5641,8.0119],[49.5674,7.9994],[49.5766,7.9903]],[[49.5109,8.0559],[49.5234,8.0526],[49.5359,8.0559],[49.5451,8.0651],[49.5484,8.0776],[49.5451,8.0901],[49.5359,8.0992],[49.5234,8.1026],[49.5109,8.0992],[49.5018,8.0901],[49.4984,8.0776],[49.5018,8.0651]],[[49.5766,8.1216],[49.5891,8.1182],[49.6016,8.1216],[49.6107,8.1307],[49.6141,8.1432],[49.6107,8.1557],[49.6016,8.1649],[49.5891,8.1682],[49.5766,8.1649],[49.5674,8.1557],[49.5641,8.1432],[49.5674,8.1307]]]},{"ext":[[49.644,8.259],[50.139,7.764],[49.644,7.764]],"holes":[[[49.7548,7.79],[49.7673,7.7933],[49.7764,7.8025],[49.7798,7.815],[49.7764,7.8275],[49.7673,7.8366],[49.7548,7.84],[49.7423,7.8366],[49.7331,7.8275],[49.7298,7.815],[49.7331,7.8025],[49.7423,7.7933]],[[49.8736,7.7933],[49.8861,7.79],[49.8986,7.7933],[49.9077,7.8025],[49.9111,7.815],[49.9077,7.8275],[49.8986,7.8366],[49.8861,7.84],[49.8736,7.8366],[49.8644,7.8275],[49.8611,7.815],[49.8644,7.8025]],[[50.0049,7.7933],[50.0174,7.79],[50.0299,7.7933],[50.039,7.8025],[50.0424,7.815],[50.039,7.8275],[50.0299,7.8366],[50.0174,7.84],[50.0049,7.8366],[49.9957,7.8275],[49.9924,7.815],[49.9957,7.8025]],[[49.6891,7.8556],[49.7016,7.859],[49.7107,7.8681],[49.7141,7.8806],[49.7107,7.8931],[49.7016,7.9023],[49.6891,7.9056],[49.6766,7.9023],[49.6674,7.8931],[49.6641,7.8806],[49.6674,7.8681],[49.6766,7.859]],[[49.8079,7.859],[49.8204,7.8556],[49.8329,7.859],[49.8421,7.8681],[49.8454,7.8806],[49.8421,7.8931],[49.8329,7.9023],[49.8204,7.9056],[49.8079,7.9023],[49.7988,7.8931],[49.7954,7.8806],[49.7988,7.8681]],[[49.9392,7.859],[49.9517,7.8556],[49.9642,7.859],[49.9734,7.8681],[49.9767,7.8806],[49.9734,7.8931],[49.9642,7.9023],[49.9517,7.9056],[49.9392,7.9023],[49.9301,7.8931],[49.9267,7.8806],[49.9301,7.8681]],[[49.7548,7.9213],[49.7673,7.9246],[49.7764,7.9338],[49.7798,7.9463],[49.7764,7.9588],[49.7673,7.9679],[49.7548,7.9713],[49.7423,7.9679],[49.7331,7.9588],[49.7298,7.9463],[49.7331,7.9338],[49.7423,7.9246]],[[49.8736,7.9246],[49.8861,7.9213],[49.8986,7.9246],[49.9077,7.9338],[49.9111,7.9463],[49.9077,7.9588],[49.8986,7.9679],[49.8861,7.9713],[49.8736,7.9679],[49.8644,7.9588],[49.8611,7.9463],[49.8644,7.9338]],[[49.6766,7.9903],[49.6891,7.9869],[49.7016,7.9903],[49.7107,7.9994],[49.7141,8.0119],[49.7107,8.0244],[49.7016,8.0336],[49.6891,8.0369],[49.6766,8.0336],[49.6674,8.0244],[49.6641,8.0119],[49.6674,7.9994]],[[49.8204,7.9869],[49.8329,7.9903],[49.8421,7.9994],[49.8454,8.0119],[49.8421,8.0244],[49.8329,8.0336],[49.8204,8.0369],[49.8079,8.0336],[49.7988,8.0244],[49.7954,8.0119],[49.7988,7.9994],[49.8079,7.9903]],[[49.7423,8.0559],[49.7548,8.0526],[49.7673,8.0559],[49.7764,8.0651],[49.7798,8.0776],[49.7764,8.0901],[49.7673,8.0992],[49.7548,8.1026],[49.7423,8.0992],[49.7331,8.0901],[49.7298,8.0776],[49.7331,8.0651]],[[49.6766,8.1216],[49.6891,8.1182],[49.7016,8.1216],[49.7107,8.1307],[49.7141,8.1432],[49.7107,8.1557],[49.7016,8.1649],[49.6891,8.1682],[49.6766,8.1649],[49.6674,8.1557],[49.6641,8.1432],[49.6674,8.1307]]]},{"ext":[[50.634,8.259],[50.634,7.764],[50.139,7.764]],"holes":[[[50.2608,7.79],[50.2733,7.7933],[50.2825,7.8025],[50.2858,7.815],[50.2825,7.8275],[50.2733,7.8366],[50.2608,7.84],[50.2483,7.8366],[50.2392,7.8275],[50.2358,7.815],[50.2392,7.8025],[50.2483,7.7933]],[[50.3796,7.7933],[50.3921,7.79],[50.4046,7.7933],[50.4138,7.8025],[50.4171,7.815],[50.4138,7.8275],[50.4046,7.8366],[50.3921,7.84],[50.3796,7.8366],[50.3705,7.8275],[50.3671,7.815],[50.3705,7.8025]],[[50.5109,7.7933],[50.5234,7.79],[50.5359,7.7933],[50.5451,7.8025],[50.5484,7.815],[50.5451,7.8275],[50.5359,7.8366],[50.5234,7.84],[50.5109,7.8366],[50.5018,7.8275],[50.4984,7.815],[50.5018,7.8025]],[[50.3265,7.8556],[50.339,7.859],[50.3481,7.8681],[50.3515,7.8806],[50.3481,7.8931],[50.339,7.9023],[50.3265,7.9056],[50.314,7.9023],[50.3048,7.8931],[50.3015,7.8806],[50.3048,7.8681],[50.314,7.859]],[[50.4453,7.859],[50.4578,7.8556],[50.4703,7.859],[50.4794,7.8681],[50.4828,7.8806],[50.4794,7.8931],[50.4703,7.9023],[50.4578,7.9056],[50.4453,7.9023],[50.4361,7.8931],[50.4328,7.8806],[50.4361,7.8681]],[[50.5766,7.859],[50.5891,7.8556],[50.6016,7.859],[50.6107,7.8681],[50.6141,7.8806],[50.6107,7.8931],[50.6016,7.9023],[50.5891,7.9056],[50.5766,7.9023],[50.5674,7.8931],[50.5641,7.8806],[50.5674,7.8681]],[[50.3921,7.9213],[50.4046,7.9246],[50.4138,7.9338],[50.4171,7.9463],[50.4138,7.9588],[50.4046,7.9679],[50.3921,7.9713],[50.3796,7.9679],[50.3705,7.9588],[50.3671,7.9463],[50.3705,7.9338],[50.3796,7.9246]],[[50.5109,7.9246],[50.5234,7.9213],[50.5359,7.9246],[50.5451,7.9338],[50.5484,7.9463],[50.5451,7.9588],[50.5359,7.9679],[50.5234,7.9713],[50.5109,7.9679],[50.5018,7.9588],[50.4984,7.9463],[50.5018,7.9338]],[[50.4453,7.9903],[50.4578,7.9869],[50.4703,7.9903],[50.4794,7.9994],[50.4828,8.0119],[50.4794,8.0244],[50.4703,8.0336],[50.4578,8.0369],[50.4453,8.0336],[50.4361,8.0244],[50.4328,8.0119],[50.4361,7.9994]],[[50.5891,7.9869],[50.6016,7.9903],[50.6107,7.9994],[50.6141,8.0119],[50.6107,8.0244],[50.6016,8.0336],[50.5891,8.0369],[50.5766,8.0336],[50.5674,8.0244],[50.5641,8.0119],[50.5674,7.9994],[50.5766,7.9903]],[[50.5109,8.0559],[50.5234,8.0526],[50.5359,8.0559],[50.5451,8.0651],[50.5484,8.0776],[50.5451,8.0901],[50.5359,8.0992],[50.5234,8.1026],[50.5109,8.0992],[50.5018,8.0901],[50.4984,8.0776],[50.5018,8.0651]],[[50.5766,8.1216],[50.5891,8.1182],[50.6016,8.1216],[50.6107,8.1307],[50.6141,8.1432],[50.6107,8.1557],[50.6016,8.1649],[50.5891,8.1682],[50.5766,8.1649],[50.5674,8.1557],[50.5641,8.1432],[50.5674,8.1307]]]},{"ext":[[50.644,8.259],[51.139,7.764],[50.644,7.764]],"holes":[[[50.7548,7.79],[50.7673,7.7933],[50.7764,7.8025],[50.7798,7.815],[50.7764,7.8275],[50.7673,7.8366],[50.7548,7.84],[50.7423,7.8366],[50.7331,7.8275],[50.7298,7.815],[50.7331,7.8025],[50.7423,7.7933]],[[50.8736,7.7933],[50.8861,7.79],[50.8986,7.7933],[50.9077,7.8025],[50.9111,7.815],[50.9077,7.8275],[50.8986,7.8366],[50.8861,7.84],[50.8736,7.8366],[50.8644,7.8275],[50.8611,7.815],[50.8644,7.8025]],[[51.0049,7.7933],[51.0174,7.79],[51.0299,7.7933],[51.039,7.8025],[51.0424,7.815],[51.039,7.8275],[51.0299,7.8366],[51.0174,7.84],[51.0049,7.8366],[50.9957,7.8275],[50.9924,7.815],[50.9957,7.8025]],[[50.6891,7.8556],[50.7016,7.859],[50.7107,7.8681],[50.7141,7.8806],[50.7107,7.8931],[50.7016,7.9023],[50.6891,7.9056],[50.6766,7.9023],[50.6674,7.8931],[50.6641,7.8806],[50.6674,7.8681],[50.6766,7.859]],[[50.8079,7.859],[50.8204,7.8556],[50.8329,7.859],[50.8421,7.8681],[50.8454,7.8806],[50.8421,7.8931],[50.8329,7.9023],[50.8204,7.9056],[50.8079,7.9023],[50.7988,7.8931],[50.7954,7.8806],[50.7988,7.8681]],[[50.9392,7.859],[50.9517,7.8556],[50.9642,7.859],[50.9734,7.8681],[50.9767,7.8806],[50.9734,7.8931],[50.9642,7.9023],[50.9517,7.9056],[50.9392,7.9023],[50.9301,7.8931],[50.9267,7.8806],[50.9301,7.8681]],[[50.7548,7.9213],[50.7673,7.9246],[50.7764,7.9338],[50.7798,7.9463],[50.7764,7.9588],[50.7673,7.9679],[50.7548,7.9713],[50.7423,7.9679],[50.7331,7.9588],[50.7298,7.9463],[50.7331,7.9338],[50.7423,7.9246]],[[50.8736,7.9246],[50.8861,7.9213],[50.8986,7.9246],[50.9077,7.9338],[50.9111,7.9463],[50.9077,7.9588],[50.8986,7.9679],[50.8861,7.9713],[50.8736,7.9679],[50.8644,7.9588],[50.8611,7.9463],[50.8644,7.9338]],[[50.6766,7.9903],[50.6891,7.9869],[50.7016,7.9903],[50.7107,7.9994],[50.7141,8.0119],[50.7107,8.0244],[50.7016,8.0336],[50.6891,8.0369],[50.6766,8.0336],[50.6674,8.0244],[50.6641,8.0119],[50.6674,7.9994]],[[50.8204,7.9869],[50.8329,7.9903],[50.8421,7.9994],[50.8454,8.0119],[50.8421,8.0244],[50.8329,8.0336],[50.8204,8.0369],[50.8079,8.0336],[50.7988,8.0244],[50.7954,8.0119],[50.7988,7.9994],[50.8079,7.9903]],[[50.7423,8.0559],[50.7548,8.0526],[50.7673,8.0559],[50.7764,8.0651],[50.7798,8.0776],[50.7764,8.0901],[50.7673,8.0992],[50.7548,8.1026],[50.7423,8.0992],[50.7331,8.0901],[50.7298,8.0776],[50.7331,8.0651]],[[50.6766,8.1216],[50.6891,8.1182],[50.7016,8.1216],[50.7107,8.1307],[50.7141,8.1432],[50.7107,8.1557],[50.7016,8.1649],[50.6891,8.1682],[50.6766,8.1649],[50.6674,8.1557],[50.6641,8.1432],[50.6674,8.1307]]]},{"ext":[[64.846,8.759],[64.846,7.764],[63.851,7.764]],"holes":[[[64.1273,7.8264],[64.1364,7.8173],[64.1489,7.8139],[64.1614,7.8173],[64.1706,7.8264],[64.1739,7.8389],[64.1706,7.8514],[64.1614,7.8606],[64.1489,7.8639],[64.1364,7.8606],[64.1273,7.8514],[64.1239,7.8389]],[[64.0099,7.8389],[64.0133,7.8264],[64.0224,7.8173],[64.0349,7.8139],[64.0474,7.8173],[64.0566,7.8264],[64.0599,7.8389],[64.0566,7.8514],[64.0474,7.8606],[64.0349,7.8639],[64.0224,7.8606],[64.0133,7.8514]],[[64.4659,7.8389],[64.4692,7.8264],[64.4784,7.8173],[64.4909,7.8139],[64.5034,7.8173],[64.5125,7.8264],[64.5159,7.8389],[64.5125,7.8514],[64.5034,7.8606],[64.4909,7.8639],[64.4784,7.8606],[64.4692,7.8514]],[[64.2379,7.8389],[64.2413,7.8264],[64.2504,7.8173],[64.2629,7.8139],[64.2754,7.8173],[64.2846,7.8264],[64.2879,7.8389],[64.2846,7.8514],[64.2754,7.8606],[64.2629,7.8639],[64.2504,7.8606],[64.2413,7.8514]],[[64.3519,7.8389],[64.3553,7.8264],[64.3644,7.8173],[64.3769,7.8139],[64.3894,7.8173],[64.3986,7.8264],[64.4019,7.8389],[64.3986,7.8514],[64.3894,7.8606],[64.3769,7.8639],[64.3644,7.8606],[64.3553,7.8514]],[[64.0669,7.8959],[64.0703,7.8834],[64.0794,7.8743],[64.0919,7.8709],[64.1044,7.8743],[64.1136,7.8834],[64.1169,7.8959],[64.1136,7.9084],[64.1044,7.9176],[64.0919,7.9209],[64.0794,7.9176],[64.0703,7.9084]],[[64.4089,7.8959],[64.4123,7.8834],[64.4214,7.8743],[64.4339,7.8709],[64.4464,7.8743],[64.4556,7.8834],[64.4589,7.8959],[64.4556,7.9084],[64.4464,7.9176],[64.4339,7.9209],[64.4214,7.9176],[64.4123,7.9084]],[[64.1843,7.8834],[64.1934,7.8743],[64.2059,7.8709],[64.2184,7.8743],[64.2276,7.8834],[64.2309,7.8959],[64.2276,7.9084],[64.2184,7.9176],[64.2059,7.9209],[64.1934,7.9176],[64.1843,7.9084],[64.1809,7.8959]],[[64.2949,7.8959],[64.2983,7.8834],[64.3074,7.8743],[64.3199,7.8709],[64.3324,7.8743],[64.3416,7.8834],[64.3449,7.8959],[64.3416,7.9084],[64.3324,7.9176],[64.3199,7.9209],[64.3074,7.9176],[64.2983,7.9084]],[[64.4659,7.9529],[64.4692,7.9404],[64.4784,7.9313],[64.4909,7.9279],[64.5034,7.9313],[64.5125,7.9404],[64.5159,7.9529],[64.5125,7.9654],[64.5034,7.9746],[64.4909,7.9779],[64.4784,7.9746],[64.4692,7.9654]],[[64.3519,7.9529],[64.3553,7.9404],[64.3644,7.9313],[64.3769,7.9279],[64.3894,7.9313],[64.3986,7.9404],[64.4019,7.9529],[64.3986,7.9654],[64.3894,7.9746],[64.3769,7.9779],[64.3644,7.9746],[64.3553,7.9654]],[[64.2379,7.9529],[64.2413,7.9404],[64.2504,7.9313],[64.2629,7.9279],[64.2754,7.9313],[64.2846,7.9404],[64.2879,7.9529],[64.2846,7.9654],[64.2754,7.9746],[64.2629,7.9779],[64.2504,7.9746],[64.2413,7.9654]],[[64.1239,7.9529],[64.1273,7.9404],[64.1364,7.9313],[64.1489,7.9279],[64.1614,7.9313],[64.1706,7.9404],[64.1739,7.9529],[64.1706,7.9654],[64.1614,7.9746],[64.1489,7.9779],[64.1364,7.9746],[64.1273,7.9654]],[[64.2949,8.0099],[64.2983,7.9974],[64.3074,7.9883],[64.3199,7.9849],[64.3324,7.9883],[64.3416,7.9974],[64.3449,8.0099],[64.3416,8.0224],[64.3324,8.0316],[64.3199,8.0349],[64.3074,8.0316],[64.2983,8.0224]],[[64.5262,7.9974],[64.5354,7.9883],[64.5479,7.9849],[64.5604,7.9883],[64.5695,7.9974],[64.5729,8.0099],[64.5695,8.0224],[64.5604,8.0316],[64.5479,8.0349],[64.5354,8.0316],[64.5262,8.0224],[64.5229,8.0099]],[[64.1809,8.0099],[64.1843,7.9974],[64.1934,7.9883],[64.2059,7.9849],[64.2184,7.9883],[64.2276,7.9974],[64.2309,8.0099],[64.2276,8.0224],[64.2184,8.0316],[64.2059,8.0349],[64.1934,8.0316],[64.1843,8.0224]],[[64.4089,8.0099],[64.4123,7.9974],[64.4214,7.9883],[64.4339,7.9849],[64.4464,7.9883],[64.4556,7.9974],[64.4589,8.0099],[64.4556,8.0224],[64.4464,8.0316],[64.4339,8.0349],[64.4214,8.0316],[64.4123,8.0224]],[[64.4659,8.0669],[64.4692,8.0544],[64.4784,8.0453],[64.4909,8.0419],[64.5034,8.0453],[64.5125,8.0544],[64.5159,8.0669],[64.5125,8.0794],[64.5034,8.0886],[64.4909,8.0919],[64.4784,8.0886],[64.4692,8.0794]],[[64.3519,8.0669],[64.3553,8.0544],[64.3644,8.0453],[64.3769,8.0419],[64.3894,8.0453],[64.3986,8.0544],[64.4019,8.0669],[64.3986,8.0794],[64.3894,8.0886],[64.3769,8.0919],[64.3644,8.0886],[64.3553,8.0794]],[[64.2379,8.0669],[64.2413,8.0544],[64.2504,8.0453],[64.2629,8.0419],[64.2754,8.0453],[64.2846,8.0544],[64.2879,8.0669],[64.2846,8.0794],[64.2754,8.0886],[64.2629,8.0919],[64.2504,8.0886],[64.2413,8.0794]],[[64.4089,8.1239],[64.4123,8.1114],[64.4214,8.1023],[64.4339,8.0989],[64.4464,8.1023],[64.4556,8.1114],[64.4589,8.1239],[64.4556,8.1364],[64.4464,8.1456],[64.4339,8.1489],[64.4214,8.1456],[64.4123,8.1364]],[[64.2983,8.1114],[64.3074,8.1023],[64.3199,8.0989],[64.3324,8.1023],[64.3416,8.1114],[64.3449,8.1239],[64.3416,8.1364],[64.3324,8.1456],[64.3199,8.1489],[64.3074,8.1456],[64.2983,8.1364],[64.2949,8.1239]],[[64.4659,8.1809],[64.4692,8.1684],[64.4784,8.1592],[64.4909,8.1559],[64.5034,8.1592],[64.5125,8.1684],[64.5159,8.1809],[64.5125,8.1934],[64.5034,8.2026],[64.4909,8.2059],[64.4784,8.2026],[64.4692,8.1934]],[[64.3519,8.1809],[64.3553,8.1684],[64.3644,8.1592],[64.3769,8.1559],[64.3894,8.1592],[64.3986,8.1684],[64.4019,8.1809],[64.3986,8.1934],[64.3894,8.2026],[64.3769,8.2059],[64.3644,8.2026],[64.3553,8.1934]],[[64.4089,8.2379],[64.4123,8.2254],[64.4214,8.2162],[64.4339,8.2129],[64.4464,8.2162],[64.4556,8.2254],[64.4589,8.2379],[64.4556,8.2504],[64.4464,8.2595],[64.4339,8.2629],[64.4214,8.2595],[64.4123,8.2504]],[[64.5229,8.2379],[64.5262,8.2254],[64.5354,8.2162],[64.5479,8.2129],[64.5604,8.2162],[64.5695,8.2254],[64.5729,8.2379],[64.5695,8.2504],[64.5604,8.2595],[64.5479,8.2629],[64.5354,8.2595],[64.5262,8.2504]],[[64.4659,8.2949],[64.4692,8.2824],[64.4784,8.2732],[64.4909,8.2699],[64.5034,8.2732],[64.5125,8.2824],[64.5159,8.2949],[64.5125,8.3074],[64.5034,8.3165],[64.4909,8.3199],[64.4784,8.3165],[64.4692,8.3074]],[[64.5229,8.3519],[64.5262,8.3394],[64.5354,8.3302],[64.5479,8.3269],[64.5604,8.3302],[64.5695,8.3394],[64.5729,8.3519],[64.5695,8.3644],[64.5604,8.3735],[64.5479,8.3769],[64.5354,8.3735],[64.5262,8.3644]],[[64.6972,7.8264],[64.7064,7.8173],[64.7189,7.8139],[64.7314,7.8173],[64.7405,7.8264],[64.7439,7.8389],[64.7405,7.8514],[64.7314,7.8606],[64.7189,7.8639],[64.7064,7.8606],[64.6972,7.8514],[64.6939,7.8389]],[[64.5799,7.8389],[64.5832,7.8264],[64.5924,7.8173],[64.6049,7.8139],[64.6174,7.8173],[64.6265,7.8264],[64.6299,7.8389],[64.6265,7.8514],[64.6174,7.8606],[64.6049,7.8639],[64.5924,7.8606],[64.5832,7.8514]],[[64.5229,7.8959],[64.5262,7.8834],[64.5354,7.8743],[64.5479,7.8709],[64.5604,7.8743],[64.5695,7.8834],[64.5729,7.8959],[64.5695,7.9084],[64.5604,7.9176],[64.5479,7.9209],[64.5354,7.9176],[64.5262,7.9084]],[[64.7509,7.8959],[64.7542,7.8834],[64.7634,7.8743],[64.7759,7.8709],[64.7884,7.8743],[64.7975,7.8834],[64.8009,7.8959],[64.7975,7.9084],[64.7884,7.9176],[64.7759,7.9209],[64.7634,7.9176],[64.7542,7.9084]],[[64.6369,7.8959],[64.6402,7.8834],[64.6494,7.8743],[64.6619,7.8709],[64.6744,7.8743],[64.6835,7.8834],[64.6869,7.8959],[64.6835,7.9084],[64.6744,7.9176],[64.6619,7.9209],[64.6494,7.9176],[64.6402,7.9084]],[[64.6939,7.9529],[64.6972,7.9404],[64.7064,7.9313],[64.7189,7.9279],[64.7314,7.9313],[64.7405,7.9404],[64.7439,7.9529],[64.7405,7.9654],[64.7314,7.9746],[64.7189,7.9779],[64.7064,7.9746],[64.6972,7.9654]],[[64.5799,7.9529],[64.5832,7.9404],[64.5924,7.9313],[64.6049,7.9279],[64.6174,7.9313],[64.6265,7.9404],[64.6299,7.9529],[64.6265,7.9654],[64.6174,7.9746],[64.6049,7.9779],[64.5924,7.9746],[64.5832,7.9654]],[[64.7542,7.9974],[64.7634,7.9883],[64.7759,7.9849],[64.7884,7.9883],[64.7975,7.9974],[64.8009,8.0099],[64.7975,8.0224],[64.7884,8.0316],[64.7759,8.0349],[64.7634,8.0316],[64.7542,8.0224],[64.7509,8.0099]],[[64.6369,8.0099],[64.6402,7.9974],[64.6494,7.9883],[64.6619,7.9849],[64.6744,7.9883],[64.6835,7.9974],[64.6869,8.0099],[64.6835,8.0224],[64.6744,8.0316],[64.6619,8.0349],[64.6494,8.0316],[64.6402,8.0224]],[[64.5799,8.0669],[64.5832,8.0544],[64.5924,8.0453],[64.6049,8.0419],[64.6174,8.0453],[64.6265,8.0544],[64.6299,8.0669],[64.6265,8.0794],[64.6174,8.0886],[64.6049,8.0919],[64.5924,8.0886],[64.5832,8.0794]],[[64.6939,8.0669],[64.6972,8.0544],[64.7064,8.0453],[64.7189,8.0419],[64.7314,8.0453],[64.7405,8.0544],[64.7439,8.0669],[64.7405,8.0794],[64.7314,8.0886],[64.7189,8.0919],[64.7064,8.0886],[64.6972,8.0794]],[[64.6369,8.1239],[64.6402,8.1114],[64.6494,8.1023],[64.6619,8.0989],[64.6744,8.1023],[64.6835,8.1114],[64.6869,8.1239],[64.6835,8.1364],[64.6744,8.1456],[64.6619,8.1489],[64.6494,8.1456],[64.6402,8.1364]],[[64.5229,8.1239],[64.5262,8.1114],[64.5354,8.1023],[64.5479,8.0989],[64.5604,8.1023],[64.5695,8.1114],[64.5729,8.1239],[64.5695,8.1364],[64.5604,8.1456],[64.5479,8.1489],[64.5354,8.1456],[64.5262,8.1364]],[[64.7509,8.1239],[64.7542,8.1114],[64.7634,8.1023],[64.7759,8.0989],[64.7884,8.1023],[64.7975,8.1114],[64.8009,8.1239],[64.7975,8.1364],[64.7884,8.1456],[64.7759,8.1489],[64.7634,8.1456],[64.7542,8.1364]],[[64.5832,8.1684],[64.5924,8.1592],[64.6049,8.1559],[64.6174,8.1592],[64.6265,8.1684],[64.6299,8.1809],[64.6265,8.1934],[64.6174,8.2026],[64.6049,8.2059],[64.5924,8.2026],[64.5832,8.1934],[64.5799,8.1809]],[[64.6939,8.1809],[64.6972,8.1684],[64.7064,8.1592],[64.7189,8.1559],[64.7314,8.1592],[64.7405,8.1684],[64.7439,8.1809],[64.7405,8.1934],[64.7314,8.2026],[64.7189,8.2059],[64.7064,8.2026],[64.6972,8.1934]],[[64.6369,8.2379],[64.6402,8.2254],[64.6494,8.2162],[64.6619,8.2129],[64.6744,8.2162],[64.6835,8.2254],[64.6869,8.2379],[64.6835,8.2504],[64.6744,8.2595],[64.6619,8.2629],[64.6494,8.2595],[64.6402,8.2504]],[[64.7509,8.2379],[64.7542,8.2254],[64.7634,8.2162],[64.7759,8.2129],[64.7884,8.2162],[64.7975,8.2254],[64.8009,8.2379],[64.7975,8.2504],[64.7884,8.2595],[64.7759,8.2629],[64.7634,8.2595],[64.7542,8.2504]],[[64.6939,8.2949],[64.6972,8.2824],[64.7064,8.2732],[64.7189,8.2699],[64.7314,8.2732],[64.7405,8.2824],[64.7439,8.2949],[64.7405,8.3074],[64.7314,8.3165],[64.7189,8.3199],[64.7064,8.3165],[64.6972,8.3074]],[[64.5799,8.2949],[64.5832,8.2824],[64.5924,8.2732],[64.6049,8.2699],[64.6174,8.2732],[64.6265,8.2824],[64.6299,8.2949],[64.6265,8.3074],[64.6174,8.3165],[64.6049,8.3199],[64.5924,8.3165],[64.5832,8.3074]],[[64.7509,8.3519],[64.7542,8.3394],[64.7634,8.3302],[64.7759,8.3269],[64.7884,8.3302],[64.7975,8.3394],[64.8009,8.3519],[64.7975,8.3644],[64.7884,8.3735],[64.7759,8.3769],[64.7634,8.3735],[64.7542,8.3644]],[[64.6402,8.3394],[64.6494,8.3302],[64.6619,8.3269],[64.6744,8.3302],[64.6835,8.3394],[64.6869,8.3519],[64.6835,8.3644],[64.6744,8.3735],[64.6619,8.3769],[64.6494,8.3735],[64.6402,8.3644],[64.6369,8.3519]],[[64.5799,8.4089],[64.5832,8.3964],[64.5924,8.3872],[64.6049,8.3839],[64.6174,8.3872],[64.6265,8.3964],[64.6299,8.4089],[64.6265,8.4214],[64.6174,8.4305],[64.6049,8.4339],[64.5924,8.4305],[64.5832,8.4214]],[[64.6939,8.4089],[64.6972,8.3964],[64.7064,8.3872],[64.7189,8.3839],[64.7314,8.3872],[64.7405,8.3964],[64.7439,8.4089],[64.7405,8.4214],[64.7314,8.4305],[64.7189,8.4339],[64.7064,8.4305],[64.6972,8.4214]],[[64.6369,8.4659],[64.6402,8.4534],[64.6494,8.4442],[64.6619,8.4409],[64.6744,8.4442],[64.6835,8.4534],[64.6869,8.4659],[64.6835,8.4784],[64.6744,8.4875],[64.6619,8.4909],[64.6494,8.4875],[64.6402,8.4784]],[[64.7509,8.4659],[64.7542,8.4534],[64.7634,8.4442],[64.7759,8.4409],[64.7884,8.4442],[64.7975,8.4534],[64.8009,8.4659],[64.7975,8.4784],[64.7884,8.4875],[64.7759,8.4909],[64.7634,8.4875],[64.7542,8.4784]],[[64.6939,8.5229],[64.6972,8.5104],[64.7064,8.5012],[64.7189,8.4979],[64.7314,8.5012],[64.7405,8.5104],[64.7439,8.5229],[64.7405,8.5354],[64.7314,8.5445],[64.7189,8.5479],[64.7064,8.5445],[64.6972,8.5354]],[[64.7509,8.5799],[64.7542,8.5674],[64.7634,8.5582],[64.7759,8.5549],[64.7884,8.5582],[64.7975,8.5674],[64.8009,8.5799],[64.7975,8.5924],[64.7884,8.6015],[64.7759,8.6049],[64.7634,8.6015],[64.7542,8.5924]]]},{"ext":[[64.856,8.759],[65.851,7.764],[64.856,7.764]],"holes":[[[64.9612,7.8264],[64.9704,7.8173],[64.9829,7.8139],[64.9954,7.8173],[65.0045,7.8264],[65.0079,7.8389],[65.0045,7.8514],[64.9954,7.8606],[64.9829,7.8639],[64.9704,7.8606],[64.9612,7.8514],[64.9579,7.8389]],[[65.0719,7.8389],[65.0752,7.8264],[65.0844,7.8173],[65.0969,7.8139],[65.1094,7.8173],[65.1185,7.8264],[65.1219,7.8389],[65.1185,7.8514],[65.1094,7.8606],[65.0969,7.8639],[65.0844,7.8606],[65.0752,7.8514]],[[65.1288,7.8959],[65.1322,7.8834],[65.1413,7.8743],[65.1538,7.8709],[65.1663,7.8743],[65.1755,7.8834],[65.1788,7.8959],[65.1755,7.9084],[65.1663,7.9176],[65.1538,7.9209],[65.1413,7.9176],[65.1322,7.9084]],[[65.0149,7.8959],[65.0182,7.8834],[65.0274,7.8743],[65.0399,7.8709],[65.0524,7.8743],[65.0615,7.8834],[65.0649,7.8959],[65.0615,7.9084],[65.0524,7.9176],[65.0399,7.9209],[65.0274,7.9176],[65.0182,7.9084]],[[64.9009,7.8959],[64.9042,7.8834],[64.9134,7.8743],[64.9259,7.8709],[64.9384,7.8743],[64.9475,7.8834],[64.9509,7.8959],[64.9475,7.9084],[64.9384,7.9176],[64.9259,7.9209],[64.9134,7.9176],[64.9042,7.9084]],[[65.0719,7.9529],[65.0752,7.9404],[65.0844,7.9313],[65.0969,7.9279],[65.1094,7.9313],[65.1185,7.9404],[65.1219,7.9529],[65.1185,7.9654],[65.1094,7.9746],[65.0969,7.9779],[65.0844,7.9746],[65.0752,7.9654]],[[64.9579,7.9529],[64.9612,7.9404],[64.9704,7.9313],[64.9829,7.9279],[64.9954,7.9313],[65.0045,7.9404],[65.0079,7.9529],[65.0045,7.9654],[64.9954,7.9746],[64.9829,7.9779],[64.9704,7.9746],[64.9612,7.9654]],[[64.9042,7.9974],[64.9134,7.9883],[64.9259,7.9849],[64.9384,7.9883],[64.9475,7.9974],[64.9509,8.0099],[64.9475,8.0224],[64.9384,8.0316],[64.9259,8.0349],[64.9134,8.0316],[64.9042,8.0224],[64.9009,8.0099]],[[65.1288,8.0099],[65.1322,7.9974],[65.1413,7.9883],[65.1538,7.9849],[65.1663,7.9883],[65.1755,7.9974],[65.1788,8.0099],[65.1755,8.0224],[65.1663,8.0316],[65.1538,8.0349],[65.1413,8.0316],[65.1322,8.0224]],[[65.0149,8.0099],[65.0182,7.9974],[65.0274,7.9883],[65.0399,7.9849],[65.0524,7.9883],[65.0615,7.9974],[65.0649,8.0099],[65.0615,8.0224],[65.0524,8.0316],[65.0399,8.0349],[65.0274,8.0316],[65.0182,8.0224]],[[65.0719,8.0669],[65.0752,8.0544],[65.0844,8.0453],[65.0969,8.0419],[65.1094,8.0453],[65.1185,8.0544],[65.1219,8.0669],[65.1185,8.0794],[65.1094,8.0886],[65.0969,8.0919],[65.0844,8.0886],[65.0752,8.0794]],[[64.9579,8.0669],[64.9612,8.0544],[64.9704,8.0453],[64.9829,8.0419],[64.9954,8.0453],[65.0045,8.0544],[65.0079,8.0669],[65.0045,8.0794],[64.9954,8.0886],[64.9829,8.0919],[64.9704,8.0886],[64.9612,8.0794]],[[64.9009,8.1239],[64.9042,8.1114],[64.9134,8.1023],[64.9259,8.0989],[64.9384,8.1023],[64.9475,8.1114],[64.9509,8.1239],[64.9475,8.1364],[64.9384,8.1456],[64.9259,8.1489],[64.9134,8.1456],[64.9042,8.1364]],[[65.0149,8.1239],[65.0182,8.1114],[65.0274,8.1023],[65.0399,8.0989],[65.0524,8.1023],[65.0615,8.1114],[65.0649,8.1239],[65.0615,8.1364],[65.0524,8.1456],[65.0399,8.1489],[65.0274,8.1456],[65.0182,8.1364]],[[65.0752,8.1684],[65.0844,8.1592],[65.0969,8.1559],[65.1094,8.1592],[65.1185,8.1684],[65.1219,8.1809],[65.1185,8.1934],[65.1094,8.2026],[65.0969,8.2059],[65.0844,8.2026],[65.0752,8.1934],[65.0719,8.1809]],[[64.9579,8.1809],[64.9612,8.1684],[64.9704,8.1592],[64.9829,8.1559],[64.9954,8.1592],[65.0045,8.1684],[65.0079,8.1809],[65.0045,8.1934],[64.9954,8.2026],[64.9829,8.2059],[64.9704,8.2026],[64.9612,8.1934]],[[65.0149,8.2379],[65.0182,8.2254],[65.0274,8.2162],[65.0399,8.2129],[65.0524,8.2162],[65.0615,8.2254],[65.0649,8.2379],[65.0615,8.2504],[65.0524,8.2595],[65.0399,8.2629],[65.0274,8.2595],[65.0182,8.2504]],[[64.9009,8.2379],[64.9042,8.2254],[64.9134,8.2162],[64.9259,8.2129],[64.9384,8.2162],[64.9475,8.2254],[64.9509,8.2379],[64.9475,8.2504],[64.9384,8.2595],[64.9259,8.2629],[64.9134,8.2595],[64.9042,8.2504]],[[64.9579,8.2949],[64.9612,8.2824],[64.9704,8.2732],[64.9829,8.2699],[64.9954,8.2732],[65.0045,8.2824],[65.0079,8.2949],[65.0045,8.3074],[64.9954,8.3165],[64.9829,8.3199],[64.9704,8.3165],[64.9612,8.3074]],[[65.0719,8.2949],[65.0752,8.2824],[65.0844,8.2732],[65.0969,8.2699],[65.1094,8.2732],[65.1185,8.2824],[65.1219,8.2949],[65.1185,8.3074],[65.1094,8.3165],[65.0969,8.3199],[65.0844,8.3165],[65.0752,8.3074]],[[65.0149,8.3519],[65.0182,8.3394],[65.0274,8.3302],[65.0399,8.3269],[65.0524,8.3302],[65.0615,8.3394],[65.0649,8.3519],[65.0615,8.3644],[65.0524,8.3735],[65.0399,8.3769],[65.0274,8.3735],[65.0182,8.3644]],[[64.9042,8.3394],[64.9134,8.3302],[64.9259,8.3269],[64.9384,8.3302],[64.9475,8.3394],[64.9509,8.3519],[64.9475,8.3644],[64.9384,8.3735],[64.9259,8.3769],[64.9134,8.3735],[64.9042,8.3644],[64.9009,8.3519]],[[64.9579,8.4089],[64.9612,8.3964],[64.9704,8.3872],[64.9829,8.3839],[64.9954,8.3872],[65.0045,8.3964],[65.0079,8.4089],[65.0045,8.4214],[64.9954,8.4305],[64.9829,8.4339],[64.9704,8.4305],[64.9612,8.4214]],[[65.0719,8.4089],[65.0752,8.3964],[65.0844,8.3872],[65.0969,8.3839],[65.1094,8.3872],[65.1185,8.3964],[65.1219,8.4089],[65.1185,8.4214],[65.1094,8.4305],[65.0969,8.4339],[65.0844,8.4305],[65.0752,8.4214]],[[65.0149,8.4659],[65.0182,8.4534],[65.0274,8.4442],[65.0399,8.4409],[65.0524,8.4442],[65.0615,8.4534],[65.0649,8.4659],[65.0615,8.4784],[65.0524,8.4875],[65.0399,8.4909],[65.0274,8.4875],[65.0182,8.4784]],[[64.9009,8.4659],[64.9042,8.4534],[64.9134,8.4442],[64.9259,8.4409],[64.9384,8.4442],[64.9475,8.4534],[64.9509,8.4659],[64.9475,8.4784],[64.9384,8.4875],[64.9259,8.4909],[64.9134,8.4875],[64.9042,8.4784]],[[64.9579,8.5229],[64.9612,8.5104],[64.9704,8.5012],[64.9829,8.4979],[64.9954,8.5012],[65.0045,8.5104],[65.0079,8.5229],[65.0045,8.5354],[64.9954,8.5445],[64.9829,8.5479],[64.9704,8.5445],[64.9612,8.5354]],[[64.9009,8.5799],[64.9042,8.5674],[64.9134,8.5582],[64.9259,8.5549],[64.9384,8.5582],[64.9475,8.5674],[64.9509,8.5799],[64.9475,8.5924],[64.9384,8.6015],[64.9259,8.6049],[64.9134,8.6015],[64.9042,8.5924]],[[65.6451,7.8264],[65.6543,7.8173],[65.6668,7.8139],[65.6793,7.8173],[65.6884,7.8264],[65.6918,7.8389],[65.6884,7.8514],[65.6793,7.8606],[65.6668,7.8639],[65.6543,7.8606],[65.6451,7.8514],[65.6418,7.8389]],[[65.1858,7.8389],[65.1892,7.8264],[65.1983,7.8173],[65.2108,7.8139],[65.2233,7.8173],[65.2325,7.8264],[65.2358,7.8389],[65.2325,7.8514],[65.2233,7.8606],[65.2108,7.8639],[65.1983,7.8606],[65.1892,7.8514]],[[65.4138,7.8389],[65.4172,7.8264],[65.4263,7.8173],[65.4388,7.8139],[65.4513,7.8173],[65.4605,7.8264],[65.4638,7.8389],[65.4605,7.8514],[65.4513,7.8606],[65.4388,7.8639],[65.4263,7.8606],[65.4172,7.8514]],[[65.2998,7.8389],[65.3032,7.8264],[65.3123,7.8173],[65.3248,7.8139],[65.3373,7.8173],[65.3465,7.8264],[65.3498,7.8389],[65.3465,7.8514],[65.3373,7.8606],[65.3248,7.8639],[65.3123,7.8606],[65.3032,7.8514]],[[65.5278,7.8389],[65.5312,7.8264],[65.5403,7.8173],[65.5528,7.8139],[65.5653,7.8173],[65.5745,7.8264],[65.5778,7.8389],[65.5745,7.8514],[65.5653,7.8606],[65.5528,7.8639],[65.5403,7.8606],[65.5312,7.8514]],[[65.2428,7.8959],[65.2462,7.8834],[65.2553,7.8743],[65.2678,7.8709],[65.2803,7.8743],[65.2895,7.8834],[65.2928,7.8959],[65.2895,7.9084],[65.2803,7.9176],[65.2678,7.9209],[65.2553,7.9176],[65.2462,7.9084]],[[65.3568,7.8959],[65.3602,7.8834],[65.3693,7.8743],[65.3818,7.8709],[65.3943,7.8743],[65.4035,7.8834],[65.4068,7.8959],[65.4035,7.9084],[65.3943,7.9176],[65.3818,7.9209],[65.3693,7.9176],[65.3602,7.9084]],[[65.4742,7.8834],[65.4833,7.8743],[65.4958,7.8709],[65.5083,7.8743],[65.5175,7.8834],[65.5208,7.8959],[65.5175,7.9084],[65.5083,7.9176],[65.4958,7.9209],[65.4833,7.9176],[65.4742,7.9084],[65.4708,7.8959]],[[65.5848,7.8959],[65.5882,7.8834],[65.5973,7.8743],[65.6098,7.8709],[65.6223,7.8743],[65.6315,7.8834],[65.6348,7.8959],[65.6315,7.9084],[65.6223,7.9176],[65.6098,7.9209],[65.5973,7.9176],[65.5882,7.9084]],[[65.4138,7.9529],[65.4172,7.9404],[65.4263,7.9313],[65.4388,7.9279],[65.4513,7.9313],[65.4605,7.9404],[65.4638,7.9529],[65.4605,7.9654],[65.4513,7.9746],[65.4388,7.9779],[65.4263,7.9746],[65.4172,7.9654]],[[65.1858,7.9529],[65.1892,7.9404],[65.1983,7.9313],[65.2108,7.9279],[65.2233,7.9313],[65.2325,7.9404],[65.2358,7.9529],[65.2325,7.9654],[65.2233,7.9746],[65.2108,7.9779],[65.1983,7.9746],[65.1892,7.9654]],[[65.5278,7.9529],[65.5312,7.9404],[65.5403,7.9313],[65.5528,7.9279],[65.5653,7.9313],[65.5745,7.9404],[65.5778,7.9529],[65.5745,7.9654],[65.5653,7.9746],[65.5528,7.9779],[65.5403,7.9746],[65.5312,7.9654]],[[65.2998,7.9529],[65.3032,7.9404],[65.3123,7.9313],[65.3248,7.9279],[65.3373,7.9313],[65.3465,7.9404],[65.3498,7.9529],[65.3465,7.9654],[65.3373,7.9746],[65.3248,7.9779],[65.3123,7.9746],[65.3032,7.9654]],[[65.4708,8.0099],[65.4742,7.9974],[65.4833,7.9883],[65.4958,7.9849],[65.5083,7.9883],[65.5175,7.9974],[65.5208,8.0099],[65.5175,8.0224],[65.5083,8.0316],[65.4958,8.0349],[65.4833,8.0316],[65.4742,8.0224]],[[65.2462,7.9974],[65.2553,7.9883],[65.2678,7.9849],[65.2803,7.9883],[65.2895,7.9974],[65.2928,8.0099],[65.2895,8.0224],[65.2803,8.0316],[65.2678,8.0349],[65.2553,8.0316],[65.2462,8.0224],[65.2428,8.0099]],[[65.3568,8.0099],[65.3602,7.9974],[65.3693,7.9883],[65.3818,7.9849],[65.3943,7.9883],[65.4035,7.9974],[65.4068,8.0099],[65.4035,8.0224],[65.3943,8.0316],[65.3818,8.0349],[65.3693,8.0316],[65.3602,8.0224]],[[65.2998,8.0669],[65.3032,8.0544],[65.3123,8.0453],[65.3248,8.0419],[65.3373,8.0453],[65.3465,8.0544],[65.3498,8.0669],[65.3465,8.0794],[65.3373,8.0886],[65.3248,8.0919],[65.3123,8.0886],[65.3032,8.0794]],[[65.4138,8.0669],[65.4172,8.0544],[65.4263,8.0453],[65.4388,8.0419],[65.4513,8.0453],[65.4605,8.0544],[65.4638,8.0669],[65.4605,8.0794],[65.4513,8.0886],[65.4388,8.0919],[65.4263,8.0886],[65.4172,8.0794]],[[65.1858,8.0669],[65.1892,8.0544],[65.1983,8.0453],[65.2108,8.0419],[65.2233,8.0453],[65.2325,8.0544],[65.2358,8.0669],[65.2325,8.0794],[65.2233,8.0886],[65.2108,8.0919],[65.1983,8.0886],[65.1892,8.0794]],[[65.3568,8.1239],[65.3602,8.1114],[65.3693,8.1023],[65.3818,8.0989],[65.3943,8.1023],[65.4035,8.1114],[65.4068,8.1239],[65.4035,8.1364],[65.3943,8.1456],[65.3818,8.1489],[65.3693,8.1456],[65.3602,8.1364]],[[65.2428,8.1239],[65.2462,8.1114],[65.2553,8.1023],[65.2678,8.0989],[65.2803,8.1023],[65.2895,8.1114],[65.2928,8.1239],[65.2895,8.1364],[65.2803,8.1456],[65.2678,8.1489],[65.2553,8.1456],[65.2462,8.1364]],[[65.1322,8.1114],[65.1413,8.1023],[65.1538,8.0989],[65.1663,8.1023],[65.1755,8.1114],[65.1788,8.1239],[65.1755,8.1364],[65.1663,8.1456],[65.1538,8.1489],[65.1413,8.1456],[65.1322,8.1364],[65.1288,8.1239]],[[65.2998,8.1809],[65.3032,8.1684],[65.3123,8.1592],[65.3248,8.1559],[65.3373,8.1592],[65.3465,8.1684],[65.3498,8.1809],[65.3465,8.1934],[65.3373,8.2026],[65.3248,8.2059],[65.3123,8.2026],[65.3032,8.1934]],[[65.1858,8.1809],[65.1892,8.1684],[65.1983,8.1592],[65.2108,8.1559],[65.2233,8.1592],[65.2325,8.1684],[65.2358,8.1809],[65.2325,8.1934],[65.2233,8.2026],[65.2108,8.2059],[65.1983,8.2026],[65.1892,8.1934]],[[65.1288,8.2379],[65.1322,8.2254],[65.1413,8.2162],[65.1538,8.2129],[65.1663,8.2162],[65.1755,8.2254],[65.1788,8.2379],[65.1755,8.2504],[65.1663,8.2595],[65.1538,8.2629],[65.1413,8.2595],[65.1322,8.2504]],[[65.2428,8.2379],[65.2462,8.2254],[65.2553,8.2162],[65.2678,8.2129],[65.2803,8.2162],[65.2895,8.2254],[65.2928,8.2379],[65.2895,8.2504],[65.2803,8.2595],[65.2678,8.2629],[65.2553,8.2595],[65.2462,8.2504]],[[65.1858,8.2949],[65.1892,8.2824],[65.1983,8.2732],[65.2108,8.2699],[65.2233,8.2732],[65.2325,8.2824],[65.2358,8.2949],[65.2325,8.3074],[65.2233,8.3165],[65.2108,8.3199],[65.1983,8.3165],[65.1892,8.3074]],[[65.1288,8.3519],[65.1322,8.3394],[65.1413,8.3302],[65.1538,8.3269],[65.1663,8.3302],[65.1755,8.3394],[65.1788,8.3519],[65.1755,8.3644],[65.1663,8.3735],[65.1538,8.3769],[65.1413,8.3735],[65.1322,8.3644]]]}],"rombos_inf":[{"ext":[[44.422,7.764],[43.422,6.764],[42.422,7.764]],"holes":[[[43.3725,6.8846],[43.3725,7.7139],[42.5432,7.7139]],[[43.4725,6.8846],[44.3017,7.7139],[43.4725,7.7139]]]},{"ext":[[45.422,7.764],[44.922,7.264],[44.422,7.764]],"holes":[[[44.8975,7.3243],[44.8975,7.7389],[44.4828,7.7389]],[[44.9475,7.3243],[45.3621,7.7389],[44.9475,7.7389]]]},{"ext":[[49.139,7.764],[48.639,7.264],[48.139,7.764]],"holes":[[[48.6141,7.3243],[48.6141,7.7389],[48.1995,7.7389]],[[48.6641,7.3243],[49.0787,7.7389],[48.6641,7.7389]]]},{"ext":[[50.139,7.764],[49.639,7.264],[49.139,7.764]],"holes":[[[49.6141,7.3243],[49.6141,7.7389],[49.1995,7.7389]],[[49.6641,7.3243],[50.0787,7.7389],[49.6641,7.7389]]]},{"ext":[[51.139,7.764],[50.639,7.264],[50.139,7.764]],"holes":[[[50.6141,7.3243],[50.6141,7.7389],[50.1995,7.7389]],[[50.6641,7.3243],[51.0787,7.7389],[50.6641,7.7389]]]},{"ext":[[65.851,7.764],[64.851,6.764],[63.851,7.764]],"holes":[[[64.8009,6.8846],[64.8009,7.7139],[63.9716,7.7139]],[[64.9009,6.8846],[65.7302,7.7139],[64.9009,7.7139]]]}]},"PT2R":[{"ext":[[2.5001,0.5679],[2.9975,1.0652],[2.9975,0.9541],[2.5206,0.4772],[2.5001,0.4794],[2.4796,0.4772],[2.0025,0.9543],[2.0025,1.0655]],"holes":[]},{"ext":[[1.9975,0.0],[1.0025,0.0],[1.0025,0.9446],[1.3977,1.3398],[1.0025,1.3398],[1.0025,1.8332],[1.9975,0.8382]],"holes":[]},{"ext":[[0.0604,1.8477],[0.2102,1.9975],[0.2936,1.9975],[0.0604,1.7643],[0.0604,1.64],[0.4179,1.9975],[0.5013,1.9975],[0.0604,1.5566],[0.0604,1.4591],[0.5988,1.9975],[0.6822,1.9975],[0.0255,1.3408],[0.1071,1.2592],[0.8454,1.9975],[0.9975,1.9975],[0.9975,1.9553],[0.4916,1.4495],[0.9975,0.9436],[0.9975,0.0],[0.0,0.0],[0.0,0.1001],[0.7213,0.1001],[0.0,0.8214],[0.0,1.9975],[0.0604,1.9975]],"holes":[[[0.7396,0.438],[0.7535,0.4212],[0.7702,0.4073],[0.7894,0.3969],[0.8107,0.3903],[0.8336,0.388],[0.8564,0.3903],[0.8777,0.3969],[0.8969,0.4073],[0.9137,0.4212],[0.9276,0.438],[0.938,0.4572],[0.9446,0.4785],[0.9469,0.5013],[0.9446,0.5242],[0.938,0.5455],[0.9276,0.5647],[0.9137,0.5814],[0.8969,0.5953],[0.8777,0.6058],[0.8564,0.6124],[0.8336,0.6146],[0.8107,0.6124],[0.7894,0.6058],[0.7702,0.5953],[0.7535,0.5814],[0.7396,0.5647],[0.7291,0.5455],[0.7225,0.5242],[0.7203,0.5013],[0.7225,0.4785],[0.7291,0.4572]]]},{"ext":[[1.4086,1.8258],[1.5803,1.9975],[1.8618,1.9975],[1.6901,1.8258],[1.9975,1.5184],[1.9975,1.2369],[1.953,1.2814],[1.8698,1.1982],[1.9975,1.0705],[1.9975,0.9593],[1.0025,1.9543],[1.0025,1.9975],[1.0705,1.9975],[1.832,1.236],[1.9152,1.3192]],"holes":[]},{"ext":[[0.9975,1.8342],[0.9975,1.3398],[0.7223,1.3398],[0.6127,1.4495]],"holes":[]},{"ext":[[1.0655,2.0025],[1.0025,2.0025],[1.0025,2.0655]],"holes":[]},{"ext":[[1.5853,2.0025],[1.9975,2.4147],[1.9975,2.1332],[1.8668,2.0025]],"holes":[]},{"ext":[[2.1961,2.6133],[2.0025,2.6133],[2.0025,2.6851],[2.2679,2.6851],[2.5001,2.9173],[2.7323,2.6851],[2.9975,2.6851],[2.9975,2.6133],[2.8041,2.6133],[2.9975,2.4199],[2.9975,2.1385],[2.5001,2.6359],[2.0025,2.1382],[2.0025,2.4197]],"holes":[]},{"ext":[[0.9975,2.2205],[0.8475,2.2205],[0.9975,2.0705],[0.9975,2.0025],[0.8504,2.0025],[0.9342,2.0863],[0.8526,2.1679],[0.6872,2.0025],[0.6038,2.0025],[0.8109,2.2096],[0.5102,2.5102],[0.9975,2.9975]],"holes":[]},{"ext":[[0.6972,2.1934],[0.5063,2.0025],[0.4229,2.0025],[0.6138,2.1934],[0.4036,2.4036],[0.4453,2.4453]],"holes":[]},{"ext":[[0.5029,2.2068],[0.2986,2.0025],[0.2152,2.0025],[0.4195,2.2068],[0.3131,2.3131],[0.3548,2.3548]],"holes":[]},{"ext":[[0.0604,2.0025],[0.0025,2.0025],[0.0604,2.0604]],"holes":[]},{"ext":[[1.121,3.0694],[1.1741,3.0613],[1.2287,3.0586],[1.2833,3.0613],[1.3364,3.0694],[1.3876,3.0826],[1.4367,3.1006],[1.4834,3.123],[1.5274,3.1498],[1.5686,3.1806],[1.6065,3.2151],[1.6409,3.253],[1.6718,3.2942],[1.6985,3.3382],[1.721,3.3849],[1.7389,3.434],[1.7522,3.4852],[1.7602,3.5382],[1.7631,3.5949],[1.5949,3.5949],[1.6461,3.6461],[1.7631,3.6461],[1.7583,3.7189],[1.7517,3.7517],[1.9975,3.9975],[1.9975,3.0061],[1.633,3.0061],[1.954,2.6851],[1.9975,2.6851],[1.9975,2.6133],[1.2402,2.6133],[1.633,2.2205],[1.0025,2.2205],[1.0025,3.0025],[1.08,3.08]],"holes":[]},{"ext":[[2.9975,3.9975],[2.9975,3.0061],[2.585,3.0061],[2.8977,3.3187],[2.1026,3.3187],[2.4152,3.0061],[2.0025,3.0061],[2.0025,3.9975]],"holes":[[[2.623,3.7434],[2.5973,3.7647],[2.5678,3.7808],[2.5352,3.7909],[2.5001,3.7944],[2.4651,3.7909],[2.4324,3.7808],[2.4029,3.7647],[2.3772,3.7434],[2.3559,3.7177],[2.3399,3.6882],[2.3297,3.6555],[2.3263,3.6205],[2.3297,3.5855],[2.3399,3.5528],[2.3559,3.5233],[2.3772,3.4976],[2.4029,3.4763],[2.4324,3.4602],[2.4651,3.4501],[2.5001,3.4466],[2.5352,3.4501],[2.5678,3.4602],[2.5973,3.4763],[2.623,3.4976],[2.6443,3.5233],[2.6604,3.5528],[2.6705,3.5855],[2.674,3.6205],[2.6705,3.6555],[2.6604,3.6882],[2.6443,3.7177]]]},{"ext":[[2.3996,0.3143],[2.425,0.2815],[2.4606,0.2601],[2.5001,0.253],[2.5397,0.2601],[2.5752,0.2815],[2.6006,0.3143],[2.6124,0.3527],[2.61,0.3928],[2.5937,0.4291],[2.9975,0.8329],[2.9975,0.0],[2.0025,0.0],[2.0025,0.8332],[2.4066,0.4291],[2.3902,0.3928],[2.3879,0.3527]],"holes":[]},{"ext":[[3.9975,0.0],[3.0025,0.0],[3.0025,0.8379],[3.9975,1.8329],[3.9975,1.3398],[3.6025,1.3398],[3.9975,0.9449]],"holes":[]},{"ext":[[4.9394,1.213],[4.9394,1.3229],[4.2649,1.9975],[4.3835,1.9975],[4.9394,1.4416],[4.9394,1.5362],[4.4781,1.9975],[4.584,1.9975],[4.9394,1.6421],[4.9394,1.7367],[4.6786,1.9975],[4.7917,1.9975],[4.9394,1.8498],[4.9394,1.9975],[5.0,1.9975],[5.0,0.7169],[4.3832,0.1001],[5.0,0.1001],[5.0,0.0],[4.0025,0.0],[4.0025,0.9433],[4.5086,1.4495],[4.0025,1.9556],[4.0025,1.9975],[4.155,1.9975]],"holes":[[[4.073,0.438],[4.0869,0.4212],[4.1037,0.4073],[4.1229,0.3969],[4.1442,0.3903],[4.167,0.388],[4.1898,0.3903],[4.2111,0.3969],[4.2303,0.4073],[4.2471,0.4212],[4.261,0.438],[4.2715,0.4572],[4.2781,0.4785],[4.2803,0.5013],[4.2781,0.5242],[4.2715,0.5455],[4.261,0.5647],[4.2471,0.5814],[4.2303,0.5953],[4.2111,0.6058],[4.1898,0.6124],[4.167,0.6146],[4.1442,0.6124],[4.1229,0.6058],[4.1037,0.5953],[4.0869,0.5814],[4.073,0.5647],[4.0626,0.5455],[4.056,0.5242],[4.0537,0.5013],[4.056,0.4785],[4.0626,0.4572]]]},{"ext":[[2.0025,1.5134],[2.5001,1.0157],[2.9975,1.5131],[2.9975,1.2316],[2.5001,0.7343],[2.0025,1.2319]],"holes":[]},{"ext":[[3.3102,1.8258],[3.1385,1.9975],[3.4199,1.9975],[3.5916,1.8258],[3.085,1.3192],[3.1682,1.236],[3.9298,1.9975],[3.9975,1.9975],[3.9975,1.954],[3.0025,0.9591],[3.0025,1.0702],[3.1305,1.1982],[3.0473,1.2814],[3.0025,1.2366],[3.0025,1.5181]],"holes":[]},{"ext":[[4.0025,1.3398],[4.0025,1.8345],[4.3875,1.4495],[4.2779,1.3398]],"holes":[]},{"ext":[[3.9348,2.0025],[3.9975,2.0652],[3.9975,2.0025]],"holes":[]},{"ext":[[3.0025,2.1335],[3.0025,2.4149],[3.4149,2.0025],[3.1335,2.0025]],"holes":[]},{"ext":[[4.8393,3.6883],[4.8292,3.6556],[4.8257,3.6205],[4.8292,3.5854],[4.8393,3.5527],[4.8554,3.5231],[4.8767,3.4973],[4.9025,3.476],[4.9321,3.4599],[4.9648,3.4498],[5.0,3.4463],[5.0,2.0025],[4.9394,2.0025],[4.9394,2.356],[4.6863,2.1029],[4.7867,2.0025],[4.6736,2.0025],[4.5732,2.1029],[4.9394,2.4691],[4.9394,2.5637],[4.4786,2.1029],[4.579,2.0025],[4.4731,2.0025],[4.3727,2.1029],[4.9394,2.6697],[4.9394,2.7643],[4.2781,2.1029],[4.3785,2.0025],[4.2599,2.0025],[4.1761,2.0863],[4.9394,2.8497],[4.9394,2.9596],[4.0662,2.0863],[4.15,2.0025],[4.0025,2.0025],[4.0025,2.0702],[4.1528,2.2205],[4.0025,2.2205],[4.0025,3.1123],[4.0387,3.1302],[4.0976,3.1696],[4.1501,3.2159],[4.1958,3.2682],[4.2342,3.3257],[4.2649,3.3877],[4.2873,3.4535],[4.3011,3.5221],[4.3059,3.5949],[4.0025,3.5949],[4.0025,3.6461],[4.3059,3.6461],[4.303,3.7028],[4.295,3.7558],[4.2818,3.807],[4.2638,3.8561],[4.2414,3.9029],[4.2146,3.9468],[4.1837,3.988],[4.1751,3.9975],[5.0,3.9975],[5.0,3.7947],[4.9648,3.7912],[4.9321,3.7811],[4.9025,3.765],[4.8767,3.7437],[4.8554,3.7179]],"holes":[]},{"ext":[[3.0025,2.6133],[3.0025,2.6851],[3.0463,2.6851],[3.3672,3.0061],[3.0025,3.0061],[3.0025,3.9975],[3.3679,3.9975],[3.3593,3.988],[3.3285,3.9468],[3.3017,3.9029],[3.2793,3.8561],[3.2613,3.807],[3.2481,3.7558],[3.24,3.7028],[3.2372,3.6461],[3.6699,3.6461],[3.6848,3.679],[3.7079,3.7035],[3.7375,3.7194],[3.7715,3.7251],[3.8055,3.7194],[3.8352,3.7035],[3.8582,3.679],[3.8732,3.6461],[3.9975,3.6461],[3.9975,3.5949],[3.8732,3.5949],[3.8582,3.562],[3.8352,3.5375],[3.8055,3.5216],[3.7715,3.5159],[3.7375,3.5216],[3.7079,3.5375],[3.6848,3.562],[3.6699,3.5949],[3.2372,3.5949],[3.2419,3.5221],[3.2558,3.4535],[3.2781,3.3877],[3.3089,3.3257],[3.3472,3.2682],[3.3929,3.2159],[3.4455,3.1696],[3.5044,3.1302],[3.568,3.0988],[3.6344,3.0765],[3.7025,3.0631],[3.7715,3.0586],[3.8406,3.0631],[3.9087,3.0765],[3.9751,3.0988],[3.9975,3.1099],[3.9975,2.2205],[3.3672,2.2205],[3.76,2.6133]],"holes":[]},{"ext":[[2.9975,4.669],[2.9892,4.669],[2.9975,4.6608],[2.9975,4.0025],[2.0025,4.0025],[2.4144,4.4144],[2.5001,4.3301],[2.8443,4.669],[2.669,4.669],[2.9975,4.9975]],"holes":[]},{"ext":[[3.9304,4.1584],[3.8792,4.1716],[3.8261,4.1797],[3.7715,4.1824],[3.7169,4.1797],[3.6639,4.1716],[3.6126,4.1584],[3.5635,4.1404],[3.5168,4.118],[3.4728,4.0912],[3.4316,4.0604],[3.3938,4.0259],[3.3725,4.0025],[3.0025,4.0025],[3.0025,4.6559],[3.3334,4.3301],[3.6776,4.669],[3.0025,4.669],[3.0025,5.0025],[3.5,5.5],[3.9975,5.9975],[3.9975,4.669],[3.8225,4.669],[3.9975,4.4967],[3.9975,4.1318],[3.9795,4.1404]],"holes":[]},{"ext":[[4.1493,4.0259],[4.1114,4.0604],[4.0702,4.0912],[4.0262,4.118],[4.0025,4.1294],[4.0025,4.4918],[4.1667,4.3301],[4.5108,4.669],[4.0025,4.669],[4.0025,5.9975],[5.0,5.0],[5.0,4.669],[4.6559,4.669],[5.0,4.3301],[5.0,4.0025],[4.1705,4.0025]],"holes":[]}],"PT1R":[{"ext":[[4.0025,0.9439],[4.0025,0.0],[5.0,0.0],[5.0,0.1001],[4.2784,0.1001],[5.0,0.8218],[5.0,1.9975],[4.9392,1.9975],[4.9392,1.8477],[4.7894,1.9975],[4.706,1.9975],[4.9392,1.7643],[4.9392,1.64],[4.5817,1.9975],[4.4984,1.9975],[4.9392,1.5566],[4.9392,1.4591],[4.4009,1.9975],[4.3175,1.9975],[4.9742,1.3408],[4.8926,1.2592],[4.1543,1.9975],[4.0025,1.9975],[4.0025,1.955],[4.5081,1.4495]],"holes":[[[4.1661,0.6146],[4.1889,0.6124],[4.2102,0.6058],[4.2294,0.5953],[4.2462,0.5814],[4.2601,0.5647],[4.2706,0.5455],[4.2771,0.5242],[4.2794,0.5013],[4.2771,0.4785],[4.2706,0.4572],[4.2601,0.438],[4.2462,0.4212],[4.2294,0.4073],[4.2102,0.3969],[4.1889,0.3903],[4.1661,0.388],[4.1433,0.3903],[4.122,0.3969],[4.1028,0.4073],[4.086,0.4212],[4.0721,0.438],[4.0616,0.4572],[4.055,0.4785],[4.0528,0.5013],[4.055,0.5242],[4.0616,0.5455],[4.0721,0.5647],[4.086,0.5814],[4.1028,0.5953],[4.122,0.6058],[4.1433,0.6124]]]},{"ext":[[3.0025,0.8385],[3.0025,0.0],[3.9975,0.0],[3.9975,0.9443],[3.602,1.3398],[3.9975,1.3398],[3.9975,1.8335]],"holes":[]},{"ext":[[2.0025,0.8326],[2.0025,0.0],[2.9975,0.0],[2.9975,0.8335],[2.5931,0.4291],[2.6094,0.3928],[2.6118,0.3527],[2.6001,0.3143],[2.5747,0.2815],[2.5391,0.2601],[2.4995,0.253],[2.46,0.2601],[2.4244,0.2815],[2.399,0.3143],[2.3873,0.3527],[2.3896,0.3928],[2.406,0.4291]],"holes":[]},{"ext":[[1.0025,0.9452],[1.0025,0.0],[1.9975,0.0],[1.9975,0.8376],[1.0025,1.8326],[1.0025,1.3398],[1.3971,1.3398]],"holes":[]},{"ext":[[0.0,0.1001],[0.0,0.0],[0.9975,0.0],[0.9975,0.943],[0.491,1.4495],[0.9975,1.9559],[0.9975,1.9975],[0.8447,1.9975],[0.0602,1.213],[0.0602,1.3229],[0.7348,1.9975],[0.6162,1.9975],[0.0602,1.4416],[0.0602,1.5362],[0.5216,1.9975],[0.4156,1.9975],[0.0602,1.6421],[0.0602,1.7367],[0.321,1.9975],[0.2079,1.9975],[0.0602,1.8498],[0.0602,1.9975],[0.0,1.9975],[0.0,0.7166],[0.6164,0.1001]],"holes":[[[0.8098,0.6124],[0.8327,0.6146],[0.8555,0.6124],[0.8768,0.6058],[0.896,0.5953],[0.9128,0.5814],[0.9266,0.5647],[0.9371,0.5455],[0.9437,0.5242],[0.946,0.5013],[0.9437,0.4785],[0.9371,0.4572],[0.9266,0.438],[0.9128,0.4212],[0.896,0.4073],[0.8768,0.3969],[0.8555,0.3903],[0.8327,0.388],[0.8098,0.3903],[0.7885,0.3969],[0.7693,0.4073],[0.7525,0.4212],[0.7387,0.438],[0.7282,0.4572],[0.7216,0.4785],[0.7193,0.5013],[0.7216,0.5242],[0.7282,0.5455],[0.7387,0.5647],[0.7525,0.5814],[0.7693,0.5953],[0.7885,0.6058]]]},{"ext":[[0.0348,3.4498],[0.0,3.4463],[0.0,2.0025],[0.0602,2.0025],[0.0602,2.356],[0.3133,2.1029],[0.2129,2.0025],[0.326,2.0025],[0.4264,2.1029],[0.0602,2.4691],[0.0602,2.5637],[0.521,2.1029],[0.4206,2.0025],[0.5266,2.0025],[0.627,2.1029],[0.0602,2.6697],[0.0602,2.7643],[0.7216,2.1029],[0.6212,2.0025],[0.7398,2.0025],[0.8236,2.0863],[0.0602,2.8497],[0.0602,2.9596],[0.9335,2.0863],[0.8497,2.0025],[0.9975,2.0025],[0.9975,2.0699],[0.8469,2.2205],[0.9975,2.2205],[0.9975,3.1122],[0.961,3.1302],[0.9021,3.1696],[0.8495,3.2159],[0.8038,3.2682],[0.7655,3.3257],[0.7348,3.3877],[0.7124,3.4535],[0.6985,3.5221],[0.6938,3.5949],[0.9975,3.5949],[0.9975,3.6461],[0.6938,3.6461],[0.6966,3.7028],[0.7047,3.7558],[0.7179,3.807],[0.7359,3.8561],[0.7583,3.9029],[0.7851,3.9468],[0.8159,3.988],[0.8245,3.9975],[0.0,3.9975],[0.0,3.7947],[0.0348,3.7912],[0.0676,3.7811],[0.0971,3.765],[0.1229,3.7437],[0.1442,3.7179],[0.1603,3.6883],[0.1705,3.6556],[0.174,3.6205],[0.1705,3.5854],[0.1603,3.5527],[0.1442,3.5231],[0.1229,3.4973],[0.0971,3.476],[0.0676,3.4599]],"holes":[]},{"ext":[[0.3438,4.669],[0.0,4.3305],[0.0,4.0025],[0.8291,4.0025],[0.8504,4.0259],[0.8883,4.0604],[0.9294,4.0912],[0.9734,4.118],[0.9975,4.1295],[0.9975,4.4921],[0.833,4.3301],[0.4888,4.669],[0.9975,4.669],[0.9975,5.3541],[0.9747,5.3353],[0.9436,5.3225],[0.9101,5.3195],[0.8765,5.3266],[0.8465,5.3436],[0.8235,5.3682],[0.8088,5.3984],[0.8036,5.4324],[0.8088,5.4664],[0.8235,5.4966],[0.8466,5.5212],[0.8765,5.5381],[0.9101,5.5453],[0.9436,5.5423],[0.9747,5.5294],[0.9975,5.5106],[0.9975,6.0],[0.0,6.0],[0.0,5.7519],[0.7207,5.0312],[0.0,5.0312],[0.0,4.669]],"holes":[]},{"ext":[[1.9975,4.669],[1.9975,5.0025],[1.0025,5.9975],[1.0025,5.5058],[1.0134,5.4909],[1.0224,5.4726],[1.0279,5.4529],[1.0298,5.4324],[1.0279,5.4118],[1.0224,5.3922],[1.0134,5.3739],[1.0025,5.359],[1.0025,4.669],[1.1772,4.669],[1.0025,4.497],[1.0025,4.1319],[1.0202,4.1404],[1.0693,4.1584],[1.1205,4.1716],[1.1735,4.1797],[1.2281,4.1824],[1.2828,4.1797],[1.3358,4.1716],[1.387,4.1584],[1.4361,4.1404],[1.4829,4.118],[1.5268,4.0912],[1.568,4.0604],[1.6059,4.0259],[1.6272,4.0025],[1.9975,4.0025],[1.9975,4.6562],[1.6663,4.3301],[1.3221,4.669]],"holes":[]},{"ext":[[4.9392,2.0025],[4.9975,2.0025],[4.9392,2.0608]],"holes":[]},{"ext":[[4.5801,2.2068],[4.6867,2.3134],[4.6449,2.3551],[4.4967,2.2068],[4.701,2.0025],[4.7844,2.0025]],"holes":[]},{"ext":[[4.3858,2.1934],[4.5962,2.4038],[4.5545,2.4455],[4.3025,2.1934],[4.4934,2.0025],[4.5767,2.0025]],"holes":[]},{"ext":[[4.1888,2.2096],[4.4896,2.5104],[4.0025,2.9975],[4.0025,2.2205],[4.1522,2.2205],[4.0025,2.0708],[4.0025,2.0025],[4.1493,2.0025],[4.0655,2.0863],[4.1471,2.1679],[4.3125,2.0025],[4.3959,2.0025]],"holes":[]},{"ext":[[4.2773,1.3398],[4.3869,1.4495],[4.0025,1.8339],[4.0025,1.3398]],"holes":[]},{"ext":[[3.0025,1.0708],[3.0025,0.9597],[3.9975,1.9546],[3.9975,1.9975],[3.9292,1.9975],[3.1677,1.236],[3.0845,1.3192],[3.5911,1.8258],[3.4194,1.9975],[3.1379,1.9975],[3.3096,1.8258],[3.0025,1.5187],[3.0025,1.2372],[3.0467,1.2814],[3.1299,1.1982]],"holes":[]},{"ext":[[2.4995,0.4794],[2.52,0.4772],[2.9975,0.9547],[2.9975,1.0658],[2.4995,0.5679],[2.0025,1.0649],[2.0025,0.9537],[2.479,0.4772]],"holes":[]},{"ext":[[1.0025,1.9975],[1.0025,1.9537],[1.9975,0.9587],[1.9975,1.0699],[1.8692,1.1982],[1.9524,1.2814],[1.9975,1.2363],[1.9975,1.5178],[1.6895,1.8258],[1.8612,1.9975],[1.5797,1.9975],[1.408,1.8258],[1.9146,1.3192],[1.8314,1.236],[1.0699,1.9975]],"holes":[]},{"ext":[[0.6122,1.4495],[0.7218,1.3398],[0.9975,1.3398],[0.9975,1.8348]],"holes":[]},{"ext":[[3.2414,3.7189],[3.248,3.752],[3.0025,3.9975],[3.0025,3.0061],[3.3667,3.0061],[3.0457,2.6851],[3.0025,2.6851],[3.0025,2.6133],[3.7594,2.6133],[3.3667,2.2205],[3.9975,2.2205],[3.9975,3.0025],[3.9199,3.0801],[3.8786,3.0694],[3.8256,3.0613],[3.771,3.0586],[3.7163,3.0613],[3.6633,3.0694],[3.6121,3.0826],[3.563,3.1006],[3.5162,3.123],[3.4723,3.1498],[3.4311,3.1806],[3.3932,3.2151],[3.3587,3.253],[3.3279,3.2942],[3.3011,3.3382],[3.2787,3.3849],[3.2607,3.434],[3.2475,3.4852],[3.2394,3.5382],[3.2366,3.5949],[3.4051,3.5949],[3.3539,3.6461],[3.2366,3.6461]],"holes":[]},{"ext":[[3.9975,2.0025],[3.9975,2.0658],[3.9342,2.0025]],"holes":[]},{"ext":[[2.9975,2.4194],[2.8036,2.6133],[2.9975,2.6133],[2.9975,2.6851],[2.7318,2.6851],[2.4995,2.9173],[2.2673,2.6851],[2.0025,2.6851],[2.0025,2.6133],[2.1955,2.6133],[2.0025,2.4203],[2.0025,2.1388],[2.4995,2.6359],[2.9975,2.1379]],"holes":[]},{"ext":[[3.1329,2.0025],[3.4144,2.0025],[3.0025,2.4144],[3.0025,2.1329]],"holes":[]},{"ext":[[2.0025,4.0025],[2.9975,4.0025],[2.5854,4.4146],[2.4995,4.3301],[2.1554,4.669],[2.331,4.669],[2.0025,4.9975],[2.0025,4.669],[2.0105,4.669],[2.0025,4.6611]],"holes":[]},{"ext":[[2.8971,3.3187],[2.5844,3.0061],[2.9975,3.0061],[2.9975,3.9975],[2.0025,3.9975],[2.0025,3.0061],[2.4147,3.0061],[2.102,3.3187]],"holes":[[[2.4645,3.4501],[2.4318,3.4602],[2.4024,3.4763],[2.3766,3.4976],[2.3553,3.5233],[2.3393,3.5528],[2.3292,3.5855],[2.3257,3.6205],[2.3292,3.6555],[2.3393,3.6882],[2.3553,3.7177],[2.3766,3.7434],[2.4024,3.7647],[2.4318,3.7808],[2.4645,3.7909],[2.4995,3.7944],[2.5346,3.7909],[2.5672,3.7808],[2.5967,3.7647],[2.6225,3.7434],[2.6438,3.7177],[2.6598,3.6882],[2.6699,3.6555],[2.6734,3.6205],[2.6699,3.5855],[2.6598,3.5528],[2.6438,3.5233],[2.6225,3.4976],[2.5967,3.4763],[2.5672,3.4602],[2.5346,3.4501],[2.4995,3.4466]]]},{"ext":[[1.9534,2.6851],[1.6324,3.0061],[1.9975,3.0061],[1.9975,3.9975],[1.6318,3.9975],[1.6404,3.988],[1.6712,3.9468],[1.698,3.9029],[1.7204,3.8561],[1.7384,3.807],[1.7516,3.7558],[1.7597,3.7028],[1.7625,3.6461],[1.3298,3.6461],[1.3148,3.679],[1.2918,3.7035],[1.2621,3.7194],[1.2281,3.7251],[1.1942,3.7194],[1.1645,3.7035],[1.1415,3.679],[1.1265,3.6461],[1.0025,3.6461],[1.0025,3.5949],[1.1265,3.5949],[1.1415,3.562],[1.1645,3.5375],[1.1942,3.5216],[1.2281,3.5159],[1.2621,3.5216],[1.2918,3.5375],[1.3148,3.562],[1.3298,3.5949],[1.7625,3.5949],[1.7577,3.5221],[1.7439,3.4535],[1.7215,3.3877],[1.6908,3.3257],[1.6525,3.2682],[1.6067,3.2159],[1.5542,3.1696],[1.4953,3.1302],[1.4317,3.0988],[1.3653,3.0765],[1.2972,3.0631],[1.2281,3.0586],[1.1591,3.0631],[1.091,3.0765],[1.0246,3.0988],[1.0025,3.1097],[1.0025,2.2205],[1.6324,2.2205],[1.2397,2.6133],[1.9975,2.6133],[1.9975,2.6851]],"holes":[]},{"ext":[[2.9975,1.2322],[2.9975,1.5137],[2.4995,1.0157],[2.0025,1.5128],[2.0025,1.2313],[2.4995,0.7343]],"holes":[]},{"ext":[[1.5847,2.0025],[1.8662,2.0025],[1.9975,2.1338],[1.9975,2.4153]],"holes":[]},{"ext":[[1.0025,2.0025],[1.0649,2.0025],[1.0025,2.0649]],"holes":[]}]}""")


# =============================================================================
# 2. UTILIDADES
# =============================================================================
def srgb(h):
    """'#RRGGBB' (sRGB) -> RGBA lineal."""
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)


def coleccion(nombre, padre=None):
    c = bpy.data.collections.get(nombre) or bpy.data.collections.new(nombre)
    padre = padre or bpy.context.scene.collection
    if c.name not in padre.children:
        padre.children.link(c)
    return c


def limpiar():
    """Borra lo que generó una ejecución anterior (colecciones propias, escena de crepúsculo, mundos)."""
    for n in COLECCIONES + ["08_LUZ_DIA", "08_LUZ_CREPUSCULO", "09_NIEVE_CREPUSCULO"]:
        c = bpy.data.collections.get(n)
        if not c:
            continue
        for sub in list(c.children_recursive) + [c]:
            for ob in list(sub.objects):
                bpy.data.objects.remove(ob, do_unlink=True)
        for sub in list(c.children_recursive):
            bpy.data.collections.remove(sub)
        bpy.data.collections.remove(c)
    for nombre in ("UYUNI_CREPUSCULO", "UYUNI_DIA_P2_SALAR_LITIO"):
        sc = bpy.data.scenes.get(nombre)
        if sc and len(bpy.data.scenes) > 1:
            bpy.data.scenes.remove(sc)
    for w in list(bpy.data.worlds):
        if w.name.startswith(PREFIJO):
            bpy.data.worlds.remove(w)
    try:
        bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    except TypeError:
        bpy.data.orphans_purge()


class Malla:
    """Acumula cajas, prismas y perfiles en una sola malla (con vértices en coordenadas de mundo)."""

    def __init__(self):
        self.v, self.f = [], []

    def caja(self, x0, x1, y0, y1, z0, z1):
        if x1 < x0: x0, x1 = x1, x0
        if y1 < y0: y0, y1 = y1, y0
        if z1 < z0: z0, z1 = z1, z0
        i = len(self.v)
        self.v += [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                   (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        self.f += [(i, i + 3, i + 2, i + 1), (i + 4, i + 5, i + 6, i + 7), (i, i + 1, i + 5, i + 4),
                   (i + 1, i + 2, i + 6, i + 5), (i + 2, i + 3, i + 7, i + 6), (i + 3, i, i + 4, i + 7)]
        return self

    def prisma_yz(self, perfil, x0, x1):
        """Polígono cerrado en el plano YZ [(y, z), ...] extruido de x0 a x1."""
        n, i = len(perfil), len(self.v)
        self.v += [(x0, y, z) for y, z in perfil] + [(x1, y, z) for y, z in perfil]
        self.f.append(tuple(range(i + n - 1, i - 1, -1)))
        self.f.append(tuple(range(i + n, i + 2 * n)))
        for k in range(n):
            a, b = k, (k + 1) % n
            self.f.append((i + a, i + b, i + n + b, i + n + a))
        return self

    def prisma_xz(self, perfil, y0, y1):
        """Polígono cerrado en el plano XZ [(x, z), ...] extruido de y0 a y1."""
        n, i = len(perfil), len(self.v)
        self.v += [(x, y0, z) for x, z in perfil] + [(x, y1, z) for x, z in perfil]
        self.f.append(tuple(range(i, i + n)))
        self.f.append(tuple(range(i + 2 * n - 1, i + n - 1, -1)))
        for k in range(n):
            a, b = k, (k + 1) % n
            self.f.append((i + b, i + a, i + n + a, i + n + b))
        return self

    def cilindro_x(self, x0, x1, y, z, r, seg=16):
        perfil = [(y + r * math.cos(2 * math.pi * k / seg), z + r * math.sin(2 * math.pi * k / seg)) for k in range(seg)]
        return self.prisma_yz(perfil, x0, x1)

    def cilindro_y(self, x, y0, y1, z, r, seg=20):
        perfil = [(x + r * math.cos(2 * math.pi * k / seg), z + r * math.sin(2 * math.pi * k / seg)) for k in range(seg)]
        return self.prisma_xz(perfil, y0, y1)

    def prisma_xy(self, perfil, z0, z1):
        """Polígono cerrado en planta [(x, y), ...] extruido de z0 a z1."""
        n, i = len(perfil), len(self.v)
        self.v += [(x, y, z0) for x, y in perfil] + [(x, y, z1) for x, y in perfil]
        self.f.append(tuple(range(i + n - 1, i - 1, -1)))
        self.f.append(tuple(range(i + n, i + 2 * n)))
        for k in range(n):
            a, b = k, (k + 1) % n
            self.f.append((i + a, i + b, i + n + b, i + n + a))
        return self

    def cilindro_z(self, x, y, z0, z1, r, seg=16):
        return self.prisma_xy([(x + r * math.cos(2 * math.pi * k / seg), y + r * math.sin(2 * math.pi * k / seg))
                               for k in range(seg)], z0, z1)

    def loft(self, anillos, tapas=(True, True)):
        """Une anillos 3D de igual cantidad de puntos con cuadriláteros; tapa los extremos con un abanico."""
        n, i0 = len(anillos[0]), len(self.v)
        for a in anillos:
            self.v += [tuple(p) for p in a]
        for r in range(len(anillos) - 1):
            for k in range(n):
                a, b = i0 + r * n + k, i0 + r * n + (k + 1) % n
                self.f.append((a, b, b + n, a + n))
        for r, tapa in zip((0, len(anillos) - 1), tapas):
            if tapa:
                c = len(self.v)
                self.v.append(tuple(sum(p[j] for p in anillos[r]) / n for j in range(3)))
                self.f += [(i0 + r * n + k, i0 + r * n + (k + 1) % n, c) for k in range(n)]
        return self

    def cilindro_eje(self, c, eje, r, largo, seg=16):
        """Cilindro de radio r y largo dado, centrado en c, con el eje en cualquier dirección."""
        e = Vector(eje).normalized()
        p = e.orthogonal().normalized()
        q = e.cross(p)
        c = Vector(c)
        anillos = [[tuple(c + e * (s * largo / 2) + r * (math.cos(2 * math.pi * k / seg) * p + math.sin(2 * math.pi * k / seg) * q))
                    for k in range(seg)] for s in (-1, 1)]
        return self.loft(anillos)

    def caja_eje(self, p0, p1, ancho, alto, z_abajo=0.0):
        """Caja de sección ancho x alto (vertical) a lo largo del eje p0 -> p1 (puntos 3D del nivel de piso);
        va de z_abajo debajo del eje hasta alto - z_abajo encima."""
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        l = math.hypot(dx, dy)
        nx, ny = -dy / l * ancho / 2, dx / l * ancho / 2
        i = len(self.v)
        for (px, py, pz) in (p0, p1):
            self.v += [(px - nx, py - ny, pz - z_abajo), (px + nx, py + ny, pz - z_abajo),
                       (px + nx, py + ny, pz - z_abajo + alto), (px - nx, py - ny, pz - z_abajo + alto)]
        self.f += [(i, i + 1, i + 2, i + 3), (i + 4, i + 7, i + 6, i + 5), (i, i + 4, i + 5, i + 1),
                   (i + 1, i + 5, i + 6, i + 2), (i + 2, i + 6, i + 7, i + 3), (i + 3, i + 7, i + 4, i)]
        return self

    def caja_rotada(self, cx, cy, largo, ancho, z0, z1, ang):
        """Caja de planta largo x ancho centrada en (cx, cy) y girada ang radianes sobre Z."""
        c, s = math.cos(ang), math.sin(ang)
        pts = [(cx + u * c - v * s, cy + u * s + v * c)
               for u, v in ((-largo / 2, -ancho / 2), (largo / 2, -ancho / 2), (largo / 2, ancho / 2), (-largo / 2, ancho / 2))]
        return self.prisma_xy(pts, z0, z1)

    def crear(self, nombre, mat, col, suave=False):
        me = bpy.data.meshes.new(PREFIJO + nombre)
        me.from_pydata(self.v, [], self.f)
        me.validate(clean_customdata=False)
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
        me.update()
        if suave:
            for p in me.polygons:
                p.use_smooth = True
        if mat:
            me.materials.append(mat)
        ob = bpy.data.objects.new(PREFIJO + nombre, me)
        col.objects.link(ob)
        return ob


def placa_con_huecos(nombre, contornos, espesor, plano, desplaz, mat, col):
    """Placa plana con agujeros (curva 2D con relleno par-impar), convertida a malla.

    contornos: lista de polígonos [(u, v), ...]; los interiores restan (agujeros).
    plano 'XZ': u = X, v = Z, extruida en Y alrededor de desplaz.
    plano 'YZ': u = Y, v = Z, extruida en X alrededor de desplaz.
    plano 'XY': u = X, v = Y, extruida en Z alrededor de desplaz (losas y veredas en planta).
    """
    cu = bpy.data.curves.new(PREFIJO + nombre + "_crv", "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    cu.extrude = espesor / 2
    for pts in contornos:
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for k, (u, v) in enumerate(pts):
            sp.points[k].co = (u, v, 0.0, 1.0)
        sp.use_cyclic_u = True
    tmp = bpy.data.objects.new(PREFIJO + nombre + "_tmp", cu)
    col.objects.link(tmp)
    if plano == "XZ":   # local (u, v, w) -> mundo (u, desplaz - w, v)
        tmp.matrix_world = Matrix.Translation((0, desplaz, 0)) @ Matrix.Rotation(math.radians(90), 4, "X")
    elif plano == "XY":  # local (u, v, w) -> mundo (u, v, desplaz + w)
        tmp.matrix_world = Matrix.Translation((0, 0, desplaz))
    else:               # local (u, v, w) -> mundo (desplaz + w, u, v)
        tmp.matrix_world = (Matrix.Translation((desplaz, 0, 0)) @ Matrix.Rotation(math.radians(90), 4, "Z")
                            @ Matrix.Rotation(math.radians(90), 4, "X"))
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    me.transform(tmp.matrix_world)
    me.name = PREFIJO + nombre
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.curves.remove(cu)
    if mat:
        me.materials.clear()
        me.materials.append(mat)
    ob = bpy.data.objects.new(PREFIJO + nombre, me)
    col.objects.link(ob)
    return ob


def dentro_poligono(x, y, pts):
    """Prueba punto en polígono (par-impar)."""
    dentro = False
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            dentro = not dentro
    return dentro


def rombo(cu, cv, lado=1.20):
    d = lado / math.sqrt(2)
    return [(cu, cv - d), (cu + d, cv), (cu, cv + d), (cu - d, cv)]


def rect(u0, u1, v0, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def z_cubierta(y):
    """Cota de la cara superior de la cubierta en Y (interpolación lineal del perfil)."""
    p = PERFIL_CUBIERTA
    if y <= p[0][0]:
        return p[0][1]
    for (y0, z0), (y1, z1) in zip(p, p[1:]):
        if y0 <= y <= y1:
            return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
    return p[-1][1]


def apuntar(ob, destino):
    d = Vector(destino) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


# =============================================================================
# 3. MATERIALES (PBR, Fase 3 del brief)
# =============================================================================
class Nodos:
    def __init__(self, mat):
        if mat.node_tree is None:
            mat.use_nodes = True
        self.nt = mat.node_tree
        self.nt.nodes.clear()
        self.out = self.n("ShaderNodeOutputMaterial")
        self.bsdf = self.n("ShaderNodeBsdfPrincipled")
        self.nt.links.new(self.bsdf.outputs[0], self.out.inputs["Surface"])

    def n(self, tipo, **props):
        nd = self.nt.nodes.new(tipo)
        for k, v in props.items():
            setattr(nd, k, v)
        return nd

    def con(self, a, b):
        if isinstance(a, (int, float, bool, tuple, list)):
            b.default_value = a
        else:
            self.nt.links.new(a, b)

    def m(self, op, a, b=None, clamp=False):
        nd = self.n("ShaderNodeMath", operation=op, use_clamp=clamp)
        self.con(a, nd.inputs[0])
        if b is not None:
            self.con(b, nd.inputs[1])
        return nd.outputs[0]

    @staticmethod
    def sk(coleccion, nombre, tipo):
        return next(s for s in coleccion if s.name == nombre and s.type == tipo)

    def mixc(self, fac, a, b):
        """Mezcla de colores; a y b pueden ser RGBA fijos o sockets."""
        nd = self.n("ShaderNodeMix", data_type="RGBA")
        self.con(fac, nd.inputs["Factor"])
        for nombre, v in (("A", a), ("B", b)):
            sock = self.sk(nd.inputs, nombre, "RGBA")
            if isinstance(v, tuple):
                sock.default_value = v
            else:
                self.nt.links.new(v, sock)
        return self.sk(nd.outputs, "Result", "RGBA")

    def mix(self, fac, a, b):
        return self.mixc(fac, a, b)

    def mixf(self, fac, a, b):
        nd = self.n("ShaderNodeMix", data_type="FLOAT")
        self.con(fac, nd.inputs["Factor"])
        self.con(a, self.sk(nd.inputs, "A", "VALUE"))
        self.con(b, self.sk(nd.inputs, "B", "VALUE"))
        return self.sk(nd.outputs, "Result", "VALUE")

    def coord(self):
        tc = self.n("ShaderNodeTexCoord")
        sep = self.n("ShaderNodeSeparateXYZ")
        self.nt.links.new(tc.outputs["Object"], sep.inputs[0])
        return tc, sep

    def ruido(self, escala, detalle=6.0, vec=None):
        nd = self.n("ShaderNodeTexNoise")
        nd.inputs["Scale"].default_value = escala
        nd.inputs["Detail"].default_value = detalle
        if vec is not None:
            self.nt.links.new(vec, nd.inputs["Vector"])
        return nd.outputs["Fac"]

    def atributo(self, nombre):
        nd = self.n("ShaderNodeAttribute", attribute_type="VIEW_LAYER", attribute_name=nombre)
        return nd.outputs["Fac"]

    def ent(self, nombre, valor):
        if nombre in self.bsdf.inputs:
            self.con(valor, self.bsdf.inputs[nombre])

    def dist_junta(self, u, paso, origen=0.0):
        """Distancia (m) a la junta más cercana de una grilla de paso 'paso'."""
        t = self.m("DIVIDE", self.m("SUBTRACT", u, origen), paso)
        f = self.m("FRACT", self.m("ADD", t, 0.5))
        return self.m("MULTIPLY", self.m("ABSOLUTE", self.m("SUBTRACT", f, 0.5)), paso)


def mat_simple(nombre, color, metal=0.0, rug=0.5, **extra):
    mat = bpy.data.materials.new(PREFIJO + nombre)
    nb = Nodos(mat)
    nb.ent("Base Color", srgb(color))
    nb.ent("Metallic", metal)
    nb.ent("Roughness", rug)
    for k, v in extra.items():
        nb.ent(k.replace("_", " "), v)
    mat.diffuse_color = srgb(color)
    return mat


def mat_perfil():
    """Carpintería de aluminio con pintura en polvo negro mate: dieléctrica (la pintura tapa el metal)."""
    return mat_simple("ALUMINIO_NEGRO_MATE", PERFIL_COLOR, metal=0.0, rug=PERFIL_RUGOSIDAD)


def mat_propuesta(nombre, rol):
    """Material liso de dos paletas: la propiedad "propuesta" de la escena mezcla P1 (0) y P2 (1) de PALETA[rol]."""
    (c1, m1, r1), (c2, m2, r2) = PALETA[rol]
    mat = bpy.data.materials.new(PREFIJO + nombre)
    nb = Nodos(mat)
    p = nb.atributo("propuesta")
    nb.ent("Base Color", nb.mixc(p, srgb(c1), srgb(c2)))
    nb.ent("Metallic", nb.mixf(p, m1, m2))
    nb.ent("Roughness", nb.mixf(p, r1, r2))
    mat.diffuse_color = srgb(c1)
    return mat


def mat_revoque(nombre, bunas=()):
    """Revoque proyectado continuo sobre panel EPS de 80 mm con malla: sin placas ni juntas verticales.

    Color de PALETA["muro"] (según la propuesta). Grano fino de mortero y variación tonal muy suave. 'bunas': cotas Z
    de buñas horizontales finas (10 mm), solo en caras verticales (entre viga y muro)."""
    (c1, _, r1), (c2, _, r2) = PALETA["muro"]
    mat = bpy.data.materials.new(PREFIJO + nombre)
    nb = Nodos(mat)
    tc, sep = nb.coord()
    p = nb.atributo("propuesta")
    base = nb.mixc(p, srgb(c1), srgb(c2))
    tono = nb.m("ADD", 0.97, nb.m("MULTIPLY", nb.ruido(0.35, 3.0, tc.outputs["Object"]), 0.06))   # ±3 % en manchas grandes
    col = nb.n("ShaderNodeVectorMath", operation="SCALE")
    nb.nt.links.new(base, col.inputs[0])
    nb.con(tono, col.inputs["Scale"])
    color = col.outputs["Vector"]
    alto = nb.m("MULTIPLY", nb.ruido(380.0, 2.0, tc.outputs["Object"]), 0.5)                    # grano del mortero
    if bunas:
        geo = nb.n("ShaderNodeNewGeometry")
        nsep = nb.n("ShaderNodeSeparateXYZ")
        nb.nt.links.new(geo.outputs["Normal"], nsep.inputs[0])
        vertical = nb.m("LESS_THAN", nb.m("ABSOLUTE", nsep.outputs["Z"]), 0.5)
        en_buna = None
        for zb in bunas:
            b = nb.m("LESS_THAN", nb.m("ABSOLUTE", nb.m("SUBTRACT", sep.outputs["Z"], zb)), 0.005)
            en_buna = b if en_buna is None else nb.m("MAXIMUM", en_buna, b)
        buna = nb.m("MULTIPLY", en_buna, vertical)
        color = nb.mixc(nb.m("MULTIPLY", buna, 0.55), color, srgb("#202020"))
        alto = nb.m("SUBTRACT", alto, nb.m("MULTIPLY", buna, 3.0))
    nb.ent("Base Color", color)
    nb.ent("Roughness", nb.mixf(p, r1, r2))
    bump = nb.n("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.002
    nb.con(alto, bump.inputs["Height"])
    nb.ent("Normal", bump.outputs["Normal"])
    mat.diffuse_color = srgb(c1)
    return mat


def color_corten(nb, tc):
    """Color de acero corten oxidado (cobrizo cálido) y el ruido fino que modula su rugosidad."""
    r1n = nb.ruido(4.0, 8.0, tc.outputs["Object"])
    r2n = nb.ruido(38.0, 6.0, tc.outputs["Object"])
    ramp = nb.n("ShaderNodeValToRGB")
    nb.con(nb.m("ADD", nb.m("MULTIPLY", r1n, 0.7), nb.m("MULTIPLY", r2n, 0.3)), ramp.inputs["Fac"])
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.30, srgb("#4F2413")
    els[1].position, els[1].color = 0.72, srgb("#A5562A")
    e = els.new(0.52)
    e.color = srgb("#7F3C1F")
    return ramp.outputs["Color"], r2n


def mat_celosia():
    """Celosías: P1 acero corten oxidado (cobrizo cálido, ref. Cementerio de Trenes); P2 chapa pintada blanco perla."""
    (_, m1, r1), (c2, m2, r2) = PALETA["celosia"]
    mat = bpy.data.materials.new(PREFIJO + "CELOSIA_CORTEN_O_BLANCA")
    nb = Nodos(mat)
    tc, _ = nb.coord()
    p = nb.atributo("propuesta")
    corten, r2n = color_corten(nb, tc)
    r1n = nb.ruido(4.0, 8.0, tc.outputs["Object"])
    blanco = nb.mixc(nb.m("MULTIPLY", r1n, 0.08), srgb(c2), srgb("#DCDBD5"))   # pintura con leve variación
    nb.ent("Base Color", nb.mixc(p, corten, blanco))
    nb.ent("Metallic", nb.mixf(p, m1, m2))
    nb.ent("Roughness", nb.mixf(p, nb.m("ADD", r1 - 0.04, nb.m("MULTIPLY", r2n, 0.15)), r2))
    bump = nb.n("ShaderNodeBump")
    bump.inputs["Distance"].default_value = 0.002
    nb.con(nb.mixf(p, 0.25, 0.04), bump.inputs["Strength"])
    nb.con(nb.ruido(140.0, 4.0, tc.outputs["Object"]), bump.inputs["Height"])
    nb.ent("Normal", bump.outputs["Normal"])
    mat.diffuse_color = srgb("#8E4524")
    return mat


def mat_cielo():
    """Listones del cielo falso: P1 aluminio símil madera (veta a lo largo del listón, en Y); P2 blanco."""
    (c1, m1, r1), (c2, m2, r2) = PALETA["cielo"]
    mat = bpy.data.materials.new(PREFIJO + "CIELO_LISTONES")
    nb = Nodos(mat)
    tc, sep = nb.coord()
    p = nb.atributo("propuesta")
    onda = nb.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="X")
    onda.inputs["Scale"].default_value = 3.0
    onda.inputs["Distortion"].default_value = 6.0
    onda.inputs["Detail"].default_value = 3.0
    vec = nb.n("ShaderNodeCombineXYZ")      # veta en Y: comprime X y Z, estira Y
    nb.con(nb.m("MULTIPLY", sep.outputs["X"], 22.0), vec.inputs[0])
    nb.con(nb.m("MULTIPLY", sep.outputs["Y"], 0.6), vec.inputs[1])
    nb.con(nb.m("MULTIPLY", sep.outputs["Z"], 22.0), vec.inputs[2])
    nb.nt.links.new(vec.outputs[0], onda.inputs["Vector"])
    madera = nb.mixc(nb.m("MULTIPLY", onda.outputs["Fac"], 0.55), srgb(c1), srgb("#6E4325"))
    madera = nb.mixc(nb.m("MULTIPLY", nb.ruido(1.5, 4.0, tc.outputs["Object"]), 0.35), madera, srgb("#A67446"))
    nb.ent("Base Color", nb.mixc(p, madera, srgb(c2)))
    nb.ent("Metallic", nb.mixf(p, m1, m2))
    nb.ent("Roughness", nb.mixf(p, r1, r2))
    mat.diffuse_color = srgb(c1)
    return mat


def mat_vidrio():
    """Vidrio de control solar elegido el 4 de octubre (VIDRIO): dieléctrico con transmisión, sin metálico. El color base
    es el tinte de transmisión y el reflejo sale de una capa fina de baja reflexión (Thin Film), como en un vidrio real.
    Cada paño es una caja de 27 mm con Thin Wall: sus dos caras hacen de las dos hojas del DVH. Lleva ondas de templado
    por paño (roller wave) y polvo fino junto a la perfilería, que solo toca la rugosidad (nunca la altura de un Bump)."""
    mat = bpy.data.materials.new(PREFIJO + "VIDRIO_CONTROL_SOLAR")
    nb = Nodos(mat)
    nb.ent("Base Color", srgb(VIDRIO["tinte"]))
    nb.ent("Metallic", 0.0)
    nb.ent("IOR", 1.52)
    nb.ent("Transmission Weight", 1.0)
    nb.ent("Thin Wall", True)
    nb.ent("Thin Film Thickness", VIDRIO["capa_nm"])
    nb.ent("Thin Film IOR", VIDRIO["capa_ior"])
    geo = nb.n("ShaderNodeNewGeometry")
    # ondas de templado: bandas horizontales de ~0,33 m (paso de los rodillos) con fase al azar por paño
    onda = nb.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="Z")
    onda.inputs["Scale"].default_value = 2 * math.pi / 20 / VIDRIO["onda_paso"]
    onda.inputs["Distortion"].default_value = 0.6
    onda.inputs["Detail"].default_value = 0.0
    nb.nt.links.new(geo.outputs["Position"], onda.inputs["Vector"])
    nb.con(nb.m("MULTIPLY", geo.outputs["Random Per Island"], 2 * math.pi), onda.inputs["Phase Offset"])
    bump = nb.n("ShaderNodeBump")
    bump.inputs["Strength"].default_value, bump.inputs["Distance"].default_value = 0.03, 0.003
    nb.con(onda.outputs["Fac"], bump.inputs["Height"])
    nb.ent("Normal", bump.outputs["Normal"])
    # polvo fino junto a la perfilería: AO corto con los demás objetos -> rugosidad de 0,02 a 0,18
    ao = nb.n("ShaderNodeAmbientOcclusion", samples=2, only_local=False)
    ao.inputs["Distance"].default_value = VIDRIO["polvo_ao"]
    borde = nb.n("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP", clamp=True)
    nb.con(nb.m("SUBTRACT", 1.0, ao.outputs["AO"]), borde.inputs["Value"])
    borde.inputs["From Min"].default_value, borde.inputs["From Max"].default_value = 0.10, 0.50
    polvo = nb.m("MULTIPLY", borde.outputs["Result"], nb.ruido(14.0, 4.0, geo.outputs["Position"]))
    rug = nb.n("ShaderNodeMapRange", clamp=True)
    nb.con(polvo, rug.inputs["Value"])
    rug.inputs["From Min"].default_value, rug.inputs["From Max"].default_value = 0.0, 0.6
    rug.inputs["To Min"].default_value, rug.inputs["To Max"].default_value = 0.02, 0.18
    nb.ent("Roughness", rug.outputs["Result"])
    mat.diffuse_color = (0.25, 0.32, 0.37, 0.7)
    return mat


def mat_asfalto():
    mat = bpy.data.materials.new(PREFIJO + "ASFALTO")
    nb = Nodos(mat)
    tc, _ = nb.coord()
    hum = nb.atributo("humedad")
    charco = nb.m("GREATER_THAN", nb.ruido(0.35, 3.0, tc.outputs["Object"]), 0.52)
    mojado = nb.m("MULTIPLY", hum, nb.m("ADD", 0.45, nb.m("MULTIPLY", charco, 0.55)))
    base = nb.mix(nb.ruido(9.0, 8.0, tc.outputs["Object"]), srgb("#2E2E2D"), srgb("#3B3A38"))
    oscuro = nb.mixc(nb.m("MULTIPLY", mojado, 0.6), base, srgb("#151515"))
    nb.ent("Base Color", oscuro)
    nb.ent("Roughness", nb.mixf(mojado, 0.82, 0.05))
    mat.diffuse_color = srgb("#333332")
    return mat


def mat_acera():
    mat = bpy.data.materials.new(PREFIJO + "HORMIGON_FRATASADO")
    nb = Nodos(mat)
    tc, sep = nb.coord()
    junta = nb.m("LESS_THAN", nb.dist_junta(sep.outputs["X"], 2.40), 0.004)
    base = nb.mix(nb.ruido(14.0, 8.0, tc.outputs["Object"]), srgb("#B3B0A9"), srgb("#A39F97"))
    cj = nb.mixc(junta, base, srgb("#55534F"))
    nb.ent("Base Color", cj)
    hum = nb.atributo("humedad")
    nb.ent("Roughness", nb.mixf(hum, 0.82, 0.18))
    mat.diffuse_color = srgb("#B0ADA6")
    return mat


def mat_plataforma():
    """Plataforma del Lado Aire en hormigón: losas de 5,00 x 5,00 m con juntas selladas, manchas suaves y
    algo más oscura donde estacionan las aeronaves (aceite y caucho)."""
    mat = bpy.data.materials.new(PREFIJO + "HORMIGON_PLATAFORMA")
    nb = Nodos(mat)
    tc, sep = nb.coord()
    junta = nb.m("MAXIMUM", nb.m("LESS_THAN", nb.dist_junta(sep.outputs["X"], 5.0), 0.008),
                 nb.m("LESS_THAN", nb.dist_junta(sep.outputs["Y"], 5.0), 0.008))
    base = nb.mix(nb.ruido(0.9, 6.0, tc.outputs["Object"]), srgb("#A9A59D"), srgb("#959189"))
    manchas = nb.m("MULTIPLY", nb.m("GREATER_THAN", nb.ruido(0.12, 4.0, tc.outputs["Object"]), 0.58), 0.25)
    c = nb.mixc(manchas, base, srgb("#7D7A74"))
    nb.ent("Base Color", nb.mixc(junta, c, srgb("#3A3936")))
    nb.ent("Roughness", nb.mixf(nb.atributo("humedad"), 0.86, 0.2))
    mat.diffuse_color = srgb("#A29E96")
    return mat


def mat_suelo():
    """Suelo árido del altiplano, con nieve o escarcha opcional ("nieve" en la view layer o la escena). El atributo
    "salar" de la malla del terreno (1 en el Salar de Uyuni) lo vuelve costra de sal blanca, y a varios kilómetros el
    color se aclara y se enfría (perspectiva aérea aproximada: el aire del altiplano es limpio, pero no a 30 km)."""
    mat = bpy.data.materials.new(PREFIJO + "SUELO_ALTIPLANO")
    nb = Nodos(mat)
    tc, _ = nb.coord()
    c = nb.mix(nb.ruido(0.08, 6.0, tc.outputs["Object"]), srgb("#B8A887"), srgb("#9E8C6C"))
    c2 = nb.mixc(nb.m("MULTIPLY", nb.ruido(2.5, 8.0, tc.outputs["Object"]), 0.5), c, srgb("#CBBF9F"))
    salar = nb.n("ShaderNodeAttribute", attribute_type="GEOMETRY", attribute_name="salar").outputs["Fac"]
    c2 = nb.mixc(salar, c2, nb.mix(nb.ruido(0.02, 4.0, tc.outputs["Object"]), srgb("#E9E7E1"), srgb("#D9D6CE")))
    nieve = nb.m("MULTIPLY", nb.atributo("nieve"), nb.m("GREATER_THAN", nb.ruido(0.6, 5.0, tc.outputs["Object"]), 0.47))
    c3 = nb.mixc(nieve, c2, srgb("#F2F4F7"))
    lejos = nb.m("SUBTRACT", 1.0, nb.m("EXPONENT", nb.m("MULTIPLY", nb.n("ShaderNodeCameraData").outputs["View Distance"],
                                                         -1.0 / 45000.0)))
    nb.ent("Base Color", nb.mixc(nb.m("MULTIPLY", lejos, 0.85), c3, srgb("#A9B4C2")))
    nb.ent("Roughness", nb.mixf(nieve, nb.mixf(salar, 0.96, 0.75), 0.55))
    bump = nb.n("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    nb.con(nb.ruido(30.0, 8.0, tc.outputs["Object"]), bump.inputs["Height"])
    nb.ent("Normal", bump.outputs["Normal"])
    mat.diffuse_color = srgb("#B8A887")
    return mat


def mat_tierra():
    """Tierra vegetal oscura con mulch fino de grava volcánica: las jardineras del frente (negras en el modelo del
    cliente) y el relleno de sus anillos elevados."""
    mat = bpy.data.materials.new(PREFIJO + "TIERRA_JARDINERAS")
    nb = Nodos(mat)
    tc, _ = nb.coord()
    c = nb.mix(nb.ruido(45.0, 4.0, tc.outputs["Object"]), srgb("#231E1A"), srgb("#3A332D"))
    nb.ent("Base Color", nb.mixc(nb.m("MULTIPLY", nb.ruido(2.0, 3.0, tc.outputs["Object"]), 0.35), c, srgb("#4A4038")))
    nb.ent("Roughness", 0.93)
    bump = nb.n("ShaderNodeBump")
    bump.inputs["Strength"].default_value, bump.inputs["Distance"].default_value = 0.8, 0.01
    nb.con(nb.ruido(60.0, 2.0, tc.outputs["Object"]), bump.inputs["Height"])
    nb.ent("Normal", bump.outputs["Normal"])
    mat.diffuse_color = srgb("#2E2823")
    return mat


def mat_hormigon_blanco():
    """Hormigón blanco prefabricado de los anillos elevados de las jardineras y de los hexágonos de la plaza."""
    mat = bpy.data.materials.new(PREFIJO + "HORMIGON_BLANCO_PREFABRICADO")
    nb = Nodos(mat)
    tc, _ = nb.coord()
    nb.ent("Base Color", nb.mix(nb.ruido(6.0, 6.0, tc.outputs["Object"]), srgb("#DEDCD5"), srgb("#CCC9C1")))
    nb.ent("Roughness", 0.62)
    bump = nb.n("ShaderNodeBump")
    bump.inputs["Strength"].default_value, bump.inputs["Distance"].default_value = 0.15, 0.002
    nb.con(nb.ruido(220.0, 3.0, tc.outputs["Object"]), bump.inputs["Height"])
    nb.ent("Normal", bump.outputs["Normal"])
    mat.diffuse_color = srgb("#D8D6CF")
    return mat


def mat_cordon_amarillo():
    """Pintura amarilla de tráfico sobre hormigón: separador L1, borde sur de la plaza, espiga y columnas de la isla."""
    mat = bpy.data.materials.new(PREFIJO + "CORDON_PINTADO_AMARILLO")
    nb = Nodos(mat)
    tc, _ = nb.coord()
    nb.ent("Base Color", nb.mix(nb.ruido(8.0, 6.0, tc.outputs["Object"]), srgb("#D9A514"), srgb("#C2921B")))
    nb.ent("Roughness", 0.58)
    bump = nb.n("ShaderNodeBump")
    bump.inputs["Strength"].default_value, bump.inputs["Distance"].default_value = 0.2, 0.002
    nb.con(nb.ruido(150.0, 3.0, tc.outputs["Object"]), bump.inputs["Height"])
    nb.ent("Normal", bump.outputs["Normal"])
    mat.diffuse_color = srgb("#D9A514")
    return mat


def mat_paja():
    """Paja brava: hojas de color paja con base verde grisácea, tono distinto en cada mata (Random de la instancia) y
    algo de luz a través de las hojas cuando están a contraluz."""
    mat = bpy.data.materials.new(PREFIJO + "PAJA_BRAVA")
    nb = Nodos(mat)
    tc, sep = nb.coord()
    al = nb.n("ShaderNodeObjectInfo").outputs["Random"]
    c = nb.mixc(al, srgb("#B49C66"), srgb("#D3C08C"))
    base = nb.m("SUBTRACT", 1.0, nb.m("MULTIPLY", sep.outputs["Z"], 7.0, clamp=True))
    c = nb.mixc(nb.m("MULTIPLY", base, 0.7), c, srgb("#7B7A55"))
    nb.ent("Base Color", c)
    nb.ent("Roughness", 0.72)
    tr = nb.n("ShaderNodeBsdfTranslucent")
    nb.con(c, tr.inputs["Color"])
    mix = nb.n("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = 0.25
    nb.nt.links.new(nb.bsdf.outputs["BSDF"], mix.inputs[1])
    nb.nt.links.new(tr.outputs["BSDF"], mix.inputs[2])
    nb.nt.links.new(mix.outputs["Shader"], nb.out.inputs["Surface"])
    mat.diffuse_color = srgb("#C2AD78")
    return mat


def mat_hormigon():
    mat = bpy.data.materials.new(PREFIJO + "HORMIGON_VISTO")
    nb = Nodos(mat)
    tc, sep = nb.coord()
    base = nb.mix(nb.ruido(5.0, 8.0, tc.outputs["Object"]), srgb("#9C9B97"), srgb("#8A8985"))
    # marcas de encofrado (tablero de 1,22 x 2,44) en altura
    marca = nb.m("LESS_THAN", nb.dist_junta(sep.outputs["Z"], 1.22), 0.0025)
    cm = nb.mixc(nb.m("MULTIPLY", marca, 0.6), base, srgb("#6E6D69"))
    nb.ent("Base Color", cm)
    nb.ent("Roughness", 0.78)
    mat.diffuse_color = srgb("#94938F")
    return mat


def mat_emisor(nombre, color, propiedad, fuerza_base=1.0, kelvin=None):
    """Emisión cálida cuya intensidad sale de la propiedad 'propiedad' de la escena / view layer.

    Con 'kelvin', el color sale de un Blackbody a esa temperatura. En Cycles, el Blackbody tiene luminancia 1: la
    fuerza se multiplica por la luminancia de 'color' para que el brillo quede igual y solo cambie el tono."""
    mat = bpy.data.materials.new(PREFIJO + nombre)
    nb = Nodos(mat)
    nb.ent("Base Color", srgb("#202020"))
    if kelvin:
        bb = nb.n("ShaderNodeBlackbody")
        bb.inputs["Temperature"].default_value = kelvin
        nb.ent("Emission Color", bb.outputs["Color"])
        c = srgb(color)
        fuerza_base *= 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    else:
        nb.ent("Emission Color", srgb(color))
    nb.ent("Emission Strength", nb.m("MULTIPLY", nb.atributo(propiedad), fuerza_base))
    mat.diffuse_color = srgb(color)
    return mat


def mat_letrero():
    """Letras, pirámides y horizonte: blanco satinado, gris casi negro o acero corten como las celosías. Propiedades de la
    escena: "letras_corten" (1 corten) y, si no es corten, "letras_gris" (1 casi negro, 0 blanco). P1 va en corten y
    P2 en gris casi negro sobre el parapeto blanco (4 de octubre). De noche, solo las blancas emiten ("luz_letrero")."""
    mat = bpy.data.materials.new(PREFIJO + "LETRERO_BLANCO_O_CORTEN")
    nb = Nodos(mat)
    tc, _ = nb.coord()
    k = nb.atributo("letras_corten")
    g = nb.atributo("letras_gris")
    corten, r2n = color_corten(nb, tc)
    pintura = nb.mixc(g, srgb("#F3F3EF"), srgb(LETRAS_GRIS))
    nb.ent("Base Color", nb.mixc(k, pintura, corten))
    nb.ent("Roughness", nb.mixf(k, nb.mixf(g, 0.28, 0.45), nb.m("ADD", 0.74, nb.m("MULTIPLY", r2n, 0.15))))
    nb.ent("Metallic", nb.mixf(k, 0.0, 0.2))
    nb.ent("Emission Color", srgb("#FFF6E8"))
    blancas = nb.m("MULTIPLY", nb.m("SUBTRACT", 1.0, k), nb.m("SUBTRACT", 1.0, g))
    nb.ent("Emission Strength", nb.m("MULTIPLY", nb.atributo("luz_letrero"), blancas))
    mat.diffuse_color = srgb("#F3F3EF")
    return mat


def crear_materiales():
    M = dict(
        cubierta=mat_propuesta("CHAPA_CUBIERTA", "cubierta"),
        antepecho=mat_propuesta("CHAPA_ANTEPECHO_REMATES", "antepecho"),
        celosia=mat_celosia(),
        vidrio=mat_vidrio(),
        perfil=mat_perfil(),
        sello=mat_simple("SELLO_ESTRUCTURAL_NEGRO", "#0B0B0B", rug=0.6),
        muro=mat_revoque("REVOQUE_CONTINUO"),
        muro_buna=mat_revoque("REVOQUE_FACHADA_BUNAS", bunas=VIGA_1),   # buñas finas arriba y abajo de la viga
        hormigon=mat_hormigon(),
        acera=mat_acera(),
        asfalto=mat_asfalto(),
        suelo=mat_suelo(),
        cielo=mat_cielo(),
        plenum=mat_simple("PLENUM_NEGRO_MATE", "#030303", rug=1.0),
        galvanizado=mat_simple("ACERO_GALVANIZADO", "#9DA1A5", metal=0.9, rug=0.35),
        bastidor=mat_propuesta("BASTIDOR_CELOSIAS", "bastidor"),
        interior=mat_emisor("INTERIOR_LUZ_CALIDA", "#FFB46B", "luz_interior", kelvin=3500),   # mismo brillo, sin naranja
        piso_int=mat_simple("PISO_INTERIOR_GRES", "#8F8A82", rug=0.35),
        luminaria=mat_emisor("LUMINARIA_ALERO", "#FFC27A", "luz_alero", 40.0),
        letrero=mat_letrero(),
        pintura_blanca=mat_simple("PINTURA_VEHICULO_BLANCO", "#E9E9E4", metal=0.3, rug=0.3),
        vidrio_auto=mat_simple("VIDRIO_VEHICULO", "#101418", metal=0.2, rug=0.05),
        neumatico=mat_simple("NEUMATICO", "#121212", rug=0.8),
        ropa=[mat_simple(f"ROPA_{i}", c, rug=0.8) for i, c in enumerate(["#B23A2E", "#2F4F7F", "#D9822B", "#3C5A3C", "#5B5B5B"])],
        senal=mat_simple("PINTURA_VIAL_BLANCA", "#E8E8E2", rug=0.6),
        nieve=mat_simple("NIEVE", "#F4F6FA", rug=0.45, Subsurface_Weight=0.2),
        # Lado Aire (4 de octubre)
        muro_aire=mat_revoque("REVOQUE_LADO_AIRE", bunas=BUNAS_AIRE),   # buñas en el borde de las vigas V30x50
        puerta=mat_simple("PUERTA_ACERO_NEGRO_MATE", PERFIL_COLOR, rug=PERFIL_RUGOSIDAD),
        cortina=mat_simple("CORTINA_ENROLLABLE_GALVANIZADA", "#A4A8AB", metal=0.85, rug=0.42),
        senal_amarilla=mat_simple("PINTURA_PLATAFORMA_AMARILLA", "#D9A514", rug=0.6),
        senal_roja=mat_simple("PINTURA_PLATAFORMA_ROJA", "#A7292B", rug=0.6),
        plataforma=mat_plataforma(),
        manga=mat_simple("MANGA_CHAPA_GRIS_CLARO", "#D3D6D8", metal=0.25, rug=0.4),
        manga_oscuro=mat_simple("MANGA_FUELLE_Y_CAUCHO", "#1C1C1C", rug=0.85),
        avion=mat_simple("AVION_PINTURA_BLANCA", "#E9EBED", metal=0.05, rug=0.22, Coat_Weight=0.6, Coat_Roughness=0.08),
        avion_ala=mat_simple("AVION_ALA_GRIS_METALICO", "#B5BABF", metal=0.55, rug=0.32),
        avion_motor=mat_simple("AVION_GONDOLA_MOTOR", "#D7DADD", metal=0.35, rug=0.25),
        avion_oscuro=mat_simple("AVION_TOBERA_Y_TREN", "#2B2D30", metal=0.6, rug=0.45),
        avion_vidrio=mat_simple("AVION_VENTANILLAS", "#0E1216", metal=0.3, rug=0.06),
        # librea BoA y contexto (4 de octubre)
        **{f"boa_{k}": mat_simple(f"AVION_BOA_{k.upper()}", LIBREA_BOA[k], metal=0.05, rug=0.22, Coat_Weight=0.6,
                                  Coat_Roughness=0.08) for k in ("azul", "rojo", "amarillo", "verde")},
        tierra=mat_tierra(),
        hormigon_blanco=mat_hormigon_blanco(),
        cordon_amarillo=mat_cordon_amarillo(),
        paja=mat_paja(),
        manga_viento=mat_simple("MANGA_VIENTO_NARANJA", "#E8611A", rug=0.7),
    )
    return M


# =============================================================================
# 4. GEOMETRÍA
# =============================================================================
def estructura(C, M):
    col = C["01_ESTRUCTURA"]
    m = Malla()
    for x in EJES_X.values():   # columnas del eje A (Lado Tierra); en el anexo (ejes 18-20) no pasan de su cubierta
        anexo = x >= ANEXO["x"][0]
        z1 = ANEXO["z"] if anexo else Z_COL_TOPE
        # la cara extrema queda 1 cm detrás del testero o del antepecho: compartir plano da manchas negras en Cycles
        x1 = min(x + COL_ANCHO / 2, (ANEXO["x"][1] if anexo else X_ALERO[1]) - 0.01)
        m.caja(x - COL_ANCHO / 2, x1, Y_COL_EXT, Y_COL_INT, 0.0, z1)
    m.crear("COLUMNAS_EJE_A", M["muro"], col)          # revocadas, mismo tono que el muro
    v = Malla()
    for z0, z1 in (VIGA_1, VIGA_2):   # vigas 300 x 500 (dintel recto a +5,51)
        v.caja(X_ALERO[0] + 0.03, X_ALERO[1] - 0.03, Y_MURO_EXT, Y_MURO_EXT + 0.30, z0, z1)
    v.crear("VIGAS_DINTEL_300x500", M["muro_buna"], col)   # en el plano del muro, revocadas


def vano_con_nicho(u0, u1):
    """True si el vano entre columnas (u0, u1) lleva una mampara ME-1 o ME-2: solo esos quedan en nicho, retirados
    hasta el plano del muro; los demás paños van al ras de la cara de las columnas (pedido del 4 de octubre)."""
    return any(u0 - 0.1 <= x0 and x1 <= u1 + 0.1 for x0, x1 in ME1 + ME2)


def y_muro_ne(x):
    """Plano exterior del paño del Lado Tierra que contiene a X: el del muro (nicho) o la cara de las columnas."""
    xs = sorted(EJES_X.values())
    for xa, xb in zip(xs, xs[1:]):
        if xa <= x <= xb:
            return Y_MURO_EXT if vano_con_nicho(xa + COL_ANCHO / 2, xb - COL_ANCHO / 2) else Y_COL_EXT
    return Y_COL_EXT


def muro_landside(C, M):
    """Paños entre columnas (panel EPS de 80 mm con revoque proyectado continuo). Los vanos con ME-1/ME-2 forman un
    nicho: el paño va en el plano del muro, retirado 0,70 m de la cara de las columnas. Los demás (con rombos ME-3,
    detrás de las celosías o ciegos) van al ras de las columnas, hasta el cielo del alero o la cubierta del anexo."""
    col = C["02_ENVOLVENTE"]
    xs = sorted(EJES_X.values())
    huecos_rect = ME1 + ME2
    contornos = []
    z_ras = Z_CIELO + CIELO_LISTON["plenum"]          # el paño al ras sube hasta el plenum del cielo listonado
    for xa, xb in zip(xs, xs[1:]):
        u0, u1 = xa + COL_ANCHO / 2, xb - COL_ANCHO / 2
        if u1 - u0 < 0.02:
            continue
        anexo = xa >= EJES_X["17"] - 0.01             # desde el eje 17 ya no hay alero: el paño sube hasta el anexo
        if not vano_con_nicho(u0, u1):
            alto = ANEXO["z"] if anexo else z_ras
            cont = [rect(u0, u1, 0.0, alto)] + [rombo(cx, cz, 1.20) for cx, cz in ME3_NE if u0 < cx < u1]
            placa_con_huecos(f"MURO_NE_RAS_{xa:05.2f}", cont, E_MURO, "XZ", Y_COL_EXT + E_MURO / 2, M["muro"], col)
            continue
        cont = [rect(u0, u1, 0.0, H_VANO)]
        for x0, x1 in huecos_rect:
            if u0 - 0.1 <= x0 and x1 <= u1 + 0.1:
                cont.append(rect(max(x0, u0 + 0.002), min(x1, u1 - 0.002), 0.0005, H_VANO - 0.0005))
        for cx, cz in ME3_NE:
            if u0 < cx < u1:
                cont.append(rombo(cx, cz, 1.20))
        if len(cont) == 1:
            contornos.append(cont[0])   # sin vanos: se suma a la placa única
        else:
            placa_con_huecos(f"MURO_NE_{xa:05.2f}", cont, E_MURO, "XZ", Y_MURO_EXT + E_MURO / 2, M["muro_buna"], col)
    if contornos:
        m = Malla()
        for c in contornos:
            (u0, v0), (u1, _), _, (_, v1) = c
            m.caja(u0, u1, Y_MURO_EXT, Y_MURO_EXT + E_MURO, v0, v1)
        m.crear("MURO_NE_CIEGO", M["muro_buna"], col)
    # franja de muro entre vigas (+6,01 a +7,10) y sobre la viga superior, hasta la cubierta; sus extremos
    # quedan 1 cm dentro de los testeros para no compartir plano con su cara exterior
    f = Malla()
    xa, xb = X_ALERO[0] + 0.01, X_ALERO[1] - 0.01
    f.caja(xa, xb, Y_MURO_EXT, Y_MURO_EXT + E_MURO, VIGA_1[1], VIGA_2[0])
    f.caja(xa, xb, Y_MURO_EXT, Y_MURO_EXT + E_MURO, VIGA_2[1], z_cubierta(Y_MURO_EXT) - E_CUBIERTA)
    f.crear("MURO_NE_SOBRE_DINTEL", M["muro_buna"], col)


# Puerta ME-2 según su detalle (4 de octubre): las dos hojas corredizas automáticas corren por el lado interior del
# perfil de 170, colgadas de un operador bajo una viga de acero negro mate de 170 x 200 que cruza toda la mampara; el
# montante central solo existe sobre la viga y en el vano de la puerta no hay vidrio fijo exterior.
ME2_PUERTA = dict(viga=(2.44, 2.64), operador=(2.32, 2.44, 0.15), hoja_e=0.028, hoja_marco=(0.045, 0.06),
                  vidrio_inf=2.40, vidrio_sup=2.44, solape=0.035)


def mamparas(C, M):
    """ME-1 (2,15 x 5,51) y ME-2 (4,28 x 5,51): perfil 170x65, travesaño 65x65, DVH de 27 mm. La ME-2 sigue su
    detalle: hojas corredizas DVH por dentro, viga de acero y operador (ME2_PUERTA)."""
    col = C["03_CARPINTERIAS_M1"]
    pf, vd, se = Malla(), Malla(), Malla()
    py0, py1 = Y_PERFIL
    c = PERFIL_CARA
    def unidad(x0, x1, n_panos):
        # marco perimetral y montantes (170 de fondo, 65 de cara)
        pf.caja(x0, x1, py0, py1, 0.0, c)
        pf.caja(x0, x1, py0, py1, H_VANO - c, H_VANO)
        paso = (x1 - x0) / n_panos
        for k in range(n_panos + 1):
            xm = x0 + k * paso
            a, b = (x0, x0 + c) if k == 0 else ((x1 - c, x1) if k == n_panos else (xm - c / 2, xm + c / 2))
            pf.caja(a, b, py0, py1, c, H_VANO - c)
        pf.caja(x0 + c, x1 - c, py0, py0 + 0.065, Z_TRAVESANO[0], Z_TRAVESANO[1])   # travesaño 65 x 65
        # paños de vidrio (exteriores al perfil) con sello negro de 10 mm entre paños
        for k in range(n_panos):
            a = x0 + k * paso + (0.005 if k else 0.0)
            b = x0 + (k + 1) * paso - (0.005 if k < n_panos - 1 else 0.0)
            for z0, z1 in ((0.0, Z_TRAVESANO[0] + 0.03), (Z_TRAVESANO[0] + 0.04, H_VANO)):
                vd.caja(a + 0.002, b - 0.002, Y_VIDRIO[0], Y_VIDRIO[1], z0 + 0.002, z1 - 0.002)
            if k:
                se.caja(a - 0.006, a, Y_VIDRIO[0], Y_VIDRIO[1], 0.0, H_VANO)
        se.caja(x0, x1, Y_VIDRIO[0], Y_VIDRIO[1], Z_TRAVESANO[0] + 0.03, Z_TRAVESANO[0] + 0.04)
    def unidad_me2(x0, x1):
        P = ME2_PUERTA
        paso = (x1 - x0) / 4                          # módulos de 1,07: paños fijos de 0,9725 y 1,005
        xc0, xc1 = x0 + paso, x1 - paso               # vano de la puerta, entre los ejes de los montantes 1 y 3
        zv0, zv1 = P["viga"]
        pf.caja(x0, x1, py0, py1, H_VANO - c, H_VANO)                       # cabezal
        for a, b in ((x0, xc0), (xc1, x1)):                                 # umbral solo bajo los fijos
            pf.caja(a, b, py0, py1, 0.0, c)
        for k in range(5):            # montantes: los de la puerta bajan al piso; el central solo va sobre la viga
            xm = x0 + k * paso
            a, b = (x0, x0 + c) if k == 0 else ((x1 - c, x1) if k == 4 else (xm - c / 2, xm + c / 2))
            pf.caja(a, b, py0, py1, zv1 if k == 2 else (0.0 if k in (1, 3) else c), H_VANO - c)
        ac = Malla()                  # viga de acero negro mate 170 x 200, 2 mm detrás de las caras de los montantes
        ac.caja(x0 + c, x1 - c, py0 + 0.002, py1 - 0.002, zv0, zv1)
        zo0, zo1, fo = P["operador"]                                        # operador bajo la viga, del lado interior
        ac.caja(x0 + c, x1 - c, py1 - 0.10, py1 + fo - 0.10, zo0, zo1)
        ac.crear(f"ME2_VIGA_OPERADOR_{x0:05.2f}", M["perfil"], col)        # mismo negro mate que la carpintería
        # paños fijos: laterales abajo (hasta +2,40) y los cuatro de arriba (desde +2,44), con sellos negros
        for k in range(4):
            a = x0 + k * paso + (0.005 if k else 0.0)
            b = x0 + (k + 1) * paso - (0.005 if k < 3 else 0.0)
            vd.caja(a + 0.002, b - 0.002, Y_VIDRIO[0], Y_VIDRIO[1], P["vidrio_sup"] + 0.002, H_VANO - 0.002)
            if k in (0, 3):
                vd.caja(a + 0.002, b - 0.002, Y_VIDRIO[0], Y_VIDRIO[1], 0.002, P["vidrio_inf"] - 0.002)
            if k:
                se.caja(a - 0.006, a, Y_VIDRIO[0], Y_VIDRIO[1], P["vidrio_sup"] if k == 2 else 0.0, H_VANO)
        for a, b in ((x0, xc0 - c / 2), (xc1 + c / 2, x1)):
            se.caja(a, b, Y_VIDRIO[0], Y_VIDRIO[1], P["vidrio_inf"], P["vidrio_sup"])
        # dos hojas corredizas (cerradas) detrás del perfil: se solapan con los montantes, sin rendijas al interior
        he = P["hoja_e"]
        mh, mr = P["hoja_marco"]
        yh0 = py1 + 0.006
        xm = (xc0 + xc1) / 2
        for a, b in ((xc0 - c / 2 - P["solape"], xm), (xm, xc1 + c / 2 + P["solape"])):
            for (pa, pb, pz0, pz1) in ((a, a + mh, 0.005, zo0), (b - mh, b, 0.005, zo0),
                                       (a, b, zo0 - mr, zo0), (a, b, 0.005, 0.005 + mr)):
                pf.caja(pa, pb, yh0, yh0 + he + 0.012, pz0, pz1)
            vd.caja(a + mh - 0.01, b - mh + 0.01, yh0 + 0.006, yh0 + 0.006 + he - 0.006, 0.005 + mr - 0.01, zo0 - mr + 0.01)
    for x0, x1 in ME1:
        unidad(x0, x1, 2)
    for x0, x1 in ME2:
        unidad_me2(x0, x1)
    pf.crear("MAMPARA_M1_FRAMES", M["perfil"], col)
    vd.crear("MAMPARA_M1_GLASS", M["vidrio"], col)
    se.crear("MAMPARA_M1_SELLOS", M["sello"], col)
    # rombos ME-3 (1,20 x 1,20 a 45°): marco y vidrio, en el Lado Tierra; en el plano de su paño (nicho o al ras)
    for i, (cx, cz) in enumerate(ME3_NE):
        yp = y_muro_ne(cx)
        placa_con_huecos(f"ME3_NE_{i}_MARCO", [rombo(cx, cz, 1.20), rombo(cx, cz, 1.20 - 2 * 0.065 * math.sqrt(2))],
                         0.10, "XZ", yp + 0.07, M["perfil"], col)
        placa_con_huecos(f"ME3_NE_{i}_VIDRIO", [rombo(cx, cz, 1.12)], 0.027, "XZ", yp + 0.087, M["vidrio"], col)


def antepecho_alero(C, M):
    """Antepecho de 2,40 m en chapa engrapada (continuación de la cubierta, color del parapeto según la propuesta),
    retornos laterales, cielo falso listonado sobre plenum negro mate y luminarias lineales entre listones."""
    col = C["02_ENVOLVENTE"]
    x0, x1 = X_ALERO
    ye = Y_ANTEPECHO_EXT
    a = Malla()
    a.caja(x0, x1, ye, ye + E_ANTEPECHO, Z_ANTEPECHO[0], Z_ANTEPECHO[1])
    yr = ye + E_ANTEPECHO   # el retorno arranca detrás del antepecho: sin caras coplanares superpuestas
    for xa, xb in ((x0, x0 + E_ANTEPECHO), (x1 - E_ANTEPECHO, x1)):   # retornos que cierran el volado
        a.prisma_yz([(yr, Z_ANTEPECHO[0]), (Y_MURO_EXT, Z_ANTEPECHO[0]), (Y_MURO_EXT, z_cubierta(Y_MURO_EXT) - 0.02),
                     (yr, z_cubierta(yr) - 0.02)], xa, xb)
    a.crear("ANTEPECHO_2_40_CHAPA", M["antepecho"], col)
    nv = Malla()   # nervios verticales (junta engrapada) cada 0,30 m sobre la cara exterior
    nv.caja(x0 + 0.10, x0 + 0.10 + NERVIO_SECCION[0], ye - NERVIO_ANTEPECHO, ye, Z_ANTEPECHO[0], Z_ANTEPECHO[1])
    ob = nv.crear("ANTEPECHO_NERVIOS", M["antepecho"], col)
    arr = ob.modifiers.new("Array_0.30", "ARRAY")
    arr.use_relative_offset, arr.use_constant_offset = False, True
    arr.constant_offset_displace = (NERVIO_PASO, 0, 0)
    arr.count = int((x1 - x0 - 0.12) / NERVIO_PASO) + 1
    cielo_alero(C, M)


def cielo_alero(C, M):
    """Cielo falso tipo parrilla: listones perpendiculares a la fachada sobre perfiles portantes y plenum negro mate,
    con luminarias lineales entre listones (reunión del 3 de octubre)."""
    col = C["02_ENVOLVENTE"]
    x0, x1 = X_ALERO
    ye = Y_ANTEPECHO_EXT
    cl = CIELO_LISTON
    xi, xf = x0 + E_ANTEPECHO, x1 - E_ANTEPECHO
    yi, yf = ye + E_ANTEPECHO + 0.01, Y_MURO_EXT - 0.01
    p = Malla()
    p.caja(xi, xf, yi - 0.01, Y_MURO_EXT, Z_CIELO + cl["plenum"], Z_CIELO + cl["plenum"] + 0.01)
    for yp in (yi + 0.30, (yi + yf) / 2, yf - 0.30):      # portantes (omega negro) sobre los listones
        p.caja(xi, xf, yp - 0.02, yp + 0.02, Z_CIELO + cl["alto"], Z_CIELO + cl["alto"] + 0.03)
    p.crear("CIELO_PLENUM_NEGRO", M["plenum"], col)
    x_ini = xi + 0.02
    ls = Malla()
    ls.caja(x_ini, x_ini + cl["ancho"], yi, yf, Z_CIELO, Z_CIELO + cl["alto"])
    ob = ls.crear("CIELO_LISTONES", M["cielo"], col)
    arr = ob.modifiers.new(f"Array_{cl['paso']:.2f}", "ARRAY")
    arr.use_relative_offset, arr.use_constant_offset = False, True
    arr.constant_offset_displace = (cl["paso"], 0, 0)
    arr.count = int((xf - 0.02 - cl["ancho"] - x_ini) / cl["paso"]) + 1
    # luminarias lineales empotradas: una por vano, en el hueco entre dos listones y a lo largo de ellos (en Y)
    lu = Malla()
    yc = (yi + yf) / 2
    xs = sorted(EJES_X.values())
    hueco = (cl["paso"] - cl["ancho"]) / 2 + cl["ancho"]       # centro del hueco desde el borde del listón
    for xa, xb in zip(xs, xs[1:]):
        xm = (xa + xb) / 2
        if x0 + 0.5 < xm < x1 - 0.5 and xb - xa > 1:
            k = round((xm - x_ini - hueco) / cl["paso"])
            xc = x_ini + k * cl["paso"] + hueco
            lu.caja(xc - 0.0175, xc + 0.0175, yc - 0.60, yc + 0.60, Z_CIELO + 0.05, Z_CIELO + 0.07)
    lu.crear("LUMINARIAS_ALERO", M["luminaria"], col)


def cubierta(C, M):
    """Chapa engrapada (color según la propuesta), nervios cada 0,30, retenedor de nieve sobre la primera correa y
    goterón sin canaleta (remate, color del parapeto)."""
    col = C["04_CUBIERTA_INDUSTRIAL"]
    # sobre el bloque del eje R (ejes 1-5) el perfil completo; entre los ejes 5 y 17 la cubierta termina al ras de las
    # pilastras del eje I (alzado ESTE: borde a +8,47 en Y 44,54)
    tramos = [(X_ALERO[0], X_CAMBIO_AIRE, PERFIL_CUBIERTA),
              (X_CAMBIO_AIRE, X_ALERO[1], [p for p in PERFIL_CUBIERTA if p[0] < Y_PILASTRA_AIRE]
               + [(Y_PILASTRA_AIRE, z_cubierta(Y_PILASTRA_AIRE))])]
    s = Malla()
    for xa, xb, perf in tramos:
        top = list(perf)
        bot = [(y, z - E_CUBIERTA) for y, z in reversed(top)]
        s.prisma_yz(top + bot, xa, xb)
    s.crear("CUBIERTA_CHAPA", M["cubierta"], col)
    # nervio (junta alzada) siguiendo el perfil; repetido con un modificador Array cada 0,30 m
    for i, (xa, xb, perf) in enumerate(tramos):
        r = Malla()
        top = list(perf)
        alto = [(y, z + NERVIO_SECCION[1]) for y, z in reversed(top)]
        x_ini = X_ALERO[0] + 0.10 + math.ceil((xa - X_ALERO[0] - 0.10) / NERVIO_PASO - 1e-9) * NERVIO_PASO
        r.prisma_yz(top + alto, x_ini, x_ini + NERVIO_SECCION[0])
        ob = r.crear(f"CUBIERTA_NERVIOS_{i}", M["cubierta"], col)
        arr = ob.modifiers.new("Array_0.30", "ARRAY")
        arr.use_relative_offset = False
        arr.use_constant_offset = True
        arr.constant_offset_displace = (NERVIO_PASO, 0, 0)
        arr.count = int((xb - x_ini - 0.03) / NERVIO_PASO) + 1
    retenedor_nieve(C, M)
    # goterón recto (sin canaleta): pestaña vertical delante del antepecho
    g = Malla()
    y0 = PERFIL_CUBIERTA[0][0]
    g.prisma_yz([(y0 - 0.012, Z_ANTEPECHO[1] - 0.07), (y0, Z_ANTEPECHO[1] - 0.07), (y0, z_cubierta(y0) + 0.01),
                 (y0 + 0.25, z_cubierta(y0 + 0.25) + 0.01), (y0 + 0.25, z_cubierta(y0 + 0.25) + 0.002),
                 (y0 - 0.012, z_cubierta(y0) + 0.012)], X_ALERO[0] - 0.01, X_ALERO[1] + 0.01)
    g.crear("GOTERON_BORDE", M["antepecho"], col)
    # cubierta del anexo (ejes 18-20), plana, detrás de las celosías PT2
    an = Malla()
    an.caja(ANEXO["x"][0] - 0.25, ANEXO["x"][1] + 0.05, ANEXO["y"][0] - 0.05, ANEXO["y"][1] + 0.05, ANEXO["z"], ANEXO["z"] + 0.25)
    an.crear("CUBIERTA_ANEXO", M["cubierta"], col)


def retenedor_marco():
    """Sistema local del retenedor sobre el primer tramo de la cubierta: punto de apoyo (Y, Z) del eje de la
    abrazadera sobre la chapa y versores s (pendiente arriba) y n (normal a la chapa), en el plano YZ."""
    (y0, z0), (y1, z1) = PERFIL_CUBIERTA[0], PERFIL_CUBIERTA[1]
    t = math.atan2(z1 - z0, y1 - y0)
    s, n = (math.cos(t), math.sin(t)), (-math.sin(t), math.cos(t))
    d = RETENEDOR["dist_borde"]
    return (y0 + d * s[0], z0 + d * s[1]), s, n


def retenedor_nieve(C, M):
    """Retenedor de nieve según el detalle del cliente (RETENEDOR): abrazadera de chapa de 6 mm perpendicular a la
    chapa, en el plano de un nervio de cada dos, con dos orejas que muerden el nervio (y sus pernos) y tres tubos que
    pasan por sus agujeros. El eje queda a 1,398 m del borde, medido sobre la pendiente."""
    col = C["04_CUBIERTA_INDUSTRIAL"]
    R = RETENEDOR
    (pb_y, pb_z), s, n = retenedor_marco()
    def mundo_yz(ls, ln):                                   # (s, n) locales en metros -> (Y, Z)
        return (pb_y + ls * s[0] + ln * n[0], pb_z + ls * s[1] + ln * n[1])
    xc = X_ALERO[0] + 0.10 + NERVIO_SECCION[0] / 2          # eje del primer nervio
    b2, h, rc = R["base"] / 2, R["alto"], R["cabeza_r"]
    zc = h - rc                                             # centro de la cabeza redondeada
    perfil = [(-b2, 0.0), (b2, 0.0), (rc, zc)]
    perfil += [(rc * math.cos(math.pi * k / 12), zc + rc * math.sin(math.pi * k / 12)) for k in range(1, 12)]
    perfil += [(-rc, zc)]
    agujeros = [[(0.0 + R["agujero_d"] / 2 * math.cos(2 * math.pi * k / 16), hz + R["agujero_d"] / 2 * math.sin(2 * math.pi * k / 16))
                 for k in range(16)] for hz in R["agujeros"]]
    placa = placa_con_huecos("RETENEDOR_PLACAS", [[mundo_yz(a, b) for a, b in perfil]]
                             + [[mundo_yz(a, b) for a, b in ag] for ag in agujeros],
                             R["espesor"], "YZ", xc, M["galvanizado"], col)
    ob = Malla()                                            # orejas de 38 mm a cada lado del nervio, con su perno
    lo, ho = R["oreja"]
    for a, b in ((-b2, -b2 + lo), (b2 - lo, b2)):
        ob.prisma_yz([mundo_yz(a, 0.002), mundo_yz(b, 0.002), mundo_yz(b, ho), mundo_yz(a, ho)], xc - 0.0205, xc + 0.0205)
        py_, pz_ = mundo_yz((a + b) / 2, ho / 2)
        ob.cilindro_x(xc - 0.027, xc + 0.027, py_, pz_, 0.005, seg=10)
    orejas = ob.crear("RETENEDOR_OREJAS", M["galvanizado"], col)
    for o in (placa, orejas):
        arr = o.modifiers.new(f"Array_{R['paso']:.2f}", "ARRAY")
        arr.use_relative_offset, arr.use_constant_offset = False, True
        arr.constant_offset_displace = (R["paso"], 0, 0)
        arr.count = int((X_ALERO[1] - X_ALERO[0] - 0.12) / R["paso"]) + 1
    br = Malla()
    for hz in R["agujeros"]:
        ty, tz = mundo_yz(0.0, hz)
        br.cilindro_x(X_ALERO[0] + 0.05, X_ALERO[1] - 0.05, ty, tz, R["tubo_d"] / 2)
    br.crear("RETENEDOR_TUBOS", M["galvanizado"], col, suave=True)


def envolvente_general(C, M):
    """Volumen general: testeros con rombos ME-3, fachada Lado Aire (fachada_aire), anexo, testero del eje 20
    (testero_este) e interior básico."""
    col = C["02_ENVOLVENTE"]
    cc = C["03_CARPINTERIAS_M1"]
    # testeros siguiendo la cubierta. El del eje 1 arranca en la cara de las columnas del Lado Tierra (como el alzado
    # OESTE); entre esa cara y el muro sube solo hasta el retorno del antepecho, que cierra el volado por encima
    def testero(x, desde, ya, rombos, nombre):
        ys = [Y_MURO_EXT] + [p[0] for p in PERFIL_CUBIERTA if Y_MURO_EXT < p[0] < ya] + [ya]
        cont = [(desde, 0.0), (ya, 0.0)] + [(y, z_cubierta(y) - E_CUBIERTA - 0.01) for y in reversed(ys)]
        if desde < Y_MURO_EXT:
            cont += [(Y_MURO_EXT, Z_ANTEPECHO[0]), (desde, Z_ANTEPECHO[0])]
        huecos = [rombo(cy, cz, 1.20) for cy, cz in rombos]
        placa_con_huecos(nombre, [cont] + huecos, 0.15, "YZ", x, M["muro"], col)
    testero(X_ALERO[0] + 0.075, Y_COL_EXT, Y_FACHADA_AIRE["principal_izq"], ME3_EJE1, "TESTERO_EJE_1")
    testero(X_ALERO[1] - 0.075, Y_MURO_EXT, Y_PILASTRA_AIRE, [], "TESTERO_EJE_17")
    for i, (cy, cz) in enumerate(ME3_EJE1):
        placa_con_huecos(f"ME3_EJE1_{i}_VIDRIO", [rombo(cy, cz, 1.12)], 0.027, "YZ", X_ALERO[0] + 0.03, M["vidrio"], cc)
        placa_con_huecos(f"ME3_EJE1_{i}_MARCO", [rombo(cy, cz, 1.20), rombo(cy, cz, 1.016)], 0.10, "YZ", X_ALERO[0] + 0.06, M["perfil"], cc)
    fachada_aire(C, M)
    # anexo (ejes 18-20): muro hacia la pista (el del Lado Tierra se genera en muro_landside), con los rombos ME-3
    # detrás de las celosías PT2 del Lado Aire
    ax0, ax1 = ANEXO["x"]
    ay1 = ANEXO["y"][1]
    placa_con_huecos("ANEXO_MURO_LADO_AIRE", [rect(ax0, ax1, 0.0, ANEXO["z"])] + [rombo(cx, cz) for cx, cz in ME3_SO],
                     0.15, "XZ", ay1 - 0.075, M["muro"], col)
    for i, (cx, cz) in enumerate(ME3_SO):
        placa_con_huecos(f"ME3_SO_{i}_VIDRIO", [rombo(cx, cz, 1.12)], 0.027, "XZ", ay1 - 0.03, M["vidrio"], cc)
        placa_con_huecos(f"ME3_SO_{i}_MARCO", [rombo(cx, cz, 1.20), rombo(cx, cz, 1.016)], 0.10, "XZ", ay1 - 0.06,
                         M["perfil"], cc)
    testero_este(C, M)
    # interior básico (bloqueado): piso, fondo y cielo cálidos detrás del vidrio del Lado Tierra
    it = Malla()
    it.caja(X_ALERO[0] + 0.2, X_ALERO[1] - 0.2, Y_COL_INT + 0.05, 9.0, -0.05, 0.0)
    it.crear("INTERIOR_PISO", M["piso_int"], col)
    lz = Malla()
    lz.caja(X_ALERO[0] + 0.2, X_ALERO[1] - 0.2, 8.9, 9.0, 0.0, 7.0)
    lz.caja(X_ALERO[0] + 0.2, X_ALERO[1] - 0.2, Y_COL_INT + 0.05, 9.0, 7.0, 7.05)
    lz.crear("INTERIOR_LUZ", M["interior"], col)


# -----------------------------------------------------------------------------
# Carpinterías y puertas genéricas. "plano" XZ: u = X y w = Y (fachadas NE/SO); YZ: u = Y y w = X (testeros).
# "afuera" es el signo de w hacia el exterior: el interior queda del lado contrario.
# -----------------------------------------------------------------------------
def caja_o(m, plano, u0, u1, w0, w1, z0, z1):
    if plano == "XZ":
        m.caja(u0, u1, w0, w1, z0, z1)
    else:
        m.caja(w0, w1, u0, u1, z0, z1)


def ventana(pf, vd, plano, u0, u1, z0, z1, n, wc, marco=0.065, fondo=0.10, travesanos=(), umbral=True):
    """Ventana de n paños iguales: marco y montantes de 'marco' de cara y 'fondo' de profundidad centrados en wc,
    travesaños horizontales (z0, z1) y DVH de 27 mm a mitad del marco, entre los perfiles."""
    c = marco
    w0, w1 = wc - fondo / 2, wc + fondo / 2
    zb = z0 + c if umbral else z0
    if umbral:
        caja_o(pf, plano, u0, u1, w0, w1, z0, zb)
    caja_o(pf, plano, u0, u1, w0, w1, z1 - c, z1)
    paso = (u1 - u0) / n
    for k in range(n + 1):
        um = u0 + k * paso
        a, b = (u0, u0 + c) if k == 0 else ((u1 - c, u1) if k == n else (um - c / 2, um + c / 2))
        caja_o(pf, plano, a, b, w0, w1, zb, z1 - c)
    for t0, t1 in travesanos:
        caja_o(pf, plano, u0 + c, u1 - c, w0, w1, t0, t1)
    for k in range(n):
        caja_o(vd, plano, u0 + k * paso + 0.01, u0 + (k + 1) * paso - 0.01, wc - 0.0135, wc + 0.0135,
               zb - 0.01, z1 - c + 0.01)


def corrediza(pf, vd, plano, u0, u1, fijo, z_cab, wc, afuera, marco=0.065, fondo=0.10, z_hoja=None, solape=0.035):
    """Puerta corrediza automática (ME-6 y vestíbulo): paños fijos laterales de ancho 'fijo' (0 = sin fijos),
    cabezal hasta z_cab y dos hojas DVH que corren por el lado interior del marco, solapadas con él (sin rendijas)."""
    c = marco
    w0, w1 = wc - fondo / 2, wc + fondo / 2
    z_hoja = z_hoja or z_cab - 0.17
    caja_o(pf, plano, u0, u1, w0, w1, z_hoja, z_cab)                               # cabezal con el operador
    for a, b in ((u0, u0 + c), (u1 - c, u1)):
        caja_o(pf, plano, a, b, w0, w1, 0.0, z_hoja)
    ui0, ui1 = u0 + c, u1 - c                                                      # luz entre jambas
    if fijo > 0:
        for a, b in ((u0 + fijo - c, u0 + fijo), (u1 - fijo, u1 - fijo + c)):    # montantes de los fijos
            caja_o(pf, plano, a, b, w0, w1, 0.0, z_hoja)
        for a, b in ((u0, u0 + fijo), (u1 - fijo, u1)):                           # umbral bajo los fijos
            caja_o(pf, plano, a, b, w0, w1, 0.0, c)
        for a, b in ((u0 + c, u0 + fijo - c), (u1 - fijo + c, u1 - c)):
            caja_o(vd, plano, a - 0.01, b + 0.01, wc - 0.0135, wc + 0.0135, c - 0.01, z_hoja + 0.01)
        ui0, ui1 = u0 + fijo, u1 - fijo
    # hojas: del lado interior del marco, cerradas, encontrándose al centro
    wh0 = w0 - 0.006 - 0.04 if afuera > 0 else w1 + 0.006
    um = (ui0 + ui1) / 2
    for a, b in ((ui0 - c - solape, um), (um, ui1 + c + solape)):
        for (pa, pb, pz0, pz1) in ((a, a + 0.045, 0.005, z_hoja), (b - 0.045, b, 0.005, z_hoja),
                                   (a, b, z_hoja - 0.06, z_hoja), (a, b, 0.005, 0.065)):
            caja_o(pf, plano, pa, pb, wh0, wh0 + 0.04, pz0, pz1)
        caja_o(vd, plano, a + 0.035, b - 0.035, wh0 + 0.009, wh0 + 0.031, 0.055, z_hoja - 0.05)


def enrollable(cm, gm, plano, u0, u1, z1, wc):
    """Puerta enrollable de chapa galvanizada (PR-10 y PR-11): guías laterales y cortina de lamas de 75 mm."""
    for a, b in ((u0, u0 + 0.06), (u1 - 0.06, u1)):
        caja_o(gm, plano, a, b, wc - 0.045, wc + 0.045, 0.0, z1)
    caja_o(cm, plano, u0 + 0.03, u1 - 0.03, wc - 0.008, wc + 0.008, 0.0, z1)
    z = 0.075
    while z < z1 - 0.02:
        caja_o(cm, plano, u0 + 0.03, u1 - 0.03, wc - 0.011, wc + 0.011, z - 0.006, z + 0.006)
        z += 0.075
    caja_o(cm, plano, u0 + 0.03, u1 - 0.03, wc - 0.02, wc + 0.02, 0.0, 0.05)     # zócalo de la cortina


def puerta_batiente(pm, plano, u0, u1, z1, wc, afuera, hojas=1, z_hoja=None, marco=0.06):
    """Puerta de acero pintado de una o dos hojas, con marco y manijas; la hoja queda 2 cm adentro del marco."""
    c = marco
    z_hoja = z_hoja or z1
    for a, b in ((u0, u0 + c), (u1 - c, u1)):
        caja_o(pm, plano, a, b, wc - 0.05, wc + 0.05, 0.0, z1)
    caja_o(pm, plano, u0, u1, wc - 0.05, wc + 0.05, z_hoja - c, z_hoja)
    wh = wc - afuera * 0.02
    paso = (u1 - u0 - 2 * c) / hojas
    for k in range(hojas):
        a = u0 + c + k * paso + (0.003 if k else 0.0)
        b = u0 + c + (k + 1) * paso - (0.003 if k < hojas - 1 else 0.0)
        caja_o(pm, plano, a, b, wh - 0.0225, wh + 0.0225, 0.008, z_hoja - c)
        um = b - 0.09 if (hojas == 1 or k == 0) else a + 0.09                   # manija del lado de la cerradura
        caja_o(pm, plano, um - 0.07, um + 0.07, wh + afuera * 0.0225, wh + afuera * 0.06, 1.03, 1.06)


def rejilla(pm, fm, plano, u0, u1, z0, z1, wc, afuera):
    """Rejilla de ventilación de lamas sobre las puertas: marco, lamas cada 6 cm y fondo negro."""
    caja_o(pm, plano, u0, u1, wc - 0.04, wc + 0.04, z0, z0 + 0.03)
    caja_o(pm, plano, u0, u1, wc - 0.04, wc + 0.04, z1 - 0.03, z1)
    for a, b in ((u0, u0 + 0.03), (u1 - 0.03, u1)):
        caja_o(pm, plano, a, b, wc - 0.04, wc + 0.04, z0, z1)
    z = z0 + 0.06
    while z < z1 - 0.04:
        caja_o(pm, plano, u0 + 0.03, u1 - 0.03, wc - 0.025, wc + 0.025, z - 0.012, z + 0.012)
        z += 0.06
    caja_o(fm, plano, u0, u1, wc - afuera * 0.05 - 0.005, wc - afuera * 0.05 + 0.005, z0, z1)


def vidriado_embarque(pf, vd, plano, u0, u1, wc):
    """Frente vidriado de las puertas de embarque (alzado SO): perfiles de 40 mm, travesaño a +5,88..5,92 y DVH."""
    z0, z1 = EMBARQUE_Z
    for a, b in ((u0, u0 + 0.04), (u1 - 0.04, u1)):
        caja_o(pf, plano, a, b, wc - 0.04, wc + 0.04, z0, z1)
    for t0, t1 in ((z0, z0 + 0.04), (5.88, 5.92), (z1 - 0.04, z1)):
        caja_o(pf, plano, u0, u1, wc - 0.04, wc + 0.04, t0, t1)
    for t0, t1 in ((z0 + 0.04, 5.88), (5.92, z1 - 0.04)):
        caja_o(vd, plano, u0 + 0.03, u1 - 0.03, wc - 0.0135, wc + 0.0135, t0 - 0.01, t1 + 0.01)


def fachada_aire(C, M):
    """Fachada SUROESTE (Lado Aire), según el alzado SO, la planta baja A111 y el IFC (4 de octubre).

    - Bloque de los ejes 1-5 hasta el eje R (cara 48,601): vano libre a una galería cubierta, abertura con antepecho,
      muro vidriado con puerta doble al fondo de la galería y la caja de la puerta de embarque 1 (elementos_laterales).
    - Entre los ejes 5 y 17, paños opacos enrasados con las pilastras a Y 44,572;
      únicamente las crujías con ME-5/ME-6 conservan el fondo a Y 43,872.
      ME-4, enrollables y puertas acompañan el nuevo plano del muro. La entrada
      entre los ejes 7 y 8 tiene ahora una puerta frontal, sin nicho lateral.
    - Marquesina de hormigón entre los ejes 5 y 7 (losa, vigas y viguetas del IFC) y el vestíbulo de los ejes 10-11,
      de dos niveles, con la puerta de embarque 2 arriba y su corrediza al costado.
    """
    col, cc = C["02_ENVOLVENTE"], C["03_CARPINTERIAS_M1"]
    e = E_MURO_AIRE
    yI, yR, xb = Y_FACHADA_AIRE["principal_der"], Y_FACHADA_AIRE["principal_izq"], X_CAMBIO_AIRE
    def z_techo(y):
        return z_cubierta(y) - E_CUBIERTA - 0.01
    pf, vd, pm, cm, gm = Malla(), Malla(), Malla(), Malla(), Malla()
    # --- muro del eje I, de testero a testero (dentro del bloque es el fondo de la galería y del recinto)
    huecos = [rect(a, b, ME4_Z[0], ME4_Z[1]) for a, b in ME4_AIRE]
    huecos += [rect(a, b, max(z0, 0.0005), z1) for a, b, z0, z1 in ME5_AIRE]
    huecos += [rect(a, b, 0.0005, ME6_Z) for a, b in ME6_AIRE]
    huecos += [rect(a, b, 0.0005, Z_ENROLLABLE) for a, b in ENROLLABLES_AIRE]
    huecos += [rect(PUERTA_P01_AIRE[0], PUERTA_P01_AIRE[1], 0.0005, PUERTA_P01_AIRE[2])]
    huecos += [rect(PUERTA_FRONTAL_AIRE[0], PUERTA_FRONTAL_AIRE[1], 0.0005, PUERTA_FRONTAL_AIRE[2])]
    bx0, bx1, bz0, bz1 = BLOQUE_AIRE["me5"]
    huecos += [rect(bx0, bx1, 0.0005, bz1)]
    x_ini, x_fin = X_ALERO[0] + 0.15, X_ALERO[1] - 0.15
    # El fondo del bloque del eje R permanece en su plano original.
    placa_con_huecos("FACHADA_AIRE_EJE_I", [rect(x_ini, xb - e, 0.0, z_techo(yI)), rect(bx0,bx1,.0005,bz1)], e, "XZ", yI - e / 2,
                     M["muro_aire"], col)
    paños_ras = []
    for izquierda, derecha in zip(PILASTRAS_AIRE, PILASTRAS_AIRE[1:]):
        u0, u1 = izquierda + .23, derecha - .23
        nicho = any(u0-.01 <= a and b <= u1+.01 for a,b,_,_ in ME5_AIRE)
        cara = yI if nicho else Y_MURO_RAS_AIRE
        contornos = [rect(u0,u1,0.0,z_techo(cara))]
        for hole in huecos:
            a,b = hole[0][0],hole[1][0]
            z0,z1 = hole[0][1],hole[2][1]
            if a < u1 and b > u0:
                contornos.append(rect(max(a,u0+.002),min(b,u1-.002),z0,z1))
        ob = placa_con_huecos(f"FACHADA_AIRE_{'NICHO_VENTANAL' if nicho else 'RAS'}_{izquierda:05.2f}",
                             contornos,e,"XZ",cara-e/2,M["muro_aire"],col)
        ob["UY_PLANO_EXTERIOR_M"] = cara
        ob["UY_REVISION_CLIENTE"] = "Paños enrasados; solo nichos de grandes ventanales"
        if not nicho: paños_ras.append((u0,u1))
    # Cierra sobre las cabezas de las columnas, sin solapar sus caras visibles.
    remates = Malla()
    for x in PILASTRAS_AIRE:
        if z_techo(Y_MURO_RAS_AIRE) > Z_PILASTRA:
            remates.prisma_yz([(yI-e,Z_PILASTRA),(Y_MURO_RAS_AIRE,Z_PILASTRA),
                               (Y_MURO_RAS_AIRE,z_techo(Y_MURO_RAS_AIRE)),(yI-e,z_techo(yI-e))],x-.23,x+.23)
    remates.crear("FACHADA_AIRE_REMATES_PILASTRAS",M["muro_aire"],col)
    wc = yI - e / 2                                   # carpinterías a mitad del muro
    wc_ras = Y_MURO_RAS_AIRE - e / 2
    for a, b in ME4_AIRE:
        ventana(pf, vd, "XZ", a, b, ME4_Z[0], ME4_Z[1], 2, wc_ras)
    for a, b, z0, z1 in ME5_AIRE + [BLOQUE_AIRE["me5"]]:
        ventana(pf, vd, "XZ", a, b, z0, z1, 3, wc)
    for a, b in ME6_AIRE:
        corrediza(pf, vd, "XZ", a, b, 1.103, ME6_Z, wc, +1, z_hoja=2.242)
    for a, b in ENROLLABLES_AIRE:
        enrollable(cm, gm, "XZ", a, b, Z_ENROLLABLE, Y_MURO_RAS_AIRE - 0.05)
    puerta_batiente(pm, "XZ", PUERTA_P01_AIRE[0], PUERTA_P01_AIRE[1], PUERTA_P01_AIRE[2], wc_ras, +1)
    # --- pilastras (columnas C40x100 revocadas), con 1 cm metido en el muro
    pl = Malla()
    for x in PILASTRAS_AIRE:
        pl.caja(x - 0.23, x + 0.23, yI - 0.01, Y_PILASTRA_AIRE, 0.0, Z_PILASTRA)
    pl.crear("PILASTRAS_AIRE", M["muro"], col)
    # --- remate (goterón) del borde de la cubierta sobre el eje I
    g = Malla()
    yb = Y_PILASTRA_AIRE
    g.caja(xb, X_ALERO[1] + 0.01, yb, yb + 0.02, z_cubierta(yb) - E_CUBIERTA - 0.08, z_cubierta(yb) + 0.012)
    g.crear("GOTERON_LADO_AIRE", M["antepecho"], C["04_CUBIERTA_INDUSTRIAL"])
    # --- bloque del eje R: muro exterior, muro lateral (hacia la marquesina) y galería cubierta
    vx0, vx1, vz0, vz1 = BLOQUE_AIRE["vano"]
    ax0_, ax1_, az0, az1 = BLOQUE_AIRE["abertura"]
    # entre el testero del eje 1 y el muro lateral: las esquinas las cierran ellos (sin caras coplanares)
    placa_con_huecos("BLOQUE_AIRE_MURO_EXTERIOR", [rect(X_ALERO[0] + 0.15, xb - e, 0.0, z_techo(yR)),
                                                    rect(vx0, vx1, 0.0005, vz1), rect(ax0_, ax1_, az0, az1)],
                     e, "XZ", yR - e / 2, M["muro_aire"], col)
    lat = Malla()
    lat.prisma_yz([(yI, 0.0), (yR, 0.0), (yR, z_techo(yR)), (45.875, z_techo(45.875)), (yI, z_techo(yI))], xb - e, xb)
    lat.crear("BLOQUE_AIRE_MURO_LATERAL", M["muro"], col)
    gx0, gx1 = BLOQUE_AIRE["galeria_x"]
    py0, py1 = BLOQUE_AIRE["puerta_y"]
    ys_t = [yI, 45.875, yR - e]
    cont = [(yI, 0.0), (yR - e, 0.0)] + [(y, z_techo(y)) for y in reversed(ys_t)]
    placa_con_huecos("BLOQUE_AIRE_TABIQUE_GALERIA", [cont, rect(yI + 0.04, yR - e - 0.04, 0.0005, 3.20)], 0.15, "YZ",
                     gx0 - 0.075, M["muro"], col)
    for a, b in ((yI + 0.04, py0), (py1, yR - e - 0.04)):                 # muro vidriado con puerta doble al centro
        n = max(1, round((b - a) / 1.2))
        ventana(pf, vd, "YZ", a, b, 0.0, 3.20, n, gx0 - 0.04, marco=0.05, fondo=0.08, travesanos=[(2.38, 2.43)])
    puerta_batiente(pf, "YZ", py0, py1, 3.20, gx0 - 0.04, +1, hojas=2, z_hoja=2.43)
    caja_o(pf, "YZ", py0, py1, gx0 - 0.08, gx0, 2.43, 3.20)                  # dintel sobre la puerta
    piso = Malla()
    piso.caja(gx0, gx1, yI, yR - e, -0.05, 0.0)
    piso.crear("BLOQUE_AIRE_PISO_GALERIA", M["acera"], col)
    # --- entrada frontal alineada, conserva la hoja de 1,00 x 2,10 m.
    puerta_batiente(pm, "XZ", PUERTA_FRONTAL_AIRE[0], PUERTA_FRONTAL_AIRE[1],
                    PUERTA_FRONTAL_AIRE[2],wc_ras,+1)
    # --- marquesina (losa, viga de borde, vigas laterales y viguetas V10x25 cada 0,50)
    mq = MARQUESINA_AIRE
    mx0, mx1 = mq["x"]
    yb_ = mq["borde_y"]
    mg = Malla()
    mg.caja(mx0, mx1, yI, yb_, mq["losa"][0], mq["losa"][1])
    mg.caja(mx0, mx1, yb_, mq["y"][1], mq["viga"][0], mq["viga"][1])
    for a, b in mq["vigas_x"]:
        mg.caja(a, b, Y_PILASTRA_AIRE, yb_, mq["viga"][0], mq["viga"][1])
    an, vz0, vz1 = mq["vigueta"]
    for a, b in ((mx0, mq["vigas_x"][0][0]), (mq["vigas_x"][0][1], mq["vigas_x"][1][0])):
        x = a + 0.24
        while x < b - 0.05:
            mg.caja(x - an / 2, x + an / 2, yI, yb_, vz0, vz1)
            x += mq["paso"]
        y = yI + 0.29
        while y < yb_ - 0.1:
            mg.caja(a, b, y - an / 2, y + an / 2, vz0, vz1)
            y += mq["paso"]
    mg.crear("MARQUESINA_AIRE", M["muro"], col)
    # --- vestíbulo de los ejes 10-11 (dos niveles): puerta de embarque 2 arriba, corrediza en su costado oeste
    vs = VESTIBULO_AIRE
    vx0, vx1 = vs["x"]
    vy1, vz = vs["y"][1], vs["z"]
    cx0, cx1 = CAJA_VESTIBULO["x"]
    placa_con_huecos("VESTIBULO_AIRE_FRENTE", [rect(vx0, vx1, 0.0, vz), rect(cx0, cx1, EMBARQUE_Z[0], EMBARQUE_Z[1])],
                     e, "XZ", vy1 - e / 2, M["muro"], col)
    vya, vyb = vs["puerta_y"]
    placa_con_huecos("VESTIBULO_AIRE_COSTADO_OESTE", [rect(yI, vy1 - e, 0.0, vz), rect(vya, vyb, 0.0005, vs["puerta_z"])],
                     e, "YZ", vx0 + e / 2, M["muro"], col)
    vl = Malla()
    vl.caja(vx1 - e, vx1, yI, vy1 - e, 0.0, vz)                             # costado este (ciego)
    vl.caja(vx0 + e, vx1 - e, yI, vy1 - e, 3.65, 3.85)                      # losa del nivel de embarque (IFC +3,70)
    vl.crear("VESTIBULO_AIRE_MUROS", M["muro"], col)
    vt = Malla()                                  # 1 cm sobre los muros: sin caras coplanares con sus cantos
    vt.caja(vx0 - 0.03, vx1 + 0.03, yI, vy1 + 0.03, vz - 0.16, vz + 0.01)
    vt.crear("VESTIBULO_AIRE_CUBIERTA", M["cubierta"], C["04_CUBIERTA_INDUSTRIAL"])
    corrediza(pf, vd, "YZ", vya, vyb, 0.0, vs["puerta_z"], vx0 + e / 2, -1)
    vidriado_embarque(pf, vd, "XZ", cx0, cx1, vy1 - 0.06)
    # --- interior básico detrás de la fachada: planta baja, losa del 1P (+3,85) y fondo cálido
    ia = Malla()
    ia.caja(x_ini, x_fin, 36.0, yI - e, -0.05, 0.0)
    ia.caja(x_ini, x_fin, 36.0, yI - e, 3.70, 3.85)
    for a,b in paños_ras:
        ia.caja(a,b,yI-e,Y_MURO_RAS_AIRE-e,-.05,0.0)
        ia.caja(a,b,yI-e,Y_MURO_RAS_AIRE-e,3.70,3.85)
    ia.caja(gx0 + 0.15, xb - e, yI, yR - e, 3.70, 3.85)                    # entrepiso del bloque, sobre la galería
    ia.caja(X_ALERO[0] + 0.15, gx0 - 0.15, yI, yR - e, -0.05, 0.0)         # piso del recinto del bloque
    ia.crear("INTERIOR_AIRE_PISOS", M["piso_int"], col)
    il = Malla()
    il.caja(x_ini, x_fin, 36.0, 36.1, 0.0, 7.0)
    il.caja(x_ini, x_fin, 36.0, yI - e, 7.0, 7.05)
    for a,b in paños_ras:
        il.caja(a,b,yI-e,Y_MURO_RAS_AIRE-e,7.0,7.05)
    il.caja(X_ALERO[0] + 0.15, X_ALERO[0] + 0.25, yI, yR - e, 0.0, 3.60)  # fondo del recinto del bloque
    il.crear("INTERIOR_AIRE_LUZ", M["interior"], col)
    # --- bajante con abrazaderas en la esquina del eje 1 (alzados SO y OESTE)
    bj = BAJANTE_OESTE
    bm = Malla()
    bm.cilindro_z(bj["x"], bj["y"], bj["z"][0], bj["z"][1], bj["d"] / 2)
    for zab in bj["abrazaderas"]:
        bm.caja(bj["x"] - 0.06, bj["x"] + 0.06, bj["y"] - 0.06, bj["y"] + 0.06, zab - 0.015, zab + 0.015)
    bm.crear("BAJANTE_OESTE", M["galvanizado"], col, suave=False)
    pf.crear("CARPINTERIAS_AIRE_PERFILES", M["perfil"], cc)
    vd.crear("CARPINTERIAS_AIRE_VIDRIOS", M["vidrio"], cc)
    pm.crear("PUERTAS_AIRE_ACERO", M["puerta"], cc)
    cm.crear("ENROLLABLES_AIRE_CORTINAS", M["cortina"], cc)
    gm.crear("ENROLLABLES_AIRE_GUIAS", M["galvanizado"], cc)


def testero_este(C, M):
    """Testero del eje 20 (FACHADA ESTE) según el alzado: rombos ME-3, tres puertas dobles con rejilla (dos detrás de las
    PT2), una puerta simple con rejilla y la boca de un patio techado de 3,21 m de alto (dos vanos a los lados de la
    columna del eje E), con su puerta al fondo y otra en el costado norte."""
    col, cc = C["02_ENVOLVENTE"], C["03_CARPINTERIAS_M1"]
    ax1 = ANEXO["x"][1]
    ay1 = ANEXO["y"][1]
    e = 0.15
    pt = PATIO_ESTE
    huecos = [rombo(cy, cz) for cy, cz in ME3_EJE20]
    huecos += [rect(a, b, 0.0005, 2.85) for a, b in PUERTAS_DOBLES_ESTE]
    huecos += [rect(a, b, 0.0005, 2.31) for a, b in PUERTAS_SIMPLES_ESTE]
    huecos += [rect(a, b, 0.0005, pt["z"]) for a, b in pt["bocas"]]
    placa_con_huecos("TESTERO_EJE_20", [rect(Y_COL_EXT, ay1, 0.0, ANEXO["z"])] + huecos, e, "YZ", ax1 - e / 2, M["muro"], col)
    for i, (cy, cz) in enumerate(ME3_EJE20):
        placa_con_huecos(f"ME3_EJE20_{i}_VIDRIO", [rombo(cy, cz, 1.12)], 0.027, "YZ", ax1 - 0.03, M["vidrio"], cc)
        placa_con_huecos(f"ME3_EJE20_{i}_MARCO", [rombo(cy, cz, 1.20), rombo(cy, cz, 1.016)], 0.10, "YZ", ax1 - 0.06,
                         M["perfil"], cc)
    pm, fm = Malla(), Malla()
    wc = ax1 - 0.06
    for a, b in PUERTAS_DOBLES_ESTE:
        puerta_batiente(pm, "YZ", a, b, 2.07, wc, +1, hojas=2)
        rejilla(pm, fm, "YZ", a, b, 2.07, 2.85, wc, +1)
    for a, b in PUERTAS_SIMPLES_ESTE:
        puerta_batiente(pm, "YZ", a, b, 2.02, wc, +1)
        rejilla(pm, fm, "YZ", a, b, 2.02, 2.31, wc, +1)
    # patio techado: piso, fondo (con puerta simple y rejilla), costados (puerta en el norte) y cielo a +3,21
    xf = pt["x_fondo"]
    xi = ax1 - e
    y0, y1 = pt["bocas"][0][0], pt["bocas"][-1][1]
    zc = pt["z"]
    pa, pb = pt["puerta_fondo"]
    placa_con_huecos("PATIO_ESTE_FONDO", [rect(y0 - e, y1 + e, 0.0, zc + e), rect(pa, pb, 0.0005, 2.31)], e, "YZ",
                     xf - e / 2, M["muro"], col)
    puerta_batiente(pm, "YZ", pa, pb, 2.02, xf - 0.06, +1)
    rejilla(pm, fm, "YZ", pa, pb, 2.02, 2.31, xf - 0.06, +1)
    la, lb = pt["puerta_lado"]
    placa_con_huecos("PATIO_ESTE_COSTADO_NORTE", [rect(xf, xi, 0.0, zc + e), rect(la, lb, 0.0005, 2.10)], e, "XZ",
                     y1 + e / 2, M["muro"], col)
    puerta_batiente(pm, "XZ", la, lb, 2.10, y1 + 0.06, -1)
    pz = Malla()
    pz.caja(xf, xi, y0 - e, y0, 0.0, zc + e)                                 # costado sur
    pz.caja(xf, xi, y0, y1, zc, zc + e)                                      # cielo
    pz.crear("PATIO_ESTE_MUROS", M["muro"], col)
    ps = Malla()
    ps.caja(xf, xi + 0.01, y0, y1, -0.05, 0.0)
    ps.crear("PATIO_ESTE_PISO", M["acera"], col)
    pm.crear("PUERTAS_ESTE_ACERO", M["puerta"], cc)
    fm.crear("PUERTAS_ESTE_REJILLAS_FONDO", M["plenum"], cc)


def borde_v(variante, u):
    """Altura del borde superior de la variante en la abscisa u (interpolación del polígono superior)."""
    pts = BORDE_SUPERIOR[variante]
    for (u0, v0), (u1, v1) in zip(pts, pts[1:]):
        if u0 <= u <= u1:
            return v0 + (v1 - v0) * (u - u0) / (u1 - u0)
    return pts[-1][1]


def elementos_laterales(C, M):
    """Elementos de los alzados laterales (pedido del 3 de octubre): rombo perforado y bloque bajo con mástil en la
    fachada OESTE (testero del eje 1) y franja de chapa nervada (color del parapeto) en la fachada ESTE (testero del eje 20)."""
    col = C["02_ENVOLVENTE"]
    # --- rombo perforado (montículo) sobre el ME-3: marco blanco, fondo oscuro y chapa blanca perforada
    r = ROMBO_OESTE
    xw = X_ALERO[0]                                   # cara exterior del testero del eje 1
    def rombo_semi(cy, cz, semi):
        return [(cy, cz - semi), (cy + semi, cz), (cy, cz + semi), (cy - semi, cz)]
    placa_con_huecos("ROMBO_OESTE_MARCO", [rombo_semi(r["y"], r["z"], r["semi_ext"]), rombo_semi(r["y"], r["z"], r["semi_int"])],
                     0.06, "YZ", xw - 0.03, M["letrero"], col)
    placa_con_huecos("ROMBO_OESTE_FONDO", [rombo_semi(r["y"], r["z"], r["semi_int"] + 0.01)], 0.006, "YZ", xw - 0.003,
                     M["plenum"], col)
    huecos, paso, rad = [], 0.09, 0.02
    n = int(r["semi_placa"] / paso) + 1
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            cy, cz = r["y"] + i * paso, r["z"] + j * paso
            if abs(cy - r["y"]) + abs(cz - r["z"]) <= r["semi_placa"] - 0.05:
                huecos.append([(cy + rad * math.cos(2 * math.pi * k / 10), cz + rad * math.sin(2 * math.pi * k / 10)) for k in range(10)])
    placa_con_huecos("ROMBO_OESTE_CHAPA_PERFORADA", [rombo_semi(r["y"], r["z"], r["semi_placa"])] + huecos, 0.003, "YZ",
                     xw - 0.04, M["letrero"], col)
    # --- bloque bajo del Lado Aire: mástil, volumen saliente y descanso con escalones
    mt = MASTIL_OESTE
    m = Malla()
    m.caja(mt["x"] - 0.10, mt["x"] + 0.10, mt["y"] - 0.10, mt["y"] + 0.10, mt["z_base"], mt["z_cambio"])
    m.caja(mt["x"] - 0.05, mt["x"] + 0.05, mt["y"] - 0.05, mt["y"] + 0.05, mt["z_cambio"], mt["z_tope"])
    m.crear("MASTIL_OESTE", M["galvanizado"], col)
    # caja de la puerta de embarque 1 (sobresale del bloque hacia la pista): frente vidriado como el del alzado SO,
    # costados y techo delgados, y piso al nivel de embarque
    cj = CAJA_OESTE
    (x0, x1), (y0, y1), (z0, z1) = cj["x"], cj["y"], cj["z"]
    c = Malla()
    c.caja(x0, x1, y0, y1, z0, EMBARQUE_Z[0])
    c.caja(x0, x1, y0, y1, EMBARQUE_Z[1], z1)
    for a, b in ((x0, x0 + 0.04), (x1 - 0.04, x1)):
        c.caja(a, b, y0, y1, EMBARQUE_Z[0], EMBARQUE_Z[1])
    c.crear("CAJA_EMBARQUE_OESTE", M["muro"], col)
    pf, vd = Malla(), Malla()
    vidriado_embarque(pf, vd, "XZ", x0 + 0.04, x1 - 0.04, y1 - 0.04)
    pf.crear("CAJA_EMBARQUE_OESTE_PERFILES", M["perfil"], C["03_CARPINTERIAS_M1"])
    vd.crear("CAJA_EMBARQUE_OESTE_VIDRIO", M["vidrio"], C["03_CARPINTERIAS_M1"])
    pf = PLATAFORMA_OESTE
    e = Malla()
    e.caja(pf["x"][0], pf["x"][1], pf["y"][0], pf["y"][1], 0.0, pf["z"])
    for k, h in enumerate((0.30, 0.15)):              # escalones de 0,15 hacia +X
        e.caja(pf["x"][1] + 0.30 * k, pf["x"][1] + 0.30 * (k + 1), pf["y"][0], pf["y"][1], 0.0, h)
    e.crear("DESCANSO_ESCALONES_OESTE", M["hormigon"], col)
    # --- franja nervada (color del parapeto) en el testero del eje 20 (+4,41 a +6,21)
    fr = FRANJA_ESTE
    xe = ANEXO["x"][1]
    f = Malla()
    f.caja(xe, xe + 0.02, fr["y"][0], fr["y"][1], fr["z"][0], fr["z"][1])
    f.crear("FRANJA_ESTE_CHAPA", M["antepecho"], col)
    nv = Malla()
    nv.caja(xe + 0.02, xe + 0.02 + NERVIO_ANTEPECHO, fr["y"][0] + 0.10, fr["y"][0] + 0.10 + NERVIO_SECCION[0], fr["z"][0], fr["z"][1])
    ob = nv.crear("FRANJA_ESTE_NERVIOS", M["antepecho"], col)
    arr = ob.modifiers.new("Array_0.30", "ARRAY")
    arr.use_relative_offset, arr.use_constant_offset = False, True
    arr.constant_offset_displace = (0, NERVIO_PASO, 0)
    arr.count = int((fr["y"][1] - fr["y"][0] - 0.12) / NERVIO_PASO) + 1


def recortar_celosia(ob, eje, minimo):
    """Recorta la chapa extruida en el encuentro y cierra sus cantos de 1 mm."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    # La conversión de curvas duplica vértices entre tapas y cantos. Soldarlos permite cerrar el nuevo corte.
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    punto, normal = Vector((0, 0, 0)), Vector((0, 0, 0))
    punto[eje], normal[eje] = minimo, 1.0
    corte = bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                                 dist=1e-7, plane_co=punto, plane_no=normal,
                                 clear_inner=True, clear_outer=False)
    cantos = [e for e in corte["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_boundary
              and all(abs(v.co[eje] - minimo) < 1e-6 for v in e.verts)]
    if cantos:
        bmesh.ops.holes_fill(bm, edges=cantos, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


def recortar_perfil_u(poly, minimo):
    """Corte en planta del perfil del bastidor; mantiene el ancho del tubo."""
    salida = []
    for p, q in zip(poly, poly[1:] + poly[:1]):
        dentro_p, dentro_q = p[0] >= minimo, q[0] >= minimo
        if dentro_p:
            salida.append(p)
        if dentro_p != dentro_q:
            t = (minimo - p[0]) / (q[0] - p[0])
            salida.append((minimo, p[1] + t * (q[1] - p[1])))
    return salida


def celosias(C, M):
    """Pantallas PT1/PT2 (corten en P1, blancas en P2): 15 planchas de 1,00 x 2,00 m (1 mm, juntas de 5 mm) con calados andinos (vacíos)
    sobre un bastidor de tubos de 40 x 40 que sigue las líneas salmón del CAD (verticales cada 1,00 m, horizontales
    cada 2,00 m y el borde superior), separado 0,12 m de su fondo."""
    col = C["05_CELOSIAS_CORTEN"]
    bast = Malla()
    xc, yc = X_ALERO[0] - CELOSIA_SEP, Y_COL_EXT - CELOSIA_SEP
    for i, (fach, variante, a, b) in enumerate(CELOSIAS):
        u0 = a
        plano = "XZ" if fach in ("NE", "SO") else "YZ"
        zb = Z_CELOSIA_FACHADA.get(fach, Z_CELOSIA)

        def tr(pts):
            return [(u0 + u, zb + v) for u, v in pts]
        anillos = []
        for pg in DATOS_GEOM[variante]:
            anillos.append(tr(pg["ext"]))
            anillos += [tr(h) for h in pg["holes"]]
        if fach == "NE":
            d, off = Y_COL_EXT - CELOSIA_SEP, 0.03
        elif fach == "SO":
            d, off = Y_CELOSIA_SO, -0.03
        elif fach == "EJE1":
            d, off = X_ALERO[0] - CELOSIA_SEP, 0.03
        else:
            d, off = ANEXO["x"][1] + CELOSIA_SEP, -0.03
        ob = placa_con_huecos(f"CELOSIA_{fach}_{variante}_{i:02d}", anillos, 0.001, plano, d, M["celosia"], col)
        esquina = fach == "NE" and a < xc < b or fach == "EJE1" and a < yc < b
        if esquina:
            limite = xc if fach == "NE" else yc
            recortar_celosia(ob, 0 if fach == "NE" else 1, limite + JUNTA_ESQUINA_NO)
            ob["junta_esquina_no_m"] = JUNTA_ESQUINA_NO
        # bastidor detrás de las planchas (eje del tubo a 3 cm de la plancha)
        miembros = [((u, 0.0), (u, borde_v(variante, u))) for u in range(6)]
        for v in (0.0, 2.0, 4.0):
            us = [k / 20 for k in range(101) if borde_v(variante, k / 20) >= v + 0.02]
            if us:
                miembros.append(((min(us), v), (max(us), v)))
        pts = BORDE_SUPERIOR[variante]
        miembros += list(zip(pts, pts[1:]))
        for (ua, va), (ub, vb) in miembros:
            dx, dz = ub - ua, vb - va
            ln = math.hypot(dx, dz) or 1.0
            nx, nz = -dz / ln * 0.02, dx / ln * 0.02
            poly = tr([(ua + nx, va + nz), (ub + nx, vb + nz), (ub - nx, vb - nz), (ua - nx, va - nz)])
            if esquina:
                # Los travesaños llegan al poste común; se suprimen los dos montantes que se cruzaban por fuera.
                poly = recortar_perfil_u(poly, limite + 0.05)
                if len(poly) < 3:
                    continue
            if plano == "XZ":
                bast.prisma_xz(poly, d + off - 0.02, d + off + 0.02)
            else:
                bast.prisma_yz(poly, d + off - 0.02, d + off + 0.02)
    # Un único tubo 40 x 40, detrás de ambos planos de chapa, resuelve la esquina del eje 1.
    z0 = min(Z_CELOSIA, Z_CELOSIA_FACHADA.get("EJE1", Z_CELOSIA)) - 0.02
    z1 = Z_CELOSIA_FACHADA.get("EJE1", Z_CELOSIA) + borde_v("PT1", 0)
    bast.caja(xc + 0.01, xc + 0.05, yc + 0.01, yc + 0.05, z0, z1)
    bast.crear("CELOSIAS_BASTIDOR", M["bastidor"], col)


def variantes_letrero():
    """Geometría del letrero: A como en el CAD (las letras sobresalen 25 cm arriba y 35 cm abajo del antepecho) y B
    contenida en los 2,40 m: horizonte al centro del antepecho y cada pieza (palabra, pirámide y su reflejo)
    reescalada sobre su propio eje, con LETRERO_B_MARGEN libre arriba y abajo. Devuelve {colección: (escala, z)}."""
    L = DATOS_GEOM["LETRERO"]
    zh = L["horizonte_z"]
    medio = (Z_ANTEPECHO[1] - Z_ANTEPECHO[0]) / 2
    alto_max = max(q[1] for pg in L["letras"] for q in pg["ext"]) - zh            # 1,50 m de las letras
    return {"LETRERO_A_SOBRESALE": (1.0, zh),
            "LETRERO_B_CONTENIDO": ((medio - LETRERO_B_MARGEN) / alto_max, Z_ANTEPECHO[0] + medio)}


def letrero(C, M):
    """Letrero "línea de horizonte" sobre el antepecho (CAD: fachada NE actual), con relieve y sombra propia.

    - Letras UYUNI corpóreas (1,50 m, trazo de 200 mm) sobre la línea de horizonte (+7,764), de 8 cm de espesor y
      despegadas 12 cm de la chapa: la sombra propia se separa de la pieza (efecto flotante).
    - Reflejo: las mismas letras espejadas bajo el horizonte, en contorno de 35 mm (5 cm de espesor).
    - Montículos de sal: pirámides facetadas en 3D. La arista frontal baja del vértice superior (en el plano del
      letrero) al centro de la base, que sobresale 15 cm (grandes, base de 2,00 m) o 10 cm (chicas, base de 1,00 m):
      la luz separa las dos caras en clara y oscura. Su reflejo debajo son marcos triangulares.
    - Línea de horizonte: pletina de X 40,976 a 72,252.
    - Juego asimétrico sin texto sobre la puerta de salida (grande + 2 chicas), con su tramo de horizonte y reflejos.
    Dos geometrías en colecciones hermanas (ver variantes_letrero): A visible y B excluida de las capas de vista.
    Material blanco o corten según la propiedad "letras_corten" de la escena; de noche las blancas brillan.
    """
    base = coleccion("LETRERO_HORIZONTE_UYUNI", C["02_ENVOLVENTE"])
    for nombre, (escala, zh_n) in variantes_letrero().items():
        letrero_variante(coleccion(nombre, base), M, escala, zh_n, "_" + nombre.split("_")[1])


def letrero_variante(col, M, s, zh_n, suf):
    L = DATOS_GEOM["LETRERO"]
    zh = L["horizonte_z"]
    y_nervios = Y_ANTEPECHO_EXT - NERVIO_ANTEPECHO
    y_plano = y_nervios - LETRERO_SEP                       # plano trasero del letrero
    def tf(cx):                                             # escala s sobre el eje x = cx y el horizonte
        return lambda u, v: (cx + (u - cx) * s, zh_n + (v - zh) * s)
    def anillos(piezas, f, dx=0.0):
        out = []
        for pg in piezas:
            out.append([f(u + dx, v) for u, v in pg["ext"]])
            out += [[f(u + dx, v) for u, v in h] for h in pg["holes"]]
        return out
    def pieza(nombre, anill, fondo):
        placa_con_huecos(nombre + suf, anill, fondo, "XZ", y_plano - fondo / 2, M["letrero"], col)
    xs_l = [q[0] for pg in L["letras"] for q in pg["ext"]]
    f_pal = tf((min(xs_l) + max(xs_l)) / 2)
    pieza("LETRERO_LETRAS_UYUNI", anillos(L["letras"], f_pal), LETRERO_FONDO["letras"])
    pieza("LETRERO_REFLEJO_UYUNI", anillos(L["reflejo"], f_pal), LETRERO_FONDO["reflejo"])
    # montículos: uno por cada reflejo (triángulo hacia abajo) del CAD; la altura sale de las mitades superiores
    def tipo(x0, x1):
        return "grande" if x1 - x0 > 1.5 else "chica"
    alto = {}
    for pg in L["rombos_sup"]:
        xs_, zs_ = [q[0] for q in pg["ext"]], [q[1] for q in pg["ext"]]
        alto[tipo(0, 2 * (max(xs_) - min(xs_)))] = max(zs_) - zh
    plantilla, montes = {}, []                              # (x0, x1, tipo, pieza del reflejo, desplazamiento)
    for pg in L["rombos_inf"]:
        xs_ = [q[0] for q in pg["ext"]]
        plantilla.setdefault(tipo(min(xs_), max(xs_)), (min(xs_), pg))
        montes.append((min(xs_), max(xs_), tipo(min(xs_), max(xs_)), pg, 0.0))
    xs_sal = LETRERO_SALIDA["x0"]                           # juego de la puerta de salida: mismas piezas, desplazadas
    for t in LETRERO_SALIDA["piezas"]:
        x_tpl, pg = plantilla[t]
        ancho = max(q[0] for q in pg["ext"]) - x_tpl
        montes.append((xs_sal, xs_sal + ancho, t, pg, xs_sal - x_tpl))
        xs_sal += ancho
    marcos = []
    pm = Malla()
    zb = zh_n + 0.0135                                      # 1 mm sobre la pletina: sin caras coplanares
    for x0, x1, t, pg, dx in montes:
        xm = (x0 + x1) / 2
        f = tf(xm)
        marcos += anillos([pg], f, dx)
        i = len(pm.v)
        (xi, _), (xd, _), (_, zv) = f(x0 + 0.005, zh), f(x1 - 0.005, zh), f(xm, zh + alto[t])
        pm.v += [(xi, y_plano, zb), (xd, y_plano, zb), (xm, y_plano, zv),
                 (xm, y_plano - PIRAMIDE_FONDO[t], zb)]     # izquierda, derecha, vértice, centro de la base al frente
        pm.f += [(i, i + 2, i + 1), (i, i + 1, i + 3), (i, i + 3, i + 2), (i + 1, i + 2, i + 3)]
    pieza("LETRERO_REFLEJO_MONTICULOS", marcos, LETRERO_FONDO["marcos"])
    pm.crear("LETRERO_PIRAMIDES_SAL_3D" + suf, M["letrero"], col)
    h = Malla()
    for hx0, hx1 in (L["horizonte_x"], LETRERO_SALIDA["horizonte"]):
        h.caja(hx0, hx1, y_plano - LETRERO_FONDO["horizonte"], y_plano, zh_n - 0.0125, zh_n + 0.0125)
    h.crear("LETRERO_LINEA_HORIZONTE" + suf, M["letrero"], col)
    sop = Malla()   # separadores ocultos: dentro del trazo de cada letra (no en sus huecos) y de cada pirámide
    centros = [((x0 + x1) / 2, zh_n + alto[t] * s / 3) for x0, x1, t, _, _ in montes]
    for pg in L["letras"]:
        xs_ = [q[0] for q in pg["ext"]]
        for z in (zh + 0.10, zh + 1.40):
            tramos, ini = [], None
            for k in range(int((max(xs_) - min(xs_)) / 0.01) + 1):
                x = min(xs_) + k * 0.01
                if dentro_poligono(x, z, pg["ext"]):
                    ini = x if ini is None else ini
                elif ini is not None:
                    tramos.append((ini, x - 0.01))
                    ini = None
            if ini is not None:
                tramos.append((ini, max(xs_)))
            tramos = [t_ for t_ in tramos if t_[1] - t_[0] >= 0.06]
            for a_, b_ in {tramos[0], tramos[-1]} if tramos else ():
                centros.append(f_pal((a_ + b_) / 2, z))
    for cx, cz in centros:
        sop.caja(cx - 0.02, cx + 0.02, y_plano, y_nervios, cz - 0.02, cz + 0.02)
    sop.crear("LETRERO_SEPARADORES" + suf, M["bastidor"], col)


def entorno(C, M):
    """Lado Tierra según la planta baja A111: vereda hasta el cordón (con sus dos dársenas), zanja de drenaje con rejilla
    bajo el goterón del alero y cordón. Fuera de la A111, el frente según el modelo del cliente (frente_lado_tierra:
    calzada, jardineras, plaza y señalización). Después llama al Lado Aire, al contexto del aeropuerto (pista y
    rodaje), al terreno y a la paja brava."""
    col = C["06_ENTORNO_SITE"]
    cord = cordon_tierra()
    inv = cord[::-1]                                                 # de este a oeste: la vereda queda a la derecha
    za, zb = ZANJA["y"]
    xz0, xz1 = X_ALERO
    # vereda 2 mm bajo el cordón, con el borde 1 cm dentro de él (sin caras coplanares) y el hueco de la zanja
    placa_con_huecos("VEREDA_TIERRA", [paralela_derecha(inv, 0.01), rect(xz0, xz1, za, zb)], 0.198, "XY", -0.101,
                     M["acera"], col)
    placa_con_huecos("CORDON_TIERRA", [franja_derecha(inv, 0.15)], 0.25, "XY", -0.125, M["hormigon"], col)
    zj = Malla()   # zanja en U de hormigón (0,50 x 0,20) con rejilla galvanizada, a lo largo del alero
    zj.caja(xz0, xz1, za, zb, -ZANJA["prof"] - 0.10, -ZANJA["prof"])
    zj.crear("ZANJA_DRENAJE", M["hormigon"], col)
    rj = Malla()
    yy = za + 0.02
    while yy < zb - 0.02:
        rj.caja(xz0, xz1, yy, yy + 0.005, -0.035, -0.005)
        yy += 0.035
    rj.crear("ZANJA_REJILLA", M["galvanizado"], col)
    frente_lado_tierra(col, M, cord)
    # sin bolardos ni postes de iluminación peatonal: no están en el presupuesto (reunión del 3 de octubre)
    entorno_aire(C, M)
    contexto_aeropuerto(C, M)
    terreno(C, M)
    paja_brava(C, M)


def arco(cx, cy, r, a0, a1, n=8):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
            for k in range(n + 1)]


def sin_repetidos(pts, tol=1e-6):
    out = []
    for p in pts:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > tol:
            out.append(p)
    return out


def paralela_derecha(pts, ancho):
    """Polilínea paralela a pts, a 'ancho' a su derecha (negativo: a la izquierda), con uniones a inglete."""
    pts = sin_repetidos(pts)
    def nor(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy)
        return dy / l, -dx / l
    off = []
    for i, p in enumerate(pts):
        if i in (0, len(pts) - 1):
            n = nor(pts[0], pts[1]) if i == 0 else nor(pts[-2], pts[-1])
            off.append((p[0] + n[0] * ancho, p[1] + n[1] * ancho))
            continue
        n1, n2 = nor(pts[i - 1], p), nor(p, pts[i + 1])
        mx, my = n1[0] + n2[0], n1[1] + n2[1]
        ml = math.hypot(mx, my)
        mx, my = (mx / ml, my / ml) if ml > 1e-9 else n1
        d = ancho / max(mx * n1[0] + my * n1[1], 0.3)
        off.append((p[0] + mx * d, p[1] + my * d))
    return off


def franja_derecha(pts, ancho):
    """Polígono de una franja de 'ancho' a la derecha de la polilínea pts (uniones a inglete)."""
    pts = sin_repetidos(pts)
    return pts + paralela_derecha(pts, ancho)[::-1]


def contraer(pol, d):
    """Polígono cerrado antihorario contraído d hacia adentro (uniones a inglete)."""
    pol = sin_repetidos(pol)
    n = len(pol)
    out = []
    for i in range(n):
        a, p, b = pol[i - 1], pol[i], pol[(i + 1) % n]
        normales = []
        for u, v in ((a, p), (p, b)):
            dx, dy = v[0] - u[0], v[1] - u[1]
            l = math.hypot(dx, dy)
            normales.append((-dy / l, dx / l))                       # izquierda = adentro
        (n1x, n1y), (n2x, n2y) = normales
        mx, my = n1x + n2x, n1y + n2y
        ml = math.hypot(mx, my)
        mx, my = (mx / ml, my / ml) if ml > 1e-9 else (n1x, n1y)
        k = d / max(mx * n1x + my * n1y, 0.3)
        out.append((p[0] + mx * k, p[1] + my * k))
    return out


def rect_redondeado(x0, x1, y0, y1, r, n=4):
    """Rectángulo antihorario con las esquinas redondeadas (radio r)."""
    r = min(r, (x1 - x0) / 2 - 1e-4, (y1 - y0) / 2 - 1e-4)
    return sin_repetidos(arco(x1 - r, y0 + r, r, 270, 360, n) + arco(x1 - r, y1 - r, r, 0, 90, n)
                         + arco(x0 + r, y1 - r, r, 90, 180, n) + arco(x0 + r, y0 + r, r, 180, 270, n))


def largo_darsena():
    """Largo total de una dársena del Lado Tierra: dos rampas a 45° (con sus curvas) y el tramo recto."""
    f, l, r = DARSENA["fondo"], DARSENA["recto"], DARSENA["r"]
    return 2 * (f + 2 * r * (math.sqrt(2) - 1)) + l


def darsena(x0):
    """Cordón de una dársena (planta A111) de oeste a este: sube a 45° hasta 2,10 m más adentro, sigue recto y vuelve."""
    f, l, r = DARSENA["fondo"], DARSENA["recto"], DARSENA["r"]
    yc, yd = Y_CORDON_TIERRA, Y_CORDON_TIERRA + f
    dx = f + 2 * r * (math.sqrt(2) - 1)                              # avance de cada rampa con sus dos curvas
    return (arco(x0, yc + r, r, 270, 315, 4) + arco(x0 + dx, yd - r, r, 135, 90, 4)
            + arco(x0 + dx + l, yd - r, r, 90, 45, 4) + arco(x0 + 2 * dx + l, yc + r, r, 225, 270, 4))


def cordon_tierra():
    """Cordón del Lado Tierra (A111, capa A-FLOR) de oeste a este: del cordón lateral oeste a la esquina en curva (r
    4,021 y contracurva de r 1,0), la línea de -8,413 con sus dos dársenas y la esquina este (r 1,0) hasta el cordón
    lateral este. Empieza y termina en el plano del muro (Y 0,392), donde siguen los tramos de cordon_aire."""
    xo, xe = X_CORDON_LATERAL
    yc = Y_CORDON_TIERRA
    pts = [(xo, Y_MURO_EXT)] + arco(0.45, -1.423, 4.021, 180, 260.7, 10) + arco(-0.57, -6.322, 1.0, 68.3, 0, 6)
    pts += arco(1.43, yc + 1.0, 1.0, 180, 270, 6)
    for x0 in DARSENAS_TIERRA:
        pts += darsena(x0)
    pts += arco(xe - 1.0, yc + 1.0, 1.0, 270, 360, 6) + [(xe, Y_MURO_EXT)]
    return sin_repetidos(pts)


def ese(p0, p1, n=12):
    """Transición suave entre dos tramos paralelos a X: avance lineal en X y coseno en Y (tangente horizontal en los
    dos extremos)."""
    (x0, y0), (x1, y1) = p0, p1
    return [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * (1 - math.cos(math.pi * k / n)) / 2) for k in range(n + 1)]


def jardinera_a():
    """Jardinera A (al oeste del eje 1): borde norte recto en -19,5; al sur, un arco de r 10,37 al oeste y otro de
    r 9,0 al este unidos por un tramo recto en -26,85 (forma de casco, más ancha al oeste). Contorno antihorario."""
    yn, ys = -19.5, -26.85
    (xo, ro), (xe, re) = (-15.58, 10.37), (-6.3, 9.0)
    a0 = 180 + math.degrees(math.asin((ys + ro - yn) / ro))          # donde el arco oeste corta el borde norte
    a1 = 360 - math.degrees(math.asin((ys + re - yn) / re))          # y donde lo corta el arco este
    return sin_repetidos(arco(xo, ys + ro, ro, a0, 270, 16) + arco(xe, ys + re, re, 270, a1, 16))


def jardinera_b():
    """Jardinera B (de X 6 a la esquina este): punta oeste redondeada (r 1,0) que aloja un anillo, panza ancha entre
    X 21 y 36, tramo medio de 4,6 m y extremo este redondeado (r 3,475), de nuevo ancho. Contorno antihorario."""
    pts = arco(7.0, -25.4, 1.0, 117.6, 270, 8)
    pts += ese((29.6, -26.4), (35.8, -23.6)) + ese((64.7, -23.6), (70.0, -25.95))
    pts += arco(78.83, -22.475, 3.475, 270, 450, 16)
    pts += ese((27.0, -19.0), (21.4, -22.1)) + [(11.15, -22.1)]
    return sin_repetidos(pts)


def anillo(cx, cy, largo, ancho, d=0.0):
    """Contorno antihorario de un anillo alargado (rectángulo con extremos semicirculares), d más adentro."""
    l, w = largo - 2 * d, ancho - 2 * d
    return rect_redondeado(cx - l / 2, cx + l / 2, cy - w / 2, cy + w / 2, w / 2, 8)


def hexagono(cx, cy, r):
    """Hexágono regular antihorario con vértices hacia ±X (radio al vértice r)."""
    return [(cx + r * math.cos(math.radians(60 * k)), cy + r * math.sin(math.radians(60 * k))) for k in range(6)]


def ese_x(p0, p1, n=12):
    """Transición suave entre dos tramos paralelos a Y: avance lineal en Y y coseno en X."""
    (x0, y0), (x1, y1) = p0, p1
    return [(x0 + (x1 - x0) * (1 - math.cos(math.pi * k / n)) / 2, y0 + (y1 - y0) * k / n) for k in range(n + 1)]


def calzada_frente(cord):
    """Contorno antihorario del asfalto del Lado Tierra. Igual que antes junto al edificio: 5 cm bajo todo el cordón
    A111 (dársenas incluidas) y las calles de los testeros de 7 m hasta la plataforma. Nuevo, en el frente: la calzada
    hasta el separador L1 (5 cm debajo), su prolongación hacia Uyuni por el oeste (curva de r 8 desde la calle del eje
    1) y, al sur, la calle del eje 20 (curva de r 12 desde L1 y empalme suave con la calle del testero)."""
    F, O, V = FRENTE, FRENTE["oeste"], FRENTE["via_este"]
    xo, xe = X_CORDON_LATERAL
    w, ya, R = CALLE_ANCHO, PLATAFORMA_AIRE["y"][0], V["r"]
    (vx0, vx1), (e0, e1) = V["x_sur"], V["empalme"]
    ys, y1 = O["y_sur"] - 0.05, F["y_l1"] - 0.05
    borde = paralela_derecha(cord[::-1], 0.05)                       # de este a oeste, 5 cm bajo el cordón
    pts = [(O["x"][0], ys), (O["x"][1], ys)] + ese((O["x"][1], ys), (F["x_l1"][0], y1))[1:]
    pts += [(F["x_l1"][1], y1)] + arco(F["x_l1"][1], F["y_l1"] - R, R - 0.05, 90, 0, 8)[1:]
    pts += [(vx0 - 0.05, V["y_sur"]), (vx1, V["y_sur"])] + ese_x((vx1, e1), (xe + w, e0))
    pts += [(xe + w, ya), (xe - 0.05, ya)] + borde + [(xo + 0.05, ya), (xo - w, ya)]
    pts += arco(xo - w - 8.0, O["y_norte"] + 8.0, 8.0, 0, -90, 6) + [(O["x"][0], O["y_norte"])]
    return sin_repetidos(pts)


def separador_l1():
    """Polilíneas del separador amarillo, de oeste a este (la franja queda a su derecha): borde sur del acceso, curva
    hasta L1, L1 frente a la plaza y curva hacia la calle del eje 20."""
    F, O, V = FRENTE, FRENTE["oeste"], FRENTE["via_este"]
    oeste = [(O["x"][1] - 23.0, O["y_sur"])] + ese((O["x"][1], O["y_sur"]), (F["x_l1"][0], F["y_l1"]))
    R = V["r"]
    este = arco(F["x_l1"][1], F["y_l1"] - R, R, 90, 0, 8) + [(V["x_sur"][0], -60.0)]
    return oeste, [(F["x_l1"][0], F["y_l1"]), (F["x_l1"][1], F["y_l1"])], este


def espiga():
    """Las dos líneas en zigzag a 45° de la plaza, del andén al hexágono este."""
    E = ESPIGA
    p, a = E["paso"], E["amplitud"]
    x0, y0, xv, yv, n = E["sup"]
    sup = [(x0, y0)]
    for k in range(n):
        sup += [(xv + k * p, yv), (xv + k * p + p / 2, yv + a)]
    sup.append((E["x_fin"], yv + a - (E["x_fin"] - sup[-1][0])))
    xi, yi, m = E["inf"]
    inf = []
    for k in range(m):
        inf += [(xi + k * p, yi), (xi + k * p + p / 2, yi + a)]
    return sup, inf


def linea_jardinera_b():
    """Línea amarilla a JARDINERAS["linea_b"] del borde de la jardinera B: borde sur desde X 36, extremo este y vuelta
    por el norte hasta lo alto del arco."""
    pol = jardinera_b()
    i0 = next(i for i, p in enumerate(pol) if abs(p[0] - 35.8) < 1e-6)
    i1 = next(i for i, p in enumerate(pol) if abs(p[0] - 78.83) < 1e-6 and abs(p[1] + 19.0) < 1e-6)
    return paralela_derecha(pol[i0:i1 + 1], JARDINERAS["linea_b"])


def frente_lado_tierra(col, M, cord):
    """Frente del Lado Tierra según las capturas del modelo del cliente (ver FRENTE): asfalto de la calzada, del acceso
    y de las calles laterales; jardineras A y B (tierra oscura con cordón de hormigón) con sus
    anillos elevados blancos; separador amarillo; plaza de estacionamiento con cordones, hexágonos elevados y espiga;
    andenes del bus, cebra, tapas y columnas amarillas, recuadros frente a las ME-2 y la pintura vial. La vereda y el
    cordón A111 (cord) no cambian: el asfalto y las dársenas entran 5 cm bajo el cordón."""
    z1 = -BORDILLO_DESNIVEL                                          # cara superior del asfalto
    J, A = JARDINERAS, JARDINERAS["anillo"]
    jard = [jardinera_a(), jardinera_b()]
    huecos = [contraer(p, 0.05) for p in jard]                      # el asfalto entra 5 cm bajo el cordón
    placa_con_huecos("CALZADA_ASFALTO", [calzada_frente(cord)] + huecos, 0.10, "XY", z1 - 0.05, M["asfalto"], col)
    pl = FRENTE["plaza"]
    placa_con_huecos("FRENTE_PLAZA_ASFALTO", [contraer(pl, -0.05)], 0.10, "XY", z1 - 0.05, M["asfalto"], col)
    # jardineras: cordón de hormigón de 0,15 al ras de la vereda y tierra 4 cm más abajo
    tierra = [contraer(p, J["cordon"]) for p in jard]
    placa_con_huecos("FRENTE_JARDINERAS_CORDON", [q for par in zip(jard, tierra) for q in par], 0.25, "XY", -0.125,
                     M["hormigon"], col)
    placa_con_huecos("FRENTE_JARDINERAS_TIERRA", tierra, 0.20, "XY", -0.14, M["tierra"], col)
    # anillos elevados blancos (0,45 sobre la calzada) con su tierra; hexágonos elevados de la plaza, sin relleno
    za = z1 + A["alto"]
    anillos = [anillo(*a) for a in J["anillos"]]
    dentro = [anillo(*a, d=A["espesor"]) for a in J["anillos"]]
    r_in = A["espesor"] / math.cos(math.radians(30))
    hexs = [q for cx, cy, r in J["hexagonos"] for q in (hexagono(cx, cy, r), hexagono(cx, cy, r - r_in))]
    placa_con_huecos("FRENTE_ANILLOS_BLANCOS", [q for par in zip(anillos, dentro) for q in par] + hexs, za + 0.20,
                     "XY", (za - 0.20) / 2, M["hormigon_blanco"], col)
    placa_con_huecos("FRENTE_ANILLOS_TIERRA", dentro, za - 0.07, "XY", (za - 0.13) / 2, M["tierra"], col)
    # cordones amarillos (+0,15): separador L1 de 0,60 y su continuación de 0,25, borde sur de la plaza de 0,30;
    # cordones grises de 0,20 en los otros bordes de la plaza; espiga de 0,20 x 0,10
    oeste, l1, este = separador_l1()
    am = [franja_derecha(oeste, 0.25), franja_derecha(l1, FRENTE["ancho_l1"]), franja_derecha(este, 0.25),
          franja_derecha(pl[4:7], 0.30)]
    placa_con_huecos("FRENTE_CORDONES_AMARILLOS", am, 0.25, "XY", -0.125, M["cordon_amarillo"], col)
    placa_con_huecos("FRENTE_PLAZA_CORDONES", [franja_derecha(pl[0:5], 0.20), franja_derecha(pl[6:8], 0.20)], 0.25,
                     "XY", -0.125, M["hormigon"], col)
    zz = Malla()
    for linea in espiga():
        for p, q in zip(linea, linea[1:]):
            zz.caja_eje((p[0], p[1], z1), (q[0], q[1], z1), 0.20, 0.15, 0.05)
    zz.crear("FRENTE_ESPIGA_CORDONES", M["cordon_amarillo"], col)
    # andenes del bus (+0,15, hormigón de vereda) y columnas amarillas de la isla sudeste
    an = Malla()
    for x0, x1, y0, y1 in ANDENES:
        an.caja(x0, x1, y0, y1, -0.25, 0.0)
    an.crear("FRENTE_ANDENES_BUS", M["acera"], col)
    co = Malla()
    for x, y in COLUMNAS["pos"]:
        co.cilindro_z(x, y, -0.30, z1 + COLUMNAS["alto"], COLUMNAS["diametro"] / 2, 32)
    co.crear("FRENTE_COLUMNAS_AMARILLAS", M["cordon_amarillo"], col, suave=True)
    # pintura, 2 mm sobre el asfalto: discontinua de los carriles de llegada, líneas amarillas, cebra y tapas
    sv, sa = Malla(), Malla()
    C = FRENTE["carril"]
    x = C["x0"] - C["paso"] * math.ceil((C["x0"] - C["x"][0]) / C["paso"])
    while x + C["trazo"] <= C["x"][1]:
        sv.caja(x, x + C["trazo"], C["y"] - 0.06, C["y"] + 0.06, z1, z1 + 0.002)
        x += C["paso"]
    for linea in (FRENTE["linea_cordon"], linea_jardinera_b()):
        for p, q in zip(linea, linea[1:]):
            sa.caja_eje((p[0], p[1], z1), (q[0], q[1], z1), 0.15, 0.002)
    ce = CEBRA
    y = ce["y"][0] + 0.25
    while y + ce["franja"] <= ce["y"][1] - 0.2:                      # franjas de 0,50 cada 1,00 m
        sv.caja(ce["x"][0], ce["x"][1], y, y + ce["franja"], z1, z1 + 0.002)
        y += ce["paso"]
    for x, y in DISCOS:
        sa.cilindro_z(x, y, z1, z1 + 0.004, 0.35, 24)
    pm = Malla()                                                     # frente a cada ME-2: recuadro claro con borde blanco
    for x0, x1 in ME2:
        a, b = x0 - FRENTE["me2"]["margen"], x1 + FRENTE["me2"]["margen"]
        y0, y1 = Y_CORDON_TIERRA - FRENTE["me2"]["fondo"], Y_CORDON_TIERRA - 0.05
        pm.caja(a, b, y0, y1, z1, z1 + 0.003)
        for u0, u1, v0, v1 in ((a, b, y0, y0 + 0.15), (a, a + 0.15, y0, y1), (b - 0.15, b, y0, y1)):
            sv.caja(u0, u1, v0, v1, z1 + 0.003, z1 + 0.005)
    pm.crear("FRENTE_PASOS_ME2", M["acera"], col)
    sv.crear("SENALIZACION_VIAL", M["senal"], col)
    sa.crear("SENALIZACION_VIAL_AMARILLA", M["senal_amarilla"], col)


def cordon_aire():
    """Cordón de la vereda del Lado Aire y de los laterales (planta baja A111, capa A-FLOR), en dos tramos: del Lado
    Tierra oeste a la esquina del bloque del eje R, y del frente de la marquesina al Lado Tierra este. Entre los dos,
    la dársena a nivel de calzada que llega al muro lateral del bloque."""
    y0 = Y_MURO_EXT
    a = ([(-3.57, y0)] + arco(-2.57, 49.779, 1.0, 180, 90) + arco(18.4, 49.779, 1.0, 90, 0)
         + [(19.4, 48.601), (X_CAMBIO_AIRE, 48.601)])
    b = ([(X_CAMBIO_AIRE, 46.779), (27.941, 46.779), (27.941, 49.079)] + arco(84.515, 48.079, 1.0, 90, 0)
         + [(85.515, y0)])
    return sin_repetidos(a), sin_repetidos(b)


def entorno_aire(C, M):
    """Lado Aire: veredas y cordón según la planta baja A111 (laterales, frente del bloque, bajo la marquesina y a lo
    largo de la fachada), plataforma de hormigón, camino de servicio de asfalto (la banda azul de la vista aérea del
    cliente) y marcas: bordes y eje del camino en blanco, calle de rodaje, guías y barras de parada en amarillo. Las
    calles de los testeros (entorno) llegan al borde de la plataforma."""
    col = C["06_ENTORNO_SITE"]
    ta, tb = cordon_aire()
    yI, yR = Y_FACHADA_AIRE["principal_der"], Y_FACHADA_AIRE["principal_izq"]
    ax1, ay1 = ANEXO["x"][1], ANEXO["y"][1]
    vs, ni = VESTIBULO_AIRE, NICHO_AIRE
    # el borde de cada vereda va 1 cm dentro del cordón, para que sus caras no coincidan con las del cordón
    oeste = paralela_derecha(ta, 0.01) + [(X_ALERO[0], yR), (X_ALERO[0], Y_MURO_EXT)]
    este = paralela_derecha(tb, 0.01) + [(ax1, Y_MURO_EXT), (ax1, ay1), (X_ALERO[1], ay1), (X_ALERO[1], yI),
                                         (vs["x"][1], yI), (vs["x"][1], vs["y"][1]), (vs["x"][0], vs["y"][1]),
                                         (vs["x"][0], yI), (ni["x"][1], yI), (ni["x"][1], ni["y"][0]),
                                         (ni["x"][0], ni["y"][0]), (ni["x"][0], yI), (X_CAMBIO_AIRE, yI)]
    for nombre, pol in (("VEREDA_AIRE_OESTE", oeste), ("VEREDA_AIRE_ESTE", este)):   # 2 mm bajo el cordón
        placa_con_huecos(nombre, [pol], 0.198, "XY", -0.101, M["acera"], col)
    for i, tramo in enumerate((ta, tb)):
        placa_con_huecos(f"CORDON_AIRE_{i}", [franja_derecha(tramo, 0.15)], 0.25, "XY", -0.125, M["hormigon"], col)
    (px0, px1), (py0, py1) = PLATAFORMA_AIRE["x"], PLATAFORMA_AIRE["y"]
    cy0, cy1 = CAMINO_AIRE_Y
    z0, z1 = -BORDILLO_DESNIVEL - 0.10, -BORDILLO_DESNIVEL
    pa = Malla()
    pa.caja(px0, px1, py0, cy0, z0, z1)
    pa.caja(px0, px1, cy1, py1, z0, z1)
    pa.crear("PLATAFORMA_AIRE_HORMIGON", M["plataforma"], col)
    cm = Malla()
    cm.caja(px0, px1, cy0, cy1, z0, z1)
    cm.crear("CAMINO_SERVICIO_AIRE", M["asfalto"], col)
    zs0, zs1 = z1, z1 + 0.002
    bl = Malla()                                                     # camino: bordes continuos y eje discontinuo
    bl.caja(px0, px1, cy0 + 0.15, cy0 + 0.27, zs0, zs1)
    bl.caja(px0, px1, cy1 - 0.27, cy1 - 0.15, zs0, zs1)
    x = px0
    while x < px1:
        bl.caja(x, x + 3.0, (cy0 + cy1) / 2 - 0.06, (cy0 + cy1) / 2 + 0.06, zs0, zs1)
        x += 6.0
    bl.crear("CAMINO_SERVICIO_AIRE_MARCAS", M["senal"], col)
    am = Malla()                         # calle de rodaje de la plataforma (sigue a la pista en contexto_aeropuerto)
    am.caja(px0 + 15.0, RODAJE["x"] - RODAJE["r_plataforma"], CALLE_RODAJE_Y - 0.075, CALLE_RODAJE_Y + 0.075, zs0, zs1)
    for nx, ny, ang in puestos_aviones():
        h = (math.cos(ang), math.sin(ang))
        sx, sy = nx - 4.8 * h[0], ny - 4.8 * h[1]                   # parada de la rueda de nariz
        am.caja_rotada(sx - 17.5 * h[0], sy - 17.5 * h[1], 35.0, 0.15, zs0, zs1, ang)
        am.caja_rotada(sx, sy, 0.30, 4.0, zs0, zs1, ang)
    am.crear("PLATAFORMA_MARCAS_AMARILLAS", M["senal_amarilla"], col)


def suave(a, b, x):
    """Escalón suave (smoothstep) de 0 en a a 1 en b."""
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def linea(m, pts, ancho, z=-BORDILLO_DESNIVEL):
    """Pintura de 'ancho' a lo largo de la polilínea pts (tramos rectos de 2 mm de espesor sobre la cota z)."""
    for a, b in zip(pts, pts[1:]):
        m.caja_eje((a[0], a[1], z), (b[0], b[1], z), ancho, 0.002)


# trazos de las cifras de designación de pista (u, v) en una caja de 3 x 9 m con trazo de 0,9 m (OACI, simplificadas)
DIGITOS = {"1": [(1.05, 1.95, 0.0, 9.0)],
           "3": [(0.0, 3.0, 8.1, 9.0), (0.6, 3.0, 4.05, 4.95), (0.0, 3.0, 0.0, 0.9), (2.1, 3.0, 0.0, 9.0)]}


def designacion(m, texto, xd, yc, s, z):
    """Cifras de 9 m sobre la pista, legibles desde la aproximación (el avión avanza hacia s·X): u crece a la derecha del
    piloto (-s·Y) y v hacia adelante, desde xd."""
    ancho = 3.0 * len(texto) + 1.5 * (len(texto) - 1)
    for i, ch in enumerate(texto):
        u0 = -ancho / 2 + 4.5 * i
        for ua, ub, va, vb in DIGITOS[ch]:
            m.caja(xd + s * va, xd + s * vb, yc - s * (u0 + ua), yc - s * (u0 + ub), z, z + 0.002)


def contexto_aeropuerto(C, M):
    """Pista 13/31 con marcas OACI (umbral, designación, eje, punto de visada, zona de toma de contacto y bordes) y
    zonas de parada con chevrones; calle de rodaje de la plataforma a la pista con su eje, punto de espera y curvas de
    entrada; manga de viento. La Y de la pista es supuesta (ver PISTA)."""
    col = C["11_CONTEXTO_AEROPUERTO"]
    P, Rd = PISTA, RODAJE
    yc, sa = P["y"], P["ancho"] / 2
    x31, x13 = P["x"]
    z1 = -BORDILLO_DESNIVEL
    pv = Malla()
    pv.caja(x31 - P["sobrepaso"], x13 + P["sobrepaso"], yc - sa, yc + sa, z1 - 0.10, z1)
    pv.crear("PISTA_13_31_ASFALTO", M["asfalto"], col)
    xr, ar, rf = Rd["x"], Rd["ancho"] / 2, 20.0
    py1 = PLATAFORMA_AIRE["y"][1]
    rodaje = (arco(xr - ar - rf, py1 + rf, rf, 270, 360, 6) + arco(xr - ar - rf, yc - sa - rf, rf, 0, 90, 6)
              + arco(xr + ar + rf, yc - sa - rf, rf, 90, 180, 6) + arco(xr + ar + rf, py1 + rf, rf, 180, 270, 6))
    placa_con_huecos("CALLE_RODAJE_ASFALTO", [sin_repetidos(rodaje)], 0.10, "XY", z1 - 0.05, M["asfalto"], col)
    mb, ma = Malla(), Malla()                                        # pintura blanca (pista) y amarilla
    def pinta(m, x0, x1, y0, y1):
        m.caja(x0, x1, y0, y1, z1, z1 + 0.002)
    for xt, s, nombre in ((x31, 1, P["nombres"][0]), (x13, -1, P["nombres"][1])):
        for k in range(6):                                           # umbral: 12 franjas de 30 x 1,6 m
            for lado in (1, -1):
                yy = yc + lado * (2.4 + 3.2 * k)
                pinta(mb, xt + s * 6, xt + s * 36, yy - 0.8, yy + 0.8)
        designacion(mb, nombre, xt + s * 48, yc, s, z1)              # a 12 m de las franjas
        for lado in (1, -1):
            pinta(mb, xt + s * 400, xt + s * 445, yc + lado * 9, yc + lado * 15)      # punto de visada
            for dist, n in ((150, 3), (300, 3), (600, 2), (750, 2), (900, 1), (1050, 1)):   # toma de contacto
                for j in range(n):
                    a = 9 + 4.5 * j
                    pinta(mb, xt + s * dist, xt + s * (dist + 22.5), yc + lado * a, yc + lado * (a + 3))
        for k in range(2):                                           # zona de parada: chevrones hacia el umbral
            xa = xt - s * (15 + 30 * k)
            for lado in (1, -1):
                linea(ma, [(xa, yc), (xa - s * (sa - 1.5), yc + lado * (sa - 1.5))], 0.9)
    x = x31 + 69
    while x + 30 < x13 - 69:                                         # eje: trazos de 30 m cada 50 m
        pinta(mb, x, x + 30, yc - 0.225, yc + 0.225)
        x += 50
    for lado in (1, -1):                                             # bordes de 0,90, cortados en la calle de rodaje
        yb = yc + lado * (sa - 0.45)
        tramos = [(x31, x13)] if lado == 1 else [(x31, xr - ar - rf), (xr + ar + rf, x13)]
        for a, b in tramos:
            pinta(mb, a, b, yb - 0.45, yb + 0.45)
    rp, rpi = Rd["r_plataforma"], Rd["r_pista"]
    linea(ma, arco(xr - rp, CALLE_RODAJE_Y + rp, rp, 270, 360, 8) + [(xr, yc - rpi)], 0.15)   # eje del rodaje
    for sgn in (1, -1):                                              # curvas de entrada al eje de la pista
        linea(ma, arco(xr - sgn * rpi, yc - rpi, rpi, 0 if sgn == 1 else 180, 90, 10), 0.15)
    yh = yc - Rd["espera"]                                           # punto de espera (patrón A)
    for y0, continua in ((yh - 0.90, True), (yh - 0.60, True), (yh - 0.15, False), (yh + 0.15, False)):
        x = xr - ar
        while x < xr + ar:
            pinta(ma, x, xr + ar if continua else min(x + 0.9, xr + ar), y0, y0 + 0.15)
            x = xr + ar if continua else x + 1.8
    mb.crear("PISTA_MARCAS_BLANCAS", M["senal"], col)
    ma.crear("PISTA_Y_RODAJE_MARCAS_AMARILLAS", M["senal_amarilla"], col)
    manga_viento(col, M)


def manga_viento(col, M):
    """Manga de viento entre la plataforma y la pista: mástil de 6 m y cono de 3,6 m en cinco franjas naranja y blancas,
    inflado por un viento suave del noreste (apunta al azimut 240°) y algo caído."""
    xm, ym = MANGA_VIENTO
    z0 = -BORDILLO_DESNIVEL - 0.08
    ms, mn, mbl = Malla(), Malla(), Malla()
    ms.caja(xm - 0.4, xm + 0.4, ym - 0.4, ym + 0.4, z0 - 0.1, z0 + 0.15)
    ms.cilindro_z(xm, ym, z0 + 0.15, 6.25, 0.055, seg=12)
    phi = math.radians(NORTE_LOCAL_DEG - 240.0)
    d = Vector((math.cos(phi), math.sin(phi), -math.tan(math.radians(12.0)))).normalized()
    p = d.orthogonal().normalized()
    q = d.cross(p)
    o = Vector((xm, ym, 6.0)) + d * 0.08
    ms.loft([[tuple(o + d * s_ + 0.465 * (math.cos(2 * math.pi * j / 16) * p + math.sin(2 * math.pi * j / 16) * q))
              for j in range(16)] for s_ in (-0.03, 0.03)], tapas=(False, False))   # aro de la boca
    for k in range(5):
        anillos = [[tuple(o + d * s_ + r * (math.cos(2 * math.pi * j / 16) * p + math.sin(2 * math.pi * j / 16) * q))
                    for j in range(16)] for s_, r in ((3.6 * k / 5, 0.45 - 0.22 * k / 5), (3.6 * (k + 1) / 5, 0.45 - 0.22 * (k + 1) / 5))]
        (mn if k % 2 == 0 else mbl).loft(anillos, tapas=(False, False))
    ms.crear("MANGA_VIENTO_MASTIL", M["galvanizado"], col)
    mn.crear("MANGA_VIENTO_FRANJAS_NARANJA", M["manga_viento"], col, suave=True)
    mbl.crear("MANGA_VIENTO_FRANJAS_BLANCAS", M["senal"], col, suave=True)


def altura_terreno(r, phi):
    """(z, salar) del terreno a r metros del centro de TERRENO, en el ángulo local phi (rad): plano del aeropuerto,
    curvatura de la Tierra desde r_plano, cordones de CERROS y lomas bajas desde 5 km; plano en el Salar."""
    T = TERRENO
    az = (NORTE_LOCAL_DEG - math.degrees(phi)) % 360
    a = math.radians(az)
    s0, s1 = SALAR["azimut"]
    hacia_salar = min(suave(s0 - 6.0, s0 + 2.0, az), 1.0 - suave(s1 - 2.0, s1 + 6.0, az))
    salar = suave(SALAR["desde"] - 1500.0, SALAR["desde"] + 500.0, r) * hacia_salar
    h = 0.0
    for azc, semi, dk, hm in CERROS:
        da = (az - azc + 180.0) % 360.0 - 180.0
        fa = math.exp(-(da / semi) ** 2)
        if fa < 1e-3:
            continue
        d = dk * 1000.0
        rug = (1.0 + 0.32 * math.sin(5 * a + r / 2300.0) + 0.20 * math.sin(13 * a - r / 1300.0 + 1.7)
               + 0.10 * math.sin(31 * a + r / 700.0))
        h += hm * fa * math.exp(-((r - d) / (0.3 * d)) ** 2) * rug
    lomas = 30.0 * (0.5 + 0.5 * math.sin(7 * a + r / 1700.0)) * (0.5 + 0.5 * math.sin(11 * a - r / 900.0 + 1.1))
    h = h * suave(4000.0, 7000.0, r) * (1.0 - salar) + lomas * suave(5000.0, 9000.0, r) * (1.0 - hacia_salar)
    caida = max(r - T["r_plano"], 0.0) ** 2 / (2 * T["r_tierra"])
    return -BORDILLO_DESNIVEL - 0.08 - caida + h, salar


def terreno(C, M):
    """Suelo del altiplano: malla polar de 45 km de radio centrada en el edificio, con el atributo "salar" que lee el
    material (reemplaza al plano de 4 x 4 km). Plana hasta 3,5 km, donde están el edificio, las calles y la pista."""
    T = TERRENO
    cx, cy = T["centro"]
    radios = [150.0, 300.0, 500.0, 800.0, 1200.0, 1700.0, 2300.0, 3000.0, 3500.0, 4200.0, 5000.0, 6000.0]
    radios += [float(r) for r in range(7000, int(T["radio"]) + 1, 1000)]
    n = T["azimutes"]
    m = Malla()
    m.v.append((cx, cy, -BORDILLO_DESNIVEL - 0.08))
    sal = [0.0]
    for r in radios:
        for k in range(n):
            phi = 2 * math.pi * k / n
            z, s = altura_terreno(r, phi)
            m.v.append((cx + r * math.cos(phi), cy + r * math.sin(phi), z))
            sal.append(s)
    m.f += [(0, 1 + k, 1 + (k + 1) % n) for k in range(n)]
    for i in range(len(radios) - 1):
        a0, b0 = 1 + i * n, 1 + (i + 1) * n
        m.f += [(a0 + k, b0 + k, b0 + (k + 1) % n, a0 + (k + 1) % n) for k in range(n)]
    ob = m.crear("SUELO_ALTIPLANO", M["suelo"], C["06_ENTORNO_SITE"])
    if ob.data.polygons[0].normal.z < 0:
        ob.data.flip_normals()
    ob.data.attributes.new("salar", "FLOAT", "POINT").data.foreach_set("value", sal)
    return ob


_PAVIMENTOS = {}


def pavimentos(m):
    """Contornos del asfalto del frente y de la plaza, ensanchados m (se calculan una vez por margen)."""
    if m not in _PAVIMENTOS:
        _PAVIMENTOS[m] = [contraer(calzada_frente(cordon_tierra()), -m), contraer(FRENTE["plaza"], -m)]
    return _PAVIMENTOS[m]


def suelo_libre(x, y, m):
    """True si (x, y) es suelo natural: fuera del edificio y sus veredas, de la calzada del frente (con el acceso y la
    calle del eje 20), de la plaza, de la plataforma, del rodaje y de la franja nivelada de la pista, con un margen m."""
    xo, xe = X_CORDON_LATERAL
    (px0, px1), (py0, py1) = PLATAFORMA_AIRE["x"], PLATAFORMA_AIRE["y"]
    return not ((xo - m < x < xe + m and Y_CORDON_TIERRA - m < y < 51.0 + m)
                or any(dentro_poligono(x, y, p) for p in pavimentos(m))
                or (px0 - m < x < px1 + m and py0 - m < y < py1 + m)
                or (abs(x - RODAJE["x"]) < RODAJE["ancho"] / 2 + 20.0 + m and py1 - m < y < PISTA["y"])
                or abs(y - PISTA["y"]) < 75.0
                or math.hypot(x - MANGA_VIENTO[0], y - MANGA_VIENTO[1]) < 4.0)


def mata_paja_brava():
    """Malla de una mata de paja brava de unos 0,55 m: 90 hojas finas que nacen del centro y se abren y caen."""
    rnd = random.Random(PAJA_BRAVA["semilla"])
    m = Malla()
    for _ in range(90):
        th = rnd.uniform(0.0, 2 * math.pi)
        inc = math.radians(rnd.uniform(6.0, 58.0))
        largo = rnd.uniform(0.32, 0.68)
        r0 = rnd.uniform(0.0, 0.07)
        ux, uy = math.cos(th), math.sin(th)
        px, py = -uy, ux
        i0 = len(m.v)
        ts = (0.0, 0.3, 0.6, 0.85, 1.0)
        for t in ts:
            h = largo * t
            rad = r0 + h * math.sin(inc) + 0.12 * largo * t * t
            z = h * math.cos(inc) - 0.20 * largo * t * t * math.sin(inc)
            w = 0.007 * (1.0 - t) + 0.0008
            cxp, cyp = rad * ux, rad * uy
            m.v += [(cxp - px * w, cyp - py * w, z), (cxp + px * w, cyp + py * w, z)]
        for j in range(len(ts) - 1):
            a = i0 + 2 * j
            m.f.append((a, a + 1, a + 3, a + 2))
    return m


def gn_dispersion(nombre, proto, escala=(0.6, 1.4)):
    """Geometry Nodes: una instancia de proto en cada vértice, con giro y escala al azar (sin realizar: memoria baja)."""
    ng = bpy.data.node_groups.new(PREFIJO + nombre, "GeometryNodeTree")
    ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes, ng.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    oi = N.new("GeometryNodeObjectInfo")
    oi.inputs["Object"].default_value = proto
    io = N.new("GeometryNodeInstanceOnPoints")
    giro = N.new("FunctionNodeRandomValue")
    giro.data_type = "FLOAT_VECTOR"
    giro.inputs["Min"].default_value = (-0.10, -0.10, 0.0)
    giro.inputs["Max"].default_value = (0.10, 0.10, 2 * math.pi)
    esc = N.new("FunctionNodeRandomValue")
    esc.data_type = "FLOAT"
    esc.inputs["Min"].default_value, esc.inputs["Max"].default_value = escala
    esc.inputs["Seed"].default_value = 3
    L.new(gi.outputs[0], io.inputs["Points"])
    L.new(oi.outputs["Geometry"], io.inputs["Instance"])
    L.new(giro.outputs["Value"], io.inputs["Rotation"])
    L.new(esc.outputs["Value"], io.inputs["Scale"])
    L.new(io.outputs["Instances"], go.inputs[0])
    return ng


def paja_brava(C, M):
    """Matas de paja brava dispersas en manchas en el suelo libre hasta 650 m del edificio (suelo_libre). Las jardineras
    del frente quedan en tierra, como en el modelo del cliente. Un objeto de puntos con Geometry Nodes instancia la mata
    (oculta en el render, bajo el suelo); los puntos quedan en el objeto PAJA_BRAVA_DISPERSION."""
    col = C["11_CONTEXTO_AEROPUERTO"]
    P = PAJA_BRAVA
    proto = mata_paja_brava().crear("PAJA_BRAVA_MATA", M["paja"], col)
    proto.location = (0.0, 0.0, -5.0)
    proto.hide_render = True
    rnd = random.Random(P["semilla"] + 1)
    cx, cy = TERRENO["centro"]
    R, zs = P["radio"], -BORDILLO_DESNIVEL - 0.08
    pts = []
    for _ in range(int(math.pi * R * R * P["densidad"])):
        r, a = R * math.sqrt(rnd.random()), rnd.uniform(0.0, 2 * math.pi)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        mancha = ((0.5 + 0.5 * math.sin(x / 23.0 + 1.3 * math.sin(y / 31.0)))
                  * (0.5 + 0.5 * math.sin(y / 17.0 - 0.7 * math.sin(x / 29.0))))
        if rnd.random() < 0.25 + 0.75 * mancha and suelo_libre(x, y, P["margen"]):
            pts.append((x, y, zs))
    me = bpy.data.meshes.new(PREFIJO + "PAJA_BRAVA_DISPERSION")
    me.from_pydata(pts, [], [])
    ob = bpy.data.objects.new(PREFIJO + "PAJA_BRAVA_DISPERSION", me)
    ob["puntos_dispersion"] = 1                                      # exportar_geometria.py guarda sus puntos
    col.objects.link(ob)
    ob.modifiers.new("DISPERSION_PAJA_BRAVA", "NODES").node_group = gn_dispersion("GN_PAJA_BRAVA", proto)
    return ob


def puestos_aviones():
    """Nariz (X, Y) y rumbo (rad) de cada 737: la puerta L1 queda en PUERTA_DESDE_ROTONDA respecto de su rotonda."""
    ang = math.radians(AVION_RUMBO)
    h, nl = (math.cos(ang), math.sin(ang)), (-math.sin(ang), math.cos(ang))
    xp, zp = AVION_PUERTA_L1
    a = semiancho_fuselaje(xp)
    out = []
    for g in MANGAS:
        dx, dy = g["x"] + PUERTA_DESDE_ROTONDA[0], MANGA["y_rotonda"] + PUERTA_DESDE_ROTONDA[1]
        out.append((dx - (xp * h[0] + a * nl[0]), dy - (xp * h[1] + a * nl[1]), ang))
    return out


# --- Boeing 737-800 genérico (medidas reales: 39,5 m de largo, 35,8 m de envergadura con winglets, 12,5 m de alto).
# Ejes locales: x hacia adelante (nariz en x = 0), y hacia la izquierda, z hacia arriba desde el piso.
AV = dict(r=1.88, b=2.005, zc=3.155, nariz=6.5, cono=(28.0, 38.0),
          deriva=((4.4, -29.6, 8.2, 0.11), (5.3, -30.9, 7.0, 0.11), (12.55, -36.75, 2.7, 0.09)))   # (z, x b. ataque, cuerda, t)


def semiancho_fuselaje(x):
    """Semiancho del fuselaje en x (negativo, detrás de la nariz)."""
    t = -x
    if t < AV["nariz"]:
        return AV["r"] * (1 - (1 - t / AV["nariz"]) ** 2.5) ** 0.5
    if t > AV["cono"][0]:
        u = min((t - AV["cono"][0]) / (AV["cono"][1] - AV["cono"][0]), 1.0)
        return AV["r"] - 1.60 * u ** 1.2
    return AV["r"]


def seccion_fuselaje(t):
    """(semiancho, semialto, z del centro) a t metros detrás de la nariz."""
    if t < AV["nariz"]:
        f = (1 - (1 - t / AV["nariz"]) ** 2.5) ** 0.5
        return AV["r"] * f, AV["b"] * f, AV["zc"] - 0.75 * (1 - t / AV["nariz"]) ** 2
    if t > AV["cono"][0]:
        u = min((t - AV["cono"][0]) / (AV["cono"][1] - AV["cono"][0]), 1.0)
        return AV["r"] - 1.60 * u ** 1.2, AV["b"] - 1.65 * u ** 1.1, AV["zc"] + 1.15 * u ** 1.3
    return AV["r"], AV["b"], AV["zc"]


def naca_yt(x, t):
    """Semiespesor del perfil NACA simétrico de espesor relativo t en la fracción de cuerda x."""
    return 5 * t * (0.2969 * math.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1036 * x ** 4)


def fracciones_perfil(n=10):
    return [0.5 * (1 - math.cos(math.pi * k / (n - 1))) for k in range(n)]


def perfil_ala(c, t, n=10):
    """Perfil NACA simétrico de espesor relativo t y cuerda c: [(distancia al borde de ataque, espesor), ...] del
    borde de fuga al de ataque por arriba y de vuelta por abajo (anillo cerrado)."""
    xs = fracciones_perfil(n)
    return [(x * c, naca_yt(x, t) * c) for x in reversed(xs)] + [(x * c, -naca_yt(x, t) * c) for x in xs[1:-1]]


def estaciones_deriva(paso=0.6):
    """Estaciones de AV["deriva"] con intermedias cada ~0,6 m de altura (interpoladas linealmente): las caras del loft
    quedan chicas y casi planas, así la librea pegada a 6 mm queda siempre por fuera de la piel."""
    est = AV["deriva"]
    out = []
    for a, b in zip(est, est[1:]):
        n = max(2, round((b[0] - a[0]) / paso))
        out += [tuple(a[i] + (b[i] - a[i]) * k / n for i in range(4)) for k in range(n)]
    return out + [est[-1]]


def piel_deriva(u, z, lado, sep=0.006):
    """Punto (x, y, z) sobre la deriva a la fracción de cuerda u y la altura z, en la cara izquierda (lado 1) o derecha
    (-1) y 'sep' por fuera de ella. Interpola como el loft de la deriva (mismas estaciones y fracciones de perfil_ala)."""
    est = estaciones_deriva()
    i = max([k for k in range(len(est) - 1) if est[k][0] <= z] or [0])
    (z0, xl0, c0, t0), (z1, xl1, c1, t1) = est[i], est[i + 1]
    w = (z - z0) / (z1 - z0)
    xs = fracciones_perfil()
    j = max(k for k in range(len(xs) - 1) if xs[k] <= u)
    q = (u - xs[j]) / (xs[j + 1] - xs[j])
    d0, d1 = (c * (naca_yt(xs[j], t) * (1 - q) + naca_yt(xs[j + 1], t) * q) for c, t in ((c0, t0), (c1, t1)))
    return ((xl0 - u * c0) * (1 - w) + (xl1 - u * c1) * w, lado * (d0 * (1 - w) + d1 * w + sep), z)


def franjas_deriva():
    """Librea BoA: tres franjas de 0,40 m de alto (rojo, amarillo y verde, de arriba abajo, como la bandera) que cruzan
    las dos caras de la deriva en diagonal, desde abajo y adelante hacia arriba y atrás, curvándose como una cola de
    ave en vuelo. [(clave del material, Malla)]."""
    est = estaciones_deriva()
    def borde(z):                                                    # (x del borde de ataque, cuerda) a la altura z
        i = max([k for k in range(len(est) - 1) if est[k][0] <= z] or [0])
        (z0, xl0, c0, _), (z1, xl1, c1, _) = est[i], est[i + 1]
        w = (z - z0) / (z1 - z0)
        return xl0 + (xl1 - xl0) * w, c0 + (c1 - c0) * w
    out = []
    for k, clave in enumerate(("boa_rojo", "boa_amarillo", "boa_verde")):
        m = Malla()
        dz = 0.50 * (1 - k)
        for lado in (1, -1):
            i0, ns = len(m.v), 30
            for i in range(ns + 1):
                s = i / ns
                x, zc = -32.5 - 6.1 * s, 5.7 + 6.1 * s ** 1.25 + dz
                for zz in (zc - 0.20, zc + 0.20):
                    zz = min(max(zz, 4.75), 12.45)
                    xle, c = borde(zz)
                    m.v.append(piel_deriva(min(max((xle - x) / c, 0.02), 0.98), zz, lado))
            m.f += [(i0 + 2 * i, i0 + 2 * i + 2, i0 + 2 * i + 3, i0 + 2 * i + 1) for i in range(ns)]
        out.append((clave, m))
    return out


def texto_fuselaje(texto, x_ini, z_base, alto, sep=0.006):
    """Texto de la librea (fuente de Blender engrosada) proyectado sobre las dos caras del fuselaje, legible desde cada
    lado: empieza en x_ini hacia la cola, con la base en z_base y 'alto' de alto. Se corta en franjas de 6 cm para que
    siga la curvatura de la sección."""
    cu = bpy.data.curves.new(PREFIJO + "TEXTO_TMP", "FONT")
    cu.body, cu.size, cu.offset = texto, 1.0, 0.012
    ob = bpy.data.objects.new(PREFIJO + "TEXTO_TMP", cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.curves.remove(cu)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    xs, ys = [v.co.x for v in bm.verts], [v.co.y for v in bm.verts]
    k = alto / (max(ys) - min(ys))
    for v in bm.verts:
        v.co = ((v.co.x - min(xs)) * k, (v.co.y - min(ys)) * k, 0.0)
    largo = (max(xs) - min(xs)) * k
    w = 0.06
    while w < alto:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0.0, w, 0.0),
                               plane_no=(0.0, 1.0, 0.0))
        w += 0.06
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.verts.index_update()
    planos = [(v.co.x, v.co.y) for v in bm.verts]
    caras = [tuple(v.index for v in f.verts) for f in bm.faces]
    bm.free()
    m = Malla()
    for lado in (1, -1):
        i0 = len(m.v)
        for u, w in planos:
            x, z = (x_ini - u if lado == 1 else x_ini - largo + u), z_base + w
            a, b, zc = seccion_fuselaje(-x)
            m.v.append((x, lado * (a * math.sqrt(max(0.0, 1 - ((z - zc) / b) ** 2)) + sep), z))
        m.f += [tuple(i0 + i for i in c) for c in caras]
    return m


def avion_737_partes():
    """Mallas del 737-800 en ejes locales: [(nombre, Malla, material, suave)]."""
    partes = []
    # fuselaje: nariz, tramo constante y cono de cola que sube
    fu = Malla()
    ts = [0.004, 0.04, 0.12, 0.3, 0.6, 1.0, 1.6, 2.4, 3.4, 4.6, 5.6, 6.5, 12.0, 20.0, 28.0, 30.0, 32.0, 34.0, 36.0, 37.4, 38.0]
    n = 28
    anillos = []
    for t in ts:
        a, b, zc = seccion_fuselaje(t)
        anillos.append([(-t, a * math.cos(2 * math.pi * k / n), zc + b * math.sin(2 * math.pi * k / n)) for k in range(n)])
    fu.loft(anillos)
    partes.append(("FUSELAJE", fu, "avion", True))
    # alas (izquierda y derecha), con diedro de 6° y flecha de 25°; winglets
    al = Malla()
    tan_f, tan_d = math.tan(math.radians(27.0)), math.tan(math.radians(6.0))
    estaciones = [(0.9, -12.0, 8.6, 1.75, 0.14), (1.88, -12.6, 7.8, 1.82, 0.13)]
    for y, cuerda, esp in ((6.0, 4.95, 0.115), (17.16, 1.25, 0.10)):
        estaciones.append((y, -12.6 - (y - 1.88) * tan_f, cuerda, 1.82 + (y - 1.88) * tan_d, esp))
    for lado in (1, -1):
        al.loft([[(xle - s, lado * y, z + d) for s, d in perfil_ala(c, t)] for y, xle, c, z, t in estaciones])
    partes.append(("ALAS", al, "avion_ala", True))
    wl = Malla()
    yt_, xt_, zt_ = 17.16, -12.6 - 15.28 * tan_f, 1.82 + 15.28 * tan_d
    for lado in (1, -1):
        wl.loft([[(xle - s, lado * (yy + d), z) for s, d in perfil_ala(c, 0.09)]
                 for yy, xle, c, z in ((yt_ - 0.25, xt_ - 0.05, 1.20, zt_), (yt_ + 0.15, xt_ - 0.45, 1.05, zt_ + 0.45),
                                       (yt_ + 0.65, xt_ - 1.55, 0.55, zt_ + 2.45))])
    partes.append(("WINGLETS", wl, "boa_azul", True))                 # librea BoA: winglets y deriva en azul
    # estabilizador horizontal (diedro 7°) y deriva
    eh = Malla()
    for lado in (1, -1):
        eh.loft([[(xle - s, lado * y, z + d) for s, d in perfil_ala(c, t)]
                 for y, xle, c, z, t in ((0.3, -32.4, 4.2, 4.25, 0.10), (7.17, -36.8, 1.3, 5.07, 0.08))])
    partes.append(("ESTABILIZADOR", eh, "avion_ala", True))
    de = Malla()
    de.loft([[(xle - s, d, z) for s, d in perfil_ala(c, t)] for z, xle, c, t in estaciones_deriva()])
    partes.append(("DERIVA", de, "boa_azul", True))
    # librea BoA: franjas de la bandera en la deriva y el nombre en las dos caras del fuselaje
    for clave, m in franjas_deriva():
        partes.append((f"LIBREA_DERIVA_{clave[4:].upper()}", m, clave, True))
    for nombre, (texto, x0, dz, alto) in (("TITULO", LIBREA_BOA["titulo"]), ("SUBTITULO", LIBREA_BOA["subtitulo"])):
        partes.append((f"LIBREA_{nombre}", texto_fuselaje(texto, x0, AV["zc"] + dz, alto), "boa_azul", True))
    # motores CFM56-7B bajo el ala (y = ±4,83), con pilón, ventilador oscuro y tobera
    mo, fn, py_ = Malla(), Malla(), Malla()
    st = [(-11.0, 0.74), (-10.62, 0.79), (-10.75, 0.90), (-11.4, 0.99), (-12.6, 0.98), (-13.9, 0.86), (-14.0, 0.56),
          (-14.8, 0.45), (-15.5, 0.10)]
    for lado in (1, -1):
        yc, zc = lado * 4.83, 1.32
        mo.loft([[(x, yc + r * math.cos(2 * math.pi * k / 24), zc + 0.94 * r * math.sin(2 * math.pi * k / 24))
                  for k in range(24)] for x, r in st])
        fn.cilindro_x(-11.0, -10.98, yc, zc, 0.74, seg=24)
        py_.caja(-14.6, -11.5, yc - 0.15, yc + 0.15, zc + 0.70, zc + 1.15)   # sobre la góndola, hasta el ala
    partes.append(("MOTORES", mo, "avion_motor", True))
    partes.append(("MOTORES_VENTILADOR", fn, "avion_oscuro", False))
    partes.append(("PILONES", py_, "avion_ala", False))
    # tren de aterrizaje: nariz a 4,8 m y principal a 20,4 m de la nariz (trocha de 5,72 m)
    tr, ru = Malla(), Malla()
    tr.cilindro_z(-4.8, 0.0, 0.35, 1.45, 0.09)
    for yy in (-0.2, 0.2):
        ru.cilindro_y(-4.8, yy - 0.11, yy + 0.11, 0.345, 0.345, seg=18)
    for lado in (1, -1):
        tr.cilindro_z(-20.4, lado * 2.86, 0.57, 1.95, 0.13)
        for dy in (-0.45, 0.45):
            yy = lado * 2.86 + dy
            ru.cilindro_y(-20.4, yy - 0.18, yy + 0.18, 0.57, 0.57, seg=22)
    partes.append(("TREN", tr, "avion_oscuro", False))
    partes.append(("RUEDAS", ru, "neumatico", True))
    # ventanillas de la cabina de pasajeros y del puesto de pilotaje
    vn = Malla()
    x = -8.2
    while x > -31.0:
        if not -17.9 < x < -15.6:                                  # salidas sobre el ala
            for lado in (1, -1):
                y = lado * (semiancho_fuselaje(x) * math.cos(math.asin(0.40 / AV["b"])) + 0.004)
                vn.caja(x - 0.11, x + 0.11, y - 0.012, y + 0.012, AV["zc"] + 0.24, AV["zc"] + 0.56)
        x -= 0.508
    for x0, x1 in ((-2.05, -2.75), (-2.85, -3.55)):
        for lado in (1, -1):
            xm = (x0 + x1) / 2
            a, b, zc = seccion_fuselaje(-xm)
            y = lado * (a * 0.80 + 0.01)
            vn.caja(x1, x0, y - 0.015, y + 0.015, zc + 0.62 * b - 0.25, zc + 0.62 * b + 0.12)
    partes.append(("VENTANILLAS", vn, "avion_vidrio", False))
    return partes


def manga_embarque(m, mo, g, cabina_c, z_cabina, rumbo_cabina):
    """Manga (puente de embarque) de la puerta g: pasarela fija desde la fachada, rotonda sobre columna, túnel
    telescópico de dos tramos en pendiente, columna con tren de ruedas y cabina con fuelle girada hacia el avión."""
    G = MANGA
    xg, yf = g["x"], g["y_frente"]
    yr, rr, zp = G["y_rotonda"], G["r_rotonda"], G["z_piso"]
    # pasarela fija y rotonda
    m.caja(xg - 1.3, xg + 1.3, yf, yr - rr + 0.2, zp - 0.35, zp + 2.6)
    m.cilindro_z(xg, yr, zp - 0.40, zp + 2.70, rr, seg=32)
    m.cilindro_z(xg, yr, zp + 2.70, zp + 2.82, rr + 0.12, seg=32)
    m.cilindro_z(xg, yr, -BORDILLO_DESNIVEL, zp - 0.40, 0.32, seg=20)
    m.caja(xg - 0.6, xg + 0.6, yr - 0.6, yr + 0.6, -BORDILLO_DESNIVEL, -BORDILLO_DESNIVEL + 0.12)
    # túnel: del centro de la rotonda al centro de la cabina, el piso baja de zp a z_cabina
    cx, cy = cabina_c
    dx, dy = cx - xg, cy - yr
    l = math.hypot(dx, dy)
    ux, uy = dx / l, dy / l
    def pt(s):
        return (xg + ux * s, yr + uy * s, zp + (z_cabina - zp) * s / l)
    (wa, ha), (wb, hb) = G["tunel_a"], G["tunel_b"]
    m.caja_eje(pt(rr - 0.3), pt(0.56 * l), wa, ha, z_abajo=0.30)
    m.caja_eje(pt(0.50 * l), pt(l), wb, hb, z_abajo=0.40)
    # columna de traslación con tren de ruedas, a 3/4 del túnel
    sx, sy, sz = pt(0.75 * l)
    nx, ny = -uy, ux
    for k in (-0.8, 0.8):
        m.caja(sx + nx * k - 0.15, sx + nx * k + 0.15, sy + ny * k - 0.15, sy + ny * k + 0.15, 0.75, sz - 0.40)
    m.caja_eje((sx - nx * 1.25, sy - ny * 1.25, 0.55), (sx + nx * 1.25, sy + ny * 1.25, 0.55), 0.35, 0.35)
    for k in (-1.05, 1.05):
        mo.cilindro_eje((sx + nx * k, sy + ny * k, 0.45 - BORDILLO_DESNIVEL), (nx, ny, 0.0), 0.45, 0.35, seg=18)
    # cabina girada hacia el avión y fuelle contra el fuselaje
    lc, ac, hc = G["cabina"]
    m.caja_rotada(cx, cy, lc, ac, z_cabina - 0.30, z_cabina - 0.30 + hc, rumbo_cabina)
    fx, fy = math.cos(rumbo_cabina), math.sin(rumbo_cabina)
    mo.caja_rotada(cx + fx * (lc / 2 + 0.25), cy + fy * (lc / 2 + 0.25), 0.5, ac - 0.4, z_cabina - 0.15,
                   z_cabina + 2.55, rumbo_cabina)


def mangas_y_aviones(C, M):
    """Dos mangas en las puertas de embarque del nivel 1P (caja del bloque del eje R y vestíbulo de los ejes 10-11) y
    dos Boeing 737-800 con la librea de BoA, con la puerta L1 en la cabina de cada manga. Los dos aviones comparten
    mallas."""
    col = C["10_MANGAS_AERONAVES"]
    partes = avion_737_partes()
    zp = -BORDILLO_DESNIVEL                                        # la plataforma
    m, mo = Malla(), Malla()
    for i, (g, (nx, ny, ang)) in enumerate(zip(MANGAS, puestos_aviones())):
        h, nl = (math.cos(ang), math.sin(ang)), (-math.sin(ang), math.cos(ang))
        xp, zpu = AVION_PUERTA_L1
        a = semiancho_fuselaje(xp)
        dx_, dy_ = nx + xp * h[0] + a * nl[0], ny + xp * h[1] + a * nl[1]          # puerta L1 en planta
        cab = (dx_ + nl[0] * (MANGA["cabina"][0] / 2 + 0.55), dy_ + nl[1] * (MANGA["cabina"][0] / 2 + 0.55))
        manga_embarque(m, mo, g, cab, zp + zpu, ang - math.pi / 2)
        matriz = Matrix.Translation((nx, ny, zp)) @ Matrix.Rotation(ang, 4, "Z")
        for nombre, malla, mat, suave in partes:
            if i == 0:
                ob = malla.crear(f"AVION_737_{nombre}_1", M[mat], col, suave=suave)
                malla.objeto = ob
            else:
                ob = bpy.data.objects.new(f"{PREFIJO}AVION_737_{nombre}_{i + 1}", malla.objeto.data)
                col.objects.link(ob)
            ob.matrix_world = matriz
    m.crear("MANGAS_EMBARQUE", M["manga"], col)
    mo.crear("MANGAS_FUELLES_Y_RUEDAS", M["manga_oscuro"], col)


def assets(C, M):
    """Placeholders a escala: vagonetas 4x4 tipo Land Cruiser, minibús de transfer y turistas.

    Van en 07_ASSETS/PROXIES_COLOCACION: se ven en el visor como guía de ubicación y escala, pero no salen en
    el render. Reemplazarlos por modelos reales (Sketchfab, BlenderKit) en 07_ASSETS.
    """
    col = coleccion("PROXIES_COLOCACION", C["07_ASSETS"])
    col.hide_render = True
    zc = -BORDILLO_DESNIVEL
    def vagoneta(nombre, x, y, rot, largo=4.90, ancho=1.94, alto=2.05, parrilla=True):
        cu, vi, ne = Malla(), Malla(), Malla()
        cu.caja(-largo / 2, largo / 2, -ancho / 2, ancho / 2, 0.45, 1.25)
        vi.caja(-largo / 2 + 0.95, largo / 2 - 0.15, -ancho / 2 + 0.05, ancho / 2 - 0.05, 1.25, alto - 0.06)
        cu.caja(-largo / 2 + 0.90, largo / 2 - 0.10, -ancho / 2 + 0.04, ancho / 2 - 0.04, alto - 0.07, alto)
        if parrilla:
            cu.caja(-largo / 2 + 1.1, largo / 2 - 0.4, -ancho / 2 + 0.15, ancho / 2 - 0.15, alto + 0.05, alto + 0.09)
            cu.caja(-largo / 2 + 1.4, -largo / 2 + 2.4, -0.6, 0.5, alto + 0.09, alto + 0.45)
        for sx in (-1, 1):
            for sy in (-1, 1):
                ne.cilindro_y(sx * (largo / 2 - 0.85), sy * ancho / 2 - 0.15 * sy - 0.14, sy * ancho / 2 - 0.15 * sy + 0.14, 0.40, 0.40)
        partes = [cu.crear(nombre + "_CARROCERIA", M["pintura_blanca"], col),
                  vi.crear(nombre + "_VIDRIOS", M["vidrio_auto"], col),
                  ne.crear(nombre + "_RUEDAS", M["neumatico"], col, suave=True)]
        for p in partes:
            p.matrix_world = Matrix.Translation((x, y, zc)) @ Matrix.Rotation(math.radians(rot), 4, "Z")
    # calzada frontal con sentido hacia el eje 1 (rot 180): dos carriles y las dos dársenas de la A111
    yd = Y_CORDON_TIERRA + DARSENA["fondo"]                         # fondo de las dársenas (-6,313)
    xd1, xd2 = (x + DARSENA["fondo"] + 2 * DARSENA["r"] * (math.sqrt(2) - 1) + DARSENA["recto"] / 2
                for x in DARSENAS_TIERRA)                           # centro del tramo recto de cada dársena
    vagoneta("4x4_01", 8.0, Y_CORDON_TIERRA - 1.75, 180)
    vagoneta("4x4_02", xd1, yd - 1.05, 180)
    vagoneta("4x4_03", 47.0, FRENTE["carril"]["y"] - 1.75, 180)    # segundo carril de llegada
    xv, yp = ESPIGA["sup"][2], ESPIGA["sup"][3] + ESPIGA["amplitud"]  # plaza: de punta en los dientes de la espiga
    vagoneta("4x4_04_ESTAC", xv + ESPIGA["paso"], yp + 1.6, 270)
    vagoneta("4x4_05_ESTAC", xv + 2 * ESPIGA["paso"], yp + 1.6, 270)
    vagoneta("MINIBUS_TRANSFER", xd2, yd - 1.09, 180, largo=6.4, ancho=2.05, alto=2.55, parrilla=False)
    personas = [(16.0, -2.0, 0), (17.6, -2.6, 1), (18.2, -1.4, 2), (54.8, -2.2, 3), (56.4, -3.1, 4), (57.1, -1.8, 0),
                (36.0, -3.3, 1), (9.5, -6.5, 2), (25.4, -5.7, 3)]
    vereda = cordon_tierra()
    for i, (x, y, c) in enumerate(personas):
        h = 1.62 + 0.12 * ((i * 7) % 5) / 4
        p = Malla()
        p.caja(-0.20, 0.20, -0.12, 0.12, 0.0, h * 0.53)      # piernas
        p.caja(-0.24, 0.24, -0.15, 0.15, h * 0.53, h * 0.86)  # torso con parka
        p.caja(-0.10, 0.10, -0.11, 0.11, h * 0.86, h)          # cabeza
        p.caja(-0.18, 0.18, 0.15, 0.36, h * 0.55, h * 0.84)   # mochila de trekking
        if i % 3 == 0:
            p.caja(0.30, 0.68, -0.12, 0.12, 0.05, 0.72)       # maleta
        ob = p.crear(f"TURISTA_{i:02d}", M["ropa"][c], col)
        ob.location = (x, y, 0.0 if dentro_poligono(x, y, vereda) else -BORDILLO_DESNIVEL)


def referencias_cad(C):
    """Planos de referencia (PNG de las vistas aisladas), ocultos en el render. Opcional."""
    try:
        base = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        base = os.path.join(globals().get("RUTA_REPO", ""), "aeropuerto_uyuni", "01_blender")
    ruta = os.path.join(base, "..", "00_auditoria", "vistas")
    idx = os.path.join(ruta, "vistas_index.json")
    if not os.path.exists(idx):
        return
    vistas = json.load(open(idx, encoding="utf-8"))
    col = C["_REF_CAD"]
    sub = {}
    def plano(nombre, png, ancho, alto, matriz, colname):
        img = bpy.data.images.load(os.path.join(ruta, png), check_existing=True)
        img.pack()
        mat = bpy.data.materials.new(PREFIJO + "REF_" + nombre)
        nb = Nodos(mat)
        tx = nb.n("ShaderNodeTexImage")
        tx.image = img
        nb.ent("Base Color", tx.outputs["Color"])
        nb.ent("Emission Color", tx.outputs["Color"])
        nb.ent("Emission Strength", 1.0)
        me = bpy.data.meshes.new(PREFIJO + "REF_" + nombre)
        me.from_pydata([(0, 0, 0), (ancho, 0, 0), (ancho, alto, 0), (0, alto, 0)], [], [(0, 1, 2, 3)])
        uv = me.uv_layers.new()
        for li, co in zip(range(4), ((0, 0), (1, 0), (1, 1), (0, 1))):
            uv.data[li].uv = co
        me.materials.append(mat)
        ob = bpy.data.objects.new(PREFIJO + "REF_" + nombre, me)
        ob.matrix_world = matriz
        ob.hide_render = True
        ob.hide_select = True
        if colname not in sub:
            sub[colname] = coleccion(colname, col)
        sub[colname].objects.link(ob)
    rx = Matrix.Rotation(math.radians(90), 4, "X")
    for nombre, v in vistas.items():
        b = v["bbox_dxf"]
        w, h = b["xmax"] - b["xmin"], b["ymax"] - b["ymin"]
        npt = v.get("npt_y", 0.0) or 0.0
        if nombre == "FACHADA_NORESTE_ACTUAL":      # detrás del edificio, alineada en X y Z
            m = Matrix.Translation((b["xmin"], 60.0, b["ymin"] - npt)) @ rx
        elif nombre == "CORTE_ACTUAL_POR_M1":       # a la izquierda del edificio, alineada en Y y Z (Y = -41,147 - x)
            m = (Matrix.Translation((-30.0, -41.147 - b["xmin"], b["ymin"])) @ Matrix.Rotation(math.radians(-90), 4, "Z") @ rx)
        else:                                       # galería fuera del sitio
            k = list(vistas).index(nombre)
            m = Matrix.Translation((-260.0 + (k % 4) * 120.0, -160.0 - (k // 4) * 40.0, 0.0)) @ rx
        plano(nombre, v["png"], w, h, m, v.get("coleccion", "REF_CAD_OTROS"))
    col.hide_render = True


# =============================================================================
# 5. LUZ, CIELO Y CÁMARAS
# =============================================================================
def sol_posicion(anio, mes, dia, hora_local):
    """Azimut (grados, horario desde el norte verdadero) y elevación del sol en Uyuni (algoritmo NOAA)."""
    import datetime as dt
    n = dt.date(anio, mes, dia).timetuple().tm_yday
    h_utc = hora_local - UTC_OFFSET
    g = 2 * math.pi / 365 * (n - 1 + (h_utc - 12) / 24)
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g) - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    dec = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
           + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    tst = h_utc * 60 + eqt + 4 * LON
    ha = math.radians(tst / 4 - 180)
    lat = math.radians(LAT)
    cz = math.sin(lat) * math.sin(dec) + math.cos(lat) * math.cos(dec) * math.cos(ha)
    elev = 90 - math.degrees(math.acos(max(-1, min(1, cz))))
    az_s = math.atan2(math.sin(ha), math.cos(ha) * math.sin(lat) - math.tan(dec) * math.cos(lat))
    return (math.degrees(az_s) + 180) % 360, elev


def dir_local(azimut, elev):
    """Vector unitario hacia el sol en coordenadas locales del edificio."""
    phi = math.radians(NORTE_LOCAL_DEG - azimut)
    e = math.radians(elev)
    return Vector((math.cos(e) * math.cos(phi), math.cos(e) * math.sin(phi), math.sin(e)))


def mundo(nombre, azimut, elev, fuerza, disco=False):
    w = bpy.data.worlds.new(PREFIJO + nombre)
    if w.node_tree is None:
        w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    sky = nt.nodes.new("ShaderNodeTexSky")
    for t in ("MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "NISHITA", "HOSEK_WILKIE"):
        try:
            sky.sky_type = t
            break
        except TypeError:
            continue
    for k, v in dict(altitude=ALTITUD_MSNM, **CIELO_ATMOSFERA,
                     sun_disc=disco, sun_elevation=math.radians(elev),
                     sun_rotation=math.radians((90.0 - (NORTE_LOCAL_DEG - azimut)) % 360)).items():
        if hasattr(sky, k):
            try:
                setattr(sky, k, v)
            except Exception:
                pass
    bg.inputs["Strength"].default_value = fuerza
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    return w


def sol(nombre, azimut, elev, fuerza, col, temp=5800):
    ld = bpy.data.lights.new(PREFIJO + nombre, "SUN")
    ld.energy = fuerza
    ld.angle = math.radians(0.53)
    if hasattr(ld, "use_temperature"):
        ld.use_temperature = True
        ld.temperature = temp
    ob = bpy.data.objects.new(PREFIJO + nombre, ld)
    ob.rotation_euler = dir_local(azimut, elev).to_track_quat("Z", "Y").to_euler()
    col.objects.link(ob)
    return ob


def camara(nombre, pos, mira, focal, col, sensor=36.0, shift_y=0.0):
    cd = bpy.data.cameras.new(nombre)
    cd.lens = focal
    cd.sensor_width = sensor
    cd.shift_y = shift_y      # descentramiento: encuadra sin inclinar la cámara (verticales rectas)
    cd.clip_start, cd.clip_end = 0.1, 60000.0     # los cerros del horizonte llegan a 45 km
    ob = bpy.data.objects.new(nombre, cd)
    ob.location = pos
    apuntar(ob, mira)
    col.objects.link(ob)
    return ob


def camaras_y_dron(C, escena):
    col = C["08_CAMERAS_LIGHTS"]
    cams = {
        # Hero, Lado Tierra: perspectiva angular a nivel de ojo (1,65 m), 32 mm
        "CAM_01_HERO_LADO_TIERRA": camara("CAM_01_HERO_LADO_TIERRA", (91.0, -17.0, 1.65), (57.0, -0.5, 4.6), 32, col),
        # detalle constructivo: encuentro chapa / retenedor de nieve / antepecho (vista elevada)
        "CAM_02_DETALLE_ALERO": camara("CAM_02_DETALLE_ALERO", (-2.8, -5.6, 10.1), (5.0, -1.0, 8.6), 35, col),
        # detalle del cielo listonado, columnas y M1 desde la acera
        "CAM_02B_DETALLE_CIELO": camara("CAM_02B_DETALLE_CIELO", (11.0, -3.6, 1.62), (19.5, -0.4, 6.2), 22, col),
        # crepuscular / nocturna con nieve y piso mojado (escena UYUNI_CREPUSCULO)
        "CAM_03_CREPUSCULAR_NIEVE": camara("CAM_03_CREPUSCULAR_NIEVE", (50.5, -36.0, 1.7), (50.5, 0.0, 5.0), 24, col),
        # concepto del letrero: horizonte, montículos de sal y su reflejo
        "CAM_05_LETRERO_HORIZONTE": camara("CAM_05_LETRERO_HORIZONTE", (54.0, -19.0, 4.2), (54.0, -1.7, 7.7), 40, col),
        # detalle de las celosías corten: planchas de 1 x 2 m, calados y su sombra sobre columnas y muro
        "CAM_06_DETALLE_CELOSIA": camara("CAM_06_DETALLE_CELOSIA", (62.5, -9.5, 2.0), (71.5, -0.5, 3.2), 28, col),
        # aérea semicenital: Lado Tierra + Lado Aire, volumetría limpia
        "CAM_04_AEREA_GENERAL": camara("CAM_04_AEREA_GENERAL", (-22.0, -58.0, 48.0), (38.0, 8.0, 2.0), 35, col),
        # Lado Aire (4 de octubre): aérea desde la plataforma, como la vista del modelo del cliente, y la manga 1
        # con su 737 en primer plano y la fachada detrás
        "CAM_08_LADO_AIRE": camara("CAM_08_LADO_AIRE", (112.0, 150.0, 40.0), (32.0, 52.0, 4.0), 28, col),
        "CAM_09_MANGA_737": camara("CAM_09_MANGA_737", (10.0, 122.0, 30.0), (14.0, 56.0, 3.0), 30, col),
        # contexto (4 de octubre): aérea desde el oeste, a 90 m, sobre el borde de la pista: la pista 13/31 nace abajo
        # a la izquierda y llega al horizonte (cabecera 13), la calle de rodaje lleva a la plataforma, y los 737 y la
        # terminal quedan a la derecha; al fondo (mira al noroeste) el Salar como franja blanca
        "CAM_10_PISTA_HORIZONTE": camara("CAM_10_PISTA_HORIZONTE", (-350.0, 320.0, 90.0), (229.6, 164.6, 5.7), 30, col),
    }
    cams.update(camaras_propuestas(col))
    # recorrido de dron: 25 s a 24 fps (600 cuadros) - aproximación, descenso, paso rasante, elevación
    cam = camara("CAM_DRON", (-40.0, -120.0, 55.0), (36.0, 10.0, 5.0), 24, col)
    obj = bpy.data.objects.new("DRON_OBJETIVO", None)
    col.objects.link(obj)
    tr = cam.constraints.new("TRACK_TO")
    tr.target = obj
    tr.track_axis, tr.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    claves = [(1, (-40.0, -120.0, 55.0), (36.0, 10.0, 5.0)), (150, (-15.0, -45.0, 22.0), (30.0, 0.0, 6.0)),
              (300, (4.0, -14.0, 5.0), (30.0, 0.0, 5.0)), (450, (60.0, -12.0, 4.5), (72.0, 0.0, 5.0)),
              (600, (98.0, -26.0, 36.0), (40.0, 25.0, 8.0))]
    for f, p, t in claves:
        cam.location = p
        cam.keyframe_insert("location", frame=f)
        obj.location = t
        obj.keyframe_insert("location", frame=f)
    escena.frame_start, escena.frame_end = 1, 600
    escena.render.fps = 24
    cams["CAM_DRON"] = cam
    # flecha de norte verdadero (empty), para orientar la escena y el sol
    n = bpy.data.objects.new("NORTE_VERDADERO", None)
    n.empty_display_type = "SINGLE_ARROW"
    n.empty_display_size = 12
    n.location = (-12.0, -12.0, 0.2)
    n.rotation_euler = (math.radians(-90), 0, math.radians(NORTE_LOCAL_DEG - 90))   # flecha (+Z) hacia el norte verdadero
    col.objects.link(n)
    return cams


def camaras_propuestas(col):
    """Cámaras de las propuestas de color (pedido del 3 de octubre)."""
    return {
        # la perspectiva de la captura del cliente (resuelta con 11 puntos, error 1,3 px), mejorada: fachada completa
        # con márgenes del 3,5 %, cámara horizontal (verticales rectas) y edificio centrado en altura, 28 mm desde
        # 6,0 m de altura y 32° de oblicuidad
        "CAM_07_PROPUESTAS": camara("CAM_07_PROPUESTAS", (83.851, -43.695, 6.0),
                                    (83.851 - 26.50, -43.695 + 42.40, 6.0), 28, col),
        # la captura del cliente tal cual: 26 mm desde 6,85 m, levemente inclinada hacia abajo
        "CAM_07B_CAPTURA_CLIENTE": camara("CAM_07B_CAPTURA_CLIENTE", (78.01, -46.19, 6.85),
                                          (78.01 - 25.04, -46.19 + 43.27, 6.85 - 1.34), 26.1, col),
    }


def config_render(sc, muestras=256):
    sc.render.engine = "CYCLES"
    sc.cycles.samples = muestras
    try:
        sc.cycles.use_denoising = True
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    try:
        sc.cycles.device = "GPU"
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = 3840, 2160
    sc.render.resolution_percentage = 50
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.length_unit = "METERS"
    sc.unit_settings.scale_length = 1.0


def geometria_letrero(sc, variante):
    """Deja visible la geometría "A" (sobresale) o "B" (contenida) del letrero en todas las capas de vista de sc."""
    def buscar(lc, nombre):
        if lc.name == nombre:
            return lc
        for h in lc.children:
            r = buscar(h, nombre)
            if r:
                return r
    for vl in sc.view_layers:
        vl.update()                    # en una escena nueva la capa de vista se sincroniza recién al actualizarla
        for nombre in variantes_letrero():
            lc = buscar(vl.layer_collection, nombre)
            if lc:
                lc.exclude = not nombre.startswith("LETRERO_" + variante)


def georreferencia(sc):
    sc["UTM_EPSG"] = 32719
    sc["UTM_E_origen"] = 724956.439
    sc["UTM_N_origen"] = 7737860.959
    sc["cota_NPT_msnm"] = 3666.593
    sc["rotacion_X_local_deg_CCW_desde_Este"] = 148.2058
    sc["norte_verdadero_local_deg_CCW_desde_X"] = NORTE_LOCAL_DEG


# =============================================================================
# 6. EJECUCIÓN
# =============================================================================
# Propiedades que leen los materiales: "propuesta" (0 = P1, 1 = P2), "letras_corten" (1 = corten) y "letras_gris"
# (1 = gris casi negro, 0 = blanco, si no son corten)
PROPIEDADES_ESCENA = {"UYUNI_DIA": dict(propuesta=0, letras_corten=1, letras_gris=0),
                      "UYUNI_DIA_P2_SALAR_LITIO": dict(propuesta=1, letras_corten=0, letras_gris=1),
                      "UYUNI_CREPUSCULO": dict(propuesta=0, letras_corten=0, letras_gris=0)}


def propiedades_escena(sc):
    for k, v in PROPIEDADES_ESCENA.get(sc.name, {}).items():
        sc[k] = v


def escena_propuesta_2(sc, C, luz_dia, cam, muestras):
    """La misma mañana con la propuesta 2 (Salar & Litio): comparte colecciones, sol y cielo; cambia la paleta."""
    sc3 = bpy.data.scenes.new("UYUNI_DIA_P2_SALAR_LITIO")
    for n in COLECCIONES:
        sc3.collection.children.link(C[n])
    sc3.collection.children.link(luz_dia)
    sc3.world = sc.world
    for k in ("humedad", "nieve", "luz_interior", "luz_alero", "luz_letrero"):
        sc3[k] = sc[k]
    propiedades_escena(sc3)
    sc3.camera = cam
    config_render(sc3, muestras)
    georreferencia(sc3)
    return sc3


def nieve_crepusculo(col, M):
    """Nieve sutil en el borde de la cubierta (escena de crepúsculo): una capa fina hasta el retenedor y, pendiente
    arriba, la que el retenedor sostiene, apoyada contra su tubo inferior."""
    nv = Malla()
    y0 = PERFIL_CUBIERTA[0][0]
    (yb, _), _, _ = retenedor_marco()
    ya = yb + 1.80                                           # hasta dónde llega la nieve retenida
    z = z_cubierta
    nv.prisma_yz([(y0 + 0.02, z(y0) + 0.01), (ya, z(ya) + 0.01), (ya, z(ya) + 0.03), (yb + 0.03, z(yb) + 0.075),
                  (yb + 0.01, z(yb) + 0.05), (yb - 0.02, z(yb) + 0.03), (y0 + 0.02, z(y0) + 0.03)],
                 X_ALERO[0] + 0.05, X_ALERO[1] - 0.05)
    nv.crear("NIEVE_BORDE_CUBIERTA", M["nieve"], col, suave=True)


def construir(muestras=256, continuacion=True):
    limpiar()
    sc = bpy.context.scene
    sc.name = "UYUNI_DIA"
    C = {n: coleccion(n) for n in COLECCIONES}
    for n in ("REF_CAD_PLANTA_GENERAL", "REF_CAD_ALZADO_LADO_TIERRA", "REF_CAD_DETALLES_M1", "REF_CAD_DETALLES_CUBIERTA",
              "REF_CAD_DETALLES_CELOSIA"):
        coleccion(n, C["_REF_CAD"])
    M = crear_materiales()
    estructura(C, M)
    muro_landside(C, M)
    mamparas(C, M)
    antepecho_alero(C, M)
    cubierta(C, M)
    envolvente_general(C, M)
    elementos_laterales(C, M)
    celosias(C, M)
    letrero(C, M)
    entorno(C, M)
    mangas_y_aviones(C, M)
    assets(C, M)
    referencias_cad(C)
    cams = camaras_y_dron(C, sc)

    # --- escena de día (mañana): sol calculado, cielo de dispersión múltiple a 3667 m
    az, el = sol_posicion(*FECHA_DIA)
    luz_dia = coleccion("08_LUZ_DIA", sc.collection)
    sol("SOL_MANANA", az, el, 4.5, luz_dia)
    sc.world = mundo("CIELO_MANANA", az, el, 0.18)
    sc["humedad"], sc["nieve"], sc["luz_interior"], sc["luz_alero"], sc["luz_letrero"] = 0.0, 0.0, 0.6, 0.0, 0.0
    propiedades_escena(sc)
    sc.camera = cams["CAM_01_HERO_LADO_TIERRA"]
    config_render(sc, muestras)
    georreferencia(sc)
    sc3 = escena_propuesta_2(sc, C, luz_dia, cams["CAM_07_PROPUESTAS"], muestras)

    # --- escena de crepúsculo: comparte las colecciones; cambian luz, cielo y propiedades (humedad, nieve)
    sc2 = bpy.data.scenes.new("UYUNI_CREPUSCULO")
    for n in COLECCIONES:
        sc2.collection.children.link(C[n])
    az2, el2 = sol_posicion(*FECHA_CREPUSCULO)
    luz_cre = coleccion("08_LUZ_CREPUSCULO", sc2.collection)
    sol("LUNA_RELLENO", (az2 + 180) % 360, 35.0, 0.03, luz_cre, temp=7500)
    xs = sorted(EJES_X.values())
    yc = (Y_ANTEPECHO_EXT + E_ANTEPECHO + Y_MURO_EXT) / 2
    for xa, xb in zip(xs, xs[1:]):   # un spot cálido por vano bajo el cielo listonado
        xm = (xa + xb) / 2
        if X_ALERO[0] + 0.5 < xm < X_ALERO[1] - 0.5 and xb - xa > 1:
            ld = bpy.data.lights.new(f"{PREFIJO}SPOT_ALERO_{xm:05.1f}", "SPOT")
            ld.energy, ld.spot_size, ld.spot_blend, ld.shadow_soft_size = 120.0, math.radians(110), 0.6, 0.05
            if hasattr(ld, "use_temperature"):
                ld.use_temperature, ld.temperature = True, 3000
            ob = bpy.data.objects.new(ld.name, ld)
            ob.location = (xm, yc, Z_CIELO - 0.01)
            luz_cre.objects.link(ob)
    sc2.world = mundo("CIELO_HORA_AZUL", az2, max(el2, -4.0), 0.9)
    sc2["humedad"], sc2["nieve"], sc2["luz_interior"], sc2["luz_alero"], sc2["luz_letrero"] = 1.0, 0.6, 7.0, 1.0, 2.5
    propiedades_escena(sc2)
    for fach, tipo, a_, b_ in CELOSIAS:   # bañadores cálidos al pie de las celosías del Lado Tierra
        if fach != "NE":
            continue
        ld = bpy.data.lights.new(f"{PREFIJO}UPLIGHT_CELOSIA_{a_:05.1f}", "SPOT")
        ld.energy, ld.spot_size, ld.spot_blend, ld.shadow_soft_size = 220.0, math.radians(60), 0.5, 0.03
        if hasattr(ld, "use_temperature"):
            ld.use_temperature, ld.temperature = True, 2700
        ob = bpy.data.objects.new(ld.name, ld)
        ob.location = ((a_ + b_) / 2, Y_COL_EXT - CELOSIA_SEP - 0.9, 0.05)
        ob.rotation_euler = Vector((0.0, 0.32, 1.0)).to_track_quat("-Z", "Y").to_euler()
        luz_cre.objects.link(ob)
    nieve_crepusculo(coleccion("09_NIEVE_CREPUSCULO", sc2.collection), M)
    sc2.camera = cams["CAM_03_CREPUSCULAR_NIEVE"]
    config_render(sc2, muestras)
    sc2.view_settings.exposure = 0.6
    georreferencia(sc2)
    for escena in (sc, sc2, sc3):   # geometría A del letrero visible; la B queda excluida (se activa a mano)
        geometria_letrero(escena, "A")
    if continuacion:
        import sys
        from pathlib import Path
        carpeta = str(Path(__file__).resolve().parent)
        if carpeta not in sys.path:
            sys.path.insert(0, carpeta)
        from continuacion.pipeline import aplicar
        aplicar(globals())
    print(f"[UYUNI] Modelo generado. Sol mañana: azimut {az:.1f}°, elevación {el:.1f}° | crepúsculo: {az2:.1f}°, {el2:.1f}°")
    return sc, sc2


if __name__ == "__main__":   # Blender (Run Script) y exec(..., {"__name__": "__main__"}) lo ejecutan; el parche solo lo carga
    construir()
