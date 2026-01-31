import uuid
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, HttpResponse
from django.core.exceptions import PermissionDenied
from django.views import View
from apps.core.utils.context_processors import roles_usuario
from apps.core.models import Acceso, Curso, Estudiante

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from haystack.query import SearchQuerySet
from .forms import CatalogoSearchForm

# Create your views here.
def inicio(request):
    return HttpResponse("Inicio estudiantes")


# Clase para crear solicitudes para acceder al contenido de un curso
class CreateAccessRequest(View):
    def post(self, request, curso_id, *args, **kwargs):
        # Función de Díaz.
        rol_usuario = roles_usuario(request)
        # Evaluación de que quien acceda ala función sea en verdad un estudiante.
        if not rol_usuario.get("es_estudiante", False):
            raise PermissionDenied(
                "Autententicación de usuario no válida."
            )  # WARNING: Forzado del error 403 (Forbidden) en caso de no ser estudiante.
        try:
            # Chequeo del formato del UUID.
            if not isinstance(curso_id, uuid.UUID):
                curso_id = uuid.UUID(curso_id)
        except ValueError:
            return HttpResponseBadRequest(
                "Formato de ID inválido"
            )  # WARNING: Forzado del error 400 (Bad Request) si el UUID es inválido.
        # Búsqueda del curso a solicitar su acceso.
        curso = get_object_or_404(
            Curso, id=curso_id
        )  # WARNING: Forzado error 404 (Not Found) si no se encuentra.
        #  Creación del acceso solo si no existía previamente.
        acceso, creado = Acceso.objects.get_or_create(
            estudiante=request.user.estudiante,
            curso=curso,
            defaults={"estado": "PE"},
        )
        # Mensajes de estado.
        if creado:
            messages.success(
                request,
                f"La solicitud de acceso al curso {curso.materia.nombre} del profesor {curso.profesor.usuario.first_name} {curso.profesor.usuario.last_name} ha sido enviada exitosamente.",
            )
        else:
            messages.info(request, "Ya tienes una solicitud en curso...")
        return redirect("detalles-cursos", id_curso=curso.id)

# Vista del catálogo de cursos
@login_required
def catalogo_cursos(request):
    """
    Vista principal del catálogo de cursos.
    Muestra cursos filtrados y permite búsqueda con Haystack/Whoosh.
    - Estudiantes: solo cursos de su carrera
    - Administradores: todos los cursos
    """
    # Verificar si el usuario es administrador
    es_admin = request.user.is_superuser or request.user.is_staff
    
    # Si es admin, puede ver todo sin necesidad de ser estudiante
    if es_admin:
        estudiante = None
        carrera_filtro = None
    else:
        # Verificar que el usuario sea un estudiante
        try:
            estudiante = Estudiante.objects.select_related(
                'usuario', 'carrera'
            ).get(usuario=request.user)
            carrera_filtro = estudiante.carrera.nombre
        except Estudiante.DoesNotExist:
            messages.error(request, 'Solo los estudiantes pueden acceder al catálogo de cursos.')
            return redirect('core:dashboard')

    # Crear el formulario de búsqueda
    form = CatalogoSearchForm(
        request.GET or None,
        estudiante=estudiante,
        searchqueryset=SearchQuerySet().models(Curso)
    )

    # Ejecutar búsqueda
    resultados = form.search()

    # Filtrar por carrera solo si NO es admin
    if not es_admin and carrera_filtro:
        resultados = resultados.filter(carrera_nombre=carrera_filtro)

    # Convertir resultados a lista de objetos Curso con información adicional
    cursos_data = []
    for result in resultados:
        curso = result.object
        
        cursos_data.append({
            'curso': curso,
            'es_admin': es_admin,  # Nuevo campo para el template
        })

    # Paginación
    paginator = Paginator(cursos_data, 8)  # 8 cursos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        'form': form,
        'page_obj': page_obj,
        'estudiante': estudiante,
        'es_admin': es_admin,
        'query': request.GET.get('q', ''),
    }

    return render(request, 'catalogo_cursos.html', context)