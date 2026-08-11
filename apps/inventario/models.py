from django.db import models




class Producto(models.Model):

    nombre = models.CharField(
        max_length=200
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

    contenido_pzas = models.PositiveIntegerField(
        default=0,
        help_text="Pzas que contiene la caja"
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