"""
Vistas principales de la aplicación Forja-Solver.
Incluye lógica para métodos numéricos (Punto Fijo, Trazador Cúbico), gestión de usuarios, historial, premium y generación de PDFs.
"""
from django.shortcuts import render, redirect
import json
from django.http import HttpResponse
from .forms import PuntoFijoForm, SplineInputForm, RegistroUsuarioForm, EditarPerfilForm
from .models import SplineHistory, PuntoFijoHistorial
from .utils import parse_points, natural_cubic_spline
import numexpr as ne
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .user_profile import UserProfile
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
import re
from typing import List, Tuple
import pandas as pd
import pandas as pd

@login_required
def punto_fijo_view(request):
    """
    Vista principal para el método de Punto Fijo.
    Permite calcular la raíz de una función usando un despeje g(x).
    Guarda el historial y muestra la gráfica solo a usuarios premium.
    """
    resultado = []
    solucion = None
    error = None
    comprobacion = None
    formula_funcion = ""
    formula_despeje = ""

    if request.method == 'POST':
        form = PuntoFijoForm(request.POST)
        if form.is_valid():
            fx_input = form.cleaned_data['funcion']
            gx_input = form.cleaned_data['despeje']
            x0 = form.cleaned_data['valor_inicial']
            decimales = form.cleaned_data['decimales']
            tolerancia = form.cleaned_data['tolerancia']

            formula_funcion = fx_input
            formula_despeje = gx_input

            iteraciones = []
            i = 0
            ea = 100
            x1 = None

            while True:
                i += 1
                try:
                    x1 = float(ne.evaluate(gx_input, local_dict={'x': x0}))
                    fxi = float(ne.evaluate(fx_input, local_dict={'x': x1}))

                    if i > 1:
                        ea = abs((x1 - x0) / x1) * 100
                    else:
                        ea = None

                    valor_x0 = round(x0, decimales)
                    valor_x1 = round(x1, decimales)
                    detalle = f"x{i} = {gx_input.replace('x', str(valor_x0))} = {valor_x1}"
                    if ea is not None:
                        error_detalle = f"ε{i} = |({valor_x1} - {valor_x0}) / {valor_x1}| × 100% = {round(ea, 2)}%"
                    else:
                        error_detalle = "ε1 = -"

                    iteraciones.append({
                        'iteracion': i,
                        'detalle': detalle,
                        'error_detalle': error_detalle,
                        'x': valor_x1,
                        'error': round(ea, 2) if ea is not None else '-',
                    })

                    if ea is not None and ea <= tolerancia:
                        break

                    x0 = x1

                except Exception as e:
                    form.add_error(None, f"Error al evaluar la función o el despeje: {e}")
                    iteraciones = []
                    x1 = None
                    break

            if iteraciones and x1 is not None:
                solucion = round(x1, decimales)
                error = round(ea, 5)
                try:
                    comprobacion = round(float(ne.evaluate(fx_input, local_dict={'x': solucion})), 8)
                except:
                    comprobacion = "Error al comprobar"

                resultado = iteraciones

                # Guardar historial
                iteraciones_texto = "\n".join(
                    f"Iter {r['iteracion']}: x={r['x']} | Error={r['error']}%" for r in resultado
                )

                PuntoFijoHistorial.objects.create(
                    user=request.user,
                    funcion=fx_input,
                    despeje=gx_input,
                    valor_inicial=form.cleaned_data['valor_inicial'],
                    tolerancia=tolerancia,
                    decimales=decimales,
                    solucion=solucion,
                    error=error,
                    comprobacion=str(comprobacion),
                    iteraciones=iteraciones_texto,
                    funcion_latex=request.POST.get('funcion_latex', ''),
                    despeje_latex=request.POST.get('despeje_latex', ''),
                )

    else:
        # Set initial values for the form so form.initial always has the keys
        form = PuntoFijoForm(initial={
            'valor_inicial': 1,
            'tolerancia': 0.001,
            'decimales': 6,
        })

    # --- Fix: ensure form.data always has the needed keys for template ---
    # Use try/except to avoid errors if form.data is not a dict (e.g., QueryDict)
    try:
        if 'valor_inicial' not in form.data or not form.data['valor_inicial']:
            form.data = form.data.copy()
            form.data['valor_inicial'] = form.initial.get('valor_inicial', 1)
        if 'tolerancia' not in form.data or not form.data['tolerancia']:
            form.data['tolerancia'] = form.initial.get('tolerancia', 0.001)
        if 'decimales' not in form.data or not form.data['decimales']:
            form.data['decimales'] = form.initial.get('decimales', 6)
    except Exception:
        pass
    # --- end fix ---

    # --- Definir valores seguros para los campos del formulario ---
    valor_inicial = form.data.get('valor_inicial') or form.initial.get('valor_inicial', 1)
    tolerancia = form.data.get('tolerancia') or form.initial.get('tolerancia', 0.001)
    decimales = form.data.get('decimales') or form.initial.get('decimales', 6)
    # --- end fix ---

    # --- Datos para gráfica Punto Fijo ---
    is_premium = hasattr(request.user, 'userprofile') and request.user.userprofile.is_premium if request.user.is_authenticated else False
    grafica_punto_fijo = None
    if resultado and is_premium:
        grafica_punto_fijo = {
            'x': [r['iteracion'] for r in resultado],
            'y': [r['x'] for r in resultado],
            'error': [r['error'] for r in resultado],
        }
    # --- end datos gráfica ---

    print("POST recibido:", request.POST)
    return render(request, 'punto_fijo/puntoFijo.html', {
        'form': form,
        'resultado': resultado,
        'solucion': solucion,
        'error': error,
        'comprobacion': comprobacion,
        'fx': formula_funcion,
        'gx': formula_despeje,
        'fx_latex': request.POST.get('funcion_latex', ''), 
        'gx_latex': request.POST.get('despeje_latex', ''),
        'is_premium': is_premium,
        'valor_inicial_val': valor_inicial,
        'tolerancia_val': tolerancia,
        'decimales_val': decimales,
        'grafica_punto_fijo': grafica_punto_fijo,
    })

