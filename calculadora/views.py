from django.shortcuts import render
from django.http import HttpResponse
from .models import PuntoFijo
from .forms import PuntoFijoForm


# Create your views here.
def puntoFijo(request):
    puntoFijo = PuntoFijo.objects.all()
    return render(request, 'punto_fijo/puntoFijo.html', {'puntoFijos': puntoFijo})

def simplexMax(request):
    return render(request, 'paginas/simplexMax.html')

def login(request):
    return render(request, 'paginas/login.html')