from django.shortcuts import redirect
from django.conf import settings
from functools import wraps

def login_excluded(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            # 1. Intentamos obtener la URL de la página anterior
            previous_url = request.META.get('HTTP_REFERER')
            
            # 2. Si existe la URL previa, lo devolvemos ahí
            if previous_url:
                return redirect(previous_url)
            
            # 3. Si no hay página previa (entró directo al link), 
            # lo enviamos al dashboard o HOME por defecto
            return redirect(settings.LOGIN_REDIRECT_URL or '')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view