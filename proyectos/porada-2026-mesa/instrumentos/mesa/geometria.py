"""Piezas como prismas rectos. Ejes: x a lo largo (centro en 0), y a lo ancho (centro en 0), z hacia arriba (suelo en 0). mm."""
from dataclasses import dataclass, field

from .materiales import Material

# Funciones del Cuadro 1 del artículo, más la unión.
SIMBOLO = {"apoyo": "⊥", "vano": "○", "masa": "●", "limite": "=", "union": "✕"}


@dataclass
class Pieza:
    nombre: str
    material: Material
    x: tuple
    y: tuple
    z: tuple
    funcion: str
    vacio_mm3: float = 0.0   # agujeros o cajas a descontar

    @property
    def volumen_mm3(self):
        return (self.x[1] - self.x[0]) * (self.y[1] - self.y[0]) * (self.z[1] - self.z[0]) - self.vacio_mm3

    @property
    def masa_kg(self):
        return self.volumen_mm3 * 1e-9 * self.material.densidad

    @property
    def centro(self):
        return tuple((a + b) / 2 for a, b in (self.x, self.y, self.z))


@dataclass
class Mesa:
    codigo: str
    nombre: str
    accion: str
    relacion: str
    piezas: list
    nodo: dict = field(default_factory=dict)      # datos de la unión para los ensayos
    juntas: list = field(default_factory=list)    # uniones piedra-madera para E2
    ronda: int = 1                                 # 1: versiones iniciales; 2: derivadas de los ensayos

    def masa(self, sin_piedra=False):
        return sum(p.masa_kg for p in self.piezas if not (sin_piedra and p.material.es_piedra))

    def cdg(self, sin_piedra=False):
        ps = [p for p in self.piezas if not (sin_piedra and p.material.es_piedra)]
        m = sum(p.masa_kg for p in ps)
        return tuple(sum(p.masa_kg * p.centro[i] for p in ps) / m for i in range(3))

    def volumen(self, piedra):
        return sum(p.volumen_mm3 for p in self.piezas if p.material.es_piedra == piedra)

    def pieza_mas_pesada(self):
        return max(self.piezas, key=lambda p: p.masa_kg)

    def piezas_de(self, nombre):
        return [p for p in self.piezas if p.nombre.startswith(nombre)]
