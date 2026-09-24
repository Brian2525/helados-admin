from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from apps.reportes.services.collectors.sucursales import obtener_resumen_sucursales
from apps.sucursales.models import Sucursal


class SucursalesCollectorTests(TestCase):

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

    def test_obtener_resumen_sucursales(self):
        sucursales_qs = Sucursal.objects.filter(pk=self.sucursal.pk)

        ventas = {
            "por_sucursal": [
                {
                    "sucursal_id": self.sucursal.id,
                    "sucursal_nombre": self.sucursal.nombre,
                    "total": Decimal("1000.00"),
                    "efectivo": Decimal("700.00"),
                    "tarjeta": Decimal("300.00"),
                    "registros_diarios": 5,
                    "fechas_unicas_registradas": 5,
                }
            ]
        }

        gastos = {
            "por_sucursal": [
                {
                    "sucursal_id": self.sucursal.id,
                    "sucursal_nombre": self.sucursal.nombre,
                    "total_registrado": Decimal("400.00"),
                    "total_categoria_nomina": Decimal("100.00"),
                    "total_excluyendo_categoria_nomina": Decimal("300.00"),
                    "cantidad_registros": 2,
                }
            ]
        }

        nomina = {
            "por_sucursal": [
                {
                    "sucursal_id": self.sucursal.id,
                    "sucursal_nombre": self.sucursal.nombre,
                    "total_pagado": Decimal("250.00"),
                    "cantidad_pagos": 1,
                    "empleados_pagados_distintos": 1,
                    "cantidad_nominas_vencidas_sin_pago": 0,
                    "monto_nominal_vencido": Decimal("0.00"),
                }
            ]
        }

        resultado = obtener_resumen_sucursales(
            sucursales_qs=sucursales_qs,
            ventas=ventas,
            gastos=gastos,
            nomina=nomina,
        )

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["nombre"], "Sucursal Centro")
        self.assertEqual(resultado[0]["ventas"]["total"], Decimal("1000.00"))
        self.assertEqual(resultado[0]["gastos"]["total_registrado"], Decimal("400.00"))
        self.assertEqual(resultado[0]["nomina"]["total_pagado"], Decimal("250.00"))