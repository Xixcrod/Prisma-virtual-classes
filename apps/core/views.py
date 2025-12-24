from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from apps.core.decorators.login_excluded import login_excluded
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# Create your views here.

# Esta vista maneja el inicio de sesión de los usuarios.
@login_excluded
def signin(request):
    return render(request, 'login.html', {'success': False})

# Esta vista maneja el cierre de sesión de los usuarios.
@login_required
def signout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'), {'success': False})

@login_excluded
def recuperar_contrasena(request):
    return render(request, 'recuperar_contrasena.html')

#Ruta de prueba para el admin
def adminp(request):
    return render(request, 'adminp.html')