from decimal import Decimal
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from apps.nomina.models import Empleado, Nomina, PagoNomina
from apps.reportes.services.collectors.nomina import obtener_metricas_nomina
from apps.sucursales.models import Sucursal


class NominaCollectorTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="owner",
            password="123"
        )

        self.sucursal = Sucursal.objects.create(
            propietario=self.user,
            nombre="Sucursal Centro"
        )

        self.empleado_1 = Empleado.objects.create(
            nombre="Ana",
            sucursal=self.sucursal,
            puesto="Cajera",
            fecha_ingreso=date(2026, 1, 1),
            tipo_nomina="SEMANA",
            salario_periodo=Decimal("1000.00"),
        )

        self.empleado_2 = Empleado.objects.create(
            nombre="Luis",
            sucursal=self.sucursal,
            puesto="Cocinero",
            fecha_ingreso=date(2026, 1, 1),
            tipo_nomina="SEMANA",
            salario_periodo=Decimal("1200.00"),
        )

        # Pagada en agosto
        self.nomina_agosto = Nomina.objects.create(
            empleado=self.empleado_1,
            fecha_inicio=date(2026, 8, 1),
            fecha_fin=date(2026, 8, 7),
            fecha_vencimiento=date(2026, 8, 8),
            monto=Decimal("1000.00"),
            estado="pagada",
        )

        PagoNomina.objects.create(
            nomina=self.nomina_agosto,
            fecha_pago=date(2026, 8, 8),
            monto=Decimal("1000.00"),
        )

        # Pagada en julio
        self.nomina_julio = Nomina.objects.create(
            empleado=self.empleado_1,
            fecha_inicio=date(2026, 7, 1),
            fecha_fin=date(2026, 7, 7),
            fecha_vencimiento=date(2026, 7, 8),
            monto=Decimal("900.00"),
            estado="pagada",
        )

        PagoNomina.objects.create(
            nomina=self.nomina_julio,
            fecha_pago=date(2026, 7, 8),
            monto=Decimal("900.00"),
        )

        # Pendiente vencida al cierre de agosto
        self.nomina_pendiente = Nomina.objects.create(
            empleado=self.empleado_2,
            fecha_inicio=date(2026, 8, 15),
            fecha_fin=date(2026, 8, 21),
            fecha_vencimiento=date(2026, 8, 22),
            monto=Decimal("1200.00"),
            estado="pendiente",
        )

        # Pago histórico sin nómina: debe excluirse
        PagoNomina.objects.create(
            nomina=None,
            fecha_pago=date(2026, 8, 10),
            monto=Decimal("999.00"),
        )

    def test_obtener_metricas_nomina(self):
        sucursales_qs = Sucursal.objects.filter(pk=self.sucursal.pk)

        resultado = obtener_metricas_nomina(
            sucursales_qs=sucursales_qs,
            inicio=date(2026, 8, 1),
            fin=date(2026, 8, 31),
            inicio_anterior=date(2026, 7, 1),
            fin_anterior=date(2026, 7, 31),
        )

        self.assertEqual(
            resultado["actual"]["total_pagado"],
            Decimal("1000.00"),
        )
        self.assertEqual(resultado["actual"]["cantidad_pagos"], 1)
        self.assertEqual(resultado["actual"]["empleados_pagados_distintos"], 1)

        self.assertEqual(
            resultado["periodo_anterior"]["total_pagado"],
            Decimal("900.00"),
        )

        self.assertEqual(
            resultado["pendientes_al_cierre"]["cantidad_nominas_vencidas_sin_pago"],
            1,
        )
        self.assertEqual(
            resultado["pendientes_al_cierre"]["monto_nominal_vencido"],
            Decimal("1200.00"),
        )

        self.assertEqual(len(resultado["por_sucursal"]), 1)
        self.assertEqual(
            resultado["por_sucursal"][0]["total_pagado"],
            Decimal("1000.00"),
        )
        self.assertEqual(
            resultado["por_sucursal"][0]["cantidad_nominas_vencidas_sin_pago"],
            1,
        )

    def test_excluye_pagos_sin_nomina(self):
        sucursales_qs = Sucursal.objects.filter(pk=self.sucursal.pk)

        resultado = obtener_metricas_nomina(
            sucursales_qs=sucursales_qs,
            inicio=date(2026, 8, 1),
            fin=date(2026, 8, 31),
            inicio_anterior=date(2026, 7, 1),
            fin_anterior=date(2026, 7, 31),
        )

        self.assertEqual(
            resultado["actual"]["total_pagado"],
            Decimal("1000.00"),
        )