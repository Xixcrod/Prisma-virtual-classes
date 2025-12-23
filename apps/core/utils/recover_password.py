
from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from ..models import Usuario  # Asegúrate de importar tu modelo Usuario


def recovering_password(request):
    """
    Recupera la contraseña verificando cédula y email.
    Args:
        username: Corresponde a la 'cedula' del usuario.
        email: El correo electrónico del usuario.
    """
    if request.method == 'POST':
        # Obtenemos los datos. 
        cedula_input = request.POST.get('username')
        email_input = request.POST.get('email')
    
    try:

        # 1. Buscamos al usuario que coincida con la cédula Y el email
        user = Usuario.objects.get(cedula=cedula_input, email=email_input)

        # 2. Generar una contraseña aleatoria (10 caracteres)
        new_password = get_random_string(length=10)

        # 3. Guardar la nueva contraseña encriptada (Hash)
        user.set_password(new_password)
        user.save()

        # 4. Enviar el correo electrónico
        asunto = 'Recuperación de Contraseña'
        mensaje = f'Hola {user.first_name}, tu contraseña ha sido restablecida. Tu nueva contraseña es: {new_password}'
        email_origen = settings.DEFAULT_FROM_EMAIL
        
        send_mail(
            asunto,
            mensaje,
            email_origen,
            [email_input],
            fail_silently=False, # Esto avisará si falla el envío de correo
        )

        # 5. Redireccionar con Success = True
        return render(request, 'login.html', {'success': True})

    except Usuario.DoesNotExist:
        # 6. Si no coinciden o no existe, redirigir con el mensaje de error
        return render(request, 'login.html', {'error': 'El usuario proporcionado no existe, por favor solicite su permiso de registro'})

    except Exception as e:
        return render(request, 'login.html', {'error': f'Ocurrio un error inesperado: {str(e)}'})