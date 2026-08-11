from django.shortcuts import render, reverse, redirect 
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView
)
from django.views import View
from dateutil.relativedelta import relativedelta
from decimal import Decimal




from .models import Proveedor, CuentaPorPagar, PagoCuentaPorPagar, ProgramacionPago
from .forms import ProveedorForm,CuentaPorPagarForm, PagoCuentaForm, ProgramacionPagoForm
from django.db.models import Q
from django.utils import timezone
from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin,SucursalPermissionMixin,PropietarioQuerysetMixin, ModulePermissionMixin


class ProveedorListView(ModulePermissionMixin, PropietarioQuerysetMixin,LoginRequiredMixin, ListView):

    model = Proveedor

    template_name = "compras/proveedor_list.html"

    context_object_name = "proveedores"

    paginate_by = 20

    ordering = ["nombre"]
    module_permission = "finanzas"      





class ProveedorCreateView(ModulePermissionMixin, LoginRequiredMixin, CreateView):

    model = Proveedor
    template_name = "compras/proveedor_form.html"
    form_class = ProveedorForm
    success_url = reverse_lazy("compras:proveedor_list")
    module_permission = "finanzas"

    def form_valid(self, form):
        form.instance.propietario = self.request.user
        return super().form_valid(form)


class ProveedorUpdateView(ModulePermissionMixin, LoginRequiredMixin, UpdateView):

    model = Proveedor
    template_name = "compras/proveedor_form.html"
    form_class = ProveedorForm
    module_permission = "finanzas"
    success_url = reverse_lazy("compras:proveedor_list")


class ProveedorDeleteView( LoginRequiredMixin, DeleteView):

    model = Proveedor
    module_permission = "finanzas"
    template_name = "compras/proveedor_confirm_delete.html"

    success_url = reverse_lazy("compras:proveedor_list")


class CuentaPorPagarListView(ModulePermissionMixin,SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, ListView):

    model = CuentaPorPagar
    module_permission = "finanzas"
    template_name = "compras/cuenta_list.html"
    context_object_name = "cuentas"
    paginate_by = 20

    def get_queryset(self):

        queryset = super().get_queryset()


        q = self.request.GET.get("q")
       
       
       
        estado = self.request.GET.get("estado", "abiertas")

        cuentas = list(queryset)

        if estado == "pagadas":
            cuentas = [c for c in cuentas if c.estatus == "pagado"]

        elif estado == "pendientes":
            cuentas = [c for c in cuentas if c.estatus == "pendiente"]

        elif estado == "parciales":
            cuentas = [c for c in cuentas if c.estatus == "parcial"]

        elif estado == "vencidas":
            cuentas = [c for c in cuentas if c.estatus == "vencido"]

        else:
            cuentas = [
                c for c in cuentas
                if c.estatus in ("pendiente", "parcial", "vencido")
            ]

        return cuentas
    





class CuentaPorPagarCreateView(ModulePermissionMixin, SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, CreateView):

    model = CuentaPorPagar
    form_class = CuentaPorPagarForm
    template_name = "compras/cuenta_form.html"
    module_permission = "finanzas"

    def form_valid(self, form):

        response = super().form_valid(form)

        meses = form.cleaned_data.get("meses")

        if meses and meses > 1:

            ProgramacionPago.objects.filter(
                cuenta=self.object
            ).delete()

            monto = (
                self.object.monto_total / Decimal(meses)
            ).quantize(Decimal("0.01"))

            fecha = self.object.fecha_vencimiento

            for i in range(meses):

                # El último pago absorbe la diferencia por redondeo
                if i == meses - 1:
                    monto_pago = self.object.monto_total - (
                        monto * (meses - 1)
                    )
                else:
                    monto_pago = monto

                ProgramacionPago.objects.create(
                    cuenta=self.object,
                    numero=i + 1,
                    fecha_vencimiento=fecha,
                    monto=monto_pago,
                )

                fecha += relativedelta(months=1)

        return response

    def get_success_url(self):
        return reverse(
            "compras:cuenta_detail",
            kwargs={"pk": self.object.pk}
        )
    

class CuentaPorPagarUpdateView(ModulePermissionMixin, SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, UpdateView):

    model = CuentaPorPagar
    module_permission = "finanzas"
    form_class = CuentaPorPagarForm
    template_name = "compras/cuenta_form.html"

    success_url = reverse_lazy(
        "compras:cuenta_list"
    )






class RegistrarPagoCuentaView(ModulePermissionMixin, SucursalQuerysetMixin, SucursalFormMixin,LoginRequiredMixin,CreateView):

    model = PagoCuentaPorPagar
    module_permission = "finanzas"


    form_class = PagoCuentaForm

    template_name = "compras/pago_form.html"

    def dispatch(self, request, *args, **kwargs):

        self.cuenta = get_object_or_404(
            CuentaPorPagar,
            pk=self.kwargs["pk"]
        )

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        form.instance.cuenta = self.cuenta

        return super().form_valid(form)


class CuentaPorPagarDeleteView(ModulePermissionMixin, SucursalQuerysetMixin, LoginRequiredMixin, DeleteView):

    model = CuentaPorPagar
    module_permission = "finanzas"


    template_name = "compras/cuenta_confirm_delete.html"

    success_url = reverse_lazy(
        "compras:cuenta_list"
    )







class CuentaPorPagarDetailView(ModulePermissionMixin, SucursalQuerysetMixin,LoginRequiredMixin, DetailView):

    model = CuentaPorPagar
    module_permission = "finanzas"


    template_name = "compras/cuenta_detail.html"

    context_object_name = "cuenta"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        
        context["today"] = date.today()

        context["pagos"] = self.object.pagos.all()

        context["programacion_form"] = ProgramacionPagoForm()

        return context
    






class RegistrarPagoCuentaView(ModulePermissionMixin,SucursalQuerysetMixin,LoginRequiredMixin, CreateView):
    model = PagoCuentaPorPagar
    module_permission = "finanzas"

    form_class = PagoCuentaForm
    template_name = "compras/pago_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.cuenta = get_object_or_404(
            CuentaPorPagar,
            pk=self.kwargs["pk"]
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.cuenta = self.cuenta
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "compras:cuenta_detail",
            kwargs={"pk": self.cuenta.pk}
        )
    

class ProgramarPagosView(ModulePermissionMixin,SucursalQuerysetMixin,LoginRequiredMixin, View):

    def post(self, request, pk):

        cuenta = get_object_or_404(
            CuentaPorPagar,
            pk=pk
        )

        form = ProgramacionPagoForm(request.POST)

        if form.is_valid():

            meses = form.cleaned_data["meses"]

            ProgramacionPago.objects.filter(
                cuenta=cuenta
            ).delete()

            monto = (
                cuenta.monto_total / Decimal(meses)
            ).quantize(Decimal("0.01"))

            acumulado = Decimal("0.00")
            fecha = cuenta.fecha_vencimiento

            for i in range(meses):

                if i == meses - 1:
                    monto_pago = cuenta.monto_total - acumulado
                else:
                    monto_pago = monto
                    acumulado += monto

                ProgramacionPago.objects.create(
                    cuenta=cuenta,
                    numero=i + 1,
                    fecha_vencimiento=fecha,
                    monto=monto_pago,
                )

                fecha += relativedelta(months=1)

        return redirect(
            "compras:cuenta_detail",
            pk=cuenta.pk
        )