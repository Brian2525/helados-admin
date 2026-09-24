from decimal import Decimal

from django.db.models import Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce

from apps.compras.models import CuentaPorPagar, PagoCuentaPorPagar


ZERO = Decimal("0.00")
MONEY_FIELD = DecimalField(max_digits=14, decimal_places=2)


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


def _agregar_cuentas_creadas(qs) -> dict:
    agregados = qs.aggregate(
        cuentas_creadas_total=Coalesce(
            Sum("monto_total", output_field=MONEY_FIELD),
            Value(ZERO),
            output_field=MONEY_FIELD,
        ),
        cuentas_creadas_count=Count("id"),
    )

    return {
        "cuentas_creadas_total": agregados["cuentas_creadas_total"] or ZERO,
        "cuentas_creadas_count": agregados["cuentas_creadas_count"] or 0,
    }


def _agregar_pagos_realizados(qs) -> dict:
    agregados = qs.aggregate(
        pagos_realizados_total=Coalesce(
            Sum("monto", output_field=MONEY_FIELD),
            Value(ZERO),
            output_field=MONEY_FIELD,
        ),
        pagos_realizados_count=Count("id"),
    )

    return {
        "pagos_realizados_total": agregados["pagos_realizados_total"] or ZERO,
        "pagos_realizados_count": agregados["pagos_realizados_count"] or 0,
    }


def _obtener_cuentas_al_cierre(*, sucursales_qs, fecha_corte):
    qs = (
        CuentaPorPagar.objects.filter(
            sucursal__in=sucursales_qs,
            fecha__lte=fecha_corte,
        )
        .select_related("sucursal", "categoria", "proveedor")
        .annotate(
            pagado_hasta_cierre=Coalesce(
                Sum(
                    "pagos__monto",
                    filter=Q(pagos__fecha__lte=fecha_corte),
                    output_field=MONEY_FIELD,
                ),
                Value(ZERO),
                output_field=MONEY_FIELD,
            )
        )
        .order_by("sucursal__nombre", "fecha_vencimiento", "id")
    )

    cuentas = []

    for cuenta in qs:
        saldo_al_cierre = (cuenta.monto_total or ZERO) - (cuenta.pagado_hasta_cierre or ZERO)

        if saldo_al_cierre < ZERO:
            saldo_al_cierre = ZERO

        vencida_al_cierre = (
            saldo_al_cierre > ZERO and
            cuenta.fecha_vencimiento <= fecha_corte
        )

        cuentas.append(
            {
                "cuenta_id": cuenta.id,
                "sucursal_id": cuenta.sucursal_id,
                "sucursal_nombre": cuenta.sucursal.nombre,
                "categoria_id": cuenta.categoria_id,
                "categoria_nombre": cuenta.categoria.nombre if cuenta.categoria_id else None,
                "proveedor_id": cuenta.proveedor_id,
                "proveedor_nombre": cuenta.proveedor.nombre if cuenta.proveedor_id else None,
                "fecha": cuenta.fecha,
                "fecha_vencimiento": cuenta.fecha_vencimiento,
                "monto_total": cuenta.monto_total or ZERO,
                "pagado_hasta_cierre": cuenta.pagado_hasta_cierre or ZERO,
                "saldo_al_cierre": saldo_al_cierre,
                "vencida_al_cierre": vencida_al_cierre,
            }
        )

    return cuentas


def _agregar_saldos_al_cierre(cuentas: list[dict]) -> dict:
    saldo_abierto = ZERO
    cuentas_con_saldo = 0
    saldo_vencido = ZERO
    cuentas_vencidas = 0

    for cuenta in cuentas:
        saldo = cuenta["saldo_al_cierre"]

        if saldo > ZERO:
            saldo_abierto += saldo
            cuentas_con_saldo += 1

            if cuenta["vencida_al_cierre"]:
                saldo_vencido += saldo
                cuentas_vencidas += 1

    return {
        "saldo_abierto_al_cierre": saldo_abierto,
        "cuentas_con_saldo_al_cierre": cuentas_con_saldo,
        "saldo_vencido_al_cierre": saldo_vencido,
        "cuentas_vencidas_al_cierre": cuentas_vencidas,
    }


def _combinar_metricas(*, cuentas_creadas: dict, pagos_realizados: dict, saldos_al_cierre: dict) -> dict:
    return {
        **cuentas_creadas,
        **pagos_realizados,
        **saldos_al_cierre,
    }


