from django.urls import path
from . import views
from .utils import loginValidation, recover_password

urlpatterns = [
    path('', views.signin, name="login"), #Ruta principal de la aplicación que lleva al login
    path('login-process/', loginValidation.loginProcess, name="login-process"), #Ruta para procesar el inicio de sesión
    path('logout/', views.signout, name="logout"), #Ruta para cerrar sesión
    path('adminprueba/', views.adminp, name="adminp"), #Ruta de prueba para el admin
    path('recuperar_contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),
    path('processing_password/', recover_password.recovering_password, name="processing_password"), #Ruta para procesar la solicitud de recuperación de contraseña
]