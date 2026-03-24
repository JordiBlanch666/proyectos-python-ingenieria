from __future__ import annotations

import argparse
import secrets
import string
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

LOWERCASE = string.ascii_lowercase
UPPERCASE = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/"
DEFAULT_OUTPUT = Path("passwords.txt")


@dataclass
class PasswordOptions:
    length: int = 16
    count: int = 1
    include_symbols: bool = True
    output_path: Path = DEFAULT_OUTPUT
    label: str = "general"
    append: bool = True


def secure_shuffle(characters: list[str]) -> str:
    shuffled = characters[:]
    for index in range(len(shuffled) - 1, 0, -1):
        swap_index = secrets.randbelow(index + 1)
        shuffled[index], shuffled[swap_index] = shuffled[swap_index], shuffled[index]
    return "".join(shuffled)


def validate_options(length: int, count: int, include_symbols: bool) -> None:
    required_groups = 4 if include_symbols else 3
    if length < required_groups:
        raise ValueError(
            f"La longitud mínima es {required_groups} para incluir todos los tipos de caracteres requeridos."
        )
    if count <= 0:
        raise ValueError("La cantidad de contraseñas debe ser mayor que cero.")


def generate_password(length: int = 16, include_symbols: bool = True) -> str:
    validate_options(length=length, count=1, include_symbols=include_symbols)

    pools = [LOWERCASE, UPPERCASE, DIGITS]
    if include_symbols:
        pools.append(SYMBOLS)

    password_characters = [secrets.choice(pool) for pool in pools]
    combined_pool = "".join(pools)

    for _ in range(length - len(password_characters)):
        password_characters.append(secrets.choice(combined_pool))

    return secure_shuffle(password_characters)


def generate_passwords(count: int = 1, length: int = 16, include_symbols: bool = True) -> list[str]:
    validate_options(length=length, count=count, include_symbols=include_symbols)
    return [generate_password(length=length, include_symbols=include_symbols) for _ in range(count)]


def build_entry_lines(passwords: list[str], label: str) -> list[str]:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    for index, password in enumerate(passwords, start=1):
        lines.append(f"{timestamp} | {label} #{index} | {password}")
    return lines


def save_passwords(passwords: list[str], output_path: str | Path, label: str = "general", append: bool = True) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = build_entry_lines(passwords, label)
    if append and path.exists() and path.stat().st_size > 0:
        content = "\n" + "\n".join(lines)
    else:
        content = "\n".join(lines)

    mode = "a" if append else "w"
    with path.open(mode, encoding="utf-8") as file:
        file.write(content)

    return path


def ask_positive_int(prompt: str, default: int) -> int:
    while True:
        value = input(f"{prompt} [{default}]: ").strip()
        if not value:
            return default
        try:
            number = int(value)
            if number > 0:
                return number
            print("Ingresa un número mayor que cero.")
        except ValueError:
            print("Ingresa un número entero válido.")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    default_text = "S/n" if default else "s/N"
    while True:
        value = input(f"{prompt} [{default_text}]: ").strip().lower()
        if not value:
            return default
        if value in {"s", "si", "sí", "y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        print("Responde con 's' o 'n'.")


def ask_text(prompt: str, default: str) -> str:
    value = input(f"{prompt} [{default}]: ").strip()
    return value or default


def interactive_options() -> PasswordOptions:
    print("=== Generador de contraseñas seguras ===")
    length = ask_positive_int("Longitud de la contraseña", 16)
    count = ask_positive_int("Cantidad de contraseñas a generar", 1)
    include_symbols = ask_yes_no("¿Incluir símbolos especiales?", True)
    label = ask_text("Etiqueta para guardar en el archivo", "general")
    output_path = Path(ask_text("Archivo de salida .txt", str(DEFAULT_OUTPUT)))
    append = ask_yes_no("¿Agregar al archivo si ya existe?", True)
    validate_options(length=length, count=count, include_symbols=include_symbols)
    return PasswordOptions(
        length=length,
        count=count,
        include_symbols=include_symbols,
        output_path=output_path,
        label=label,
        append=append,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Genera contraseñas seguras y las guarda en un archivo .txt"
    )
    parser.add_argument("--length", type=int, default=16, help="Longitud de cada contraseña.")
    parser.add_argument("--count", type=int, default=1, help="Cantidad de contraseñas a generar.")
    parser.add_argument(
        "--no-symbols",
        action="store_true",
        help="Genera contraseñas sin símbolos especiales.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Ruta del archivo .txt donde se guardarán las contraseñas.",
    )
    parser.add_argument("--label", type=str, default="general", help="Etiqueta para cada contraseña guardada.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Sobrescribe el archivo en lugar de agregar nuevas entradas.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Muestra las contraseñas generadas en consola además de guardarlas.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Ejecuta el programa en modo interactivo.",
    )
    return parser


def run_with_options(options: PasswordOptions, show_passwords: bool = True) -> tuple[list[str], Path]:
    passwords = generate_passwords(
        count=options.count,
        length=options.length,
        include_symbols=options.include_symbols,
    )
    saved_path = save_passwords(
        passwords=passwords,
        output_path=options.output_path,
        label=options.label,
        append=options.append,
    )

    print(f"Se generaron {len(passwords)} contraseña(s) seguras.")
    print(f"Archivo de salida: {saved_path.resolve()}")
    if show_passwords:
        print("\nContraseñas generadas:")
        for index, password in enumerate(passwords, start=1):
            print(f"{index}. {password}")

    return passwords, saved_path


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.interactive or (argv is None and len(sys.argv) == 1):
            options = interactive_options()
            run_with_options(options, show_passwords=True)
            return 0

        options = PasswordOptions(
            length=args.length,
            count=args.count,
            include_symbols=not args.no_symbols,
            output_path=args.output,
            label=args.label,
            append=not args.overwrite,
        )
        validate_options(length=options.length, count=options.count, include_symbols=options.include_symbols)
        run_with_options(options, show_passwords=args.show)
        return 0
    except ValueError as error:
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

