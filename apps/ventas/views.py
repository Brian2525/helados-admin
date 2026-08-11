from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import ResumenSemanal, VentaDiaria
from .forms import ResumenSemanalForm, VentaDiariaForm
from apps.sucursales.models import Sucursal
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin,ModulePermissionMixin


class ResumenSemanalListView(ModulePermissionMixin,SucursalQuerysetMixin, LoginRequiredMixin,ListView ):
    model = ResumenSemanal
    module_permission = "ventas"
    template_name = "ventas/list.html"
    context_object_name = "ventas:resumenes"


class ResumenSemanalCreateView(ModulePermissionMixin,SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, CreateView):
    model = ResumenSemanal
    module_permission = "ventas"
    form_class = ResumenSemanalForm
    template_name = "ventas/create.html"
    success_url = reverse_lazy("ventas:resumen_list")


class ResumenSemanalUpdateView(ModulePermissionMixin,SucursalQuerysetMixin,  SucursalFormMixin, LoginRequiredMixin, UpdateView):
    model = ResumenSemanal
    module_permission = "ventas"
    form_class = ResumenSemanalForm
    template_name = "ventas/update.html"
    success_url = reverse_lazy("ventas:resumen_list")


class ResumenSemanalDeleteView(ModulePermissionMixin,SucursalQuerysetMixin, LoginRequiredMixin, DeleteView):
    model = ResumenSemanal
    module_permission = "ventas"
    template_name = "ventas/delete.html"
    success_url = reverse_lazy("ventas:resumen_list")



class VentaDiariaListView(ModulePermissionMixin,SucursalQuerysetMixin,LoginRequiredMixin, ListView):

    model = VentaDiaria
    module_permission = "ventas"
    template_name = "ventas/ventas_diarias/venta_diaria_list.html"
    context_object_name = "ventas"
    paginate_by = 30



class VentaDiariaCreateView(ModulePermissionMixin,SucursalQuerysetMixin,SucursalFormMixin, LoginRequiredMixin, CreateView):


    model = VentaDiaria
    module_permission = "ventas"
    form_class = VentaDiariaForm
    template_name = "ventas/ventas_diarias/venta_diaria_form.html"
    success_url = reverse_lazy(
        "ventas:venta_diaria_list"
    )

    def form_valid(self, form):

        # Asigna el usuario que registró la venta
        form.instance.usuario = self.request.user

        return super().form_valid(form)


class VentaDiariaUpdateView(ModulePermissionMixin,SucursalQuerysetMixin,SucursalFormMixin, LoginRequiredMixin, UpdateView):

    model = VentaDiaria
    module_permission = "ventas"
    form_class = VentaDiariaForm
    template_name = "ventas/ventas_diarias/venta_diaria_form.html"
    success_url = reverse_lazy(
        "ventas:venta_diaria_list"
    )




class VentaDiariaDeleteView(ModulePermissionMixin,SucursalQuerysetMixin,LoginRequiredMixin, DeleteView):

    model = VentaDiaria
    module_permission = "ventas"
    template_name = "ventas/venta_diaria/venta_diaria_confirm_delete.html"
    success_url = reverse_lazy(
        "ventas:venta_diaria_list"
    )

