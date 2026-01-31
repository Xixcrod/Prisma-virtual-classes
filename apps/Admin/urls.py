from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin, name="dashboard"),
    path('registrar-usuario/', views.registrar_usuario, name="registrar_usuario"),
    path('profesores/', views.lista_profesores, name="lista_profesores"),
    
    # Rutas que usan UUID para los profesores
    path('asignar-materias/<uuid:profesor_id>/', views.gestionar_materias_profesor, name="gestionar_materias_profesor"),
    path('eliminar-profesor/<uuid:profesor_id>/', views.eliminar_profesor, name="eliminar_profesor"),
    
    path('registrar-carrera-materia/', views.registrar_carrera_materia, name="registrar_carrera_materia"),
    path('editar-carrera/<uuid:carrera_id>/', views.editar_carrera, name="editar_carrera"),
    path('editar-materia/<uuid:materia_id>/', views.editar_materia, name="editar_materia"),
    path('eliminar-materia/<uuid:materia_id>/', views.eliminar_materia, name="eliminar_materia"),
    path('eliminar-carrera/<uuid:carrera_id>/', views.eliminar_carrera, name="eliminar_carrera"),
    path('obtener-materias/<uuid:carrera_id>/<int:semestre>/', views.obtener_materias_por_carrera, name="obtener_materias"),

    # Rutas para Cursos
    path('catalogo/', views.catalogo_cursos_admin, name="catalogo"),
    path('eliminar-curso/<uuid:curso_id>/', views.eliminar_curso, name="eliminar_curso"),
    path('mis-cursos/', views.mis_cursos, name="admin_mis_cursos"),
]