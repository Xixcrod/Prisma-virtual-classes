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

def registrar_carrera_materia(request):
    carreras = Carrera.objects.all().order_by('nombre') # Obtiene todas las carreras ordenadas A-Z
    if request.method == "POST":  # VERIFICACIÓN MÉTODO POST (formulario enviado)
        print("DEBUG POST:", request.POST) # Esto imprimirá los datos en tu consola para verificar
        action = request.POST.get('action')
        
        # Registrar Carrera
        if action == 'registrar_carrera':
            nombre = request.POST.get('nombre', '').strip()
            cantidad_semestres = request.POST.get('cantidad_semestres')
            if not nombre or not cantidad_semestres:  # VALIDACIÓN: Campos obligatorios
                messages.error(request, "El nombre y la cantidad de semestres son obligatorios.")
            else:
                try:
                    if Carrera.objects.filter(nombre__iexact=nombre).exists():
                        messages.error(request, "Error: Ya existe una carrera con este nombre.")
                    else:
                        # Crea la nueva carrera
                        Carrera.objects.create(nombre=nombre, cantidad_semestres=int(cantidad_semestres))
                        messages.success(request, "Carrera registrada con éxito.")
                        return redirect('registrar_carrera_materia') # Recarga página
                except Exception as e:
                    messages.error(request, f"Error al registrar carrera: {str(e)}")
        
        # Registrar Materia
        elif action == 'registrar_materia':
            nombre = request.POST.get('nombre', '').strip()
            semestre = request.POST.get('semestre')
            carrera_id = request.POST.get('carrera')
            
            if not nombre or not semestre or not carrera_id:
                messages.error(request, "Todos los campos son obligatorios para registrar una materia.")
            else:
                try:
                     # Obtiene objeto Carrera desde el ID
                    carrera_obj = Carrera.objects.get(id=carrera_id)
                    # Validación: Materia única por carrera
                    if Materia.objects.filter(nombre__iexact=nombre, carrera=carrera_obj).exists():
                        messages.error(request, "Error: Ya existe una materia con este nombre en la carrera seleccionada.")
                    else:
                        Materia.objects.create(
                            nombre=nombre,
                            semestre=int(semestre),
                            carrera=carrera_obj
                        )
                        messages.success(request, "Materia registrada con éxito.")
                        return redirect('registrar_carrera_materia')
                except Exception as e:
                    messages.error(request, f"Error al registrar materia: {str(e)}")

    # Preparar datos para el listado (Carreras -> Semestres -> Materias)
    carreras_data = []
    for carrera in carreras:
         # Obtiene todas las materias de esta carrera, ordenadas por semestre y nombre
        materias = Materia.objects.filter(carrera=carrera).order_by('semestre', 'nombre')
        # Diccionario para agrupar materias por semestre
        semestres_dict = {}
        for materia in materias:
            sem = materia.semestre
            # Si el semestre no existe en el diccionario, crea lista vacía
            if sem not in semestres_dict:
                semestres_dict[sem] = []
            semestres_dict[sem].append(materia) # Agrega materia a la lista de su semestre

         # Ordena semestres de menor a mayor (1, 2, 3...)
        sorted_semestres = dict(sorted(semestres_dict.items()))
        
        # Agrega datos organizados de esta carrera a la lista final
        carreras_data.append({
            'info': carrera,
            'semestres': sorted_semestres # Materias agrupadas por semestre
        })

# Renderiza template con datos organizados
    return render(request, "Admin/registrar_carrera_materia.html", {
        "carreras": carreras,
        "carreras_data": carreras_data
    })

def editar_carrera(request, carrera_id):
     # Busca carrera por ID, si no existe error 404
    carrera = get_object_or_404(Carrera, id=carrera_id)
    if request.method == "POST":
         # Actualiza los campos con datos del formulario
        carrera.nombre = request.POST.get('nombre')
        carrera.cantidad_semestres = int(request.POST.get('cantidad_semestres'))
        carrera.save()
        messages.success(request, "Carrera actualizada correctamente.")
        return redirect('registrar_carrera_materia')
     # Si es GET, muestra formulario con datos actuales
    return render(request, "Admin/editar_carrera.html", {"carrera": carrera})

def editar_materia(request, materia_id):
     # Busca materia por ID
    materia = get_object_or_404(Materia, id=materia_id)
    carreras = Carrera.objects.all()
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        semestre = request.POST.get('semestre')
        carrera_id = request.POST.get('carrera')
        
        try:
            # Obtiene nueva carrera seleccionada
            carrera_obj = Carrera.objects.get(id=carrera_id)
            # VALIDACIÓN: Verifica que no exista otra materia con el mismo nombre en la misma carrera
            if Materia.objects.filter(nombre=nombre, carrera=carrera_obj).exclude(id=materia_id).exists():
                messages.error(request, "Error: Ya existe una materia con este nombre en la carrera seleccionada.")
            else:
                # Actualiza datos de la materia
                materia.nombre = nombre
                materia.semestre = semestre
                materia.carrera = carrera_obj
                materia.save()
                messages.success(request, "Materia actualizada correctamente.")
                return redirect('registrar_carrera_materia')
        except Exception as e:
            messages.error(request, f"Error al actualizar materia: {str(e)}")

      # Si es GET, muestra formulario con datos actuales       
    return render(request, "Admin/editar_materia.html", {"materia": materia, "carreras": carreras})

def eliminar_materia(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    materia.delete()
    messages.success(request, "Materia eliminada correctamente.")
    return redirect('registrar_carrera_materia')

def eliminar_carrera(request, carrera_id):
    carrera = get_object_or_404(Carrera, id=carrera_id)
    carrera.delete() # Elimina la materia de la base de datos
    messages.success(request, "Carrera eliminada correctamente.")
    return redirect('registrar_carrera_materia')

def obtener_materias_por_carrera(request, carrera_id, semestre):
    # carrera_id llegará como un UUID válido
    materias = Materia.objects.filter(
        carrera_id=carrera_id, 
        semestre=semestre
    ).values('id', 'nombre')
    
    return JsonResponse(list(materias), safe=False)