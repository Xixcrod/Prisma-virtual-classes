from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from apps.core.models import Usuario, Estudiante, Profesor, Carrera
import secrets
import string

def admin(request):
    return render(request, "Admin/dashboard.html")

def registrar_usuario(request):
    carreras = Carrera.objects.all()
    if request.method == "POST":
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        cedula = request.POST.get('cedula')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        rol = request.POST.get('rol')

        alphabet = string.ascii_letters + string.digits
        password_plana = ''.join(secrets.choice(alphabet) for i in range(8))

        try:
            # Verificar si ya existe un usuario con esa cédula o correo antes de intentar guardar
            if Usuario.objects.filter(cedula=cedula).exists():
                messages.error(request, "Error: Ya existe un usuario registrado con esta cédula.")
                return redirect('registrar_usuario')
            
            if Usuario.objects.filter(email=correo).exists():
                messages.error(request, "Error: Ya existe un usuario registrado con este correo electrónico.")
                return redirect('registrar_usuario')

            nuevo_usuario = Usuario(
                first_name=nombres,
                last_name=apellidos,
                email=correo,
                cedula=cedula,
                telefono=telefono,
                username=cedula
            )
            nuevo_usuario.set_password(password_plana)
            nuevo_usuario.save()

            if rol == 'profesor':
                Profesor.objects.create(usuario=nuevo_usuario)
            elif rol == 'estudiante':
                carrera_id = request.POST.get('carrera')
                if carrera_id:
                    carrera_obj = Carrera.objects.get(id=carrera_id)
                    Estudiante.objects.create(usuario=nuevo_usuario, carrera=carrera_obj)

            # Envío de correo real
            asunto = 'Tus credenciales de Prisma'
            mensaje = f'Hola {nombres} {apellidos},\n\nTu cuenta ha sido creada exitosamente.\nTu contraseña es: {password_plana}'
            
            send_mail(
                asunto,
                mensaje,
                settings.EMAIL_HOST_USER,
                [correo],
                fail_silently=False,
            )

            messages.success(request, f"Usuario registrado con éxito. La contraseña ha sido enviada a {correo}")
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f"Error al registrar: {str(e)}")
            return redirect('registrar_usuario')

    return render(request, "Admin/registrar_usuario.html", {"carreras": carreras})
