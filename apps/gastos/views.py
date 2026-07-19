from django.urls import reverse_lazy
from django.db.models import Q
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import CategoriaGasto, Gasto
from .forms import CategoriaGastoForm, GastoForm
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.sucursales.models import Sucursal

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
    template_name = "gastos/list.html"
    context_object_name = "gastos"
    paginate_by = 20

    def get_queryset(self):

        queryset = Gasto.objects.all()

        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(sucursal__propietario=self.request.user) |
                Q(sucursal__usuarios=self.request.user)
            ).distinct()

        # Filtros
        sucursal = self.request.GET.get("sucursal")
        categoria = self.request.GET.get("categoria")
        fecha_inicio = self.request.GET.get("fecha_inicio")
        fecha_fin = self.request.GET.get("fecha_fin")

        if sucursal:
            queryset = queryset.filter(sucursal_id=sucursal)

        if categoria:
            queryset = queryset.filter(categoria_id=categoria)

        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)

        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)

        return queryset.order_by("-fecha", "-id")

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        if self.request.user.is_superuser:
            context["sucursales"] = Sucursal.objects.all()
        else:
            context["sucursales"] = Sucursal.objects.filter(
                Q(propietario=self.request.user) |
                Q(usuarios=self.request.user)
            ).distinct()

        context["categorias"] = CategoriaGasto.objects.all()

        return context


class GastoCreateView(LoginRequiredMixin, CreateView):
    model = Gasto
    form_class = GastoForm
    template_name = "gastos/form.html"
    success_url = reverse_lazy("gastos:list")


class GastoUpdateView(LoginRequiredMixin, UpdateView):
    model = Gasto
    form_class = GastoForm
    template_name = "gastos/form.html"
    success_url = reverse_lazy("gastos:list")

    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            Q(sucursal__propietario=self.request.user) |
            Q(sucursal__usuarios=self.request.user)
        ).distinct()


class GastoDeleteView(LoginRequiredMixin, DeleteView):
    model = Gasto
    template_name = "gastos/delete.html"
    success_url = reverse_lazy("gastos:list")

    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            Q(sucursal__propietario=self.request.user) |
            Q(sucursal__usuarios=self.request.user)
        ).distinct()


