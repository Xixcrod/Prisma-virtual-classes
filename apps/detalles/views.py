from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import FileResponse, Http404, HttpResponse
from django.views.generic import DetailView, UpdateView
from django.views.generic.detail import BaseDetailView
from apps.core.models import Curso, Tema, Video, Usuario, Profesor, Acceso
from .mixins import AuthorizationsMixin, ConfigAccessToMediaFilesMixin
from django.conf import settings
from apps.core.utils.context_processors import (
    roles_usuario,
)  # Importación de la función de Díaz para gestionar los roles de usuario
from .forms import UpdateCoursesImageForm
import mimetypes

# INFO: Clases para las vistas de detalles de Cursos, Temas y Vídeos.


# NOTE: Falta agregar el LoginRequiredMixin para garantizar el acceso solo de usuarios autenticados.


#   Vista para detalles de los cursos.
class CoursesDetails(AuthorizationsMixin, DetailView):
    # Modelo desde donde pertenece el objeto a detallar.
    model = Curso

    # El template a donde se enviará la información.
    template_name = "detalles-cursos.html"

    # De dónde se pretende recibir el parámetro de la uuid desde la url.
    pk_url_kwarg = "id_curso"
    context_object_name = "curso"

    # Determinación de los contextos para el template, agergando los temas del curso y evaluando los acceso para los estudiantes.
    def get_context_data(self, **kwargs):
        # El curso (objeto) obtenido por la ejecución de la clase.
        curso = self.object
        # Función de Díaz para roles.
        roles = roles_usuario(self.request)
        # Llamada a método padre de obtención de contextos para opbtener los contextos base.
        context = super().get_context_data(**kwargs)
        # context["url_retorno"] = reverse("dashboard")   #TEST: Meramente de prueba, esto se debe cambiar una vez culminada la sección de catálogo.

        # Si se trata de un estudiante sin acceso a ese curso, entonces no retornará en el contexto la información de los temas.
        if roles["es_estudiante"]:
            # Obtención del acceso correspondiente.
            acceso = Acceso.objects.filter(
                curso=self.object, estudiante=self.request.user.estudiante
            ).first()
            # Verificación de la existencia y aprobación del acceso
            if not acceso or acceso.estado != "AP":
                context["tiene_acceso"] = False
                # Envío del estado actual del acceso.
                context["estado_acceso"] = acceso.estado if acceso else None
                return context
        # Si se trata de un profesor, se contará la cantidad de estudiantes inscritos en el curso.
        if roles["es_profesor"]:
            context["cantidad_estudiantes"] = Acceso.objects.filter(
                curso=curso, estado="AP"
            ).count()
        # Agragación al contexto el nuevo campo para los temas del curso.
        context["temas"] = Tema.objects.filter(curso=curso)
        context["tiene_acceso"] = True
        context["form_img_curso"] = UpdateCoursesImageForm(instance=self.object)
        # Retorno del contexto junto con los temas del curso.
        return context


# Vista para detalles de los temas.
class ThemesDetails(AuthorizationsMixin, DetailView):
    # Modelo desde donde pertenece el objeto a detallar.
    model = Tema

    # El template a donde se enviará la información.
    template_name = "detalles-temas.html"

    # De dónde se pretende recibir el parámetro de la uuid desde la url.
    pk_url_kwarg = "id_tema"
    context_object_name = "tema"

    def get_context_data(self, **kwargs):
        # El tema (objeto) obtenido por la ejecución de la clase.
        tema = self.object
        # Llamada a método padre de obtención de contextos para opbtener los contextos base.
        context = super().get_context_data(**kwargs)
        # Agragación al contexto el nuevo campo para los videos del tema.
        context["videos"] = Video.objects.filter(tema=tema)
        # URL de retorno a la vista anterior.
        context["url_retorno"] = reverse(
            "detalles-cursos", kwargs={"id_curso": tema.curso.id}
        )
        # Retorno del contexto junto con los videos del tema.
        return context


# Vista para detalles de los vídeos.
class VideoDetails(AuthorizationsMixin, DetailView):
    # Modelo desde donde pertenece el objeto a detallar.
    model = Video

    # El template a donde se enviará la información.
    template_name = "detalles-videos.html"

    # De dónde se pretende recibir el parámetro de la uuid desde la url.
    pk_url_kwarg = "id_video"
    context_object_name = "video"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # URL de retotno ala vista anterior.
        context["url_retorno"] = reverse(
            "detalles-temas", kwargs={"id_tema": self.object.tema.id}
        )
        return context


