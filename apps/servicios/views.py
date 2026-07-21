from django.urls import reverse_lazy
from datetime import date

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)

from .models import ServicioRecurrente, PagoServicio
from apps.compras.models import CuentaPorPagar

from .forms import ServicioRecurrenteForm, PagoServicioForm
from django.contrib.auth.mixins import LoginRequiredMixin


class ServicioRecurrenteListView(LoginRequiredMixin, TemplateView):

    template_name = "servicios/list.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        hoy = date.today()
       

        tipo = self.request.GET.get("tipo", "todos")

        compromisos = []

        # ============================
        # SERVICIOS RECURRENTES
        # ============================

        servicios = ServicioRecurrente.objects.filter(
            activo=True
        ).select_related(
            "sucursal",
            "categoria"
        )

        if not self.request.user.is_superuser:
            servicios = servicios.filter(
                sucursal__usuarios=self.request.user
            )

        if tipo in ["todos", "servicios"]:

            for servicio in servicios:

                pagado = PagoServicio.objects.filter(
                    servicio=servicio,
                    fecha_pago__year=hoy.year,
                    fecha_pago__month=hoy.month,
                ).exists()

                if pagado:
                    continue

                fecha_vencimiento = date(
                    hoy.year,
                    hoy.month,
                    servicio.dia_pago
                )

                dias = (fecha_vencimiento - hoy).days
                dias_restantes = (fecha_vencimiento - hoy).days

                if dias < 0:
                    estado = "vencido"
                elif dias <= 5:
                    estado = "proximo"
                else:
                    estado = "pendiente"

                compromisos.append({
                    "tipo": "Servicio",
                    "sucursal": servicio.sucursal,
                    "concepto": servicio.nombre,
                    "categoria": servicio.categoria,
                    "proveedor": servicio.proveedor,
                    "monto": servicio.monto_estimado,
                    "fecha": fecha_vencimiento,
                    "estado": estado,
                    "objeto": servicio,
                    "dias_restantes": dias_restantes,
                })

        # ============================
        # CUENTAS POR PAGAR
        # ============================

        cuentas = CuentaPorPagar.objects.select_related(
            "proveedor",
            "categoria",
            "sucursal"
        )

        if not self.request.user.is_superuser:
            cuentas = cuentas.filter(
                sucursal__usuarios=self.request.user
            )

        if tipo in ["todos", "cuentas"]:

            for cuenta in cuentas:

                if cuenta.estatus == "pagado":
                    continue

                compromisos.append({
                    "tipo": "Cuenta",
                    "sucursal": cuenta.sucursal,
                    "concepto": cuenta.descripcion,
                    "categoria": cuenta.categoria,
                    "proveedor": cuenta.proveedor,
                    "monto": cuenta.saldo,
                    "fecha": cuenta.fecha_vencimiento,
                    "estado": cuenta.estatus,
                    "objeto": cuenta,
                    "dias_restantes": (cuenta.fecha_vencimiento - hoy).days,
                })

        # ============================
        # ORDENAR POR FECHA
        # ============================

        compromisos.sort(
            key=lambda x: x["fecha"]
        )

        context["compromisos"] = compromisos
        context["tipo"] = tipo

        return context


class ServicioRecurrenteCreateView(LoginRequiredMixin, CreateView):

    model = ServicioRecurrente
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )

    form_class = ServicioRecurrenteForm

    template_name = "servicios/form.html"

    success_url = reverse_lazy(
        "servicios:list"
    )


class ServicioRecurrenteUpdateView(LoginRequiredMixin, UpdateView):

    model = ServicioRecurrente
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )

    form_class = ServicioRecurrenteForm

    template_name = "servicios/form.html"

    success_url = reverse_lazy(
        "servicios:list"
    )


class ServicioRecurrenteDeleteView(LoginRequiredMixin, DeleteView):

    model = ServicioRecurrente
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )

    template_name = "servicios/delete.html"

    success_url = reverse_lazy(
        "servicios:list"
    )

class ServiciosPendientesView(LoginRequiredMixin, TemplateView):

    template_name = "servicios/pendientes.html"

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


class RegistrarPagoServicioView(LoginRequiredMixin, CreateView):

    model = PagoServicio

    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )

    form_class = PagoServicioForm

    template_name = "servicios/pago_form.html"

    success_url = reverse_lazy(
        "servicios:pendientes"
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