from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys

CLIMAS_PERMITIDOS = {"despejado", "nublado", "llovizna"}


@dataclass(frozen=True)
class RutaOptions:
    distancia_km: float
    rendimiento_km_litro: float
    precio_combustible_litro: float
    peso_carga_kg: float
    capacidad_maxima_kg: float
    clima: str
    peajes: float = 0.0
    costos_extra: float = 0.0


@dataclass(frozen=True)
class EvaluacionRuta:
    puede_salir: bool
    motivo: str
    costo_combustible: float
    litros_estimados: float
    factor_carga: float


def normalizar_clima(clima: str) -> str:
    return clima.strip().lower()


def validar_valor_positivo(nombre: str, valor: float, permitir_cero: bool = False) -> None:
    if permitir_cero and valor < 0:
        raise ValueError(f"{nombre} no puede ser negativo.")
    if not permitir_cero and valor <= 0:
        raise ValueError(f"{nombre} debe ser mayor que cero.")


def pedir_numero(prompt: str, permitir_cero: bool = False, default: float | None = None) -> float:
    while True:
        suffix = f" [{default}]" if default is not None else ""
        valor = input(f"{prompt}{suffix}: ").strip()
        if not valor and default is not None:
            return default

        try:
            numero = float(valor)
            validar_valor_positivo(prompt, numero, permitir_cero=permitir_cero)
            return numero
        except ValueError:
            if valor:
                print("Ingresa un número válido.")
            else:
                print("Este campo es obligatorio.")


def pedir_texto(prompt: str, default: str | None = None) -> str:
    while True:
        suffix = f" [{default}]" if default is not None else ""
        valor = input(f"{prompt}{suffix}: ").strip()
        if valor:
            return valor
        if default is not None:
            return default
        print("Este campo es obligatorio.")


def interactive_options() -> RutaOptions:
    print("=== Captura de datos de logística de transporte ===")
    print("Ingresa los valores solicitados para evaluar el costo y la salida a ruta.")

    return RutaOptions(
        distancia_km=pedir_numero("Distancia de la ruta en km"),
        rendimiento_km_litro=pedir_numero("Rendimiento del camión (km por litro)"),
        precio_combustible_litro=pedir_numero("Precio del combustible por litro"),
        peso_carga_kg=pedir_numero("Peso de la carga en kg", permitir_cero=True),
        capacidad_maxima_kg=pedir_numero("Capacidad máxima del camión en kg"),
        clima=pedir_texto("Clima actual (por ejemplo: despejado, nublado, tormenta)"),
        peajes=pedir_numero("Peajes estimados", permitir_cero=True, default=0.0),
        costos_extra=pedir_numero("Costos operativos extra", permitir_cero=True, default=0.0),
    )


def calcular_litros_estimados(
    distancia_km: float,
    rendimiento_km_litro: float,
    peso_carga_kg: float,
    capacidad_maxima_kg: float,
) -> tuple[float, float]:
    validar_valor_positivo("La distancia", distancia_km)
    validar_valor_positivo("El rendimiento", rendimiento_km_litro)
    validar_valor_positivo("La capacidad máxima", capacidad_maxima_kg)
    validar_valor_positivo("El peso de la carga", peso_carga_kg, permitir_cero=True)

    factor_carga = 1 + (peso_carga_kg / capacidad_maxima_kg)
    litros_base = distancia_km / rendimiento_km_litro
    litros_estimados = litros_base * factor_carga
    return litros_estimados, factor_carga


def calcular_costo_combustible(
    distancia_km: float,
    rendimiento_km_litro: float,
    precio_combustible_litro: float,
    peso_carga_kg: float,
    capacidad_maxima_kg: float,
    peajes: float = 0.0,
    costos_extra: float = 0.0,
) -> tuple[float, float, float]:
    validar_valor_positivo("El precio del combustible", precio_combustible_litro)
    validar_valor_positivo("Los peajes", peajes, permitir_cero=True)
    validar_valor_positivo("Los costos extra", costos_extra, permitir_cero=True)

    litros_estimados, factor_carga = calcular_litros_estimados(
        distancia_km=distancia_km,
        rendimiento_km_litro=rendimiento_km_litro,
        peso_carga_kg=peso_carga_kg,
        capacidad_maxima_kg=capacidad_maxima_kg,
    )
    costo_combustible = (litros_estimados * precio_combustible_litro) + peajes + costos_extra
    return round(costo_combustible, 2), round(litros_estimados, 2), round(factor_carga, 3)


def puede_salir_a_ruta(
    peso_carga_kg: float,
    capacidad_maxima_kg: float,
    clima: str,
    climas_permitidos: set[str] | None = None,
) -> tuple[bool, str]:
    validar_valor_positivo("La capacidad máxima", capacidad_maxima_kg)
    validar_valor_positivo("El peso de la carga", peso_carga_kg, permitir_cero=True)

    climas_validos = climas_permitidos or CLIMAS_PERMITIDOS
    clima_normalizado = normalizar_clima(clima)
    carga_en_rango = 0 <= peso_carga_kg <= capacidad_maxima_kg
    clima_seguro = clima_normalizado in climas_validos

    if carga_en_rango and clima_seguro:
        return True, "Salida autorizada: la carga y el clima cumplen la política operativa."
    if not carga_en_rango and not clima_seguro:
        return False, "Salida denegada: la carga excede el límite y el clima no es seguro."
    if not carga_en_rango:
        return False, "Salida denegada: la carga excede la capacidad máxima permitida."
    return False, "Salida denegada: el clima actual no cumple las condiciones de seguridad."


