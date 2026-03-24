import string
import tempfile
import unittest
from pathlib import Path

import password_app


class PasswordAppTests(unittest.TestCase):
    def test_generate_password_incluye_tipos_de_caracteres_requeridos(self):
        password = password_app.generate_password(length=20, include_symbols=True)

        self.assertEqual(len(password), 20)
        self.assertTrue(any(character in string.ascii_lowercase for character in password))
        self.assertTrue(any(character in string.ascii_uppercase for character in password))
        self.assertTrue(any(character in string.digits for character in password))
        self.assertTrue(any(character in password_app.SYMBOLS for character in password))

    def test_generate_password_sin_simbolos_no_agrega_simbolos(self):
        password = password_app.generate_password(length=18, include_symbols=False)

        self.assertEqual(len(password), 18)
        self.assertFalse(any(character in password_app.SYMBOLS for character in password))
        self.assertTrue(any(character in string.ascii_lowercase for character in password))
        self.assertTrue(any(character in string.ascii_uppercase for character in password))
        self.assertTrue(any(character in string.digits for character in password))

    def test_validate_options_rechaza_longitud_demasiado_corta(self):
        with self.assertRaises(ValueError):
            password_app.validate_options(length=3, count=1, include_symbols=True)

        with self.assertRaises(ValueError):
            password_app.validate_options(length=2, count=1, include_symbols=False)

    def test_save_passwords_crea_archivo_txt_con_etiqueta(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "generated_passwords.txt"
            saved_path = password_app.save_passwords(
                passwords=["ClaveSegura1!", "OtraClave2@"],
                output_path=output_path,
                label="correo",
                append=True,
            )

            self.assertEqual(saved_path, output_path)
            self.assertTrue(output_path.exists())

            content = output_path.read_text(encoding="utf-8")
            self.assertIn("correo #1", content)
            self.assertIn("ClaveSegura1!", content)
            self.assertIn("correo #2", content)
            self.assertIn("OtraClave2@", content)

    def test_save_passwords_con_overwrite_reemplaza_el_contenido(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "generated_passwords.txt"
            output_path.write_text("contenido anterior", encoding="utf-8")

            password_app.save_passwords(
                passwords=["NuevaClave9!"],
                output_path=output_path,
                label="banco",
                append=False,
            )

            content = output_path.read_text(encoding="utf-8")
            self.assertNotIn("contenido anterior", content)
            self.assertTrue(content.startswith("20"))
            self.assertIn("banco #1", content)
            self.assertIn("NuevaClave9!", content)

    def test_generate_passwords_devuelve_cantidad_solicitada(self):
        passwords = password_app.generate_passwords(count=3, length=16, include_symbols=True)

        self.assertEqual(len(passwords), 3)
        self.assertEqual(len(set(passwords)), 3)
        self.assertTrue(all(len(password) == 16 for password in passwords))


if __name__ == "__main__":
    unittest.main()

