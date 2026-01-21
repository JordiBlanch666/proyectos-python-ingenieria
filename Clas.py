print ("===================Bienvenid@ a la calculadora Blanch de IMC=====================")
peso = input ("Ingresa tu peso en kilogramos: ")
estatura = input ("Ingresa tu estatura en metros: ")

peso_num = float (peso)
estatura_num = float(estatura)

imc = peso_num / (estatura_num**2)
print ("tu IMC es", imc)