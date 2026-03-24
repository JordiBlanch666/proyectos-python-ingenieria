import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

import Prueba


class PlanificadorViajesTests(unittest.TestCase):
    def test_normalizar_texto_ignora_acentos_y_mayusculas(self):
        self.assertEqual(Prueba.normalizar_texto("París"), "paris")
        self.assertEqual(Prueba.normalizar_texto("  BOGOTÁ "), "bogota")

    def test_construir_catalogo_calcula_promedios_esperados(self):
        catalogo = Prueba.construir_catalogo_viajes()
        buenos_aires = catalogo[Prueba.normalizar_texto("Buenos Aires")]
        paris = next(destino for destino in buenos_aires["destinos"] if destino.nombre == "París")

        self.assertAlmostEqual(paris.promedio_vuelo, 1000.0)
        self.assertAlmostEqual(paris.promedio_hospedaje, 152.5)
        self.assertIn("aerolineas.csv", paris.fuentes)
        self.assertIn("aerolineas.json", paris.fuentes)
        self.assertIn("hospedaje.csv", paris.fuentes)
        self.assertIn("hospedaje.db", paris.fuentes)

    def test_viaje_calcula_total_estimado(self):
        catalogo = Prueba.construir_catalogo_viajes()
        lima = catalogo[Prueba.normalizar_texto("Lima")]
        tokio = next(destino for destino in lima["destinos"] if destino.nombre == "Tokio")

        viaje = Prueba.Viaje("Lima", tokio, 4, 80)

        self.assertAlmostEqual(viaje.calcular_costo_vuelo(), 1500.0)
        self.assertAlmostEqual(viaje.calcular_costo_hospedaje(), 680.0)
        self.assertAlmostEqual(viaje.calcular_costo_total(), 2260.0)

    def test_asegurar_base_hospedaje_crea_datos_en_sqlite(self):
        with tempfile.TemporaryDirectory() as carpeta_temporal:
            ruta_db = Path(carpeta_temporal) / "hospedaje_test.db"
            Prueba.asegurar_base_hospedaje(ruta_db)

            with closing(sqlite3.connect(ruta_db)) as conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT COUNT(*) FROM hospedaje")
                total = cursor.fetchone()[0]

            self.assertEqual(total, len(Prueba.SEMILLA_HOSPEDAJE_DB))


if __name__ == "__main__":
    unittest.main()

