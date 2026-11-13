


from decimal import Decimal
from .models import Promocion   
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date
from collections import defaultdict
from apps.inventario.models import VarianteProducto





DIAS_SEMANA = {
    0: "lunes",
    1: "martes",
    2: "miercoles",
    3: "jueves",
    4: "viernes",
    5: "sabado",
    6: "domingo",
}


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
    variantes,
):
    """
    Valida que las variantes seleccionadas
    no participen en otra promoción activa
    durante fechas y días coincidentes.

    variantes:
        QuerySet o lista de objetos VarianteProducto.
    """

    # ==========================================
    # 1. IDS DE VARIANTES SELECCIONADAS
    # ==========================================

    variantes_ids = {
        variante.pk
        for variante in variantes
    }

    if not variantes_ids:
        return

    # ==========================================
    # 2. OTRAS PROMOCIONES ACTIVAS
    # ==========================================

    promociones = (
        Promocion.objects
        .filter(activa=True)
        .exclude(pk=promocion.pk)
        .prefetch_related(
            "detalles",
            "detalles__producto",
            "detalles__variantes_elegibles",
        )
    )

    conflictos = []

    for otra in promociones:

        # ======================================
        # VALIDAR PERIODO
        # ======================================

        if not periodos_se_superponen(
            promocion,
            otra,
        ):
            continue

        # ======================================
        # VALIDAR DÍAS
        # ======================================

        if not promociones_comparten_dia(
            promocion,
            otra,
        ):
            continue

        # ======================================
        # VARIANTES DE LA OTRA PROMOCIÓN
        # ======================================

        otras_variantes_ids = set()

        for detalle in otra.detalles.all():

            for variante in get_variantes_elegibles(
                detalle
            ):
                otras_variantes_ids.add(variante.pk)

        # ======================================
        # DETECTAR COINCIDENCIAS
        # ======================================

        variantes_repetidas = (
            variantes_ids & otras_variantes_ids
        )

        if variantes_repetidas:
            conflictos.append(otra.nombre)

    # ==========================================
    # 3. MOSTRAR ERROR
    # ==========================================

    if conflictos:

        nombres = ", ".join(
            sorted(set(conflictos))
        )

        raise ValidationError(
            "Las variantes seleccionadas ya "
            "participan en otra promoción activa "
            "durante el mismo periodo y días: "
            f"{nombres}."
        )





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

def get_variantes_elegibles(
    detalle,
    sucursal=None,
):

    if not detalle.producto:
        return []

    # ==========================================
    # VALIDAR SUCURSAL
    # ==========================================

    if sucursal is not None:

        sucursal_id = (
            sucursal.pk
            if hasattr(sucursal, "pk")
            else sucursal
        )

        sucursales_ids = {
            s.pk
            for s in detalle.sucursales.all()
        }

        # Si hay sucursales configuradas,
        # la actual debe estar incluida.
        if (
            sucursales_ids
            and sucursal_id not in sucursales_ids
        ):
            return []

    # ==========================================
    # OBTENER VARIANTES ELEGIBLES
    # ==========================================

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



