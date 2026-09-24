from decimal import Decimal

ZERO = Decimal("0.00")


def obtener_resumen_sucursales(
    *,
    sucursales_qs,
    ventas,
    gastos,
    nomina,
    cuentas_por_pagar=None,
) -> list[dict]:
    sucursales_base = list(
        sucursales_qs.order_by("nombre").values("id", "nombre", "activa")
    )

    resumen_map = {
        item["id"]: {
            "id": item["id"],
            "nombre": item["nombre"],
            "activa": item["activa"],
            "ventas": {
                "total": ZERO,
                "efectivo": ZERO,
                "tarjeta": ZERO,
                "registros_diarios": 0,
                "fechas_unicas_registradas": 0,
            },
            "gastos": {
                "total_registrado": ZERO,
                "total_categoria_nomina": ZERO,
                "total_excluyendo_categoria_nomina": ZERO,
                "cantidad_registros": 0,
            },
            "nomina": {
                "total_pagado": ZERO,
                "cantidad_pagos": 0,
                "empleados_pagados_distintos": 0,
                "cantidad_nominas_vencidas_sin_pago": 0,
                "monto_nominal_vencido": ZERO,
            },
            "cuentas_por_pagar": {
                "cuentas_creadas_total": ZERO,
                "cuentas_creadas_count": 0,
                "pagos_realizados_total": ZERO,
                "pagos_realizados_count": 0,
                "saldo_abierto_al_cierre": ZERO,
                "cuentas_con_saldo_al_cierre": 0,
                "saldo_vencido_al_cierre": ZERO,
                "cuentas_vencidas_al_cierre": 0,
            },
        }
        for item in sucursales_base
    }

    for item in ventas.get("por_sucursal", []):
        sucursal_id = item["sucursal_id"]
        if sucursal_id not in resumen_map:
            continue

        resumen_map[sucursal_id]["ventas"] = {
            "total": item.get("total", ZERO),
            "efectivo": item.get("efectivo", ZERO),
            "tarjeta": item.get("tarjeta", ZERO),
            "registros_diarios": item.get("registros_diarios", 0),
            "fechas_unicas_registradas": item.get("fechas_unicas_registradas", 0),
        }

    for item in gastos.get("por_sucursal", []):
        sucursal_id = item["sucursal_id"]
        if sucursal_id not in resumen_map:
            continue

        resumen_map[sucursal_id]["gastos"] = {
            "total_registrado": item.get("total_registrado", ZERO),
            "total_categoria_nomina": item.get("total_categoria_nomina", ZERO),
            "total_excluyendo_categoria_nomina": item.get(
                "total_excluyendo_categoria_nomina",
                ZERO,
            ),
            "cantidad_registros": item.get("cantidad_registros", 0),
        }

    for item in nomina.get("por_sucursal", []):
        sucursal_id = item["sucursal_id"]
        if sucursal_id not in resumen_map:
            continue

        resumen_map[sucursal_id]["nomina"] = {
            "total_pagado": item.get("total_pagado", ZERO),
            "cantidad_pagos": item.get("cantidad_pagos", 0),
            "empleados_pagados_distintos": item.get("empleados_pagados_distintos", 0),
            "cantidad_nominas_vencidas_sin_pago": item.get(
                "cantidad_nominas_vencidas_sin_pago",
                0,
            ),
            "monto_nominal_vencido": item.get("monto_nominal_vencido", ZERO),
        }

    if cuentas_por_pagar:
        for item in cuentas_por_pagar.get("por_sucursal", []):
            sucursal_id = item["sucursal_id"]
            if sucursal_id not in resumen_map:
                continue

            resumen_map[sucursal_id]["cuentas_por_pagar"] = {
                "cuentas_creadas_total": item.get("cuentas_creadas_total", ZERO),
                "cuentas_creadas_count": item.get("cuentas_creadas_count", 0),
                "pagos_realizados_total": item.get("pagos_realizados_total", ZERO),
                "pagos_realizados_count": item.get("pagos_realizados_count", 0),
                "saldo_abierto_al_cierre": item.get("saldo_abierto_al_cierre", ZERO),
                "cuentas_con_saldo_al_cierre": item.get(
                    "cuentas_con_saldo_al_cierre",
                    0,
                ),
                "saldo_vencido_al_cierre": item.get("saldo_vencido_al_cierre", ZERO),
                "cuentas_vencidas_al_cierre": item.get(
                    "cuentas_vencidas_al_cierre",
                    0,
                ),
            }

    return list(resumen_map.values())