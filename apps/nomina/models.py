from django.db import models

from apps.sucursales.models import Sucursal
from apps.gastos.models import Gasto, CategoriaGasto




class Empleado(models.Model):
    

    TIPO_NOMINA = [
        ("SEMANA", "Lunes a Viernes"),
        ("FIN_SEMANA", "Sábado y Domingo"),
    ]

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


  


    fecha_ingreso = models.DateField()

    tipo_nomina = models.CharField(
        max_length=20,
        choices=TIPO_NOMINA,
        default="SEMANA"
    )

    salario_periodo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

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
    


class Nomina(models.Model):

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="nominas"
    )

    fecha_inicio = models.DateField()

    fecha_fin = models.DateField()

    fecha_vencimiento = models.DateField()

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("pagada", "Pagada"),
        ("vencida", "Vencida"),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="pendiente"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["fecha_vencimiento"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "empleado",
                    "fecha_inicio",
                    "fecha_fin"
                ],
                name="nomina_unica_por_periodo"
            )
        ]

    def __str__(self):
        return (
            f"{self.empleado.nombre} "
            f"{self.fecha_inicio} - {self.fecha_fin}"
        )




class PagoNomina(models.Model):

    nomina = models.OneToOneField(
        Nomina,
        on_delete=models.PROTECT,
        related_name="pago",
        null=True, 
    )

    fecha_pago = models.DateField()

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

    def __str__(self):
        if self.nomina:
            return (
                f"Pago {self.nomina.empleado.nombre} "
                f"{self.fecha_pago}"
            )

        return f"Pago histórico {self.fecha_pago}"

