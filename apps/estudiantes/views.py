import uuid
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, HttpResponse
from django.core.exceptions import PermissionDenied
from django.views import View
from apps.core.utils.context_processors import roles_usuario
from apps.core.models import Acceso, Curso, Estudiante


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
