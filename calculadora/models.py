from django.db import models

# Create your models here.

class PuntoFijo(models.Model):
    id = models.AutoField(primary_key=True)
    funcion = models.CharField(verbose_name="Funcion", max_length=255)
    valorInicial = models.CharField(verbose_name="Valor Inicial", max_length=255)
    pricision = models.CharField(verbose_name="Precicion", max_length=255)
    decimales = models.CharField(verbose_name="Decimales", max_length=255)
    creado = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación") 

    def __str__(self):
        punto = (
            "Creado: " + self.creado +
            " - Funcion: " + self.funcion +
            " - Valor Inicial: " + self.valorInicial +
            " - Precision: " + self.pricision +
            " - Decimales: " + self.decimales
        )
        return punto
    
    def delete(self, using = None, keep_parents = False):
        return super().delete()