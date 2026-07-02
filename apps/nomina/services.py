from datetime import date, timedelta

from .models import Empleado, PagoNomina


def obtener_nominas_pendientes():

    hoy = date.today()

    empleados = []

    # Viernes
    if hoy.weekday() == 4:

        inicio = hoy - timedelta(days=4)
        fin = hoy

        queryset = Empleado.objects.filter(
            activo=True,
            tipo_nomina="SEMANA"
        )

    # Domingo
    elif hoy.weekday() == 6:

        inicio = hoy - timedelta(days=1)
        fin = hoy

        queryset = Empleado.objects.filter(
            activo=True,
            tipo_nomina="FIN_SEMANA"
        )

    else:
        return []

    for empleado in queryset:

        ya_pagado = PagoNomina.objects.filter(
            empleado=empleado,
            fecha_inicio=inicio,
            fecha_fin=fin
        ).exists()

        if not ya_pagado:

            empleados.append({
                "empleado": empleado,
                "inicio": inicio,
                "fin": fin,
                "monto": empleado.salario_periodo
            })

    return empleados