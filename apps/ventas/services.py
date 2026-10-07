
from django.db.models import Sum, Count
from decimal import Decimal
from datetime import timedelta
from apps.ventas.models import VentaDiaria, ResumenSemanal, Venta, VentaDetalle
from apps.sucursales.models import Sucursal
from django.db.models.functions import Coalesce
from django.db import transaction
from django.utils import timezone





def construir_resumen_semanal(sucursal, fecha):

    inicio = fecha - timedelta(days=fecha.weekday())
    fin = inicio + timedelta(days=6)

    ventas = VentaDiaria.objects.filter(
        sucursal=sucursal,
        fecha__range=[inicio, fin]
    )

    totales = ventas.aggregate(
        efectivo=Sum("efectivo"),
        tarjeta=Sum("tarjeta"),
    )

    resumen, created = ResumenSemanal.objects.update_or_create(
        sucursal=sucursal,
        fecha_inicio=inicio,
        fecha_fin=fin,
        defaults={
            "efectivo": totales["efectivo"] or Decimal("0"),
            "tarjeta": totales["tarjeta"] or Decimal("0"),
        }
    )

    return resumen




def resumen_ventas_periodo(sucursal,fecha_inicio,fecha_fin,):
    """
    Devuelve el resumen financiero de ventas confirmadas
    de una sucursal dentro de un periodo.

    fecha_inicio y fecha_fin deben ser objetos date.
    """

    ventas = Venta.objects.filter(
        sucursal=sucursal,
        fecha_hora__date__range=(
            fecha_inicio,
            fecha_fin,
        ),
        estado=Venta.EstadoVenta.CONFIRMADA,
    )


    totales = ventas.aggregate(

        efectivo=Coalesce(
            Sum("efectivo"),
            Decimal("0.00")
        ),

        tarjeta=Coalesce(
            Sum("tarjeta"),
            Decimal("0.00")
        ),

        total=Coalesce(
            Sum("total"),
            Decimal("0.00")
        ),

        transacciones=Count("id"),
    )


    numero_transacciones = (
        totales["transacciones"]
    )


    if numero_transacciones:

        ticket_promedio = (
            totales["total"]
            / numero_transacciones
        )

    else:

        ticket_promedio = Decimal("0.00")


    return {

        "efectivo":
            totales["efectivo"],

        "tarjeta":
            totales["tarjeta"],

        "total":
            totales["total"],

        "transacciones":
            numero_transacciones,

        "ticket_promedio":
            ticket_promedio,
    }


def productos_vendidos_periodo(
    sucursal,
    fecha_inicio,
    fecha_fin,
):
    """
    Devuelve productos vendidos agrupados por producto
    y sus variantes.

    Ejemplo:

    [
        {
            "producto_id": 1,
            "nombre": "Cono",
            "cantidad": Decimal("20"),
            "variantes": [
                {
                    "variante_id": 1,
                    "nombre": "Vainilla",
                    "cantidad": Decimal("10"),
                },
                ...
            ]
        }
    ]
    """

    detalles = (
        VentaDetalle.objects
        .filter(
            venta__sucursal=sucursal,
            venta__fecha_hora__date__range=(
                fecha_inicio,
                fecha_fin,
            ),
            venta__estado=Venta.EstadoVenta.CONFIRMADA,
        )
        .values(
            "variante__producto_id",
            "producto_nombre",
            "variante_id",
            "variante_nombre",
        )
        .annotate(
            cantidad=Sum("cantidad")
        )
        .order_by(
            "producto_nombre",
            "variante_nombre",
        )
    )


    productos = {}


    for detalle in detalles:

        producto_id = detalle[
            "variante__producto_id"
        ]

        if producto_id not in productos:

            productos[producto_id] = {

                "producto_id":
                    producto_id,

                "nombre":
                    detalle["producto_nombre"],

                "cantidad":
                    Decimal("0"),

                "variantes":
                    [],
            }


        cantidad = (
            detalle["cantidad"]
            or Decimal("0")
        )


        productos[
            producto_id
        ]["cantidad"] += cantidad


        productos[
            producto_id
        ]["variantes"].append({

            "variante_id":
                detalle["variante_id"],

            "nombre":
                detalle["variante_nombre"],

            "cantidad":
                cantidad,
        })


    return list(
        productos.values()
    )



