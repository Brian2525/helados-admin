from calendar import monthrange
from datetime import date
from decimal import Decimal
from django.db.models import Q

from django.db.models import Sum
from django.views.generic import TemplateView

from apps.gastos.models import Gasto
from apps.ventas.models import ResumenSemanal
from apps.sucursales.models import Sucursal
from apps.servicios.models import ServicioRecurrente, PagoServicio
from django.contrib.auth.mixins import LoginRequiredMixin




class DashboardView(LoginRequiredMixin, TemplateView):

    template_name = "dashboard/home.html"

    def dispatch(self, request, *args, **kwargs):
        print("Usuario:", request.user)
        print("Autenticado:", request.user.is_authenticated)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        hoy = date.today()

        servicios_por_vencer = []
        servicios_vencidos = []

        for servicio in ServicioRecurrente.objects.filter(
            activo=True
        ):

            pagado = PagoServicio.objects.filter(
                servicio=servicio,
                fecha_pago__year=hoy.year,
                fecha_pago__month=hoy.month,
            ).exists()

            if pagado:
                continue

            dias_restantes = servicio.dia_pago - hoy.day

            item = {
                "servicio": servicio,
                "dias_restantes": dias_restantes,
            }

            if dias_restantes < 0:
                servicios_vencidos.append(item)

            elif dias_restantes <= 5:
                servicios_por_vencer.append(item)

        anio = int(
            self.request.GET.get(
                "anio",
                hoy.year
            )
        )

        mes = int(
            self.request.GET.get(
                "mes",
                hoy.month
            )
        )

        sucursal_id = self.request.GET.get("sucursal")

        if self.request.user.is_superuser:
            sucursales = Sucursal.objects.all()
        else:
            sucursales = Sucursal.objects.filter(
                Q(propietario=self.request.user) |
                Q(usuarios=self.request.user)
            ).distinct()

        ultimo_dia = monthrange(
            anio,
            mes
        )[1]

        inicio_mes = date(
            anio,
            mes,
            1
        )

        fin_mes = date(
            anio,
            mes,
            ultimo_dia
        )

        ventas = ResumenSemanal.objects.filter(
            fecha_inicio__lte=fin_mes,
            fecha_fin__gte=inicio_mes
        )

        if not self.request.user.is_superuser:
            ventas = ventas.filter(
                Q(sucursal__propietario=self.request.user) |
                Q(sucursal__usuarios=self.request.user)
            ).distinct()

        gastos = Gasto.objects.filter(
            fecha__range=[inicio_mes, fin_mes]
        )

        if not self.request.user.is_superuser:
            gastos = gastos.filter(
                Q(sucursal__propietario=self.request.user) |
                Q(sucursal__usuarios=self.request.user)
            ).distinct()
        

        if sucursal_id:
            sucursal = sucursales.filter(id=sucursal_id).first()

            if sucursal:
                ventas = ventas.filter(sucursal=sucursal)
                gastos = gastos.filter(sucursal=sucursal)

        totales_ventas = ventas.aggregate(
            efectivo=Sum("efectivo"),
            tarjeta=Sum("tarjeta")
        )

        ventas_efectivo = (
            totales_ventas["efectivo"]
            or Decimal("0.00")
        )

        ventas_tarjeta = (
            totales_ventas["tarjeta"]
            or Decimal("0.00")
        )

        total_ventas = (
            ventas_efectivo +
            ventas_tarjeta
        )

        total_gastos = (
            gastos.aggregate(
                total=Sum("monto")
            )["total"]
            or Decimal("0.00")
        )

        utilidad = (
            total_ventas -
            total_gastos
        )

        margen = (
            utilidad / total_ventas * 100
        ) if total_ventas else Decimal("0.00")

        context["ventas_efectivo"] = ventas_efectivo
        context["ventas_tarjeta"] = ventas_tarjeta
        context["total_ventas"] = total_ventas
        context["total_gastos"] = total_gastos
        context["utilidad"] = utilidad
        context["margen"] = margen

        context["servicios_vencidos"] = servicios_vencidos
        context["servicios_por_vencer"] = servicios_por_vencer

        context["mes_seleccionado"] = mes
        context["anio_seleccionado"] = anio

        context["sucursales"] = sucursales

        context["sucursal_seleccionada"] = (
            int(sucursal_id)
            if sucursal_id
            else None
        )

        return context