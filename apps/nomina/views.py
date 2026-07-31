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

from .models import Empleado, PagoNomina
from .forms import EmpleadoForm, PagoNominaForm
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin,SucursalPermissionMixin


class EmpleadoListView(SucursalQuerysetMixin,LoginRequiredMixin, ListView):

    model = Empleado

    template_name = "nomina/empleado_list.html"

    context_object_name = "empleados"


class EmpleadoCreateView(SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, CreateView):

    model = Empleado

    form_class = EmpleadoForm

    template_name = "nomina/empleado_form.html"

    success_url = reverse_lazy(
        "nomina:empleado_list"
    )


class EmpleadoUpdateView(SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, UpdateView):

    model = Empleado

    form_class = EmpleadoForm

    template_name = "nomina/empleado_form.html"

    success_url = reverse_lazy(
        "nomina:empleado_list"
    )


class EmpleadoDeleteView( LoginRequiredMixin, DeleteView):

    model = Empleado
   

    template_name = "nomina/empleado_delete.html"

    success_url = reverse_lazy(
        "nomina:empleado_list"
    )


class NominaPendienteListView(SucursalQuerysetMixin, LoginRequiredMixin, ListView):

    template_name = "nomina/pendientes.html"
    context_object_name = "empleados"

    def get_queryset(self):

        hoy = timezone.now().date()
        weekday = hoy.weekday()

        empleados = Empleado.objects.filter(
            activo=True,
            sucursal__usuarios=self.request.user
        )

        pendientes = []

        for empleado in empleados:

            ultimo = empleado.pagos.order_by("-fecha_pago").first()

            if empleado.tipo_nomina == "SEMANA":

                if weekday != 4:
                    continue

            else:

                if weekday != 6:
                    continue

            if ultimo:

                dias = (hoy - ultimo.fecha_pago).days

                if dias < 7:
                    continue

            pendientes.append(empleado)

        return pendientes
    


class PagoNominaListView( LoginRequiredMixin,SucursalPermissionMixin, ListView):

    sucursal_lookup = "empleado__sucursal"

    model = PagoNomina

    template_name = "nomina/historial.html"

    context_object_name = "pagos"

    paginate_by = 20


    def get_queryset(self):
        queryset = PagoNomina.objects.select_related(
            "empleado",
            "empleado__sucursal",
        )

        return self.filtrar_por_sucursal_usuario(queryset)




@login_required
def registrar_pago(request, empleado_id):

    empleado = Empleado.objects.get(id=empleado_id)

    hoy = timezone.now().date()

    PagoNomina.objects.create(

        empleado=empleado,

        fecha_pago=hoy,

        fecha_inicio=hoy - timedelta(days=6),

        fecha_fin=hoy,

        monto=empleado.salario_periodo,

    )

    return redirect("nomina:pendientes")







class PagoNominaCreateView(SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, CreateView):

    model = PagoNomina

    form_class = PagoNominaForm

    template_name = "nomina/pago_form.html"

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