from collections import defaultdict
from decimal import Decimal
from datetime import timedelta, datetime, time
from django.utils import timezone
from django.db import transaction
from apps.ventas.models import VentaDetalle, Venta
from apps.inventario.models import VarianteProducto, InventarioDiario, Receta, MovimientoInventario, InventarioInicialAutorizado
from  django.core.exceptions    import ValidationError
from apps.inventario.models import VarianteProducto, MovimientoInventario 




def consumo_teorico_periodo(
    sucursal,
    fecha_inicio,
    fecha_fin,
):
    """
    Calcula el consumo de insumos provocado directamente
    por las ventas.

    IMPORTANTE:
    Solo considera recetas cuyo momento de consumo sea
    'venta'.

    Los productos preparados previamente (Mordiscón,
    Copa Fiesta, etc.) se descontarán mediante movimientos
    de preparación y no aquí.
    """

    detalles_venta = (
        VentaDetalle.objects
        .filter(
            venta__sucursal=sucursal,
            venta__fecha_hora__date__range=(
                fecha_inicio,
                fecha_fin,
            ),
            venta__estado=Venta.EstadoVenta.CONFIRMADA,

  
        )
        .select_related(
            "venta",
            "variante",
            "variante__producto",
            "variante__receta",
        )
        .prefetch_related(
            "variante__receta__detalles",
            "variante__receta__detalles__insumo",
            "variante__receta__detalles__insumo__producto",
        )
    )

    consumos = defaultdict(
        lambda: {
            "variante": None,
            "cantidad": Decimal("0.0000"),
        }
    )

    for detalle_venta in detalles_venta:

        variante = detalle_venta.variante

        # Obtener receta si existe
        try:
            receta = variante.receta
        except Receta.DoesNotExist:
            receta = None

        # ==========================================
        # PRODUCTO CON RECETA ACTIVA
        # ==========================================

        if receta and receta.activa:

            if receta.momento_consumo == Receta.MomentoConsumo.VENTA:

                for receta_detalle in receta.detalles.all():

                    cantidad_consumida = (
                        detalle_venta.cantidad
                        * receta_detalle.cantidad
                    )

                    insumo = receta_detalle.insumo

                    consumos[insumo.id]["variante"] = insumo

                    consumos[insumo.id]["cantidad"] += cantidad_consumida

            elif receta.momento_consumo == Receta.MomentoConsumo.PREPARACION:

                consumos[variante.id]["variante"] = variante

                consumos[variante.id]["cantidad"] += detalle_venta.cantidad

        # ==========================================
        # PRODUCTO SIN RECETA
        # ==========================================

        elif receta is None and variante.producto.controlar_inventario:

            consumos[variante.id]["variante"] = variante

            consumos[variante.id]["cantidad"] += detalle_venta.cantidad

    resultado = list(
        consumos.values()
    )

    resultado.sort(
        key=lambda item: (
            item["variante"].producto.nombre,
            item["variante"].nombre,
        )
    )

    return resultado



