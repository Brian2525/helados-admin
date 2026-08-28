from django.shortcuts import render
from django.db.models import ProtectedError
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.db import transaction
from django.db.models import Count
from datetime import datetime
from datetime import date



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
)

from .forms import ProductoForm, VarianteProductoForm, InventarioDiarioFormSet, InventarioSucursalForm
from .models import Producto, VarianteProducto, InventarioDiario
from apps.sucursales.models import Sucursal
from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin,ModulePermissionMixin



from .models import (
    InventarioDiario,
    VarianteProducto,
)

from .forms import (
    InventarioDiarioFormSet,
    InventarioSucursalForm,
)

from apps.core.mixins import (
    SucursalPermissionMixin,
)











class ProductoListView(ModulePermissionMixin,LoginRequiredMixin, ListView):
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
    success_url = reverse_lazy(
        "inventario:producto_list"
    )

    module_permission = "finanzas"



class ProductoUpdateView( LoginRequiredMixin, UpdateView):
    module_permission = "administracion"
    model = Producto
    module_permission = "administracion"
    form_class = ProductoForm
    template_name = "inventario/productos/producto_form.html"
    success_url = reverse_lazy(
        "inventario:producto_list"
    )


    


class ProductoDeleteView(ModulePermissionMixin, LoginRequiredMixin, DeleteView):
    module_permission = "administracion"
    model = Producto
    module_permission = "administracion"
    template_name = "inventario/productos/producto_confirm_delete.html"
    success_url = reverse_lazy(
        "inventario:producto_list"
    )



#variantes de producto


