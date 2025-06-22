from django import forms
from .models import PuntoFijo

class PuntoFijoForm(forms.ModelForm):
    class Meta:
        model = PuntoFijo
        fields = '__all__'