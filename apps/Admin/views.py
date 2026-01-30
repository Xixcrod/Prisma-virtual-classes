from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
import secrets
import string
from django.contrib.auth.decorators import login_required

# Importaciones consolidadas de los modelos
from apps.core.models import Usuario, Estudiante, Profesor, Carrera, Materia, Curso

@login_required
def admin(request):
    # 1. Si es Superusuario, entra al dashboard
    if request.user.is_superuser:
        return render(request, "Admin/dashboard.html")

    elif hasattr(request.user, 'profesor'):
        return redirect('adminp')
    
    if hasattr(request.user, 'estudiante'):
        return redirect('adminp')
    
    # 3. Si es alguien más, error 404
    raise Http404()

@login_required
@user_passes_test(lambda u: u.is_superuser)
def registrar_usuario(request):
    carreras = Carrera.objects.all()
    if request.method == "POST":
        # Limpiar y extraer datos
        nombres = request.POST.get('nombres', '').strip()
        apellidos = request.POST.get('apellidos', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        correo = request.POST.get('correo', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        rol = request.POST.get('rol')

        alphabet = string.ascii_letters + string.digits
        password_plana = ''.join(secrets.choice(alphabet) for i in range(8))

        from django.db import transaction

        try:
            with transaction.atomic():
                # Validaciones insensibles a mayúsculas/minúsculas y espacios
                if Usuario.objects.filter(cedula__iexact=cedula).exists():
                    messages.error(request, "Error: Ya existe un usuario registrado con esta cédula.")
                    return redirect('registrar_usuario')
                
                if Usuario.objects.filter(email__iexact=correo).exists():
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

                # Envío de correo (dentro de la transacción)
                # Si falla el correo, la transacción se revierte y no se crea el usuario
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

@login_required
@user_passes_test(lambda u: u.is_superuser)
def lista_profesores(request):
    profesores = Profesor.objects.filter(activo=True) 
    carreras = Carrera.objects.all()
    
    # Se crea un diccionario con las materias de cada profesor para enviarlo al JS
    asignaciones = {}
    for p in profesores:
        materias_ids = list(Curso.objects.filter(profesor=p).values_list('materia_id', flat=True))
        # Convertir UUIDs a strings para el JSON
        asignaciones[str(p.id)] = [str(m_id) for m_id in materias_ids]

    return render(request, "Admin/lista_profesores.html", {
        'profesores': profesores, 
        'carreras': carreras,
        'asignaciones_json': asignaciones
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def gestionar_materias_profesor(request, profesor_id):
    profesor_obj = get_object_or_404(Profesor, id=profesor_id)
    carreras = Carrera.objects.all()
    
    # Se obtienen las materias que ya tiene asignadas para marcarlas en el checklist
    materias_actuales = Curso.objects.filter(profesor=profesor_obj).values_list('materia_id', flat=True)

    if request.method == 'POST':
        materias_seleccionadas = request.POST.getlist('materias_ids')
        carrera_id = request.POST.get('carrera_id')
        semestre = request.POST.get('semestre')
        
        # Si vienen carrera y semestre, solo se borra lo de ese bloque para no borrar todo
        if carrera_id and semestre:
            Curso.objects.filter(
                profesor=profesor_obj,
                materia__carrera_id=carrera_id,
                materia__semestre=semestre
            ).delete()
        else:
            # Comportamiento anterior por si acaso
            Curso.objects.filter(profesor=profesor_obj).delete()
        
        for m_id in materias_seleccionadas:
            materia_obj = Materia.objects.get(id=m_id)
            Curso.objects.create(
                profesor=profesor_obj,
                materia=materia_obj,
                activo=True,
                descripcion=f"Asignado el {materia_obj.nombre}" 
            )
        messages.success(request, "Asignación actualizada correctamente")
        return redirect('lista_profesores')

    return render(request, 'Admin/asignar_materias.html', {
        'profesor': profesor_obj,
        'carreras': carreras,
        'materias_actuales': list(materias_actuales)
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_profesor(request, profesor_id):
    profesor = get_object_or_404(Profesor, id=profesor_id)
    profesor.activo = False
    profesor.save() # Guarda en la base de datos
    
    messages.warning(request, f"El profesor {profesor.usuario.first_name} ha sido desactivado.")
    return redirect('lista_profesores')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def registrar_carrera_materia(request):
    carreras = Carrera.objects.all().order_by('nombre') # Obtiene todas las carreras ordenadas A-Z
    materias = Materia.objects.all().select_related('carrera').order_by('carrera__nombre', 'semestre', 'nombre')

    if request.method == "POST":  # Verificación método POST (formulario enviado)
        print("DEBUG POST:", request.POST) # Esto imprimirá los datos en la consola para verificar
        action = request.POST.get('action')
        
        # Registrar Carrera
        if action == 'crear_carrera':
            nombre = request.POST.get('nombre', '').strip()
            cantidad_semestres = request.POST.get('cantidad_semestres', 10)
            if not nombre:  # Validación: Campos obligatorios
                messages.error(request, "El nombre de la carrera es obligatorio.")
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
        elif action == 'crear_materia':
            nombre = request.POST.get('nombre', '').strip()
            semestre = request.POST.get('semestre', 1)
            carrera_id = request.POST.get('carrera')
            
            if not carrera_id:
                messages.error(request, "Debe seleccionar una carrera.")
            elif not nombre:
                messages.error(request, "El nombre de la materia es obligatorio.")
            elif not semestre:
                messages.error(request, "El semestre es obligatorio.")
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
        materias_carrera = Materia.objects.filter(carrera=carrera).order_by('semestre', 'nombre')
        # Diccionario para agrupar materias por semestre
        semestres_dict = {}
        for materia in materias_carrera:
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
        "materias": materias,
        "carreras_data": carreras_data
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
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
    # Si es GET, redirigimos a la página principal 
    return redirect('registrar_carrera_materia')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def editar_materia(request, materia_id):
     # Busca materia por ID
    materia = get_object_or_404(Materia, id=materia_id)
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
            return redirect('registrar_carrera_materia')

    # Si es GET, redirigimos a la página principal
    return redirect('registrar_carrera_materia')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_materia(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    materia.delete()
    messages.success(request, "Materia eliminada correctamente.")
    return redirect('registrar_carrera_materia')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_carrera(request, carrera_id):
    carrera = get_object_or_404(Carrera, id=carrera_id)
    carrera.delete()
    messages.success(request, "Carrera eliminada correctamente.")
    return redirect('registrar_carrera_materia')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def obtener_materias_por_carrera(request, carrera_id, semestre):
    # carrera_id llegará como un UUID válido
    materias = Materia.objects.filter(
        carrera_id=carrera_id, 
        semestre=semestre
    ).values('id', 'nombre')
    
    return JsonResponse(list(materias), safe=False)

# Función para eliminar curso recibiendo su id
@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    curso.activo = False
    curso.save()
    
    messages.warning(request, f"El curso {curso.materia.nombre} ha sido desactivado correctamente.")
#   return redirect('catalogo')