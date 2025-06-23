from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login' ),
    path('sign_in', views.inicio_sesion, name='inicio_sesion'),
    path('sign_up', views.registro, name='registro'),
]