from django.shortcuts import render
from django.contrib import messages


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
from apps.gastos.models import CategoriaGasto, Gasto
from django.db import transaction
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
    model = Nomina
    context_object_name = "nominas"
    module_permission = "administracion"

    def get_queryset(self):
        return (
            Nomina.objects
            .filter(
                empleado__activo=True,
                estado="pendiente")
            .select_related(
                "empleado",
                "empleado__sucursal",
            )
            .order_by("fecha_vencimiento")
        )




    

class PagoNominaListView(ModulePermissionMixin, LoginRequiredMixin,SucursalPermissionMixin, ListView):

    module_permission = "administracion"
    model = Nomina
    template_name = "nomina/historial.html"
    context_object_name = "pagos"
    paginate_by = 20

    sucursal_lookup = "empleado__sucursal"

    def get_queryset(self):
        return (
            Nomina.objects
            .filter(
                empleado__activo=True,
                estado="pendiente"
            )
            .select_related(
                "empleado",
                "empleado__sucursal",
            )
            .order_by("fecha_vencimiento")
        )





@login_required
@transaction.atomic
def registrar_pago(request, nomina_id):

    nomina = get_object_or_404(
        Nomina.objects.select_related(
            "empleado",
            "empleado__sucursal",
        ),
        id=nomina_id,
        empleado__activo=True,
        empleado__sucursal__usuarios=request.user,
    )

    # Evitar pagar dos veces
    if nomina.estado == "pagada":
        messages.warning(
            request,
            "Esta nómina ya fue pagada."
        )
        return redirect("nomina:pendientes")

    # Buscar categoría Nómina
    categoria_nomina = get_object_or_404(
        CategoriaGasto,
        nombre__iexact="nómina",
        activa=True,
    )

    hoy = timezone.now().date()

    # ==========================================
    # 1. CREAR PAGO DE NÓMINA
    # ==========================================

    pago = PagoNomina.objects.create(
        nomina=nomina,
        fecha_pago=hoy,
        monto=nomina.monto,
    )

    # ==========================================
    # 2. CREAR GASTO
    # ==========================================

    Gasto.objects.create(
        sucursal=nomina.empleado.sucursal,
        fecha=hoy,
        categoria=categoria_nomina,
        descripcion=(
            f"Nómina de {nomina.empleado.nombre} "
            f"({nomina.fecha_inicio} - {nomina.fecha_fin})"
        ),
        monto=pago.monto,
        pago_nomina=pago,
    )

    # ==========================================
    # 3. MARCAR NÓMINA COMO PAGADA
    # ==========================================

    nomina.estado = "pagada"
    nomina.save(update_fields=["estado"])

    messages.success(
        request,
        f"Nómina de {nomina.empleado.nombre} "
        f"pagada correctamente."
    )

    return redirect("nomina:pendientes")



class PagoNominaCreateView(ModulePermissionMixin,LoginRequiredMixin,CreateView):

    model = PagoNomina
    form_class = PagoNominaForm
    template_name = "nomina/pago_form.html"
    module_permission = "administracion"

    def dispatch(self, request, *args, **kwargs):

        self.nomina = get_object_or_404(
            Nomina.objects.select_related(
                "empleado",
                "empleado__sucursal",
            ),
            pk=self.kwargs["nomina_id"],
            empleado__activo=True,
        )

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {
            "fecha_pago": timezone.now().date(),
            "monto": self.nomina.monto,
        }

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["nomina"] = self.nomina
        context["empleado"] = self.nomina.empleado

        return context

    @transaction.atomic
    def form_valid(self, form):

        # Verificar que todavía no exista un pago
        if PagoNomina.objects.filter(
            nomina=self.nomina
        ).exists():

            messages.warning(
                self.request,
                "Esta nómina ya tiene un pago registrado."
            )

            return redirect("nomina:pendientes")

        # ==========================================
        # 1. CREAR PAGO
        # ==========================================

        form.instance.nomina = self.nomina

        pago = form.save()

        # ==========================================
        # 2. CREAR GASTO
        # ==========================================

        categoria_nomina = get_object_or_404(
            CategoriaGasto,
            nombre__iexact="nómina",
            activa=True,
        )

        Gasto.objects.create(
            sucursal=self.nomina.empleado.sucursal,
            fecha=pago.fecha_pago,
            categoria=categoria_nomina,
            descripcion=(
                f"Nómina de {self.nomina.empleado.nombre} "
                f"({self.nomina.fecha_inicio} - "
                f"{self.nomina.fecha_fin})"
            ),
            monto=pago.monto,
            pago_nomina=pago,
        )

        # ==========================================
        # 3. MARCAR COMO PAGADA
        # ==========================================

        self.nomina.estado = "pagada"
        self.nomina.save(update_fields=["estado"])

        messages.success(
            self.request,
            f"Nómina de {self.nomina.empleado.nombre} "
            "pagada correctamente."
        )

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("nomina:pendientes")