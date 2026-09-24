from apps.reportes.services.serializers import serialize_value


def _construir_alcance(*, sucursal, sucursales_qs) -> dict:
    sucursales_incluidas = list(
        sucursales_qs.order_by("nombre").values("id", "nombre")
    )

    return {
        "consolidado": sucursal is None,
        "sucursal_id": sucursal.id if sucursal else None,
        "sucursal_nombre": sucursal.nombre if sucursal else None,
        "sucursales_incluidas": sucursales_incluidas,
    }


def _construir_periodo(*, rango_actual, rango_anterior) -> dict:
    return {
        "anio": rango_actual.anio,
        "mes": rango_actual.mes,
        "inicio": rango_actual.inicio,
        "fin": rango_actual.fin,
        "periodo_anterior": {
            "anio": rango_anterior.anio,
            "mes": rango_anterior.mes,
            "inicio": rango_anterior.inicio,
            "fin": rango_anterior.fin,
        },
    }


def _construir_advertencias(*, ventas, gastos, nomina, cuentas_por_pagar) -> list[dict]:
    advertencias = [
        {
            "codigo": "ventas_sin_detalle_transaccional",
            "detalle": (
                "Las ventas provienen de VentaDiaria y no incluyen tickets "
                "individuales ni detalle por producto."
            ),
        },
        {
            "codigo": "gastos_nomina_pueden_solaparse",
            "detalle": (
                "Gastos y nómina se reportan por separado. Si existen gastos "
                "categorizados como nómina, pueden representar el mismo fenómeno "
                "económico desde otra capa de registro."
            ),
        },
        {
            "codigo": "nomina_sucursal_no_historica",
            "detalle": (
                "La sucursal de nómina se asigna mediante Nomina -> Empleado -> "
                "sucursal actual. Si un empleado cambia de sucursal, la atribución "
                "histórica puede variar."
            ),
        },
        {
            "codigo": "nomina_pagos_sin_nomina_excluidos",
            "detalle": (
                "Los pagos de nómina sin relación a una nómina específica se "
                "excluyen del reporte porque no pueden asignarse confiablemente "
                "a un propietario ni a una sucursal."
            ),
        },
        {
            "codigo": "cuentas_por_pagar_saldo_calculado_por_movimientos",
            "detalle": (
                "Las cuentas por pagar se calculan por fecha de creación, pagos "
                "registrados y saldo acumulado al cierre. No dependen del estatus "
                "actual del modelo."
            ),
        },
    ]

    if ventas.get("actual", {}).get("registros_diarios", 0) == 0:
        advertencias.append(
            {
                "codigo": "ventas_sin_registros_en_periodo",
                "detalle": "No se encontraron registros de ventas en el periodo actual.",
            }
        )

    if gastos.get("actual", {}).get("cantidad_registros", 0) == 0:
        advertencias.append(
            {
                "codigo": "gastos_sin_registros_en_periodo",
                "detalle": "No se encontraron gastos registrados en el periodo actual.",
            }
        )

    if nomina.get("actual", {}).get("cantidad_pagos", 0) == 0:
        advertencias.append(
            {
                "codigo": "nomina_sin_pagos_en_periodo",
                "detalle": "No se encontraron pagos de nómina en el periodo actual.",
            }
        )

    if (
        cuentas_por_pagar.get("actual", {}).get("cuentas_creadas_count", 0) == 0
        and cuentas_por_pagar.get("actual", {}).get("pagos_realizados_count", 0) == 0
        and cuentas_por_pagar.get("actual", {}).get("cuentas_con_saldo_al_cierre", 0) == 0
    ):
        advertencias.append(
            {
                "codigo": "cuentas_por_pagar_sin_movimiento_en_periodo",
                "detalle": (
                    "No se encontraron cuentas por pagar creadas, pagos aplicados "
                    "ni saldos abiertos al cierre en el alcance consultado."
                ),
            }
        )

    return advertencias


def construir_snapshot_reporte_mensual(
    *,
    propietario,
    sucursal,
    sucursales_qs,
    rango_actual,
    rango_anterior,
    generado_por,
    generado_en,
    ventas,
    gastos,
    nomina,
    cuentas_por_pagar,
    sucursales_resumen,
    schema_version=3,
) -> dict:
    snapshot = {
        "schema_version": schema_version,
        "tipo": "reporte_mensual",
        "propietario": {
            "id": propietario.id,
            "username": propietario.username,
        },
        "alcance": _construir_alcance(
            sucursal=sucursal,
            sucursales_qs=sucursales_qs,
        ),
        "periodo": _construir_periodo(
            rango_actual=rango_actual,
            rango_anterior=rango_anterior,
        ),
        "generado": {
            "en": generado_en,
            "por_usuario_id": generado_por.id if generado_por else None,
            "por_username": generado_por.username if generado_por else None,
        },
        "modulos_incluidos": [
            "ventas",
            "gastos",
            "nomina",
            "cuentas_por_pagar",
            "sucursales",
        ],
        "modulos_pendientes": [
            "inventario",
        ],
        "fuentes": {
            "ventas": "VentaDiaria",
            "gastos": "Gasto",
            "nomina_pagada": "PagoNomina",
            "nomina_pendiente": "Nomina",
            "cuentas_por_pagar": "CuentaPorPagar",
            "pagos_cuentas_por_pagar": "PagoCuentaPorPagar",
        },
        "ventas": ventas,
        "gastos": gastos,
        "nomina": nomina,
        "cuentas_por_pagar": cuentas_por_pagar,
        "sucursales": sucursales_resumen,
        "advertencias": _construir_advertencias(
            ventas=ventas,
            gastos=gastos,
            nomina=nomina,
            cuentas_por_pagar=cuentas_por_pagar,
        ),
    }

    return serialize_value(snapshot)