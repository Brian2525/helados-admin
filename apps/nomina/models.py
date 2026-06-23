from django.db import models

from apps.sucursales.models import Sucursal


class Empleado(models.Model):

    nombre = models.CharField(
        max_length=200
    )

    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name="empleados"
    )

    puesto = models.CharField(
        max_length=100
    )

    sueldo_semanal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    fecha_ingreso = models.DateField()

    activo = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
    



class PagoNomina(models.Model):

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name="pagos"
    )

    fecha_pago = models.DateField()

    fecha_inicio = models.DateField()

    fecha_fin = models.DateField()

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    observaciones = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-fecha_pago"]

    def __str__(self):
        return (
            f"{self.empleado.nombre} "
            f"{self.fecha_pago}"
        )