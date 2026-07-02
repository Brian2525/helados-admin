from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.shortcuts import redirect
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

from .models import Empleado
from .models import PagoNomina
from .forms import EmpleadoForm
from django.contrib.auth.mixins import LoginRequiredMixin


class EmpleadoListView(LoginRequiredMixin, ListView):

    model = Empleado

    template_name = "nomina/empleado_list.html"

    context_object_name = "empleados"


class EmpleadoCreateView(LoginRequiredMixin, CreateView):

    model = Empleado

    form_class = EmpleadoForm

    template_name = "nomina/empleado_form.html"

    success_url = reverse_lazy(
        "nomina:empleado_list"
    )


class EmpleadoUpdateView(LoginRequiredMixin, UpdateView):

    model = Empleado

    form_class = EmpleadoForm

    template_name = "nomina/empleado_form.html"

    success_url = reverse_lazy(
        "nomina:empleado_list"
    )


class EmpleadoDeleteView(LoginRequiredMixin, DeleteView):

    model = Empleado
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )

    template_name = "nomina/empleado_delete.html"

    success_url = reverse_lazy(
        "nomina:empleado_list"
    )


class NominaPendienteListView(LoginRequiredMixin, ListView):

    template_name = "nomina/pendientes.html"
    context_object_name = "empleados"

    def get_queryset(self):

        hoy = timezone.now().date()
        weekday = hoy.weekday()

        empleados = Empleado.objects.filter(activo=True)

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
    


class PagoNominaListView(LoginRequiredMixin, ListView):

    model = PagoNomina

    template_name = "nomina/historial.html"

    context_object_name = "pagos"

    paginate_by = 20


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



@login_required
def registrar_todos(request):

    hoy = timezone.now().date()

    empleados = Empleado.objects.filter(activo=True)

    for empleado in empleados:

        ultimo = empleado.pagos.order_by("-fecha_pago").first()

        if empleado.tipo_nomina == "SEMANA":

            if hoy.weekday() != 4:
                continue

        else:

            if hoy.weekday() != 6:
                continue

        if ultimo:

            if (hoy - ultimo.fecha_pago).days < 7:
                continue

        PagoNomina.objects.create(

            empleado=empleado,

            fecha_pago=hoy,

            fecha_inicio=hoy - timedelta(days=6),

            fecha_fin=hoy,

            monto=empleado.salario_periodo,

        )

    return redirect("nomina:pendientes")