

# Register your models here.
from django.contrib import admin

from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):

    list_display = (
        "usuario",
        "ventas",
        "gastos",
        "compras",
        "finanzas",
        "inventario",
        "administracion",
        "nomina",
    )