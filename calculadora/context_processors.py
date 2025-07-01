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
            # Traducciones para index
            'index_title': 'Métodos Numéricos',
            'fixed_point_desc': 'Método iterativo para encontrar raíces de ecuaciones',
            'cubic_spline_desc': 'Interpolación por splines cúbicos',
            'premium_store': 'Tienda Premium',
            'premium_store_desc': 'Desbloquea funciones avanzadas',
            'docs_cubic': 'Docs Trazadores',
            'docs_cubic_desc': 'Documentación técnica del método',
            'docs_fixed_point': 'Docs Punto Fijo',
            'docs_fixed_point_desc': 'Teoría y ejemplos del método',
            'user_registration': 'Registro de Usuario',
            'user_registration_desc': 'Crea una cuenta con tus datos y foto de perfil',
            'my_profile': 'Mi Perfil',
            'my_profile_desc': 'Consulta y gestiona tus datos personales',
            'edit_profile': 'Editar Perfil',
            'edit_profile_desc': 'Actualiza tu información y fotografía',
            'project_credits': 'Créditos del Proyecto',
            'project_credits_desc': 'Conoce a los desarrolladores y sus roles',
            'simplex_method': 'Método Simplex',
            'simplex_method_desc': 'Optimización lineal usando el método simplex',
            'docs_simplex': 'Docs Método Simplex',
            'docs_simplex_desc': 'Documentación técnica del método',
            'docs_big_m': 'Docs Método de la M',
            'docs_big_m_desc': 'Documentación técnica del método',
            'docs_graphic': 'Docs Método Gráfico',
            'docs_graphic_desc': 'Documentación técnica del método',
            'graphic_method_nav': 'Método Gráfico',
            'big_m_method': 'Método de la Gran M',
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
            # Traducciones para index
            'index_title': 'Numerical Methods',
            'fixed_point_desc': 'Iterative method to find equation roots',
            'cubic_spline_desc': 'Cubic spline interpolation',
            'premium_store': 'Premium Store',
            'premium_store_desc': 'Unlock advanced features',
            'docs_cubic': 'Spline Docs',
            'docs_cubic_desc': 'Technical documentation of the method',
            'docs_fixed_point': 'Fixed Point Docs',
            'docs_fixed_point_desc': 'Theory and examples of the method',
            'user_registration': 'User Registration',
            'user_registration_desc': 'Create an account with your data and profile picture',
            'my_profile': 'My Profile',
            'my_profile_desc': 'View and manage your personal data',
            'edit_profile': 'Edit Profile',
            'edit_profile_desc': 'Update your information and photograph',
            'project_credits': 'Project Credits',
            'project_credits_desc': 'Meet the developers and their roles',
            'simplex_method': 'Simplex Method',
            'simplex_method_desc': 'Linear optimization using the simplex method',
            'docs_simplex': 'Simplex Method Docs',
            'docs_simplex_desc': 'Technical documentation of the method',
            'docs_big_m': 'Big M Method Docs',
            'docs_big_m_desc': 'Technical documentation of the method',
            'docs_graphic': 'Graphic Method Docs',
            'docs_graphic_desc': 'Technical documentation of the method',
            'graphic_method_nav': 'Graphic Method',
            'big_m_method': 'Big M Method',
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
