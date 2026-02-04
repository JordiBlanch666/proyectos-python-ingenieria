import random

# 1. Configuración inicial
numero_secreto = random.randint(1, 50)
intentos = 0

print("--- BIENVENIDO AL JUEGO ---")
# Descomenta la línea de abajo para saber el número y probar rápido
# print(f"DEBUG: El número es {numero_secreto}")

while True:
    try:
        # 2. Pedir el número
        usuario_escribio = int(input("Adivina el número (1-50): "))
        intentos += 1

        # 3. COMPROBACIÓN
        if usuario_escribio == numero_secreto:
            print("\n========================================")
            print(f"¡LO LOGRASTE! El número era {numero_secreto}")
            print(f"Número de intentos: {intentos}")
            print("========================================")

            # 4. PAUSA DE SEGURIDAD
            input("\nPresiona ENTER para salir...")
            break

        elif usuario_escribio < numero_secreto:
            print("Pista: Es más GRANDE ↑")
        else:
            print("Pista: Es más PEQUEÑO ↓")

    except ValueError:
        print("¡Error! Solo puedes escribir números.")
