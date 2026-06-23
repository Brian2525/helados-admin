from django.db import models
from apps.sucursales.models import Sucursal
from apps.gastos.models import CategoriaGasto
from apps.gastos.models import Gasto



class ServicioRecurrente(models.Model):

    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name="servicios"
    )

    categoria = models.ForeignKey(
        CategoriaGasto,
        on_delete=models.PROTECT
    )

    nombre = models.CharField(
        max_length=100
    )

    proveedor = models.CharField(
        max_length=100,
        blank=True
    )

    monto_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    dia_pago = models.PositiveSmallIntegerField()

    activo = models.BooleanField(
        default=True
    )

    observaciones = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.sucursal} - {self.nombre}"

# Create your models here.




class PagoServicio(models.Model):

    servicio = models.ForeignKey(
        ServicioRecurrente,
        on_delete=models.CASCADE,
        related_name="pagos"
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

    gasto = models.OneToOneField(
        Gasto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pago_servicio"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-fecha_pago"]

    def __str__(self):
        return (
            f"{self.servicio.nombre} - "
            f"{self.fecha_pago}"
        )
    
    def save(self, *args, **kwargs):

        nuevo = self.pk is None

        super().save(*args, **kwargs)

        if nuevo and not self.gasto:

            gasto = Gasto.objects.create(
                sucursal=self.servicio.sucursal,
                categoria=self.servicio.categoria,
                fecha=self.fecha_pago,
                monto=self.monto,
               
            )

            self.gasto = gasto

            super().save(
                update_fields=["gasto"]
            )