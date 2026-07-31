from django.db import models


from apps.sucursales.models import Sucursal


class Producto(models.Model):

    nombre = models.CharField(
        max_length=200
    )

    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name="productos"
    )

    descripcion = models.TextField(
        blank=True
    )

    proveedor = models.ForeignKey(
        "compras.Proveedor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos"
    )

    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    existencia = models.PositiveIntegerField(
        default=0,
        help_text="Existencia en cajas o bolsas."
    )

    stock_minimo = models.PositiveIntegerField(
        default=0
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


    @property
    def valor_existencia(self):
        return self.existencia * self.precio_compra

    @property
    def necesita_reabastecer(self):
        return self.existencia <= self.stock_minimo

    #def comprado_mes(self):

    #   hoy = timezone.now().date()

    #   return (
    #        self.detalles_compra.filter(
    #            compra__fecha__year=hoy.year,
    #            compra__fecha__month=hoy.month,
    #        ).aggregate(
    #            total=Sum("cantidad")
    #        )["total"] or 0
    #    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre