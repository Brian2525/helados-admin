from django.contrib import admin
from .models import Producto, VarianteProducto, InventarioDiario, Receta, RecetaDetalle, MovimientoInventario

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
        "naturaleza",
        "usuario",
    )

    list_filter = (
        "sucursal",
        "tipo",
        "motivo_merma",
        "fecha_hora",
    )

    search_fields = (
        "variante__nombre",
        "variante__producto__nombre",
        "sucursal__nombre",
        "observaciones",
    )

    readonly_fields = (
        "sucursal",
        "variante",
        "fecha_hora",
        "tipo",
        "cantidad",
        "motivo_merma",
        "usuario",
        "venta",
        "venta_detalle",
        "observaciones",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "sucursal",
        "variante__producto",
        "usuario",
    )

    ordering = ("-fecha_hora", "-id")

    list_per_page = 30

    @admin.display(description="Movimiento")
    def naturaleza(self, obj):
        if obj.es_entrada:
            return "Entrada (+)"

        if obj.es_salida:
            return "Salida (-)"

        return "Sin clasificar"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    


admin.site.register(Producto, ProductoAdmin)
admin.site.register(Receta, RecetaAdmin)
admin.site.register(RecetaDetalle)
admin.site.register(MovimientoInventario, MovimientoInventarioAdmin)


admin.site.register(VarianteProducto, VarianteProductoAdmin)
admin.site.register(InventarioDiario, InventarioDiarioAdmin)

