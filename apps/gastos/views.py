from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import CategoriaGasto, Gasto
from .forms import CategoriaGastoForm, GastoForm


class CategoriaGastoListView(ListView):
    model = CategoriaGasto
    template_name = "gastos/categorias/list.html"
    context_object_name = "categorias"


class CategoriaGastoCreateView(CreateView):
    model = CategoriaGasto
    form_class = CategoriaGastoForm
    template_name = "gastos/categorias/form.html"
    success_url = reverse_lazy("gastos:categoria_list")


class CategoriaGastoUpdateView(UpdateView):
    model = CategoriaGasto
    form_class = CategoriaGastoForm
    template_name = "gastos/categorias/form.html"
    success_url = reverse_lazy("gastos:categoria_list")


class CategoriaGastoDeleteView(DeleteView):
    model = CategoriaGasto
    template_name = "gastos/categorias/delete.html"
    success_url = reverse_lazy("gastos:categoria_list")





class GastoListView(ListView):
    model = Gasto
    template_name = "gastos/list.html"
    context_object_name = "gastos"
    paginate_by = 20


class GastoCreateView(CreateView):
    model = Gasto
    form_class = GastoForm
    template_name = "gastos/form.html"
    success_url = reverse_lazy("gastos:list")


class GastoUpdateView(UpdateView):
    model = Gasto
    form_class = GastoForm
    template_name = "gastos/form.html"
    success_url = reverse_lazy("gastos:list")


class GastoDeleteView(DeleteView):
    model = Gasto
    template_name = "gastos/delete.html"
    success_url = reverse_lazy("gastos:list")


