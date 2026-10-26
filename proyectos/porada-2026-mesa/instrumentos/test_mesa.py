"""Comprobaciones de las fórmulas contra cálculos a mano. Correr: python3 -m unittest test_mesa (desde instrumentos/)."""
import unittest

from mesa import versiones
from mesa.calculos import e1_viga_piedra, e2_movimiento, e3_vuelco, e4_union, e12_interferencias
from mesa.materiales import NOGAL


class Formulas(unittest.TestCase):
    def setUp(self):
        versiones.configurar()

    def test_viga_piedra_a_mano(self):
        # Barra 160 × 40, luz 1500, P = 1000 N: M = PL/4 = 375 000 N·mm; S = bh²/6 = 42 667 mm³ → 8,79 MPa.
        r = e1_viga_piedra(versiones.v0())
        self.assertAlmostEqual(r["sigma_P"], 375000 / (160 * 40 ** 2 / 6), places=6)
        self.assertFalse(r["cumple"])

    def test_movimiento_canal(self):
        # Canal de 160 mm, CT nogal 0,00274: secado 8→4 % = 1,75 mm; total 4→13 % = 3,95 mm; por lado, la mitad.
        j = e2_movimiento(versiones.v0b())["juntas"][0]
        self.assertAlmostEqual(j["holgura_fabricacion_por_lado"], 160 * NOGAL.ct * 4 / 2, places=6)
        self.assertAlmostEqual(j["junta_maxima_por_lado"], 160 * NOGAL.ct * 9 / 2, places=6)

    def test_vuelco_simetrico_y_monotono(self):
        r = e3_vuelco(versiones.v0())
        self.assertAlmostEqual(r["con_piedra"]["xg"], 0.0, places=6)
        self.assertGreater(r["con_piedra"]["vuelco_extremo_N"], r["sin_piedra"]["vuelco_extremo_N"])
        self.assertAlmostEqual(r["aporte_piedra"]["vuelco_extremo_N"], r["aporte_piedra"]["vuelco_borde_N"], places=6)

    def test_control_sin_piedra(self):
        r = e3_vuelco(versiones.v3())
        self.assertEqual(r["aporte_piedra"]["vuelco_extremo_N"], 0.0)

    def test_llave_modelos(self):
        # Modelo a dobla la tracción del modelo b; la tensión escala igual.
        r = e4_union(versiones.v1())["modelos"]
        self.assertAlmostEqual(r["a"]["T_N"], 2 * r["b"]["T_N"], places=6)
        self.assertAlmostEqual(r["a"]["sigma_llave"], 2 * r["b"]["sigma_llave"], places=6)

    def test_configurar_mueve_la_arista(self):
        versiones.configurar(pie_x=180)
        r = e3_vuelco(versiones.v3())
        self.assertAlmostEqual(r["sin_piedra"]["x_eje"], versiones.XC + 90, places=6)

    def test_interferencias(self):
        # E12: AB tiene la clavija y la cuña de las tablas centrales dentro del montante; F1 no.
        versiones.configurar(a_extremo=450, pie_x=180)
        ab, f1 = e12_interferencias(versiones.ab()), e12_interferencias(versiones.f1())
        self.assertEqual(len(ab["errores"]), 8)
        self.assertTrue(all("montante" in x["b"] for x in ab["errores"]))
        self.assertEqual(f1["errores"], [])
        self.assertTrue(f1["grupos_cumplen"])


if __name__ == "__main__":
    unittest.main()
