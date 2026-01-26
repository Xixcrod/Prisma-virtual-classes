from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.views.generic import DetailView, UpdateView
from django.views.generic.detail import BaseDetailView, SingleObjectMixin
from django.views import View
from apps.core.models import Curso, Tema, Video, Usuario, Profesor, Acceso
from .mixins import AuthorizationsMixin, ConfigAccessToMediaFilesMixin, FormsPostMixin
from django.conf import settings
from apps.core.utils.context_processors import (
    roles_usuario,
)  # Importación de la función de Díaz para gestionar los roles de usuario
from .forms import (
    UpdateCoursesImageForm,
    UpdateCoursesForm,
    CreateTemaForm,
    UpdateThemesImageForm,
    UpdateThemeForm,
    UpdateVideoForm,
    CreateVideoForm,
)
import mimetypes
from .utils.forms_config import FormConfig


#   Vista para detalles de los cursos.
class CoursesDetails(
    LoginRequiredMixin, AuthorizationsMixin, FormsPostMixin, DetailView
):
    # Modelo desde donde pertenece el objeto a detallar.
    model = Curso

    # El template a donde se enviará la información.
    template_name = "detalles-cursos.html"

    # De dónde se pretende recibir el parámetro de la uuid desde la url.
    pk_url_kwarg = "id_curso"
    context_object_name = "curso"
    # Declaración de la configuración de formularios
    forms_config = {
        # Formulario de modificación de imagen
        "update_course_image_form": FormConfig(
            form_class=UpdateCoursesImageForm,
            prefix="update_course_image",
            roles={"es_profesor"},
        ),
        # Formulario de modificación de detalles de curso
        "update_course_form": FormConfig(
            form_class=UpdateCoursesForm,
            prefix="update_course_form",
            roles={"es_profesor"},
        ),
        # Formulario de creación de temas
        "create_theme_form": FormConfig(
            form_class=CreateTemaForm,
            is_create=True,
            prefix="create_theme",
            roles={"es_profesor"},
        ),
    }

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
        # Cantidad de vídeos
        context["cantidad_videos"] = Video.objects.filter(tema__curso=curso).count()
        context["tiene_acceso"] = True
        return context

    # En de que los formularios pasen las validaciones
    def form_valid(self, form, action):
        # Mensajes de éxito según el formulario
        forms_success_msj = {
            "update_course_image_form": "La imagen se ha cargado correctamente.",
            "update_course_form": "El curso ha sido modificado exitosamente.",
            "create_theme_form": "El tema ha sido creado exitosamente.",
        }
        # Si es la creación de un tema, referenciar la FK del curso actual
        if action == "create_theme_form":
            obj = form.save(commit=False)
            obj.curso = self.get_object()
            obj.save()

        else:
            form.save()
        if action in forms_success_msj:
            messages.success(self.request, forms_success_msj.get(action))
        return redirect(self.request.path)


# Vista para detalles de los temas.
class ThemesDetails(
    LoginRequiredMixin, AuthorizationsMixin, FormsPostMixin, DetailView
):
    # Modelo desde donde pertenece el objeto a detallar.
    model = Tema

    # El template a donde se enviará la información.
    template_name = "detalles-temas.html"

    # De dónde se pretende recibir el parámetro de la uuid desde la url.
    pk_url_kwarg = "id_tema"
    context_object_name = "tema"

    # Confirguración de formularios
    forms_config = {
        "update_theme_image_form": FormConfig(
            form_class=UpdateThemesImageForm,
            prefix="update_theme_image_form",
            roles={"es_profesor"},
        ),
        "update_theme_form": FormConfig(
            form_class=UpdateThemeForm,
            prefix="update_theme_form",
            roles={"es_profesor"},
        ),
        "create_video_form": FormConfig(
            form_class=CreateVideoForm,
            is_create=True,
            prefix="create_video_form",
            roles={"es_profesor"},
        ),
    }

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

    # En caso de que el formulario sea validado
    def form_valid(self, form, action):
        # Mensajes de éxito según el formulario
        forms_success_msj = {
            "update_theme_image_form": "La imagen se ha cargado correctamente.",
            "update_theme_form": "El tema ha sido modificado exitosamente.",
            "create_video_form": "El vídeo ha sido cargado exitosamente.",
        }
        if action == "create_video_form":
            obj = form.save(commit=False)
            obj.tema = self.get_object()
            obj.duracion = getattr(form, "duracion_extraida", None)
            obj.save()
        else:
            form.save()
        if action in forms_success_msj:
            messages.success(self.request, forms_success_msj.get(action))
        return redirect(self.request.path)


# Vista para detalles de los vídeos.
class VideoDetails(LoginRequiredMixin, AuthorizationsMixin, FormsPostMixin, DetailView):
    # Modelo desde donde pertenece el objeto a detallar.
    model = Video

    # El template a donde se enviará la información.
    template_name = "detalles-videos.html"

    # De dónde se pretende recibir el parámetro de la uuid desde la url.
    pk_url_kwarg = "id_video"
    context_object_name = "video"
    # Configuración de formularios
    forms_config = {
        "update_video_form": FormConfig(
            form_class=UpdateVideoForm,
            prefix="update_video_form",
            roles={"es_profesor"},
        )
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # URL de retotno ala vista anterior.
        context["url_retorno"] = reverse(
            "detalles-temas", kwargs={"id_tema": self.object.tema.id}
        )
        return context

    # En caso de que el formulario sea validado
    def form_valid(self, form, action):
        # Mensajes de éxito según el formulario
        forms_success_msj = {
            "update_theme_image_form": "La imagen se ha cargado correctamente.",
            "update_theme_form": "El curso ha sido modificado exitosamente.",
        }
        form.save()
        if action in forms_success_msj:
            messages.success(self.request, forms_success_msj.get(action))
        return redirect(self.request.path)


# Vista para borrar temas de un curso
class DeleteTheme(LoginRequiredMixin, AuthorizationsMixin, SingleObjectMixin, View):
    model = Tema
    pk_url_kwarg = "id_tema"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        curso = self.object.curso.id
        self.object.delete()
        return redirect("detalles-cursos", id_curso=curso)


# Vista para borrar vídeos
class DeleteVideo(LoginRequiredMixin, AuthorizationsMixin, SingleObjectMixin, View):
    model = Video
    pk_url_kwarg = "id_video"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        tema = self.object.tema.id
        self.object.delete()
        return redirect("detalles-temas", id_tema=tema)


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
