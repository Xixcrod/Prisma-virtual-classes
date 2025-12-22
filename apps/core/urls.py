from django.urls import path
from . import views
from .utils import loginValidation

urlpatterns = [
    path('', views.signin, name="login"), #Ruta principal de la aplicación que lleva al login
    path('login-process/', loginValidation.loginProcess, name="login-process"), #Ruta para procesar el inicio de sesión
    path('logout/', views.signout, name="logout"), #Ruta para cerrar sesión
    path('adminprueba/', views.adminp, name="adminp"), #Ruta de prueba para el admin
]