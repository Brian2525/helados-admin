from django.contrib import admin
from django.utils.html import format_html

from .models import Producto, VarianteProducto, InventarioDiario, Receta, RecetaDetalle, MovimientoInventario, InventarioInicialDetalle, CategoriaProducto 




@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "activa",
    )

    search_fields = ("nombre",)
    list_filter = ("activa",)



# Register your models here.
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "categoria",
        "tipo",
        "vista_previa",
        "registrar_venta_diaria",
        "activo",
    )

    list_filter = (
        "activo",
        "tipo",
        "categoria",
    )

    search_fields = (
        "nombre",
        "descripcion",
    )

    readonly_fields = ("vista_previa",)

    def vista_previa(self, obj):
        if obj and obj.imagen:
            return format_html(
                '<img src="{}" '
                'style="width:70px;height:70px;'
                'object-fit:contain;border-radius:8px;">',
                obj.imagen.url,
            )
        return "Sin imagen"

    vista_previa.short_description = "Fotografía"


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

