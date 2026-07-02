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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        categoria = CategoriaGasto.objects.get(nombre="Nómina")

        Gasto.objects.update_or_create(
            pago_nomina=self,
            defaults={
                "sucursal": self.empleado.sucursal,
                "categoria": categoria,
                "fecha": self.fecha_pago,
                "monto": self.monto,
                "descripcion": f"Nómina {self.empleado.nombre}",
            }
        )

        