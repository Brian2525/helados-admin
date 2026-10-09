

from django.db import models
from django.contrib.auth.models import User


from apps.sucursales.models import Sucursal
from apps.inventario.models import VarianteProducto
from apps.gastos.models import Gasto
from django.db.models import Sum
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.promociones.models import Promocion




class Venta(models.Model):

    class EstadoVenta(models.TextChoices):
        CONFIRMADA = "confirmada", "Confirmada"
        ANULADA = "anulada", "Anulada"

    class MetodoPago(models.TextChoices):
        EFECTIVO = "efectivo", "Efectivo"
        TARJETA = "tarjeta", "Tarjeta"
        OTRO = "otro", "Otro"

    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name="ventas"
    )

    metodo_pago = models.CharField(
        max_length=20,
        choices=MetodoPago.choices
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ventas"
    )

    fecha_hora = models.DateTimeField(
        default=timezone.now
    )

    estado = models.CharField(
        max_length=20,
        choices=EstadoVenta.choices,
        default=EstadoVenta.CONFIRMADA
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    efectivo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Monto de la venta pagado en efectivo."
    )

    tarjeta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Monto de la venta pagado con tarjeta."
    )

    monto_recibido = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Dinero recibido del cliente. Usar solo cuando el método sea efectivo."
    )

    cambio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    observaciones = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_hora"]
        indexes = [
            models.Index(fields=["sucursal", "fecha_hora"]),
            models.Index(fields=["estado", "fecha_hora"]),
            models.Index(fields=["metodo_pago", "fecha_hora"]),
        ]

    def clean(self):
        errors = {}

        campos_no_negativos = {
            "descuento": self.descuento,
            "efectivo": self.efectivo,
            "tarjeta": self.tarjeta,
            "monto_recibido": self.monto_recibido,
            "cambio": self.cambio,
            "subtotal": self.subtotal,
            "total": self.total,
        }

        for campo, valor in campos_no_negativos.items():
            if valor is not None and valor < 0:
                errors[campo] = "Este valor no puede ser negativo."

        if self.total < 0:
            errors["total"] = "El total no puede ser negativo."

        if self.descuento > self.subtotal:
            errors["descuento"] = "El descuento no puede ser mayor al subtotal."

        if self.metodo_pago == self.MetodoPago.EFECTIVO:
            if self.tarjeta != Decimal("0.00"):
                errors["tarjeta"] = "En una venta en efectivo, tarjeta debe ser 0."

            if self.efectivo != self.total:
                errors["efectivo"] = "En una venta en efectivo, el monto en efectivo debe ser igual al total."

            if self.monto_recibido < self.total:
                errors["monto_recibido"] = "El monto recibido no puede ser menor al total."

            cambio_esperado = self.monto_recibido - self.total
            if self.cambio != cambio_esperado:
                errors["cambio"] = f"El cambio debe ser {cambio_esperado}."

        elif self.metodo_pago == self.MetodoPago.TARJETA:
            if self.efectivo != Decimal("0.00"):
                errors["efectivo"] = "En una venta con tarjeta, efectivo debe ser 0."

            if self.tarjeta != self.total:
                errors["tarjeta"] = "En una venta con tarjeta, el monto en tarjeta debe ser igual al total."

            if self.monto_recibido != Decimal("0.00"):
                errors["monto_recibido"] = "En una venta con tarjeta, monto recibido debe ser 0."

            if self.cambio != Decimal("0.00"):
                errors["cambio"] = "En una venta con tarjeta, cambio debe ser 0."

        elif self.metodo_pago == self.MetodoPago.OTRO:
            if self.efectivo != Decimal("0.00"):
                errors["efectivo"] = "En una venta con método 'otro', efectivo debe ser 0."

            if self.tarjeta != Decimal("0.00"):
                errors["tarjeta"] = "En una venta con método 'otro', tarjeta debe ser 0."

            if self.monto_recibido != Decimal("0.00"):
                errors["monto_recibido"] = "En una venta con método 'otro', monto recibido debe ser 0."

            if self.cambio != Decimal("0.00"):
                errors["cambio"] = "En una venta con método 'otro', cambio debe ser 0."

        if errors:
            raise ValidationError(errors)



    @property
    def total_pagado(self):
        return (self.efectivo or Decimal("0.00")) + (self.tarjeta or Decimal("0.00"))

    def __str__(self):
        return f"Venta #{self.pk or 'N/A'} - {self.sucursal} - {self.fecha_hora:%Y-%m-%d %H:%M}"




