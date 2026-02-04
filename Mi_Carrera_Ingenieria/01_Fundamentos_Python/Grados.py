#1er paso se solicita al user ingresar la temperatura en grado Celsius
Celsius = float(input("ingresa la temperatura en grados Celcius: "))

#2nda etapa convertir a Farenheit utilizando fórmula F = (C *9/5) + 32
Fahrenheit = (Celsius * 9/5) + 32

#3era etapa se determina si hace calor (>= 86°F)
hace_calor = Fahrenheit >= 86

#4a etapa mostrar resultados
print(f"Temperatura en Fahrenheit: {Fahrenheit:.1f}°F")
print(f"¿Hace calor?: {hace_calor}")