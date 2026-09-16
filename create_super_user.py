import os
import django

# 1. Configurar el entorno de Django (reemplaza 'tu_proyecto.settings' con el nombre de tu proyecto)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prismasettings.settings')
django.setup()

from django.contrib.auth import get_user_model

Usuario = get_user_model()

def crear_superusuario_inicial():
    # Datos requeridos por tu modelo personalizado
    cedula = os.getenv('SUPERUSER_CEDULA', '12345678')
    username = os.getenv('SUPERUSER_USERNAME', 'admin')
    first_name = os.getenv('SUPERUSER_FIRST_NAME', 'Admin')
    last_name = os.getenv('SUPERUSER_LAST_NAME', 'Sistema')
    email = os.getenv('SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('SUPERUSER_PASSWORD', 'admin12345')
    telefono = os.getenv('SUPERUSER_TELEFONO', '04121234567')

    # Verificar existencia utilizando el USERNAME_FIELD ('cedula')
    if not Usuario.objects.filter(cedula=cedula).exists():
        print(f"Creando superusuario con cédula: {cedula}...")
        
        Usuario.objects.create_superuser(
            cedula=cedula,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            telefono=telefono
        )
        print("Superusuario creado exitosamente.")
    else:
        print(f"El superusuario con cédula '{cedula}' ya existe en el sistema.")

if __name__ == '__main__':
    crear_superusuario_inicial()