from django.contrib import admin

# Register your models here.
# 
from .models import Promocion, PromocionDetalle


class PromocionAdmin(admin.ModelAdmin):

    list_display = (
        "nombre",
        "tipo",
        "activa",
        "fecha_inicio",
        "fecha_fin",
    )


class PromocionDetalleAdmin(admin.ModelAdmin):

    list_display = (
        "promocion",
        "producto",
        "cantidad",
        "precio",
        "descuento",
    )




admin.site.register(Promocion, PromocionAdmin)
admin.site.register(PromocionDetalle)