class VentaPromocion(models.Model):

    venta = models.ForeignKey(
        "ventas.Venta",
        on_delete=models.CASCADE,
        related_name="promociones_aplicadas"
    )

    promocion = models.ForeignKey(
        Promocion,
        on_delete=models.PROTECT
    )

    nombre = models.CharField(
        max_length=150
    )

    tipo = models.CharField(
        max_length=30,
        choices=Promocion.Tipo.choices
    )

    cantidad_aplicaciones = models.PositiveIntegerField(
        default=1
    )

    descuento_por_aplicacion = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    descuento = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["venta", "promocion"],
                name="unique_promocion_por_venta"
            )
        ]

    def clean(self):
        errors = {}

        if self.cantidad_aplicaciones <= 0:
            errors["cantidad_aplicaciones"] = (
                "Debe existir al menos una aplicación."
            )

        if self.descuento_por_aplicacion < Decimal("0.00"):
            errors["descuento_por_aplicacion"] = (
                "El descuento no puede ser negativo."
            )

        if self.descuento < Decimal("0.00"):
            errors["descuento"] = (
                "El descuento no puede ser negativo."
            )

        if errors:
            raise ValidationError(errors)


class VentaDetalle(models.Model):

    venta = models.ForeignKey(
        "ventas.Venta",
        on_delete=models.CASCADE,
        related_name="detalles"
    )

    variante = models.ForeignKey(
        VarianteProducto,
        on_delete=models.PROTECT,
        related_name="detalles_venta"
    )

    producto_nombre = models.CharField(
        max_length=200
    )

    variante_nombre = models.CharField(
        max_length=200
    )

    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["venta", "variante"],
                name="unique_variante_por_venta"
            )
        ]

    def clean(self):
        errors = {}

        if self.cantidad is None or self.cantidad <= 0:
            errors["cantidad"] = "La cantidad debe ser mayor que cero."

        if self.precio_unitario is None or self.precio_unitario < 0:
            errors["precio_unitario"] = "El precio unitario no puede ser negativo."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.producto_nombre:
            self.producto_nombre = self.variante.producto.nombre

        if not self.variante_nombre:
            self.variante_nombre = self.variante.nombre

        self.subtotal = (self.cantidad or Decimal("0.00")) * (
            self.precio_unitario or Decimal("0.00")
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto_nombre} - {self.variante_nombre} x {self.cantidad}"




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



class VentaDiaria(models.Model):


    class TipoRegistro(models.TextChoices):
        MANUAL = "manual", "Manual"
        AUTOMATICO = "automatico", "Automático"


    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name="ventas_diarias"
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="ventas_registradas"
    )

    fecha = models.DateField()

    efectivo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    efectivo_contado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    tarjeta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    otro = models.DecimalField(
    max_digits=12,
    decimal_places=2,
    default=0,
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


    tipo_registro = models.CharField(
        max_length=15,
        choices=TipoRegistro.choices,
        default=TipoRegistro.MANUAL
    )

    fecha_registro = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        ordering = ["-fecha"]

        constraints = [
            models.UniqueConstraint(
                fields=["sucursal", "fecha"],
                name="unique_venta_diaria_sucursal_fecha"
            )
        ]



    @property
    def total(self):
        return (
            self.efectivo
            + self.tarjeta
            + self.otro
        )

    def __str__(self):

        return f"{self.sucursal} - {self.fecha}"










