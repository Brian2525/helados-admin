from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import Empleado
from .forms import EmpleadoForm
from django.contrib.auth.mixins import LoginRequiredMixin


class EmpleadoListView(LoginRequiredMixin, ListView):

    model = Empleado

    template_name = "nomina/empleado_list.html"

    context_object_name = "empleados"


class EmpleadoCreateView(LoginRequiredMixin, CreateView):

    model = Empleado

    form_class = EmpleadoForm

    template_name = "nomina/empleado_form.html"

    success_url = reverse_lazy(
        "nomina:empleado_list"
    )


class EmpleadoUpdateView(LoginRequiredMixin, UpdateView):

    model = Empleado

    form_class = EmpleadoForm

    template_name = "nomina/empleado_form.html"

    success_url = reverse_lazy(
        "nomina:empleado_list"
    )


class EmpleadoDeleteView(LoginRequiredMixin, DeleteView):

    model = Empleado
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )

    template_name = "nomina/empleado_delete.html"

    success_url = reverse_lazy(
        "nomina:empleado_list"
    )