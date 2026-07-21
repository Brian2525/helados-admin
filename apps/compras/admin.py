from django.contrib import admin
from .models import Proveedor, CuentaPorPagar


class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'correo', 'activo']
    search_fields = ['nombre', 'telefono', 'correo']


class CuentaPorPagarAdmin(admin.ModelAdmin):
    list_display = ['proveedor', 'monto_total', 'fecha_vencimiento']
    list_filter = [ 'fecha_vencimiento']
    search_fields = ['proveedor__nombre', 'monto_total']



admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(CuentaPorPagar, CuentaPorPagarAdmin)

# Register your models here.
