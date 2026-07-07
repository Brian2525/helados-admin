from django.db import models
import datetime 
from django.utils import timezone
from apps.gastos.models import CategoriaGasto
from apps.sucursales.models import Sucursal
from decimal import Decimal
from django.db.models import Sum
from apps.gastos.models import Gasto, CategoriaGasto

# Create your models here.
class Proveedor(models.Model):

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
        )["total"] or 0

    @property
    def saldo(self):
        return self.monto_total - self.total_pagado


    @property
    def estatus(self):
        if self.saldo <= 0:
            return "pagado"
        elif self.total_pagado > 0:
            return "parcial"
        elif self.fecha_vencimiento < datetime.date.today():
            return "vencido"
        else:
            return "pendiente"  
    




#Abonos de cuentas por pagar
class PagoCuentaPorPagar(models.Model):

    cuenta = models.ForeignKey(
        CuentaPorPagar,
        related_name="pagos",
        on_delete=models.CASCADE
    )

    fecha = models.DateField(
        default=datetime.date.today
    )

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    observaciones = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    
    )

    class Meta:

        ordering = ["-fecha"]

    def save(self, *args, **kwargs):

        nuevo = self.pk is None

        super().save(*args, **kwargs)

        if nuevo:
            cuenta = self.cuenta

            if cuenta.saldo <= Decimal("0"):
                cuenta.estatus = "pagado"
            elif cuenta.total_pagado > Decimal("0"):
                cuenta.estatus = "parcial"
            else:
                cuenta.estatus = "pendiente"

            cuenta.save(update_fields=["estatus"])

           

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        categoria = self.cuenta.categoria

        Gasto.objects.create(

            sucursal=self.cuenta.sucursal,

            categoria=categoria,

            fecha=self.fecha,

            monto=self.monto,

            descripcion=f"Pago a {self.cuenta.proveedor.nombre}",

        )
    @property
    def total_pagado(self):

        return self.pagos.aggregate(

            total=Sum("monto")

        )["total"] or 0