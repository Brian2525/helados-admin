from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta
from calendar import monthrange


from decimal import Decimal

from datetime import date

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)

from .models import ServicioRecurrente, PagoServicio
from apps.nomina.models import PagoNomina, Empleado, Nomina
from apps.compras.models import CuentaPorPagar

from .forms import ServicioRecurrenteForm, PagoServicioForm
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin,SucursalPermissionMixin,ModulePermissionMixin


class ServicioRecurrenteListView(
    LoginRequiredMixin,
    SucursalPermissionMixin,
    TemplateView
):

    template_name = "servicios/list.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        sucursal_id = self.request.GET.get("sucursal", "")

        # ==========================================================
        # SUCURSALES DISPONIBLES PARA EL USUARIO
        # ==========================================================

        sucursales = (
            self.request.user.sucursales_asignadas.all()
            | self.request.user.sucursales_propias.all()
        ).distinct().order_by("nombre")

        # ==========================================================
        # SERVICIOS
        # ==========================================================

        servicios = self.filtrar_por_sucursal_usuario(
            ServicioRecurrente.objects.filter(
                activo=True
            ).select_related(
                "sucursal",
                "categoria"
            )
        )

        # ==========================================================
        # FILTRO POR SUCURSAL
        # ==========================================================

        if sucursal_id:
            try:
                sucursal_id = int(sucursal_id)

                servicios = servicios.filter(
                    sucursal_id=sucursal_id
                )

            except (TypeError, ValueError):
                sucursal_id = ""

        # ==========================================================
        # CONTEXTO
        # ==========================================================

        context["servicios"] = servicios
        context["sucursales"] = sucursales
        context["sucursal_id"] = sucursal_id

        return context


class ServicioRecurrenteCreateView( ModulePermissionMixin, SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, CreateView):

    model = ServicioRecurrente
    module_permission = "finanzas"

    form_class = ServicioRecurrenteForm

    template_name = "servicios/form.html"

    success_url = reverse_lazy(
        "servicios:list"
    )


class ServicioRecurrenteUpdateView(ModulePermissionMixin, SucursalFormMixin, SucursalQuerysetMixin,LoginRequiredMixin, UpdateView):

    model = ServicioRecurrente
    module_permission = "finanzas"

    form_class = ServicioRecurrenteForm

    template_name = "servicios/form.html"

    success_url = reverse_lazy(
        "servicios:list"
    )


class ServicioRecurrenteDeleteView(ModulePermissionMixin, SucursalQuerysetMixin, LoginRequiredMixin, DeleteView):

    model = ServicioRecurrente
    module_permission = "finanzas"

    template_name = "servicios/delete.html"

    success_url = reverse_lazy(
        "servicios:list"
    )

class ServiciosPendientesView(ModulePermissionMixin, SucursalQuerysetMixin, LoginRequiredMixin, TemplateView):

    template_name = "servicios/pendientes.html"
    module_permission = "finanzas"
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        hoy = date.today()

        servicios = []

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

            servicios.append({
                "servicio": servicio,
                "dias_restantes": dias_restantes,
            })

        servicios.sort(
            key=lambda x: x["dias_restantes"]
        )

        context["servicios"] = servicios

        return context


class RegistrarPagoServicioView(ModulePermissionMixin, SucursalQuerysetMixin, SucursalFormMixin,LoginRequiredMixin, CreateView):

    model = PagoServicio
    form_class = PagoServicioForm
    module_permission = "finanzas"
    template_name = "servicios/pago_form.html"
    success_url = reverse_lazy(
        "servicios:list"
    )

    def get_initial(self):

        initial = super().get_initial()

        servicio = ServicioRecurrente.objects.get(
            pk=self.kwargs["pk"]
        )

        initial["servicio"] = servicio
        initial["monto"] = servicio.monto_estimado
        initial["fecha_pago"] = date.today()

        return initial
    


