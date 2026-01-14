from django.urls import path
from . import views
from apps.core.models import Curso, Tema, Video

urlpatterns = [
    path(
        "curso/<uuid:id_curso>/",
        views.CoursesDetails.as_view(),
        name="detalles-cursos",
    ),
    path(
        "curso/<uuid:id_curso>/editar-imagen",
        views.UpdateCourseImage.as_view(),
        name="editar-imagen-cursos",
    ),
    path("tema/<uuid:id_tema>/", views.ThemesDetails.as_view(), name="detalles-temas"),
    path(
        "video/<uuid:id_video>/", views.VideoDetails.as_view(), name="detalles-videos"
    ),
    path(
        "archivos-media/<str:alias_modelo>/<uuid:id_objeto>/",
        views.AccessToMediaFiles.as_view(),
        name="consumir-media-files",
    ),
]
