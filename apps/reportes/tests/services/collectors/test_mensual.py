from decimal import Decimal
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from apps.gastos.models import CategoriaGasto, Gasto
from apps.nomina.models import Empleado, Nomina, PagoNomina
from apps.reportes.models import ReporteMensual
from apps.reportes.services.mensual import generar_reporte_mensual
from apps.sucursales.models import Sucursal
from apps.ventas.models import VentaDiaria


class ReporteMensualServiceTests(TestCase):

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

        VentaDiaria.objects.create(
            sucursal=self.sucursal,
            usuario=self.user,
            fecha=date(2026, 8, 5),
            efectivo=Decimal("700.00"),
            tarjeta=Decimal("300.00"),
        )

        self.cat_renta = CategoriaGasto.objects.create(nombre="Renta")
        self.cat_nomina = CategoriaGasto.objects.create(nombre="nómina")

        Gasto.objects.create(
            sucursal=self.sucursal,
            fecha=date(2026, 8, 10),
            categoria=self.cat_renta,
            monto=Decimal("400.00"),
        )

        empleado = Empleado.objects.create(
            nombre="Ana",
            sucursal=self.sucursal,
            puesto="Cajera",
            fecha_ingreso=date(2026, 1, 1),
            tipo_nomina="SEMANA",
            salario_periodo=Decimal("1000.00"),
        )

        nomina = Nomina.objects.create(
            empleado=empleado,
            fecha_inicio=date(2026, 8, 1),
            fecha_fin=date(2026, 8, 7),
            fecha_vencimiento=date(2026, 8, 8),
            monto=Decimal("1000.00"),
            estado="pagada",
        )

        PagoNomina.objects.create(
            nomina=nomina,
            fecha_pago=date(2026, 8, 8),
            monto=Decimal("1000.00"),
        )

    def test_generar_reporte_mensual_consolidado(self):
        reporte = generar_reporte_mensual(
            usuario=self.user,
            anio=2026,
            mes=8,
        )

        self.assertIsInstance(reporte, ReporteMensual)
        self.assertEqual(reporte.propietario, self.user)
        self.assertIsNone(reporte.sucursal)
        self.assertEqual(reporte.anio, 2026)
        self.assertEqual(reporte.mes, 8)

        self.assertEqual(reporte.datos["tipo"], "reporte_mensual")
        self.assertEqual(reporte.datos["ventas"]["actual"]["total"], "1000.00")
        self.assertEqual(
            reporte.datos["gastos"]["actual"]["total_registrado"],
            "400.00",
        )
        self.assertEqual(
            reporte.datos["nomina"]["actual"]["total_pagado"],
            "1000.00",
        )

    def test_regenerar_reporte_mensual_actualiza_mismo_registro(self):
        reporte_1 = generar_reporte_mensual(
            usuario=self.user,
            anio=2026,
            mes=8,
        )

        Gasto.objects.create(
            sucursal=self.sucursal,
            fecha=date(2026, 8, 20),
            categoria=self.cat_renta,
            monto=Decimal("100.00"),
        )

        reporte_2 = generar_reporte_mensual(
            usuario=self.user,
            anio=2026,
            mes=8,
        )

        self.assertEqual(reporte_1.id, reporte_2.id)
        self.assertEqual(
            reporte_2.datos["gastos"]["actual"]["total_registrado"],
            "500.00",
        )
        self.assertEqual(ReporteMensual.objects.count(), 1)

    def test_generar_reporte_mensual_por_sucursal(self):
        reporte = generar_reporte_mensual(
            usuario=self.user,
            anio=2026,
            mes=8,
            sucursal_id=self.sucursal.id,
        )

        self.assertEqual(reporte.sucursal, self.sucursal)
        self.assertFalse(reporte.datos["alcance"]["consolidado"])
        self.assertEqual(
            reporte.datos["alcance"]["sucursal_nombre"],
            self.sucursal.nombre,
        )