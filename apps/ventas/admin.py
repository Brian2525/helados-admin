from django.contrib import admin
from .models import ResumenSemanal, Venta, VentaDetalle, VentaDiaria



admin.site.register(ResumenSemanal)
admin.site.register(Venta)
admin.site.register(VentaDetalle)
admin.site.register(VentaDiaria)

# Register your models here.
