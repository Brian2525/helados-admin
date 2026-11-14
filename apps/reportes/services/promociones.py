from django.db.models import Count, Sum
from apps.ventas.models import VentaPromocion


def reporte_promociones(
    fecha_inicio=None,
    fecha_fin=None,
    sucursal_id=None,
    promocion_id=None,
    tipo=None,
    sucursales_ids=None,
):

    registros = VentaPromocion.objects.filter(
        venta__estado="confirmada"
    )

    if fecha_inicio:
        registros = registros.filter(
            venta__fecha_hora__date__gte=fecha_inicio
        )

    if fecha_fin:
        registros = registros.filter(
            venta__fecha_hora__date__lte=fecha_fin
        )

    if sucursales_ids is not None:
        registros = registros.filter(
            venta__sucursal_id__in=sucursales_ids
        )

    if promocion_id:
        registros = registros.filter(
            promocion_id=promocion_id
        )

    if tipo:
        registros = registros.filter(
            tipo=tipo
        )

    resumen = registros.aggregate(
        tickets=Count("venta_id", distinct=True),
        aplicaciones=Sum("cantidad_aplicaciones"),
        descuento=Sum("descuento"),
    )

    por_promocion = (
        registros
        .values(
            "promocion_id",
            "nombre",
            "tipo",
        )
        .annotate(
            tickets=Count("venta_id", distinct=True),
            aplicaciones=Sum("cantidad_aplicaciones"),
            descuento=Sum("descuento"),
        )
        .order_by("-aplicaciones")
    )

    por_sucursal = (
        registros
        .values(
            "venta__sucursal_id",
            "venta__sucursal__nombre",
        )
        .annotate(
            tickets=Count("venta_id", distinct=True),
            aplicaciones=Sum("cantidad_aplicaciones"),
            descuento=Sum("descuento"),
        )
        .order_by("-aplicaciones")
    )

    return {
        "resumen": resumen,
        "por_promocion": por_promocion,
        "por_sucursal": por_sucursal,
    }