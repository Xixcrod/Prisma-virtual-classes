from django.urls import path
from . import views
from .utils import loginValidation, recover_password
from .utils import context_processors 

urlpatterns = [
    path('', views.signin, name="login"), #Ruta principal de la aplicación que lleva al login
    path('login-process/', loginValidation.loginProcess, name="login-process"), #Ruta para procesar el inicio de sesión
    path('logout/', views.signout, name="logout"), #Ruta para cerrar sesión
    path('dashboardpe/', views.dashboardpe, name="dashboardpe"), #Ruta de dashboard de profesores y estudiantes
    path('recuperar_contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),#Ruta para la página de recuperación de contraseña
    path('processing_password/', recover_password.recovering_password, name="processing_password"), #Ruta para procesar la solicitud de recuperación de contraseña

    path('notificaciones/marcar-leidas/', context_processors.marcar_notificaciones_leidas, name='marcar_leidas'), # Ruta para marcar notificaciones como leídas
]