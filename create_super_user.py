import os
import django

# 1. Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prismasettings.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command

# IMPORTANTE: Reemplaza 'apps.core.models' por la ruta donde residen tus modelos si están en otra app
from apps.core.models import Carrera, Estudiante, Profesor

Usuario = get_user_model()

def ejecutar_inicializacion():
    # ----------------------------------------------------
    # 1. CREACIÓN DEL SUPERUSUARIO
    # ----------------------------------------------------
    cedula_admin = os.getenv('SUPERUSER_CEDULA', '12345678')
    username_admin = os.getenv('SUPERUSER_USERNAME', 'admin')
    first_name_admin = os.getenv('SUPERUSER_FIRST_NAME', 'Admin')
    last_name_admin = os.getenv('SUPERUSER_LAST_NAME', 'Sistema')
    email_admin = os.getenv('SUPERUSER_EMAIL', 'admin@example.com')
    password_admin = os.getenv('SUPERUSER_PASSWORD', 'admin12345')
    telefono_admin = os.getenv('SUPERUSER_TELEFONO', '04121234567')

    if not Usuario.objects.filter(cedula=cedula_admin).exists():
        print(f"Creando superusuario con cédula: {cedula_admin}...")
        Usuario.objects.create_superuser(
            cedula=cedula_admin,
            username=username_admin,
            first_name=first_name_admin,
            last_name=last_name_admin,
            email=email_admin,
            password=password_admin,
            telefono=telefono_admin
        )
        print("Superusuario creado exitosamente.")
    else:
        print(f"El superusuario con cédula '{cedula_admin}' ya existe.")

    # ----------------------------------------------------
    # 2. CREACIÓN DEL PROFESOR
    # ----------------------------------------------------
    cedula_prof = os.getenv('PROFESOR_CEDULA', '22222222')
    email_prof = os.getenv('PROFESOR_EMAIL', 'profesor@example.com')
    
    if not Usuario.objects.filter(cedula=cedula_prof).exists():
        print(f"Creando usuario Profesor con cédula: {cedula_prof}...")
        user_prof = Usuario.objects.create_user(
            cedula=cedula_prof,
            username=cedula_prof,
            first_name='Gregorio',
            last_name='Mavo',
            email=email_prof,
            telefono='04141234567'
        )
        user_prof.set_password(os.getenv('PROFESOR_PASSWORD', 'profesor12345'))
        user_prof.save()

        Profesor.objects.create(usuario=user_prof, activo=True)
        print("Profesor creado exitosamente.")
    else:
        print(f"El profesor con cédula '{cedula_prof}' ya existe.")

    # ----------------------------------------------------
    # 3. CREACIÓN DE CARRERA Y ESTUDIANTE
    # ----------------------------------------------------
    # Se asegura la existencia de una carrera para poder vincular al estudiante
    carrera_demo, _ = Carrera.objects.get_or_create(
        nombre='Ingeniería de Sistemas',
        defaults={'cantidad_semestres': 10}
    )

    cedula_est = os.getenv('ESTUDIANTE_CEDULA', '33333333')
    email_est = os.getenv('ESTUDIANTE_EMAIL', 'estudiante@example.com')

    if not Usuario.objects.filter(cedula=cedula_est).exists():
        print(f"Creando usuario Estudiante con cédula: {cedula_est}...")
        user_est = Usuario.objects.create_user(
            cedula=cedula_est,
            username=cedula_est,
            first_name='Daniel',
            last_name='Reyes',
            email=email_est,
            telefono='04161234567'
        )
        user_est.set_password(os.getenv('ESTUDIANTE_PASSWORD', 'estudiante12345'))
        user_est.save()

        Estudiante.objects.create(usuario=user_est, carrera=carrera_demo)
        print("Estudiante creado exitosamente.")
    else:
        print(f"El estudiante con cédula '{cedula_est}' ya existe.")

    # ----------------------------------------------------
    # 4. RECONSTRUIR EL ÍNDICE DE BÚSQUEDA DE HAYSTACK
    # ----------------------------------------------------
    print("Actualizando/Anexando registros al índice de búsqueda de Haystack...")
    try:
        call_command('rebuild_index', interactive=False)
        print("Índice de búsqueda reconstruido correctamente.")
    except Exception as e:
        print(f"Ocurrió un error al indexar: {e}")

if __name__ == '__main__':
    ejecutar_inicializacion()