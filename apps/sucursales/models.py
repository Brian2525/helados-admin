
# Create your models here.
from django.db import models
from django.contrib.auth.models import User



class Sucursal(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text="Ejemplo: SUR16, SUR20, SUR24"

    )

    usuarios= models.ManyToManyField(
        User,
        related_name="sucursales",
        blank=True,
        )

    direccion = models.TextField(
        blank=True,
        null=True
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    responsable = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    fecha_apertura = models.DateField(
        blank=True,
        null=True
    )

    activa = models.BooleanField(
        default=True
    )

    notas = models.TextField(
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
        ordering = ["nombre"]
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"

    def __str__(self):
        return self.nombre