from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False)
    # Nuevos campos para gestión de usuarios
    nombre_completo = models.CharField(max_length=100, blank=True)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    carrera = models.CharField(max_length=100, blank=True)
    carnet = models.CharField(max_length=30, blank=True)
    ciclo = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username} (Premium: {self.is_premium})"

    def get_foto_url(self):
        if self.foto_perfil:
            return self.foto_perfil.url
        return '/static/img/default_profile.png'
