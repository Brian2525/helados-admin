
from django.utils import timezone

from apps.sucursales.models import Sucursal
from apps.inventario.models import (
    VarianteProducto,
    InventarioDiario,
    InventarioInicialAutorizado,
)


def obtener_alertas_inventario(fecha):
    """
    Genera alertas de inventario para todas las
    sucursales activas.

    No modifica datos.
    Sólo evalúa días anteriores al actual.
    """

    hoy = timezone.localdate()

    if fecha >= hoy:
        return {
            "alertas": [],
            "resumen": {},
            "aviso": (
                "Selecciona un día anterior a hoy "
                "para revisar cierres finalizados."
            ),
        }

    sucursales = Sucursal.objects.filter(
        activa=True
    ).order_by("nombre")

    variantes = list(
        VarianteProducto.objects.filter(
            activo=True,
            producto__activo=True,
            producto__controlar_inventario=True,
        ).select_related("producto")
    )

    variantes_por_id = {
        variante.id: variante
        for variante in variantes
    }

    ids_variantes = set(variantes_por_id)

    alertas = []

    resumen = {
        "faltantes": 0,
        "sobrantes": 0,
        "sin_conteo": 0,
        "sin_cierre": 0,
        "sin_teorico": 0,
        "sin_inicial": 0,
        "correctos": 0,
        "sucursales_evaluadas": 0,
    }

    for sucursal in sucursales:

        corte = (
            InventarioInicialAutorizado.objects
            .filter(
                sucursal=sucursal,
                estado=(
                    InventarioInicialAutorizado
                    .Estado.AUTORIZADO
                ),
            )
            .order_by("-fecha_corte", "-id")
            .first()
        )

        # Todavía no tiene inventario inicial oficial.
        if corte is None or corte.fecha_corte is None:

            resumen["sin_inicial"] += 1

            alertas.append({
                "sucursal": sucursal,
                "variante": None,
                "tipo": "sin_inicial",
                "descripcion": (
                    "La sucursal no tiene inventario "
                    "inicial autorizado."
                ),
                "fisico": None,
                "teorico": None,
                "diferencia": None,
            })

            continue

        fecha_corte = timezone.localtime(
            corte.fecha_corte
        ).date()

        # Un día anterior o igual al día de inicio
        # no representa una jornada completa posterior.
        if fecha <= fecha_corte:
            continue

        resumen["sucursales_evaluadas"] += 1

        conteos = list(
            InventarioDiario.objects
            .filter(
                sucursal=sucursal,
                fecha=fecha,
                variante_id__in=ids_variantes,
            )
            .select_related("usuario")
        )

        conteos_por_variante = {
            conteo.variante_id: conteo
            for conteo in conteos
        }

        if not conteos:

            resumen["sin_cierre"] += 1

            alertas.append({
                "sucursal": sucursal,
                "variante": None,
                "tipo": "sin_cierre",
                "descripcion": (
                    "No se registró ningún conteo "
                    "de inventario para esta fecha."
                ),
                "fisico": None,
                "teorico": None,
                "diferencia": None,
            })

            continue

        for variante_id, variante in variantes_por_id.items():

            conteo = conteos_por_variante.get(
                variante_id
            )

            if conteo is None:

                resumen["sin_conteo"] += 1

                alertas.append({
                    "sucursal": sucursal,
                    "variante": variante,
                    "tipo": "sin_conteo",
                    "descripcion": (
                        "El producto no tiene conteo físico."
                    ),
                    "fisico": None,
                    "teorico": None,
                    "diferencia": None,
                })

                continue

            if conteo.cantidad_teorica is None:

                resumen["sin_teorico"] += 1

                alertas.append({
                    "sucursal": sucursal,
                    "variante": variante,
                    "tipo": "sin_teorico",
                    "descripcion": (
                        "El conteo no tiene saldo teórico "
                        "guardado al cierre."
                    ),
                    "fisico": conteo.cantidad,
                    "teorico": None,
                    "diferencia": None,
                })

                continue

            diferencia = (
                conteo.cantidad
                - conteo.cantidad_teorica
            )

            if diferencia == 0:
                resumen["correctos"] += 1
                continue

            tipo = (
                "faltante"
                if diferencia < 0
                else "sobrante"
            )

            resumen[
                "faltantes" if diferencia < 0 else "sobrantes"
            ] += 1

            alertas.append({
                "sucursal": sucursal,
                "variante": variante,
                "tipo": tipo,
                "descripcion": (
                    "Diferencia detectada entre el "
                    "conteo físico y el saldo teórico."
                ),
                "fisico": conteo.cantidad,
                "teorico": conteo.cantidad_teorica,
                "diferencia": diferencia,
            })

    prioridad = {
        "faltante": 0,
        "sin_cierre": 1,
        "sin_conteo": 2,
        "sin_teorico": 3,
        "sobrante": 4,
        "sin_inicial": 5,
    }

    alertas.sort(
        key=lambda a: (
            prioridad.get(a["tipo"], 99),
            a["sucursal"].nombre,
        )
    )

    resumen["total_alertas"] = len(alertas)

    return {
        "alertas": alertas,
        "resumen": resumen,
        "aviso": None,
    }
