from ..models import Notificacion

def roles_usuario(request):
    """
    Este diccionario estará disponible en todos los templates.
    """
    if request.user.is_authenticated:
        return {
            'es_admin': request.user.is_superuser,
            'es_profesor': hasattr(request.user, 'profesor'),
            'es_estudiante': hasattr(request.user, 'estudiante'),
        }
    # Si el usuario no está logueado, todo es falso
    return {
        'es_admin': False,
        'es_profesor': False,
        'es_estudiante': False,
    }

def notificaciones_context(request):
    if request.user.is_authenticated:
        # Traemos las notificaciones donde el usuario logueado es el receptor
        lista = Notificacion.objects.filter(receptor=request.user).order_by('-fecha_creacion')
        return {
            'notificaciones': lista[:400], # Las últimas 400 para el despliegue
            'notif_count': lista.filter(leido=False).count() # Solo el conteo de no leídas
        }
    return {}