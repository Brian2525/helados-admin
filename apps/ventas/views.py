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
from .services import construir_resumen_semanal


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


    def get_queryset(self):
        queryset = (
            VentaDiaria.objects
            .filter(sucursal__in=self.get_sucursales_usuario())
            .select_related("sucursal")
            .order_by("-fecha", "-id")
        )

        sucursal = self.request.GET.get("sucursal")
        fecha_inicio = self.request.GET.get("fecha_inicio")
        fecha_fin = self.request.GET.get("fecha_fin")

        if sucursal:
            queryset = queryset.filter(sucursal_id=sucursal)

        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)

        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["sucursales"] = self.get_sucursales_usuario()

        # Mantener valores seleccionados
        context["filtros"] = {
            "sucursal": self.request.GET.get("sucursal", ""),
            "fecha_inicio": self.request.GET.get("fecha_inicio", ""),
            "fecha_fin": self.request.GET.get("fecha_fin", ""),
        }

        return context











class VentaDiariaCreateView(ModulePermissionMixin,SucursalQuerysetMixin,SucursalFormMixin,LoginRequiredMixin,CreateView
):

    model = VentaDiaria
    module_permission = "ventas"
    form_class = VentaDiariaForm
    template_name = "ventas/ventas_diarias/venta_diaria_form.html"

    success_url = reverse_lazy(
        "ventas:venta_diaria_completada"
    )

    def form_valid(self, form):

        form.instance.usuario = self.request.user

        response = super().form_valid(form)

        construir_resumen_semanal(
            self.object.sucursal,
            self.object.fecha
        )

        return response
        



class VentaDiariaCompletadaView(LoginRequiredMixin,TemplateView):

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

    def form_valid(self, form):

        venta_anterior = self.get_object()

        sucursal_anterior = venta_anterior.sucursal
        fecha_anterior = venta_anterior.fecha

        response = super().form_valid(form)

        construir_resumen_semanal(
            sucursal_anterior,
            fecha_anterior
        )

        construir_resumen_semanal(
            self.object.sucursal,
            self.object.fecha
        )

        return response




class VentaDiariaDeleteView(ModulePermissionMixin,SucursalQuerysetMixin,LoginRequiredMixin, DeleteView):

    model = VentaDiaria
    module_permission = "administracion"
    template_name = "ventas/ventas_diarias/venta_diaria_confirm_delete.html"
    success_url = reverse_lazy(
        "ventas:venta_diaria_list"
    )



    def delete(self, request, *args, **kwargs):

        venta = self.get_object()

        sucursal = venta.sucursal
        fecha = venta.fecha

        response = super().delete(request, *args, **kwargs)

        construir_resumen_semanal(
            sucursal,
            fecha
        )

        return response

