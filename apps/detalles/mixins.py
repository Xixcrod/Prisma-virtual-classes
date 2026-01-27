from apps.core.models import Curso, Tema, Video, Usuario, Profesor, Acceso, Estudiante
from apps.core.utils.context_processors import roles_usuario
from django.http import Http404
from django.core.exceptions import ValidationError
from django.views.generic.base import ContextMixin
from .utils.media_config import MediaConfig
from .utils.images_processor import ImagesProcessor


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
            return (
                qs.filter(**{f"{prefij}": user}) if prefij else qs.none()
            )  # WARNING: 404 Si no se encontró el prefijo.
        # En caso de ser estudiante, el filtrado original ahora se adaptará al acceso aprobado del usuario, para que los estudiantes solo accedan a los contenidos solo si tienen el acceso al curso.
        if roles[
            "es_estudiante"
        ]:  # Segunda condición para que de ninguna manera un estudiante pueda modificar nada, ya que se le impide el uso del método POST.
            if self.request.method != "GET":
                return qs.none()  # WARNING: Error 404 en caso de que el estudiante intente hacer cualquier POST. (porque no puede crear o modificar nada por ahora)
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


# Mixin para el manejo dinámico de formularios en una vista, con solo declarar un forms_config {"form": FormConfig(form_class=FormClass, prefix="prefix", is_create=False, roles={"es_profesor", "otro_rol"})}
class FormsPostMixin(ContextMixin):
    # Inicialización del set para guardar las configuraciones
    forms_config = {}

    # Opbtención de las instancias de los formularios, siendo bind_form_key la forma de enlazar un formulario con su action (y así contarlo como post y llenarlo (bound)).
    def get_forms(self, bind_form_key=None):
        # Determinación de los roles de usuarios
        dict_roles = roles_usuario(self.request)
        list_roles_usuario = []
        for rol, value in dict_roles.items():
            if value:
                list_roles_usuario.append(rol)
        # Roles de usuario actual en un set (conjunto).
        set_roles_usuario = set(list_roles_usuario)

        # Obtención del objeto o instancia específica sobre la que trabajar (desde la DetailView para formularios de modificación)
        obj = getattr(self, "object", None)
        if not obj and hasattr(self, "get_object"):
            obj = self.get_object()

        forms_instanced = {}
        # Para cada formulario delcarado en la forms_config
        for key, config in self.forms_config.items():
            # Verificar si coindiden los roles actuales con los permitidos para acceder al formulario.
            if set_roles_usuario.intersection(config.roles):
                # Argumentos que se van a pasar al momento de instanciar el formulario.
                kwargs = {}
                # Agregación de todas los argumentos
                if config.prefix:
                    kwargs["prefix"] = config.prefix
                # Si el formulario no está destinado a crear un nuevo registro, se le pasa el registro actual (para modificarlo)
                if not config.is_create and obj:
                    kwargs["instance"] = obj
                # En caso de que el formulario coindida o esté enlazado con el action actual, se le pasan los datos desde el POST para instanciar un formulario lleno de datos (bound).
                if key == bind_form_key:
                    kwargs["data"] = self.request.POST
                    kwargs["files"] = self.request.FILES
                # Instanciamiento de formularios, pasandoles argumentos y datos dado el caso.
                forms_instanced[key] = config.form_class(**kwargs)
        return forms_instanced

    # Devolución de los formularios al template como contextos
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_forms()
        # Se obtienen los formularios isntanciados y se agregan al contexto, a excepción de los formularios que ya estaban (los que fallaron a las validaciones y contienen sus errores, siendo trasnferidos al context).
        for key, form in forms.items():
            if key not in context:
                context[key] = form
        return context

    # En caso de POST
    def post(self, request, *args, **kwargs):
        if hasattr(self, "get_object"):
            self.object = self.get_object()
        action = request.POST.get("action")
        # Si el action del botón no está en las configuraciones del formulario, simplemente se retornan los formularios sin cambios.
        if action not in self.forms_config:
            return self.render_to_response(self.get_context_data())
        # Obtenbción de todos los formularios.
        forms = self.get_forms(bind_form_key=action)
        # Obtención de solo el formulario enlazado con el action, que para este momento estará lleno (bound)
        form_active = forms.get(action)
        # Aplicación de validaciones
        if form_active and form_active.is_valid():
            return self.form_valid(form_active, action)
        # Si es inválido, se retornan al contexto los formularios, ya incluyendo en el context el formulario fallido ( con errores)
        else:
            return self.render_to_response(self.get_context_data(**forms))


# Mixin de procesamiento y limpieza de imágenes.
class CleanImageFormMixin:
    def clean_imagen(self):
        # Obtenbción del campo ya validado.
        imagen = self.cleaned_data.get("imagen")
        if not imagen:
            return None
        # Procesamiento de la imagen.
        try:
            processor = ImagesProcessor(imagen)

            nombre, imagen_procesada = processor()

            if not nombre and not imagen_procesada:
                print(
                    f"DEBUG: La imagen procesada ha generado como resultado en su nombre: {nombre} y en su contenido: {imagen_procesada}"
                )
                raise ValidationError(
                    "No se ha podido procesar la imagen, intente más tarde."
                )
            # Redefinición de los valores del campo (nombre del archivo y su contenido).
            imagen.file = imagen_procesada
            imagen.name = nombre
        except Exception as e:
            raise ValidationError(f"Error procesando la imagen: {str(e)}")
        return imagen
