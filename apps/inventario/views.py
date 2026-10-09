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
from decimal import Decimal


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
)
from .models import Producto, VarianteProducto, InventarioDiario, Receta
from apps.sucursales.models import Sucursal
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


class InventarioDiarioUpdateView(
    ModulePermissionMixin, SucursalQuerysetMixin, LoginRequiredMixin, View
):

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

        return redirect("inventario:preparacion_list")


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