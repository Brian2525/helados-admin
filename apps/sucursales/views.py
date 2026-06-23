from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import Sucursal
from .forms import SucursalForm


class SucursalListView(ListView):
    model = Sucursal
    template_name = "sucursales/list.html"
    context_object_name = "sucursales"


class SucursalCreateView(CreateView):
    model = Sucursal
    form_class = SucursalForm
    template_name = "sucursales/form.html"
    success_url = reverse_lazy("sucursales:list")


class SucursalUpdateView(UpdateView):
    model = Sucursal
    form_class = SucursalForm
    template_name = "sucursales/form.html"
    success_url = reverse_lazy("sucursales:list")


class SucursalDeleteView(DeleteView):
    model = Sucursal
    template_name = "sucursales/delete.html"
    success_url = reverse_lazy("sucursales:list")
# Create your views here.