@login_required
def spline_view(request):
    """
    Vista principal para el método de Trazador Cúbico.
    Permite interpolar un valor usando splines cúbicos naturales.
    Guarda el historial y muestra la gráfica solo a usuarios premium.
    """
    result = None
    if request.method == 'POST':
        form = SplineInputForm(request.POST)
        if form.is_valid():
            points_str = form.cleaned_data['points']
            x_val = form.cleaned_data['x_value']
            try:
                points = parse_points(points_str)
                result = natural_cubic_spline(points, x_val)

                # Guardar en base de datos
                SplineHistory.objects.create(
                    user=request.user,         
                    puntos=points_str,
                    x_valor=x_val,
                    resultado=result['resultado'],
                    razonamiento=result['razonamiento'],
                    polinomio_usado=result['polinomio_usado']
                )
            except Exception as e:
                form.add_error(None, f"Error en los datos: {e}")
    else:
        form = SplineInputForm()

    # --- Datos para gráfica Trazador Cúbico ---
    is_premium = hasattr(request.user, 'userprofile') and request.user.userprofile.is_premium if request.user.is_authenticated else False
    grafica_trazador = None
    if result and 'tabla_hm' in result and is_premium:
        try:
            # Extraer puntos para graficar la curva y los puntos originales
            puntos = []
            if hasattr(form, 'cleaned_data') and 'points' in form.cleaned_data:
                puntos = parse_points(form.cleaned_data['points'])
            elif hasattr(form, 'initial') and 'points' in form.initial:
                puntos = parse_points(form.initial['points'])
            x_vals = [p[0] for p in puntos]
            y_vals = [p[1] for p in puntos]
            # Si hay polinomios, graficar la curva
            polinomios = result.get('polinomios', [])
            grafica_trazador = {
                'x': x_vals,
                'y': y_vals,
                'polinomios': polinomios,
                'x_query': result.get('x_query'),
                'y_query': result.get('resultado'),
            }
        except Exception:
            grafica_trazador = None
    # --- end datos gráfica ---

    return render(request, 'trazador_cubico/trazadorCubico.html', {
        'form': form,
        'result': result,
        'is_premium': is_premium,
        'grafica_trazador': grafica_trazador,
    })

