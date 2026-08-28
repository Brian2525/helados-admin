from django.contrib import admin
from .models import Producto, VarianteProducto, InventarioDiario

# Register your models here.
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion", "registrar_venta_diaria", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre", "descripcion")

class VarianteProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "producto", "activo")
    list_filter = ("activo", "producto")
    search_fields = ("nombre",)

class InventarioDiarioAdmin(admin.ModelAdmin):
    list_display = ("sucursal", "variante", "fecha", "cantidad")
    list_filter = ("sucursal", "variante", "fecha")
    search_fields = ("sucursal__nombre", "variante__nombre")

admin.site.register(Producto, ProductoAdmin)
admin.site.register(VarianteProducto, VarianteProductoAdmin)
admin.site.register(InventarioDiario, InventarioDiarioAdmin)