def evaluar_ruta(
    distancia_km: float,
    rendimiento_km_litro: float,
    precio_combustible_litro: float,
    peso_carga_kg: float,
    capacidad_maxima_kg: float,
    clima: str,
    peajes: float = 0.0,
    costos_extra: float = 0.0,
) -> EvaluacionRuta:
    costo_combustible, litros_estimados, factor_carga = calcular_costo_combustible(
        distancia_km=distancia_km,
        rendimiento_km_litro=rendimiento_km_litro,
        precio_combustible_litro=precio_combustible_litro,
        peso_carga_kg=peso_carga_kg,
        capacidad_maxima_kg=capacidad_maxima_kg,
        peajes=peajes,
        costos_extra=costos_extra,
    )
    autorizada, motivo = puede_salir_a_ruta(
        peso_carga_kg=peso_carga_kg,
        capacidad_maxima_kg=capacidad_maxima_kg,
        clima=clima,
    )
    return EvaluacionRuta(
        puede_salir=autorizada,
        motivo=motivo,
        costo_combustible=costo_combustible,
        litros_estimados=litros_estimados,
        factor_carga=factor_carga,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evalúa costos de combustible y viabilidad de salida para un camión de transporte."
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Solicita los datos por consola en lugar de recibirlos por argumentos.",
    )
    parser.add_argument("--distance-km", type=float, help="Distancia total de la ruta en kilómetros.")
    parser.add_argument(
        "--efficiency-km-l",
        type=float,
        help="Rendimiento del camión en kilómetros por litro.",
    )
    parser.add_argument(
        "--fuel-price",
        type=float,
        help="Precio del combustible por litro.",
    )
    parser.add_argument("--weight-kg", type=float, help="Peso actual de la carga en kilogramos.")
    parser.add_argument(
        "--max-weight-kg",
        type=float,
        help="Capacidad máxima autorizada del camión en kilogramos.",
    )
    parser.add_argument("--climate", type=str, help="Clima actual de la ruta.")
    parser.add_argument("--tolls", type=float, default=0.0, help="Costo total estimado de peajes.")
    parser.add_argument("--extra-costs", type=float, default=0.0, help="Costos operativos adicionales.")
    return parser


def formatear_reporte(evaluacion: EvaluacionRuta) -> str:
    estado = "AUTORIZADO" if evaluacion.puede_salir else "BLOQUEADO"
    return "\n".join(
        [
            "=== Evaluación de Logística de Transporte ===",
            f"Estado de salida: {estado}",
            f"Costo estimado de combustible y operación: ${evaluacion.costo_combustible:.2f}",
            f"Consumo estimado: {evaluacion.litros_estimados:.2f} L",
            f"Factor de carga aplicado: {evaluacion.factor_carga:.3f}",
            f"Detalle: {evaluacion.motivo}",
        ]
    )


def construir_opciones_desde_argumentos(args: argparse.Namespace) -> RutaOptions:
    campos_requeridos = {
        "--distance-km": args.distance_km,
        "--efficiency-km-l": args.efficiency_km_l,
        "--fuel-price": args.fuel_price,
        "--weight-kg": args.weight_kg,
        "--max-weight-kg": args.max_weight_kg,
        "--climate": args.climate,
    }
    faltantes = [nombre for nombre, valor in campos_requeridos.items() if valor is None]
    if faltantes:
        raise ValueError(f"Faltan argumentos requeridos: {', '.join(faltantes)}")

    return RutaOptions(
        distancia_km=args.distance_km,
        rendimiento_km_litro=args.efficiency_km_l,
        precio_combustible_litro=args.fuel_price,
        peso_carga_kg=args.weight_kg,
        capacidad_maxima_kg=args.max_weight_kg,
        clima=args.climate,
        peajes=args.tolls,
        costos_extra=args.extra_costs,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.interactive or (argv is None and len(sys.argv) == 1):
            options = interactive_options()
        else:
            options = construir_opciones_desde_argumentos(args)

        evaluacion = evaluar_ruta(
            distancia_km=options.distancia_km,
            rendimiento_km_litro=options.rendimiento_km_litro,
            precio_combustible_litro=options.precio_combustible_litro,
            peso_carga_kg=options.peso_carga_kg,
            capacidad_maxima_kg=options.capacidad_maxima_kg,
            clima=options.clima,
            peajes=options.peajes,
            costos_extra=options.costos_extra,
        )
    except ValueError as error:
        print(f"Error: {error}")
        return 1

    print(formatear_reporte(evaluacion))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
