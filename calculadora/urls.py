from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import historial_gran_m

urlpatterns = [

    #RUTA DE M 
    path('gran_m/', views.metodo_gran_m, name='gran_m'),
    path('exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('exportar/excel/', views.exportar_excel, name='exportar_excel'),
    path('exportar/word/', views.exportar_word, name='exportar_word'),
    path('historial/gran_m/', historial_gran_m, name='historial_gran_m'),
    path('gran_m/editar/<int:pk>/', views.editar_gran_m, name='editar_gran_m'),

    path('', views.login_view, name='login'),
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
    path('tienda/', views.tienda, name='tienda'),

    path('simplex/historial/', views.simplex_historial, name='simplex_historial'),
    path('simplex/cargar/<int:historial_id>/', views.cargar_simplex_historial, name='cargar_simplex_historial'),
    path('simplex/pdf/<int:historial_id>/', views.exportar_simplex_pdf, name='exportar_simplex_pdf'),

    path('documentacionSimplex/',views.documentacion_simplex, name='documentacionSimplex'),
    path('documentacionM', views.documentacion_m, name='documentacionM'),
    path('documentacionGrafico', views.documentacion_grafico, name='documentacionGrafico'),

    # Punto Fijo
    path('punto/', views.punto_fijo_view, name='puntoFijo'),
    path('punto/historial/', views.historial_punto_fijo, name='historialPuntoFijo'),
    path('punto/historial/pdf/<int:id>/', views.punto_fijo_pdf, name='pdfPuntoFijo'),
    path('punto/repetir/<int:id>/', views.repetir_punto_fijo, name='repetirPuntoFijo'),

    # Trazador Cúbico
    path('trazador/', views.spline_view, name='trazador'),
    path('historial/', views.historial_view, name='historial'),
    path('trazador/historial/pdf/<int:id>/', views.trazador_pdf, name='pdfTrazador'),
    path('trazador/repetir/<int:id>/', views.repetir_trazador, name='repetirTrazador'),

    # Documentación
    path('documentacionTrazador/', views.documentacion_trazadores, name='documentacionTrazador'),
    path('documentacionPuntoFijo/', views.documentacion_punto, name='documentacionPuntoFijo'),

    # Método Gráfico
    path('metodo-grafico/', views.metodo_grafico, name='metodoGrafico'),
    path('metodo-grafico/historial/', views.historial_metodo_grafico, name='historialMetodoGrafico'),
    path('metodo-grafico/historial/pdf/<int:id>/', views.metodo_grafico_pdf, name='pdfMetodoGrafico'),
    path('metodo-grafico/historial/repetir/<int:id>/', views.repetir_metodo_grafico, name='repetirMetodoGrafico'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
