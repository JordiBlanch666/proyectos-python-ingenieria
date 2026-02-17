# --- BLOQUE DE FUNCIONES ---

def calcular_transporte(distancia):
    costo = distancia * 5
    return costo

def calcular_comida(dias, presupuesto_diario=500): # El 500 es el valor por defecto
    costo = dias * presupuesto_diario
    return costo

def mostrar_resumen(destino, costo_transporte, costo_comida):
    total = costo_transporte + costo_comida
    resumen = f"--- Resumen de Viaje a {destino} ---\n"
    resumen += f"Transporte: ${costo_transporte}\n"
    resumen += f"Comida: ${costo_comida}\n"
    resumen += f"COSTO TOTAL: ${total}"
    return resumen
# --- CAPTURA DE DATOS ---

destino = input("¿A qué ciudad viajas?: ")
distancia_km = float(input("¿Cuántos kilómetros hay de distancia?: "))
dias_viaje = int(input("¿Cuántos días estarás allá?: "))
# --- EJECUCIÓN ---

# Calculamos usando nuestras funciones
gasto_transporte = calcular_transporte(distancia_km)
gasto_comida = calcular_comida(dias_viaje) # Aquí usará los 500 por defecto

# Generamos el mensaje final
mensaje_final = mostrar_resumen(destino, gasto_transporte, gasto_comida)

# ¡Mostramos el resultado!
print(mensaje_final)