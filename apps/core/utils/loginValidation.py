from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.urls import reverse
from apps.core.decorators import login_excluded
"""
    Esta funcion verifica la existencia del usuario cuyas credenciales recibe desde el método POST
    y de existir, loguea al usuario y lo redirecciona al dashboard.
"""

# @login_excluded('dashboard')
def loginProcess(request):
    if request.method == 'POST':
        # Obtenemos los datos. 
        cedula_input = request.POST.get('username')
        password = request.POST.get('password')

        if not cedula_input or not password:
            return render(request, 'login.html', {'error': "Por favor, ingresa cédula y contraseña"})

        if len(cedula_input) < 7 or len(cedula_input) > 8:
            return render(request, 'login.html', {'error': "Cédula inválida."})

        # Autenticación:
        user = authenticate(request, username=cedula_input, password=password)

        if user is not None:
            login(request, user)

            # --- LÓGICA DE REDIRECCIÓN POR ROL ---

            # 1. Si es Superusuario / Administrador
            if user.is_superuser or user.is_staff:
                return redirect('dashboard')

            # 2. Si es Profesor (Verificamos la relación OneToOne)
            elif hasattr(user, 'profesor'):
                return redirect('adminp')

            # 3. Si es Estudiante
            elif hasattr(user, 'estudiante'):
                return redirect('dashboard')

            # 4. Por defecto (si es un usuario sin rol específico)
            else:
                return render(request, 'login.html', {'error': "Tú usuario no tiene un rol asignado."})


        else:
            return render(request, 'login.html', {'error': "Cédula o contraseña incorrecta"})

    else:
        return redirect('login')
