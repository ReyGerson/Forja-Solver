from django.shortcuts import render, redirect
import json
from django.http import HttpResponse
from .forms import PuntoFijoForm, SplineInputForm
from .models import SplineHistory, PuntoFijoHistorial
from .utils import parse_points, natural_cubic_spline
import numexpr as ne
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .user_profile import UserProfile

@login_required
def punto_fijo_view(request):
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
    grafica_punto_fijo = None
    if resultado:
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
        'is_premium': hasattr(request.user, 'userprofile') and request.user.userprofile.is_premium if request.user.is_authenticated else False,
        'valor_inicial_val': valor_inicial,
        'tolerancia_val': tolerancia,
        'decimales_val': decimales,
        'grafica_punto_fijo': grafica_punto_fijo,
    })

@login_required
def spline_view(request):
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
    grafica_trazador = None
    if result and 'tabla_hm' in result:
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
        'is_premium': hasattr(request.user, 'userprofile') and request.user.userprofile.is_premium if request.user.is_authenticated else False,
        'grafica_trazador': grafica_trazador,
    })

@login_required
def historial_view(request):
    historial = SplineHistory.objects.filter(user=request.user).order_by('-fecha_creacion')
    return render(request, 'trazador_cubico/historialTrazador.html', {'historial': historial})

@login_required
def historial_punto_fijo(request):
    historial = PuntoFijoHistorial.objects.filter(user=request.user).order_by('-fecha')
    return render(request, 'punto_fijo/historial_punto_fijo.html', {'historial': historial})

@login_required
def punto_fijo_pdf(request, id):
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
    if resultado:
        if is_premium:
            grafica_punto_fijo = {
                'x': [r['iteracion'] for r in resultado],
                'y': [r['x'] for r in resultado],
                'error': [r['error'] for r in resultado],
            }
        else:
            # Solo el último punto para no premium
            last = resultado[-1]
            grafica_punto_fijo = {
                'x': [last['iteracion']],
                'y': [last['x']],
                'error': [last['error']],
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
        if result and 'tabla_hm' in result:
            x_vals = [p[0] for p in points]
            y_vals = [p[1] for p in points]
            polinomios = result.get('polinomios', [])
            if is_premium:
                grafica_trazador = {
                    'x': x_vals,
                    'y': y_vals,
                    'polinomios': polinomios,
                    'x_query': result.get('x_query'),
                    'y_query': result.get('resultado'),
                }
            else:
                # Solo el punto evaluado para no premium
                grafica_trazador = {
                    'x': [result.get('x_query')],
                    'y': [result.get('resultado')],
                    'polinomios': [],
                    'x_query': result.get('x_query'),
                    'y_query': result.get('resultado'),
                }
        # --- end datos gráfica ---
    except Exception as e:
        form.add_error(None, f"Error en los datos: {e}")

    is_premium = hasattr(request.user, 'userprofile') and request.user.userprofile.is_premium if request.user.is_authenticated else False
    return render(request, 'trazador_cubico/trazadorCubico.html', {
        'form': form,
        'result': result if is_premium else {
            'razonamiento': result['razonamiento'] if result else '',
            'polinomio_usado': result['polinomio_usado'] if result else '',
            'x_query': result['x_query'] if result and 'x_query' in result else '',
            'resultado': result['resultado'] if result else '',
        },
        'is_premium': is_premium,
        'modo_repetir': True,
        'grafica_trazador': grafica_trazador,
    })


from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout


# Create your views here.


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

def cerrar_sesion(request):
    logout(request)
    return redirect('login') 

def index(request):
    return render(request,'paginas/index.html') 

def tienda(request):
    is_premium = False
    if request.user.is_authenticated:
        try:
            is_premium = request.user.userprofile.is_premium
        except Exception:
            is_premium = False
    return render(request,'paginas/tienda.html', {'is_premium': is_premium})

def documentacion_trazadores(request):
    return render(request, 'trazador_cubico/documentacion_trazador.html')

def documentacion_punto(request):
    return render(request, 'punto_fijo/documentacion_puntoFijo.html')

@login_required
def comprar_premium(request):
    profile = UserProfile.objects.get(user=request.user)
    if not profile.is_premium:
        profile.is_premium = True
        profile.save()
    return redirect('tienda')
