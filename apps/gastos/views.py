from django.urls import reverse_lazy
from django.db.models import Q
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)

from datetime import date
from calendar import monthrange
from apps.servicios.models import ServicioRecurrente, PagoServicio



from .models import CategoriaGasto, Gasto
from .forms import CategoriaGastoForm, GastoForm
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.sucursales.models import Sucursal
from apps.compras.models import CuentaPorPagar
from apps.nomina.models import Empleado, Nomina

from django.db.models import Sum
from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin,SucursalPermissionMixin,ModulePermissionMixin


 
class CategoriaGastoListView(ModulePermissionMixin, SucursalQuerysetMixin, LoginRequiredMixin, ListView):
    model = CategoriaGasto
    template_name = "gastos/categorias/list.html"
    context_object_name = "categorias"
    module_permission = "finanzas"


class CategoriaGastoCreateView(ModulePermissionMixin, SucursalQuerysetMixin ,  SucursalFormMixin, LoginRequiredMixin, CreateView):
    model = CategoriaGasto
    form_class = CategoriaGastoForm
    template_name = "gastos/categorias/form.html"
    success_url = reverse_lazy("gastos:categoria_list")
    module_permission = "finanzas"




class CategoriaGastoUpdateView(ModulePermissionMixin, SucursalFormMixin, LoginRequiredMixin, UpdateView,SucursalQuerysetMixin):
    model = CategoriaGasto
    form_class = CategoriaGastoForm
    template_name = "gastos/categorias/form.html"
    success_url = reverse_lazy("gastos:categoria_list")
    module_permission = "finanzas"

class CategoriaGastoDeleteView(ModulePermissionMixin, SucursalQuerysetMixin, LoginRequiredMixin, DeleteView):
    model = CategoriaGasto
    template_name = "gastos/categorias/delete.html"
    success_url = reverse_lazy("gastos:categoria_list")
    module_permission = "finanzas"




class GastoListView(ModulePermissionMixin, SucursalQuerysetMixin, LoginRequiredMixin, ListView):
    model = Gasto
    template_name = "gastos/list.html"
    context_object_name = "gastos"
    paginate_by = 20
    module_permission = "finanzas"

    def get_queryset(self):
        queryset = super().get_queryset()

        sucursal = self.request.GET.get("sucursal")
        categoria = self.request.GET.get("categoria")
        fecha_inicio = self.request.GET.get("fecha_inicio")
        fecha_fin = self.request.GET.get("fecha_fin")

        if sucursal:
            queryset = queryset.filter(sucursal_id=sucursal)

        if categoria:
            queryset = queryset.filter(categoria_id=categoria)

        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)

        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)

        return queryset.order_by("-fecha", "-id")

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs) 
        # Categorías disponibles 
        context["categorias"] = CategoriaGasto.objects.all() 
        # Total de todos los gastos que cumplen los filtros 
        total_gastos = self.get_queryset().aggregate( 
            total=Sum("monto") 
            )["total"] or 0 
        context["total_gastos"] = total_gastos 

        return context


class GastoCreateView(ModulePermissionMixin, SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, CreateView):
    model = Gasto
    form_class = GastoForm
    template_name = "gastos/form.html"
    success_url = reverse_lazy("gastos:list")
    module_permission = "ventas"

class GastoUpdateView(SucursalQuerysetMixin, LoginRequiredMixin, UpdateView):
    model = Gasto
    form_class = GastoForm
    template_name = "gastos/form.html"
    success_url = reverse_lazy("gastos:list")
    module_permission = "finanzas"


class GastoDeleteView(ModulePermissionMixin,SucursalQuerysetMixin, SucursalFormMixin, LoginRequiredMixin, DeleteView):
    model = Gasto
    template_name = "gastos/delete.html"
    success_url = reverse_lazy("gastos:list")
    module_permission = "finanzas"




  
