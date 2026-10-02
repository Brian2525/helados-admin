from collections import defaultdict
from decimal import Decimal

from apps.ventas.models import VentaDetalle


def consumo_teorico_periodo(
    sucursal,
    fecha_inicio,
    fecha_fin,
):
    """
    Calcula el consumo teórico de insumos
    a partir de las ventas confirmadas y
    las recetas configuradas.
    """

    detalles_venta = (
        VentaDetalle.objects
        .filter(
            venta__sucursal=sucursal,
            venta__fecha_hora__date__range=(
                fecha_inicio,
                fecha_fin,
            ),
            venta__estado="confirmada",
            variante__receta__activa=True,
        )
        .select_related(
            "variante",
            "variante__producto",
            "variante__receta",
        )
        .prefetch_related(
            "variante__receta__detalles__insumo",
            "variante__receta__detalles__insumo__producto",
        )
    )

    consumos = defaultdict(
        lambda: {
            "cantidad": Decimal("0.0000"),
            "variante": None,
        }
    )

    for detalle_venta in detalles_venta:

        receta = detalle_venta.variante.receta

        for ingrediente in receta.detalles.all():

            consumo = (
                detalle_venta.cantidad
                * ingrediente.cantidad
            )

            insumo = ingrediente.insumo

            consumos[insumo.id]["variante"] = insumo

            consumos[insumo.id]["cantidad"] += consumo

    return list(consumos.values())