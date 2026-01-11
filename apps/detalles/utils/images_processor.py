import uuid
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError


# INFO: Esta clase instancia un objeto a partir de recibir una imagen para procesarla recibiendo si es necesario, las dimensiones en pixeles (ancho, alto), y el formato que se desea convertir al final.
class ImagesProcessor:
    def __init__(self, img, size_tp=(1080, 608), format="WEBP"):
        self.size_tp = size_tp
        self.format = format
        self.img = img

    def __call__(self):
        try:
            print("PROCESANDO IMAGEN")
            if not self.img:
                return None, None
            # Máximo de píxeles permitido para lasd imagenes (Evita las bombas de pixeles).
            Image.MAX_IMAGE_PIXELS = 10000000
            # Lleva al puntero al inicio del archivo, por si acaso.
            self.img.seek(0)
            # Procesamiento...
            with Image.open(self.img) as pil_img:
                # En caso de ser un .png, les cambia la configuración de color quítandoles la transparencia (A).
                if pil_img.mode in ("RGBA", "P"):
                    pil_img = pil_img.convert("RGB")
                # Borra los metadatos (Evita la permanencia de datos EXIF).
                pil_img.info = {}
                target_size = self.size_tp

                # Procesamiento de la imagen (ajuste a los pixeles indicadosd como tamnaño, el nivel de optimización del proceso y punto de referencia desde donde iniciar con la redimensión (en este caso desde el centro)).
                pil_img = ImageOps.fit(
                    pil_img,
                    target_size,
                    method=Image.Resampling.LANCZOS,
                    centering=(0.5, 0.5),
                )
                # Espacio que se comporta como archivo virtual para alkmacenar el contenido de la imagen (los binarios).
                buffer = BytesIO()

                # Conversión de la imagen a otro formato, copiando y pegando solo sus pixeles en una nueva (almacenandola en el buffer, estableciendo el formato (en este caso .webp), la calidad de la conversión final y el nivel de optimización para el proceso).
                pil_img.save(buffer, format=self.format, quality=80, method=6)
                # Uso de uuid para renombrar la nueva imagen generada.
                uuid_nombre = uuid.uuid4()
                nombre_final = f"{uuid_nombre}.{self.format.lower()}"
                # Retorno del nombre final y el contenido del archivo para la reasignación.
                return nombre_final, ContentFile(buffer.getvalue())
        except Exception as e:
            print(
                f"Error en el procesamiento de la clase {ImagesProcessor.__name__}: {e}"
            )
            raise ValidationError(
                "Hubo un error al procesar el archivo, intente más tarde."
            )