class CompromisosListView(LoginRequiredMixin,SucursalPermissionMixin,TemplateView):

    template_name = "gastos/compromisos_pago.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        hoy = date.today()

        # ==========================================================
        # FILTROS
        # ==========================================================

        tipo = self.request.GET.get("tipo", "todos")

        try:
            mes = int(self.request.GET.get("mes", hoy.month))
            if mes < 1 or mes > 12:
                mes = hoy.month
        except (TypeError, ValueError):
            mes = hoy.month

        try:
            anio = int(self.request.GET.get("anio", hoy.year))
        except (TypeError, ValueError):
            anio = hoy.year

        sucursal_id = self.request.GET.get("sucursal", "")

        compromisos = []

        # ==========================================================
        # SUCURSALES DISPONIBLES PARA EL USUARIO
        # ==========================================================

        sucursales = self.request.user.sucursales_asignadas.all()

        # Si el usuario es propietario, agregar sus sucursales
        sucursales_propias = self.request.user.sucursales_propias.all()

        sucursales = (
            (sucursales | sucursales_propias)
            .distinct()
            .order_by("nombre")
        )

        # ==========================================================
        # FILTRO DE SUCURSAL
        # ==========================================================

        if sucursal_id:
            try:
                sucursal_id = int(sucursal_id)
            except (TypeError, ValueError):
                sucursal_id = ""

        # ==========================================================
        # SERVICIOS RECURRENTES
        # ==========================================================

        if tipo in ["todos", "servicios"]:

            servicios = self.filtrar_por_sucursal_usuario(
                ServicioRecurrente.objects.filter(
                    activo=True
                ).select_related(
                    "sucursal",
                    "categoria"
                )
            )

            if sucursal_id:
                servicios = servicios.filter(
                    sucursal_id=sucursal_id
                )

            # Último día del mes seleccionado
            ultimo_dia = monthrange(anio, mes)[1]

            for servicio in servicios:

                # --------------------------------------------------
                # ¿Ya fue pagado ese servicio durante el mes?
                # --------------------------------------------------

                pagado = PagoServicio.objects.filter(
                    servicio=servicio,
                    fecha_pago__year=anio,
                    fecha_pago__month=mes,
                ).exists()

                if pagado:
                    continue

                # --------------------------------------------------
                # Evitar error para servicios con día 29, 30 o 31
                # en meses que no tienen ese día.
                # --------------------------------------------------

                dia_pago = min(
                    servicio.dia_pago,
                    ultimo_dia
                )

                fecha_vencimiento = date(
                    anio,
                    mes,
                    dia_pago
                )

                dias_restantes = (
                    fecha_vencimiento - hoy
                ).days

                if dias_restantes < 0:
                    estado = "vencido"
                elif dias_restantes <= 5:
                    estado = "proximo"
                else:
                    estado = "pendiente"

                compromisos.append({
                    "tipo": "Servicio",
                    "sucursal": servicio.sucursal,
                    "concepto": servicio.nombre,
                    "categoria": servicio.categoria,
                    "proveedor": servicio.proveedor,
                    "monto": servicio.monto_estimado,
                    "fecha": fecha_vencimiento,
                    "estado": estado,
                    "objeto": servicio,
                    "dias_restantes": dias_restantes,
                })

        # ==========================================================
        # CUENTAS POR PAGAR
        # ==========================================================

        if tipo in ["todos", "cuentas"]:

            cuentas = self.filtrar_por_sucursal_usuario(
                CuentaPorPagar.objects.select_related(
                    "proveedor",
                    "categoria",
                    "sucursal"
                )
            )

            if sucursal_id:
                cuentas = cuentas.filter(
                    sucursal_id=sucursal_id
                )

            # Filtrar por mes y año
            cuentas = cuentas.filter(
                fecha_vencimiento__year=anio,
                fecha_vencimiento__month=mes,
            )

            for cuenta in cuentas:

                if cuenta.estatus == "pagado":
                    continue

                dias_restantes = (
                    cuenta.fecha_vencimiento - hoy
                ).days

                # Si tu modelo usa "parcial", conservarlo
                if cuenta.estatus == "parcial":
                    estado = "parcial"
                elif dias_restantes < 0:
                    estado = "vencido"
                elif dias_restantes <= 5:
                    estado = "proximo"
                else:
                    estado = "pendiente"

                compromisos.append({
                    "tipo": "Cuenta",
                    "sucursal": cuenta.sucursal,
                    "concepto": cuenta.descripcion,
                    "categoria": cuenta.categoria,
                    "proveedor": cuenta.proveedor,
                    "monto": cuenta.saldo,
                    "fecha": cuenta.fecha_vencimiento,
                    "estado": estado,
                    "objeto": cuenta,
                    "dias_restantes": dias_restantes,
                })

        # ==========================================================
        # NÓMINA
        # ==========================================================

        if tipo in ["todos", "nomina"]:

            empleados = self.filtrar_por_sucursal_usuario(
                Empleado.objects.filter(
                    activo=True
                ).select_related(
                    "sucursal"
                )
            )

            if sucursal_id:
                empleados = empleados.filter(
                    sucursal_id=sucursal_id
                )

            nominas = Nomina.objects.filter(
                empleado__in=empleados,
                estado__in=["pendiente", "vencida"],
                fecha_vencimiento__year=anio,
                fecha_vencimiento__month=mes,
            ).select_related(
                "empleado",
                "empleado__sucursal",
            )

            for nomina in nominas:

                dias_restantes = (
                    nomina.fecha_vencimiento - hoy
                ).days

                if dias_restantes < 0:
                    estado = "vencido"
                elif dias_restantes <= 5:
                    estado = "proximo"
                else:
                    estado = "pendiente"

                compromisos.append({
                    "tipo": "Nomina",
                    "sucursal": nomina.empleado.sucursal,
                    "concepto": nomina.empleado.nombre,
                    "categoria": "Nómina",
                    "proveedor": "Empleado",
                    "monto": nomina.monto,
                    "fecha": nomina.fecha_vencimiento,
                    "estado": estado,
                    "objeto": nomina,
                    "dias_restantes": dias_restantes,
                })

        # ==========================================================
        # ORDENAR
        # ==========================================================

        compromisos.sort(
            key=lambda x: x["fecha"]
        )

        # ==========================================================
        # CONTEXTO
        # ==========================================================

        context["compromisos"] = compromisos
        context["tipo"] = tipo
        context["mes"] = mes
        context["anio"] = anio
        context["sucursal_id"] = sucursal_id
        context["sucursales"] = sucursales

        return context
