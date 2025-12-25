from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin, name="dashboard"),
    path('registrar-usuario/', views.registrar_usuario, name="registrar_usuario"),
    path('profesores/', views.lista_profesores, name="lista_profesores"),
    
    # Rutas que usan UUID para los profesores
    path('asignar-materias/<uuid:profesor_id>/', views.gestionar_materias_profesor, name="gestionar_materias_profesor"),
    path('eliminar-profesor/<uuid:profesor_id>/', views.eliminar_profesor, name="eliminar_profesor"),
    
    path('obtener-materias/<uuid:carrera_id>/<int:semestre>/', views.obtener_materias_por_carrera, name="obtener_materias"),
]