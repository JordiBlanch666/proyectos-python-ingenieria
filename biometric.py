from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np


@dataclass
class FaceMetrics:
    bounding_box: dict
    center: dict
    area_ratio: float
    aspect_ratio: float
    mean_brightness: float


def load_face_detector() -> cv2.CascadeClassifier:
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(str(cascade_path))
    if detector.empty():
        raise RuntimeError(f"No se pudo cargar el detector facial desde {cascade_path}")
    return detector


def ensure_color_image(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.ndim == 3 and image.shape[2] == 3:
        return image
    raise ValueError("La imagen debe ser grayscale o BGR.")


def compute_face_metrics(image: np.ndarray, face_box: tuple[int, int, int, int]) -> FaceMetrics:
    color_image = ensure_color_image(image)
    x, y, width, height = face_box
    image_height, image_width = color_image.shape[:2]

    face_region = color_image[y:y + height, x:x + width]
    if face_region.size == 0:
        raise ValueError("La región del rostro está fuera de los límites de la imagen.")

    gray_region = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
    return FaceMetrics(
        bounding_box={"x": int(x), "y": int(y), "width": int(width), "height": int(height)},
        center={"x": int(x + (width / 2)), "y": int(y + (height / 2))},
        area_ratio=round((width * height) / float(image_width * image_height), 4),
        aspect_ratio=round(width / float(height), 4),
        mean_brightness=round(float(np.mean(gray_region)), 2),
    )


def detect_faces(
    image: np.ndarray,
    detector: Any = None,
    scale_factor: float = 1.1,
    min_neighbors: int = 5,
) -> list[tuple[int, int, int, int]]:
    color_image = ensure_color_image(image)
    gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
    detector = detector or load_face_detector()
    faces = detector.detectMultiScale(
        gray_image,
        scaleFactor=scale_factor,
        minNeighbors=min_neighbors,
        minSize=(40, 40),
    )
    return [
        (int(face[0]), int(face[1]), int(face[2]), int(face[3]))
        for face in faces
    ]


def summarize_faces(image: np.ndarray, faces: list[tuple[int, int, int, int]]) -> dict:
    return {
        "face_count": len(faces),
        "faces": [asdict(compute_face_metrics(image, face_box)) for face_box in faces],
    }


def draw_face_annotations(image: np.ndarray, summary: dict) -> np.ndarray:
    annotated = ensure_color_image(image).copy()
    for index, face in enumerate(summary["faces"], start=1):
        x = face["bounding_box"]["x"]
        y = face["bounding_box"]["y"]
        width = face["bounding_box"]["width"]
        height = face["bounding_box"]["height"]
        brightness = face["mean_brightness"]

        cv2.rectangle(annotated, (x, y), (x + width, y + height), (0, 200, 0), 2)
        cv2.putText(
            annotated,
            f"Rostro {index} | brillo={brightness:.1f}",
            (x, max(20, y - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 200, 0),
            1,
        )
    return annotated


def analyze_image(image_path: str | Path, save_annotated: str | Path | None = None) -> dict:
    image_path = Path(image_path)
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"No se pudo abrir la imagen: {image_path}")

    faces = detect_faces(image)
    summary = summarize_faces(image, faces)
    summary["image_path"] = str(image_path)

    if save_annotated:
        output_path = Path(save_annotated)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        annotated = draw_face_annotations(image, summary)
        if not cv2.imwrite(str(output_path), annotated):
            raise RuntimeError(f"No se pudo guardar la imagen anotada en {output_path}")
        summary["annotated_path"] = str(output_path)

    return summary


def run_webcam_demo(camera_index: int = 0) -> None:
    detector = load_face_detector()
    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        raise RuntimeError("No se pudo acceder a la cámara web.")

    print("Demo segura iniciada. Presiona 'q' para cerrar la ventana.")
    print("Este programa detecta rostros y calcula métricas visuales básicas; no identifica personas.")

    try:
        while True:
            success, frame = capture.read()
            if not success:
                raise RuntimeError("No fue posible leer un frame de la cámara.")

            faces = detect_faces(frame, detector=detector)
            summary = summarize_faces(frame, faces)
            annotated = draw_face_annotations(frame, summary)
            cv2.putText(
                annotated,
                f"Rostros detectados: {summary['face_count']}",
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (50, 220, 255),
                2,
            )
            cv2.imshow("Demo facial segura", annotated)
            if (cv2.waitKey(1) & 0xFF) == ord("q"):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Demo local de detección facial segura con métricas visuales básicas."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--image", type=str, help="Ruta de la imagen a analizar.")
    group.add_argument("--webcam", action="store_true", help="Abre la webcam para detección en vivo.")
    parser.add_argument("--save-annotated", type=str, help="Ruta donde guardar la imagen anotada.")
    parser.add_argument("--camera-index", type=int, default=0, help="Índice de la cámara para --webcam.")
    return parser


def print_quick_start(parser: argparse.ArgumentParser) -> None:
    print("No se indicó ningún modo de ejecución. Usa una imagen o la webcam.\n")
    parser.print_help()
    print("\nEjemplos:")
    print("  python biometric.py --image .\\foto.jpg")
    print("  python biometric.py --image .\\foto.jpg --save-annotated .\\foto_anotada.jpg")
    print("  python biometric.py --webcam")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    effective_argv = list(sys.argv[1:] if argv is None else argv)
    if not effective_argv:
        print_quick_start(parser)
        return 0

    args = parser.parse_args(effective_argv)

    if args.webcam:
        run_webcam_demo(camera_index=args.camera_index)
        return 0

    if not args.image:
        print("Debes indicar `--image` o `--webcam`.\n")
        parser.print_help()
        return 1

    summary = analyze_image(args.image, save_annotated=args.save_annotated)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

