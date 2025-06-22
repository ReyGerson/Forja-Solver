from django.urls import path
from . import views

from django.conf import settings
from django.contrib.staticfiles.urls import static

urlpatterns = [
    path('', views.punto_fijo_view, name='puntoFijo'),
    path('trazador', views.spline_view, name='trazador'),
    path('historial/', views.historial_view, name='historial'),
    path('punto/historial/', views.historial_punto_fijo, name='historialPuntoFijo'),


    path('punto/historial/pdf/<int:id>/', views.punto_fijo_pdf, name='pdfPuntoFijo'),
    path('punto/repetir/<int:id>/', views.repetir_punto_fijo, name='repetirPuntoFijo'),


    path('trazador/historial/pdf/<int:id>/', views.trazador_pdf, name='pdfTrazador'),
    path('trazador/repetir/<int:id>/', views.repetir_trazador, name='repetirTrazador'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)