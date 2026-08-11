from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta

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
from apps.nomina.models import PagoNomina, Empleado
from apps.compras.models import CuentaPorPagar

from .forms import ServicioRecurrenteForm, PagoServicioForm
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin,SucursalPermissionMixin,ModulePermissionMixin


class ServicioRecurrenteListView(LoginRequiredMixin,SucursalPermissionMixin, TemplateView):

    template_name = "servicios/list.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        hoy = date.today()
       

        tipo = self.request.GET.get("tipo", "todos")

        compromisos = []

        # ============================
        # SERVICIOS RECURRENTES
        # ============================

        servicios = self.filtrar_por_sucursal_usuario(
        ServicioRecurrente.objects.filter(
            activo=True
        ).select_related(
            "sucursal",
            "categoria"
        )
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

        cuentas = self.filtrar_por_sucursal_usuario(
        CuentaPorPagar.objects.select_related(
            "proveedor",
            "categoria",
            "sucursal"
        )
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
        # NÓMINA
        # ============================

        empleados = self.filtrar_por_sucursal_usuario(
        Empleado.objects.filter(
            activo=True
        ).select_related(
            "sucursal"
        )
    )



        if tipo in ["todos", "nomina"]:

            for empleado in empleados:

                if empleado.tipo_nomina == "SEMANA":

                    if hoy.weekday() <= 4:
                        fecha_pago = hoy + timedelta(
                            days=(4 - hoy.weekday())
                        )
                    else:
                        fecha_pago = hoy + timedelta(days=7)

                else:

                    if hoy.weekday() <= 6:
                        fecha_pago = hoy + timedelta(
                            days=(6 - hoy.weekday())
                        )
                    else:
                        fecha_pago = hoy + timedelta(days=7)

                ultimo_pago = empleado.pagos.order_by(
                    "-fecha_pago"
                ).first()

                if ultimo_pago:

                    if (fecha_pago - ultimo_pago.fecha_pago).days < 7:
                        continue

                dias = (fecha_pago - hoy).days

                if dias < 0:
                    estado = "vencido"
                elif dias <= 5:
                    estado = "proximo"
                else:
                    estado = "pendiente"

                compromisos.append({

                    "tipo": "Nomina",

                    "sucursal": empleado.sucursal,

                    "concepto": empleado.nombre,

                    "categoria": "Nómina",

                    "proveedor": "Empleado",

                    "monto": empleado.salario_periodo,

                    "fecha": fecha_pago,

                    "estado": estado,

                    "objeto": empleado,

                    "dias_restantes": dias,

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
    


