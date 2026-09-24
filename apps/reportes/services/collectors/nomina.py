from decimal import Decimal

from django.db.models import Count, Sum

from apps.nomina.models import Nomina, PagoNomina


ZERO = Decimal("0.00")


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


def _agregar_pagos(qs) -> dict:
    agregados = qs.aggregate(
        total_pagado=Sum("monto"),
        cantidad_pagos=Count("id"),
        empleados_pagados_distintos=Count("nomina__empleado", distinct=True),
    )

    return {
        "total_pagado": agregados["total_pagado"] or ZERO,
        "cantidad_pagos": agregados["cantidad_pagos"] or 0,
        "empleados_pagados_distintos": agregados["empleados_pagados_distintos"] or 0,
    }


def _agregar_pendientes(qs) -> dict:
    agregados = qs.aggregate(
        cantidad_nominas_vencidas_sin_pago=Count("id"),
        monto_nominal_vencido=Sum("monto"),
    )

    return {
        "cantidad_nominas_vencidas_sin_pago": (
            agregados["cantidad_nominas_vencidas_sin_pago"] or 0
        ),
        "monto_nominal_vencido": agregados["monto_nominal_vencido"] or ZERO,
    }


def obtener_metricas_nomina(
    *,
    sucursales_qs,
    inicio,
    fin,
    inicio_anterior,
    fin_anterior,
) -> dict:
    """
    Criterio v1 seguro:
    - Nómina pagada: PagoNomina por fecha_pago, SOLO si tiene nomina asociada
      y la sucursal del empleado está dentro del alcance.
    - Nómina pendiente al cierre: Nomina sin pago, con fecha_vencimiento <= fin.
    - Pagos con nomina=None se excluyen porque no pueden asignarse confiablemente
      a propietario/sucursal.
    """
    pagos_actual_qs = (
        PagoNomina.objects.filter(
            fecha_pago__range=(inicio, fin),
            nomina__isnull=False,
            nomina__empleado__sucursal__in=sucursales_qs,
        )
        .select_related("nomina", "nomina__empleado", "nomina__empleado__sucursal")
    )

    pagos_anterior_qs = (
        PagoNomina.objects.filter(
            fecha_pago__range=(inicio_anterior, fin_anterior),
            nomina__isnull=False,
            nomina__empleado__sucursal__in=sucursales_qs,
        )
        .select_related("nomina", "nomina__empleado", "nomina__empleado__sucursal")
    )

    actual = _agregar_pagos(pagos_actual_qs)
    anterior = _agregar_pagos(pagos_anterior_qs)

    pendientes_actual_qs = (
        Nomina.objects.filter(
            empleado__sucursal__in=sucursales_qs,
            pago__isnull=True,
            fecha_vencimiento__lte=fin,
        )
        .select_related("empleado", "empleado__sucursal")
    )

    pendientes_al_cierre = _agregar_pendientes(pendientes_actual_qs)

    # Base por sucursal para devolver siempre todas las sucursales del alcance
    sucursales_base = list(
        sucursales_qs.order_by("nombre").values("id", "nombre")
    )

    por_sucursal_map = {
        item["id"]: {
            "sucursal_id": item["id"],
            "sucursal_nombre": item["nombre"],
            "total_pagado": ZERO,
            "cantidad_pagos": 0,
            "empleados_pagados_distintos": 0,
            "cantidad_nominas_vencidas_sin_pago": 0,
            "monto_nominal_vencido": ZERO,
        }
        for item in sucursales_base
    }

    pagadas_por_sucursal_qs = (
        pagos_actual_qs.values(
            "nomina__empleado__sucursal_id",
            "nomina__empleado__sucursal__nombre",
        )
        .annotate(
            total_pagado=Sum("monto"),
            cantidad_pagos=Count("id"),
            empleados_pagados_distintos=Count("nomina__empleado", distinct=True),
        )
        .order_by("nomina__empleado__sucursal__nombre")
    )

    for item in pagadas_por_sucursal_qs:
        sucursal_id = item["nomina__empleado__sucursal_id"]

        if sucursal_id not in por_sucursal_map:
            continue

        por_sucursal_map[sucursal_id]["total_pagado"] = item["total_pagado"] or ZERO
        por_sucursal_map[sucursal_id]["cantidad_pagos"] = item["cantidad_pagos"] or 0
        por_sucursal_map[sucursal_id]["empleados_pagados_distintos"] = (
            item["empleados_pagados_distintos"] or 0
        )

    pendientes_por_sucursal_qs = (
        pendientes_actual_qs.values(
            "empleado__sucursal_id",
            "empleado__sucursal__nombre",
        )
        .annotate(
            cantidad_nominas_vencidas_sin_pago=Count("id"),
            monto_nominal_vencido=Sum("monto"),
        )
        .order_by("empleado__sucursal__nombre")
    )

    for item in pendientes_por_sucursal_qs:
        sucursal_id = item["empleado__sucursal_id"]

        if sucursal_id not in por_sucursal_map:
            continue

        por_sucursal_map[sucursal_id]["cantidad_nominas_vencidas_sin_pago"] = (
            item["cantidad_nominas_vencidas_sin_pago"] or 0
        )
        por_sucursal_map[sucursal_id]["monto_nominal_vencido"] = (
            item["monto_nominal_vencido"] or ZERO
        )

    por_sucursal = list(por_sucursal_map.values())

    return {
        "criterio": {
            "pagada": "PagoNomina.fecha_pago",
            "pendiente_al_cierre": (
                "Nomina sin pago con fecha_vencimiento <= fin del periodo"
            ),
            "incluye_solo_pagos_con_nomina_asociada": True,
            "pagos_sin_nomina_se_excluyen": True,
            "motivo_exclusion_pagos_sin_nomina": (
                "No pueden asignarse confiablemente a propietario ni sucursal."
            ),
        },
        "actual": actual,
        "periodo_anterior": anterior,
        "comparaciones": {
            "total_pagado": _build_variation(
                actual["total_pagado"],
                anterior["total_pagado"],
            ),
        },
        "pendientes_al_cierre": pendientes_al_cierre,
        "por_sucursal": por_sucursal,
    }