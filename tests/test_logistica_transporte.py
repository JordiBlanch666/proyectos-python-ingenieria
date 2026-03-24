import contextlib
import io
import unittest
from unittest.mock import patch

import logistica_transporte


class LogisticaTransporteTests(unittest.TestCase):
    def test_calcular_costo_combustible_aplica_factor_de_carga_y_costos_operativos(self):
        costo, litros, factor = logistica_transporte.calcular_costo_combustible(
            distancia_km=300,
            rendimiento_km_litro=5,
            precio_combustible_litro=2,
            peso_carga_kg=2500,
            capacidad_maxima_kg=5000,
            peajes=30,
            costos_extra=20,
        )

        self.assertEqual(costo, 230.0)
        self.assertEqual(litros, 90.0)
        self.assertEqual(factor, 1.5)

    def test_calcular_costo_combustible_con_mayor_carga_incrementa_consumo(self):
        costo_ligero, litros_ligeros, _ = logistica_transporte.calcular_costo_combustible(
            distancia_km=200,
            rendimiento_km_litro=4,
            precio_combustible_litro=1.5,
            peso_carga_kg=1000,
            capacidad_maxima_kg=5000,
        )
        costo_pesado, litros_pesados, _ = logistica_transporte.calcular_costo_combustible(
            distancia_km=200,
            rendimiento_km_litro=4,
            precio_combustible_litro=1.5,
            peso_carga_kg=4000,
            capacidad_maxima_kg=5000,
        )

        self.assertGreater(costo_pesado, costo_ligero)
        self.assertGreater(litros_pesados, litros_ligeros)

    def test_puede_salir_a_ruta_autoriza_cuando_peso_y_clima_son_validos(self):
        autorizado, motivo = logistica_transporte.puede_salir_a_ruta(
            peso_carga_kg=3200,
            capacidad_maxima_kg=5000,
            clima="Despejado",
        )

        self.assertTrue(autorizado)
        self.assertIn("autorizada", motivo.lower())

    def test_puede_salir_a_ruta_bloquea_por_sobrecarga(self):
        autorizado, motivo = logistica_transporte.puede_salir_a_ruta(
            peso_carga_kg=6200,
            capacidad_maxima_kg=5000,
            clima="nublado",
        )

        self.assertFalse(autorizado)
        self.assertIn("capacidad máxima", motivo)

    def test_puede_salir_a_ruta_bloquea_por_clima_adverso(self):
        autorizado, motivo = logistica_transporte.puede_salir_a_ruta(
            peso_carga_kg=2000,
            capacidad_maxima_kg=5000,
            clima="tormenta",
        )

        self.assertFalse(autorizado)
        self.assertIn("clima actual", motivo)

    def test_main_muestra_reporte_autorizado(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            resultado = logistica_transporte.main(
                [
                    "--distance-km",
                    "180",
                    "--efficiency-km-l",
                    "6",
                    "--fuel-price",
                    "1.8",
                    "--weight-kg",
                    "2000",
                    "--max-weight-kg",
                    "5000",
                    "--climate",
                    "nublado",
                    "--tolls",
                    "25",
                ]
            )

        salida = buffer.getvalue()
        self.assertEqual(resultado, 0)
        self.assertIn("AUTORIZADO", salida)
        self.assertIn("Costo estimado", salida)

    def test_main_devuelve_error_si_el_precio_es_invalido(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            resultado = logistica_transporte.main(
                [
                    "--distance-km",
                    "180",
                    "--efficiency-km-l",
                    "6",
                    "--fuel-price",
                    "0",
                    "--weight-kg",
                    "2000",
                    "--max-weight-kg",
                    "5000",
                    "--climate",
                    "nublado",
                ]
            )

        salida = buffer.getvalue()
        self.assertEqual(resultado, 1)
        self.assertIn("Error", salida)

    def test_interactive_options_captura_los_datos_del_usuario(self):
        entradas = iter(["150", "5", "1.75", "1800", "4000", "llovizna", "20", "15"])

        with patch("builtins.input", side_effect=lambda _: next(entradas)):
            opciones = logistica_transporte.interactive_options()

        self.assertEqual(opciones.distancia_km, 150.0)
        self.assertEqual(opciones.rendimiento_km_litro, 5.0)
        self.assertEqual(opciones.precio_combustible_litro, 1.75)
        self.assertEqual(opciones.peso_carga_kg, 1800.0)
        self.assertEqual(opciones.capacidad_maxima_kg, 4000.0)
        self.assertEqual(opciones.clima, "llovizna")
        self.assertEqual(opciones.peajes, 20.0)
        self.assertEqual(opciones.costos_extra, 15.0)

    def test_interactive_options_reintenta_si_el_valor_es_invalido(self):
        entradas = iter(["", "100", "0", "5", "abc", "2", "-10", "0", "3000", "nublado", "", ""])
        buffer = io.StringIO()

        with patch("builtins.input", side_effect=lambda _: next(entradas)):
            with contextlib.redirect_stdout(buffer):
                opciones = logistica_transporte.interactive_options()

        salida = buffer.getvalue()
        self.assertIn("Este campo es obligatorio.", salida)
        self.assertIn("Ingresa un número válido.", salida)
        self.assertEqual(opciones.distancia_km, 100.0)
        self.assertEqual(opciones.rendimiento_km_litro, 5.0)
        self.assertEqual(opciones.precio_combustible_litro, 2.0)
        self.assertEqual(opciones.peso_carga_kg, 0.0)
        self.assertEqual(opciones.peajes, 0.0)
        self.assertEqual(opciones.costos_extra, 0.0)

    def test_main_en_modo_interactivo_muestra_reporte(self):
        entradas = iter(["180", "6", "1.8", "2000", "5000", "nublado", "25", "10"])
        buffer = io.StringIO()

        with patch("builtins.input", side_effect=lambda _: next(entradas)):
            with contextlib.redirect_stdout(buffer):
                resultado = logistica_transporte.main(["--interactive"])

        salida = buffer.getvalue()
        self.assertEqual(resultado, 0)
        self.assertIn("AUTORIZADO", salida)
        self.assertIn("Evaluación de Logística de Transporte", salida)


if __name__ == "__main__":
    unittest.main()
