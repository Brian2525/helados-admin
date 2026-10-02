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
from django.urls import reverse
from django.views import View

from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404


from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin,ModulePermissionMixin, SucursalPermissionMixin, SucursalActivaMixin

@method_decorator(login_required, name="dispatch")
class SucursalListView(ModulePermissionMixin,SucursalPermissionMixin, LoginRequiredMixin, ListView):
    model = Sucursal
    template_name = "sucursales/list.html"
    context_object_name = "sucursales"
    module_permission = "administracion"



class SucursalCreateView(ModulePermissionMixin,LoginRequiredMixin, CreateView):
    model = Sucursal
    form_class = SucursalForm
    template_name = "sucursales/form.html"
    success_url = reverse_lazy("sucursales:list")
    module_permission = "administracion"


    def form_valid(self, form):
        form.instance.propietario = self.request.user

        if Sucursal.objects.filter(
            propietario=self.request.user,
            nombre=form.instance.nombre,
        ).exists():
            form.add_error(
                "nombre",
                "Ya tienes una sucursal con ese nombre."
            )
            return self.form_invalid(form)

        return super().form_valid(form)
        
    



class SucursalUpdateView(ModulePermissionMixin, SucursalFormMixin, LoginRequiredMixin, UpdateView):
    model = Sucursal
    form_class = SucursalForm
    template_name = "sucursales/form.html"
    success_url = reverse_lazy("sucursales:list")
    module_permission = "administracion"



class SucursalDeleteView(ModulePermissionMixin, LoginRequiredMixin, DeleteView):
    model = Sucursal
    template_name = "sucursales/delete.html"
    success_url = reverse_lazy("sucursales:list")
    module_permission = "administracion"





class SeleccionarSucursalView(LoginRequiredMixin,SucursalPermissionMixin,View):

    template_name = "sucursales/seleccionar.html"

    def get(self, request):

        sucursales = (
            self.get_sucursales_usuario()
            .filter(activa=True)
            .order_by("nombre")
        )

        return render(
            request,
            self.template_name,
            {
                "sucursales": sucursales
            }
        )


    def post(self, request):

        sucursal_id = request.POST.get(
            "sucursal"
        )

        sucursal = (
            self.get_sucursales_usuario()
            .filter(
                id=sucursal_id,
                activa=True,
            )
            .first()
        )

        if not sucursal:

            messages.error(
                request,
                "La sucursal seleccionada no es válida."
            )

            return redirect(
                "sucursales:seleccionar_sucursal"
            )


        request.session[
            "sucursal_activa_id"
        ] = sucursal.id

        messages.success(
            request,
            f"Sucursal activa: {sucursal.nombre}"
        )

        return redirect(
            "ventas:pos_nueva_venta"
        )



class ConfirmarCambioSucursalView(LoginRequiredMixin,SucursalActivaMixin,SucursalPermissionMixin,View):

    template_name = (
        "sucursales/confirmar_cambio.html"
    )

    def get(self, request):

        return render(
            request,
            self.template_name,
            {
                "sucursal_activa":
                    request.sucursal_activa
            }
        )


    def post(self, request):

        request.session.pop(
            "sucursal_activa_id",
            None
        )

        return redirect(
            "sucursales:seleccionar_sucursal"
        )