class VarianteProductoListView(LoginRequiredMixin, ListView):
    module_permission = "administracion"
    model = VarianteProducto
    template_name = "inventario/productos/variantes_productos/variante_list.html"
    context_object_name = "variantes"

    def dispatch(self, request, *args, **kwargs):

        self.producto = get_object_or_404(
            Producto,
            pk=kwargs["producto_id"]
        )

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        return (
            VarianteProducto.objects
            .filter(producto=self.producto)
            .order_by("nombre")
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

        self.producto = get_object_or_404(
            Producto,
            pk=kwargs["producto_id"]
        )

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        form.instance.producto = self.producto

        messages.success(
            self.request,
            f'La variante "{form.instance.nombre}" fue creada correctamente.'
        )

        return super().form_valid(form)

    def get_success_url(self):

        return reverse(
            "inventario:variante_list",
            kwargs={
                "producto_id": self.producto.id
            }
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

            self.producto = get_object_or_404(
                Producto,
                pk=kwargs["producto_id"]
            )

            return super().dispatch(request, *args, **kwargs)

        def get_queryset(self):

            return VarianteProducto.objects.filter(
                producto=self.producto
            )

        def get_success_url(self):

            return reverse(
                "inventario:variante_list",
                kwargs={
                    "producto_id": self.producto.id
                }
            )

        def get_context_data(self, **kwargs):

            context = super().get_context_data(**kwargs)

            context["producto"] = self.producto
            context["titulo"] = "Editar variante"

            return context

        def form_valid(self, form):

            messages.success(
                self.request,
                f'La variante "{form.instance.nombre}" fue actualizada correctamente.'
            )

            return super().form_valid(form)



class VarianteProductoDeleteView(SucursalQuerysetMixin,LoginRequiredMixin, DeleteView):
        module_permission = "administracion"
        model = VarianteProducto
        template_name = "inventario/productos/variantes_productos/variante_confirm_delete.html"
        context_object_name = "variante"

        def dispatch(self, request, *args, **kwargs):

            self.producto = get_object_or_404(
                Producto,
                pk=kwargs["producto_id"]
            )

            return super().dispatch(request, *args, **kwargs)

        def get_queryset(self):

            return VarianteProducto.objects.filter(
                producto=self.producto
            )

        def get_success_url(self):

            return reverse(
                "inventario:variante_list",
                kwargs={
                    "producto_id": self.producto.id
                }
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
                    self.request,
                    f'La variante "{nombre}" fue eliminada correctamente.'
                )

                return response

            except ProtectedError:

                messages.error(
                    self.request,
                    "No se puede eliminar esta variante porque "
                    "está siendo utilizada en otros registros."
                )

                return redirect(
                    self.get_success_url()
                )

#Inventario diario views


class InventarioDiarioView(SucursalPermissionMixin,LoginRequiredMixin,View):


    module_permission = "ventas"
    template_name = (
        "inventario/inventario_diario/"
        "inventario_form.html"
    )

    def get_sucursales(self):

        return self.get_sucursales_usuario()

    def preparar_inventario(
        self,
        sucursal,
        fecha
    ):

        variantes = (
            VarianteProducto.objects
            .filter(
                activo=True,
                producto__activo=True,
                producto__registrar_venta_diaria=True
            )
            .select_related("producto")
        )

        for variante in variantes:

            inventario_anterior = (
                InventarioDiario.objects
                .filter(
                    sucursal=sucursal,
                    variante=variante,
                    fecha__lt=fecha
                )
                .order_by("-fecha")
                .first()
            )

            cantidad_inicial = (
                inventario_anterior.cantidad
                if inventario_anterior
                else 0
            )

            InventarioDiario.objects.get_or_create(
                sucursal=sucursal,
                variante=variante,
                fecha=fecha,
                defaults={
                    "cantidad": cantidad_inicial
                }
            )

    def get(self, request):

        sucursales = self.get_sucursales()

        sucursal_id = request.GET.get(
            "sucursal"
        )

        sucursal = None
        formset = None

        if sucursal_id:

            sucursal = get_object_or_404(
                sucursales,
                pk=sucursal_id
            )

            fecha = timezone.localdate()

            self.preparar_inventario(
                sucursal,
                fecha
            )

            inventarios = (
                InventarioDiario.objects
                .filter(
                    sucursal=sucursal,
                    fecha=fecha,
                    variante__activo=True,
                    variante__producto__activo=True,
                    variante__producto__registrar_venta_diaria=True
                )
                .select_related(
                    "variante",
                    "variante__producto"
                )
                .order_by(
                    "variante__producto__nombre",
                    "variante__nombre"
                )
            )

            formset = InventarioDiarioFormSet(
                queryset=inventarios
            )

        sucursal_form = InventarioSucursalForm(
            sucursales=sucursales,
            initial={
                "sucursal": sucursal_id
            }
        )

        return render(
            request,
            self.template_name,
            {
                "sucursal_form": sucursal_form,
                "formset": formset,
                "sucursal": sucursal,
                "fecha": timezone.localdate(),
            }
        )

    @transaction.atomic
    def post(self, request):

        sucursales = self.get_sucursales()

        sucursal_form = InventarioSucursalForm(
            request.POST,
            sucursales=sucursales
        )

        if not sucursal_form.is_valid():

            return render(
                request,
                self.template_name,
                {
                    "sucursal_form": sucursal_form,
                    "formset": None,
                    "sucursal": None,
                    "fecha": timezone.localdate(),
                }
            )

        sucursal = sucursal_form.cleaned_data[
            "sucursal"
        ]

        fecha = timezone.localdate()

        self.preparar_inventario(
            sucursal,
            fecha
        )

        inventarios = (
            InventarioDiario.objects
            .filter(
                                sucursal=sucursal,
                                fecha=fecha,
                                variante__activo=True,
                                variante__producto__activo=True,
                                variante__producto__registrar_venta_diaria=True
                            )
            .select_related(
                "variante",
                "variante__producto"
            )
            .order_by(
                "variante__producto__nombre",
                "variante__nombre"
            )
        )

        formset = InventarioDiarioFormSet(
            request.POST,
            queryset=inventarios
        )

        if formset.is_valid():

            formset.save()

            

            return redirect(
                "inventario:inventario_diario_completado",
                sucursal_id=sucursal.id,
                fecha=fecha.isoformat()
            )

        return render(
            request,
            self.template_name,
            {
                "sucursal_form": sucursal_form,
                "formset": formset,
                "sucursal": sucursal,
                "fecha": fecha,
            }
        )



class InventarioDiarioCompletadoView(ModulePermissionMixin,SucursalQuerysetMixin,LoginRequiredMixin,View):

    module_permission = "ventas"

    template_name = (
        "inventario/inventario_diario/"
        "inventario_completado.html"
    )

    def get(
        self,
        request,
        sucursal_id,
        fecha
    ):

        sucursal = get_object_or_404(
            self.get_sucursales_usuario(),
            pk=sucursal_id
        )

        fecha = date.fromisoformat(fecha)

        return render(
            request,
            self.template_name,
            {
                "sucursal": sucursal,
                "fecha": fecha,
            }
        )




class InventarioDiarioListView(SucursalPermissionMixin,LoginRequiredMixin,ListView):
    module_permission = "administracion"
    template_name = (
        "inventario/inventario_diario/inventario_list.html"
    )

    context_object_name = "inventarios"

    paginate_by = 30

    def get_queryset(self):

        sucursales = self.get_sucursales_usuario()

        qs = (
            InventarioDiario.objects
            .filter(
                sucursal__in=sucursales
            )
            .values(
                "sucursal",
                "sucursal__nombre",
                "fecha"
            )
            .annotate(
                total_variantes=Count("id")
            )
            .order_by(
                "-fecha",
                "sucursal__nombre"
            )
        )

        sucursal_id = self.request.GET.get(
            "sucursal"
        )

        fecha = self.request.GET.get(
            "fecha"
        )

        if sucursal_id:

            qs = qs.filter(
                sucursal_id=sucursal_id
            )

        if fecha:

            qs = qs.filter(
                fecha=fecha
            )

        return qs



class InventarioDiarioDetailView(SucursalPermissionMixin,LoginRequiredMixin,View):
    module_permission = "administracion"

    template_name = (
        "inventario/inventario_diario/inventario_detail.html"
    )

    def get(self, request, sucursal_id, fecha):

        sucursales = self.get_sucursales_usuario()

        sucursal = get_object_or_404(
            sucursales,
            pk=sucursal_id
        )

        inventarios = (
            InventarioDiario.objects
            .filter(
                sucursal=sucursal,
                fecha=fecha
            )
            .select_related(
                "variante",
                "variante__producto"
            )
            .order_by(
                "variante__producto__nombre",
                "variante__nombre"
            )
        )

        return render(
            request,
            self.template_name,
            {
                "sucursal": sucursal,
                "fecha": fecha,
                "inventarios": inventarios,
            }
        )



class InventarioDiarioUpdateView(ModulePermissionMixin,SucursalQuerysetMixin,LoginRequiredMixin,View):


    module_permission = "administracion"

    template_name = (
        "inventario/inventario_diario/"
        "inventario_update.html"
    )

    def get_inventarios(
        self,
        sucursal_id,
        fecha
    ):
        return (
            InventarioDiario.objects
            .filter(
                sucursal_id=sucursal_id,
                fecha=fecha
            )
            .select_related(
                "sucursal",
                "variante",
                "variante__producto"
            )
            .order_by(
                "variante__producto__nombre",
                "variante__nombre"
            )
        )

    def get(
        self,
        request,
        sucursal_id,
        fecha
    ):
        sucursal = get_object_or_404(
            self.get_sucursales_usuario(),
            pk=sucursal_id
        )

        fecha = datetime.strptime(
        fecha,
        "%Y-%m-%d"
        ).date()

        inventarios = self.get_inventarios(
            sucursal.id,
            fecha
        )

        formset = InventarioDiarioFormSet(
            queryset=inventarios
        )

        return render(
            request,
            self.template_name,
            {
                "formset": formset,
                "sucursal": sucursal,
                "fecha": fecha,
            }
        )

    @transaction.atomic
    def post(
        self,
        request,
        sucursal_id,
        fecha
    ):
        sucursal = get_object_or_404(
            self.get_sucursales_usuario(),
            pk=sucursal_id
        )

        inventarios = self.get_inventarios(
            sucursal.id,
            fecha
        )

        formset = InventarioDiarioFormSet(
            request.POST,
            queryset=inventarios
        )

        if formset.is_valid():

            formset.save()

            messages.success(
                request,
                "Inventario actualizado correctamente."
            )

            return redirect(
                "inventario:inventario_detail",
                sucursal_id=sucursal.id,
                fecha=fecha
            )

        return render(
            request,
            self.template_name,
            {
                "formset": formset,
                "sucursal": sucursal,
                "fecha": fecha,
            }
        )