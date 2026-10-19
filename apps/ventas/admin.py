from django.contrib import admin
from .models import ResumenSemanal, Venta, VentaDetalle, VentaDiaria



admin.site.register(ResumenSemanal)
admin.site.register(Venta)
admin.site.register(VentaDetalle)
admin.site.register(VentaDiaria)

# Register your models here.



class VentaAdmin(admin.ModelAdmin):
    list_display = ("sucursal", "fecha", "total", "usuario")
    list_filter = ("sucursal", "fecha", "usuario")
    search_fields = ("sucursal__nombre", "usuario__username")



class VentaDetalleAdmin(admin.ModelAdmin):
    list_display = ("venta", "variante_producto", "cantidad", "precio_unitario", "total")
    list_filter = ("venta__sucursal", "variante_producto")
    search_fields = ("venta__sucursal__nombre", "variante_producto__nombre")

class VentaDiariaAdmin(admin.ModelAdmin):
    list_display = ("sucursal", "fecha", "total_ventas", "total_gastos", "total_cierre")
    list_filter = ("sucursal", "fecha")
    search_fields = ("sucursal__nombre",)

class ResumenSemanalAdmin(admin.ModelAdmin):
    list_display = ("sucursal", "fecha_inicio", "fecha_fin", "total_ventas", "total_gastos", "total_cierre")
    list_filter = ("sucursal", "fecha_inicio", "fecha_fin")
    search_fields = ("sucursal__nombre",)


