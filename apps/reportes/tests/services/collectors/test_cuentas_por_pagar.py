from decimal import Decimal
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from apps.compras.models import CuentaPorPagar, PagoCuentaPorPagar, Proveedor
from apps.gastos.models import CategoriaGasto
from apps.reportes.services.collectors.cuentas_por_pagar import (
    obtener_metricas_cuentas_por_pagar,
)
from apps.sucursales.models import Sucursal


class CuentasPorPagarCollectorTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="owner",
            password="123"
        )

        self.sucursal = Sucursal.objects.create(
            propietario=self.user,
            nombre="Sucursal Centro"
        )

        self.proveedor = Proveedor.objects.create(
            propietario=self.user,
            nombre="Proveedor Demo"
        )

        self.categoria = CategoriaGasto.objects.create(
            nombre="Insumos"
        )

        # Cuenta anterior (julio)
        self.cuenta_julio = CuentaPorPagar.objects.create(
            sucursal=self.sucursal,
            proveedor=self.proveedor,
            fecha=date(2026, 7, 5),
            fecha_vencimiento=date(2026, 7, 15),
            descripcion="Compra julio",
            monto_total=Decimal("800.00"),
            categoria=self.categoria,
        )

        PagoCuentaPorPagar.objects.create(
            cuenta=self.cuenta_julio,
            fecha=date(2026, 7, 10),
            monto=Decimal("300.00"),
        )

        PagoCuentaPorPagar.objects.create(
            cuenta=self.cuenta_julio,
            fecha=date(2026, 8, 12),
            monto=Decimal("200.00"),
        )

        # Cuenta agosto 1
        self.cuenta_agosto_1 = CuentaPorPagar.objects.create(
            sucursal=self.sucursal,
            proveedor=self.proveedor,
            fecha=date(2026, 8, 6),
            fecha_vencimiento=date(2026, 8, 20),
            descripcion="Compra agosto 1",
            monto_total=Decimal("1000.00"),
            categoria=self.categoria,
        )

        PagoCuentaPorPagar.objects.create(
            cuenta=self.cuenta_agosto_1,
            fecha=date(2026, 8, 18),
            monto=Decimal("400.00"),
        )

        # Cuenta agosto 2
        self.cuenta_agosto_2 = CuentaPorPagar.objects.create(
            sucursal=self.sucursal,
            proveedor=self.proveedor,
            fecha=date(2026, 8, 25),
            fecha_vencimiento=date(2026, 9, 10),
            descripcion="Compra agosto 2",
            monto_total=Decimal("500.00"),
            categoria=self.categoria,
        )

    def test_obtener_metricas_cuentas_por_pagar(self):
        sucursales_qs = Sucursal.objects.filter(pk=self.sucursal.pk)

        resultado = obtener_metricas_cuentas_por_pagar(
            sucursales_qs=sucursales_qs,
            inicio=date(2026, 8, 1),
            fin=date(2026, 8, 31),
            inicio_anterior=date(2026, 7, 1),
            fin_anterior=date(2026, 7, 31),
        )

        self.assertEqual(
            resultado["actual"]["cuentas_creadas_total"],
            Decimal("1500.00"),
        )
        self.assertEqual(
            resultado["actual"]["cuentas_creadas_count"],
            2,
        )
        self.assertEqual(
            resultado["actual"]["pagos_realizados_total"],
            Decimal("600.00"),
        )
        self.assertEqual(
            resultado["actual"]["pagos_realizados_count"],
            2,
        )
        self.assertEqual(
            resultado["actual"]["saldo_abierto_al_cierre"],
            Decimal("1400.00"),
        )
        self.assertEqual(
            resultado["actual"]["cuentas_con_saldo_al_cierre"],
            3,
        )
        self.assertEqual(
            resultado["actual"]["saldo_vencido_al_cierre"],
            Decimal("900.00"),
        )
        self.assertEqual(
            resultado["actual"]["cuentas_vencidas_al_cierre"],
            2,
        )

        self.assertEqual(
            resultado["periodo_anterior"]["cuentas_creadas_total"],
            Decimal("800.00"),
        )
        self.assertEqual(
            resultado["periodo_anterior"]["pagos_realizados_total"],
            Decimal("300.00"),
        )
        self.assertEqual(
            resultado["periodo_anterior"]["saldo_abierto_al_cierre"],
            Decimal("500.00"),
        )
        self.assertEqual(
            resultado["periodo_anterior"]["saldo_vencido_al_cierre"],
            Decimal("500.00"),
        )

        self.assertEqual(len(resultado["por_sucursal"]), 1)
        self.assertEqual(
            resultado["por_sucursal"][0]["saldo_abierto_al_cierre"],
            Decimal("1400.00"),
        )

        self.assertEqual(len(resultado["por_categoria"]), 1)
        self.assertEqual(
            resultado["por_categoria"][0]["cuentas_creadas_total"],
            Decimal("1500.00"),
        )

        self.assertEqual(len(resultado["top_proveedores"]), 1)
        self.assertEqual(
            resultado["top_proveedores"][0]["saldo_abierto_al_cierre"],
            Decimal("1400.00"),
        )