def existencia_teorica_diaria(
    sucursal,
    fecha,
):

    resultado = []

    variantes = (
        VarianteProducto.objects
        .filter(
            activo=True,
            producto__activo=True,
            producto__controlar_inventario=True,
        )
        .select_related("producto")
        .order_by(
            "producto__nombre",
            "nombre",
        )
    )

    for variante in variantes:

        # ==========================================
        # ÚLTIMO CONTEO FÍSICO
        # ==========================================

        ultimo_inventario = (
            InventarioDiario.objects
            .filter(
                sucursal=sucursal,
                variante=variante,
                fecha__lt=fecha,
            )
            .order_by("-fecha")
            .first()
        )

        # ==========================================
        # NUNCA SE HA CONTADO
        # ==========================================

        if not ultimo_inventario:

            resultado.append({
                "variante": variante,
                "inventario_inicial": None,
                "fecha_ultimo_conteo": None,
                "consumo_teorico": Decimal("0.0000"),
                "movimientos_netos": Decimal("0.0000"),
                "cantidad_teorica": None,
                "sin_inventario_inicial": True,
            })

            continue

        # ==========================================
        # EXISTE CONTEO ANTERIOR
        # ==========================================

        inventario_inicial = ultimo_inventario.cantidad

        fecha_inicio = (
            ultimo_inventario.fecha
            + timedelta(days=1)
        )

        # ==========================================
        # CONSUMO POR VENTAS
        # ==========================================

        consumos = consumo_teorico_periodo(
            sucursal=sucursal,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha,
        )

        consumo_por_variante = {
            item["variante"].id: item["cantidad"]
            for item in consumos
        }

        consumo_ventas = (
            consumo_por_variante.get(
                variante.id,
                Decimal("0.0000"),
            )
        )

        # ==========================================
        # MOVIMIENTOS DE INVENTARIO
        # ==========================================

        movimientos = (
            MovimientoInventario.objects
            .filter(
                sucursal=sucursal,
                variante=variante,
                fecha_hora__date__range=(
                    fecha_inicio,
                    fecha,
                ),
            )
        )

        movimientos_netos = sum(
            (
                movimiento.cantidad_firmada
                for movimiento in movimientos
            ),
            Decimal("0.0000"),
        )

        # ==========================================
        # EXISTENCIA TEÓRICA
        # ==========================================

        cantidad_teorica = (
            inventario_inicial
            + movimientos_netos
            - consumo_ventas
        )

        resultado.append({
            "variante": variante,

            "inventario_inicial":
                inventario_inicial,

            "fecha_ultimo_conteo":
                ultimo_inventario.fecha,

            "consumo_teorico":
                consumo_ventas,

            "movimientos_netos":
                movimientos_netos,

            "cantidad_teorica":
                cantidad_teorica,

            "sin_inventario_inicial":
                False,
        })

    return resultado




@transaction.atomic
def registrar_preparacion(
    *,
    sucursal,
    variante,
    cantidad,
    usuario,
):
    cantidad = Decimal(str(cantidad))

    if cantidad <= 0:
        raise ValidationError(
            "La cantidad a preparar debe ser mayor que cero."
        )

    try:
        receta = (
            Receta.objects
            .select_related(
                "variante_vendida",
                "variante_vendida__producto",
            )
            .prefetch_related(
                "detalles",
                "detalles__insumo",
                "detalles__insumo__producto",
            )
            .get(
                variante_vendida=variante,
                activa=True,
                momento_consumo=(
                    Receta.MomentoConsumo.PREPARACION
                ),
            )
        )

    except Receta.DoesNotExist:
        raise ValidationError(
            "Este producto no tiene una receta "
            "activa de preparación."
        )

    ahora = timezone.now()
    movimientos = []

    # Consumir ingredientes
    for detalle in receta.detalles.all():

        cantidad_insumo = (
            cantidad * detalle.cantidad
        )

        movimiento = (
            MovimientoInventario.objects.create(
                sucursal=sucursal,
                variante=detalle.insumo,
                fecha_hora=ahora,
                tipo=(
                    MovimientoInventario
                    .TipoMovimiento
                    .PRODUCCION_SALIDA
                ),
                cantidad=cantidad_insumo,
                usuario=usuario,
                observaciones=(
                    f"Preparación de {cantidad} "
                    f"{variante}"
                ),
            )
        )

        movimientos.append(movimiento)

    # Generar producto preparado
    movimiento_producto = (
        MovimientoInventario.objects.create(
            sucursal=sucursal,
            variante=variante,
            fecha_hora=ahora,
            tipo=(
                MovimientoInventario
                .TipoMovimiento
                .PRODUCCION_ENTRADA
            ),
            cantidad=cantidad,
            usuario=usuario,
            observaciones=(
                f"Preparación de {cantidad} "
                f"{variante}"
            ),
        )
    )

    movimientos.append(
        movimiento_producto
    )

    return movimientos



