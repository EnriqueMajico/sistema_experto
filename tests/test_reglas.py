import os
import sys
import unittest

# Asegurar que Python encuentre 'motor.py' y 'explicacion.py' en la carpeta superior
RUTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RUTA_RAIZ not in sys.path:
    sys.path.insert(0, RUTA_RAIZ)

from motor import MotorInferencia3D


class TestSistemaExperto3D(unittest.TestCase):
    def setUp(self):
        self.motor = MotorInferencia3D("conocimiento/reglas.json")

    def test_total_reglas_cargadas(self):
        """Verifica que las 32 reglas del archivo JSON estén cargadas."""
        self.assertEqual(len(self.motor.reglas), 32)

    def test_encadenamiento_multifase_videojuego_highpoly(self):
        informe = self.motor.cotizar_detallado({
            "destino": "videojuego",
            "categoria": "personaje",
            "complejidad": "high_poly",
            "texturizado": "pbr_completo",
            "uso": "personal",
        })
        ids_activados = [r["id"] for r in informe["reglas_aplicadas"]]
        self.assertIn("R10", ids_activados)
        self.assertIn("R13", ids_activados)
        self.assertIn("R14", ids_activados)
        self.assertIn("R19", ids_activados)
        self.assertGreater(informe["costo_total"], 0)

    def test_inferencia_animacion_activa_rigging_organico(self):
        informe = self.motor.cotizar_detallado({
            "categoria": "personaje",
            "complejidad": "low_poly",
            "texturizado": "sin_texturas",
            "rigging": False,
            "animacion": True,
        })
        ids_activados = [r["id"] for r in informe["reglas_aplicadas"]]
        self.assertIn("R12", ids_activados)
        self.assertIn("R22", ids_activados)
        self.assertIn("R24", ids_activados)

    def test_alerta_incompatibilidad_impresion3d_pbr(self):
        informe = self.motor.cotizar_detallado({
            "destino": "impresion_3d",
            "categoria": "prop",
            "complejidad": "high_poly",
            "texturizado": "pbr_completo",
        })
        reglas_alerta = [a.get("regla") for a in informe["alertas"]]
        self.assertIn("R31", reglas_alerta)


if __name__ == "__main__":
    unittest.main()