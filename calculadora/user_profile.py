"""
Modelo de perfil de usuario extendido para Forja-Solver.
Permite almacenar información adicional y estado premium.
"""

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Extiende el modelo de usuario de Django para agregar datos personales y estado premium.
    """
    LANGUAGE_CHOICES = [
        ('es', 'Español'),
        ('en', 'English'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False)
    nombre_completo = models.CharField(max_length=100, blank=True)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    carrera = models.CharField(max_length=100, blank=True)
    carnet = models.CharField(max_length=30, blank=True)
    ciclo = models.CharField(max_length=30, blank=True)
    idioma_preferido = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='es')

    def __str__(self):
        return f"Perfil de {self.user.username} (Premium: {self.is_premium})"

    def get_foto_url(self):
        """
        Devuelve la URL de la foto de perfil o una imagen por defecto.
        """
        if self.foto_perfil:
            return self.foto_perfil.url
        return '/static/img/default_profile.png'
