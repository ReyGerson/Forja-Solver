from django import forms

class PuntoFijoForm(forms.Form):
    funcion = forms.CharField(
        label="Función F(x)",
        help_text="Ej: exp(-x)-x. Usa funciones como: exp(), log(), sin(), cos(), sqrt(), x**2"
    )
    despeje = forms.CharField(
        label="Despeje g(x)",
        help_text="Ej: exp(-x). Usa operaciones como: ** para potencias, exp(), log(), etc."
    )
    valor_inicial = forms.FloatField(label="Valor inicial")
    tolerancia = forms.FloatField(label="Tolerancia (%)")
    decimales = forms.IntegerField(label="Número de decimales", initial=5)

class SplineInputForm(forms.Form):
    points = forms.CharField(
        label="Lista de puntos",
        help_text='Ejemplo: (1.2,4.6),(1.5,5.3),(2.4,6),(3,4.8),(3.8,3.2)',
        widget=forms.Textarea(attrs={'rows': 3})
    )
    x_value = forms.FloatField(label="Valor de x")