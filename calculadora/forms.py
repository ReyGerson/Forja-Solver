"""
Formularios principales de la app Forja-Solver.
Incluye formularios para métodos numéricos y gestión de usuario.
"""
from django import forms
from django.contrib.auth.models import User
from .user_profile import UserProfile
from django.contrib.auth.forms import UserCreationForm

class PuntoFijoForm(forms.Form):
    """
    Formulario para ingresar los datos del método de Punto Fijo.
    """
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
    """
    Formulario para ingresar los datos del método de Trazador Cúbico.
    """
    points = forms.CharField(
        label="Lista de puntos",
        help_text='Ejemplo: (1.2,4.6),(1.5,5.3),(2.4,6),(3,4.8),(3.8,3.2)',
        widget=forms.Textarea(attrs={'rows': 3})
    )
    x_value = forms.FloatField(label="Valor de x")

class RegistroUsuarioForm(UserCreationForm):
    """
    Formulario de registro extendido para nuevos usuarios, con datos personales y foto.
    """
    email = forms.EmailField(required=True)
    nombre_completo = forms.CharField(max_length=100, required=True)
    foto_perfil = forms.ImageField(required=False)
    carrera = forms.CharField(max_length=100, required=False)
    carnet = forms.CharField(max_length=30, required=False)
    ciclo = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.nombre_completo = self.cleaned_data['nombre_completo']
            if self.cleaned_data.get('foto_perfil'):
                profile.foto_perfil = self.cleaned_data['foto_perfil']
            profile.carrera = self.cleaned_data['carrera']
            profile.carnet = self.cleaned_data['carnet']
            profile.ciclo = self.cleaned_data['ciclo']
            profile.save()
        return user

class EditarPerfilForm(forms.ModelForm):
    """
    Formulario para editar los datos del perfil de usuario.
    """
    nombre_completo = forms.CharField(max_length=100, required=True)
    foto_perfil = forms.ImageField(required=False)
    carrera = forms.CharField(max_length=100, required=False)
    carnet = forms.CharField(max_length=30, required=False)
    ciclo = forms.CharField(max_length=30, required=False)

    class Meta:
        model = UserProfile
        fields = ['nombre_completo', 'foto_perfil', 'carrera', 'carnet', 'ciclo']


from django import forms

class MetodoGraficoForm(forms.Form):
    funcion_objetivo = forms.CharField(
        label='Función objetivo (ej: max 3x + 4y)',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'max 3x + 4y'})
    )
    restricciones = forms.CharField(
        label='Restricciones (una por línea, ej: x + y <= 5)',
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'x + y <= 5\n2x + y <= 8'}),
        help_text='Una restricción por línea, variables x e y, desigualdades <=, >=, ='
    )