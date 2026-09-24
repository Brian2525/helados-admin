# apps/reportes/services/permisos.py

from dataclasses import dataclass

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q, QuerySet

from apps.sucursales.models import Sucursal


@dataclass(frozen=True)
class AlcanceReporteMensual:
    propietario: User
    sucursal: Sucursal | None
    consolidado: bool
    sucursales_qs: QuerySet
    sucursales_ids: list[int]


def get_sucursales_usuario(usuario) -> QuerySet:
    if usuario.is_superuser:
        return Sucursal.objects.all()

    return (
        Sucursal.objects.filter(
            Q(propietario=usuario) |
            Q(usuarios=usuario)
        )
        .distinct()
    )


def usuario_tiene_acceso_a_sucursal(usuario, sucursal: Sucursal) -> bool:
    if usuario.is_superuser:
        return True

    if sucursal.propietario_id == usuario.id:
        return True

    return sucursal.usuarios.filter(id=usuario.id).exists()


def resolver_alcance_reporte(
    *,
    usuario,
    sucursal_id: int | None = None,
    propietario_id: int | None = None,
) -> AlcanceReporteMensual:
    """
    Reglas:
    - Si se solicita sucursal específica:
        * superuser, propietario de la sucursal o usuario asignado pueden generar.
        * el propietario del reporte se toma desde sucursal.propietario.
    - Si se solicita consolidado:
        * superuser puede generar para cualquier propietario (requiere propietario_id).
        * usuario normal solo puede generar su propio consolidado si es propietario.
        * usuarios asignados a sucursales NO pueden generar consolidado.
    """
    if sucursal_id:
        try:
            sucursal = Sucursal.objects.select_related("propietario").get(pk=sucursal_id)
        except Sucursal.DoesNotExist:
            raise ValidationError({"sucursal": "La sucursal seleccionada no existe."})

        if not usuario_tiene_acceso_a_sucursal(usuario, sucursal):
            raise PermissionDenied("No tienes acceso a esa sucursal.")

        if sucursal.propietario_id is None:
            raise ValidationError(
                {"sucursal": "La sucursal seleccionada no tiene propietario asignado."}
            )

        sucursales_qs = Sucursal.objects.filter(pk=sucursal.pk)

        return AlcanceReporteMensual(
            propietario=sucursal.propietario,
            sucursal=sucursal,
            consolidado=False,
            sucursales_qs=sucursales_qs,
            sucursales_ids=[sucursal.id],
        )

    # Consolidado
    if usuario.is_superuser:
        if not propietario_id:
            raise ValidationError(
                {"propietario": "Para un consolidado como superusuario debes indicar propietario_id."}
            )

        try:
            propietario = User.objects.get(pk=propietario_id)
        except User.DoesNotExist:
            raise ValidationError({"propietario": "El propietario indicado no existe."})

        sucursales_qs = Sucursal.objects.filter(propietario=propietario)

        if not sucursales_qs.exists():
            raise ValidationError(
                {"propietario": "El propietario no tiene sucursales para consolidar."}
            )

        return AlcanceReporteMensual(
            propietario=propietario,
            sucursal=None,
            consolidado=True,
            sucursales_qs=sucursales_qs,
            sucursales_ids=list(sucursales_qs.values_list("id", flat=True)),
        )

    # Usuario normal: consolidado solo si es propietario
    sucursales_propias = Sucursal.objects.filter(propietario=usuario)

    if not sucursales_propias.exists():
        raise PermissionDenied(
            "No puedes generar un consolidado porque no eres propietario de sucursales."
        )

    return AlcanceReporteMensual(
        propietario=usuario,
        sucursal=None,
        consolidado=True,
        sucursales_qs=sucursales_propias,
        sucursales_ids=list(sucursales_propias.values_list("id", flat=True)),
    )