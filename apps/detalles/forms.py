from typing import Required
from django import forms
from django.core.validators import FileExtensionValidator
from apps.core.models import Curso, Tema, Video
from .utils.videos_processor import VideosProcessor
from .utils.images_processor import ImagesProcessor
from django.core.exceptions import ValidationError
from apps.detalles.validators import ValidateImage, not_only_whitespaces
from .mixins import CleanImageFormMixin

# Formularios de la aplicación detalles


# INFO: Formulario de modificación de imagen del Curso.
class UpdateCoursesImageForm(CleanImageFormMixin, forms.ModelForm):
    # Campo dodne se alamacena la url de la imagen (curso.imagen).
    imagen = forms.ImageField(
        # Validaciones de extensiones y validaciones básicas de la imagen (Máximo de tamaño permitido, y mimes types permitidos).
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            ValidateImage(
                mb_max=15,
                mimes_perm=["image/jpeg", "image/jpg", "image/png", "image/webp"],
            ),
        ],
        widget=forms.FileInput(attrs={"class": "form-control"}),
        label="Cambiar imagen del curso.",
        # Mensajes de error modificados a conveniencia.
        error_messages={
            "invalid_image": "El archivo no es una imagen válida o está corrupto. Intenta con un formato real.",
            "missing": "No has seleccionado ningún archivo.",
            "empty": "El archivo está vacío.",
            "invalid_extension": "Esta extensión de archivo no está permitida. Usa JPG, PNG o WebP.",
        },
    )

    # Meta clase para señalar el nombre del campo y en cuál modelo se guardarán las instancias.
    class Meta:
        model = Curso
        fields = ["imagen"]

    # Función clean que determina lo que se hace una vez se han efectuado las validaciones establecidas.
    def save(self, commit=True):
        if not self.files.get(f"{self.prefix}-imagen" if self.prefix else "imagen"):
            return self.instance
        return super().save(commit=commit)


# Formulario para editar los detalles del curso
class UpdateCoursesForm(forms.ModelForm):
    descripcion = forms.CharField(
        min_length=10,
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                "class": "form-class",
                "placeholder": "Escribe una descripción para el tema...",
                "autocomplete": "off",
            }
        ),
        label="Descripción:",
        validators=[not_only_whitespaces],
        error_messages={
            "required": "La descripción no puede quedar vacía.",
            "min_length": "Como mínimo, el número mínimo de caracteres es de 10.",
            "max_length": "El número máximo de caracteres es de 5000. Vuelve a intentarlo.",
        },
    )

    class Meta:
        model = Curso
        fields = ["descripcion"]


# Formulario para crear nuevos temas
class CreateTemaForm(CleanImageFormMixin, forms.ModelForm):
    imagen = forms.ImageField(
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            ValidateImage(
                mb_max=15,
                mimes_perm=["image/jpeg", "image/jpg", "image/png", "image/webp"],
            ),
        ],
        widget=forms.FileInput(attrs={"class": "form-control"}),
        label="Subir imagen del tema:",
        error_messages={
            "required": "Debes adjuntar obligatoriamente una imagen.",
            "invalid_image": "El archivo no es una imagen válida o está corrupto. Intenta con un formato real.",
            "missing": "No has seleccionado ningún archivo.",
            "empty": "El archivo está vacío.",
            "invalid_extension": "Esta extensión de archivo no está permitida. Usa JPG, PNG o WebP.",
        },
    )

    titulo = forms.CharField(
        max_length=75,
        widget=forms.TextInput(
            attrs={
                "class": "form-class",
                "placeholder": "Introducción al Pseudocódigo...",
                "autocomplete": "off",
            }
        ),
        label="Título:",
        error_messages={
            "required": "El título no puede quedar vacío.",
            "max_length": "El número de caracteres máximos es de 75. Vuelve a intentarlo.",
        },
    )
    descripcion = forms.CharField(
        min_length=10,
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                "class": "form-class",
                "placeholder": "Escribe una descripción para el tema...",
                "autocomplete": "off",
            }
        ),
        label="Descripción:",
        validators=[not_only_whitespaces],
        error_messages={
            "required": "La descripción no puede quedar vacía.",
            "min_length": "Como mínimo, el número mínimo de caracteres es de 10.",
            "max_length": "El número máximo de caracteres es de 5000. Vuelve a intentarlo.",
        },
    )

    class Meta:
        model = Tema
        fields = ["imagen", "titulo", "descripcion"]


