from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    )

from .models import ResumenSemanal, VentaDiaria
from .forms import ResumenSemanalForm, VentaDiariaForm
from apps.sucursales.models import Sucursal
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin,ModulePermissionMixin


class ResumenSemanalListView(ModulePermissionMixin,SucursalQuerysetMixin, LoginRequiredMixin,ListView ):
    model = ResumenSemanal
    module_permission = "administracion"
    template_name = "ventas/list.html"
    context_object_name = "ventas:resumenes"


class ResumenSemanalCreateView(ModulePermissionMixin,SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, CreateView):
    model = ResumenSemanal
    module_permission = "administracion"
    form_class = ResumenSemanalForm
    template_name = "ventas/create.html"
    success_url = reverse_lazy("ventas:resumen_list")


class ResumenSemanalUpdateView(ModulePermissionMixin,SucursalQuerysetMixin,  SucursalFormMixin, LoginRequiredMixin, UpdateView):
    model = ResumenSemanal
    module_permission = "administracion"
    form_class = ResumenSemanalForm
    template_name = "ventas/update.html"
    success_url = reverse_lazy("ventas:resumen_list")


class ResumenSemanalDeleteView(ModulePermissionMixin,SucursalQuerysetMixin, LoginRequiredMixin, DeleteView):
    model = ResumenSemanal
    module_permission = "administracion"
    template_name = "ventas/delete.html"
    success_url = reverse_lazy("ventas:resumen_list")









class VentaDiariaListView(ModulePermissionMixin,SucursalQuerysetMixin,LoginRequiredMixin, ListView):

    model = VentaDiaria
    module_permission = "administracion"
    template_name = "ventas/ventas_diarias/venta_diaria_list.html"
    context_object_name = "ventas"
    paginate_by = 30



class VentaDiariaCreateView(
    ModulePermissionMixin,
    SucursalQuerysetMixin,
    SucursalFormMixin,
    LoginRequiredMixin,
    CreateView
):

    model = VentaDiaria
    module_permission = "ventas"
    form_class = VentaDiariaForm
    template_name = "ventas/ventas_diarias/venta_diaria_form.html"

    success_url = reverse_lazy(
        "ventas:venta_diaria_completada"
    )

    def form_valid(self, form):

        print("FORMULARIO VÁLIDO")

        form.instance.usuario = self.request.user

        response = super().form_valid(form)

        print("VENTA GUARDADA:", self.object.pk)

        return response

    def form_invalid(self, form):

        print("FORMULARIO INVÁLIDO")
        print(form.errors)

        return super().form_invalid(form)



class VentaDiariaCompletadaView(
    LoginRequiredMixin,
    TemplateView
):

    template_name = "ventas/ventas_diarias/venta_diaria_completada.html"

    def get_context_data(self, **kwargs):

        print("ENTRÉ A VENTA DIARIA COMPLETADA")

        context = super().get_context_data(**kwargs)

        context["nombre_usuario"] = (
            self.request.user.get_full_name()
            or self.request.user.username
        )

        return context





class VentaDiariaUpdateView(ModulePermissionMixin,SucursalQuerysetMixin,SucursalFormMixin, LoginRequiredMixin, UpdateView):

    model = VentaDiaria
    module_permission = "administracion"
    form_class = VentaDiariaForm
    template_name = "ventas/ventas_diarias/venta_diaria_form.html"
    success_url = reverse_lazy(
        "ventas:venta_diaria_list"
    )




class VentaDiariaDeleteView(ModulePermissionMixin,SucursalQuerysetMixin,LoginRequiredMixin, DeleteView):

    model = VentaDiaria
    module_permission = "administracion"
    template_name = "ventas/ventas_diarias/venta_diaria_confirm_delete.html"
    success_url = reverse_lazy(
        "ventas:venta_diaria_list"
    )

