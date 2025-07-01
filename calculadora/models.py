"""
Modelos principales de la app Forja-Solver.
Incluye historial de métodos numéricos y perfil de usuario extendido.
"""

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone


from .user_profile import UserProfile

class SplineHistory(models.Model):
    """
    Guarda el historial de cálculos del método de Trazador Cúbico para cada usuario.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    puntos = models.TextField() 
    x_valor = models.FloatField()
    resultado = models.FloatField()
    razonamiento = models.TextField()
    polinomio_usado = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"x = {self.x_valor} → {self.resultado:.4f} ({self.fecha_creacion.strftime('%Y-%m-%d %H:%M')})"

class PuntoFijoHistorial(models.Model):
    """
    Guarda el historial de cálculos del método de Punto Fijo para cada usuario.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    funcion = models.TextField()
    despeje = models.TextField()
    funcion_latex = models.TextField(blank=True, null=True)
    despeje_latex = models.TextField(blank=True, null=True)
    valor_inicial = models.FloatField()
    tolerancia = models.FloatField()
    decimales = models.IntegerField()
    solucion = models.FloatField()
    error = models.FloatField()
    comprobacion = models.TextField()
    iteraciones = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.funcion} (x0={self.valor_inicial}) → {self.solucion} [{self.fecha.strftime('%Y-%m-%d %H:%M')}]"

class SimplexHistorial(models.Model):
    """
    Guarda el historial de cálculos del método Simplex para cada usuario.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    tipo_objetivo = models.CharField(max_length=20)  # "Maximizar" o "Minimizar"
    funcion_objetivo = models.TextField()  # LaTeX de la función objetivo
    restricciones = models.TextField()  # JSON con las restricciones en LaTeX
    solucion_optima = models.TextField()  # JSON con las variables y sus valores
    valor_z = models.FloatField()  # Valor óptimo de Z
    iteraciones_json = models.TextField()  # JSON con todas las iteraciones (solo para premium)
    modelo_matematico = models.TextField()  # JSON con el modelo completo
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_objetivo} Z (Z={self.valor_z:.2f}) [{self.fecha.strftime('%Y-%m-%d %H:%M')}]"

    class Meta:
        ordering = ['-fecha']

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil de usuario extendido al registrar un nuevo usuario.
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Guarda automáticamente el perfil extendido al guardar el usuario.
    """
    instance.userprofile.save()

class MetodoGraficoHistorial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    funcion = models.CharField(max_length=255)
    optimizacion = models.CharField(max_length=10)  # 'max' o 'min'
    restricciones = models.TextField()
    solucion = models.CharField(max_length=100)
    punto_optimo = models.CharField(max_length=100)
    puntos_factibles = models.TextField()
    vertices = models.TextField(blank=True, null=True)
    iteraciones = models.TextField(blank=True, null=True)
    grafica = models.TextField(blank=True, null=True)  # Para almacenar el HTML de la gráfica

    class Meta:
        verbose_name = "Historial Método Gráfico"
        verbose_name_plural = "Historial Método Gráfico"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Método Gráfico - {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}"