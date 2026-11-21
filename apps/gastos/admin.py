from django.contrib import admin
from .models import Gasto, CategoriaGasto, CajaChica, MovimientoCajaChica



class GastoAdmin(admin.ModelAdmin):
    list_display = ['descripcion', 'categoria', 'monto', 'fecha', 'sucursal']
    list_filter = ['sucursal', 'categoria']



admin.site.register(CategoriaGasto)
admin.site.register(Gasto, GastoAdmin)
admin.site.register(CajaChica)
admin.site.register(MovimientoCajaChica)









# Register your models here.