# Formulario para cambiar la imagen de un tema
class UpdateThemesImageForm(CleanImageFormMixin, forms.ModelForm):
    imagen = forms.ImageField(
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            ValidateImage(
                mb_max=15,
                mimes_perm=["image/jpeg", "image/jpg", "image/png", "image/webp"],
            ),
        ],
        widget=forms.FileInput(attrs={"class": "form-control"}),
        label="Cambiar imagen del tema.",
        # Mensajes de error modificados a conveniencia.
        error_messages={
            "required": "La imagen debe ser ingresada.",
            "invalid_image": "El archivo no es una imagen válida o está corrupto. Intenta con un formato real.",
            "missing": "No has seleccionado ningún archivo.",
            "empty": "El archivo está vacío.",
            "invalid_extension": "Esta extensión de archivo no está permitida. Usa JPG, PNG o WebP.",
        },
    )

    class Meta:
        model = Tema
        fields = ["imagen"]


# Formulario para editar los detalles de un tema
class UpdateThemeForm(forms.ModelForm):
    titulo = forms.CharField(
        max_length=75,
        widget=forms.TextInput(
            attrs={
                "class": "form-class",
                "placeholder": "Bucles for...",
                "autocomplete": "off",
            }
        ),
        label="Título:",
        error_messages={
            "required": "El título no puede quedar vacío.",
            "max_length": "El número de caracteres máximos es de 75. Vuelve a intentarlo.",
        },
    )
    descripcion = forms.CharField(
        min_length=10,
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                "class": "form-class",
                "placeholder": "Escribe una descripción para el tema...",
                "autocomplete": "off",
            }
        ),
        label="Descripción:",
        validators=[not_only_whitespaces],
        error_messages={
            "required": "La descripción no puede quedar vacía.",
            "min_length": "Como mínimo, el número mínimo de caracteres es de 10.",
            "max_length": "El número máximo de caracteres es de 5000. Vuelve a intentarlo.",
        },
    )

    class Meta:
        model = Tema
        fields = ["titulo", "descripcion"]


# Formulario para editar los detalles de un vídeo
class UpdateVideoForm(forms.ModelForm):
    titulo = forms.CharField(
        max_length=75,
        widget=forms.TextInput(
            attrs={
                "class": "form-class",
                "placeholder": "Bucles for...",
                "autocomplete": "off",
            }
        ),
        label="Título:",
        error_messages={
            "required": "El título no puede quedar vacío.",
            "max_length": "El número de caracteres máximos es de 75. Vuelve a intentarlo.",
        },
    )
    resumen = forms.CharField(
        min_length=10,
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                "class": "form-class",
                "placeholder": "Escribe un resumen para el video...",
                "autocomplete": "off",
                "row": 6,
            }
        ),
        label="Resumen:",
        validators=[not_only_whitespaces],
        error_messages={
            "required": "La descripción no puede quedar vacía.",
            "min_length": "Como mínimo, el número mínimo de caracteres es de 10.",
            "max_length": "El número máximo de caracteres es de 5000. Vuelve a intentarlo.",
        },
    )

    class Meta:
        model = Video
        fields = ["titulo", "resumen"]


