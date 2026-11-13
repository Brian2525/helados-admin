
# Create your models here.
# apps/promociones/models.py

from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal

class Promocion(models.Model):

    class Tipo(models.TextChoices):
        PRECIO_GRUPO = "precio_grupo", "Precio por grupo"
        DESCUENTO_GRUPO = "descuento_grupo", "Descuento por grupo"
        DESCUENTO_UNIDAD = "descuento_unidad", "Descuento por unidad"
        COMPRA_LLEVA = "compra_lleva", "Compra X lleva Y"


    nombre = models.CharField(max_length=150)

    tipo = models.CharField(
        max_length=30,
        choices=Tipo.choices
    )

    activa = models.BooleanField(default=True)

    fecha_inicio = models.DateField(
        null=True,
        blank=True
    )

    fecha_fin = models.DateField(
        null=True,
        blank=True
    )

    lunes = models.BooleanField(default=True)
    martes = models.BooleanField(default=True)
    miercoles = models.BooleanField(default=True)
    jueves = models.BooleanField(default=True)
    viernes = models.BooleanField(default=True)
    sabado = models.BooleanField(default=True)
    domingo = models.BooleanField(default=True)

    precio_grupo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    descuento_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    descuento_por_unidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )


    cantidad_compra = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Cantidad de unidades que paga el cliente"
    )

    cantidad_lleva = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Cantidad total de unidades que recibe"
    )


  


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    def clean(self):
        super().clean()

        if self.tipo == self.Tipo.COMPRA_LLEVA:

            if (
                self.cantidad_compra is None
                or self.cantidad_lleva is None
            ):
                raise ValidationError(
                    "Debes indicar las cantidades de compra y lleva."
                )

            if (
                self.cantidad_compra < 1
                or self.cantidad_lleva <= self.cantidad_compra
            ):
                raise ValidationError(
                    "La cantidad que lleva debe ser mayor "
                    "a la cantidad que compra."
                )

    



class PromocionDetalle(models.Model):

    promocion = models.ForeignKey(
        Promocion,
        on_delete=models.CASCADE,
        related_name="detalles"
    )

    producto = models.ForeignKey(
        "inventario.Producto",
        on_delete=models.PROTECT,
        related_name="detalles_promocion",
        null=True,
        blank=True,
    )

    variantes_elegibles = models.ManyToManyField(
        "inventario.VarianteProducto",
        blank=True,
        related_name="detalles_promocion"
    )

    cualquier_variante = models.BooleanField(
        default=False
    )

    cantidad = models.PositiveIntegerField(
        default=1
    )

    sucursales = models.ManyToManyField(
        "sucursales.Sucursal",
        related_name="detalles_promocion",
        blank=True,
        help_text=(
            "Selecciona las sucursales donde "
            "participan estos productos o variantes. "
            "Si no seleccionas ninguna, "
            "aplica en todas las sucursales."
        ),
    )

    def __str__(self):

        producto = (
            self.producto.nombre
            if self.producto
            else "Sin producto"
        )

        return (
            f"{self.promocion.nombre} - "
            f"{producto} x {self.cantidad}"
        )