@login_required
def historial_view(request):
    """
    Muestra el historial de cálculos de Trazador Cúbico del usuario.
    """
    historial = SplineHistory.objects.filter(user=request.user).order_by('-fecha_creacion')
    return render(request, 'trazador_cubico/historialTrazador.html', {'historial': historial})

@login_required
def historial_punto_fijo(request):
    """
    Muestra el historial de cálculos de Punto Fijo del usuario.
    """
    historial = PuntoFijoHistorial.objects.filter(user=request.user).order_by('-fecha')
    return render(request, 'punto_fijo/historial_punto_fijo.html', {'historial': historial})

@login_required
def punto_fijo_pdf(request, id):
    """
    Genera un PDF con el historial de un cálculo de Punto Fijo.
    """
    obj = PuntoFijoHistorial.objects.get(id=id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="punto_fijo_{obj.id}.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12)
    y = 800

    p.drawString(50, y, f"PUNTO FIJO - Historial ID {obj.id}")
    y -= 30
    p.drawString(50, y, f"F(x): {obj.funcion}")
    y -= 20
    p.drawString(50, y, f"g(x): {obj.despeje}")
    y -= 20
    p.drawString(50, y, f"x₀: {obj.valor_inicial}, Tolerancia: {obj.tolerancia}, Decimales: {obj.decimales}")
    y -= 20
    p.drawString(50, y, f"Solución: x = {obj.solucion}, Error = {obj.error}%")
    y -= 20
    p.drawString(50, y, f"Comprobación: F(x) = {obj.comprobacion}")
    y -= 40

    p.drawString(50, y, "Iteraciones:")
    y -= 20
    for linea in obj.iteraciones.split('\n'):
        if y < 50:
            p.showPage()
            y = 800
        p.drawString(60, y, linea)
        y -= 20

    p.showPage()
    p.save()
    return response

@login_required
def repetir_punto_fijo(request, id):
    """
    Permite repetir un cálculo de Punto Fijo guardado en el historial.
    Solo muestra el proceso completo a usuarios premium.
    """
    obj = get_object_or_404(PuntoFijoHistorial, id=id)

    form = PuntoFijoForm(initial={
        'funcion': obj.funcion,
        'despeje': obj.despeje,
        'valor_inicial': obj.valor_inicial,
        'tolerancia': obj.tolerancia,
        'decimales': obj.decimales,
    })

    resultado = []
    solucion = None
    error = None
    comprobacion = None

    try:
        fx_input = obj.funcion
        gx_input = obj.despeje
        x0 = obj.valor_inicial
        tolerancia = obj.tolerancia
        decimales = obj.decimales

        i = 0
        ea = 100
        x1 = None

        while True:
            i += 1
            x1 = float(ne.evaluate(gx_input, local_dict={'x': x0}))
            fxi = float(ne.evaluate(fx_input, local_dict={'x': x1}))

            if i > 1:
                ea = abs((x1 - x0) / x1) * 100
            else:
                ea = None

            valor_x0 = round(x0, decimales)
            valor_x1 = round(x1, decimales)
            detalle = f"x{i} = {gx_input.replace('x', str(valor_x0))} = {valor_x1}"
            if ea is not None:
                error_detalle = f"ε{i} = |({valor_x1} - {valor_x0}) / {valor_x1}| × 100% = {round(ea, 2)}%"
            else:
                error_detalle = "ε1 = -"

            resultado.append({
                'iteracion': i,
                'detalle': detalle,
                'error_detalle': error_detalle,
                'x': valor_x1,
                'error': round(ea, 2) if ea is not None else '-',
            })

            if ea is not None and ea <= tolerancia:
                break

            x0 = x1

        if resultado and x1 is not None:
            solucion = round(x1, decimales)
            error = round(ea, 5)
            try:
                comprobacion = round(float(ne.evaluate(fx_input, local_dict={'x': solucion})), 8)
            except:
                comprobacion = "Error al comprobar"

    except Exception as e:
        form.add_error(None, f"Error al evaluar la función o el despeje: {e}")

    # --- Datos para gráfica Punto Fijo en modo repetir ---
    is_premium = hasattr(request.user, 'userprofile') and request.user.userprofile.is_premium if request.user.is_authenticated else False
    if resultado and is_premium:
        grafica_punto_fijo = {
            'x': [r['iteracion'] for r in resultado],
            'y': [r['x'] for r in resultado],
            'error': [r['error'] for r in resultado],
        }
    else:
        grafica_punto_fijo = None
    # --- end datos gráfica ---

    return render(request, 'punto_fijo/puntoFijo.html', {
        'form': form,
        # Mostrar solo el resultado mínimo para no premium, igual que en trazador cubico
        'resultado': resultado if is_premium else None,
        'solucion': solucion,
        'error': error,
        'comprobacion': comprobacion,
        'fx': obj.funcion,
        'gx': obj.despeje,
        'fx_latex': obj.funcion_latex or obj.funcion,
        'gx_latex': obj.despeje_latex or obj.despeje,
        'is_premium': is_premium,
        'valor_inicial_val': obj.valor_inicial,
        'tolerancia_val': obj.tolerancia,
        'decimales_val': obj.decimales,
        'modo_repetir': True,
        'mostrar_resultado_minimo': True,  # Forzar mostrar el bloque de resultado mínimo
        'grafica_punto_fijo': grafica_punto_fijo,
    })


@login_required
def trazador_pdf(request, id):
    """
    Genera un PDF con el historial de un cálculo de Trazador Cúbico.
    """
    obj = SplineHistory.objects.get(id=id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="trazador_{obj.id}.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12)
    y = 800

    p.drawString(50, y, f"TRAZADOR CÚBICO - Historial ID {obj.id}")
    y -= 30
    p.drawString(50, y, f"Puntos: {obj.puntos}")
    y -= 20
    p.drawString(50, y, f"x evaluado: {obj.x_valor}")
    y -= 20
    p.drawString(50, y, f"Resultado: {obj.resultado}")
    y -= 40

    p.drawString(50, y, "Polinomio usado:")
    y -= 20
    for linea in obj.polinomio_usado.split('\n'):
        if y < 50:
            p.showPage()
            y = 800
        p.drawString(60, y, linea)
        y -= 20

    y -= 20
    p.drawString(50, y, "Razonamiento:")
    y -= 20
    for linea in obj.razonamiento.split('\n'):
        if y < 50:
            p.showPage()
            y = 800
        p.drawString(60, y, linea)
        y -= 20

    p.showPage()
    p.save()
    return response

@login_required
def repetir_trazador(request, id):
    """
    Permite repetir un cálculo de Trazador Cúbico guardado en el historial.
    Solo muestra el proceso completo a usuarios premium.
    """
    obj = get_object_or_404(SplineHistory, id=id)

    form = SplineInputForm(initial={
        'points': obj.puntos,
        'x_value': obj.x_valor
    })

    result = None
    grafica_trazador = None
    try:
        points = parse_points(obj.puntos)
        result = natural_cubic_spline(points, obj.x_valor)
        # --- Datos para gráfica Trazador Cúbico en modo repetir ---
        is_premium = hasattr(request.user, 'userprofile') and request.user.userprofile.is_premium if request.user.is_authenticated else False
        if result and 'tabla_hm' in result and is_premium:
            x_vals = [p[0] for p in points]
            y_vals = [p[1] for p in points]
            polinomios = result.get('polinomios', [])
            grafica_trazador = {
                'x': x_vals,
                'y': y_vals,
                'polinomios': polinomios,
                'x_query': result.get('x_query'),
                'y_query': result.get('resultado'),
            }
        # Si no es premium, no se muestra gráfica
        # --- end datos gráfica ---
    except Exception as e:
        form.add_error(None, f"Error en los datos: {e}")
        grafica_trazador = None

    is_premium = hasattr(request.user, 'userprofile') and request.user.userprofile.is_premium if request.user.is_authenticated else False
    return render(request, 'trazador_cubico/trazadorCubico.html', {
        'form': form,
        'result': result if is_premium else {
            'razonamiento': result['razonamiento'] if result else '',
            'polinomio_usado': result['polinomio_usado'] if result else '',
            'x_query': result['x_query'] if result and 'x_query' in result and result['x_query'] not in [None, ''] else None,
            'resultado': result['resultado'] if result and 'resultado' in result and result['resultado'] not in [None, ''] else None,
        },
        'is_premium': is_premium,
        'modo_repetir': True,
        'grafica_trazador': grafica_trazador,
    })


from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout


# Create your views here.


def login_view(request):
    """Renderiza la página de login simple."""
    return render(request, 'paginas/login.html')

def inicio_sesion(request):
    """Procesa el inicio de sesión de usuario."""
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
    """Registro de usuario básico (no recomendado, usar registro_usuario)."""
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

def cerrar_sesion(request):
    """Cierra la sesión del usuario actual."""
    logout(request)
    return redirect('login') 

def index(request):
    """Página principal de la aplicación."""
    return render(request,'paginas/index.html') 

def tienda(request):
    """Página de compra de premium."""
    is_premium = False
    if request.user.is_authenticated:
        try:
            is_premium = request.user.userprofile.is_premium
        except Exception:
            is_premium = False
    return render(request,'paginas/tienda.html', {'is_premium': is_premium})

def documentacion_trazadores(request):
    """Documentación del método de Trazador Cúbico."""
    return render(request, 'trazador_cubico/documentacion_trazador.html')

def documentacion_punto(request):
    """Documentación del método de Punto Fijo."""
    return render(request, 'punto_fijo/documentacion_puntoFijo.html')

@login_required
def comprar_premium(request):
    """Convierte al usuario en premium."""
    profile = UserProfile.objects.get(user=request.user)
    if not profile.is_premium:
        profile.is_premium = True
        profile.save()
    return redirect('tienda')

def registro_usuario(request):
    """Registro de usuario extendido con perfil personalizado."""
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'paginas/registro_usuario.html', {'form': form})

@login_required
def perfil_usuario(request):
    """Muestra el perfil del usuario. Redirige a edición si faltan datos."""
    profile = request.user.userprofile
    # Si algún campo obligatorio está vacío, redirigir a editar perfil
    if not profile.nombre_completo or not profile.carrera or not profile.carnet or not profile.ciclo:
        return redirect('editar_perfil')
    return render(request, 'paginas/perfil_usuario.html', {'profile': profile})

@login_required
def editar_perfil(request):
    """Permite editar los datos del perfil de usuario."""
    profile = request.user.userprofile
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('perfil_usuario')
    else:
        form = EditarPerfilForm(instance=profile)
    return render(request, 'paginas/editar_perfil.html', {'form': form})

def creditos(request):
    """Muestra los créditos del proyecto y el equipo de desarrollo."""
    integrantes = [
        {
            'nombre': 'Nombre 1',
            'rol': 'Diseño de interfaz, backend, métodos',
        },
        {
            'nombre': 'Nombre 2',
            'rol': 'Base de datos, seguridad, pruebas',
        },
        # Agrega más integrantes y roles aquí
    ]
    return render(request, 'paginas/creditos.html', {'integrantes': integrantes})

# ==================== MÉTODO SIMPLEX ====================

# Variable global para definir decimales en el simplex
decimal_places = 2

def format_value(value: float) -> str:
    """Formatea un valor flotante con el número de decimales especificado"""
    return f"{value:.{decimal_places}f}"

def parse_latex_to_numbers(funcion_latex, restricciones_latex):
    """
    Convierte las expresiones LaTeX de MathLive a listas numéricas
    """
    try:
        # Parsear función objetivo
        # Ejemplo: "20x_1 + 40x_2" -> [20, 40]
        objetivo = []
        
        # Limpiar la expresión y extraer coeficientes
        funcion_clean = funcion_latex.replace('\\cdot', '*').replace(' ', '')
        
        # Buscar patrones como 20x_1, -15x_2, etc.
        import re
        patron_coef = r'([+-]?\d*)\*?x_\{?(\d+)\}?'
        matches = re.findall(patron_coef, funcion_clean)
        
        # Crear diccionario con coeficientes
        coef_dict = {}
        for coef_str, var_num in matches:
            if coef_str in ['', '+']:
                coef = 1
            elif coef_str == '-':
                coef = -1
            else:
                coef = int(coef_str)
            coef_dict[int(var_num)] = coef
        
        # Crear lista ordenada de coeficientes
        max_var = max(coef_dict.keys()) if coef_dict else 1
        objetivo = [coef_dict.get(i+1, 0) for i in range(max_var)]
        
        # Parsear restricciones
        # Ejemplo: ["2x_1 + 3x_2 \\leq 110", "4x_1 + x_2 \\leq 130"]
        restricciones = []
        
        for restriccion in restricciones_latex:
            # Separar lado izquierdo del derecho
            if '\\leq' in restriccion:
                lado_izq, lado_der = restriccion.split('\\leq')
            elif '\\le' in restriccion:
                lado_izq, lado_der = restriccion.split('\\le')
            elif '≤' in restriccion:
                lado_izq, lado_der = restriccion.split('≤')
            else:
                continue
            
            # Limpiar y parsear lado izquierdo
            lado_izq = lado_izq.replace('\\cdot', '*').replace(' ', '')
            lado_der = lado_der.strip()
            
            # Extraer coeficientes del lado izquierdo
            matches_rest = re.findall(patron_coef, lado_izq)
            coef_rest_dict = {}
            
            for coef_str, var_num in matches_rest:
                if coef_str in ['', '+']:
                    coef = 1
                elif coef_str == '-':
                    coef = -1
                else:
                    coef = int(coef_str)
                coef_rest_dict[int(var_num)] = coef
            
            # Crear fila de restricción [coef_x1, coef_x2, ..., b]
            fila_restriccion = [coef_rest_dict.get(i+1, 0) for i in range(max_var)]
            
            # Agregar término independiente (lado derecho)
            try:
                rhs = float(lado_der)
                fila_restriccion.append(rhs)
                restricciones.append(fila_restriccion)
            except ValueError:
                continue
        
        return objetivo, restricciones
        
    except Exception as e:
        print(f"Error en parsing: {e}")
        # Valores por defecto en caso de error
        return [20, 40], [[2, 3, 110], [4, 1, 130]]

def prepare_initial_table(obj: List[float], constraints: List[List[float]]) -> Tuple[List[List[float]], List[str]]:
    """Prepara la tabla inicial del método simplex"""
    num_vars = len(obj)
    num_constraints = len(constraints)

    matrix = []
    for i, row in enumerate(constraints):
        vars_part = row[:-1]
        rhs = row[-1]
        slack = [0] * num_constraints
        slack[i] = 1
        matrix.append(vars_part + slack + [rhs])

    z_row = [-c for c in obj] + [0] * (num_constraints + 1)
    matrix.append(z_row)

    var_names = [f"x{i+1}" for i in range(num_vars)]
    return matrix, var_names

def generate_simplex_solution(matrix: List[List[float]], var_names: List[str], obj: List[float], constraints: List[List[float]]) -> dict:
    """
    Genera la solución completa del método simplex adaptada para Django
    """
    num_constraints = len(matrix) - 1
    num_vars = len(var_names)

    slack_vars = [f"s{i+1}" for i in range(num_constraints)]
    all_vars = var_names + slack_vars + ["B"] 
    table = pd.DataFrame(matrix, columns=all_vars)

    basis = slack_vars.copy()
    
    # Datos para el template
    resultado = {
        'obj_original': obj,
        'constraints_original': constraints,
        'var_names': var_names,
        'slack_vars': slack_vars,
        'iteraciones': [],
        'solucion_optima': {},
        'valor_z': 0,
        'tabla_inicial': None,
        'modelo_matematico': None,
        'modelo_holgura': None
    }
    
    # Modelo matemático original
    obj_expr = " + ".join(f"{format_value(c)}x_{{{i+1}}}" for i, c in enumerate(obj))
    constraints_expr = []
    for i, row in enumerate(constraints):
        lhs = " + ".join(f"{format_value(val)}x_{{{j+1}}}" for j, val in enumerate(row[:-1]) if val != 0)
        rhs = format_value(row[-1])
        constraints_expr.append(f"{lhs} \\leq {rhs}")
    
    # Función Z igualada a 0 (forma estándar)
    funcion_z_estandar = f"Z - ({obj_expr}) = 0"
    
    resultado['modelo_matematico'] = {
        'funcion_objetivo': f"\\text{{Maximizar }} Z = {obj_expr}",
        'funcion_z_estandar': funcion_z_estandar,
        'restricciones': constraints_expr
    }
    
    # Modelo con variables de holgura
    transformed_expr = []
    for i, row in enumerate(constraints):
        lhs = " + ".join(f"{format_value(val)}x_{{{j+1}}}" for j, val in enumerate(row[:-1]) if val != 0)
        lhs += f" + s_{{{i+1}}}"
        rhs = format_value(row[-1])
        transformed_expr.append(f"{lhs} = {rhs}")
    
    resultado['modelo_holgura'] = transformed_expr
    
    # Tabla inicial
    tabla_inicial_html = generar_tabla_html(table, basis, 0)
    resultado['tabla_inicial'] = tabla_inicial_html

    # Iteraciones del algoritmo simplex
    iteration = 0
    while True:
        # Crear datos de la iteración actual
        iteracion_data = {
            'numero': iteration,
            'tabla_html': generar_tabla_html(table, basis, iteration),
            'es_optima': False,
            'variable_entra': None,
            'variable_sale': None,
            'elemento_pivote': None,
            'operaciones': []
        }
        
        # Verificar si es solución óptima
        last_row = table.iloc[-1, :-1]
        pivot_col_name = last_row.idxmin()
        
        if table.at[len(table) - 1, pivot_col_name] >= 0:
            iteracion_data['es_optima'] = True
            resultado['iteraciones'].append(iteracion_data)
            break

        # Encontrar variable que entra y sale
        ratios = []
        for i in range(len(table) - 1):
            col_val = table.at[i, pivot_col_name]
            if col_val > 0:
                ratios.append(table.at[i, "B"] / col_val) 
            else:
                ratios.append(float('inf'))

        pivot_row = ratios.index(min(ratios))
        pivot_element = table.at[pivot_row, pivot_col_name]

        entering = pivot_col_name
        leaving = basis[pivot_row]
        
        iteracion_data['variable_entra'] = entering
        iteracion_data['variable_sale'] = leaving
        iteracion_data['elemento_pivote'] = format_value(pivot_element)
        
        # Normalización de fila pivote
        operacion_pivote = []
        new_pivot_row = []
        for col in table.columns:
            original_val = table.at[pivot_row, col]
            new_val = original_val / pivot_element
            new_pivot_row.append(new_val)
            operacion_pivote.append({
                'variable': col,
                'operacion': f"{format_value(original_val)} ÷ {format_value(pivot_element)} = {format_value(new_val)}"
            })
        table.iloc[pivot_row] = new_pivot_row
        
        iteracion_data['operaciones'].append({
            'tipo': 'normalizacion',
            'fila': f"F{pivot_row+1}",
            'detalles': operacion_pivote
        })
        
        # Actualización de otras filas
        for i in range(len(table)):
            if i != pivot_row:
                factor = table.at[i, pivot_col_name]
                if factor != 0:
                    operacion_fila = []
                    original_row = table.iloc[i].copy()
                    new_row = []
                    for col in table.columns:
                        old_val = original_row[col]
                        pivot_val = table.at[pivot_row, col]
                        result = old_val - factor * pivot_val
                        new_row.append(result)
                        operacion_fila.append({
                            'variable': col,
                            'operacion': f"{format_value(old_val)} - ({format_value(factor)} × {format_value(pivot_val)}) = {format_value(result)}"
                        })
                    table.iloc[i] = new_row
                    
                    iteracion_data['operaciones'].append({
                        'tipo': 'actualizacion',
                        'fila': f"F{i+1}",
                        'factor': format_value(factor),
                        'detalles': operacion_fila
                    })

        basis[pivot_row] = entering
        resultado['iteraciones'].append(iteracion_data)
        iteration += 1

    # Solución óptima
    solution = {var: 0.0 for var in var_names}
    for i, var in enumerate(basis):
        if var in solution:
            solution[var] = table.at[i, "B"]  

    resultado['solucion_optima'] = solution
    resultado['valor_z'] = table.at[len(table) - 1, "B"] 
    
    return resultado

def generar_tabla_html(table, basis, iteration_num):
    """Genera HTML para una tabla del simplex"""
    html = f'<div class="tabla-iteracion">'
    html += f'<h4>Iteración {iteration_num}</h4>'
    html += '<table class="simplex-table">'
    html += '<thead><tr><th>Base</th>'
    
    for col in table.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'

    for i in range(len(table)):
        html += '<tr>'
        base_name = basis[i] if i < len(basis) else 'Z'
        html += f'<td><strong>{base_name}</strong></td>'
        
        for col in table.columns:
            val = table.at[i, col]
            html += f'<td>{format_value(val)}</td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    
    return html

def simplex(request):
    """Vista principal del método simplex"""
    if request.method == "POST":
        try:
            # Obtener datos del formulario
            funcion_objetivo = request.POST.get("funcion_objetivo", "")
            restricciones_raw = request.POST.get("restricciones", "[]")
            
            # Parsear las restricciones JSON
            restricciones = json.loads(restricciones_raw)
            
            # Convertir de LaTeX a números
            objetivo, constraints = parse_latex_to_numbers(funcion_objetivo, restricciones)
            
            # Preparar tabla inicial
            matrix, var_names = prepare_initial_table(objetivo, constraints)
            
            # Resolver el problema simplex
            resultado = generate_simplex_solution(matrix, var_names, objetivo, constraints)
            
            return render(request, 'simplex/simplex.html', {
                'funcion_objetivo': funcion_objetivo,
                'restricciones': restricciones,
                'resultado': resultado,
                'tiene_solucion': True
            })
            
        except Exception as e:
            print(f"Error en simplex: {e}")
            return render(request, 'simplex/simplex.html', {
                'error': f"Error al procesar los datos: {str(e)}"
            })

    return render(request, 'simplex/simplex.html')
