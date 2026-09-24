# apps/reportes/services/collectors/ventas.py

from decimal import Decimal

from django.db.models import Count, Sum, Value
from django.db.models.functions import Coalesce

from apps.ventas.models import VentaDiaria


ZERO = Decimal("0.00")


def _agregar_totales(qs) -> dict:
    agregados = qs.aggregate(
        efectivo=Coalesce(Sum("efectivo"), Value(ZERO)),
        tarjeta=Coalesce(Sum("tarjeta"), Value(ZERO)),
        registros_diarios=Coalesce(Count("id"), Value(0)),
        fechas_unicas_registradas=Coalesce(Count("fecha", distinct=True), Value(0)),
    )

    efectivo = agregados["efectivo"] or ZERO
    tarjeta = agregados["tarjeta"] or ZERO

    return {
        "total": efectivo + tarjeta,
        "efectivo": efectivo,
        "tarjeta": tarjeta,
        "registros_diarios": agregados["registros_diarios"] or 0,
        "fechas_unicas_registradas": agregados["fechas_unicas_registradas"] or 0,
    }


def _build_variation(actual: Decimal, anterior: Decimal) -> dict:
    variacion_absoluta = actual - anterior

    if anterior == ZERO:
        return {
            "actual": actual,
            "periodo_anterior": anterior,
            "variacion_absoluta": variacion_absoluta,
            "variacion_porcentual": None,
            "comparable": False,
        }

    variacion_porcentual = (variacion_absoluta / anterior) * Decimal("100")

    return {
        "actual": actual,
        "periodo_anterior": anterior,
        "variacion_absoluta": variacion_absoluta,
        "variacion_porcentual": variacion_porcentual,
        "comparable": True,
    }


def obtener_metricas_ventas(
    *,
    sucursales_qs,
    inicio,
    fin,
    inicio_anterior,
    fin_anterior,
) -> dict:
    qs_actual = VentaDiaria.objects.filter(
        sucursal__in=sucursales_qs,
        fecha__range=(inicio, fin),
    )

    qs_anterior = VentaDiaria.objects.filter(
        sucursal__in=sucursales_qs,
        fecha__range=(inicio_anterior, fin_anterior),
    )

    actual = _agregar_totales(qs_actual)
    anterior = _agregar_totales(qs_anterior)

    por_sucursal_qs = (
        qs_actual
        .values("sucursal_id", "sucursal__nombre")
        .annotate(
            efectivo=Coalesce(Sum("efectivo"), Value(ZERO)),
            tarjeta=Coalesce(Sum("tarjeta"), Value(ZERO)),
            registros_diarios=Coalesce(Count("id"), Value(0)),
            fechas_unicas_registradas=Coalesce(Count("fecha", distinct=True), Value(0)),
        )
        .order_by("sucursal__nombre")
    )

    total_actual = actual["total"] or ZERO
    por_sucursal = []

    for item in por_sucursal_qs:
        total_sucursal = (item["efectivo"] or ZERO) + (item["tarjeta"] or ZERO)

        if total_actual == ZERO:
            participacion = ZERO
        else:
            participacion = (total_sucursal / total_actual) * Decimal("100")

        por_sucursal.append(
            {
                "sucursal_id": item["sucursal_id"],
                "sucursal_nombre": item["sucursal__nombre"],
                "total": total_sucursal,
                "efectivo": item["efectivo"] or ZERO,
                "tarjeta": item["tarjeta"] or ZERO,
                "registros_diarios": item["registros_diarios"] or 0,
                "fechas_unicas_registradas": item["fechas_unicas_registradas"] or 0,
                "participacion_total": participacion,
            }
        )

    return {
        "actual": actual,
        "periodo_anterior": anterior,
        "comparaciones": {
            "total": _build_variation(actual["total"], anterior["total"]),
            "efectivo": _build_variation(actual["efectivo"], anterior["efectivo"]),
            "tarjeta": _build_variation(actual["tarjeta"], anterior["tarjeta"]),
        },
        "por_sucursal": por_sucursal,
    }