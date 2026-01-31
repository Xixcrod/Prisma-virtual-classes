from haystack import indexes
from apps.core.models import Curso


class CursoIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Índice de búsqueda para el modelo Curso.
    Define los campos que serán indexados y buscables.
    """
    # Campo de texto principal para búsqueda general
    text = indexes.CharField(document=True, use_template=True)
    
    # Campos indexados para búsqueda y filtrado
    materia_nombre = indexes.CharField(model_attr='materia__nombre')
    materia_id = indexes.CharField(model_attr='materia__id')
    
    profesor_nombre_completo = indexes.CharField()
    profesor_id = indexes.CharField(model_attr='profesor__id')
    
    semestre = indexes.IntegerField(model_attr='materia__semestre')
    carrera_nombre = indexes.CharField(model_attr='materia__carrera__nombre')
    carrera_id = indexes.CharField(model_attr='materia__carrera__id')
    
    descripcion = indexes.CharField(model_attr='descripcion')
    fecha_creacion = indexes.DateTimeField(model_attr='fecha_creacion')
    activo = indexes.BooleanField(model_attr='activo')
    
    # Campos adicionales para mostrar en resultados
    imagen_url = indexes.CharField()

    def get_model(self):
        return Curso

    def prepare_profesor_nombre_completo(self, obj):
        # Combina nombre y apellido del profesor
        return f"{obj.profesor.usuario.first_name} {obj.profesor.usuario.last_name}"

    def prepare_imagen_url(self, obj):
        # Retorna la URL de la imagen del curso
        if obj.imagen:
            return obj.imagen.url
        return '/static/img/placeholders/placeholder-images.webp'

    def index_queryset(self, using=None):
        # Define qué objetos se indexarán.
        # Solo indexamos cursos activos con profesores activos.
        return self.get_model().objects.filter(
            activo=True,
            profesor__activo=True
        ).select_related(
            'materia',
            'materia__carrera',
            'profesor',
            'profesor__usuario'
        )