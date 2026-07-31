from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .forms import ProductoForm
from .models import Producto
from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin


class ProductoListView(SucursalQuerysetMixin, LoginRequiredMixin, ListView):

    model = Producto

    template_name = "inventario/producto_list.html"

    context_object_name = "productos"

    paginate_by = 20

    def get_queryset(self):

        queryset = Producto.objects.select_related(
            "sucursal",
            "proveedor",
        )

        if not self.request.user.is_superuser:

            queryset = queryset.filter(
                sucursal__usuarios=self.request.user
            )

        return queryset


class ProductoCreateView(SucursalQuerysetMixin,SucursalFormMixin , LoginRequiredMixin, CreateView):

    model = Producto

    form_class = ProductoForm

    template_name = "inventario/producto_form.html"

    success_url = reverse_lazy(
        "inventario:producto_list"
    )

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs


class ProductoUpdateView(SucursalQuerysetMixin, SucursalFormMixin,LoginRequiredMixin, UpdateView):

    model = Producto

    form_class = ProductoForm

    template_name = "inventario/producto_form.html"

    success_url = reverse_lazy(
        "inventario:producto_list"
    )

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs


class ProductoDeleteView(SucursalQuerysetMixin,LoginRequiredMixin, DeleteView):

    model = Producto

    template_name = "inventario/producto_confirm_delete.html"

    success_url = reverse_lazy(
        "inventario:producto_list"
    )