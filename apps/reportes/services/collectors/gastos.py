# apps/reportes/services/collectors/gastos.py

from decimal import Decimal

from django.db.models import Count, Sum

from apps.gastos.models import Gasto


ZERO = Decimal("0.00")
NOMBRE_CATEGORIA_NOMINA = "nómina"


def _normalizar_nombre_categoria(nombre: str | None) -> str:
    return (nombre or "").strip().lower()


def _es_categoria_nomina(nombre: str | None) -> bool:
    return _normalizar_nombre_categoria(nombre) == NOMBRE_CATEGORIA_NOMINA


def _agregar_totales(qs) -> dict:
    total_registrado = qs.aggregate(total=Sum("monto"))["total"] or ZERO

    qs_nomina = qs.filter(categoria__nombre__iexact="Nómina")
    total_categoria_nomina = qs_nomina.aggregate(total=Sum("monto"))["total"] or ZERO

    return {
        "total_registrado": total_registrado,
        "total_categoria_nomina": total_categoria_nomina,
        "total_excluyendo_categoria_nomina": total_registrado - total_categoria_nomina,
        "cantidad_registros": qs.count(),
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


def obtener_metricas_gastos(
    *,
    sucursales_qs,
    inicio,
    fin,
    inicio_anterior,
    fin_anterior,
) -> dict:
    qs_actual = Gasto.objects.filter(
        sucursal__in=sucursales_qs,
        fecha__range=(inicio, fin),
    ).select_related("categoria", "sucursal")

    qs_anterior = Gasto.objects.filter(
        sucursal__in=sucursales_qs,
        fecha__range=(inicio_anterior, fin_anterior),
    ).select_related("categoria", "sucursal")

    actual = _agregar_totales(qs_actual)
    anterior = _agregar_totales(qs_anterior)

    por_categoria_qs = (
        qs_actual
        .values("categoria_id", "categoria__nombre")
        .annotate(
            total=Sum("monto"),
            cantidad_registros=Count("id"),
        )
        .order_by("categoria__nombre")
    )

    por_categoria = []
    total_registrado_actual = actual["total_registrado"] or ZERO

    for item in por_categoria_qs:
        total_categoria = item["total"] or ZERO

        if total_registrado_actual == ZERO:
            participacion = ZERO
        else:
            participacion = (total_categoria / total_registrado_actual) * Decimal("100")

        nombre_categoria = item["categoria__nombre"]

        por_categoria.append(
            {
                "categoria_id": item["categoria_id"],
                "categoria_nombre": nombre_categoria,
                "es_nomina": _es_categoria_nomina(nombre_categoria),
                "total": total_categoria,
                "cantidad_registros": item["cantidad_registros"] or 0,
                "participacion_total_registrado": participacion,
            }
        )

    por_sucursal_qs = (
        qs_actual
        .values("sucursal_id", "sucursal__nombre")
        .annotate(
            total_registrado=Sum("monto"),
            cantidad_registros=Count("id"),
        )
        .order_by("sucursal__nombre")
    )

    por_sucursal = []

    for item in por_sucursal_qs:
        sucursal_id = item["sucursal_id"]

        total_registrado = item["total_registrado"] or ZERO

        total_categoria_nomina = (
            qs_actual
            .filter(
                sucursal_id=sucursal_id,
                categoria__nombre__iexact="Nómina",
            )
            .aggregate(total=Sum("monto"))["total"]
            or ZERO
        )

        por_sucursal.append(
            {
                "sucursal_id": sucursal_id,
                "sucursal_nombre": item["sucursal__nombre"],
                "total_registrado": total_registrado,
                "total_categoria_nomina": total_categoria_nomina,
                "total_excluyendo_categoria_nomina": total_registrado - total_categoria_nomina,
                "cantidad_registros": item["cantidad_registros"] or 0,
            }
        )

    return {
        "actual": actual,
        "periodo_anterior": anterior,
        "comparaciones": {
            "total_registrado": _build_variation(
                actual["total_registrado"],
                anterior["total_registrado"],
            ),
            "total_excluyendo_categoria_nomina": _build_variation(
                actual["total_excluyendo_categoria_nomina"],
                anterior["total_excluyendo_categoria_nomina"],
            ),
        },
        "por_categoria": por_categoria,
        "por_sucursal": por_sucursal,
    }