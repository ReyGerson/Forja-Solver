from django.urls import path
from . import views

from django.conf import settings
from django.contrib.staticfiles.urls import static

urlpatterns = [
    path('ss', views.simplexMax, name='simplexMax'),
    path('login', views.login, name='login'),
    path('', views.puntoFijo, name='puntoFijo'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)