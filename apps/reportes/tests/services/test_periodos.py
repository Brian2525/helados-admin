from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from apps.reportes.services.periodos import (
    validar_periodo,
    obtener_rango_mensual,
    obtener_periodo_anterior,
)


class PeriodosServiceTests(SimpleTestCase):

    def test_obtener_rango_mensual_agosto_2026(self):
        rango = obtener_rango_mensual(2026, 8)

        self.assertEqual(str(rango.inicio), "2026-08-01")
        self.assertEqual(str(rango.fin), "2026-08-31")
        self.assertEqual(rango.anio, 2026)
        self.assertEqual(rango.mes, 8)

    def test_obtener_periodo_anterior_agosto_2026(self):
        anterior = obtener_periodo_anterior(2026, 8)

        self.assertEqual(anterior.anio, 2026)
        self.assertEqual(anterior.mes, 7)
        self.assertEqual(str(anterior.inicio), "2026-07-01")
        self.assertEqual(str(anterior.fin), "2026-07-31")

    def test_obtener_periodo_anterior_enero_2026(self):
        anterior = obtener_periodo_anterior(2026, 1)

        self.assertEqual(anterior.anio, 2025)
        self.assertEqual(anterior.mes, 12)
        self.assertEqual(str(anterior.inicio), "2025-12-01")
        self.assertEqual(str(anterior.fin), "2025-12-31")

    def test_validar_periodo_falla_si_mes_menor_a_1(self):
        with self.assertRaises(ValidationError):
            validar_periodo(2026, 0)

    def test_validar_periodo_falla_si_mes_mayor_a_12(self):
        with self.assertRaises(ValidationError):
            validar_periodo(2026, 13)

    def test_validar_periodo_falla_si_anio_fuera_de_rango(self):
        with self.assertRaises(ValidationError):
            validar_periodo(1999, 8)