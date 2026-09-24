# apps/reportes/services/periodos.py

import calendar
from dataclasses import dataclass
from datetime import date

from django.core.exceptions import ValidationError
from django.utils import timezone


@dataclass(frozen=True)
class RangoPeriodo:
    anio: int
    mes: int
    inicio: date
    fin: date


def validar_periodo(anio: int, mes: int) -> None:
    if mes < 1 or mes > 12:
        raise ValidationError({"mes": "El mes debe estar entre 1 y 12."})

    if anio < 2000 or anio > 2100:
        raise ValidationError({"anio": "El año está fuera del rango permitido."})

    anio_actual = timezone.localdate().year
    if anio > anio_actual + 1:
        raise ValidationError(
            {"anio": "No se permite generar reportes para años demasiado futuros."}
        )


def obtener_rango_mensual(anio: int, mes: int) -> RangoPeriodo:
    validar_periodo(anio, mes)

    ultimo_dia = calendar.monthrange(anio, mes)[1]

    return RangoPeriodo(
        anio=anio,
        mes=mes,
        inicio=date(anio, mes, 1),
        fin=date(anio, mes, ultimo_dia),
    )


def obtener_periodo_anterior(anio: int, mes: int) -> RangoPeriodo:
    validar_periodo(anio, mes)

    if mes == 1:
        anio_anterior = anio - 1
        mes_anterior = 12
    else:
        anio_anterior = anio
        mes_anterior = mes - 1

    return obtener_rango_mensual(anio_anterior, mes_anterior)