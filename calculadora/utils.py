"""
Funciones utilitarias para métodos numéricos en Forja-Solver.
Incluye parseo de puntos y cálculo de splines cúbicos.
"""
import re
import numpy as np
import pandas as pd

def parse_points(point_str):
    """
    Parsea una cadena de puntos y retorna una lista ordenada de tuplas (x, y).
    Formato esperado: (x1,y1),(x2,y2),...
    """
    pattern = r"\(([^)]+)\)"
    try:
        points = [tuple(map(float, p.split(','))) for p in re.findall(pattern, point_str)]
        if len(points) < 2:
            raise ValueError("Se requieren al menos dos puntos.")
        return sorted(points)  # Orden ascendente en x
    except:
        raise ValueError("Formato inválido de puntos. Usa: (x1,y1),(x2,y2),...")

def natural_cubic_spline(points, x_query):
    """
    Calcula el valor interpolado usando el método de splines cúbicos naturales.
    Devuelve el resultado, razonamiento, polinomios y coeficientes.
    """
    n = len(points)
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])
    h = np.diff(x)
    m = np.diff(y) / h
    tabla_hm = pd.DataFrame({
        'i': list(range(n)),
        'xi': x,
        'yi': y,
        'hi': [None] + list(h),
        'mi': [None] + list(m)
    })
    A = np.zeros((n, n))
    b = np.zeros(n)
    A[0][0] = A[-1][-1] = 1  # Condiciones naturales
    for i in range(1, n - 1):
        A[i][i - 1] = h[i - 1]
        A[i][i]     = 2 * (h[i - 1] + h[i])
        A[i][i + 1] = h[i]
        b[i]        = 3 * (m[i] - m[i - 1])
    C = np.linalg.solve(A, b)
    a = y[:-1]
    b_coef = m - h * (2 * C[:-1] + C[1:]) / 3
    d = (C[1:] - C[:-1]) / (3 * h)
    polinomios = []
    for i in range(n - 1):
        polinomios.append({
            'intervalo': f"[{x[i]}, {x[i+1]}]",
            'formula': (
                f"{a[i]:.6f} + {b_coef[i]:.6f}(x - {x[i]}) + "
                f"{C[i]:.6f}(x - {x[i]})^2 + {d[i]:.6f}(x - {x[i]})^3"
            )
        })
    if x_query < x[0] or x_query > x[-1]:
        raise ValueError("El valor de x está fuera del dominio de los puntos.")
    i = np.searchsorted(x, x_query) - 1
    if i < 0:
        i = 0
    if i >= n - 1:
        i = n - 2
    dx = x_query - x[i]
    Sx = a[i] + b_coef[i]*dx + C[i]*dx**2 + d[i]*dx**3
    razonamiento = (
        f"El valor x = {x_query} está en el intervalo [{x[i]}, {x[i+1]}], "
        f"por lo tanto se usa el polinomio p_{i+1}(x) definido en ese tramo."
    )
    return {
        'tabla_hm': tabla_hm,
        'coef_c': C,
        'coef_b': b_coef,
        'coef_d': d,
        'coef_a': a,
        'polinomios': polinomios,
        'resultado': Sx,
        'x_query': x_query,
        'razonamiento': razonamiento,
        'x_intervalo': [x[i], x[i+1]],
        'polinomio_usado': polinomios[i]['formula']
    }

