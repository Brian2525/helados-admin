from django.urls import reverse_lazy
from django.db.models import Q
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
    template_name = "sucursales/list.html"
    context_object_name = "sucursales"

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            Q(propietario=self.request.user) |
            Q(usuarios=self.request.user)
        ).distinct()


class SucursalCreateView(LoginRequiredMixin, CreateView):
    model = Sucursal
    form_class = SucursalForm
    template_name = "sucursales/form.html"
    success_url = reverse_lazy("sucursales:list")

    def form_valid(self, form):
        # El usuario que crea la sucursal será el propietario
        form.instance.propietario = self.request.user

        response = super().form_valid(form)

        # El propietario también queda asignado a la sucursal
        self.object.usuarios.add(self.request.user)

        return response


class SucursalUpdateView(LoginRequiredMixin, UpdateView):
    model = Sucursal
    form_class = SucursalForm
    template_name = "sucursales/form.html"
    success_url = reverse_lazy("sucursales:list")

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            propietario=self.request.user
        )


class SucursalDeleteView(LoginRequiredMixin, DeleteView):
    model = Sucursal
    template_name = "sucursales/delete.html"
    success_url = reverse_lazy("sucursales:list")

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            propietario=self.request.user
        )