from decimal import Decimal
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.gastos.models import CategoriaGasto, Gasto
from apps.nomina.models import Empleado, Nomina, PagoNomina
from apps.reportes.models import ReporteMensual
from apps.sucursales.models import Sucursal
from apps.ventas.models import VentaDiaria


class ReporteMensualViewsTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="123456"
        )

        self.owner = User.objects.create_user(
            username="owner",
            password="123456"
        )

        self.sucursal = Sucursal.objects.create(
            propietario=self.owner,
            nombre="Sucursal Centro",
            activa=True,
        )

        self.cat_renta = CategoriaGasto.objects.create(nombre="Renta")
        self.cat_nomina = CategoriaGasto.objects.create(nombre="nómina")

        VentaDiaria.objects.create(
            sucursal=self.sucursal,
            usuario=self.user,
            fecha=date(2026, 8, 5),
            efectivo=Decimal("700.00"),
            tarjeta=Decimal("300.00"),
        )

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

        self.client.login(
            username="admin",
            password="123456"
        )

    def test_generar_reporte_mensual_view(self):
        url = reverse("reportes:reporte_mensual_generar")

        response = self.client.post(
            url,
            data={
                "anio": 2026,
                "mes": 8,
                "propietario": self.owner.id,
            },
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ReporteMensual.objects.count(), 1)

        reporte = ReporteMensual.objects.first()
        self.assertEqual(reporte.propietario, self.owner)
        self.assertIsNone(reporte.sucursal)
        self.assertEqual(reporte.schema_version, 1)
        self.assertEqual(reporte.datos["ventas"]["actual"]["total"], "1000.00")

    def test_ver_json_reporte_mensual_view(self):
        reporte = ReporteMensual.objects.create(
            propietario=self.owner,
            sucursal=None,
            anio=2026,
            mes=8,
            schema_version=1,
            datos={
                "schema_version": 1,
                "tipo": "reporte_mensual",
                "ventas": {"actual": {"total": "1000.00"}},
            },
        )

        url = reverse(
            "reportes:reporte_mensual_json",
            kwargs={"pk": reporte.pk},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertContains(response, '"schema_version": 1')
        self.assertContains(response, '"tipo": "reporte_mensual"')

    def test_regenerar_reporte_mensual_view_actualiza_mismo_registro(self):
        reporte = ReporteMensual.objects.create(
            propietario=self.owner,
            sucursal=None,
            anio=2026,
            mes=8,
            schema_version=1,
            datos={"schema_version": 1},
        )

        Gasto.objects.create(
            sucursal=self.sucursal,
            fecha=date(2026, 8, 20),
            categoria=self.cat_renta,
            monto=Decimal("100.00"),
        )

        url = reverse(
            "reportes:reporte_mensual_regenerar",
            kwargs={"pk": reporte.pk},
        )

        response = self.client.post(url, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ReporteMensual.objects.count(), 1)

        reporte.refresh_from_db()
        self.assertEqual(reporte.id, reporte.pk)
        self.assertEqual(reporte.schema_version, 1)
        self.assertEqual(
            reporte.datos["gastos"]["actual"]["total_registrado"],
            "500.00",
        )

    def test_list_view_muestra_reportes(self):
        ReporteMensual.objects.create(
            propietario=self.owner,
            sucursal=None,
            anio=2026,
            mes=8,
            schema_version=1,
            datos={"schema_version": 1},
        )

        url = reverse("reportes:reporte_mensual_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reportes mensuales")
        self.assertContains(response, "Consolidado")

    def test_list_view_filtra_por_anio_y_mes(self):
        ReporteMensual.objects.create(
            propietario=self.owner,
            sucursal=None,
            anio=2026,
            mes=8,
            schema_version=1,
            datos={"schema_version": 1},
        )

        ReporteMensual.objects.create(
            propietario=self.owner,
            sucursal=None,
            anio=2025,
            mes=7,
            schema_version=1,
            datos={"schema_version": 1},
        )

        url = reverse("reportes:reporte_mensual_list")
        response = self.client.get(
            url,
            data={
                "anio": 2026,
                "mes": 8,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2026")
        self.assertContains(response, "8/2026")
        self.assertNotContains(response, "7/2025")


    def test_regenerar_reporte_no_permite_get(self):
        reporte = ReporteMensual.objects.create(
            propietario=self.owner,
            sucursal=None,
            anio=2026,
            mes=8,
            schema_version=1,
            datos={"schema_version": 1},
        )

        url = reverse(
            "reportes:reporte_mensual_regenerar",
            kwargs={"pk": reporte.pk},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)