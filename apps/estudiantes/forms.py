from django import forms
from haystack.forms import SearchForm
from apps.core.models import Materia, Profesor, Carrera


class CatalogoSearchForm(SearchForm):
    """
    Formulario personalizado para búsqueda y filtrado de cursos.
    Incluye filtros por semestre, materia y profesor.
    """
    
    # Campo de búsqueda general (opcional)
    q = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-white',
            'placeholder': 'Buscar cursos, materias, profesores...',
            'autocomplete': 'off'
        })
    )
    
    # Filtro por semestre
    semestre = forms.ChoiceField(
        required=False,
        label='Semestre',
        choices=[('', 'Todos los semestres')],
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white'})
    )
    
    # Filtro por materia
    materia = forms.ChoiceField(
        required=False,
        label='Materia',
        choices=[('', 'Todas las materias')],
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white'})
    )
    
    # Filtro por profesor
    profesor = forms.ChoiceField(
        required=False,
        label='Profesor',
        choices=[('', 'Todos los profesores')],
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white'})
    )
    
    # Filtro por carrera (adicional)
    carrera = forms.ChoiceField(
        required=False,
        label='Carrera',
        choices=[('', 'Todas las carreras')],
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white'})
    )
    
    # Ordenamiento
    order_by = forms.ChoiceField(
        required=False,
        label='Ordenar por',
        initial='-fecha_creacion',
        choices=[
            ('-fecha_creacion', 'Más recientes'),
            ('fecha_creacion', 'Más antiguos'),
            ('materia_nombre', 'Materia (A-Z)'),
            ('-materia_nombre', 'Materia (Z-A)'),
            ('semestre', 'Semestre (ascendente)'),
            ('-semestre', 'Semestre (descendente)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white'})
    )

    def __init__(self, *args, **kwargs):
        # Obtener el estudiante actual si se pasa como parámetro
        self.estudiante = kwargs.pop('estudiante', None)
        super().__init__(*args, **kwargs)
        
        # Cargar opciones dinámicas
        self._cargar_opciones_semestre()
        self._cargar_opciones_materia()
        self._cargar_opciones_profesor()
        self._cargar_opciones_carrera()

    def _cargar_opciones_semestre(self):
        """Carga los semestres disponibles basados en las materias"""
        semestres = Materia.objects.values_list('semestre', flat=True).distinct().order_by('semestre')
        choices = [('', 'Todos los semestres')]
        choices.extend([(str(sem), f'Semestre {sem}') for sem in semestres])
        self.fields['semestre'].choices = choices

    def _cargar_opciones_materia(self):
        """Carga las materias disponibles"""
        if self.estudiante:
            # Filtrar materias de la carrera del estudiante
            materias = Materia.objects.filter(
                carrera=self.estudiante.carrera,
                curso__activo=True,
                curso__profesor__activo=True
            ).distinct().order_by('nombre')
        else:
            materias = Materia.objects.filter(
                curso__activo=True,
                curso__profesor__activo=True
            ).distinct().order_by('nombre')
        
        choices = [('', 'Todas las materias')]
        choices.extend([
            (str(materia.id), f'{materia.nombre} - Semestre {materia.semestre}') 
            for materia in materias
        ])
        self.fields['materia'].choices = choices

    def _cargar_opciones_profesor(self):
        """Carga los profesores que tienen cursos activos"""
        profesores = Profesor.objects.filter(
            activo=True,
            curso__activo=True
        ).distinct().select_related('usuario').order_by('usuario__first_name', 'usuario__last_name')
        
        choices = [('', 'Todos los profesores')]
        choices.extend([
            (str(prof.id), f'{prof.usuario.first_name} {prof.usuario.last_name}') 
            for prof in profesores
        ])
        self.fields['profesor'].choices = choices

    def _cargar_opciones_carrera(self):
        """Carga las carreras disponibles"""
        carreras = Carrera.objects.filter(
            materia__curso__activo=True
        ).distinct().order_by('nombre')
        
        choices = [('', 'Todas las carreras')]
        choices.extend([(str(carrera.id), carrera.nombre) for carrera in carreras])
        self.fields['carrera'].choices = choices

    def search(self):
        """
        Ejecuta la búsqueda con los filtros aplicados
        """
        # Si no hay término de búsqueda, obtener todos los resultados
        if not self.is_valid():
            return self.no_query_found()
        
        # Obtener el query inicial (puede estar vacío)
        sqs = self.searchqueryset
        
        # Si hay término de búsqueda, aplicarlo
        if self.cleaned_data.get('q'):
            sqs = sqs.auto_query(self.cleaned_data['q'])
        else:
            # Si no hay búsqueda, traer todos los cursos activos
            sqs = sqs.all()

        # Aplicar filtros
        if self.cleaned_data.get('semestre'):
            sqs = sqs.filter(semestre=int(self.cleaned_data['semestre']))

        if self.cleaned_data.get('materia'):
            sqs = sqs.filter(materia_id=self.cleaned_data['materia'])

        if self.cleaned_data.get('profesor'):
            sqs = sqs.filter(profesor_id=self.cleaned_data['profesor'])

        if self.cleaned_data.get('carrera'):
            sqs = sqs.filter(carrera_nombre__exact=self.cleaned_data['carrera'])

        # Aplicar ordenamiento
        order_by = self.cleaned_data.get('order_by', '-fecha_creacion')
        if order_by:
            sqs = sqs.order_by(order_by)

        # Aplicar filtro por carrera si se seleccionó
        if self.cleaned_data.get('carrera'):
            sqs = sqs.filter(carrera_id=self.cleaned_data['carrera'])


        return sqs

    def no_query_found(self):
        """
        Retorna todos los cursos activos cuando no hay búsqueda específica
        """
        return self.searchqueryset.all()