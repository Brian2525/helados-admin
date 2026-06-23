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


class EmpleadoListView(ListView):

    model = Empleado

    template_name = "nomina/empleado_list.html"

    context_object_name = "empleados"


class EmpleadoCreateView(CreateView):

    model = Empleado

    form_class = EmpleadoForm

    template_name = "nomina/empleado_form.html"

    success_url = reverse_lazy(
        "nomina:empleado_list"
    )


class EmpleadoUpdateView(UpdateView):

    model = Empleado

    form_class = EmpleadoForm

    template_name = "nomina/empleado_form.html"

    success_url = reverse_lazy(
        "nomina:empleado_list"
    )


class EmpleadoDeleteView(DeleteView):

    model = Empleado

    template_name = "nomina/empleado_delete.html"

    success_url = reverse_lazy(
        "nomina:empleado_list"
    )