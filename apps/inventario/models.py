from django.db import models
from apps.sucursales.models import Sucursal




class Producto(models.Model):

    nombre = models.CharField(
        max_length=200
    )

    descripcion = models.TextField(
        blank=True
    )

    registrar_venta_diaria = models.BooleanField(
        default=True,
        help_text="Indica si sus variantes se muestran en el registro diario de ventas."
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



class VarianteProducto(models.Model):

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="variantes_producto"
    )

    nombre = models.CharField(
        max_length=200
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
        ordering = ["producto__nombre", "nombre"]

        constraints = [
            models.UniqueConstraint(
                fields=["producto", "nombre"],
                name="unique_variante_producto"
            )
        ]

    def __str__(self):
        return f"{self.producto.nombre} - {self.nombre}"





class InventarioDiario(models.Model):

    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name="inventarios_diarios"
    )

    fecha = models.DateField()

    variante = models.ForeignKey(
        VarianteProducto,
        on_delete=models.PROTECT,
        related_name="inventarios_diarios"
    )

    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )



    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def inventario_inicial(self):

        inventario_anterior = (
            InventarioDiario.objects
            .filter(
                sucursal=self.sucursal,
                variante=self.variante,
                fecha__lt=self.fecha
            )
            .order_by("-fecha")
            .first()
        )

        if inventario_anterior:
            return inventario_anterior.cantidad

        return 0

    @property
    def consumo(self):

        return self.inventario_inicial - self.cantidad

    class Meta:

        ordering = [
            "-fecha",
            "variante__producto__nombre",
            "variante__nombre",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "sucursal",
                    "variante",
                    "fecha",
                ],
                name="unique_inventario_diario"
            )
        ]

        indexes = [
            models.Index(
                fields=[
                    "sucursal",
                    "fecha",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.sucursal} - "
            f"{self.variante} - "
            f"{self.fecha}"
        )