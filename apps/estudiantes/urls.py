from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path(
        "solicitar-acceso/<uuid:curso_id>",
        views.CreateAccessRequest.as_view(),
        name="solicitar-acceso",
    ),
    path('catalogo/', views.catalogo_cursos, name='catalogo_cursos'),
]
