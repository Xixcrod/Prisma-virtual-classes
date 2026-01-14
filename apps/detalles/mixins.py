from apps.core.models import Curso, Tema, Video, Usuario, Profesor, Acceso, Estudiante
from apps.core.utils.context_processors import roles_usuario
from django.http import Http404
from django.views.generic import UpdateView
from .utils.media_config import MediaConfig


# Clase mixin para la autorización basada en roles de usuario para evitar el acceso no autorizado.
class AuthorizationsMixin:
    # Redrefinición del queryset para filtrar según los roles de usuario.
    def get_queryset(self):
        # Función de Díaz para roles.
        roles = roles_usuario(self.request)
        # Obtención del usuario autenticado.
        user = self.request.user
        # Llamada al método padre del queryset de DetailView (necesario, como clase base, declarar en orden en la herencia).
        qs = super().get_queryset()

        # Mapeo de lookups según el rol del usuario y el modelo en cuestión. Para agregar un nuevo rol o modelo hijo es necesario modificar.
        MODELOS_LOOKUPS_MAP = {
            "profesor": {
                Curso: "profesor__usuario",
                Tema: "curso__profesor__usuario",
                Video: "tema__curso__profesor__usuario",
            },
            "estudiante": {
                Curso: "acceso",
                Tema: "curso__acceso",
                Video: "tema__curso__acceso",
            },
        }

        # En caso de ser profesor, el filtrado original ahora se adaptará al usuario específico para que cada profesor solo tenga acceso a su contenido.
        if roles["es_profesor"]:
            # En caso de no tener el modelo mapeado.
            if self.model not in MODELOS_LOOKUPS_MAP["profesor"]:
                print(
                    f"DEBUG: {self.model} no es un modelo válido para el mixin de autorización de profesores."
                )
            # Prefijo según el modelo y rol para modificar el filtro.
            prefij = MODELOS_LOOKUPS_MAP["profesor"].get(self.model)
            return qs.filter(**{f"{prefij}": user}) if prefij else qs.none()
        # En caso de ser estudiante, el filtrado original ahora se adaptará al acceso aprobado del usuario, para que los estudiantes solo accedan a los contenidos solo si tienen el acceso al curso.
        if (
            roles["es_estudiante"] and not isinstance(self, UpdateView)
        ):  # Segunda condición para que de ninguna manera un estudiante pueda modificar nada desde la clase UpdateView.
            # En caso del modelo ser un Curso, no efectúa un filtrado adicional porque se requiere enviar al template el booleeano para las solicitudes de acceso.
            if self.model == Curso:
                return qs
            # Prefijo de según el modelo y rol para modificar el filtro.
            prefij = MODELOS_LOOKUPS_MAP["estudiante"].get(self.model)
            return (
                qs.filter(
                    **{
                        f"{prefij}__estudiante__usuario": user,
                        f"{prefij}__estado": "AP",
                    }
                )
                if prefij
                else qs.none()
            )

        return qs.none()  # WARNING: Error 404 si no cumple con los roles (si no es estudiante o profesor).


# Mixin para establecer las configuraciones para el funcionamiento de la función que permite consumir lor recursos multimedia del servidor externo (todo según la ógica de negocios (establecido por el AuthorizationsMixin) y de autenticación de usuarios.
class ConfigAccessToMediaFilesMixin:
    # Mapeado de las configuraciones posibles para consumir los recursos según el alias puesto como argumento en el llamado de la función (si se añaden nuevos modelos o recursos, bastaría con ponerlos aquí).
    MEDIA_ACCESS_MAPPING = {
        "img_curso": MediaConfig(model=Curso, file_field="imagen", alias="img_curso"),
        "img_tema": MediaConfig(model=Tema, file_field="imagen", alias="img_tema"),
        "video": MediaConfig(model=Video, file_field="url_video", alias="video"),
    }

    # Obtención de la configuración según el alias establecido en la url del template.
    def get_media_access_config(self, alias):
        config = self.MEDIA_ACCESS_MAPPING.get(alias, None)
        if not config:
            raise Http404(
                "Recuso no válido."
            )  # WARNING: Error 404 si se ha proporcionado un alias inexistente en el mapeo.
        return config
