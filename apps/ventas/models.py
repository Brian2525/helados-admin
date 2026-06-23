

from django.db import models

from apps.sucursales.models import Sucursal
from apps.gastos.models import Gasto
from django.db.models import Sum


class ResumenSemanal(models.Model):

    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name="resumenes"
    )

    fecha_inicio = models.DateField()

    fecha_fin = models.DateField()

    efectivo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    tarjeta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    observaciones = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-fecha_inicio"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "sucursal",
                    "fecha_inicio",
                    "fecha_fin"
                ],
                name="unique_resumen_semanal"
            )
        ]

    @property
    def total_ventas(self):
        return self.efectivo + self.tarjeta
    
    @property
    def total_gastos(self):

        return Gasto.objects.filter(
            sucursal=self.sucursal,
            fecha__range=[
                self.fecha_inicio,
                self.fecha_fin
            ]
        ).aggregate(
            total=Sum("monto")
        )["total"] or 0

    def __str__(self):
        return (
            f"{self.sucursal} "
            f"{self.fecha_inicio} - {self.fecha_fin}"
        )