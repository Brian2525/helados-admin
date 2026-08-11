from django.db import models
from django.contrib.auth.models import User




class PerfilUsuario(models.Model):

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil"
    )

    dashboard = models.BooleanField(default=False)

    ventas = models.BooleanField(default=False)      # Ventas, cortes, devoluciones

    gastos= models.BooleanField(default=False)      # Gastos, cuentas por pagar, servicios

    compras = models.BooleanField(default=False)    # Compras, proveedores, inventario

    finanzas = models.BooleanField(default=False)    # Gastos, cuentas por pagar, servicios

    inventario = models.BooleanField(default=False)  # Inventario, compras, proveedores

    nomina = models.BooleanField(default=False)

    administracion = models.BooleanField(default=False)