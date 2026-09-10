from django.shortcuts import render, reverse, redirect 
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView
)
from django.views import View
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.db import transaction




from .models import Proveedor, CuentaPorPagar, PagoCuentaPorPagar, ProgramacionPago
from .queries import con_resumen_financiero
from .forms import ProveedorForm,CuentaPorPagarForm, PagoCuentaForm, ProgramacionPagoForm, FiltroCuentasPorPagarForm
from apps.gastos.models import Gasto
from .models import CategoriaGasto, Proveedor

from django.db.models import Q

from django.utils import timezone
from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin,SucursalPermissionMixin,PropietarioQuerysetMixin, ModulePermissionMixin


class ProveedorListView(ModulePermissionMixin, PropietarioQuerysetMixin,LoginRequiredMixin, ListView):

    model = Proveedor

    template_name = "compras/proveedor_list.html"

    context_object_name = "proveedores"

    paginate_by = 20

    ordering = ["nombre"]
    module_permission = "finanzas"      





class ProveedorCreateView(ModulePermissionMixin, LoginRequiredMixin, CreateView):

    model = Proveedor
    template_name = "compras/proveedor_form.html"
    form_class = ProveedorForm
    success_url = reverse_lazy("compras:proveedor_list")
    module_permission = "finanzas"

    def form_valid(self, form):
        form.instance.propietario = self.request.user
        return super().form_valid(form)


class ProveedorUpdateView(ModulePermissionMixin, LoginRequiredMixin, UpdateView):

    model = Proveedor
    template_name = "compras/proveedor_form.html"
    form_class = ProveedorForm
    module_permission = "finanzas"
    success_url = reverse_lazy("compras:proveedor_list")


class ProveedorDeleteView( LoginRequiredMixin, DeleteView):

    model = Proveedor
    module_permission = "finanzas"
    template_name = "compras/proveedor_confirm_delete.html"

    success_url = reverse_lazy("compras:proveedor_list")


class CuentaPorPagarListView(
    ModulePermissionMixin,
    SucursalQuerysetMixin,
    SucursalFormMixin,
    LoginRequiredMixin,
    ListView
):

    model = CuentaPorPagar
    module_permission = "finanzas"
    template_name = "compras/cuenta_list.html"
    context_object_name = "cuentas"
    paginate_by = 20


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["filtros_form"] = self.filtros_form

        # Si existen restricciones por empresa o usuario,
        # aplica también esos permisos a estos catálogos.
        context["categorias"] = (
            CategoriaGasto.objects.order_by("pk")
        )

        context["proveedores"] = (
            Proveedor.objects.order_by("nombre")
        )

        # URL del listado sin filtros.
        context["list_url"] = self.request.path

        # Conserva los filtros, pero elimina la página actual
        # para no generar parámetros "page" duplicados.
        parametros = self.request.GET.copy()
        parametros.pop("page", None)

        context["pagination_params"] = parametros.urlencode()

        return context 

    def get_queryset(self):
        queryset = super().get_queryset()

        # IMPORTANTE:
        # Este queryset debe estar restringido a la empresa y/o
        # sucursales que el usuario tiene permitido consultar.
        # Conserva aquí tu lógica de autorización existente.

        self.filtros_form = FiltroCuentasPorPagarForm(
            self.request.GET
        )

        if not self.filtros_form.is_valid():
            return queryset.none()

        filtros = self.filtros_form.cleaned_data

        queryset = queryset.select_related(
            "proveedor",
            "sucursal",
            "categoria",
        )

        # -------------------------
        # BÚSQUEDA
        # -------------------------

        q = filtros.get("q")

        if q:
            queryset = queryset.filter(
                Q(proveedor__nombre__icontains=q)
                | Q(descripcion__icontains=q)
            )

        # -------------------------
        # CATEGORÍA
        # -------------------------

        categoria = filtros.get("categoria")

        if categoria is not None:
            queryset = queryset.filter(
                categoria_id=categoria
            )

        # -------------------------
        # PROVEEDOR
        # -------------------------

        proveedor = filtros.get("proveedor")

        if proveedor is not None:
            queryset = queryset.filter(
                proveedor_id=proveedor
            )

        # -------------------------
        # FECHAS
        # -------------------------

        fecha_desde = filtros.get("fecha_desde")

        if fecha_desde:
            queryset = queryset.filter(
                fecha__gte=fecha_desde
            )

        fecha_hasta = filtros.get("fecha_hasta")

        if fecha_hasta:
            queryset = queryset.filter(
                fecha__lte=fecha_hasta
            )

        # -------------------------
        # RESUMEN FINANCIERO
        # -------------------------

        queryset = con_resumen_financiero(queryset)

        # -------------------------
        # ESTADO
        # -------------------------

        estado = filtros.get("estado") or "abiertas"

        equivalencias = {
            "pagadas": "pagado",
            "pendientes": "pendiente",
            "parciales": "parcial",
            "vencidas": "vencido",
        }

        if estado == "abiertas":
            queryset = queryset.filter(
                saldo_db__gt=0
            )

        elif estado in equivalencias:
            queryset = queryset.filter(
                estado_filtro=equivalencias[estado]
            )

        # "todas" no agrega restricciones por estado.

        return queryset.order_by("-fecha", "-pk")


  
    





