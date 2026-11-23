

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.ventas.models import Venta


def usuario_puede_anular(usuario):
    if not usuario.is_authenticated or not usuario.is_active:
        return False

    if usuario.is_superuser:
        return True

    return (
        usuario.groups.filter(name="Supervisor").exists()
        and usuario.has_perm("ventas.change_venta")
    )


@transaction.atomic
def anular_venta(
    *,
    venta_id,
    usuario,
    motivo,
    sucursales_autorizadas,
):
    if not usuario_puede_anular(usuario):
        raise PermissionDenied(
            "No tienes permiso para anular ventas."
        )

    venta = get_object_or_404(
        Venta.objects.select_for_update().filter(
            sucursal__in=sucursales_autorizadas
        ),
        pk=venta_id,
    )

    if venta.estado == Venta.EstadoVenta.ANULADA:
        raise ValidationError(
            "La venta ya se encuentra anulada."
        )

    if venta.estado != Venta.EstadoVenta.CONFIRMADA:
        raise ValidationError(
            "La venta no está confirmada."
        )

    motivo = (motivo or "").strip()

    if not motivo:
        raise ValidationError(
            "Es obligatorio indicar el motivo."
        )

    if len(motivo) > 1000:
        raise ValidationError(
            "El motivo no puede superar 1000 caracteres."
        )

    venta.estado = Venta.EstadoVenta.ANULADA
    venta.anulada_por = usuario
    venta.anulada_at = timezone.now()
    venta.motivo_anulacion = motivo

    venta.save(update_fields=[
        "estado",
        "anulada_por",
        "anulada_at",
        "motivo_anulacion",
        "updated_at",
    ])

    return venta
