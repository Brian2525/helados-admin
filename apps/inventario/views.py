from django.shortcuts import render
from django.db.models import ProtectedError
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.db import transaction
from django.db.models import Count
from datetime import datetime, timedelta
from datetime import date
from decimal import Decimal, InvalidOperation
from django.core.exceptions import PermissionDenied
from apps.inventario.services_conciliacion import (
    calcular_conciliacion_diaria,
)

from apps.inventario.services_alertas import (
    obtener_alertas_inventario,
)



from django.shortcuts import get_object_or_404, redirect, render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
    TemplateView,
)

from .forms import (
    ProductoForm,
    VarianteProductoForm,
    InventarioDiarioFormSet,
    InventarioSucursalForm,
    InventarioCapturaFormSet,
    PreparacionForm,
    RecepcionMercanciaForm,
    MermaForm,
    CierreInventarioFormSet,
    MovimientoInventarioPOSForm,
    InventarioInicialAutorizacionForm,
)
from .models import Producto, VarianteProducto, InventarioDiario, Receta, MovimientoInventario, InventarioInicialAutorizado, InventarioInicialDetalle
from apps.sucursales.models import Sucursal
from apps.ventas.models import CierreDiario
from apps.core.mixins import (
    SucursalQuerysetMixin,
    SucursalFormMixin,
    ModulePermissionMixin,
    SucursalActivaMixin,
    SucursalPermissionMixin,
)
from .services import (
    consumo_teorico_periodo,
    existencia_teorica_diaria,
    registrar_preparacion,
    registrar_entrada_inventario,
    registrar_merma,
)


class ProductoListView(ModulePermissionMixin, LoginRequiredMixin, ListView):
    module_permission = "administracion"
    model = Producto
    template_name = "inventario/productos/producto_list.html"
    context_object_name = "productos"
    paginate_by = 20
    module_permission = "finanzas"


class ProductoCreateView(ModulePermissionMixin, LoginRequiredMixin, CreateView):
    module_permission = "administracion"
    model = Producto
    form_class = ProductoForm
    template_name = "inventario/productos/producto_form.html"
    success_url = reverse_lazy("inventario:producto_list")

    module_permission = "finanzas"


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    module_permission = "administracion"
    model = Producto
    module_permission = "administracion"
    form_class = ProductoForm
    template_name = "inventario/productos/producto_form.html"
    success_url = reverse_lazy("inventario:producto_list")


class ProductoDeleteView(ModulePermissionMixin, LoginRequiredMixin, DeleteView):
    module_permission = "administracion"
    model = Producto
    module_permission = "administracion"
    template_name = "inventario/productos/producto_confirm_delete.html"
    success_url = reverse_lazy("inventario:producto_list")


# variantes de producto


