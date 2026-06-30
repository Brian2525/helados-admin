from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import CategoriaGasto, Gasto
from .forms import CategoriaGastoForm, GastoForm
from django.contrib.auth.mixins import LoginRequiredMixin


class CategoriaGastoListView(LoginRequiredMixin, ListView):
    model = CategoriaGasto
    template_name = "gastos/categorias/list.html"
    context_object_name = "categorias"


class CategoriaGastoCreateView(LoginRequiredMixin, CreateView):
    model = CategoriaGasto
    form_class = CategoriaGastoForm
    template_name = "gastos/categorias/form.html"
    success_url = reverse_lazy("gastos:categoria_list")


class CategoriaGastoUpdateView(LoginRequiredMixin, UpdateView):
    model = CategoriaGasto
    form_class = CategoriaGastoForm
    template_name = "gastos/categorias/form.html"
    success_url = reverse_lazy("gastos:categoria_list")


class CategoriaGastoDeleteView(LoginRequiredMixin, DeleteView):
    model = CategoriaGasto
    template_name = "gastos/categorias/delete.html"
    success_url = reverse_lazy("gastos:categoria_list")





class GastoListView(LoginRequiredMixin, ListView):
    model = Gasto
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )
    template_name = "gastos/list.html"
    context_object_name = "gastos"
    paginate_by = 20


class GastoCreateView(LoginRequiredMixin, CreateView):
    model = Gasto
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )
    form_class = GastoForm
    template_name = "gastos/form.html"
    success_url = reverse_lazy("gastos:list")


class GastoUpdateView(LoginRequiredMixin, UpdateView):
    model = Gasto
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )
   
    form_class = GastoForm
    template_name = "gastos/form.html"
    success_url = reverse_lazy("gastos:list")


class GastoDeleteView(LoginRequiredMixin, DeleteView):
    model = Gasto
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )
    template_name = "gastos/delete.html"
    success_url = reverse_lazy("gastos:list")


