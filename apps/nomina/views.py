from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy, reverse

from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from decimal import Decimal


from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import Empleado, PagoNomina, Nomina
from .forms import EmpleadoForm, PagoNominaForm
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin,SucursalPermissionMixin,ModulePermissionMixin


class EmpleadoListView(ModulePermissionMixin,SucursalQuerysetMixin,LoginRequiredMixin, ListView):

    model = Empleado

    template_name = "nomina/empleado_list.html"

    context_object_name = "empleados"
    module_permission = "administracion"


class EmpleadoCreateView( SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, CreateView):

    model = Empleado

    form_class = EmpleadoForm

    template_name = "nomina/empleado_form.html"

    success_url = reverse_lazy(
        "nomina:empleado_list"
    )


class EmpleadoUpdateView(ModulePermissionMixin, SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, UpdateView):

    model = Empleado
    form_class = EmpleadoForm
    template_name = "nomina/empleado_form.html"
    module_permission = "administracion"
    success_url = reverse_lazy(
        "nomina:empleado_list"
    )


class EmpleadoDeleteView(ModulePermissionMixin, LoginRequiredMixin, DeleteView):

    model = Empleado
    module_permission = "administracion"
    template_name = "nomina/empleado_delete.html"
    success_url = reverse_lazy(
        "nomina:empleado_list"
    )




class NominaPendienteListView(SucursalQuerysetMixin,LoginRequiredMixin,ListView):
    template_name = "nomina/pendientes.html"
    context_object_name = "empleados"
    module_permission = "administracion"

    def get_queryset(self):

        hoy = timezone.now().date()
        weekday = hoy.weekday()

        empleados = Empleado.objects.filter(
            activo=True,
            sucursal__usuarios=self.request.user
        )

        pendientes = []

        for empleado in empleados:

            # =====================================
            # NÓMINA SEMANAL
            # LUNES -> VIERNES
            # =====================================

            if empleado.tipo_nomina == "SEMANA":

                lunes_actual = hoy - timedelta(days=weekday)
                viernes_actual = lunes_actual + timedelta(days=4)

                # ---------------------------------
                # Buscar si existe un pago de esta
                # semana
                # ---------------------------------

                pago_actual = PagoNomina.objects.filter(
                    empleado=empleado,
                    fecha_inicio=lunes_actual,
                    fecha_fin=viernes_actual,
                ).first()

                if pago_actual:
                    continue

                fecha_inicio = lunes_actual
                fecha_fin = viernes_actual
                fecha_pago = viernes_actual

            # =====================================
            # NÓMINA FIN DE SEMANA
            # SÁBADO -> DOMINGO
            # =====================================

            else:

                if weekday == 5:
                    # Sábado

                    fecha_inicio = hoy
                    fecha_fin = hoy + timedelta(days=1)

                elif weekday == 6:
                    # Domingo

                    fecha_inicio = hoy - timedelta(days=1)
                    fecha_fin = hoy

                else:
                    # Lunes -> viernes
                    # Buscar el próximo sábado

                    dias_hasta_sabado = 5 - weekday

                    fecha_inicio = hoy + timedelta(
                        days=dias_hasta_sabado
                    )

                    fecha_fin = fecha_inicio + timedelta(days=1)

                fecha_pago = fecha_fin

                # ---------------------------------
                # Buscar si existe un pago de este
                # periodo
                # ---------------------------------

                pago_actual = PagoNomina.objects.filter(
                    empleado=empleado,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                ).first()

                if pago_actual:
                    continue

            # =====================================
            # DETERMINAR ESTADO
            # =====================================

            dias = (fecha_pago - hoy).days

            if dias < 0:
                estado = "vencido"

            elif dias == 0:
                estado = "pendiente"

            elif dias <= 3:
                estado = "proximo"

            else:
                continue

            # Guardamos información adicional
            # para utilizarla en el template

            empleado.estado_nomina = estado
            empleado.fecha_inicio_nomina = fecha_inicio
            empleado.fecha_fin_nomina = fecha_fin
            empleado.fecha_pago_nomina = fecha_pago

            pendientes.append(empleado)

        return pendientes




    

class PagoNominaListView(ModulePermissionMixin, LoginRequiredMixin,SucursalPermissionMixin, ListView):

    module_permission = "administracion"
    model = Nomina
    template_name = "nomina/historial.html"
    context_object_name = "pagos"
    paginate_by = 20






@login_required
def registrar_pago(request, empleado_id):

    empleado = get_object_or_404(
        Empleado,
        id=empleado_id
    )

    hoy = timezone.now().date()
    weekday = hoy.weekday()

    # =====================================
    # NÓMINA SEMANAL
    # LUNES -> VIERNES
    # =====================================

    if empleado.tipo_nomina == "SEMANA":

        lunes = hoy - timedelta(days=weekday)
        viernes = lunes + timedelta(days=4)

        fecha_inicio = lunes
        fecha_fin = viernes

    # =====================================
    # NÓMINA FIN DE SEMANA
    # SÁBADO -> DOMINGO
    # =====================================

    else:

        if weekday == 5:
            # Sábado

            fecha_inicio = hoy
            fecha_fin = hoy + timedelta(days=1)

        elif weekday == 6:
            # Domingo

            fecha_inicio = hoy - timedelta(days=1)
            fecha_fin = hoy

        else:
            # Lunes -> viernes

            dias_hasta_sabado = 5 - weekday

            fecha_inicio = hoy + timedelta(
                days=dias_hasta_sabado
            )

            fecha_fin = fecha_inicio + timedelta(days=1)

    # =====================================
    # EVITAR DUPLICADOS
    # =====================================

    pago_existente = PagoNomina.objects.filter(
        empleado=empleado,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    ).exists()

    if pago_existente:
        return redirect("nomina:pendientes")

    # =====================================
    # REGISTRAR PAGO
    # =====================================

    PagoNomina.objects.create(
        empleado=empleado,
        fecha_pago=hoy,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        monto=empleado.salario_periodo,
    )

    return redirect("nomina:pendientes")






class PagoNominaCreateView(ModulePermissionMixin, SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, CreateView):

    model = PagoNomina
    form_class = PagoNominaForm
    template_name = "nomina/pago_form.html"
    module_permission = "administracion"

    def dispatch(self, request, *args, **kwargs):

        self.empleado = get_object_or_404(
            Empleado,
            pk=self.kwargs["empleado_id"],
        )

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):

        hoy = timezone.now().date()

        return {
            "fecha_pago": hoy,
            "fecha_inicio": hoy - timedelta(days=6),
            "fecha_fin": hoy,
            "monto": self.empleado.salario_periodo,
        }

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["empleado"] = self.empleado

        return context

    def form_valid(self, form):

        form.instance.empleado = self.empleado

        return super().form_valid(form)

    def get_success_url(self):

        return reverse("servicios:list")