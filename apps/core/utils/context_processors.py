from ..models import Notificacion
from django.utils.timesince import timesince
from django.http import JsonResponse

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
        lista = Notificacion.objects.filter(receptor=request.user).order_by('-fecha_creacion')
        
        # Creamos una lista de diccionarios con la fecha ya procesada
        notificaciones_procesadas = []
        for n in lista[:400]:
            notificaciones_procesadas.append({
                'id': n.id,
                'emisor_nombre': n.emisor.get_full_name(),
                'mensaje': n.mensaje,
                'hace_cuanto': timesince(n.fecha_creacion), # Procesamos aquí
                'leido': n.leido
            })

        return {
            'notificaciones': notificaciones_procesadas,
            'notif_count': lista.filter(leido=False).count()
        }
    return {}

def marcar_notificaciones_leidas(request):
    if request.method == 'POST' and request.user.is_authenticated:
        # Marcamos todas las notificaciones del receptor actual como leídas
        Notificacion.objects.filter(receptor=request.user, leido=False).update(leido=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)