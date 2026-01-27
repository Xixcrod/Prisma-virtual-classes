import os
import av
import uuid
from datetime import timedelta
from tempfile import NamedTemporaryFile
from django.core.exceptions import ValidationError


# Clase para el procesamiento de los vídeos.
class VideosProcessor:
    def __init__(self, video, form):
        self.video = video
        self.form = form

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
        # Retorno del vídeo con su nuevo nombre y el formulario con la duración del vídeo.
        return self.video
