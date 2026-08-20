from calendar import monthrange
from decimal import Decimal
from django.db.models import Q
from datetime import timedelta, date

from django.db.models import Sum
from django.views.generic import TemplateView

from apps.gastos.models import Gasto
from apps.ventas.models import ResumenSemanal, VentaDiaria
from apps.sucursales.models import Sucursal
from apps.servicios.models import ServicioRecurrente, PagoServicio
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import SucursalPermissionMixin, ModulePermissionMixin



class DashboardView(ModulePermissionMixin,SucursalPermissionMixin, LoginRequiredMixin, TemplateView):

    template_name = "dashboard/home.html"
    module_permission = "administracion"

    def dispatch(self, request, *args, **kwargs):
        print("Usuario:", request.user)
        print("Autenticado:", request.user.is_authenticated)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        hoy = date.today()

        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)



        servicios_por_vencer = []
        servicios_vencidos = []
        if self.request.user.is_superuser:
            servicios = ServicioRecurrente.objects.filter(
                activo=True
            )
        else:
            servicios = ServicioRecurrente.objects.filter(
                activo=True
            ).filter(
                Q(sucursal__propietario=self.request.user) |
                Q(sucursal__usuarios=self.request.user)
            ).distinct()

        for servicio in servicios:

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

        sucursales = self.get_sucursales_usuario()

        ventas_hoy = VentaDiaria.objects.filter(fecha=hoy)



        if not self.request.user.is_superuser:
            ventas_hoy = ventas_hoy.filter(
                Q(sucursal__propietario=self.request.user) |
                Q(sucursal__usuarios=self.request.user)
            ).distinct()

        if sucursal_id:
            sucursal = sucursales.filter(id=sucursal_id).first()

            if sucursal:
                ventas_hoy = ventas_hoy.filter(
                    sucursal=sucursal
                )

        totales_hoy = ventas_hoy.aggregate(
            efectivo=Sum("efectivo"),
            tarjeta=Sum("tarjeta")
        )

        ventas_hoy_efectivo = (
            totales_hoy["efectivo"]
            or Decimal("0.00")
        )

        ventas_hoy_tarjeta = (
            totales_hoy["tarjeta"]
            or Decimal("0.00")
        )

        total_ventas_hoy = (
            ventas_hoy_efectivo +
            ventas_hoy_tarjeta
        )

        ventas_semana = ResumenSemanal.objects.filter(
            fecha_inicio=inicio_semana,
            fecha_fin=fin_semana
        )

        if not self.request.user.is_superuser:
            ventas_semana = ventas_semana.filter(
                Q(sucursal__propietario=self.request.user) |
                Q(sucursal__usuarios=self.request.user)
            ).distinct()

        if sucursal_id:
            sucursal = sucursales.filter(id=sucursal_id).first()

            if sucursal:
                ventas_semana = ventas_semana.filter(
                    sucursal=sucursal
                )

        totales_semana = ventas_semana.aggregate(
            efectivo=Sum("efectivo"),
            tarjeta=Sum("tarjeta")
        )

        ventas_semana_efectivo = (
            totales_semana["efectivo"]
            or Decimal("0.00")
        )

        ventas_semana_tarjeta = (
            totales_semana["tarjeta"]
            or Decimal("0.00")
        )

        total_ventas_semana = (
            ventas_semana_efectivo +
            ventas_semana_tarjeta
        )








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
        #Mensual 
        ventas = VentaDiaria.objects.filter(
            fecha__range=[inicio_mes, fin_mes]
        )

        if not self.request.user.is_superuser:
            ventas = ventas.filter(
                Q(sucursal__propietario=self.request.user) |
                Q(sucursal__usuarios=self.request.user)
            ).distinct()



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
            or Decimal("0.0")
        )

        total_ventas = (
            ventas_efectivo +
            ventas_tarjeta
        )

        total_gastos = (
            gastos.aggregate(
                total=Sum("monto")
            )["total"]
            or Decimal("0")
        )

        utilidad = (
            total_ventas -
            total_gastos
        )

        margen = (
            utilidad / total_ventas * 100
        ) if total_ventas else Decimal("0.00")



        context["ventas_hoy_efectivo"] = ventas_hoy_efectivo
        context["ventas_hoy_tarjeta"] = ventas_hoy_tarjeta
        context["total_ventas_hoy"] = total_ventas_hoy

        context["ventas_semana_efectivo"] = ventas_semana_efectivo
        context["ventas_semana_tarjeta"] = ventas_semana_tarjeta
        context["total_ventas_semana"] = total_ventas_semana

        context["inicio_semana"] = inicio_semana
        context["fin_semana"] = fin_semana






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