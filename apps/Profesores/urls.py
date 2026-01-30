from django.urls import path
from . import views
from .utils import solicitudes

urlpatterns = [
    path('', views.curso, name="curso"),
    path('aceptar_rechazar_solicitud/', views.aceptar_rechazar_solicitud, name="aceptar_rechazar_solicitud"),
    path('gestionar_estatus/<uuid:acceso_id>/<str:nuevo_estado>/', solicitudes.gestionar_estatus, name="gestionar_estatus"),
]