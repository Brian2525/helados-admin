from datetime import timedelta, date    

from django.utils import timezone 

from .models import Empleado, Nomina 


def generar_nominas(tipo_nomina):

    hoy = timezone.localdate()
    weekday = hoy.weekday()

    empleados = Empleado.objects.filter(
        activo=True,
        tipo_nomina=tipo_nomina,
    )

    nominas_creadas = []

    for empleado in empleados:

        # ==========================================
        # LUNES - VIERNES
        # ==========================================

        if tipo_nomina == "SEMANA":

            fecha_inicio = hoy - timedelta(
                days=weekday
            )

            fecha_fin = fecha_inicio + timedelta(
                days=4
            )

        # ==========================================
        # SÁBADO - DOMINGO
        # ==========================================

        elif tipo_nomina == "FIN_SEMANA":

            fecha_inicio = hoy
            fecha_fin = hoy + timedelta(days=1)

        else:
            raise ValueError(
                f"Tipo de nómina no válido: {tipo_nomina}"
            )

        # ==========================================
        # CREAR NOMINA
        # ==========================================

        nomina, creada = Nomina.objects.get_or_create(
            empleado=empleado,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            defaults={
                "fecha_vencimiento": fecha_fin,
                "monto": empleado.salario_periodo,
                "estado": "pendiente",
            }
        )

        if creada:
            nominas_creadas.append(nomina)

    return nominas_creadas