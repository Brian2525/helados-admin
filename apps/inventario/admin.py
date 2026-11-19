from django.contrib import admin
from .models import Producto, VarianteProducto, InventarioDiario, Receta, RecetaDetalle, MovimientoInventario, InventarioInicialDetalle

# Register your models here.
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion", "registrar_venta_diaria", "activo", "tipo", "controlar_inventario")
    list_filter = ("activo", "tipo")
    search_fields = ("nombre", "descripcion")

class VarianteProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "producto", "activo")
    list_filter = ("activo", "producto")
    search_fields = ("nombre",)

class InventarioDiarioAdmin(admin.ModelAdmin):
    list_display = ("sucursal", "variante", "fecha", "cantidad")
    list_filter = ("sucursal", "variante", "fecha")
    search_fields = ("sucursal__nombre", "variante__nombre")



class RecetaAdmin(admin.ModelAdmin):
    list_filter = ("activa",)
    


class MovimientoInventarioAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "fecha_hora",
        "sucursal",
        "variante",
        "tipo",
        "cantidad",
        "usuario",
    )

    list_filter = (
        "sucursal",
        "tipo",
        "fecha_hora",
    )

    search_fields = (
        "variante__nombre",
        "variante__producto__nombre",
        "observaciones",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-fecha_hora", "-id")

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    


class InventarioInicialDetalleAdmin(admin.ModelAdmin):
    list_display = ("inventario", "variante", "cantidad")
    search_fields = ("sucursal__nombre", "variante__nombre")
    list_filter = ( "inventario__sucursal", )
    list_select_related = (
        "inventario__sucursal",
        "variante",
    )



admin.site.register(Producto, ProductoAdmin)
admin.site.register(Receta, RecetaAdmin)
admin.site.register(RecetaDetalle)
admin.site.register(MovimientoInventario, MovimientoInventarioAdmin)
admin.site.register(InventarioInicialDetalle, InventarioInicialDetalleAdmin)



admin.site.register(VarianteProducto, VarianteProductoAdmin)
admin.site.register(InventarioDiario, InventarioDiarioAdmin)

