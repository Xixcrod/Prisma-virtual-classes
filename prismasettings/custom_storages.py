import mimetypes
from django.core.files.storage import Storage
from django.conf import settings
from supabase import create_client, Client

class SupabaseMediaStorage(Storage):
    """
    Storage nativo para Django usando la librería oficial de Supabase.
    Evita el uso de boto3/S3 y garantiza los MIME types correctos.
    """
    def __init__(self):
        # Inicializamos el cliente de Supabase con las variables de tu settings
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_KEY
        )
        self.bucket = settings.SUPABASE_MEDIA_BUCKET

    def _save(self, name, content):
        # 1. Detectar el formato exacto del archivo (ej: video/mp4)
        content_type, _ = mimetypes.guess_type(name)
        mime_type = content_type or 'application/octet-stream'
        
        # 2. Configurar los metadatos para Supabase
        file_options = {"content-type": mime_type}
        
        # 3. Leer los bytes del archivo desde la memoria de Django
        content.seek(0)
        file_data = content.read()
        
        # 4. Subir directamente por la API de Supabase
        self.supabase.storage.from_(self.bucket).upload(
            file=file_data, 
            path=name, 
            file_options=file_options
        )
        return name

    def url(self, name):
        # Retorna la URL pública, limpia y sin parámetros extraños
        return self.supabase.storage.from_(self.bucket).get_public_url(name)

    def exists(self, name):
        # Retorna False para permitir que Django sobrescriba archivos si tienen el mismo nombre
        return False
        
    def delete(self, name):
        # Método para borrar el archivo de Supabase si se elimina en Django
        self.supabase.storage.from_(self.bucket).remove([name])