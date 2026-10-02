from django.db import models
from apps.sucursales.models import Sucursal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal





class Receta(models.Model):

    variante_vendida = models.OneToOneField(
        "inventario.VarianteProducto",
        on_delete=models.PROTECT,
        related_name="receta"
    )

    activa = models.BooleanField(default=True)

    observaciones = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["variante_vendida__producto__nombre", "variante_vendida__nombre"]

    def clean(self):
        tipo = self.variante_vendida.producto.tipo
        if tipo == "insumo":
            raise ValidationError("No puedes crear una receta de venta para un producto marcado solo como insumo.")

    def __str__(self):
        return f"Receta de {self.variante_vendida}"



class RecetaDetalle(models.Model):

    receta = models.ForeignKey(
        "inventario.Receta",
        on_delete=models.CASCADE,
        related_name="detalles"
    )

    insumo = models.ForeignKey(
        "inventario.VarianteProducto",
        on_delete=models.PROTECT,
        related_name="recetas_como_insumo"
    )

    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text="Cantidad consumida del insumo por 1 unidad vendida."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["insumo__producto__nombre", "insumo__nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["receta", "insumo"],
                name="unique_insumo_por_receta"
            )
        ]

    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad del insumo debe ser mayor que cero.")

        if self.insumo_id == self.receta.variante_vendida_id:
            raise ValidationError("La variante vendida no puede ser insumo de sí misma.")

        tipo = self.insumo.producto.tipo
        if tipo == "terminado":
            raise ValidationError("El insumo debe ser un producto tipo insumo o ambos.")

    def __str__(self):
        return f"{self.receta.variante_vendida} -> {self.insumo} ({self.cantidad})"


class MovimientoInventario(models.Model):

    class TipoMovimiento(models.TextChoices):
        INVENTARIO_INICIAL = "inventario_inicial", "Inventario inicial"
        COMPRA = "compra", "Compra"
        AJUSTE_ENTRADA = "ajuste_entrada", "Ajuste entrada"
        AJUSTE_SALIDA = "ajuste_salida", "Ajuste salida"
        VENTA = "venta", "Consumo por venta"
        MERMA = "merma", "Merma"
        TRASLADO_ENTRADA = "traslado_entrada", "Traslado entrada"
        TRASLADO_SALIDA = "traslado_salida", "Traslado salida"

    TIPOS_ENTRADA = {
        TipoMovimiento.INVENTARIO_INICIAL,
        TipoMovimiento.COMPRA,
        TipoMovimiento.AJUSTE_ENTRADA,
        TipoMovimiento.TRASLADO_ENTRADA,
    }

    TIPOS_SALIDA = {
        TipoMovimiento.VENTA,
        TipoMovimiento.MERMA,
        TipoMovimiento.AJUSTE_SALIDA,
        TipoMovimiento.TRASLADO_SALIDA,
    }

    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name="movimientos_inventario"
    )

    variante = models.ForeignKey(
        "inventario.VarianteProducto",
        on_delete=models.PROTECT,
        related_name="movimientos_inventario"
    )

    fecha_hora = models.DateTimeField(
        default=timezone.now
    )

    tipo = models.CharField(
        max_length=30,
        choices=TipoMovimiento.choices
    )

    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text="Guardar siempre como valor positivo."
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimientos_inventario",
        null=True,
        blank=True
    )

    venta = models.ForeignKey(
        "ventas.Venta",
        on_delete=models.PROTECT,
        related_name="movimientos_inventario",
        null=True,
        blank=True
    )

    venta_detalle = models.ForeignKey(
        "ventas.VentaDetalle",
        on_delete=models.PROTECT,
        related_name="movimientos_inventario",
        null=True,
        blank=True
    )

    observaciones = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_hora", "-id"]
        indexes = [
            models.Index(fields=["sucursal", "fecha_hora"]),
            models.Index(fields=["variante", "fecha_hora"]),
            models.Index(fields=["tipo", "fecha_hora"]),
        ]

    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad del movimiento debe ser mayor que cero.")

    @property
    def es_entrada(self):
        return self.tipo in self.TIPOS_ENTRADA

    @property
    def es_salida(self):
        return self.tipo in self.TIPOS_SALIDA

    @property
    def cantidad_firmada(self):
        if self.es_entrada:
            return self.cantidad
        if self.es_salida:
            return -self.cantidad
        return Decimal("0.0000")

    def __str__(self):
        return f"{self.sucursal} - {self.variante} - {self.tipo} - {self.cantidad}"


class Producto(models.Model):

    class TipoProducto(models.TextChoices):
        TERMINADO = "terminado", "Producto terminado"
        INSUMO = "insumo", "Insumo"
        AMBOS = "ambos", "Ambos"

    nombre = models.CharField(
        max_length=200
    )

    tipo = models.CharField(
        max_length=20,
        choices=TipoProducto.choices,
        default=TipoProducto.TERMINADO,
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

    precio_venta=models.DecimalField(
        max_digits=12,
        decimal_places=2,
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