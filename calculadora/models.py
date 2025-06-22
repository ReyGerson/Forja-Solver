from django.db import models

from django.db import models

class SplineHistory(models.Model):
    puntos = models.TextField() 
    x_valor = models.FloatField()
    resultado = models.FloatField()
    razonamiento = models.TextField()
    polinomio_usado = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"x = {self.x_valor} → {self.resultado:.4f} ({self.fecha_creacion.strftime('%Y-%m-%d %H:%M')})"

class PuntoFijoHistorial(models.Model):
    funcion = models.TextField()
    despeje = models.TextField()
    valor_inicial = models.FloatField()
    tolerancia = models.FloatField()
    decimales = models.IntegerField()
    solucion = models.FloatField()
    error = models.FloatField()
    comprobacion = models.TextField()
    iteraciones = models.TextField()  # guardamos resumen como texto plano
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.funcion} (x0={self.valor_inicial}) → {self.solucion} [{self.fecha.strftime('%Y-%m-%d %H:%M')}]"