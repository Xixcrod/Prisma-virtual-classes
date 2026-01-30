from ..models import Curso, Tema, Video, Estudiante


def obtener_estadisticas_profesor(user):
    # 1. Obtenemos el objeto profesor asociado al usuario logueado
    # Usamos .filter().first() para evitar errores si el usuario no es profesor
    profesor = getattr(user, 'profesor', None)

    if not profesor:
        return {'cursos': 0, 'temas': 0, 'videos': 0}

    # 2. Contamos los cursos del profesor
    total_cursos = Curso.objects.filter(profesor=profesor).count()

    # 3. Contamos los temas asociados a esos cursos
    total_temas = Tema.objects.filter(curso__profesor=profesor).count()

    # 4. Contamos los videos asociados a esos temas
    total_videos = Video.objects.filter(tema__curso__profesor=profesor).count()

    return {
        'total_cursos': total_cursos,
        'total_temas': total_temas,
        'total_videos': total_videos
    }


def obtener_ultimos_contenidos_estudiante(request):
    try:
        estudiante = Estudiante.objects.get(usuario=request.user)

        # --- OBTENER ÚLTIMOS 8 VIDEOS ---
        ultimos_videos = Video.objects.filter(
            # Navegamos: Video -> Tema -> Curso -> Acceso -> Estudiante
            tema__curso__acceso__estudiante=estudiante,
            # IMPORTANTE: Solo cursos donde el acceso esté 'AP' (Aprobado)
            tema__curso__acceso__estado='AP'
            # Orden desc (-fecha) y limitamos a 8
        ).order_by('-fecha_creacion')[:8]

        # --- OBTENER ÚLTIMOS 8 TEMAS ---
        ultimos_temas = Tema.objects.filter(
            # Navegamos: Tema -> Curso -> Acceso -> Estudiante
            curso__acceso__estudiante=estudiante,
            # Filtramos solo aprobados
            curso__acceso__estado='AP'
        ).order_by('-fecha_creacion')[:8]
        return {'ultimos_videos': ultimos_videos, 'ultimos_temas': ultimos_temas}

    except Estudiante.DoesNotExist:
        # Manejo de error si el usuario no es un estudiante
        ultimos_videos = []
        ultimos_temas = []
        return {'ultimos_videos': ultimos_videos, 'ultimos_temas': ultimos_temas}

def obtener_cursos_estudiante(request):
    try:
        # 1. Identificamos al estudiante
        estudiante = Estudiante.objects.get(usuario=request.user)

        # 2. OBTENER CURSOS CON ACCESO APROBADO ('AP')
        # Filtramos Cursos a través del modelo Acceso
        cursos_aprobados = Curso.objects.filter(
            acceso__estudiante=estudiante,
            acceso__estado='AP',
            activo=True
        ).order_by('-fecha_creacion')

        return {
            'cursos_estudiante': cursos_aprobados,
        }

    except (Estudiante.DoesNotExist, TypeError):
        # Manejo si no es estudiante o no está logueado
        return {
            'cursos_estudiante': [],
        }