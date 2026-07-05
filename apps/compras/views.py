from django.shortcuts import render

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import Proveedor
from .forms import ProveedorForm


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