from django.contrib import admin

# Register your models here.
# 
from .models import Promocion, PromocionDetalle

admin.site.register(Promocion)
admin.site.register(PromocionDetalle)