# Vista para cambiar imagen del curso.
class UpdateCourseImage(AuthorizationsMixin, UpdateView):
    model = Curso
    form_class = UpdateCoursesImageForm
    pk_url_kwarg = "id_curso"

    # Redirección a la vista de detalles del curso una vez procesada la subida con éxito.
    def get_success_url(self):
        curso = self.object
        return reverse("detalles-cursos", kwargs={"id_curso": curso.id})

    # En caso de ser un formulario inválido, agrupa y retorna los mensajes de error.
    def form_invalid(self, form):
        for field, message in form.errors.items():
            for error in message:
                messages.error(
                    self.request, error
                )  # NOTE: Esto podría recibir un tercer argumento para almacenar tags de configuraciones de CSS.
        return redirect("detalles-cursos", id_curso=self.get_object().pk)

    # Si el formulario adquiere la característica de ser válido después de las validaciones, simplemente retorna un mensaje de éxito y sigue con el curso del procedimiento (llamada al get_success_url)
    def form_valid(self, form):
        messages.success(self.request, "La imagen ha sido cargada correctamente.")
        return super().form_valid(form)


# Vista para garantizar el acceso a los recursos multimedia expuestos por el servidor media/ (garantizando el cumplimiento de la lógica de negocios y de autenticación).
class AccessToMediaFiles(
    LoginRequiredMixin,
    AuthorizationsMixin,
    ConfigAccessToMediaFilesMixin,
    BaseDetailView,
):
    pk_url_kwarg = "id_objeto"

    # Acceso a las configuraciones de acceso de los archivos media según lo establecido en la llamada del endpoint (alias) y así determinar el modelo general de la petición (Curso, Tema, Video).
    def get_queryset(self):
        alias = self.kwargs.get("alias_modelo")
        config = self.get_media_access_config(alias)
        if config:
            self.model = config.model
            # Llamada al método padre, que sería el mpetodo suministrado por el AuthorizationsMixin, destinado a garantizar la lógica de accesos según roles y permisos.
            return super().get_queryset()

    # Después de pasados los accesos de roles y permisos y determinado el modelo, se obtiene el objeto y el valor de su archivo. Para retornarlo como FileResponse.
    def get(self, request, *args, **kwargs):
        alias = self.kwargs.get("alias_modelo")
        # Configuraciones para acceder al recurso multimedia
        config = self.get_media_access_config(alias)
        # Objeto gracias al queryset efectuado al modelo y según los permisos necesarios para recuperarlo.
        obj = self.get_object()
        archivo = None
        if obj and config:
            # Obtención del archivo según la configuración (el nombre de su campo dodne está la url de acceso).
            archivo = getattr(obj, config.file_field, None)
        if not archivo:
            raise Http404(
                "El archivo no fue encontrado."
            )  # WARNING: Error 404 si no se ha obtenido el archivo.
        # Recuperación de su Mime type para pasarlo en los cabeceros
        content_type, encoding = mimetypes.guess_type(archivo.path)
        mime_type = (
            content_type or "application/octet-stream"
        )  # Si no se consigue su mime type, queda como desconocido y destinado a ejecutar desde una aplicación externa.

        # Uso del servidor de Django para servir el archivo
        if settings.DEBUG:
            return FileResponse(archivo.open("rb"), content_type=content_type)
        response = HttpResponse()
        # Cabecera que garantiza el acceso rápido e interno (redirección interna) mediante la configuración Nginx para carpetas denominadas "internal".
        response["X-Accel-Redirect"] = (
            "ruta_ficticia"  # TEST: Esto debería de estar accediendo a una dirección dentro del .env con la dirección privada (internal) de los recursos en el servidor de producción Nginx.
        )

        response["Content-type"] = mime_type
        return response


# Método deshabilitado (por AuthorizationsMixin). A espera de más pruebas.
"""# Modificación del queryset para verificar roles y, en base a eso, realizar las consultas según sea el caso.
    def get_queryset(self):
        # El uso de la función de Díaz.
        roles = roles_usuario(self.request)
        # Obtención del id desde la url
        id_curso = self.kwargs.get("id_curso")
        # Los profesores solo podrán acceder a sus propios cursos.
        if roles["es_profesor"]:
            return Curso.objects.filter(
                id=id_curso, profesor__usuario=self.request.user
            )
        # Los estudiantes solo podrán acceden al curso.
        if roles["es_estudiante"]:
            return Curso.objects.filter(id=id_curso)

        # WARNING: Retorna un error 404 si no cumple con los roles.
        return Curso.objects.none()"""

# NOTE: Falta construir las vistas para la creación de accesos a los cursos desde los estudiantes.
# TEST: Falta testear el ingreso según tipo de usuario, de los ingresos de profesores siempre y cuando les pertenezca el curso (estos dos de forma más incisiva), entre otros.
