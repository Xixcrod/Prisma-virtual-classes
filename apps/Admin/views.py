from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import secrets
import string

# Importaciones consolidadas de tus modelos
from apps.core.models import Usuario, Estudiante, Profesor, Carrera, Materia, Curso

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

            # Envío de correo
            asunto = 'Tus credenciales de Prisma'
            mensaje = f'Hola {nombres} {apellidos},\ntu cuenta ha sido creada exitosamente.\nTu contraseña es: {password_plana}'
            
            send_mail(
                asunto,
                mensaje,
                settings.EMAIL_HOST_USER,
                [correo],
                fail_silently=False,
            )

            messages.success(request, f"Usuario registrado con éxito. Contraseña enviada a {correo}")
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f"Error al registrar: {str(e)}")
            return redirect('registrar_usuario')

    return render(request, "Admin/registrar_usuario.html", {"carreras": carreras})

def lista_profesores(request):
    profesores = Profesor.objects.filter(activo=True) 
    return render(request, "Admin/lista_profesores.html", {'profesores': profesores})

def gestionar_materias_profesor(request, profesor_id):
    profesor_obj = get_object_or_404(Profesor, id=profesor_id)
    carreras = Carrera.objects.all()
    
    # Obtenemos las materias que ya tiene asignadas para marcarlas en el checklist
    materias_actuales = Curso.objects.filter(profesor=profesor_obj).values_list('materia_id', flat=True)

    if request.method == 'POST':
        materias_seleccionadas = request.POST.getlist('materias_ids')
        
        # Eliminamos las asignaciones anteriores para sobrescribir con las nuevas
        Curso.objects.filter(profesor=profesor_obj).delete()
        
        for m_id in materias_seleccionadas:
            materia_obj = Materia.objects.get(id=m_id)
            Curso.objects.create(
                profesor=profesor_obj,
                materia=materia_obj,
                activo=True,
                descripcion=f"Asignado el {materia_obj.nombre}" 
            )
        messages.success(request, "Asignación actualizada correctamente.")
        return redirect('lista_profesores')

    return render(request, 'Admin/asignar_materias.html', {
        'profesor': profesor_obj,
        'carreras': carreras,
        'materias_actuales': list(materias_actuales)
    })

def eliminar_profesor(request, profesor_id):
    profesor = get_object_or_404(Profesor, id=profesor_id)
    profesor.activo = False
    profesor.save()          # Guarda en la base de datos
    
    messages.warning(request, f"El profesor {profesor.usuario.first_name} ha sido desactivado.")
    return redirect('lista_profesores')

def obtener_materias_por_carrera(request, carrera_id, semestre):
    # carrera_id llegará como un UUID válido
    materias = Materia.objects.filter(
        carrera_id=carrera_id, 
        semestre=semestre
    ).values('id', 'nombre')
    
    return JsonResponse(list(materias), safe=False)