from django.db import models
from apps.sucursales.models import Sucursal

import datetime
from django.core.exceptions import ValidationError


class CategoriaGasto(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    activa = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Categoría de gasto"
        verbose_name_plural = "Categorías de gastos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
    
    def delete(self, *args, **kwargs):

        if self.nombre.lower() == "nómina":

            raise ValidationError(
                "La categoría Nómina es obligatoria y no puede eliminarse."
            )

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):

        if self.pk:

            original = CategoriaGasto.objects.get(
                pk=self.pk
            )

            if (
                original.nombre.lower() == "nómina"
                and self.nombre.lower() != "nómina"
            ):

                raise ValidationError(
                    "La categoría Nómina no puede renombrarse."
                )

        super().save(*args, **kwargs)
    



class Gasto(models.Model):

    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT
    )

    fecha = models.DateField( default=datetime.date.today )

    categoria = models.ForeignKey(
        CategoriaGasto,
        on_delete=models.PROTECT
    )

    descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    
    pago_nomina = models.OneToOneField(
        "nomina.PagoNomina",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)











