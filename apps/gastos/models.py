from django.db import models
from apps.sucursales.models import Sucursal
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
import datetime 
from django.core.exceptions import ValidationError


class CategoriaGasto(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    activa = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Categoría de gasto"
        verbose_name_plural = "Categorías de gastos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
    
    def delete(self, *args, **kwargs):

        if self.nombre.lower() == "nómina":

            raise ValidationError(
                "La categoría Nómina es obligatoria y no puede eliminarse."
            )

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):

        if self.pk:

            original = CategoriaGasto.objects.get(
                pk=self.pk
            )

            if (
                original.nombre.lower() == "nómina"
                and self.nombre.lower() != "nómina"
            ):

                raise ValidationError(
                    "La categoría Nómina no puede renombrarse."
                )

        super().save(*args, **kwargs)
    

class Gasto(models.Model):

    class OrigenFondos(models.TextChoices):
        NO_ESPECIFICADO = (
            "no_especificado",
            "No especificado"
        )
        CAJA_CHICA = (
            "caja_chica",
            "Caja chica"
        )
        CAJA_VENTAS = (
            "caja_ventas",
            "Caja de ventas"
        )
        BANCO = (
            "banco",
            "Cuenta bancaria"
        )
        OTRO = (
            "otro",
            "Otro"
        )

    class Estado(models.TextChoices):
        REGISTRADO = "registrado", "Registrado"
        ANULADO = "anulado", "Anulado"

    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT
    )

    fecha = models.DateField(
        default=timezone.localdate
    )

    categoria = models.ForeignKey(
        CategoriaGasto,
        on_delete=models.PROTECT
    )

    descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    origen_fondos = models.CharField(
        max_length=20,
        choices=OrigenFondos.choices,
        null=True,
        blank=True,
        default=None
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.REGISTRADO
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="gastos_registrados"
    )

    comprobante = models.FileField(
        upload_to="gastos/comprobantes/%Y/%m/",
        blank=True,
        null=True
    )

    pago_nomina = models.OneToOneField(
        "nomina.PagoNomina",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ["-fecha", "-created_at"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(monto__gt=0),
                name="gasto_monto_positivo"
            )
        ]

    def __str__(self):
        return (
            f"{self.categoria.nombre} - "
            f"${self.monto} - "
            f"{self.sucursal}"
        )



class CajaChica(models.Model):

    sucursal = models.OneToOneField(
        Sucursal,
        on_delete=models.PROTECT,
        related_name="caja_chica"
    )

    fondo_objetivo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=200
    )

    saldo_actual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    activa = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Caja chica"
        verbose_name_plural = "Cajas chicas"

        constraints = [
            models.CheckConstraint(
                condition=models.Q(fondo_objetivo__gte=0),
                name="cajachica_fondo_no_negativo"
            ),
            models.CheckConstraint(
                condition=models.Q(saldo_actual__gte=0),
                name="cajachica_saldo_no_negativo"
            )
        ]

    def __str__(self):
        return f"Caja chica - {self.sucursal}"

    @property
    def monto_para_reponer(self):
        return max(
            self.fondo_objetivo - self.saldo_actual,
            Decimal("0.00")
        )




class MovimientoCajaChica(models.Model):

    class TipoMovimiento(models.TextChoices):
        APERTURA = "apertura", "Apertura"
        GASTO = "gasto", "Gasto"
        REPOSICION = "reposicion", "Reposición"
        AJUSTE_ENTRADA = (
            "ajuste_entrada",
            "Ajuste de entrada"
        )
        AJUSTE_SALIDA = (
            "ajuste_salida",
            "Ajuste de salida"
        )
        REVERSO = "reverso", "Reverso"

    caja_chica = models.ForeignKey(
        CajaChica,
        on_delete=models.PROTECT,
        related_name="movimientos"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TipoMovimiento.choices
    )

    # Positivo: entra dinero
    # Negativo: sale dinero
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    saldo_anterior = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    saldo_nuevo = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    gasto = models.OneToOneField(
        Gasto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movimiento_caja_chica"
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimientos_caja_chica"
    )

    movimiento_revertido = models.OneToOneField(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reversion"
    )

    observaciones = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Movimiento de caja chica"
        verbose_name_plural = "Movimientos de caja chica"
        ordering = ["-created_at", "-id"]

        constraints = [
            models.CheckConstraint(
                condition=~models.Q(monto=0),
                name="mov_cajachica_monto_no_cero"
            ),
            models.CheckConstraint(
                condition=models.Q(saldo_nuevo__gte=0),
                name="mov_cajachica_saldo_no_negativo"
            )
        ]

    def __str__(self):
        return (
            f"{self.caja_chica.sucursal} - "
            f"{self.get_tipo_display()} - "
            f"${self.monto}"
        )









