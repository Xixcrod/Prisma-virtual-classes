from django.urls import path
from . import views

urlpatterns = [
    path(
        "curso/<uuid:id_curso>/",
        views.CoursesDetails.as_view(),
        name="detalles-cursos",
    ),
    path("tema/<uuid:id_tema>/", views.ThemesDetails.as_view(), name="detalles-temas"),
    path(
        "video/<uuid:id_video>/", views.VideoDetails.as_view(), name="detalles-videos"
    ),
]
