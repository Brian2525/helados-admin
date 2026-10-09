


from decimal import Decimal
from .models import Promocion   
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date





DIAS_SEMANA = {
    0: "lunes",
    1: "martes",
    2: "miercoles",
    3: "jueves",
    4: "viernes",
    5: "sabado",
    6: "domingo",
}


def promocion_vigente(promocion, fecha=None):

    if fecha is None:
        fecha = timezone.localdate()

    if not promocion.activa:
        return False

    if (
        promocion.fecha_inicio
        and fecha < promocion.fecha_inicio
    ):
        return False

    if (
        promocion.fecha_fin
        and fecha > promocion.fecha_fin
    ):
        return False

    campo_dia = DIAS_SEMANA[fecha.weekday()]

    if not getattr(promocion, campo_dia):
        return False

    return True


def calcular_grupos_promocion(
    promocion,
    cantidades_carrito
):

    grupos_posibles = []

    for detalle in promocion.detalles.all():

        cantidad_elegible = (
            cantidad_elegible_detalle(
                detalle,
                cantidades_carrito
            )
        )

        if detalle.cantidad <= 0:
            continue

        grupos = (
            cantidad_elegible
            // detalle.cantidad
        )

        grupos_posibles.append(
            int(grupos)
        )

    if not grupos_posibles:
        return 0

    return min(grupos_posibles)



def calcular_descuento_promocion(
    promocion,
    cantidades_carrito
):

    if not promocion_vigente(promocion):
        return Decimal("0.00")

    grupos = calcular_grupos_promocion(
        promocion,
        cantidades_carrito
    )

    if grupos <= 0:
        return Decimal("0.00")

    # ==========================
    # PRECIO POR GRUPO
    # Ej. 2 helados por $30
    # ==========================

    if promocion.tipo == Promocion.Tipo.PRECIO_GRUPO:

        precio_normal_grupo = Decimal("0.00")

        for detalle in promocion.detalles.select_related(
            "variante"
        ):

            precio_normal_grupo += (
                detalle.variante.precio_venta
                * detalle.cantidad
            )

        descuento_grupo = (
            precio_normal_grupo
            - promocion.precio_grupo
        )

        if descuento_grupo <= Decimal("0.00"):
            return Decimal("0.00")

        return descuento_grupo * grupos

    # ==========================
    # DESCUENTO TOTAL DEL GRUPO
    # Ej. 2 Sundaes + 2 toppings
    # descuento total $8
    # ==========================

    if promocion.tipo == Promocion.Tipo.DESCUENTO_GRUPO:

        return (
            promocion.descuento_total
            * grupos
        )

    # ==========================
    # DESCUENTO POR UNIDAD
    # Ej. Domingo -$21
    # ==========================

    if promocion.tipo == Promocion.Tipo.DESCUENTO_UNIDAD:

        unidades_por_grupo = sum(
            detalle.cantidad
            for detalle in promocion.detalles.all()
        )

        return (
            promocion.descuento_por_unidad
            * unidades_por_grupo
            * grupos
        )

    return Decimal("0.00")





def promociones_comparten_dia(promocion_a, promocion_b):

    dias = [
        "lunes",
        "martes",
        "miercoles",
        "jueves",
        "viernes",
        "sabado",
        "domingo",
    ]

    return any(
        getattr(promocion_a, dia)
        and getattr(promocion_b, dia)
        for dia in dias
    )

def periodos_se_superponen(promo_a, promo_b):

    inicio_a = promo_a.fecha_inicio or date.min
    fin_a = promo_a.fecha_fin or date.max

    inicio_b = promo_b.fecha_inicio or date.min
    fin_b = promo_b.fecha_fin or date.max

    return (
        inicio_a <= fin_b
        and inicio_b <= fin_a
    )




