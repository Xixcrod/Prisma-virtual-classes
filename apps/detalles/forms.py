from django import forms
from django.core.validators import FileExtensionValidator
from apps.core.models import Curso
from apps.detalles.utils.images_processor import ImagesProcessor
from django.core.exceptions import ValidationError
from apps.detalles.validators import ValidateImage

# Formularios de la aplicación detalles


# INFO: Formulario de modificación de imagen del Curso.
class UpdateCoursesImageForm(forms.ModelForm):
    # Campo dodne se alamacena la url de la imagen (curso.imagen).
    imagen = forms.ImageField(
        # Validaciones de extensiones y validaciones básicas de la imagen (Máximo de tamaño permitido, y mimes types permitidos).
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            ValidateImage(
                mb_max=20,
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
    def clean_imagen(self):
        # Obtenbción del campo ya validado.
        imagen = self.cleaned_data.get("imagen")
        # Procesamiento de la imagen.
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

        return imagen
