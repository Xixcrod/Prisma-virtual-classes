from django.shortcuts import render
from django.http import HttpResponse
from .utils import solicitudes

# Create your views here.
def curso(request):
    return HttpResponse("Curso profesor")

def aceptar_rechazar_solicitud(request):
    context = solicitudes.panel_solicitudes(request)
    return render(request, 'aceptar_rechazar_solicitud.html', context)