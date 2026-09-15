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

        hoy = date.today()

        # ==========================================================
        # FILTROS
        # ==========================================================

        tipo = self.request.GET.get("tipo", "todos")

        try:
            mes = int(self.request.GET.get("mes", hoy.month))
            if mes < 1 or mes > 12:
                mes = hoy.month
        except (TypeError, ValueError):
            mes = hoy.month

        try:
            anio = int(self.request.GET.get("anio", hoy.year))
        except (TypeError, ValueError):
            anio = hoy.year

        sucursal_id = self.request.GET.get("sucursal", "")

        compromisos = []

        # ==========================================================
        # SUCURSALES DISPONIBLES PARA EL USUARIO
        # ==========================================================

        sucursales = self.request.user.sucursales_asignadas.all()

        # Si el usuario es propietario, agregar sus sucursales
        sucursales_propias = self.request.user.sucursales_propias.all()

        sucursales = (
            (sucursales | sucursales_propias)
            .distinct()
            .order_by("nombre")
        )

        # ==========================================================
        # FILTRO DE SUCURSAL
        # ==========================================================

        if sucursal_id:
            try:
                sucursal_id = int(sucursal_id)
            except (TypeError, ValueError):
                sucursal_id = ""

        # ==========================================================
        # SERVICIOS RECURRENTES
        # ==========================================================

        if tipo in ["todos", "servicios"]:

            servicios = self.filtrar_por_sucursal_usuario(
                ServicioRecurrente.objects.filter(
                    activo=True
                ).select_related(
                    "sucursal",
                    "categoria"
                )
            )

            if sucursal_id:
                servicios = servicios.filter(
                    sucursal_id=sucursal_id
                )

            # Último día del mes seleccionado
            ultimo_dia = monthrange(anio, mes)[1]

            for servicio in servicios:

                # --------------------------------------------------
                # ¿Ya fue pagado ese servicio durante el mes?
                # --------------------------------------------------

                pagado = PagoServicio.objects.filter(
                    servicio=servicio,
                    fecha_pago__year=anio,
                    fecha_pago__month=mes,
                ).exists()

                if pagado:
                    continue

                # --------------------------------------------------
                # Evitar error para servicios con día 29, 30 o 31
                # en meses que no tienen ese día.
                # --------------------------------------------------

                dia_pago = min(
                    servicio.dia_pago,
                    ultimo_dia
                )

                fecha_vencimiento = date(
                    anio,
                    mes,
                    dia_pago
                )

                dias_restantes = (
                    fecha_vencimiento - hoy
                ).days

                if dias_restantes < 0:
                    estado = "vencido"
                elif dias_restantes <= 5:
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

        # ==========================================================
        # CUENTAS POR PAGAR
        # ==========================================================

        if tipo in ["todos", "cuentas"]:

            cuentas = self.filtrar_por_sucursal_usuario(
                CuentaPorPagar.objects.select_related(
                    "proveedor",
                    "categoria",
                    "sucursal"
                )
            )

            if sucursal_id:
                cuentas = cuentas.filter(
                    sucursal_id=sucursal_id
                )

            # Filtrar por mes y año
            cuentas = cuentas.filter(
                fecha_vencimiento__year=anio,
                fecha_vencimiento__month=mes,
            )

            for cuenta in cuentas:

                if cuenta.estatus == "pagado":
                    continue

                dias_restantes = (
                    cuenta.fecha_vencimiento - hoy
                ).days

                # Si tu modelo usa "parcial", conservarlo
                if cuenta.estatus == "parcial":
                    estado = "parcial"
                elif dias_restantes < 0:
                    estado = "vencido"
                elif dias_restantes <= 5:
                    estado = "proximo"
                else:
                    estado = "pendiente"

                compromisos.append({
                    "tipo": "Cuenta",
                    "sucursal": cuenta.sucursal,
                    "concepto": cuenta.descripcion,
                    "categoria": cuenta.categoria,
                    "proveedor": cuenta.proveedor,
                    "monto": cuenta.saldo,
                    "fecha": cuenta.fecha_vencimiento,
                    "estado": estado,
                    "objeto": cuenta,
                    "dias_restantes": dias_restantes,
                })

        # ==========================================================
        # NÓMINA
        # ==========================================================

        if tipo in ["todos", "nomina"]:

            empleados = self.filtrar_por_sucursal_usuario(
                Empleado.objects.filter(
                    activo=True
                ).select_related(
                    "sucursal"
                )
            )

            if sucursal_id:
                empleados = empleados.filter(
                    sucursal_id=sucursal_id
                )

            nominas = Nomina.objects.filter(
                empleado__in=empleados,
                estado__in=["pendiente", "vencida"],
                fecha_vencimiento__year=anio,
                fecha_vencimiento__month=mes,
            ).select_related(
                "empleado",
                "empleado__sucursal",
            )

            for nomina in nominas:

                dias_restantes = (
                    nomina.fecha_vencimiento - hoy
                ).days

                if dias_restantes < 0:
                    estado = "vencido"
                elif dias_restantes <= 5:
                    estado = "proximo"
                else:
                    estado = "pendiente"

                compromisos.append({
                    "tipo": "Nomina",
                    "sucursal": nomina.empleado.sucursal,
                    "concepto": nomina.empleado.nombre,
                    "categoria": "Nómina",
                    "proveedor": "Empleado",
                    "monto": nomina.monto,
                    "fecha": nomina.fecha_vencimiento,
                    "estado": estado,
                    "objeto": nomina,
                    "dias_restantes": dias_restantes,
                })

        # ==========================================================
        # ORDENAR
        # ==========================================================

        compromisos.sort(
            key=lambda x: x["fecha"]
        )

        # ==========================================================
        # CONTEXTO
        # ==========================================================

        context["compromisos"] = compromisos
        context["tipo"] = tipo
        context["mes"] = mes
        context["anio"] = anio
        context["sucursal_id"] = sucursal_id
        context["sucursales"] = sucursales

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
    


