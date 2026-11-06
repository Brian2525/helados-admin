
from decimal import Decimal

from apps.inventario.models import InventarioDiario
from apps.inventario.services import existencia_teorica_diaria


def calcular_conciliacion_diaria(sucursal, fecha):
    """
    Compara el inventario teórico contra el conteo físico
    registrado por los vendedores.

    No modifica el inventario.
    """

    cero = Decimal("0.0000")

    # 1. Existencias calculadas desde el corte autorizado.
    existencias = existencia_teorica_diaria(
        sucursal=sucursal,
        fecha=fecha,
    )

    # 2. Conteos físicos correspondientes a esa fecha.
    inventarios_fisicos = (
        InventarioDiario.objects
        .filter(
            sucursal=sucursal,
            fecha=fecha,
        )
        .select_related("usuario")
    )

    fisicos_por_variante = {
        inventario.variante_id: inventario
        for inventario in inventarios_fisicos
    }

    resultado = []

    resumen = {
        "total": 0,
        "correctos": 0,
        "faltantes": 0,
        "sobrantes": 0,
        "sin_conteo": 0,
        "sin_inicial": 0,
        "con_diferencias": 0,
    }

    for item in existencias:

        variante = item["variante"]

        cantidad_teorica = item["cantidad_teorica"]

        inventario_fisico = fisicos_por_variante.get(
            variante.id
        )

        cantidad_fisica = (
            inventario_fisico.cantidad
            if inventario_fisico is not None
            else None
        )

        diferencia = None

        if cantidad_teorica is None:
            estado = "sin_inicial"
            resumen["sin_inicial"] += 1

        elif cantidad_fisica is None:
            estado = "sin_conteo"
            resumen["sin_conteo"] += 1

        else:
            diferencia = (
                cantidad_fisica - cantidad_teorica
            )

            if diferencia < cero:
                estado = "faltante"
                resumen["faltantes"] += 1

            elif diferencia > cero:
                estado = "sobrante"
                resumen["sobrantes"] += 1

            else:
                estado = "correcto"
                resumen["correctos"] += 1

        resultado.append({
            "variante": variante,
            "inventario_fisico": inventario_fisico,
            "inventario_inicial": item["inventario_inicial"],
            "cantidad_teorica": cantidad_teorica,
            "cantidad_fisica": cantidad_fisica,
            "consumo_teorico": item["consumo_teorico"],
            "movimientos_netos": item["movimientos_netos"],
            "diferencia": diferencia,
            "estado": estado,
        })

        resumen["total"] += 1

    resumen["con_diferencias"] = (
        resumen["faltantes"] + resumen["sobrantes"]
    )

    return {
        "detalles": resultado,
        "resumen": resumen,
    }
