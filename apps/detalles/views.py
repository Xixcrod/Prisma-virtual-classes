from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from apps.core.models import Curso, Tema, Video, Usuario, Profesor, Acceso
from .mixins import AuthorizationsMixin
from apps.core.utils.context_processors import (
    roles_usuario,
)  # Importación de la función de Díaz para gestionar los roles de usuario


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

        # Si se trata de un estudiante sin acceso a ese curso, entonces no retornará en el contexto la información de los temas.
        if (
            roles["es_estudiante"]
            and not Acceso.objects.filter(
                curso=self.object, estudiante=self.request.user.estudiante, estado="AP"
            ).exists()
        ):
            context["tiene_acceso"] = False
            return context
        # Si se trata de un profesor, se contará la cantidad de estudiantes inscritos en el curso.
        if roles["es_profesor"]:
            context["cantidad_estudiantes"] = Acceso.objects.filter(
                curso=curso, estado="AP"
            ).count()
        # Agragación al contexto el nuevo campo para los temas del curso.
        context["temas"] = Tema.objects.filter(curso=curso)
        context["tiene_acceso"] = True
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
