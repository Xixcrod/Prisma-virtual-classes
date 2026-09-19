import mimetypes
from storages.backends.s3boto3 import S3Boto3Storage

class SupabaseMediaStorage(S3Boto3Storage):
    """
    Custom Storage para Supabase que fuerza la detección correcta
    del ContentType (MIME type) antes de subir archivos.
    """
    def _get_write_parameters(self, name, content=None):
        params = super()._get_write_parameters(name, content)
        
        # Detectar el tipo MIME según la extensión del archivo (ej. .mp4 -> video/mp4)
        content_type, _ = mimetypes.guess_type(name)
        
        if content_type:
            params['ContentType'] = content_type
        elif hasattr(content, 'content_type') and content.content_type:
            params['ContentType'] = content.content_type
        
        return params