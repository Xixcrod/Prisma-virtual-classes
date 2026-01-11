from django.core.exceptions import ValidationError


# Validaciones básicas (tamaño y tipo de mimes).
class ValidateImage:
    def __init__(self, mb_max=20, mimes_perm=None):
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
                f"La imagen que intentas subir excede del máximo permitido ({(self.mb_max * 1024 * 1024)})."
            )

        mime = archivo.content_type
        if mime not in self.mimes_perm:
            raise ValidationError(
                "El tipo de archivo no está soportado. Intenta con png, jpeg o webp."
            )
