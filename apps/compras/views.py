from django.shortcuts import render, reverse 
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView
)

from .models import Proveedor, CuentaPorPagar, PagoCuentaPorPagar
from .forms import ProveedorForm,CuentaPorPagarForm, PagoCuentaForm
from django.db.models import Q


class ProveedorListView(LoginRequiredMixin, ListView):

    model = Proveedor

    template_name = "compras/proveedor_list.html"

    context_object_name = "proveedores"

    paginate_by = 20

    ordering = ["nombre"]


class ProveedorCreateView(LoginRequiredMixin, CreateView):

    model = Proveedor

    template_name = "compras/proveedor_form.html"

    form_class = ProveedorForm

    success_url = reverse_lazy("compras:proveedor_list")


class ProveedorUpdateView(LoginRequiredMixin, UpdateView):

    model = Proveedor

    template_name = "compras/proveedor_form.html"
    
    form_class = ProveedorForm

    success_url = reverse_lazy("compras:proveedor_list")


class ProveedorDeleteView(LoginRequiredMixin, DeleteView):

    model = Proveedor

    template_name = "compras/proveedor_confirm_delete.html"

    success_url = reverse_lazy("compras:proveedor_list")



class CuentaPorPagarListView(LoginRequiredMixin,ListView):

    model = CuentaPorPagar

    template_name = "compras/cuenta_list.html"

    context_object_name = "cuentas"

    paginate_by = 20

    def get_queryset(self):

        queryset = super().get_queryset()

        if not self.request.user.is_superuser:

            queryset = queryset.filter(
                sucursal__usuarios=self.request.user
            )

        q = self.request.GET.get("q")

        if q:

            queryset = queryset.filter(

            Q(proveedor__nombre__icontains=q) |
            Q(descripcion__icontains=q)

    )

        return queryset.select_related(
            "proveedor",
            "categoria",
            "sucursal"
        )


class CuentaPorPagarCreateView(LoginRequiredMixin,CreateView):

    model = CuentaPorPagar

    form_class = CuentaPorPagarForm

    template_name = "compras/cuenta_form.html"

    success_url = reverse_lazy(
        "compras:cuenta_list"
    )

    







class RegistrarPagoCuentaView(
    LoginRequiredMixin,
    CreateView
):

    model = PagoCuentaPorPagar

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


class CuentaPorPagarDeleteView(LoginRequiredMixin,DeleteView):

    model = CuentaPorPagar

    template_name = "compras/cuenta_confirm_delete.html"

    success_url = reverse_lazy(
        "compras:cuenta_list"
    )


class CuentaPorPagarDetailView(LoginRequiredMixin, DetailView):
    model = CuentaPorPagar
    template_name = "compras/cuenta_detail.html"
    context_object_name = "cuenta"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["pagos"] = (
            PagoCuentaPorPagar.objects
            .filter(cuenta=self.object)
            .order_by("-fecha")
        )

        return context
    

class RegistrarPagoCuentaView(LoginRequiredMixin, CreateView):
    model = PagoCuentaPorPagar
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