def validar_conflictos_promocion(
    promocion,
    variantes
):

    promociones = (
        Promocion.objects
        .filter(
            activa=True,
            detalles__producto__in=variantes,
            detalles__variantes_elegibles__in=variantes,
        )
        .exclude(pk=promocion.pk)
        .distinct()
    )

    conflictos = []

    for otra in promociones:

        if not periodos_se_superponen(
            promocion,
            otra
        ):
            continue

        if not promociones_comparten_dia(
            promocion,
            otra
        ):
            continue

        conflictos.append(otra)

    if conflictos:
        nombres = ", ".join(
            promo.nombre
            for promo in conflictos
        )

        raise ValidationError(
            "Los productos seleccionados ya tienen "
            f"una promoción coincidente: {nombres}."
        )


from decimal import Decimal
from django.utils import timezone

from .models import Promocion


DIAS_SEMANA = {
    0: "lunes",
    1: "martes",
    2: "miercoles",
    3: "jueves",
    4: "viernes",
    5: "sabado",
    6: "domingo",
}


def promocion_vigente(promocion, fecha=None):

    if fecha is None:
        fecha = timezone.localdate()

    if not promocion.activa:
        return False

    if (
        promocion.fecha_inicio
        and fecha < promocion.fecha_inicio
    ):
        return False

    if (
        promocion.fecha_fin
        and fecha > promocion.fecha_fin
    ):
        return False

    campo_dia = DIAS_SEMANA[fecha.weekday()]

    return getattr(promocion, campo_dia, False)







def calcular_grupos_promocion(
    promocion,
    cantidades_carrito
):

    grupos_posibles = []

    for detalle in promocion.detalles.all():

        cantidad_elegible = (
            cantidad_elegible_detalle(
                detalle,
                cantidades_carrito
            )
        )

        if detalle.cantidad <= 0:
            continue

        grupos = (
            cantidad_elegible
            // detalle.cantidad
        )

        grupos_posibles.append(
            int(grupos)
        )

    if not grupos_posibles:
        return 0

    return min(grupos_posibles)










def calcular_descuento_promocion(
    promocion,
    cantidades_carrito
):

    # ==========================================
    # DESCUENTO POR UNIDAD
    # ==========================================
    #
    # Ejemplo:
    # Litros elegibles -> -$21 por unidad
    #
    # No es necesario comprar todas las
    # variantes configuradas.
    # ==========================================

    if (
        promocion.tipo
        == Promocion.Tipo.DESCUENTO_UNIDAD
    ):

        unidades_elegibles = Decimal("0.00")

        for detalle in promocion.detalles.all():

            unidades_elegibles += (
                cantidad_elegible_detalle(
                    detalle,
                    cantidades_carrito
                )
            )

        if unidades_elegibles <= 0:
            return Decimal("0.00")

        return (
            promocion.descuento_por_unidad
            * unidades_elegibles
        )


    # ==========================================
    # PROMOCIONES POR GRUPO
    # ==========================================

    grupos = calcular_grupos_promocion(
        promocion,
        cantidades_carrito
    )

    if grupos <= 0:
        return Decimal("0.00")


    # ==========================================
    # PRECIO POR GRUPO
    # ==========================================
    #
    # Ejemplo:
    # 2 helados por $30
    # ==========================================

    if (
        promocion.tipo
        == Promocion.Tipo.PRECIO_GRUPO
    ):

        precio_normal_total = Decimal("0.00")

        for detalle in promocion.detalles.all():

            cantidad_necesaria = (
                detalle.cantidad
                * grupos
            )

            cantidad_restante = (
                Decimal(
                    str(cantidad_necesaria)
                )
            )

            # ==================================
            # VARIANTES ELEGIBLES QUE SÍ ESTÁN
            # EN EL CARRITO
            # ==================================

            variantes = (
                get_variantes_elegibles(
                    detalle
                )
            )

            for variante in variantes:

                if cantidad_restante <= 0:
                    break

                cantidad_carrito = (
                    cantidades_carrito.get(
                        variante.id,
                        Decimal("0.00")
                    )
                )

                if cantidad_carrito <= 0:
                    continue

                cantidad_usada = min(
                    cantidad_carrito,
                    cantidad_restante
                )

                precio_normal_total += (
                    variante.precio_venta
                    * cantidad_usada
                )

                cantidad_restante -= (
                    cantidad_usada
                )

        precio_promocional_total = (
            promocion.precio_grupo
            * grupos
        )

        descuento = (
            precio_normal_total
            - precio_promocional_total
        )

        if descuento <= Decimal("0.00"):
            return Decimal("0.00")

        return descuento


    # ==========================================
    # DESCUENTO POR GRUPO
    # ==========================================
    #
    # Ejemplo:
    # 2 Sundaes + 2 toppings
    # descuento total $8
    # ==========================================

    if (
        promocion.tipo
        == Promocion.Tipo.DESCUENTO_GRUPO
    ):

        return (
            promocion.descuento_total
            * grupos
        )


    return Decimal("0.00")



