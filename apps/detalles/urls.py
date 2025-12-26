from django.urls import path
from . import views

urlpatterns = [
    path(
        "curso/<uuid:id_curso>/",
        views.CoursesDetails.as_view(),
        name="detalles-cursos",
    ),
]