class CuentaPorPagarCreateView(ModulePermissionMixin, SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, CreateView):

    model = CuentaPorPagar
    form_class = CuentaPorPagarForm
    template_name = "compras/cuenta_form.html"
    module_permission = "finanzas"

    def form_valid(self, form):

        response = super().form_valid(form)

        meses = form.cleaned_data.get("meses")

        if meses and meses > 1:

            ProgramacionPago.objects.filter(
                cuenta=self.object
            ).delete()

            monto = (
                self.object.monto_total / Decimal(meses)
            ).quantize(Decimal("0.01"))

            fecha = self.object.fecha_vencimiento

            for i in range(meses):

                # El último pago absorbe la diferencia por redondeo
                if i == meses - 1:
                    monto_pago = self.object.monto_total - (
                        monto * (meses - 1)
                    )
                else:
                    monto_pago = monto

                ProgramacionPago.objects.create(
                    cuenta=self.object,
                    numero=i + 1,
                    fecha_vencimiento=fecha,
                    monto=monto_pago,
                )

                fecha += relativedelta(months=1)

        return response

    def get_success_url(self):
        return reverse(
            "compras:cuenta_detail",
            kwargs={"pk": self.object.pk}
        )
    

class CuentaPorPagarUpdateView(ModulePermissionMixin, SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, UpdateView):

    model = CuentaPorPagar
    module_permission = "finanzas"
    form_class = CuentaPorPagarForm
    template_name = "compras/cuenta_form.html"

    success_url = reverse_lazy(
        "compras:cuenta_list"
    )






class RegistrarPagoCuentaView(ModulePermissionMixin, SucursalQuerysetMixin, SucursalFormMixin,LoginRequiredMixin,CreateView):

    model = PagoCuentaPorPagar
    module_permission = "finanzas"


    form_class = PagoCuentaForm

    template_name = "compras/pago_form.html"

    def dispatch(self, request, *args, **kwargs):

        self.cuenta = get_object_or_404(
            CuentaPorPagar,
            pk=self.kwargs["pk"]
        )

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        form.instance.cuenta = self.cuenta

        return super().form_valid(form)


class CuentaPorPagarDeleteView(ModulePermissionMixin, SucursalQuerysetMixin, LoginRequiredMixin, DeleteView):

    model = CuentaPorPagar
    module_permission = "finanzas"


    template_name = "compras/cuenta_confirm_delete.html"

    success_url = reverse_lazy(
        "compras:cuenta_list"
    )







class CuentaPorPagarDetailView(ModulePermissionMixin,SucursalQuerysetMixin,LoginRequiredMixin,DetailView):

    model = CuentaPorPagar
    module_permission = "finanzas"

    template_name = "compras/cuenta_detail.html"
    context_object_name = "cuenta"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["today"] = date.today()

        context["pagos"] = (
            self.object.pagos
            .select_related("programacion")
            .all()
        )

        context["programaciones"] = (
            self.object.programaciones.all()
        )

        context["programacion_form"] = ProgramacionPagoForm()

        return context
    


class RegistrarPagoCuentaView(ModulePermissionMixin,SucursalQuerysetMixin,LoginRequiredMixin,CreateView):
    model = PagoCuentaPorPagar
    module_permission = "finanzas"
    form_class = PagoCuentaForm
    template_name = "compras/pago_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.cuenta = get_object_or_404(
            CuentaPorPagar.objects.select_related(
                "proveedor",
                "sucursal",
                "categoria",
            ),
            pk=kwargs["pk"],
        )

        self.programacion = None

        if kwargs.get("programacion_id"):
            self.programacion = get_object_or_404(
                ProgramacionPago,
                pk=kwargs["programacion_id"],
                cuenta=self.cuenta,
                estado="pendiente",
            )

        return super().dispatch(
            request,
            *args,
            **kwargs
        )

    def get_initial(self):
        return {
            "fecha": timezone.localdate(),
            "monto": (
                self.programacion.monto
                if self.programacion
                else self.cuenta.saldo
            ),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["cuenta"] = self.cuenta
        context["programacion"] = self.programacion

        return context

    @transaction.atomic
    def form_valid(self, form):
        pago = form.save(commit=False)

        pago.cuenta = self.cuenta

        if self.programacion:
            # Pago de una mensualidad
            pago.programacion = self.programacion
            pago.monto = self.programacion.monto

        else:
            # Pago en una sola exhibición
            pago.programacion = None
            pago.monto = self.cuenta.saldo

        pago.save()

        # Si se está pagando una programación,
        # marcarla como pagada.
        if self.programacion:
            self.programacion.estado = "pagado"
            self.programacion.save(
                update_fields=["estado"]
            )

        # Registrar gasto
        Gasto.objects.create(
            sucursal=self.cuenta.sucursal,
            categoria=self.cuenta.categoria,
            fecha=pago.fecha,
            monto=pago.monto,
            descripcion=(
                f"Pago a {self.cuenta.proveedor.nombre}"
            ),
        )

        return redirect(
            "compras:cuenta_detail",
            pk=self.cuenta.pk
        )


    






class ProgramarPagosView(ModulePermissionMixin,SucursalQuerysetMixin,LoginRequiredMixin, View):
    module_permission = "finanzas"


    def post(self, request, pk):

        cuenta = get_object_or_404(
            CuentaPorPagar,
            pk=pk
        )

        form = ProgramacionPagoForm(request.POST)

        if form.is_valid():

            meses = form.cleaned_data["meses"]

            ProgramacionPago.objects.filter(
                cuenta=cuenta
            ).delete()

            monto = (
                cuenta.monto_total / Decimal(meses)
            ).quantize(Decimal("0.01"))

            acumulado = Decimal("0.00")
            fecha = cuenta.fecha_vencimiento

            for i in range(meses):

                if i == meses - 1:
                    monto_pago = cuenta.monto_total - acumulado
                else:
                    monto_pago = monto
                    acumulado += monto

                ProgramacionPago.objects.create(
                    cuenta=cuenta,
                    numero=i + 1,
                    fecha_vencimiento=fecha,
                    monto=monto_pago,
                )

                fecha += relativedelta(months=1)

        return redirect(
            "compras:cuenta_detail",
            pk=cuenta.pk
        )