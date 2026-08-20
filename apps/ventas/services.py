
from django.db.models import Sum
from decimal import Decimal
from datetime import timedelta
from apps.ventas.models import VentaDiaria, ResumenSemanal
from apps.sucursales.models import Sucursal


def construir_resumen_semanal(sucursal, fecha):

    inicio = fecha - timedelta(days=fecha.weekday())
    fin = inicio + timedelta(days=6)

    ventas = VentaDiaria.objects.filter(
        sucursal=sucursal,
        fecha__range=[inicio, fin]
    )

    totales = ventas.aggregate(
        efectivo=Sum("efectivo"),
        tarjeta=Sum("tarjeta"),
    )

    resumen, created = ResumenSemanal.objects.update_or_create(
        sucursal=sucursal,
        fecha_inicio=inicio,
        fecha_fin=fin,
        defaults={
            "efectivo": totales["efectivo"] or Decimal("0"),
            "tarjeta": totales["tarjeta"] or Decimal("0"),
        }
    )

    return resumen