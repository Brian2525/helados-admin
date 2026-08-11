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
from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin, SucursalPermissionMixin,ModulePermissionMixin

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