def calcular_promociones_carrito(
    cantidades_carrito,
    fecha=None,
    sucursal=None,
):

    fecha = fecha or timezone.localdate()

    promociones = list(
        Promocion.objects
        .filter(activa=True)
        .prefetch_related(
            "detalles",
            "detalles__producto",
            "detalles__variantes_elegibles",
        )
        .order_by("id")
    )

    promociones_aplicadas = []
    descuento_total = Decimal("0.00")

    # Copiamos las cantidades originales.
    cantidades_disponibles = {
        variante_id: Decimal(str(cantidad))
        for variante_id, cantidad in cantidades_carrito.items()
    }

    # ==========================================
    # PROMOCIONES VIGENTES
    # ==========================================

    promociones_vigentes = [
        promocion
        for promocion in promociones
        if promocion_vigente(promocion, fecha)
    ]

    # ==========================================
    # 1. COMPRA X LLEVA Y
    # ==========================================

    for promocion in promociones_vigentes:

        if (
            promocion.tipo
            != Promocion.Tipo.COMPRA_LLEVA
        ):
            continue

        resultado = calcular_promocion_compra_lleva(
            promocion=promocion,
            cantidades_carrito=cantidades_disponibles,
            sucursal=sucursal,
        )

        descuento = resultado["descuento_total"]

        if descuento <= Decimal("0.00"):
            continue

        # Reservar las unidades utilizadas.
        for variante_id, cantidad in (
            resultado["cantidades_consumidas"].items()
        ):

            if cantidades_disponibles[variante_id] < cantidad:
                raise ValueError(
                    "Cantidad insuficiente para aplicar "
                    "la promoción."
                )

        for variante_id, cantidad in (
            resultado["cantidades_consumidas"].items()
        ):

            cantidades_disponibles[variante_id] -= cantidad

        promociones_aplicadas.extend(
            resultado["promociones"]
        )

        descuento_total += descuento

    # ==========================================
    # 2. PROMOCIONES EXISTENTES
    # ==========================================

    for promocion in promociones_vigentes:

        if (
            promocion.tipo
            == Promocion.Tipo.COMPRA_LLEVA
        ):
            continue

        # ======================================
        # DESCUENTO POR UNIDAD
        # ======================================

        if (
            promocion.tipo
            == Promocion.Tipo.DESCUENTO_UNIDAD
        ):

            descuento = calcular_descuento_promocion(
                promocion,
                cantidades_disponibles,
            )

            if descuento <= Decimal("0.00"):
                continue

            unidades_aplicadas = Decimal("0.00")

            for detalle in promocion.detalles.all():

                unidades_aplicadas += (
                    cantidad_elegible_detalle(
                        detalle,
                        cantidades_disponibles,
                    )
                )

            if unidades_aplicadas <= 0:
                continue

            promociones_aplicadas.append({
                "promocion": promocion,
                "nombre": promocion.nombre,
                "tipo": promocion.tipo,
                "cantidad_aplicaciones": int(
                    unidades_aplicadas
                ),
                "descuento_por_aplicacion": (
                    promocion.descuento_por_unidad
                ),
                "descuento": descuento,
            })

            descuento_total += descuento

            continue

        # ======================================
        # PROMOCIONES POR GRUPO
        # ======================================

        grupos = calcular_grupos_promocion(
            promocion,
            cantidades_disponibles,
        )

        if grupos <= 0:
            continue

        descuento = calcular_descuento_promocion(
            promocion,
            cantidades_disponibles,
        )

        if descuento <= Decimal("0.00"):
            continue

        descuento_por_aplicacion = (
            descuento / grupos
        )

        promociones_aplicadas.append({
            "promocion": promocion,
            "nombre": promocion.nombre,
            "tipo": promocion.tipo,
            "cantidad_aplicaciones": grupos,
            "descuento_por_aplicacion": (
                descuento_por_aplicacion
            ),
            "descuento": descuento,
        })

        descuento_total += descuento

    return {
        "descuento_total": descuento_total,
        "promociones": promociones_aplicadas,
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




def calcular_promocion_compra_lleva(
    promocion,
    items,
    sucursal=None,
):
    """
    Calcula promociones Compra X Lleva Y.

    Reglas:
    - Solo agrupa unidades de la misma variante.
    - Solo agrupa unidades con el mismo precio.
    - Se aplica una vez por cada grupo completo.
    - No modifica los precios ni el carrito.

    items = [
        {
            "variante_id": 1,
            "cantidad": 3,
            "precio": Decimal("25.00"),
        }
    ]

    IMPORTANTE:
    Los items ya deben contener únicamente
    variantes elegibles para esta promoción.
    """

    if (
        not promocion.cantidad_compra
        or not promocion.cantidad_lleva
        or promocion.cantidad_lleva <= promocion.cantidad_compra
    ):
        return {
            "descuento": Decimal("0.00"),
            "aplicaciones": [],
        }

    grupos_items = defaultdict(int)

    for item in items:
        variante_id = int(item["variante_id"])
        cantidad = int(item["cantidad"])
        precio = Decimal(str(item["precio"]))

        if cantidad <= 0 or precio < 0:
            raise ValueError(
                "Cantidad o precio inválido."
            )

        clave = (variante_id, precio)

        grupos_items[clave] += cantidad

    descuento_total = Decimal("0.00")
    aplicaciones = []

    for (variante_id, precio), cantidad in grupos_items.items():

        grupos_completos = (
            cantidad // promocion.cantidad_lleva
        )

        if grupos_completos == 0:
            continue

        unidades_gratis_por_grupo = (
            promocion.cantidad_lleva
            - promocion.cantidad_compra
        )

        unidades_gratis = (
            grupos_completos
            * unidades_gratis_por_grupo
        )

        descuento = (
            precio * unidades_gratis
        )

        descuento_total += descuento

        aplicaciones.append({
            "variante_id": variante_id,
            "precio": precio,
            "grupos": grupos_completos,
            "unidades_gratis": unidades_gratis,
            "unidades_utilizadas": (
                grupos_completos
                * promocion.cantidad_lleva
            ),
            "descuento": descuento,
        })

    return {
        "descuento": descuento_total,
        "aplicaciones": aplicaciones,
    }






def calcular_promocion_compra_lleva(
    promocion,
    cantidades_carrito,
    sucursal=None,
):
    """
    Calcula promociones Compra X Lleva Y.

    Ejemplos:
        Compra 2, lleva 3 -> 3x2
        Compra 1, lleva 2 -> 2x1

    Reglas:
    - Solo combina unidades de la misma variante.
    - Cada variante usa su precio de BD.
    - No aplica a cantidades fraccionarias.
    - No modifica el carrito original.
    """

    resultado = {
        "descuento_total": Decimal("0.00"),
        "promociones": [],
        "cantidades_consumidas": {},
    }

    compra = promocion.cantidad_compra
    lleva = promocion.cantidad_lleva

    if (
        compra is None
        or lleva is None
        or compra < 1
        or lleva <= compra
    ):
        return resultado

    # ==========================================
    # 1. VARIANTES ELEGIBLES
    # ==========================================

    variantes_ids = set()

    for detalle in promocion.detalles.all():

        for variante in get_variantes_elegibles(detalle, sucursal=sucursal,):
            variantes_ids.add(variante.id)

    if not variantes_ids:
        return resultado

    # Consultar los precios reales.
    variantes = VarianteProducto.objects.filter(
        id__in=variantes_ids,
        activo=True,
        producto__activo=True,
    )

    # ==========================================
    # 2. CALCULAR POR CADA VARIANTE
    # ==========================================

    unidades_gratis_por_grupo = lleva - compra

    for variante in variantes.order_by("id"):

        cantidad = Decimal(
            str(cantidades_carrito.get(
                variante.id,
                Decimal("0.00"),
            ))
        )

        if cantidad <= 0:
            continue

        # El 3x2 solo aplica a unidades enteras.
        if cantidad != cantidad.to_integral_value():
            continue

        grupos = int(cantidad) // lleva

        if grupos <= 0:
            continue

        precio = variante.precio_venta

        if precio is None or precio <= 0:
            continue

        unidades_gratis = (
            grupos * unidades_gratis_por_grupo
        )

        descuento_por_aplicacion = (
            precio * unidades_gratis_por_grupo
        )

        descuento = (
            descuento_por_aplicacion * grupos
        )

        unidades_consumidas = grupos * lleva

        resultado["descuento_total"] += descuento

        resultado["cantidades_consumidas"][
            variante.id
        ] = Decimal(unidades_consumidas)

        resultado["promociones"].append({
            "promocion": promocion,
            "nombre": promocion.nombre,
            "tipo": promocion.tipo,
            "variante_id": variante.id,
            "cantidad_aplicaciones": grupos,
            "descuento_por_aplicacion": (
                descuento_por_aplicacion
            ),
            "descuento": descuento,
            "unidades_gratis": unidades_gratis,
        })

    return resultado