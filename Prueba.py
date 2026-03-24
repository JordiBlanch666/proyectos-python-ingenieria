import csv
from contextlib import closing
import json
import sqlite3
import unicodedata
from pathlib import Path
from statistics import mean


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
AEROLINEAS_CSV = DATA_DIR / "aerolineas.csv"
AEROLINEAS_JSON = DATA_DIR / "aerolineas.json"
HOSPEDAJE_CSV = DATA_DIR / "hospedaje.csv"
HOSPEDAJE_DB = DATA_DIR / "hospedaje.db"

SEMILLA_HOSPEDAJE_DB = [
    ("París", "Seine Palace", 150.0),
    ("París", "Left Bank Hotel", 160.0),
    ("Roma", "Vaticano Suites", 118.0),
    ("Roma", "Piazza Navona Stay", 122.0),
    ("Madrid", "Puerta del Sol Rooms", 98.0),
    ("Madrid", "Castellana House", 102.0),
    ("Tokio", "Asakusa Comfort", 168.0),
    ("Tokio", "Ginza Urban Hotel", 172.0),
]


class Destino:
    def __init__(self, nombre, promedio_vuelo, promedio_hospedaje, aerolineas, proveedores, fuentes):
        self.nombre = nombre
        self.promedio_vuelo = promedio_vuelo
        self.promedio_hospedaje = promedio_hospedaje
        self.aerolineas = aerolineas
        self.proveedores = proveedores
        self.fuentes = fuentes


class Viaje:
    def __init__(self, origen, destino, dias, otros_costos):
        self.origen = origen
        self.destino = destino
        self.dias = dias
        self.otros_costos = otros_costos

    def calcular_costo_vuelo(self):
        return self.destino.promedio_vuelo

    def calcular_costo_hospedaje(self):
        return self.destino.promedio_hospedaje * self.dias

    def calcular_costo_total(self):
        return self.calcular_costo_vuelo() + self.calcular_costo_hospedaje() + self.otros_costos


def normalizar_texto(texto):
    texto = unicodedata.normalize("NFD", texto.strip())
    texto = "".join(caracter for caracter in texto if unicodedata.category(caracter) != "Mn")
    return texto.casefold()


