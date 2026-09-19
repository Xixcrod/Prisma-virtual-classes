import mimetypes
from django.core.files.storage import Storage
from django.conf import settings
from supabase import create_client, Client

class SupabaseMediaStorage(Storage):
    """
    Storage nativo para Django usando la librería oficial de Supabase.
    """
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_KEY
        )
        self.bucket = settings.SUPABASE_MEDIA_BUCKET

    def _save(self, name, content):
        content_type, _ = mimetypes.guess_type(name)
        mime_type = content_type or 'application/octet-stream'
        
        file_options = {"content-type": mime_type}
        
        content.seek(0)
        file_data = content.read()
        
        self.supabase.storage.from_(self.bucket).upload(
            file=file_data, 
            path=name, 
            file_options=file_options
        )
        return name

    def url(self, name):
        if not name:
            return ""
        # Construcción directa y segura de la URL pública de Supabase
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket}/{name}"

    def exists(self, name):
        return False
        
    def delete(self, name):
        self.supabase.storage.from_(self.bucket).remove([name])