import os
import av
import io
import uuid
from datetime import timedelta
from tempfile import NamedTemporaryFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from .images_processor import ImagesProcessor


# Clase para el procesamiento de los vídeos.
class VideosProcessor:
    def __init__(self, video, form, use_default_thumbnail):
        self.video = video
        self.form = form
        self.use_default_thumbnail = use_default_thumbnail

    def __call__(self):
        temp_path = None
        try:
            # Obtención de la extensión del archivo.
            ext_original = os.path.splitext(self.video.name)[1].lower()
            # Archivo temporal
            with NamedTemporaryFile(delete=False, suffix=ext_original) as temp_file:
                # Llenar al archivo temporal con los datos del real.
                for chunk in self.video.chunks():
                    temp_file.write(chunk)
                # Dirección del archivo temporal recién cargado.
                temp_path = temp_file.name
            # La librería abre el archivo temporal
            container = av.open(temp_path)
            # Verificación de que el archivo cargado cuente con al menos un stream del tipo vídeo
            video_stream = next(
                (s for s in container.streams.video),
                None,
            )
            # En caso de no tenerlo, da error
            if not video_stream:
                raise ValidationError(
                    "El vídeo suministrado no contiene un flujo de vídeo válido"
                )
            # Extracción de la duración y conversión de milisegundos a segundos
            duracion_segundos = container.duration / 1000000
            # Formateo del tiempo y guardado en un nuevo atributo del formulario.
            self.form.duracion_extraida = timedelta(seconds=int(duracion_segundos))
            # Si el usuario no cargó una miniatura. aquí se extrae una del primer frame del vídeo
            if self.use_default_thumbnail:
                stream = container.streams.video[0]
                for frame in container.decode(stream):
                    img_pil = frame.to_image()
                    # Si inicializa un contenedor de bytes
                    temp_thumb_io = io.BytesIO()
                    # Se guarda la imagen (PIL Object) que se ha extraído
                    img_pil.save(temp_thumb_io, format="JPEG", quality=85)
                    temp_thumb_io.seek(0)

                    # Se inicia un nombre único para la miniatura generada.
                    thumb_filename = f"thumb_{uuid.uuid4()}.jpg"

                    # Se guarda el contenido y características como un objeto de archivo que Django puede reconocer.
                    django_file = SimpleUploadedFile(
                        thumb_filename, temp_thumb_io.read(), content_type="image/jpeg"
                    )
                    # Se procesa la miniatura
                    processor = ImagesProcessor(django_file)
                    thumbnail_name, thumbnail_processed = processor()
                    # Se introduce la miniatura procesada en un nuevo campo al formulario
                    self.form.thumbnail_final = (
                        thumbnail_name,
                        thumbnail_processed,
                    )
                    break
            # Se cierra el proceso de la librería AV (Buena práctica)
            container.close()
            # Renombre del vídeo meidante un uuid
            uuid_name = uuid.uuid4()
            self.video.name = f"{uuid_name}{ext_original}"
        except Exception:
            raise ValidationError(
                "El vídeo que intentas cargar es inválido o está corrupto."
            )
        # Proceso de eliminación del archivo temporal
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                # Este es un manejo para que en caso de que, con el proceso realizado con AV, se tarde el sistema de reconocer o eliminar ese archivo temporal
                except PermissionError:
                    pass
        # Retorno del vídeo con su nuevo nombre y el formulario con la duración del vídeo y la miniatura para el vídeo.
        return self.video
