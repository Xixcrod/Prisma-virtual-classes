from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def curso(request):
    return HttpResponse("Curso profesor")