from django.contrib import admin
from .models import Gasto, CategoriaGasto


class GastoAdmin(admin.ModelAdmin):
    list_display = ['descripcion', 'categoria', 'monto', 'fecha', 'sucursal']
   # list_filter = ['fecha__month', 'fecha__year']


admin.site.register(CategoriaGasto)
admin.site.register(Gasto, GastoAdmin)








# Register your models here.
