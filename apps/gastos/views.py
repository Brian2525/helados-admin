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
from django.db.models import Sum
from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin,ModulePermissionMixin

class CategoriaGastoListView(ModulePermissionMixin, SucursalQuerysetMixin, LoginRequiredMixin, ListView):
    model = CategoriaGasto
    template_name = "gastos/categorias/list.html"
    context_object_name = "categorias"
    module_permission = "finanzas"


class CategoriaGastoCreateView(ModulePermissionMixin, SucursalQuerysetMixin ,  SucursalFormMixin, LoginRequiredMixin, CreateView):
    model = CategoriaGasto
    form_class = CategoriaGastoForm
    template_name = "gastos/categorias/form.html"
    success_url = reverse_lazy("gastos:categoria_list")
    module_permission = "finanzas"




class CategoriaGastoUpdateView(ModulePermissionMixin, SucursalFormMixin, LoginRequiredMixin, UpdateView,SucursalQuerysetMixin):
    model = CategoriaGasto
    form_class = CategoriaGastoForm
    template_name = "gastos/categorias/form.html"
    success_url = reverse_lazy("gastos:categoria_list")
    module_permission = "finanzas"

class CategoriaGastoDeleteView(ModulePermissionMixin, SucursalQuerysetMixin, LoginRequiredMixin, DeleteView):
    model = CategoriaGasto
    template_name = "gastos/categorias/delete.html"
    success_url = reverse_lazy("gastos:categoria_list")
    module_permission = "finanzas"




class GastoListView(ModulePermissionMixin, SucursalQuerysetMixin, LoginRequiredMixin, ListView):
    model = Gasto
    template_name = "gastos/list.html"
    context_object_name = "gastos"
    paginate_by = 20
    module_permission = "finanzas"

    def get_queryset(self):
        queryset = super().get_queryset()

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
        # Categorías disponibles 
        context["categorias"] = CategoriaGasto.objects.all() 
        # Total de todos los gastos que cumplen los filtros 
        total_gastos = self.get_queryset().aggregate( 
            total=Sum("monto") 
            )["total"] or 0 
        context["total_gastos"] = total_gastos 

        return context


class GastoCreateView(ModulePermissionMixin, SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, CreateView):
    model = Gasto
    form_class = GastoForm
    template_name = "gastos/form.html"
    success_url = reverse_lazy("gastos:list")
    module_permission = "ventas"

class GastoUpdateView(SucursalQuerysetMixin, LoginRequiredMixin, UpdateView):
    model = Gasto
    form_class = GastoForm
    template_name = "gastos/form.html"
    success_url = reverse_lazy("gastos:list")
    module_permission = "finanzas"


class GastoDeleteView(ModulePermissionMixin,SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, DeleteView):
    model = Gasto
    template_name = "gastos/delete.html"
    success_url = reverse_lazy("gastos:list")
    module_permission = "finanzas"

  

