from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import Sucursal
from .forms import SucursalForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name="dispatch")
class SucursalListView(ListView):
    model = Sucursal
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )
    template_name = "sucursales/list.html"
    context_object_name = "sucursales"


class SucursalCreateView(LoginRequiredMixin, CreateView):
    model = Sucursal
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )
    form_class = SucursalForm
    template_name = "sucursales/form.html"
    success_url = reverse_lazy("sucursales:list")


class SucursalUpdateView(LoginRequiredMixin, UpdateView):
    model = Sucursal
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )
    form_class = SucursalForm
    template_name = "sucursales/form.html"
    success_url = reverse_lazy("sucursales:list")


class SucursalDeleteView(LoginRequiredMixin, DeleteView):
    model = Sucursal
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )
    template_name = "sucursales/delete.html"
    success_url = reverse_lazy("sucursales:list")
# Create your views here.