class VarianteProductoListView(LoginRequiredMixin, ListView):
    module_permission = "administracion"
    model = VarianteProducto
    template_name = "inventario/productos/variantes_productos/variante_list.html"
    context_object_name = "variantes"

    def dispatch(self, request, *args, **kwargs):

        self.producto = get_object_or_404(Producto, pk=kwargs["producto_id"])

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        return VarianteProducto.objects.filter(producto=self.producto).order_by(
            "nombre"
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["producto"] = self.producto

        return context


class VarianteProductoCreateView(LoginRequiredMixin, CreateView):
    module_permission = "administracion"
    model = VarianteProducto
    form_class = VarianteProductoForm
    template_name = "inventario/productos/variantes_productos/variante_form.html"

    def dispatch(self, request, *args, **kwargs):

        self.producto = get_object_or_404(Producto, pk=kwargs["producto_id"])

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        form.instance.producto = self.producto

        messages.success(
            self.request,
            f'La variante "{form.instance.nombre}" fue creada correctamente.',
        )

        return super().form_valid(form)

    def get_success_url(self):

        return reverse(
            "inventario:variante_list", kwargs={"producto_id": self.producto.id}
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["producto"] = self.producto
        context["titulo"] = "Nueva variante"

        return context


class VarianteProductoUpdateView(LoginRequiredMixin, UpdateView):

    module_permission = "administracion"
    model = VarianteProducto
    form_class = VarianteProductoForm
    template_name = "inventario/productos/variantes_productos/variante_form.html"
    context_object_name = "variante"

    def dispatch(self, request, *args, **kwargs):

        self.producto = get_object_or_404(Producto, pk=kwargs["producto_id"])

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        return VarianteProducto.objects.filter(producto=self.producto)

    def get_success_url(self):

        return reverse(
            "inventario:variante_list", kwargs={"producto_id": self.producto.id}
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["producto"] = self.producto
        context["titulo"] = "Editar variante"

        return context

    def form_valid(self, form):

        messages.success(
            self.request,
            f'La variante "{form.instance.nombre}" fue actualizada correctamente.',
        )

        return super().form_valid(form)


class VarianteProductoDeleteView(SucursalQuerysetMixin, LoginRequiredMixin, DeleteView):
    module_permission = "administracion"
    model = VarianteProducto
    template_name = (
        "inventario/productos/variantes_productos/variante_confirm_delete.html"
    )
    context_object_name = "variante"

    def dispatch(self, request, *args, **kwargs):

        self.producto = get_object_or_404(Producto, pk=kwargs["producto_id"])

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        return VarianteProducto.objects.filter(producto=self.producto)

    def get_success_url(self):

        return reverse(
            "inventario:variante_list", kwargs={"producto_id": self.producto.id}
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["producto"] = self.producto

        return context

    def form_valid(self, form):

        nombre = self.object.nombre

        try:
            response = super().form_valid(form)

            messages.success(
                self.request, f'La variante "{nombre}" fue eliminada correctamente.'
            )

            return response

        except ProtectedError:

            messages.error(
                self.request,
                "No se puede eliminar esta variante porque "
                "está siendo utilizada en otros registros.",
            )

            return redirect(self.get_success_url())


# Inventario diario views


class InventarioDiarioView(SucursalPermissionMixin, LoginRequiredMixin, View):

    module_permission = "ventas"

    template_name = "inventario/inventario_diario/" "inventario_form.html"

    def get_sucursales(self):
        return self.get_sucursales_usuario()

    def get_variantes_inventario(self):

        return (
            VarianteProducto.objects.filter(
                activo=True,
                producto__activo=True,
                producto__tipo__in=[
                    "insumo",
                    "ambos",
                ],
            )
            .select_related("producto")
            .order_by(
                "producto__nombre",
                "nombre",
            )
        )

    # ==========================================================
    # GET
    # ==========================================================

    def get(self, request):

        sucursales = self.get_sucursales()

        sucursal_id = request.GET.get("sucursal")

        sucursal = None
        formset = None

        if sucursal_id:

            sucursal = get_object_or_404(sucursales, pk=sucursal_id)

            fecha = timezone.localdate()

            variantes = list(self.get_variantes_inventario())

            # ==========================================
            # VERIFICAR INVENTARIO YA REGISTRADO
            # ==========================================

            inventario_existente = InventarioDiario.objects.filter(
                sucursal=sucursal,
                fecha=fecha,
            ).exists()

            if inventario_existente:

                messages.info(request, "El inventario de hoy ya fue registrado.")

                return redirect(
                    "inventario:inventario_detail",
                    sucursal_id=sucursal.id,
                    fecha=fecha.isoformat(),
                )

            # ==========================================
            # EXISTENCIA TEÓRICA
            # ==========================================

            existencias = existencia_teorica_diaria(
                sucursal=sucursal,
                fecha=fecha,
            )

            existencias_por_variante = {
                item["variante"].id: item for item in existencias
            }

            # ==========================================
            # FORMSET
            # ==========================================

            initial = [
                {
                    "variante_id": variante.id,
                }
                for variante in variantes
            ]

            formset = InventarioCapturaFormSet(initial=initial)

            variantes_por_id = {variante.id: variante for variante in variantes}

            # Información adicional para el template
            for form in formset:

                variante_id = form.initial["variante_id"]

                form.variante = variantes_por_id.get(variante_id)

                form.datos_teoricos = existencias_por_variante.get(variante_id)

        sucursal_form = InventarioSucursalForm(
            sucursales=sucursales, initial={"sucursal": sucursal_id}
        )

        return render(
            request,
            self.template_name,
            {
                "sucursal_form": sucursal_form,
                "formset": formset,
                "sucursal": sucursal,
                "fecha": timezone.localdate(),
            },
        )

    # ==========================================================
    # POST
    # ==========================================================

    @transaction.atomic
    def post(self, request):

        sucursales = self.get_sucursales()

        sucursal_form = InventarioSucursalForm(request.POST, sucursales=sucursales)

        # ==========================================
        # VALIDAR SUCURSAL
        # ==========================================

        if not sucursal_form.is_valid():

            return render(
                request,
                self.template_name,
                {
                    "sucursal_form": sucursal_form,
                    "formset": None,
                    "sucursal": None,
                    "fecha": timezone.localdate(),
                },
            )

        sucursal = sucursal_form.cleaned_data["sucursal"]

        fecha = timezone.localdate()

        # ==========================================
        # EVITAR DOBLE INVENTARIO
        # ==========================================

        inventario_existente = InventarioDiario.objects.filter(
            sucursal=sucursal,
            fecha=fecha,
        ).exists()

        if inventario_existente:

            messages.warning(request, "El inventario de hoy ya fue registrado.")

            return redirect(
                "inventario:inventario_detail",
                sucursal_id=sucursal.id,
                fecha=fecha.isoformat(),
            )

        # ==========================================
        # VARIANTES PERMITIDAS
        # ==========================================

        variantes = list(self.get_variantes_inventario())

        variantes_por_id = {variante.id: variante for variante in variantes}

        # ==========================================
        # FORMSET
        # ==========================================

        formset = InventarioCapturaFormSet(request.POST)

        # ==========================================
        # EXISTENCIA TEÓRICA
        # ==========================================

        existencias = existencia_teorica_diaria(
            sucursal=sucursal,
            fecha=fecha,
        )

        existencias_por_variante = {item["variante"].id: item for item in existencias}

        # ==========================================
        # GUARDAR INVENTARIO
        # ==========================================

        if formset.is_valid():

            for form in formset:

                variante_id = form.cleaned_data["variante_id"]

                cantidad = form.cleaned_data["cantidad"]

                # No confiar directamente
                # en el ID enviado por navegador
                variante = variantes_por_id.get(variante_id)

                if not variante:
                    continue

                datos = existencias_por_variante.get(variante_id)

                # Si nunca ha existido conteo previo,
                # no existe cantidad teórica confiable.
                cantidad_teorica = None
                consumo_teorico = None

                if datos:

                    cantidad_teorica = datos.get("cantidad_teorica")

                    if not datos.get("sin_inventario_inicial"):
                        consumo_teorico = datos.get("consumo_teorico")

                InventarioDiario.objects.create(
                    sucursal=sucursal,
                    fecha=fecha,
                    variante=variante,
                    cantidad=cantidad,
                    consumo_teorico=consumo_teorico,
                    cantidad_teorica=cantidad_teorica,
                    usuario=request.user,
                )

            messages.success(request, "Inventario registrado correctamente.")

            return redirect(
                "inventario:inventario_detail",
                sucursal_id=sucursal.id,
                fecha=fecha.isoformat(),
            )

        # ==========================================
        # FORMSET INVÁLIDO
        # RECONSTRUIR INFORMACIÓN VISUAL
        # ==========================================

        for form in formset:

            variante_id = None

            try:
                variante_id = int(form.data.get(form.add_prefix("variante_id")))

            except (
                TypeError,
                ValueError,
            ):
                pass

            form.variante = variantes_por_id.get(variante_id)

            form.datos_teoricos = existencias_por_variante.get(variante_id)

        return render(
            request,
            self.template_name,
            {
                "sucursal_form": sucursal_form,
                "formset": formset,
                "sucursal": sucursal,
                "fecha": fecha,
            },
        )


class InventarioDiarioCompletadoView(
    ModulePermissionMixin, SucursalQuerysetMixin, LoginRequiredMixin, View
):

    module_permission = "ventas"

    template_name = "inventario/inventario_diario/" "inventario_completado.html"

    def get(self, request, sucursal_id, fecha):

        sucursal = get_object_or_404(self.get_sucursales_usuario(), pk=sucursal_id)

        fecha = date.fromisoformat(fecha)

        return render(
            request,
            self.template_name,
            {
                "sucursal": sucursal,
                "fecha": fecha,
            },
        )


class InventarioDiarioListView(SucursalPermissionMixin, LoginRequiredMixin, ListView):
    module_permission = "administracion"
    template_name = "inventario/inventario_diario/inventario_list.html"

    context_object_name = "inventarios"

    paginate_by = 30

    def get_queryset(self):

        sucursales = self.get_sucursales_usuario()

        qs = (
            InventarioDiario.objects.filter(sucursal__in=sucursales)
            .values("sucursal", "sucursal__nombre", "fecha")
            .annotate(total_variantes=Count("id"))
            .order_by("-fecha", "sucursal__nombre")
        )

        sucursal_id = self.request.GET.get("sucursal")

        fecha = self.request.GET.get("fecha")

        if sucursal_id:

            qs = qs.filter(sucursal_id=sucursal_id)

        if fecha:

            qs = qs.filter(fecha=fecha)

        return qs


class InventarioDiarioDetailView(SucursalPermissionMixin, LoginRequiredMixin, View):

    module_permission = "administracion"

    template_name = "inventario/inventario_diario/" "inventario_detail.html"

    def get(self, request, sucursal_id, fecha):

        sucursales = self.get_sucursales_usuario()

        sucursal = get_object_or_404(sucursales, pk=sucursal_id)

        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

        inventarios = list(
            InventarioDiario.objects.filter(sucursal=sucursal, fecha=fecha)
            .select_related(
                "variante",
                "variante__producto",
                "usuario",
            )
            .order_by("variante__producto__nombre", "variante__nombre")
        )

        # ==========================================
        # INVENTARIO ANTERIOR
        # ==========================================

        for inventario in inventarios:

            anterior = (
                InventarioDiario.objects.filter(
                    sucursal=sucursal,
                    variante=inventario.variante,
                    fecha__lt=fecha,
                )
                .order_by("-fecha")
                .first()
            )

            inventario.conteo_anterior = anterior.cantidad if anterior else None

            inventario.fecha_conteo_anterior = anterior.fecha if anterior else None

        # ==========================================
        # RESUMEN
        # ==========================================

        productos_con_diferencia = 0
        productos_correctos = 0

        for inventario in inventarios:

            if inventario.diferencia is None:
                continue

            if inventario.diferencia == 0:
                productos_correctos += 1
            else:
                productos_con_diferencia += 1

        es_inventario_inicial = inventarios and all(
            inventario.cantidad_teorica is None for inventario in inventarios
        )

        return render(
            request,
            self.template_name,
            {
                "sucursal": sucursal,
                "fecha": fecha,
                "inventarios": inventarios,
                "productos_correctos": productos_correctos,
                "productos_con_diferencia": productos_con_diferencia,
                "es_inventario_inicial": es_inventario_inicial,
            },
        )


class InventarioDiarioUpdateView(ModulePermissionMixin, SucursalQuerysetMixin, LoginRequiredMixin, View):

    module_permission = "administracion"

    template_name = "inventario/inventario_diario/" "inventario_update.html"

    def get_inventarios(self, sucursal_id, fecha):
        return (
            InventarioDiario.objects.filter(sucursal_id=sucursal_id, fecha=fecha)
            .select_related("sucursal", "variante", "variante__producto")
            .order_by("variante__producto__nombre", "variante__nombre")
        )

    def get(self, request, sucursal_id, fecha):
        sucursal = get_object_or_404(self.get_sucursales_usuario(), pk=sucursal_id)

        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

        inventarios = self.get_inventarios(sucursal.id, fecha)

        formset = InventarioDiarioFormSet(queryset=inventarios)

        return render(
            request,
            self.template_name,
            {
                "formset": formset,
                "sucursal": sucursal,
                "fecha": fecha,
            },
        )

    @transaction.atomic
    def post(self, request, sucursal_id, fecha):
        sucursal = get_object_or_404(self.get_sucursales_usuario(), pk=sucursal_id)

        inventarios = self.get_inventarios(sucursal.id, fecha)

        formset = InventarioDiarioFormSet(request.POST, queryset=inventarios)

        if formset.is_valid():

            formset.save()

            messages.success(request, "Inventario actualizado correctamente.")

            return redirect(
                "inventario:inventario_detail", sucursal_id=sucursal.id, fecha=fecha
            )

        return render(
            request,
            self.template_name,
            {
                "formset": formset,
                "sucursal": sucursal,
                "fecha": fecha,
            },
        )


class ConsumoTeoricoView(
    LoginRequiredMixin, SucursalActivaMixin, SucursalPermissionMixin, View
):
    template_name = "inventario/consumo_teorico.html"

    def get(self, request):

        sucursal = request.sucursal_activa
        hoy = timezone.localdate()

        # ==========================================
        # FILTRO
        # ==========================================

        periodo = request.GET.get("periodo", "hoy")

        fecha_inicio = hoy
        fecha_fin = hoy

        # ==========================================
        # HOY
        # ==========================================

        if periodo == "hoy":

            fecha_inicio = hoy
            fecha_fin = hoy

        # ==========================================
        # ESTA SEMANA
        # ==========================================

        elif periodo == "semana":

            fecha_inicio = hoy - timedelta(days=hoy.weekday())

            fecha_fin = hoy

        # ==========================================
        # PERSONALIZADO
        # ==========================================

        elif periodo == "personalizado":

            fecha_inicio_str = request.GET.get("fecha_inicio")

            fecha_fin_str = request.GET.get("fecha_fin")

            try:

                if fecha_inicio_str:
                    fecha_inicio = timezone.datetime.strptime(
                        fecha_inicio_str, "%Y-%m-%d"
                    ).date()

                if fecha_fin_str:
                    fecha_fin = timezone.datetime.strptime(
                        fecha_fin_str, "%Y-%m-%d"
                    ).date()

            except ValueError:

                fecha_inicio = hoy
                fecha_fin = hoy
                periodo = "hoy"

        # ==========================================
        # EVITAR RANGO INVERTIDO
        # ==========================================

        if fecha_inicio > fecha_fin:

            fecha_inicio, fecha_fin = (
                fecha_fin,
                fecha_inicio,
            )

        # ==========================================
        # CONSUMO
        # ==========================================

        consumos = consumo_teorico_periodo(
            sucursal=sucursal,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        # ==========================================
        # AGRUPAR POR PRODUCTO
        # ==========================================

        productos = {}

        for item in consumos:

            variante = item["variante"]

            producto = variante.producto

            if producto.id not in productos:

                productos[producto.id] = {
                    "producto": producto,
                    "variantes": [],
                }

            productos[producto.id]["variantes"].append(
                {
                    "variante": variante,
                    "cantidad": item["cantidad"],
                }
            )

        # ==========================================
        # CONTEXTO
        # ==========================================

        return render(
            request,
            self.template_name,
            {
                "sucursal_activa": sucursal,
                "periodo": periodo,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "productos": list(productos.values()),
            },
        )


class PreparacionCreateView(
    LoginRequiredMixin,
    SucursalPermissionMixin,
    SucursalActivaMixin,
    FormView,
):

    template_name = "inventario/preparacion_form.html"
    form_class = PreparacionForm

    def get_variante(self):

        return get_object_or_404(
            VarianteProducto.objects.select_related("producto"),
            id=self.kwargs["variante_id"],
            activo=True,
            producto__activo=True,
            receta__activa=True,
            receta__momento_consumo=(Receta.MomentoConsumo.PREPARACION),
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        variante = self.get_variante()

        receta = Receta.objects.prefetch_related(
            "detalles",
            "detalles__insumo",
            "detalles__insumo__producto",
        ).get(
            variante_vendida=variante,
            activa=True,
            momento_consumo=(Receta.MomentoConsumo.PREPARACION),
        )

        context["variante"] = variante
        context["receta"] = receta

        return context

    def form_valid(self, form):

        variante = self.get_variante()
        cantidad = form.cleaned_data["cantidad"]

        registrar_preparacion(
            sucursal=self.request.sucursal_activa,
            variante=variante,
            cantidad=cantidad,
            usuario=self.request.user,
        )

        messages.success(
            self.request,
            (f"Se prepararon correctamente " f"{cantidad} unidades de {variante}."),
        )

        return redirect("ventas:pos_nueva_venta")







class PreparacionListView(
    LoginRequiredMixin,
    SucursalPermissionMixin,
    SucursalActivaMixin,
    TemplateView,
):
    template_name = "inventario/preparacion_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["recetas"] = Receta.objects.filter(
            activa=True,
            momento_consumo=(Receta.MomentoConsumo.PREPARACION),
            variante_vendida__activo=True,
            variante_vendida__producto__activo=True,
        ).select_related(
            "variante_vendida",
            "variante_vendida__producto",
        )

        return context


class RecepcionMercanciaListView(LoginRequiredMixin,SucursalPermissionMixin,SucursalActivaMixin,TemplateView,):

    template_name = "inventario/recepcion_list.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["variantes"] = (
            VarianteProducto.objects.filter(
                activo=True,
                producto__activo=True,
                producto__controlar_inventario=True,
            )
            .select_related("producto")
            .order_by(
                "producto__nombre",
                "nombre",
            )
        )

        return context


class RecepcionMercanciaCreateView(LoginRequiredMixin,SucursalPermissionMixin,SucursalActivaMixin,FormView,):

    template_name = "inventario/recepcion_form.html"
    form_class = RecepcionMercanciaForm

    def get_variante(self):

        return get_object_or_404(
            VarianteProducto.objects.select_related("producto"),
            id=self.kwargs["variante_id"],
            activo=True,
            producto__activo=True,
            producto__controlar_inventario=True,
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["variante"] = self.get_variante()

        return context

    def form_valid(self, form):

        variante = self.get_variante()

        movimiento = registrar_entrada_inventario(
            sucursal=self.request.sucursal_activa,
            variante=variante,
            cantidad=form.cleaned_data["cantidad"],
            usuario=self.request.user,
            observaciones=(form.cleaned_data["observaciones"]),
        )

        messages.success(
            self.request,
            (f"Se recibieron " f"{movimiento.cantidad} " f"de {variante}."),
        )

        return redirect("inventario:recepcion_list")


class MermaListView(
    LoginRequiredMixin,
    SucursalPermissionMixin,
    SucursalActivaMixin,
    TemplateView,
):

    template_name = "inventario/merma_list.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["variantes"] = (
            VarianteProducto.objects.filter(
                activo=True,
                producto__activo=True,
                producto__controlar_inventario=True,
            )
            .select_related("producto")
            .order_by(
                "producto__nombre",
                "nombre",
            )
        )

        return context


class MermaCreateView(
    LoginRequiredMixin,
    SucursalPermissionMixin,
    SucursalActivaMixin,
    FormView,
):

    template_name = "inventario/merma_form.html"
    form_class = MermaForm

    def get_variante(self):

        return get_object_or_404(
            VarianteProducto.objects.select_related("producto"),
            id=self.kwargs["variante_id"],
            activo=True,
            producto__activo=True,
            producto__controlar_inventario=True,
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["variante"] = self.get_variante()

        return context

    def form_valid(self, form):

        variante = self.get_variante()

        movimiento = registrar_merma(
            sucursal=self.request.sucursal_activa,
            variante=variante,
            cantidad=form.cleaned_data["cantidad"],
            motivo=form.cleaned_data["motivo"],
            observaciones=form.cleaned_data["observaciones"],
            usuario=self.request.user,
        )

        messages.success(
            self.request,
            (f"Se registró una merma de " f"{movimiento.cantidad} de {variante}."),
        )

        return redirect("inventario:merma_list")


class CierreInventarioView(
    LoginRequiredMixin,
    SucursalPermissionMixin,
    SucursalActivaMixin,
    TemplateView,
):

    template_name = "inventario/cierre_inventario.html"

    def get_fecha(self):
        return timezone.localdate()

    def get_existencias(self):

        return existencia_teorica_diaria(
            sucursal=self.request.sucursal_activa,
            fecha=self.get_fecha(),
        )

    def get_initial(self):

        initial = []

        for item in self.get_existencias():

            initial.append(
                {
                    "variante_id": item["variante"].id,
                }
            )

        return initial

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        existencias = self.get_existencias()

        formset = kwargs.get("formset")

        if formset is None:
            formset = CierreInventarioFormSet(
                initial=[
                    {
                        "variante_id": item["variante"].id,
                    }
                    for item in existencias
                ]
            )

        # Relacionamos cada formulario con su cálculo
        filas = []

        for item, form in zip(
            existencias,
            formset.forms,
        ):

            filas.append(
                {
                    "item": item,
                    "form": form,
                }
            )

        context["fecha"] = self.get_fecha()
        context["formset"] = formset
        context["filas"] = filas

        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        fecha = self.get_fecha()


        cierre_finalizado = CierreDiario.objects.filter(
            sucursal=request.sucursal_activa,
            fecha=fecha,
            estado__in=[
                CierreDiario.Estado.COMPLETADO,
                CierreDiario.Estado.REVISADO,
            ],
        ).exists()

        if cierre_finalizado:
            messages.warning(
                request,
                "El cierre diario ya fue finalizado. "
                "No puedes modificar el inventario."
            )

            return redirect("ventas:cierre_diario_flow")






        existencias = self.get_existencias()

        formset = CierreInventarioFormSet(
            request.POST
        )

        if not formset.is_valid():
  
           

            return self.render_to_response(
                self.get_context_data(
                formset=formset
              )  
            )

        existencia_por_variante = {
            item["variante"].id: item
            for item in existencias
        }

        for form in formset:

            variante_id = form.cleaned_data[
                "variante_id"
            ]

            cantidad_fisica = form.cleaned_data[
                "cantidad"
            ]

            item = existencia_por_variante.get(
                variante_id
            )

            if not item:
                continue

            variante = item["variante"]

            InventarioDiario.objects.update_or_create(
                sucursal=request.sucursal_activa,
                fecha=fecha,
                variante=variante,
                defaults={
                    "cantidad": cantidad_fisica,
                    "cantidad_teorica": (
                        item["cantidad_teorica"]
                    ),
                    "consumo_teorico": (
                        item["consumo_teorico"]
                    ),
                },
            )

        messages.success(
            request,
            "El cierre de inventario se registró correctamente."
        )

        return redirect(
            "inventario:cierre_inventario_completado"
        )





class CierreInventarioCompletadoView(LoginRequiredMixin,SucursalPermissionMixin,SucursalActivaMixin,TemplateView,):

    
    template_name = (
        "inventario/cierre_inventario_completado.html"
    )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        fecha = timezone.localdate()

        inventarios = (
            InventarioDiario.objects
            .filter(
                sucursal=self.request.sucursal_activa,
                fecha=fecha,
            )
            .select_related(
                "variante",
                "variante__producto",
            )
            .order_by(
                "variante__producto__nombre",
                "variante__nombre",
            )
        )

        context["fecha"] = fecha
        context["inventarios"] = inventarios

        return context



class InventarioMenuView(
    LoginRequiredMixin,
    SucursalPermissionMixin,
    SucursalActivaMixin,
    TemplateView,
):
    template_name = "inventario/pos/inventario_menu.html"






class MovimientoInventarioPOSListView(
    LoginRequiredMixin,
    ModulePermissionMixin,
    SucursalActivaMixin,
    SucursalPermissionMixin,
    View,
):

    module_permission = "inventario"
   

    template_name = "inventario/pos/movimiento_list.html"

    def get(self, request):
        sucursal = request.sucursal_activa

        movimientos = (
            MovimientoInventario.objects
            .filter(sucursal=sucursal)
            .select_related(
                "variante",
                "variante__producto",
                "usuario",
            )
            .order_by("-fecha_hora", "-id")[:50]
        )

        return render(
            request,
            self.template_name,
            {
                "movimientos": movimientos,
                "sucursal_activa": sucursal,
                "pos_seccion": "mas",
            },
        )






class MovimientoInventarioPOSCreateView(
    LoginRequiredMixin,
    ModulePermissionMixin,
    SucursalActivaMixin,
    SucursalPermissionMixin,
    View,
):

    module_permission = "inventario"
   
    template_name = "inventario/pos/movimiento_form.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "form": MovimientoInventarioPOSForm(),
                "sucursal_activa": request.sucursal_activa,
                "pos_seccion": "mas",
            },
        )

    @transaction.atomic
    def post(self, request):

        form = MovimientoInventarioPOSForm(request.POST)

        if form.is_valid():

            movimiento = form.save(commit=False)

            # No confiar en sucursal ni usuario del navegador.
            movimiento.sucursal = request.sucursal_activa
            movimiento.usuario = request.user

            # Restricción adicional del lado del servidor.
            tipos_permitidos = {
                MovimientoInventario.TipoMovimiento.AJUSTE_ENTRADA,
                MovimientoInventario.TipoMovimiento.AJUSTE_SALIDA,
                MovimientoInventario.TipoMovimiento.MERMA,
            }

            if movimiento.tipo not in tipos_permitidos:
                form.add_error(
                    "tipo",
                    "Movimiento no permitido.",
                )
            else:
                movimiento.full_clean()
                movimiento.save()

                messages.success(
                    request,
                    "Movimiento de inventario registrado correctamente.",
                )

                return redirect(
                    "inventario:pos_movimiento_list"
                )

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "sucursal_activa": request.sucursal_activa,
                "pos_seccion": "mas",
            },
            status=400,
        )




class InventarioInicialPOSView(
    LoginRequiredMixin,
    SucursalPermissionMixin,
    SucursalActivaMixin,
    View,
):

    template_name = "inventario/pos/inventario_inicial.html"

    def dispatch(self, request, *args, **kwargs):
        # Primera versión: sólo superusuario.
        if not request.user.is_superuser:
            raise PermissionDenied(
                "Sólo administración puede autorizar el inventario inicial."
            )

        return super().dispatch(request, *args, **kwargs)

    def get_variantes(self):
        return (
            VarianteProducto.objects
            .filter(
                activo=True,
                producto__activo=True,
                producto__controlar_inventario=True,
            )
            .select_related("producto")
            .order_by(
                "producto__nombre",
                "nombre",
            )
        )

    def inicializado(self, sucursal):
        return MovimientoInventario.objects.filter(
            sucursal=sucursal,
            tipo=MovimientoInventario.TipoMovimiento.INVENTARIO_INICIAL,
        ).exists()

    def get(self, request):

        sucursal = request.sucursal_activa

        return render(
            request,
            self.template_name,
            {
                "sucursal_activa": sucursal,
                "variantes": self.get_variantes(),
                "inicializado": self.inicializado(sucursal),
                "pos_seccion": "mas",
            },
        )

    def post(self, request):

        sucursal = request.sucursal_activa
        variantes = list(self.get_variantes())

        cantidades = {}
        errores = {}

        # Validar todas las variantes antes de guardar.
        for variante in variantes:

            campo = f"cantidad_{variante.id}"
            valor = request.POST.get(campo, "").strip()

            if not valor:
                errores[variante.id] = "Captura la cantidad."
                continue

            try:
                cantidad = Decimal(valor)
            except (InvalidOperation, ValueError):
                errores[variante.id] = "Cantidad inválida."
                continue

            if not cantidad.is_finite() or cantidad < 0:
                errores[variante.id] = (
                    "La cantidad debe ser cero o mayor."
                )
                continue

            if cantidad.as_tuple().exponent < -4:
                errores[variante.id] = (
                    "Máximo cuatro decimales."
                )
                continue

            if cantidad >= Decimal("100000000"):
                errores[variante.id] = (
                    "Cantidad fuera del rango permitido."
                )
                continue

            cantidades[variante.id] = cantidad

        if not variantes:
            messages.error(
                request,
                "No hay variantes con control de inventario."
            )

        elif errores:
            messages.error(
                request,
                "Revisa las cantidades antes de autorizar."
            )

        else:
            with transaction.atomic():

                # Serializa inicializaciones concurrentes
                # de esta sucursal.
                Sucursal.objects.select_for_update().get(
                    pk=sucursal.pk
                )

                # Sólo una inicialización inicial por sucursal.
                if self.inicializado(sucursal):
                    messages.error(
                        request,
                        "Esta sucursal ya tiene inventario inicial."
                    )
                else:
                    fecha_corte = timezone.now()

                    movimientos = [
                        MovimientoInventario(
                            sucursal=sucursal,
                            variante=variante,
                            tipo=(
                                MovimientoInventario
                                .TipoMovimiento
                                .INVENTARIO_INICIAL
                            ),
                            cantidad=cantidades[variante.id],
                            fecha_hora=fecha_corte,
                            usuario=request.user,
                            observaciones=(
                                "Inventario inicial autorizado "
                                f"por {request.user.get_username()}."
                            ),
                        )
                        for variante in variantes
                    ]

                    # El modelo exige cantidad > 0.
                    # Las existencias cero quedan representadas
                    # por la ausencia de un movimiento inicial
                    # para esa variante, pero la sucursal debe
                    # quedar inicializada por lo menos con uno.
                    movimientos = [
                        m for m in movimientos
                        if m.cantidad > 0
                    ]

                    if not movimientos:
                        messages.error(
                            request,
                            "No se puede inicializar con todas "
                            "las cantidades en cero usando "
                            "este esquema."
                        )
                    else:
                        for movimiento in movimientos:
                            movimiento.full_clean()

                        MovimientoInventario.objects.bulk_create(
                            movimientos
                        )

                        messages.success(
                            request,
                            "Inventario inicial autorizado "
                            "correctamente."
                        )

                        return redirect(
                            "inventario:pos_inventario_inicial"
                        )

        return render(
            request,
            self.template_name,
            {
                "sucursal_activa": sucursal,
                "variantes": variantes,
                "inicializado": self.inicializado(sucursal),
                "errores": errores,
                "valores": request.POST,
                "pos_seccion": "mas",
            },
            status=400,
        )



class InventarioInicialPOSView(
    LoginRequiredMixin,
    SucursalPermissionMixin,
    SucursalActivaMixin,
    View,
):
    template_name = "inventario/pos/inventario_inicial.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_superuser:
            raise PermissionDenied("Sólo un superusuario puede autorizar el inventario inicial.")
        return super().dispatch(request, *args, **kwargs)

    def get_variantes(self):
        return list(
            VarianteProducto.objects.filter(
                activo=True,
                producto__activo=True,
                producto__controlar_inventario=True,
            )
            .select_related("producto")
            .order_by("producto__nombre", "nombre", "id")
        )

    def get_autorizacion(self, sucursal):
        return (
            InventarioInicialAutorizado.objects.filter(
                sucursal=sucursal,
                estado=InventarioInicialAutorizado.Estado.AUTORIZADO,
            )
            .select_related("usuario")
            .first()
        )

    def hay_movimientos_iniciales_anteriores(self, sucursal):
        # Evitar coexistencia con la versión provisional que creaba
        # movimientos INVENTARIO_INICIAL como saldos iniciales.
        return MovimientoInventario.objects.filter(
            sucursal=sucursal,
            tipo=MovimientoInventario.TipoMovimiento.INVENTARIO_INICIAL,
        ).exists()

    def get(self, request, *args, **kwargs):
        sucursal = request.sucursal_activa
        autorizacion = self.get_autorizacion(sucursal)
        variantes = self.get_variantes()
        form = InventarioInicialAutorizacionForm(variantes=variantes)
        return render(request, self.template_name, {
            "form": form,
            "filas": form.filas,
            "autorizacion": autorizacion,
            "hay_movimientos_iniciales_anteriores": self.hay_movimientos_iniciales_anteriores(sucursal),
            "sucursal_activa": sucursal,
            "pos_seccion": "mas",
        })

    def post(self, request, *args, **kwargs):
        sucursal = request.sucursal_activa
        variantes = self.get_variantes()
        form = InventarioInicialAutorizacionForm(request.POST, variantes=variantes)
        autorizacion = self.get_autorizacion(sucursal)
        hay_movimientos = self.hay_movimientos_iniciales_anteriores(sucursal)

        if not variantes:
            form.add_error(None, "No hay variantes activas bajo control de inventario.")
        if autorizacion:
            form.add_error(None, "Esta sucursal ya tiene un inventario inicial autorizado.")
        if hay_movimientos:
            form.add_error(None, "Hay movimientos de inventario inicial antiguos. Revisa la migración antes de autorizar.")

        if form.is_valid() and variantes and not autorizacion and not hay_movimientos:
            with transaction.atomic():
                # Serializa autorizaciones concurrentes de la misma sucursal.
                Sucursal.objects.select_for_update().get(pk=sucursal.pk)

                if InventarioInicialAutorizado.objects.filter(sucursal=sucursal).exists():
                    messages.error(request, "Ya existe una inicialización para esta sucursal.")
                    return redirect("inventario:pos_inventario_inicial")
                if self.hay_movimientos_iniciales_anteriores(sucursal):
                    messages.error(request, "Se detectaron movimientos iniciales anteriores.")
                    return redirect("inventario:pos_inventario_inicial")

                corte = InventarioInicialAutorizado.objects.create(
                    sucursal=sucursal,
                    usuario=request.user,
                    estado=InventarioInicialAutorizado.Estado.AUTORIZADO,
                    fecha_corte=timezone.now(),
                    observaciones="Corte inicial autorizado desde el POS.",
                )

                detalles = [
                    InventarioInicialDetalle(
                        inventario=corte,
                        variante=variante,
                        cantidad=form.cleaned_data[f"cantidad_{variante.pk}"],
                    )
                    for variante in variantes
                ]

                # bulk_create no ejecuta full_clean: validar antes de guardar.
                for detalle in detalles:
                    detalle.full_clean()
                InventarioInicialDetalle.objects.bulk_create(detalles)

            messages.success(request, "Inventario inicial autorizado correctamente.")
            return redirect("inventario:pos_inventario_inicial")

        return render(request, self.template_name, {
            "form": form,
            "filas": form.filas,
            "autorizacion": autorizacion,
            "hay_movimientos_iniciales_anteriores": hay_movimientos,
            "sucursal_activa": sucursal,
            "pos_seccion": "mas",
        }, status=400)




class ConciliacionInventarioPOSView(
    LoginRequiredMixin,
    SucursalPermissionMixin,
    SucursalActivaMixin,
    View,
):

    template_name = "inventario/pos/conciliacion_diaria.html"

    
    def get(self, request):

        sucursal = request.sucursal_activa

        # Por defecto mostrar ayer, porque hoy
        # todavía puede haber ventas y movimientos.
        fecha_default = (
            timezone.localdate()
            - timezone.timedelta(days=1)
        )

        fecha_texto = request.GET.get(
            "fecha",
            fecha_default.isoformat()
        )

        try:
            fecha = date.fromisoformat(fecha_texto)
        except (ValueError, TypeError):
            fecha = fecha_default

        fecha_hoy = timezone.localdate()

        # No permitir fechas futuras.
        if fecha > fecha_hoy:
            fecha = fecha_hoy

        corte = (
            InventarioInicialAutorizado.objects
            .filter(
                sucursal=sucursal,
                estado=(
                    InventarioInicialAutorizado
                    .Estado.AUTORIZADO
                ),
            )
            .order_by("-fecha_corte", "-id")
            .first()
        )

        conciliacion = None
        aviso = None

        if corte is None:
            aviso = (
                "Esta sucursal no tiene un inventario "
                "inicial autorizado."
            )

        elif corte.fecha_corte is None:
            aviso = (
                "El corte autorizado no tiene fecha válida."
            )

        else:
            fecha_corte_local = (
                timezone.localtime(corte.fecha_corte).date()
            )

            if fecha < fecha_corte_local:
                aviso = (
                    "La fecha seleccionada es anterior "
                    "al inventario inicial autorizado."
                )
            else:
                conciliacion = calcular_conciliacion_diaria(
                    sucursal=sucursal,
                    fecha=fecha,
                )

                if fecha == fecha_hoy:
                    aviso = (
                        "Estás consultando el día actual. "
                        "Las diferencias son provisionales "
                        "mientras existan ventas o movimientos."
                    )

                elif fecha == fecha_corte_local:
                    aviso = (
                        "Esta fecha contiene el corte inicial. "
                        "Los conteos físicos anteriores al corte "
                        "no deben compararse como cierre del día."
                    )

        return render(
            request,
            self.template_name,
            {
                "sucursal_activa": sucursal,
                "fecha": fecha,
                "fecha_hoy": fecha_hoy,
                "corte": corte,
                "conciliacion": conciliacion,
                "aviso": aviso,
                "pos_seccion": "mas",
            },
        )
    




class AlertasInventarioPOSView(
    LoginRequiredMixin,
    SucursalPermissionMixin,
    View,
):

    template_name = (
        "inventario/pos/alertas_inventario.html"
    )

    

    def get(self, request):

        fecha_default = (
            timezone.localdate()
            - timedelta(days=1)
        )

        fecha_texto = request.GET.get(
            "fecha",
            fecha_default.isoformat(),
        )

        try:
            fecha = date.fromisoformat(fecha_texto)
        except (TypeError, ValueError):
            fecha = fecha_default

        resultado = obtener_alertas_inventario(
            fecha=fecha
        )

        return render(
            request,
            self.template_name,
            {
                "fecha": fecha,
                "fecha_hoy": timezone.localdate(),
                "alertas": resultado["alertas"],
                "resumen": resultado["resumen"],
                "aviso": resultado["aviso"],
                "pos_seccion": "mas",
            },
        )