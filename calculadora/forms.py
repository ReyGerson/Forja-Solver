from django import forms
from django.contrib.auth.models import User
from .user_profile import UserProfile
from django.contrib.auth.forms import UserCreationForm

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

class RegistroUsuarioForm(UserCreationForm):
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
    nombre_completo = forms.CharField(max_length=100, required=True)
    foto_perfil = forms.ImageField(required=False)
    carrera = forms.CharField(max_length=100, required=False)
    carnet = forms.CharField(max_length=30, required=False)
    ciclo = forms.CharField(max_length=30, required=False)

    class Meta:
        model = UserProfile
        fields = ['nombre_completo', 'foto_perfil', 'carrera', 'carnet', 'ciclo']