def reporte_ventas_periodo(
    sucursal,
    fecha_inicio,
    fecha_fin,
):

    resumen = resumen_ventas_periodo(
        sucursal,
        fecha_inicio,
        fecha_fin,
    )

    productos = productos_vendidos_periodo(
        sucursal,
        fecha_inicio,
        fecha_fin,
    )


    total_unidades = sum(
        (
            producto["cantidad"]
            for producto in productos
        ),
        Decimal("0")
    )


    return {
        **resumen,

        "total_unidades":
            total_unidades,

        "productos":
            productos,
    }






@transaction.atomic
def generar_venta_diaria(
    *,
    sucursal,
    usuario,
    fecha=None,
):

    if fecha is None:
        fecha = timezone.localdate()

    ventas = Venta.objects.filter(
        sucursal=sucursal,
        fecha_hora__date=fecha,
        estado=Venta.EstadoVenta.CONFIRMADA,
    )

    efectivo = (
        ventas
        .filter(
            metodo_pago=Venta.MetodoPago.EFECTIVO
        )
        .aggregate(total=Sum("total"))
        ["total"]
        or Decimal("0.00")
    )

    tarjeta = (
        ventas
        .filter(
            metodo_pago=Venta.MetodoPago.TARJETA
        )
        .aggregate(total=Sum("total"))
        ["total"]
        or Decimal("0.00")
    )

    venta_diaria, creada = (
        VentaDiaria.objects.update_or_create(
            sucursal=sucursal,
            fecha=fecha,
            defaults={
                "usuario": usuario,
                "efectivo": efectivo,
                "tarjeta": tarjeta,
            },
        )
    )

    return venta_diaria





def resumen_ventas_dia(
    *,
    sucursal,
    fecha,
):

    ventas = Venta.objects.filter(
        sucursal=sucursal,
        fecha_hora__date=fecha,
        estado=Venta.EstadoVenta.CONFIRMADA,
    )

    efectivo = (
        ventas
        .filter(
            metodo_pago=Venta.MetodoPago.EFECTIVO
        )
        .aggregate(total=Sum("total"))
        ["total"]
        or Decimal("0.00")
    )

    tarjeta = (
        ventas
        .filter(
            metodo_pago=Venta.MetodoPago.TARJETA
        )
        .aggregate(total=Sum("total"))
        ["total"]
        or Decimal("0.00")
    )

    otro = (
        ventas
        .filter(
            metodo_pago=Venta.MetodoPago.OTRO
        )
        .aggregate(total=Sum("total"))
        ["total"]
        or Decimal("0.00")
    )

    numero_ventas = ventas.count()

    total = (
        efectivo
        + tarjeta
        + otro
    )

    ticket_promedio = (
        total / numero_ventas
        if numero_ventas
        else Decimal("0.00")
    )

    return {
        "efectivo": efectivo,
        "tarjeta": tarjeta,
        "otro": otro,
        "total": total,
        "numero_ventas": numero_ventas,
        "ticket_promedio": ticket_promedio,
    }


@transaction.atomic
def generar_venta_diaria(
    *,
    sucursal,
    usuario,
    fecha,
):

    resumen = resumen_ventas_dia(
        sucursal=sucursal,
        fecha=fecha,
    )

    venta_diaria, creada = (
        VentaDiaria.objects.update_or_create(
            sucursal=sucursal,
            fecha=fecha,
            defaults={
                "usuario": usuario,
                "efectivo": resumen["efectivo"],
                "tarjeta": resumen["tarjeta"],
                "otro": resumen["otro"],
            },
        )
    )

    return venta_diaria, creada