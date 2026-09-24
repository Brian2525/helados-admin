from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.sucursales.models import Sucursal


class ReporteMensual(models.Model):
    propietario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="reportes_mensuales"
    )

    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name="reportes_mensuales",
        null=True,
        blank=True,
        help_text="NULL representa un reporte consolidado de todas las sucursales del propietario."
    )

    anio = models.PositiveIntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2100)]
    )

    mes = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )

    datos = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot JSON del reporte mensual."
    )

    schema_version = models.PositiveSmallIntegerField(
        default=2
    )

    generado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reportes_mensuales_generados"
    )

    generado_en = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha/hora en que se generó o regeneró el snapshot actual."
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-anio", "-mes", "sucursal__nombre"]
        verbose_name = "Reporte mensual"
        verbose_name_plural = "Reportes mensuales"
        constraints = [
            models.CheckConstraint(
                check=Q(mes__gte=1) & Q(mes__lte=12),
                name="reporte_mensual_mes_valido"
            ),
            models.CheckConstraint(
                check=Q(anio__gte=2000) & Q(anio__lte=2100),
                name="reporte_mensual_anio_valido"
            ),
            models.UniqueConstraint(
                fields=["propietario", "sucursal", "anio", "mes"],
                condition=Q(sucursal__isnull=False),
                name="uniq_reporte_mensual_propietario_sucursal_periodo"
            ),
            models.UniqueConstraint(
                fields=["propietario", "anio", "mes"],
                condition=Q(sucursal__isnull=True),
                name="uniq_reporte_mensual_propietario_consolidado_periodo"
            ),
        ]
        indexes = [
            models.Index(fields=["propietario", "anio", "mes"]),
            models.Index(fields=["sucursal", "anio", "mes"]),
            models.Index(fields=["generado_en"]),
        ]

    def clean(self):
        if self.sucursal and self.sucursal.propietario_id != self.propietario_id:
            raise ValidationError(
                {
                    "sucursal": (
                        "La sucursal seleccionada no pertenece al propietario del reporte."
                    )
                }
            )

    @property
    def es_consolidado(self):
        return self.sucursal_id is None

    def __str__(self):
        alcance = (
            "Consolidado"
            if self.es_consolidado
            else self.sucursal.nombre
        )
        return f"{alcance} - {self.mes:02d}/{self.anio}"