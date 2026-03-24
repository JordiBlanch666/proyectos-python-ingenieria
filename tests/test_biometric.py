import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

import biometric


class BiometricTests(unittest.TestCase):
    def test_main_sin_argumentos_muestra_ayuda_y_devuelve_cero(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            result = biometric.main([])

        output = buffer.getvalue()
        self.assertEqual(result, 0)
        self.assertIn("--image", output)
        self.assertIn("--webcam", output)

    def test_ensure_color_image_convierte_grayscale_a_bgr(self):
        image = np.zeros((10, 10), dtype=np.uint8)
        converted = biometric.ensure_color_image(image)

        self.assertEqual(converted.shape, (10, 10, 3))

    def test_compute_face_metrics_calcula_valores_esperados(self):
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[20:60, 10:40] = 200

        metrics = biometric.compute_face_metrics(image, (10, 20, 30, 40))

        self.assertEqual(metrics.bounding_box["x"], 10)
        self.assertEqual(metrics.bounding_box["y"], 20)
        self.assertEqual(metrics.bounding_box["width"], 30)
        self.assertEqual(metrics.bounding_box["height"], 40)
        self.assertEqual(metrics.center, {"x": 25, "y": 40})
        self.assertAlmostEqual(metrics.area_ratio, 0.12)
        self.assertAlmostEqual(metrics.aspect_ratio, 0.75)
        self.assertAlmostEqual(metrics.mean_brightness, 200.0)

    def test_detect_faces_en_imagen_vacia_devuelve_lista_vacia(self):
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        faces = biometric.detect_faces(image)
        self.assertEqual(faces, [])

    def test_analyze_image_guarda_anotacion(self):
        image = np.zeros((120, 120, 3), dtype=np.uint8)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            image_path = temp_path / "blank.png"
            annotated_path = temp_path / "annotated.png"
            cv2.imwrite(str(image_path), image)

            summary = biometric.analyze_image(image_path, save_annotated=annotated_path)

            self.assertEqual(summary["face_count"], 0)
            self.assertEqual(summary["image_path"], str(image_path))
            self.assertEqual(summary["annotated_path"], str(annotated_path))
            self.assertTrue(annotated_path.exists())

    def test_main_con_image_devuelve_json(self):
        image = np.zeros((120, 120, 3), dtype=np.uint8)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            image_path = temp_path / "blank.png"
            cv2.imwrite(str(image_path), image)

            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                result = biometric.main(["--image", str(image_path)])

            output = json.loads(buffer.getvalue())
            self.assertEqual(result, 0)
            self.assertEqual(output["face_count"], 0)
            self.assertEqual(output["image_path"], str(image_path))


if __name__ == "__main__":
    unittest.main()

