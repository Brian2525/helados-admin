from django.db import models
import datetime 
from django.utils import timezone
from apps.gastos.models import CategoriaGasto
from apps.sucursales.models import Sucursal
from decimal import Decimal
from django.db.models import Sum
from apps.gastos.models import Gasto, CategoriaGasto
from django.contrib.auth.models import User

# Create your models here.
class Proveedor(models.Model):

    propietario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="proveedores",
    )

    nombre = models.CharField(max_length=200)

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    telefono = models.CharField(
        max_length=20,
        blank=True
    )

    correo = models.EmailField(
        blank=True
    )

    direccion = models.TextField(
        blank=True
    )



    activo = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.nombre
    
    def get_queryset(self):

        queryset = Proveedor.objects.all()

        q = self.request.GET.get("q")

        if q:

            queryset = queryset.filter(
                nombre__icontains=q
            )

        return queryset.order_by("nombre")
    
class CuentaPorPagar(models.Model):

    ESTATUS = [
        ("pendiente", "Pendiente"),
        ("parcial", "Pago parcial"),
        ("pagado", "Pagado"),
        ("vencido", "Vencido"),
    ]

    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT
    )

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT
    )

    fecha = models.DateField(
        default=datetime.date.today
    )

    fecha_vencimiento = models.DateField()

    descripcion = models.CharField(
        max_length=255
    )

    monto_total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    categoria = models.ForeignKey(
        CategoriaGasto,
        on_delete=models.PROTECT
    )

    observaciones = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["fecha_vencimiento"]

    def __str__(self):
        return f"{self.proveedor} - ${self.saldo}"

    @property
    def total_pagado(self):
        return self.pagos.aggregate(
            total=Sum("monto")
        )["total"] or Decimal("0.00")

    @property
    def saldo(self):
        return self.monto_total - self.total_pagado

    @property
    def estatus(self):
        if self.saldo <= Decimal("0.00"):
            return "pagado"

        programaciones = self.programaciones.all()

        if not programaciones.exists():
            return "pendiente"

        if programaciones.filter(estado="pagado").exists():
            return "parcial"

        if self.fecha_vencimiento < timezone.localdate():
            return "vencido"

        return "pendiente"
    




class ProgramacionPago(models.Model):

    cuenta = models.ForeignKey(
        CuentaPorPagar,
        on_delete=models.CASCADE,
        related_name="programaciones"
    )

    numero = models.PositiveIntegerField()

    fecha_vencimiento = models.DateField()

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    estado = models.CharField(
        max_length=20,
        choices=[
            ("pendiente", "Pendiente"),
            ("pagado", "Pagado"),
        ],
        default="pendiente"
    )

 
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["numero"]



#Abonos de cuentas por pagar

class PagoCuentaPorPagar(models.Model):

    cuenta = models.ForeignKey(
        CuentaPorPagar,
        on_delete=models.PROTECT,
        related_name="pagos"
    )

    programacion = models.ForeignKey(
        ProgramacionPago,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pagos",
    )

    fecha = models.DateField()

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
        ordering = ["-fecha"]