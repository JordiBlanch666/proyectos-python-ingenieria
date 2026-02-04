#Titulo
nombre = input ("¿Como se llama la receta?: ")
#INGREDIENTES
ingredientes = []
print ("Escribe los ingredientes uno por uno. Escriba 'fin' para finalizar ")
while True:
    item = input("> ")
    if item.lower() == "fin": #por si escriben FIN"
        break
    ingredientes.append(item)
    #PASOS (3)
pasos = []
print("\nAhora los 3 pasos de preparación:")
for i in range (1, 4):
    action =input(f"Paso {i}: ")
    pasos.append(action)
        #RESULTADO
print(f"\n---LISTO PAR COCINAR {nombre.upper()}---")
print(f"Necesitas {len(ingredientes)} ingredientes:") #len () #Cuenta cuantos son
for ing in ingredientes:
    print(f"• {ing}")
print("\nInstrucciones:")
for i, p in enumerate(pasos, 1): #ENUMERATE ASISTE A COLOCAR EL NÚMERO AUTOMATICAMENTE
   print(f"{i}. {p}")

