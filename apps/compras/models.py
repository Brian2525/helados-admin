from django.db import models
import datetime
from apps.gastos.models import CategoriaGasto
from apps.sucursales.models import Sucursal


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

    saldo = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    estatus = models.CharField(
        max_length=20,
        choices=ESTATUS,
        default="pendiente"
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
    

#Abonos de cuentas por pagar
class PagoCuentaPorPagar(models.Model):

    cuenta = models.ForeignKey(
        CuentaPorPagar,
        on_delete=models.CASCADE,
        related_name="pagos"
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