"""Materiales con su procedencia. Unidades: kg/m3, MPa, cambio dimensional por 1 % de contenido de humedad."""
from dataclasses import dataclass

# Resistencia de diseño = media de probeta / FACTOR_DISENO (supuesto común de los ensayos).
FACTOR_DISENO = 3.0


@dataclass(frozen=True)
class Material:
    nombre: str
    densidad: float      # a 12 % CH para madera: GE * 1,12 * 1000
    mor: float           # módulo de rotura (flexión), media
    comp_par: float      # compresión paralela a la fibra (en piedra: compresión)
    comp_perp: float     # compresión perpendicular a la fibra (en piedra: igual a comp_par)
    corte: float         # corte paralelo a la fibra
    cr: float            # coeficiente radial
    ct: float            # coeficiente tangencial
    fuente: str
    es_piedra: bool = False
    mor_alto: float | None = None   # extremo alto del rango, solo piedra

    def diseno(self, valor):
        return valor / FACTOR_DISENO


FPL = "FPL 2010 (FPL-GTR-190), tabla 5-3a p. 5-4 a 5-6 y tabla 13-5 p. 13-16"

NOGAL = Material("nogal canaleta (Juglans nigra)", 0.55 * 1.12 * 1000, 101, 52.3, 7.0, 9.4, 0.00190, 0.00274, FPL)
FRESNO = Material("fresno (Fraxinus americana)", 0.60 * 1.12 * 1000, 103, 51.1, 8.0, 13.2, 0.00169, 0.00274, FPL)

# Mármol: MOR típico 7-15 MPa (a confirmar con ficha EN 12372 del mármol elegido; Kessler 1919 tabla 6 pendiente).
# Compresión: mínimo medido por Kessler 1919 p. 11 (7 850 psi ≈ 54 MPa). No se mueve con la humedad.
MARMOL = Material("mármol (catálogo Porada, por elegir)", 2700, 7.0, 54.0, 54.0, 0.0, 0.0, 0.0,
                  "Kessler 1919 pp. 11-12; rango MOR típico, a confirmar", es_piedra=True, mor_alto=15.0)
