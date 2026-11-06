from django.test import TestCase

# Create your tests here.
"""Pegar/adaptar en apps/inventario/tests/test_corte.py.

Tests unitarios de fórmula. Además se requieren pruebas integrales Django
con la BD real para fechas de corte, recetas y movimientos.
"""
from decimal import Decimal
from django.test import SimpleTestCase
from apps.inventario.services import calcular_saldo_desde_corte


class SaldoDesdeCorteTests(SimpleTestCase):
    def test_compras_ventas_y_mermas(self):
        # 100 + compra 25 - merma 5 - venta 15 = 105
        saldo = calcular_saldo_desde_corte(
            Decimal("100.0000"), Decimal("20.0000"), Decimal("15.0000")
        )
        self.assertEqual(saldo, Decimal("105.0000"))

    def test_existencia_cero_es_valida(self):
        self.assertEqual(
            calcular_saldo_desde_corte(
                Decimal("0.0000"), Decimal("0.0000"), Decimal("0.0000")
            ),
            Decimal("0.0000"),
        )

    def test_no_recorta_saldo_negativo(self):
        # Un negativo es señal de inconsistencia; no ocultarlo.
        saldo = calcular_saldo_desde_corte(
            Decimal("2.0000"), Decimal("0.0000"), Decimal("3.0000")
        )
        self.assertEqual(saldo, Decimal("-1.0000"))
