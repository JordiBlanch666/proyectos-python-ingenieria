print ("===================Bienvenid@ a la calculadora Blanch de IMC=====================")

try:
    peso = input("Ingresa tu peso en kilogramos: ")
    estatura = input("Ingresa tu estatura en metros: ")

    # Usamos tus variables de conversión
    peso_num = float(peso)
    estatura_num = float(estatura)

    imc = peso_num / (estatura_num**2)

    # Mejoramos el print para que se vea limpio (usando f-string y .2f)
    print(f"\nTu IMC es: {imc:.2f}")

    # Agregamos la lógica de salud
    if imc < 18.5:
        print("Resultado: Bajo peso")
    elif 18.5 <= imc < 25:
        print("Resultado: Peso saludable (¡Felicidades!)")
    elif 25 <= imc < 30:
        print("Resultado: Sobrepeso")
    else:
        print("Resultado: Obesidad")

except ValueError:
    print("¡Error! Por favor usa números y usa punto (.) para los decimales.")

print("=================================================================================")