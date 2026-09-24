from decimal import Decimal
from datetime import date, datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.reportes.services.builders import construir_snapshot_reporte_mensual
from apps.reportes.services.periodos import obtener_periodo_anterior, obtener_rango_mensual
from apps.sucursales.models import Sucursal


class BuildersServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="owner",
            password="123"
        )

        self.sucursal = Sucursal.objects.create(
            propietario=self.user,
            nombre="Sucursal Centro",
            activa=True,
        )

    def test_construir_snapshot_reporte_mensual(self):
        rango_actual = obtener_rango_mensual(2026, 8)
        rango_anterior = obtener_periodo_anterior(2026, 8)

        ventas = {
            "actual": {
                "total": Decimal("1000.00"),
                "efectivo": Decimal("700.00"),
                "tarjeta": Decimal("300.00"),
                "registros_diarios": 5,
                "fechas_unicas_registradas": 5,
            },
            "periodo_anterior": {
                "total": Decimal("900.00"),
                "efectivo": Decimal("600.00"),
                "tarjeta": Decimal("300.00"),
                "registros_diarios": 4,
                "fechas_unicas_registradas": 4,
            },
            "comparaciones": {
                "total": {
                    "actual": Decimal("1000.00"),
                    "periodo_anterior": Decimal("900.00"),
                    "variacion_absoluta": Decimal("100.00"),
                    "variacion_porcentual": Decimal("11.11"),
                    "comparable": True,
                }
            },
            "por_sucursal": [],
        }

        gastos = {
            "actual": {
                "total_registrado": Decimal("400.00"),
                "total_categoria_nomina": Decimal("100.00"),
                "total_excluyendo_categoria_nomina": Decimal("300.00"),
                "cantidad_registros": 2,
            },
            "periodo_anterior": {
                "total_registrado": Decimal("350.00"),
                "total_categoria_nomina": Decimal("50.00"),
                "total_excluyendo_categoria_nomina": Decimal("300.00"),
                "cantidad_registros": 2,
            },
            "comparaciones": {},
            "por_categoria": [],
            "por_sucursal": [],
        }

        nomina = {
            "criterio": {
                "pagada": "PagoNomina.fecha_pago",
                "pendiente_al_cierre": "Nomina sin pago con fecha_vencimiento <= fin del periodo",
                "incluye_solo_pagos_con_nomina_asociada": True,
                "pagos_sin_nomina_se_excluyen": True,
            },
            "actual": {
                "total_pagado": Decimal("250.00"),
                "cantidad_pagos": 1,
                "empleados_pagados_distintos": 1,
            },
            "periodo_anterior": {
                "total_pagado": Decimal("200.00"),
                "cantidad_pagos": 1,
                "empleados_pagados_distintos": 1,
            },
            "comparaciones": {},
            "pendientes_al_cierre": {
                "cantidad_nominas_vencidas_sin_pago": 0,
                "monto_nominal_vencido": Decimal("0.00"),
            },
            "por_sucursal": [],
        }

        sucursales_resumen = [
            {
                "id": self.sucursal.id,
                "nombre": self.sucursal.nombre,
                "activa": True,
                "ventas": {
                    "total": Decimal("1000.00"),
                    "efectivo": Decimal("700.00"),
                    "tarjeta": Decimal("300.00"),
                    "registros_diarios": 5,
                    "fechas_unicas_registradas": 5,
                },
                "gastos": {
                    "total_registrado": Decimal("400.00"),
                    "total_categoria_nomina": Decimal("100.00"),
                    "total_excluyendo_categoria_nomina": Decimal("300.00"),
                    "cantidad_registros": 2,
                },
                "nomina": {
                    "total_pagado": Decimal("250.00"),
                    "cantidad_pagos": 1,
                    "empleados_pagados_distintos": 1,
                    "cantidad_nominas_vencidas_sin_pago": 0,
                    "monto_nominal_vencido": Decimal("0.00"),
                },
            }
        ]

        snapshot = construir_snapshot_reporte_mensual(
            propietario=self.user,
            sucursal=self.sucursal,
            sucursales_qs=Sucursal.objects.filter(pk=self.sucursal.pk),
            rango_actual=rango_actual,
            rango_anterior=rango_anterior,
            generado_por=self.user,
            generado_en=timezone.now(),
            ventas=ventas,
            gastos=gastos,
            nomina=nomina,
            sucursales_resumen=sucursales_resumen,
            schema_version=1,
        )

        self.assertEqual(snapshot["schema_version"], 1)
        self.assertEqual(snapshot["tipo"], "reporte_mensual")
        self.assertEqual(snapshot["propietario"]["username"], "owner")
        self.assertEqual(snapshot["alcance"]["consolidado"], False)
        self.assertEqual(snapshot["alcance"]["sucursal_nombre"], "Sucursal Centro")
        self.assertEqual(snapshot["periodo"]["inicio"], "2026-08-01")
        self.assertEqual(snapshot["periodo"]["fin"], "2026-08-31")
        self.assertEqual(snapshot["ventas"]["actual"]["total"], "1000.00")
        self.assertEqual(snapshot["gastos"]["actual"]["total_registrado"], "400.00")
        self.assertEqual(snapshot["nomina"]["actual"]["total_pagado"], "250.00")
        self.assertEqual(snapshot["sucursales"][0]["ventas"]["total"], "1000.00")
        self.assertIn("modulos_incluidos", snapshot)
        self.assertIn("advertencias", snapshot)