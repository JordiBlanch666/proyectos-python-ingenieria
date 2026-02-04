#Genera una contraseña alfanumérica de diez caracteres
# con al menos un carácter en minúscula, al menos un carácter en mayúscula y al menos tres dígitos:
import string
import secrets
alphabet = string.ascii_letters + string.digits
while True:
    password = ''.join(secrets.choice(alphabet) for i in range(10))
    if (any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3):
        break

print(f"Tu nueva contraseña segura es: {password}")