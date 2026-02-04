import requests
from bs4 import BeautifulSoup

# 1. URL de Wikipedia
url = "https://es.wikipedia.org/wiki/Python"

# 2. El "User-Agent" engaña al sitio para que piense que somos un humano navegando
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 3. Enviamos la petición con los headers
response = requests.get(url, headers=headers)

# 4. Procesamos el contenido
soup = BeautifulSoup(response.content, "html.parser")

# 5. Buscamos el h1
resultado = soup.find('h1')

# 6. Validación profesional
if resultado is not None:
    titulo = resultado.text.strip()
    print(f"✅ ¡ÉXITO! El título encontrado es: {titulo}")
else:
    # Mensaje de seguridad en caso de que la estructura de la web haya cambiado
    print("❌ Wikipedia bloqueó la conexión o cambió su estructura.")