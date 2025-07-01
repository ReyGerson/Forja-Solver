"""
Context processors para agregar variables globales a todas las plantillas.
"""

def language_context(request):
    """
    Agrega el idioma actual del usuario y las traducciones básicas al contexto de todas las plantillas.
    """
    # Idioma por defecto
    current_language = 'es'
    
    # Si el usuario está autenticado y tiene perfil, usar su idioma preferido
    if request.user.is_authenticated:
        try:
            if hasattr(request.user, 'userprofile'):
                current_language = request.user.userprofile.idioma_preferido
            else:
                # Si no tiene perfil, crearlo con idioma por defecto
                from .user_profile import UserProfile
                profile = UserProfile.objects.create(user=request.user)
                current_language = profile.idioma_preferido
        except Exception as e:
            # En caso de error, usar idioma por defecto
            current_language = 'es'
    
    # Traducciones básicas para el navbar y elementos comunes
    translations = {
        'es': {
            'inicio': 'Inicio',
            'logout': 'Cerrar Sesión',
            'profile': 'Perfil',
            'premium': 'Premium',
            'store': 'Tienda',
            'documentation': 'Documentación',
            'history': 'Historial',
            'spanish': 'Español',
            'english': 'Inglés',
            'language': 'Idioma',
            'methods': 'Métodos',
            'fixed_point': 'Punto Fijo',
            'cubic_spline': 'Trazador Cúbico',
            'simplex': 'Simplex',
            'graphic_method': 'Método Gráfico',
            'gran_m': 'Gran M',
            'welcome': 'Bienvenido',
            'numerical_methods': 'Métodos Numéricos',
            'solver': 'Solucionador',
            'credits': 'Créditos',
            'export_pdf': 'Exportar PDF',
            'calculate': 'Calcular',
            'clear': 'Limpiar',
            'save': 'Guardar',
            'edit': 'Editar',
            'delete': 'Eliminar',
            'close': 'Cerrar',
            'error': 'Error',
            'success': 'Éxito',
            'warning': 'Advertencia',
            'info': 'Información',
            'loading': 'Cargando...',
            'search': 'Buscar',
            'filters': 'Filtros',
            'date': 'Fecha',
            'user': 'Usuario',
            'result': 'Resultado',
            'details': 'Detalles',
            'back': 'Volver',
            'next': 'Siguiente',
            'previous': 'Anterior',
            'page': 'Página',
            'total': 'Total',
            'no_data': 'No hay datos disponibles',
            'confirm': 'Confirmar',
            'cancel': 'Cancelar',
        },
        'en': {
            'inicio': 'Home',
            'logout': 'Logout',
            'profile': 'Profile',
            'premium': 'Premium',
            'store': 'Store',
            'documentation': 'Documentation',
            'history': 'History',
            'spanish': 'Spanish',
            'english': 'English',
            'language': 'Language',
            'methods': 'Methods',
            'fixed_point': 'Fixed Point',
            'cubic_spline': 'Cubic Spline',
            'simplex': 'Simplex',
            'graphic_method': 'Graphic Method',
            'gran_m': 'Big M',
            'welcome': 'Welcome',
            'numerical_methods': 'Numerical Methods',
            'solver': 'Solver',
            'credits': 'Credits',
            'export_pdf': 'Export PDF',
            'calculate': 'Calculate',
            'clear': 'Clear',
            'save': 'Save',
            'edit': 'Edit',
            'delete': 'Delete',
            'close': 'Close',
            'error': 'Error',
            'success': 'Success',
            'warning': 'Warning',
            'info': 'Information',
            'loading': 'Loading...',
            'search': 'Search',
            'filters': 'Filters',
            'date': 'Date',
            'user': 'User',
            'result': 'Result',
            'details': 'Details',
            'back': 'Back',
            'next': 'Next',
            'previous': 'Previous',
            'page': 'Page',
            'total': 'Total',
            'no_data': 'No data available',
            'confirm': 'Confirm',
            'cancel': 'Cancel',
        }
    }
    
    return {
        'current_language': current_language,
        'translations': translations.get(current_language, translations['es']),
        'available_languages': [
            {'code': 'es', 'name': translations[current_language]['spanish']},
            {'code': 'en', 'name': translations[current_language]['english']},
        ]
    }