def get_variantes_elegibles(detalle):

    if not detalle.producto:
        return []

    if detalle.cualquier_variante:

        return (
            detalle.producto
            .variantes_producto
            .filter(activo=True)
        )

    return (
        detalle.variantes_elegibles
        .filter(activo=True)
    )









def cantidad_elegible_detalle(
    detalle,
    cantidades_carrito
):

    total = Decimal("0.00")

    for variante in get_variantes_elegibles(detalle):

        total += cantidades_carrito.get(
            variante.id,
            Decimal("0.00")
        )

    return total




def calcular_promociones_carrito(
    cantidades_carrito,
    fecha=None,
):

    fecha = fecha or timezone.localdate()

    promociones = (
        Promocion.objects
        .filter(activa=True)
        .prefetch_related(
            "detalles",
            "detalles__producto",
            "detalles__variantes_elegibles",
        )
    )

    promociones_aplicadas = []

    descuento_total = Decimal("0.00")


 
    # ==========================================
    # CALCULAR PROMOCIONES
    # ==========================================

    for promocion in promociones:

        if not promocion_vigente(
            promocion,
            fecha
        ):
            continue


        # ======================================
        # DESCUENTO POR UNIDAD
        # ======================================

        if (
            promocion.tipo
            == Promocion.Tipo.DESCUENTO_UNIDAD
        ):

            descuento = (
                calcular_descuento_promocion(
                    promocion,
                    cantidades_carrito
                )
            )

            if descuento <= Decimal("0.00"):
                continue


            unidades_aplicadas = Decimal("0.00")


            for detalle in promocion.detalles.all():

                unidades_aplicadas += (
                    cantidad_elegible_detalle(
                        detalle,
                        cantidades_carrito
                    )
                )


            if unidades_aplicadas <= 0:
                continue


            promociones_aplicadas.append({

                "promocion":
                    promocion,

                "nombre":
                    promocion.nombre,

                "tipo":
                    promocion.tipo,

                "cantidad_aplicaciones":
                    int(unidades_aplicadas),

                "descuento_por_aplicacion":
                    promocion.descuento_por_unidad,

                "descuento":
                    descuento,
            })


            descuento_total += (
                descuento
            )

            continue


        # ======================================
        # PROMOCIONES POR GRUPO
        # ======================================

        grupos = calcular_grupos_promocion(
            promocion,
            cantidades_carrito
        )

        if grupos <= 0:
            continue


        descuento = (
            calcular_descuento_promocion(
                promocion,
                cantidades_carrito
            )
        )

        if descuento <= Decimal("0.00"):
            continue


        descuento_por_aplicacion = (
            descuento / grupos
        )


        promociones_aplicadas.append({

            "promocion":
                promocion,

            "nombre":
                promocion.nombre,

            "tipo":
                promocion.tipo,

            "cantidad_aplicaciones":
                grupos,

            "descuento_por_aplicacion":
                descuento_por_aplicacion,

            "descuento":
                descuento,
        })


        descuento_total += (
            descuento
        )


    return {
        "descuento_total":
            descuento_total,

        "promociones":
            promociones_aplicadas,
    }



def cantidad_elegible_detalle(
    detalle,
    cantidades_carrito
):

    total = Decimal("0.00")

    if not detalle.producto:
        return total

    if detalle.cualquier_variante:

        variantes = (
            detalle.producto
            .variantes_producto
            .filter(activo=True)
        )

    else:

        variantes = (
            detalle.variantes_elegibles
            .filter(activo=True)
        )

    for variante in variantes:

        total += cantidades_carrito.get(
            variante.id,
            Decimal("0.00")
        )

    return total