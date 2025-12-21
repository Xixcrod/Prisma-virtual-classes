from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def admin(request):
    return HttpResponse("Admin Page")