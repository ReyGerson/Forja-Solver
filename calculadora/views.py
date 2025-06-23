from django.shortcuts import render, redirect
import json
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login

# Create your views here.
def index(request):
    return render(request, 'paginas/index.html')

def login_view(request):
    return render(request, 'paginas/login.html')

def inicio_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect( 'index')
        else:
            return render(request, "paginas/inicio_sesion.html", {'form': form, 'error': 'credenciales incorrectas'})
    else:
        form = AuthenticationForm()
    return render(request, "paginas/inicio_sesion.html")

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect( 'inicio_sesion')
        else:
            return render(request, "paginas/registro.html", {'form': form, 'error': 'credenciales incorrectas'})
    else:
        form = UserCreationForm()

    return render(request, "paginas/registro.html")