def asegurar_base_hospedaje(ruta_db):
    ruta_db.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(ruta_db)) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS hospedaje (
                destino TEXT NOT NULL,
                proveedor TEXT NOT NULL,
                precio_noche REAL NOT NULL
            )
            """
        )
        cursor.execute("SELECT COUNT(*) FROM hospedaje")
        cantidad_registros = cursor.fetchone()[0]
        if cantidad_registros == 0:
            cursor.executemany(
                "INSERT INTO hospedaje (destino, proveedor, precio_noche) VALUES (?, ?, ?)",
                SEMILLA_HOSPEDAJE_DB,
            )
        conexion.commit()


def cargar_aerolineas_csv(ruta_csv):
    ofertas = []
    with ruta_csv.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            precio = float(fila["precio"])
            ofertas.append(
                {
                    "origen": fila["origen"].strip(),
                    "destino": fila["destino"].strip(),
                    "aerolinea": fila["aerolinea"].strip(),
                    "precio": precio,
                    "fuente": ruta_csv.name,
                }
            )
    return ofertas


def cargar_aerolineas_json(ruta_json):
    ofertas = []
    with ruta_json.open(encoding="utf-8") as archivo:
        datos = json.load(archivo)
    for fila in datos:
        ofertas.append(
            {
                "origen": fila["origen"].strip(),
                "destino": fila["destino"].strip(),
                "aerolinea": fila["aerolinea"].strip(),
                "precio": float(fila["precio"]),
                "fuente": ruta_json.name,
            }
        )
    return ofertas


def cargar_hospedaje_csv(ruta_csv):
    registros = []
    with ruta_csv.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            registros.append(
                {
                    "destino": fila["destino"].strip(),
                    "proveedor": fila["proveedor"].strip(),
                    "precio_noche": float(fila["precio_noche"]),
                    "fuente": ruta_csv.name,
                }
            )
    return registros


def cargar_hospedaje_sqlite(ruta_db):
    asegurar_base_hospedaje(ruta_db)
    registros = []
    with closing(sqlite3.connect(ruta_db)) as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT destino, proveedor, precio_noche FROM hospedaje")
        for destino, proveedor, precio_noche in cursor.fetchall():
            registros.append(
                {
                    "destino": destino.strip(),
                    "proveedor": proveedor.strip(),
                    "precio_noche": float(precio_noche),
                    "fuente": ruta_db.name,
                }
            )
    return registros


def cargar_fuentes():
    ofertas_vuelo = cargar_aerolineas_csv(AEROLINEAS_CSV) + cargar_aerolineas_json(AEROLINEAS_JSON)
    registros_hospedaje = cargar_hospedaje_csv(HOSPEDAJE_CSV) + cargar_hospedaje_sqlite(HOSPEDAJE_DB)
    return ofertas_vuelo, registros_hospedaje


def construir_catalogo_viajes():
    ofertas_vuelo, registros_hospedaje = cargar_fuentes()

    rutas = {}
    for oferta in ofertas_vuelo:
        clave = (normalizar_texto(oferta["origen"]), normalizar_texto(oferta["destino"]))
        ruta = rutas.setdefault(
            clave,
            {
                "origen": oferta["origen"],
                "destino": oferta["destino"],
                "precios": [],
                "aerolineas": set(),
                "fuentes": set(),
            },
        )
        ruta["precios"].append(oferta["precio"])
        ruta["aerolineas"].add(oferta["aerolinea"])
        ruta["fuentes"].add(oferta["fuente"])

    hospedajes = {}
    for registro in registros_hospedaje:
        clave = normalizar_texto(registro["destino"])
        hospedaje = hospedajes.setdefault(
            clave,
            {
                "destino": registro["destino"],
                "precios": [],
                "proveedores": set(),
                "fuentes": set(),
            },
        )
        hospedaje["precios"].append(registro["precio_noche"])
        hospedaje["proveedores"].add(registro["proveedor"])
        hospedaje["fuentes"].add(registro["fuente"])

    catalogo = {}
    for (clave_origen, clave_destino), ruta in rutas.items():
        if clave_destino not in hospedajes:
            continue

        hospedaje = hospedajes[clave_destino]
        destino = Destino(
            nombre=ruta["destino"],
            promedio_vuelo=mean(ruta["precios"]),
            promedio_hospedaje=mean(hospedaje["precios"]),
            aerolineas=sorted(ruta["aerolineas"]),
            proveedores=sorted(hospedaje["proveedores"]),
            fuentes=sorted(ruta["fuentes"] | hospedaje["fuentes"]),
        )

        origen = catalogo.setdefault(clave_origen, {"nombre": ruta["origen"], "destinos": []})
        origen["destinos"].append(destino)

    for origen in catalogo.values():
        origen["destinos"].sort(key=lambda destino: destino.nombre)

    return dict(sorted(catalogo.items(), key=lambda item: item[1]["nombre"]))


def pedir_numero(mensaje):
    while True:
        entrada = input(mensaje).strip().replace(",", ".")
        try:
            valor = float(entrada)
            if valor >= 0:
                return valor
            print("El valor no puede ser negativo.")
        except ValueError:
            print("Ingresa un número válido.")


def pedir_entero_positivo(mensaje):
    while True:
        entrada = input(mensaje).strip()
        try:
            valor = int(entrada)
            if valor > 0:
                return valor
            print("El número debe ser mayor que cero.")
        except ValueError:
            print("Ingresa un número entero válido.")


def elegir_origen(catalogo):
    origenes = list(catalogo.values())
    print("\nOrígenes disponibles según las fuentes cargadas:")
    for indice, origen in enumerate(origenes, start=1):
        print(f"{indice}. {origen['nombre']}")

    while True:
        opcion = input("Elige el número del origen: ").strip()
        try:
            indice = int(opcion)
            if 1 <= indice <= len(origenes):
                return origenes[indice - 1]
            print("Selecciona una opción dentro de la lista.")
        except ValueError:
            print("Ingresa un número válido.")


def elegir_destino(destinos):
    print("\nDestinos disponibles con costos promedio calculados:")
    for indice, destino in enumerate(destinos, start=1):
        print(
            f"{indice}. {destino.nombre} - vuelo promedio {destino.promedio_vuelo:.2f} euros - "
            f"hospedaje promedio {destino.promedio_hospedaje:.2f} euros/noche"
        )

    while True:
        opcion = input("Elige el número del destino: ").strip()
        try:
            indice = int(opcion)
            if 1 <= indice <= len(destinos):
                return destinos[indice - 1]
            print("Selecciona una opción dentro de la lista.")
        except ValueError:
            print("Ingresa un número válido.")


def mostrar_resumen(viaje):
    print("\n=== Resumen del viaje ===")
    print(f"Origen: {viaje.origen}")
    print(f"Destino: {viaje.destino.nombre}")
    print(f"Días: {viaje.dias}")
    print(f"Vuelo promedio: {viaje.calcular_costo_vuelo():.2f} euros")
    print(f"Hospedaje promedio por noche: {viaje.destino.promedio_hospedaje:.2f} euros")
    print(f"Costo total de hospedaje: {viaje.calcular_costo_hospedaje():.2f} euros")
    print(f"Otros costos: {viaje.otros_costos:.2f} euros")
    print(f"Costo total estimado: {viaje.calcular_costo_total():.2f} euros")
    print(f"Aerolíneas consideradas: {', '.join(viaje.destino.aerolineas)}")
    print(f"Hospedajes considerados: {', '.join(viaje.destino.proveedores)}")
    print(f"Fuentes consultadas: {', '.join(viaje.destino.fuentes)}")


def main():
    try:
        catalogo = construir_catalogo_viajes()
    except FileNotFoundError as error:
        print(f"No se encontró una fuente de datos necesaria: {error}")
        return
    except (ValueError, KeyError, json.JSONDecodeError, sqlite3.DatabaseError) as error:
        print(f"No fue posible cargar las fuentes de datos: {error}")
        return

    if not catalogo:
        print("No hay datos suficientes para calcular promedios de viaje.")
        return

    print("=== Planificador de viajes con costos promedio ===")
    print("El sistema usa datos de archivos CSV, JSON y una base SQLite local.")

    origen = elegir_origen(catalogo)
    destino = elegir_destino(origen["destinos"])
    dias = pedir_entero_positivo("¿Cuántos días durará el viaje?: ")
    otros_costos = pedir_numero("Ingresa otros costos adicionales: ")

    viaje = Viaje(origen["nombre"], destino, dias, otros_costos)
    mostrar_resumen(viaje)


if __name__ == "__main__":
    main()