@transaction.atomic
def registrar_entrada_inventario(
    *,
    sucursal,
    variante,
    cantidad,
    usuario,
    observaciones="",
):

    cantidad = Decimal(str(cantidad))

    if cantidad <= 0:
        raise ValidationError(
            "La cantidad recibida debe ser mayor que cero."
        )

    movimiento = MovimientoInventario.objects.create(
        sucursal=sucursal,
        variante=variante,
        fecha_hora=timezone.now(),
        tipo=MovimientoInventario.TipoMovimiento.COMPRA,
        cantidad=cantidad,
        usuario=usuario,
        observaciones=observaciones,
    )

    return movimiento



@transaction.atomic
def registrar_merma(
    *,
    sucursal,
    variante,
    cantidad,
    usuario,
    motivo,
    observaciones="",
):

    cantidad = Decimal(str(cantidad))

    if cantidad <= 0:
        raise ValidationError(
            "La cantidad de merma debe ser mayor que cero."
        )

    motivos_validos = {
        value
        for value, label
        in MovimientoInventario.MotivoMerma.choices
    }

    if motivo not in motivos_validos:
        raise ValidationError(
            "El motivo de merma no es válido."
        )

    return MovimientoInventario.objects.create(
        sucursal=sucursal,
        variante=variante,
        fecha_hora=timezone.now(),
        tipo=MovimientoInventario.TipoMovimiento.MERMA,
        cantidad=cantidad,
        motivo_merma=motivo,
        usuario=usuario,
        observaciones=observaciones,
    )



def consumo_teorico_desde_corte(
    sucursal,
    fecha_hora_inicio,
    fecha_hora_fin,
):
    """
    Calcula consumo por ventas desde un corte autorizado.

    Intervalo:
        fecha_hora_inicio < venta.fecha_hora < fecha_hora_fin

    La fecha_hora_fin representa el inicio del día
    siguiente al solicitado.

    No modifica inventarios ni crea movimientos.
    """

    detalles_venta = (
        VentaDetalle.objects
        .filter(
            venta__sucursal=sucursal,
            venta__fecha_hora__gt=fecha_hora_inicio,
            venta__fecha_hora__lt=fecha_hora_fin,
            venta__estado=Venta.EstadoVenta.CONFIRMADA,
        )
        .select_related(
            "venta",
            "variante",
            "variante__producto",
            "variante__receta",
        )
        .prefetch_related(
            "variante__receta__detalles",
            "variante__receta__detalles__insumo",
        )
    )

    consumos = defaultdict(
        lambda: Decimal("0.0000")
    )

    for detalle_venta in detalles_venta:

        variante = detalle_venta.variante

        try:
            receta = variante.receta
        except Receta.DoesNotExist:
            receta = None

        if receta and receta.activa:

            if (
                receta.momento_consumo
                == Receta.MomentoConsumo.VENTA
            ):

                for receta_detalle in receta.detalles.all():

                    cantidad = (
                        detalle_venta.cantidad
                        * receta_detalle.cantidad
                    )

                    consumos[
                        receta_detalle.insumo_id
                    ] += cantidad

            elif (
                receta.momento_consumo
                == Receta.MomentoConsumo.PREPARACION
            ):

                # Descontar producto terminado vendido.
                consumos[variante.id] += (
                    detalle_venta.cantidad
                )

        elif (
            receta is None
            and variante.producto.controlar_inventario
        ):

            consumos[variante.id] += (
                detalle_venta.cantidad
            )

    return dict(consumos)



