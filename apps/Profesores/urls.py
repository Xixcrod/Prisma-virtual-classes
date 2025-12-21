from django.urls import path
from . import views

urlpatterns = [
    path('', views.curso, name="curso"),
]