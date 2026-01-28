from django.core.exceptions import ValidationError
from PIL import Image


# Validaciones básicas (tamaño y tipo de mimes).
class ValidateImage:
    def __init__(self, mb_max=15, mimes_perm=None):
        self.mimes_perm = mimes_perm or [
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/jpg",
        ]
        self.mb_max = mb_max

    def __call__(self, archivo):
        if archivo.size > self.mb_max * 1024 * 1024:
            raise ValidationError(
                f"La imagen que intentas subir excede del máximo permitido ({(self.mb_max)}MB)"
            )

        mime = archivo.content_type
        if mime not in self.mimes_perm:
            raise ValidationError(
                "El tipo de archivo no está soportado. Intenta con png, jpeg o webp.",
                code="invalid_image",
            )
        archivo.seek(0)
        # Contra bomba de pixeles.
        try:
            with Image.open(archivo) as pil_img:
                Image.MAX_IMAGE_PIXELS = 10000000
                width, height = pil_img.size
                total_pixels = width * height
                if total_pixels > Image.MAX_IMAGE_PIXELS:
                    raise ValidationError(
                        "La imagen no ha podido ser procesada, excedió del límite permitido de pixeles."
                    )
        except (IOError, SyntaxError, Image.UnidentifiedImageError):
            raise ValidationError(
                "La imagen suministrada no está en un formato válido."
            )


# Validación de que la cantidad de caracteres sea mayor o igual a 10, sin contar espacios en blanco.
def not_only_whitespaces(value):
    if len(value.strip()) < 10:
        raise ValidationError(
            "El número de caracteres debe ser como mínimo de 10, sin incluir los espacios en blanco."
        )
