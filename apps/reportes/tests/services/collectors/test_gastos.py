from decimal import Decimal
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from apps.gastos.models import CategoriaGasto, Gasto
from apps.reportes.services.collectors.gastos import obtener_metricas_gastos
from apps.sucursales.models import Sucursal


class GastosCollectorTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="owner",
            password="123"
        )

        self.sucursal = Sucursal.objects.create(
            propietario=self.user,
            nombre="Sucursal Centro"
        )

        self.cat_renta = CategoriaGasto.objects.create(nombre="Renta")
        self.cat_nomina = CategoriaGasto.objects.create(nombre="nómina")

        Gasto.objects.create(
            sucursal=self.sucursal,
            fecha=date(2026, 8, 5),
            categoria=self.cat_renta,
            monto=Decimal("1000.00"),
        )

        Gasto.objects.create(
            sucursal=self.sucursal,
            fecha=date(2026, 8, 10),
            categoria=self.cat_nomina,
            monto=Decimal("500.00"),
        )

        Gasto.objects.create(
            sucursal=self.sucursal,
            fecha=date(2026, 7, 20),
            categoria=self.cat_renta,
            monto=Decimal("800.00"),
        )

    def test_obtener_metricas_gastos(self):
        sucursales_qs = Sucursal.objects.filter(pk=self.sucursal.pk)

        resultado = obtener_metricas_gastos(
            sucursales_qs=sucursales_qs,
            inicio=date(2026, 8, 1),
            fin=date(2026, 8, 31),
            inicio_anterior=date(2026, 7, 1),
            fin_anterior=date(2026, 7, 31),
        )

        self.assertEqual(resultado["actual"]["total_registrado"], Decimal("1500.00"))
        self.assertEqual(resultado["actual"]["total_categoria_nomina"], Decimal("500.00"))
        self.assertEqual(
            resultado["actual"]["total_excluyendo_categoria_nomina"],
            Decimal("1000.00"),
        )
        self.assertEqual(resultado["actual"]["cantidad_registros"], 2)

        self.assertEqual(
            resultado["periodo_anterior"]["total_registrado"],
            Decimal("800.00"),
        )

        self.assertEqual(len(resultado["por_categoria"]), 2)
        self.assertEqual(len(resultado["por_sucursal"]), 1)