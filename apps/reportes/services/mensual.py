from django.db import transaction
from django.utils import timezone

from apps.reportes.models import ReporteMensual
from apps.reportes.services.builders import construir_snapshot_reporte_mensual
from apps.reportes.services.collectors.gastos import obtener_metricas_gastos
from apps.reportes.services.collectors.nomina import obtener_metricas_nomina
from apps.reportes.services.collectors.sucursales import obtener_resumen_sucursales
from apps.reportes.services.collectors.ventas import obtener_metricas_ventas
from apps.reportes.services.collectors.cuentas_por_pagar import (
    obtener_metricas_cuentas_por_pagar)
from apps.reportes.services.periodos import (
    obtener_periodo_anterior,
    obtener_rango_mensual,
)
from apps.reportes.services.permisos import resolver_alcance_reporte


DEFAULT_SCHEMA_VERSION = 3


def obtener_datos_reporte_mensual(
    *,
    usuario,
    anio: int,
    mes: int,
    sucursal_id: int | None = None,
    propietario_id: int | None = None,
    schema_version: int = DEFAULT_SCHEMA_VERSION,
) -> dict:
    """
    Calcula y construye el snapshot del reporte mensual,
    pero no lo guarda en la base de datos.
    """
    rango_actual = obtener_rango_mensual(anio, mes)
    rango_anterior = obtener_periodo_anterior(anio, mes)

    alcance = resolver_alcance_reporte(
        usuario=usuario,
        sucursal_id=sucursal_id,
        propietario_id=propietario_id,
    )

    ventas = obtener_metricas_ventas(
        sucursales_qs=alcance.sucursales_qs,
        inicio=rango_actual.inicio,
        fin=rango_actual.fin,
        inicio_anterior=rango_anterior.inicio,
        fin_anterior=rango_anterior.fin,
    )

    gastos = obtener_metricas_gastos(
        sucursales_qs=alcance.sucursales_qs,
        inicio=rango_actual.inicio,
        fin=rango_actual.fin,
        inicio_anterior=rango_anterior.inicio,
        fin_anterior=rango_anterior.fin,
    )

    nomina = obtener_metricas_nomina(
        sucursales_qs=alcance.sucursales_qs,
        inicio=rango_actual.inicio,
        fin=rango_actual.fin,
        inicio_anterior=rango_anterior.inicio,
        fin_anterior=rango_anterior.fin,
    )

    cuentas_por_pagar = obtener_metricas_cuentas_por_pagar(
    sucursales_qs=alcance.sucursales_qs,
    inicio=rango_actual.inicio,
    fin=rango_actual.fin,
    inicio_anterior=rango_anterior.inicio,
    fin_anterior=rango_anterior.fin,
)

    sucursales_resumen = obtener_resumen_sucursales(
    sucursales_qs=alcance.sucursales_qs,
    ventas=ventas,
    gastos=gastos,
    nomina=nomina,
    cuentas_por_pagar=cuentas_por_pagar,
)

    generado_en = timezone.now()

    snapshot = construir_snapshot_reporte_mensual(
        propietario=alcance.propietario,
        sucursal=alcance.sucursal,
        sucursales_qs=alcance.sucursales_qs,
        rango_actual=rango_actual,
        rango_anterior=rango_anterior,
        generado_por=usuario,
        generado_en=generado_en,
        ventas=ventas,
        gastos=gastos,
        nomina=nomina,
        cuentas_por_pagar=cuentas_por_pagar,
        sucursales_resumen=sucursales_resumen,
        schema_version=schema_version,
)

    return {
        "propietario": alcance.propietario,
        "sucursal": alcance.sucursal,
        "anio": anio,
        "mes": mes,
        "schema_version": schema_version,
        "generado_por": usuario,
        "generado_en": generado_en,
        "datos": snapshot,
    }


def _guardar_reporte_mensual(
    *,
    propietario,
    sucursal,
    anio: int,
    mes: int,
    datos: dict,
    schema_version: int,
    generado_por,
    generado_en,
) -> ReporteMensual:
    """
    Crea o actualiza explícitamente el ReporteMensual del periodo.
    """
    filtros = {
        "propietario": propietario,
        "anio": anio,
        "mes": mes,
        "sucursal": sucursal,
    }

    reporte = ReporteMensual.objects.filter(**filtros).first()

    if reporte is None:
        reporte = ReporteMensual(
            propietario=propietario,
            sucursal=sucursal,
            anio=anio,
            mes=mes,
        )

    reporte.datos = datos
    reporte.schema_version = schema_version
    reporte.generado_por = generado_por
    reporte.generado_en = generado_en

    reporte.full_clean()
    reporte.save()

    return reporte


@transaction.atomic
def generar_reporte_mensual(
    *,
    usuario,
    anio: int,
    mes: int,
    sucursal_id: int | None = None,
    propietario_id: int | None = None,
    schema_version: int = DEFAULT_SCHEMA_VERSION,
) -> ReporteMensual:
    """
    Genera o regenera el snapshot mensual y lo persiste en ReporteMensual.
    """
    payload = obtener_datos_reporte_mensual(
        usuario=usuario,
        anio=anio,
        mes=mes,
        sucursal_id=sucursal_id,
        propietario_id=propietario_id,
        schema_version=schema_version,
    )

    reporte = _guardar_reporte_mensual(
        propietario=payload["propietario"],
        sucursal=payload["sucursal"],
        anio=payload["anio"],
        mes=payload["mes"],
        datos=payload["datos"],
        schema_version=payload["schema_version"],
        generado_por=payload["generado_por"],
        generado_en=payload["generado_en"],
    )

    return reporte