def _construir_por_sucursal(
    *,
    sucursales_qs,
    cuentas_creadas_qs,
    pagos_realizados_qs,
    cuentas_al_cierre: list[dict],
) -> list[dict]:
    sucursales_base = list(
        sucursales_qs.order_by("nombre").values("id", "nombre")
    )

    resultado = {
        item["id"]: {
            "sucursal_id": item["id"],
            "sucursal_nombre": item["nombre"],
            "cuentas_creadas_total": ZERO,
            "cuentas_creadas_count": 0,
            "pagos_realizados_total": ZERO,
            "pagos_realizados_count": 0,
            "saldo_abierto_al_cierre": ZERO,
            "cuentas_con_saldo_al_cierre": 0,
            "saldo_vencido_al_cierre": ZERO,
            "cuentas_vencidas_al_cierre": 0,
        }
        for item in sucursales_base
    }

    creadas_por_sucursal = (
        cuentas_creadas_qs.values("sucursal_id", "sucursal__nombre")
        .annotate(
            cuentas_creadas_total=Coalesce(
                Sum("monto_total", output_field=MONEY_FIELD),
                Value(ZERO),
                output_field=MONEY_FIELD,
            ),
            cuentas_creadas_count=Count("id"),
        )
        .order_by("sucursal__nombre")
    )

    for item in creadas_por_sucursal:
        sucursal_id = item["sucursal_id"]
        if sucursal_id not in resultado:
            continue

        resultado[sucursal_id]["cuentas_creadas_total"] = item["cuentas_creadas_total"] or ZERO
        resultado[sucursal_id]["cuentas_creadas_count"] = item["cuentas_creadas_count"] or 0

    pagos_por_sucursal = (
        pagos_realizados_qs.values("cuenta__sucursal_id", "cuenta__sucursal__nombre")
        .annotate(
            pagos_realizados_total=Coalesce(
                Sum("monto", output_field=MONEY_FIELD),
                Value(ZERO),
                output_field=MONEY_FIELD,
            ),
            pagos_realizados_count=Count("id"),
        )
        .order_by("cuenta__sucursal__nombre")
    )

    for item in pagos_por_sucursal:
        sucursal_id = item["cuenta__sucursal_id"]
        if sucursal_id not in resultado:
            continue

        resultado[sucursal_id]["pagos_realizados_total"] = item["pagos_realizados_total"] or ZERO
        resultado[sucursal_id]["pagos_realizados_count"] = item["pagos_realizados_count"] or 0

    for cuenta in cuentas_al_cierre:
        sucursal_id = cuenta["sucursal_id"]
        if sucursal_id not in resultado:
            continue

        saldo = cuenta["saldo_al_cierre"]

        if saldo > ZERO:
            resultado[sucursal_id]["saldo_abierto_al_cierre"] += saldo
            resultado[sucursal_id]["cuentas_con_saldo_al_cierre"] += 1

            if cuenta["vencida_al_cierre"]:
                resultado[sucursal_id]["saldo_vencido_al_cierre"] += saldo
                resultado[sucursal_id]["cuentas_vencidas_al_cierre"] += 1

    return list(resultado.values())


def _construir_por_categoria(
    *,
    cuentas_creadas_qs,
    cuentas_al_cierre: list[dict],
) -> list[dict]:
    resultado = {}

    creadas_por_categoria = (
        cuentas_creadas_qs.values("categoria_id", "categoria__nombre")
        .annotate(
            cuentas_creadas_total=Coalesce(
                Sum("monto_total", output_field=MONEY_FIELD),
                Value(ZERO),
                output_field=MONEY_FIELD,
            ),
            cuentas_creadas_count=Count("id"),
        )
        .order_by("categoria__nombre")
    )

    for item in creadas_por_categoria:
        categoria_id = item["categoria_id"]

        resultado[categoria_id] = {
            "categoria_id": categoria_id,
            "categoria_nombre": item["categoria__nombre"],
            "cuentas_creadas_total": item["cuentas_creadas_total"] or ZERO,
            "cuentas_creadas_count": item["cuentas_creadas_count"] or 0,
            "saldo_abierto_al_cierre": ZERO,
            "cuentas_con_saldo_al_cierre": 0,
        }

    for cuenta in cuentas_al_cierre:
        categoria_id = cuenta["categoria_id"]
        saldo = cuenta["saldo_al_cierre"]

        if categoria_id not in resultado:
            resultado[categoria_id] = {
                "categoria_id": categoria_id,
                "categoria_nombre": cuenta["categoria_nombre"],
                "cuentas_creadas_total": ZERO,
                "cuentas_creadas_count": 0,
                "saldo_abierto_al_cierre": ZERO,
                "cuentas_con_saldo_al_cierre": 0,
            }

        if saldo > ZERO:
            resultado[categoria_id]["saldo_abierto_al_cierre"] += saldo
            resultado[categoria_id]["cuentas_con_saldo_al_cierre"] += 1

    return sorted(resultado.values(), key=lambda x: (x["categoria_nombre"] or ""))


