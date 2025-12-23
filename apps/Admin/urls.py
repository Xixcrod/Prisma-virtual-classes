from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin, name="dashboard"),
    path('registrar-usuario/', views.registrar_usuario, name="registrar_usuario"),
]