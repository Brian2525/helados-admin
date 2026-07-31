from django.db.models import Q
from apps.sucursales.models import Sucursal
from apps.compras.models import Proveedor


class SucursalPermissionMixin:

    sucursal_lookup = "sucursal"

    def get_sucursales_usuario(self):
        if self.request.user.is_superuser:
            return Sucursal.objects.all()

        return (
            Sucursal.objects.filter(
                Q(propietario=self.request.user) |
                Q(usuarios=self.request.user)
            ).distinct()
        )

    def filtrar_por_sucursal_usuario(self, queryset):
        if self.request.user.is_superuser:
            return queryset

        sucursales = self.get_sucursales_usuario()

        return queryset.filter(
            **{
                f"{self.sucursal_lookup}__in": sucursales
            }
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sucursales"] = self.get_sucursales_usuario()
        return context

class SucursalQuerysetMixin(SucursalPermissionMixin):

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.is_superuser:
            return qs

        return qs.filter(
            sucursal__in=self.get_sucursales_usuario()
        )

class SucursalFormMixin(SucursalPermissionMixin):

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if "sucursal" in form.fields:
            form.fields["sucursal"].queryset = self.get_sucursales_usuario()

        if "proveedor" in form.fields:
            if self.request.user.is_superuser:
                form.fields["proveedor"].queryset = Proveedor.objects.all()
            else:
                form.fields["proveedor"].queryset = Proveedor.objects.filter(
                    propietario=self.request.user
                )

        return form



class PropietarioQuerysetMixin:
    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.is_superuser:
            return qs

        return qs.filter(
            propietario=self.request.user
        )