def _construir_top_proveedores(
    *,
    cuentas_al_cierre: list[dict],
    limite: int = 5,
) -> list[dict]:
    resultado = {}

    for cuenta in cuentas_al_cierre:
        proveedor_id = cuenta["proveedor_id"]
        saldo = cuenta["saldo_al_cierre"]

        if proveedor_id is None or saldo <= ZERO:
            continue

        if proveedor_id not in resultado:
            resultado[proveedor_id] = {
                "proveedor_id": proveedor_id,
                "proveedor_nombre": cuenta["proveedor_nombre"],
                "saldo_abierto_al_cierre": ZERO,
                "cuentas_con_saldo_al_cierre": 0,
                "saldo_vencido_al_cierre": ZERO,
            }

        resultado[proveedor_id]["saldo_abierto_al_cierre"] += saldo
        resultado[proveedor_id]["cuentas_con_saldo_al_cierre"] += 1

        if cuenta["vencida_al_cierre"]:
            resultado[proveedor_id]["saldo_vencido_al_cierre"] += saldo

    proveedores = sorted(
        resultado.values(),
        key=lambda x: x["saldo_abierto_al_cierre"],
        reverse=True,
    )

    return proveedores[:limite]


def obtener_metricas_cuentas_por_pagar(
    *,
    sucursales_qs,
    inicio,
    fin,
    inicio_anterior,
    fin_anterior,
) -> dict:
    cuentas_creadas_actual_qs = CuentaPorPagar.objects.filter(
        sucursal__in=sucursales_qs,
        fecha__range=(inicio, fin),
    ).select_related("sucursal", "categoria", "proveedor")

    cuentas_creadas_anterior_qs = CuentaPorPagar.objects.filter(
        sucursal__in=sucursales_qs,
        fecha__range=(inicio_anterior, fin_anterior),
    ).select_related("sucursal", "categoria", "proveedor")

    pagos_actual_qs = PagoCuentaPorPagar.objects.filter(
        cuenta__sucursal__in=sucursales_qs,
        fecha__range=(inicio, fin),
    ).select_related("cuenta", "cuenta__sucursal", "cuenta__categoria", "cuenta__proveedor")

    pagos_anterior_qs = PagoCuentaPorPagar.objects.filter(
        cuenta__sucursal__in=sucursales_qs,
        fecha__range=(inicio_anterior, fin_anterior),
    ).select_related("cuenta", "cuenta__sucursal", "cuenta__categoria", "cuenta__proveedor")

    cuentas_al_cierre_actual = _obtener_cuentas_al_cierre(
        sucursales_qs=sucursales_qs,
        fecha_corte=fin,
    )

    cuentas_al_cierre_anterior = _obtener_cuentas_al_cierre(
        sucursales_qs=sucursales_qs,
        fecha_corte=fin_anterior,
    )

    actual = _combinar_metricas(
        cuentas_creadas=_agregar_cuentas_creadas(cuentas_creadas_actual_qs),
        pagos_realizados=_agregar_pagos_realizados(pagos_actual_qs),
        saldos_al_cierre=_agregar_saldos_al_cierre(cuentas_al_cierre_actual),
    )

    anterior = _combinar_metricas(
        cuentas_creadas=_agregar_cuentas_creadas(cuentas_creadas_anterior_qs),
        pagos_realizados=_agregar_pagos_realizados(pagos_anterior_qs),
        saldos_al_cierre=_agregar_saldos_al_cierre(cuentas_al_cierre_anterior),
    )

    por_sucursal = _construir_por_sucursal(
        sucursales_qs=sucursales_qs,
        cuentas_creadas_qs=cuentas_creadas_actual_qs,
        pagos_realizados_qs=pagos_actual_qs,
        cuentas_al_cierre=cuentas_al_cierre_actual,
    )

    por_categoria = _construir_por_categoria(
        cuentas_creadas_qs=cuentas_creadas_actual_qs,
        cuentas_al_cierre=cuentas_al_cierre_actual,
    )

    top_proveedores = _construir_top_proveedores(
        cuentas_al_cierre=cuentas_al_cierre_actual,
        limite=5,
    )

    return {
        "criterio": {
            "obligaciones_creadas": "CuentaPorPagar.fecha",
            "pagos_realizados": "PagoCuentaPorPagar.fecha",
            "saldo_al_cierre": "monto_total - pagos acumulados con fecha <= fin_del_periodo",
            "vencida_al_cierre": (
                "saldo_al_cierre > 0 y fecha_vencimiento <= fin_del_periodo"
            ),
            "usa_estatus_modelo_actual": False,
        },
        "actual": actual,
        "periodo_anterior": anterior,
        "comparaciones": {
            "cuentas_creadas_total": _build_variation(
                actual["cuentas_creadas_total"],
                anterior["cuentas_creadas_total"],
            ),
            "pagos_realizados_total": _build_variation(
                actual["pagos_realizados_total"],
                anterior["pagos_realizados_total"],
            ),
            "saldo_abierto_al_cierre": _build_variation(
                actual["saldo_abierto_al_cierre"],
                anterior["saldo_abierto_al_cierre"],
            ),
        },
        "por_sucursal": por_sucursal,
        "por_categoria": por_categoria,
        "top_proveedores": top_proveedores,
    }