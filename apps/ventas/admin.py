from django.contrib import admin
from .models import ResumenSemanal, Venta, VentaDetalle, VentaDiaria



# Register your models here.



class VentaAdmin(admin.ModelAdmin):
    list_display = ("sucursal" ,"fecha_hora", "total", "usuario")
    list_filter = ("sucursal", "usuario", "fecha_hora")
    search_fields = ("sucursal__nombre", "usuario__username")


class VentaDiariaAdmin(admin.ModelAdmin): 
    list_display=("sucursal","fecha",)


class VentaDetalleAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "sucursal",
        "venta",
        "variante",
        "cantidad",
        "precio_unitario",
        "subtotal",
    )

    list_filter = (
        ("venta__sucursal", admin.RelatedOnlyFieldListFilter),
        ("variante", admin.RelatedOnlyFieldListFilter),
        "venta__fecha_hora",
    )

    search_fields = (
        "venta__sucursal__nombre",
        "producto_nombre",
        "variante_nombre",
        "variante__producto__nombre",
    )

    list_select_related = (
        "venta",
        "venta__sucursal",
        "variante",
    )

    list_per_page = 50

    @admin.display(
        description="Sucursal",
        ordering="venta__sucursal__nombre"
    )
    def sucursal(self, obj):
        return obj.venta.sucursal

class ResumenSemanalAdmin(admin.ModelAdmin):
    list_display = ("sucursal", "fecha_inicio", "fecha_fin", "total_ventas", "total_gastos",)
    list_filter = ("sucursal", "fecha_inicio", "fecha_fin")
    search_fields = ("sucursal__nombre",)



admin.site.register(VentaDetalle, VentaDetalleAdmin)
admin.site.register(ResumenSemanal, ResumenSemanalAdmin)
admin.site.register(Venta, VentaAdmin)
admin.site.register(VentaDiaria,VentaDiariaAdmin)