# Formulario para crear vídeos
class CreateVideoForm(forms.ModelForm):
    titulo = forms.CharField(
        max_length=75,
        widget=forms.TextInput(
            attrs={
                "class": "form-class",
                "placeholder": "Bucles for...",
                "autocomplete": "off",
            }
        ),
        label="Título:",
        error_messages={
            "required": "El título no puede quedar vacío.",
            "max_length": "El número de caracteres máximos es de 75. Vuelve a intentarlo.",
        },
    )
    resumen = forms.CharField(
        min_length=10,
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                "class": "form-class",
                "placeholder": "Escribe un resumen para el video...",
                "autocomplete": "off",
                "row": 6,
            }
        ),
        label="Resumen:",
        validators=[not_only_whitespaces],
        error_messages={
            "required": "La descripción no puede quedar vacía.",
            "min_length": "Como mínimo, el número mínimo de caracteres es de 10.",
            "max_length": "El número máximo de caracteres es de 5000. Vuelve a intentarlo.",
        },
    )

    url_video = forms.FileField(
        widget=forms.FileInput(
            attrs={
                "class": "form-input",
                "accept": "video/*",
            }
        ),
        label="Vídeo:",
    )
    thumbnail = forms.ImageField(
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            ValidateImage(
                mb_max=15,
                mimes_perm=["image/jpeg", "image/jpg", "image/png", "image/webp"],
            ),
        ],
        widget=forms.FileInput(attrs={"class": "form-control"}),
        label="Subir miniatura del vídeo (Opcional):",
        error_messages={
            "invalid_image": "El archivo no es una imagen válida o está corrupto. Intenta con un formato real.",
            "missing": "No has seleccionado ningún archivo.",
            "empty": "El archivo está vacío.",
            "invalid_extension": "Esta extensión de archivo no está permitida. Usa JPG, PNG o WebP.",
        },
        required=False,
    )

    # Aplicación de validaciones y procesamientos de vídeo
    def clean_url_video(self):
        video = self.cleaned_data.get("url_video")
        if not video:
            raise ValidationError("El vídeo no ha sido suministrado.")
        if video.size > 10000 * 1024 * 1024:
            raise ValidationError(
                "El vídeo suministrado excede del límite establecido."
            )
        allowed_types = [
            "video/mp4",
            "video/webm",
            "video/quicktime",
            "video/x-msvideo",
        ]
        if video.content_type not in allowed_types:
            raise ValidationError("Este vídeo no está en un formato válido.")
        # Obtención del prefijo que denota el formulario desde el html (porque todavía no se ha ejecutado el clean_thumbnail)
        prefix = f"{self.prefix}-" if self.prefix else ""
        # Se obtiene la miniatura que el usuario cargó
        thumbnail_uploaded = self.files.get(f"{prefix}thumbnail")
        # Si no la ha cargado, se procesa el vídeo y ahí también se extrae del primer frame una imagen que servirá de miniatura para guardarla en la Base de Datos. Si lo hizo, se procesa y guarda esa miniatura.
        if not thumbnail_uploaded:
            processor = VideosProcessor(video, self, use_default_thumbnail=True)
        else:
            processor = VideosProcessor(video, self, use_default_thumbnail=False)
            # Validaciones y procesamientos directos de la miniatura si la cargó el usuario
            validator_thumbnail = ValidateImage(mb_max=15)
            validator_thumbnail(thumbnail_uploaded)
            thumbnail_uploaded.seek(0)
            # Procesamiento de la miniatura
            processor_image = ImagesProcessor(thumbnail_uploaded)

            thumnail_name, thumbnail = processor_image()
            # Se guarda la miniatura procesada y enviada por el usuario en un nuevo campo del formulario
            self.thumbnail_final = (thumnail_name, thumbnail)

        video = processor()
        return video

    class Meta:
        model = Video
        fields = ["titulo", "resumen", "url_video", "thumbnail"]


# Formulario para cambiar la miniatura de un vídeo
class UpdateThumbnailVideoForm(forms.ModelForm):
    thumbnail = forms.ImageField(
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            ValidateImage(
                mb_max=15,
                mimes_perm=["image/jpeg", "image/jpg", "image/png", "image/webp"],
            ),
        ],
        widget=forms.FileInput(attrs={"class": "form-control"}),
        label="Cambiar la miniatura del vídeo.",
        # Mensajes de error modificados a conveniencia.
        error_messages={
            "required": "La miniatura debe ser ingresada.",
            "invalid_image": "El archivo no es una imagen válida o está corrupto. Intenta con un formato real.",
            "missing": "No has seleccionado ningún archivo.",
            "empty": "El archivo está vacío.",
            "invalid_extension": "Esta extensión de archivo no está permitida. Usa JPG, PNG o WebP.",
        },
    )

    def clean_thumbnail(self):
        # Obtenbción del campo ya validado.
        thumbnail = self.cleaned_data.get("thumbnail")
        if not thumbnail:
            return None
        # Procesamiento de la imagen.
        try:
            processor = ImagesProcessor(thumbnail)

            nombre, imagen_procesada = processor()

            if not nombre and not imagen_procesada:
                print(
                    f"DEBUG: La imagen procesada ha generado como resultado en su nombre: {nombre} y en su contenido: {imagen_procesada}"
                )
                raise ValidationError(
                    "No se ha podido procesar la imagen, intente más tarde."
                )
            # Redefinición de los valores del campo (nombre del archivo y su contenido).
            thumbnail.file = imagen_procesada
            thumbnail.name = nombre
        except Exception as e:
            raise ValidationError(f"Error procesando la imagen: {str(e)}")
        return thumbnail

    class Meta:
        model = Video
        fields = ["thumbnail"]
