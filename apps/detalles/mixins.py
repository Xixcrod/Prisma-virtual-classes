from apps.core.models import Curso, Tema, Video, Usuario, Profesor, Acceso, Estudiante
from apps.core.utils.context_processors import roles_usuario


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
            return qs.filter(**{f"{prefij}": user})
        # En caso de ser estudiante, el filtrado original ahora se adaptará al acceso aprobado del usuario, para que los estudiantes solo accedan a los contenidos solo si tienen el acceso al curso.
        if roles["es_estudiante"]:
            # En caso del modelo ser un Curso, no efectúa un filtrado adicional porque se requiere enviar al template el booleeano para las solicitudes de acceso.
            if self.model == Curso:
                return qs
            # Prefijo de según el modelo y rol para modificar el filtro.
            prefij = MODELOS_LOOKUPS_MAP["estudiante"].get(self.model)
            return qs.filter(
                **{f"{prefij}__estudiante__usuario": user, f"{prefij}__estado": "AP"}
            )
        return qs.none()  # WARNING: Error 404 si no cumple con los roles (si no es estudiante o profesor).
