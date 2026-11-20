
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.db import transaction
from apps.gastos.models import Gasto, CajaChica, MovimientoCajaChica

@transaction.atomic
def registrar_gasto_caja_chica(
    *,
    sucursal,
    categoria,
    monto,
    descripcion,
    usuario
):
    monto = Decimal(str(monto))

    if monto <= 0 or monto != monto.quantize(Decimal("0.01")):
        raise ValidationError("Importe inválido.")

    caja = CajaChica.objects.select_for_update().get(
        sucursal=sucursal,
        activa=True
    )

    if caja.saldo_actual < monto:
        raise ValidationError(
            "Saldo insuficiente en caja chica."
        )

    saldo_anterior = caja.saldo_actual
    saldo_nuevo = saldo_anterior - monto

    gasto = Gasto.objects.create(
        sucursal=sucursal,
        categoria=categoria,
        monto=monto,
        descripcion=descripcion,
        origen_fondos=Gasto.OrigenFondos.CAJA_CHICA,
        usuario=usuario
    )

    MovimientoCajaChica.objects.create(
        caja_chica=caja,
        tipo=MovimientoCajaChica.TipoMovimiento.GASTO,
        monto=-monto,
        saldo_anterior=saldo_anterior,
        saldo_nuevo=saldo_nuevo,
        gasto=gasto,
        usuario=usuario
    )

    caja.saldo_actual = saldo_nuevo
    caja.save(update_fields=["saldo_actual", "updated_at"])

    return gasto




@transaction.atomic
def ingresar_dinero_caja_chica(
    *,
    sucursal,
    monto,
    usuario,
    observaciones="",
):
    """
    Registra la apertura o reposición de caja chica.

    Esta función debe ser utilizada solamente
    desde una vista autorizada para administradores.
    """

    try:
        monto = Decimal(str(monto))
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError("Importe inválido.")

    if (
        not monto.is_finite()
        or monto <= 0
        or monto.as_tuple().exponent < -2
    ):
        raise ValidationError(
            "El importe debe ser positivo y tener "
            "máximo dos decimales."
        )

    caja, _ = CajaChica.objects.get_or_create(
        sucursal=sucursal,
        defaults={
            "fondo_objetivo": Decimal("200.00"),
            "saldo_actual": Decimal("0.00"),
        },
    )

    # Se bloquea el registro antes de modificar el saldo.
    caja = CajaChica.objects.select_for_update().get(
        pk=caja.pk
    )

    if not caja.activa:
        raise ValidationError(
            "La caja chica está desactivada."
        )

    tiene_movimientos = (
        MovimientoCajaChica.objects.filter(
            caja_chica=caja
        ).exists()
    )

    tipo = (
        MovimientoCajaChica.TipoMovimiento.REPOSICION
        if tiene_movimientos
        else MovimientoCajaChica.TipoMovimiento.APERTURA
    )

    saldo_anterior = caja.saldo_actual
    saldo_nuevo = saldo_anterior + monto

    movimiento = MovimientoCajaChica.objects.create(
        caja_chica=caja,
        tipo=tipo,
        monto=monto,
        saldo_anterior=saldo_anterior,
        saldo_nuevo=saldo_nuevo,
        usuario=usuario,
        observaciones=observaciones,
    )

    caja.saldo_actual = saldo_nuevo
    caja.save(
        update_fields=["saldo_actual", "updated_at"]
    )

    return movimiento