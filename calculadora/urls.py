from django.urls import path
from . import views

from django.conf import settings
from django.contrib.staticfiles.urls import static

urlpatterns = [
    path('index/', views.index, name='index'),
    path('punto/', views.punto_fijo_view, name='puntoFijo'),
    path('trazador/', views.spline_view, name='trazador'),
    path('tienda/', views.tienda, name='tienda'),
    path('historial/', views.historial_view, name='historial'),
    path('punto/historial/', views.historial_punto_fijo, name='historialPuntoFijo'),
    path('documentacionTrazador/',views.documentacion_trazadores, name='documentacionTrazador' ),
    path('documentacionPuntoFijo/',views.documentacion_punto, name='documentacionPuntoFijo'),
    path('simplex/',views.simplex, name='simplex'),
    


    path('punto/historial/pdf/<int:id>/', views.punto_fijo_pdf, name='pdfPuntoFijo'),
    path('punto/repetir/<int:id>/', views.repetir_punto_fijo, name='repetirPuntoFijo'),


    path('trazador/historial/pdf/<int:id>/', views.trazador_pdf, name='pdfTrazador'),
    path('trazador/repetir/<int:id>/', views.repetir_trazador, name='repetirTrazador'),


    path('', views.login_view, name='login' ),
    path('sign_in', views.inicio_sesion, name='inicio_sesion'),
    path('sign_up', views.registro, name='registro'),
    path('logout/', views.cerrar_sesion, name='logout'),

    path('comprar_premium/', views.comprar_premium, name='comprar_premium'),

    path('registro_usuario/', views.registro_usuario, name='registro_usuario'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('creditos/', views.creditos, name='creditos'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