def existencia_teorica_diaria(sucursal, fecha):

    resultado = []

    cero = Decimal("0.0000")

    # ==========================================
    # 1. INVENTARIO INICIAL AUTORIZADO
    # ==========================================

    inventario_inicial = (
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

    # ==========================================
    # 2. VARIANTES CONTROLADAS
    # ==========================================

    variantes = list(
        VarianteProducto.objects
        .filter(
            activo=True,
            producto__activo=True,
            producto__controlar_inventario=True,
        )
        .select_related("producto")
        .order_by(
            "producto__nombre",
            "nombre",
        )
    )

    # ==========================================
    # 3. SIN INVENTARIO INICIAL
    # ==========================================

    if not inventario_inicial:

        for variante in variantes:

            resultado.append({
                "variante": variante,
                "inventario_inicial": None,
                "fecha_ultimo_conteo": None,
                "consumo_teorico": cero,
                "movimientos_netos": cero,
                "cantidad_teorica": None,
                "sin_inventario_inicial": True,
            })

        return resultado

    fecha_corte = inventario_inicial.fecha_corte

    # ==========================================
    # 4. FIN DEL PERIODO SOLICITADO
    # ==========================================

    fecha_siguiente = fecha + timedelta(days=1)

    fecha_hora_fin = timezone.make_aware(
        datetime.combine(
            fecha_siguiente,
            time.min,
        ),
        timezone.get_current_timezone(),
    )

    # Evitar consultar fechas anteriores al corte.
    if fecha_hora_fin <= fecha_corte:

        for variante in variantes:
            resultado.append({
                "variante": variante,
                "inventario_inicial": None,
                "fecha_ultimo_conteo": None,
                "consumo_teorico": cero,
                "movimientos_netos": cero,
                "cantidad_teorica": None,
                "sin_inventario_inicial": True,
            })

        return resultado

    # ==========================================
    # 5. CANTIDADES INICIALES
    # ==========================================

    cantidades_iniciales = {
        detalle.variante_id: detalle.cantidad
        for detalle in inventario_inicial.detalles.all()
    }

    # ==========================================
    # 6. CONSUMOS POR VENTAS
    # ==========================================

    consumos = consumo_teorico_desde_corte(
        sucursal=sucursal,
        fecha_hora_inicio=fecha_corte,
        fecha_hora_fin=fecha_hora_fin,
    )

    # ==========================================
    # 7. MOVIMIENTOS POSTERIORES AL CORTE
    # ==========================================

    movimientos = (
        MovimientoInventario.objects
        .filter(
            sucursal=sucursal,
            fecha_hora__gt=fecha_corte,
            fecha_hora__lt=fecha_hora_fin,
        )
        .exclude(
            tipo__in=[
                MovimientoInventario.TipoMovimiento.VENTA,
                MovimientoInventario.TipoMovimiento.INVENTARIO_INICIAL,
            ]
        )
    )

    movimientos_por_variante = {}

    for movimiento in movimientos:

        variante_id = movimiento.variante_id

        movimientos_por_variante[variante_id] = (
            movimientos_por_variante.get(
                variante_id,
                cero,
            )
            + movimiento.cantidad_firmada
        )

    # ==========================================
    # 8. EXISTENCIA TEÓRICA
    # ==========================================

    for variante in variantes:

        if variante.id not in cantidades_iniciales:

            resultado.append({
                "variante": variante,
                "inventario_inicial": None,
                "fecha_ultimo_conteo": None,
                "consumo_teorico": cero,
                "movimientos_netos": cero,
                "cantidad_teorica": None,
                "sin_inventario_inicial": True,
            })

            continue

        cantidad_inicial = (
            cantidades_iniciales[variante.id]
        )

        consumo_ventas = consumos.get(
            variante.id,
            cero,
        )

        movimientos_netos = movimientos_por_variante.get(
            variante.id,
            cero,
        )

        cantidad_teorica = (
            cantidad_inicial
            + movimientos_netos
            - consumo_ventas
        )

        resultado.append({
            "variante": variante,
            "inventario_inicial": cantidad_inicial,
            "fecha_ultimo_conteo": (
                timezone.localtime(fecha_corte).date()
            ),
            "consumo_teorico": consumo_ventas,
            "movimientos_netos": movimientos_netos,
            "cantidad_teorica": cantidad_teorica,
            "sin_inventario_inicial": False,
        })

    return resultado