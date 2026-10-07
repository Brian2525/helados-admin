from django.urls import reverse_lazy
from django.views.generic import (
    DetailView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    )

from .models import ResumenSemanal, VentaDiaria
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.db.models import Prefetch

from .forms import ResumenSemanalForm, VentaDiariaForm, VentaDetalleFormSet, VentaForm
from decimal import Decimal
from apps.sucursales.models import Sucursal
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import SucursalQuerysetMixin, SucursalFormMixin,ModulePermissionMixin, SucursalPermissionMixin, SucursalActivaMixin
from .services import construir_resumen_semanal
from .models import Venta, VentaDetalle
from django.utils import timezone
from apps.inventario.models import VarianteProducto, Producto
from .forms import POSCobroForm
from .services import reporte_ventas_periodo, resumen_ventas_dia, generar_venta_diaria







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



class VentaListView(SucursalPermissionMixin, LoginRequiredMixin, ListView):
    model = Venta
    template_name = "ventas/venta_list.html"
    context_object_name = "ventas"
    paginate_by = 30

    def get_queryset(self):
        sucursales = self.get_sucursales_usuario()

        qs = (
            Venta.objects
            .filter(sucursal__in=sucursales)
            .select_related("sucursal", "usuario")
            .prefetch_related("detalles")
            .order_by("-fecha_hora")
        )

        sucursal_id = self.request.GET.get("sucursal")
        estado = self.request.GET.get("estado")
        fecha = self.request.GET.get("fecha")

        if sucursal_id:
            qs = qs.filter(sucursal_id=sucursal_id)

        if estado:
            qs = qs.filter(estado=estado)

        if fecha:
            qs = qs.filter(fecha_hora__date=fecha)

        return qs


class VentaDetailView(SucursalPermissionMixin, LoginRequiredMixin, DetailView):
    model = Venta
    template_name = "ventas/venta_detail.html"
    context_object_name = "venta"

    def get_queryset(self):
        return (
            Venta.objects
            .filter(sucursal__in=self.get_sucursales_usuario())
            .select_related("sucursal", "usuario")
            .prefetch_related("detalles__variante__producto")
        )


class VentaCreateView(SucursalPermissionMixin, LoginRequiredMixin, View):
    template_name = "ventas/venta_form.html"

    def get(self, request):
        form = VentaForm()
        form.fields["sucursal"].queryset = self.get_sucursales_usuario()
        formset = VentaDetalleFormSet()

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "formset": formset,
                "titulo": "Nueva venta",
            }
        )

    @transaction.atomic
    def post(self, request):
        form = VentaForm(request.POST)
        form.fields["sucursal"].queryset = self.get_sucursales_usuario()
        formset = VentaDetalleFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            venta = form.save(commit=False)
            venta.usuario = request.user
            venta.estado = Venta.EstadoVenta.CONFIRMADA
            venta.subtotal = Decimal("0.00")
            venta.total = Decimal("0.00")
            venta.save()

            formset.instance = venta
            detalles = formset.save()

            venta.recalcular_totales()

            messages.success(
                request,
                "La venta fue registrada correctamente."
            )

            return redirect(
                "ventas:venta_detail",
                pk=venta.pk
            )

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "formset": formset,
                "titulo": "Nueva venta",
            }
        )


class VentaUpdateView(SucursalPermissionMixin, LoginRequiredMixin, View):
    template_name = "ventas/venta_form.html"

    def get_object(self):
        return get_object_or_404(
            Venta.objects.filter(
                sucursal__in=self.get_sucursales_usuario()
            ),
            pk=self.kwargs["pk"]
        )

    def get(self, request, pk):
        venta = self.get_object()

        if venta.estado == Venta.EstadoVenta.ANULADA:
            messages.error(request, "No puedes editar una venta anulada.")
            return redirect("ventas:venta_detail", pk=venta.pk)

        form = VentaForm(instance=venta)
        form.fields["sucursal"].queryset = self.get_sucursales_usuario()
        formset = VentaDetalleFormSet(instance=venta)

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "formset": formset,
                "venta": venta,
                "titulo": "Editar venta",
            }
        )

    @transaction.atomic
    def post(self, request, pk):
        venta = self.get_object()

        if venta.estado == Venta.EstadoVenta.ANULADA:
            messages.error(request, "No puedes editar una venta anulada.")
            return redirect("ventas:venta_detail", pk=venta.pk)

        form = VentaForm(request.POST, instance=venta)
        form.fields["sucursal"].queryset = self.get_sucursales_usuario()
        formset = VentaDetalleFormSet(request.POST, instance=venta)

        if form.is_valid() and formset.is_valid():
            venta = form.save(commit=False)
            venta.save()

            formset.instance = venta
            formset.save()

            venta.recalcular_totales()

            messages.success(
                request,
                "La venta fue actualizada correctamente."
            )

            return redirect("ventas:venta_detail", pk=venta.pk)

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "formset": formset,
                "venta": venta,
                "titulo": "Editar venta",
            }
        )


class VentaAnularView(SucursalPermissionMixin, LoginRequiredMixin, View):
    template_name = "ventas/venta_confirm_anular.html"

    def get_object(self):
        return get_object_or_404(
            Venta.objects.filter(
                sucursal__in=self.get_sucursales_usuario()
            ),
            pk=self.kwargs["pk"]
        )

    def get(self, request, pk):
        venta = self.get_object()

        return render(
            request,
            self.template_name,
            {
                "venta": venta,
            }
        )

    @transaction.atomic
    def post(self, request, pk):
        venta = self.get_object()

        if venta.estado == Venta.EstadoVenta.ANULADA:
            messages.warning(request, "La venta ya estaba anulada.")
            return redirect("ventas:venta_detail", pk=venta.pk)

        venta.estado = Venta.EstadoVenta.ANULADA
        venta.save(update_fields=["estado", "updated_at"])

        messages.success(request, "La venta fue anulada correctamente.")

        return redirect("ventas:venta_detail", pk=venta.pk)




############- POS - PUNTO DE VENTA - #############

class POSNuevaVentaView(LoginRequiredMixin, SucursalPermissionMixin,SucursalActivaMixin,View):

    template_name = "ventas/pos/nueva_venta.html"

    def get_variantes(self):
        return (
            VarianteProducto.objects
            .filter(
                activo=True,
                producto__activo=True,
            )
            .select_related("producto")
            .order_by("nombre")
        )

    def get_productos(self):

        variantes_activas = (
            VarianteProducto.objects
            .filter(
                activo=True,
                producto__activo=True,
                 
            )
            .order_by("nombre")
        )

        productos = (
            Producto.objects
            .filter(
                activo=True,
                registrar_venta_diaria=True,
            )
            .prefetch_related(
                Prefetch(
                    "variantes_producto",
                    queryset=variantes_activas,
                    to_attr="variantes_pos"
                )
            )
            .order_by("nombre")
        )

        return productos

    def get(self, request):

        productos = self.get_productos()

        return render(
            request,
            self.template_name,
            {
                "productos": productos,
                "sucursal_activa": request.sucursal_activa,
                "pos_seccion": "venta",
            }
        )

    def post(self, request):

        # ==========================================
        # SUCURSAL ACTIVA
        # ==========================================

        sucursal = request.sucursal_activa


        # ==========================================
        # PRODUCTOS
        # ==========================================

        variantes = self.get_variantes()

        items = []

        total = Decimal("0.00")


        for variante in variantes:

            cantidad_str = request.POST.get(
                f"cantidad_{variante.id}",
                ""
            ).strip()


            if not cantidad_str:
                continue


            try:

                cantidad = Decimal(
                    cantidad_str
                )

            except Exception:

                continue


            if cantidad <= 0:
                continue


            precio = variante.precio_venta

            subtotal = (
                cantidad * precio
            )

            total += subtotal


            items.append({

                "variante_id":
                    variante.id,

                "producto_nombre":
                    variante.producto.nombre,

                "variante_nombre":
                    variante.nombre,

                "cantidad":
                    str(cantidad),

                "precio_unitario":
                    str(precio),

                "subtotal":
                    str(subtotal),

            })


        if not items:

            messages.error(
                request,
                "Debes capturar al menos un producto."
            )

            return redirect(
                "ventas:pos_nueva_venta"
            )


        # ==========================================
        # VENTA TEMPORAL
        # ==========================================

        request.session["pos_venta"] = {

            "sucursal_id":
                sucursal.id,

            "sucursal_nombre":
                sucursal.nombre,

            "items":
                items,

            "subtotal":
                str(total),

            "total":
                str(total),

        }


        return redirect(
            "ventas:pos_cobro"
        )



class POSCobroView(
    LoginRequiredMixin,
    SucursalPermissionMixin,
    View
):
    template_name = "ventas/pos/cobro.html"

    def get_pos_data(self, request):
        return request.session.get("pos_venta")


    def get(self, request):

        pos_data = self.get_pos_data(request)

        if not pos_data:

            messages.error(
                request,
                "No hay una venta en proceso."
            )

            return redirect(
                "ventas:pos_nueva_venta"
            )

        total = Decimal(
            pos_data["total"]
        )

        form = POSCobroForm(
            total=total
        )

        return render(
            request,
            self.template_name,
            {
                "pos_data": pos_data,
                "total": total,
                "form": form,
            }
        )


    @transaction.atomic
    def post(self, request):

        # ==========================================
        # VENTA TEMPORAL
        # ==========================================

        pos_data = self.get_pos_data(request)

        if not pos_data:

            messages.error(
                request,
                "No hay una venta en proceso."
            )

            return redirect(
                "ventas:pos_nueva_venta"
            )


        total = Decimal(
            pos_data["total"]
        )


        # ==========================================
        # VALIDAR COBRO
        # ==========================================

        form = POSCobroForm(
            request.POST,
            total=total
        )


        if not form.is_valid():

            return render(
                request,
                self.template_name,
                {
                    "pos_data": pos_data,
                    "total": total,
                    "form": form,
                }
            )


        forma_pago = (
            form.cleaned_data["forma_pago"]
        )

        monto_recibido = (
            form.cleaned_data.get(
                "monto_recibido"
            )
            or Decimal("0.00")
        )


        # ==========================================
        # VALIDACIONES DE EFECTIVO
        # ==========================================

        if forma_pago == "efectivo":

            if monto_recibido < total:

                form.add_error(
                    "monto_recibido",
                    "El monto recibido es menor al total."
                )

                return render(
                    request,
                    self.template_name,
                    {
                        "pos_data": pos_data,
                        "total": total,
                        "form": form,
                    }
                )

            cambio = (
                monto_recibido - total
            )

        else:

            monto_recibido = Decimal("0.00")
            cambio = Decimal("0.00")


        # ==========================================
        # SUCURSAL DE LA VENTA
        # ==========================================

        sucursal_id = pos_data.get(
            "sucursal_id"
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
                "La sucursal de esta venta "
                "no está disponible."
            )

            return redirect(
                "ventas:pos_nueva_venta"
            )


        # ==========================================
        # CREAR VENTA
        # ==========================================

        venta = Venta.objects.create(

            sucursal=sucursal,

            usuario=request.user,

            fecha_hora=timezone.now(),

            estado=(
                Venta.EstadoVenta.CONFIRMADA
            ),

            metodo_pago=forma_pago,

            subtotal=total,

            descuento=Decimal("0.00"),

            total=total,

            efectivo=(
                total
                if forma_pago == "efectivo"
                else Decimal("0.00")
            ),

            tarjeta=(
                total
                if forma_pago == "tarjeta"
                else Decimal("0.00")
            ),

            monto_recibido=(
                monto_recibido
                if forma_pago == "efectivo"
                else Decimal("0.00")
            ),

            cambio=cambio,

            observaciones=(
                f"Forma de pago: {forma_pago}"
            ),
        )


        # ==========================================
        # CREAR DETALLES
        # ==========================================

        for item in pos_data["items"]:

            variante = get_object_or_404(
                VarianteProducto,
                pk=item["variante_id"],
                activo=True,
            )


            VentaDetalle.objects.create(

                venta=venta,

                variante=variante,

                producto_nombre=(
                    item["producto_nombre"]
                ),

                variante_nombre=(
                    item["variante_nombre"]
                ),

                cantidad=Decimal(
                    item["cantidad"]
                ),

                precio_unitario=Decimal(
                    item["precio_unitario"]
                ),

                subtotal=Decimal(
                    item["subtotal"]
                ),
            )


        # ==========================================
        # LIMPIAR SESION
        # ==========================================

        request.session.pop(
            "pos_venta",
            None
        )

        request.session.pop(
            "pos_pago",
            None
        )


        # ==========================================
        # ÉXITO
        # ==========================================

        return redirect(
            "ventas:pos_exito",
            venta_id=venta.id
        )


class POSVentaExitosaView(SucursalPermissionMixin, LoginRequiredMixin, View):
    template_name = "ventas/pos/exito.html"

    def get(self, request, venta_id):
        venta = get_object_or_404(
            Venta.objects.filter(
                sucursal__in=self.get_sucursales_usuario()
            ).select_related("sucursal", "usuario"),
            pk=venta_id
        )

        return render(
            request,
            self.template_name,
            {
                "venta": venta,
            }
        )


############ END POS - PUNTO DE VENTA - #############
class POSTransaccionesView(
    LoginRequiredMixin,
    SucursalActivaMixin,
    SucursalPermissionMixin,
    View
):
    template_name = "ventas/pos/transacciones.html"

    def get(self, request):

        sucursal = request.sucursal_activa
        hoy = timezone.localdate()

        ventas = (
            Venta.objects
            .filter(
                sucursal=sucursal,
                fecha_hora__date=hoy,
            )
            .select_related(
                "sucursal",
                "usuario",
            )
            .prefetch_related(
                "detalles",
                "detalles__variante",
            )
            .order_by("-fecha_hora")
        )

        total_hoy = sum(
            (
                venta.total
                for venta in ventas
                if venta.estado == Venta.EstadoVenta.CONFIRMADA
            ),
            Decimal("0.00")
        )

        return render(
            request,
            self.template_name,
            {
                "ventas": ventas,
                "total_hoy": total_hoy,
                "fecha": hoy,
                "sucursal_activa": sucursal,
                "pos_seccion": "transacciones",
            }
        )


class POSMasView(LoginRequiredMixin,SucursalActivaMixin,SucursalPermissionMixin,View):

    template_name = "ventas/pos/mas.html"

    def get(self, request):

        return render(
            request,
            self.template_name,
            {
                "sucursal_activa":
                    request.sucursal_activa,

                "pos_seccion":
                    "mas",
            }
        )






class POSResumenDiaView(LoginRequiredMixin,SucursalActivaMixin,SucursalPermissionMixin,View):

    template_name = "ventas/pos/resumen_dia.html"

    def get(self, request):

        sucursal = request.sucursal_activa

        hoy = timezone.localdate()

        reporte = reporte_ventas_periodo(
            sucursal=sucursal,
            fecha_inicio=hoy,
            fecha_fin=hoy,
        )

        return render(
            request,
            self.template_name,
            {
                "sucursal_activa": sucursal,
                "fecha": hoy,
                "reporte": reporte,
                "pos_seccion": "mas",
            }
        )



class CierreCajaView(
    LoginRequiredMixin,
    SucursalPermissionMixin,
    SucursalActivaMixin,
    TemplateView,
):

    template_name = "ventas/pos/cierre_caja.html"

    def get_fecha(self):
        return timezone.localdate()

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        fecha = self.get_fecha()
        sucursal = self.request.sucursal_activa

        resumen = resumen_ventas_dia(
            sucursal=sucursal,
            fecha=fecha,
        )

        venta_diaria = (
            VentaDiaria.objects
            .filter(
                sucursal=sucursal,
                fecha=fecha,
            )
            .first()
        )

        context["fecha"] = fecha
        context["resumen"] = resumen
        context["venta_diaria"] = venta_diaria

        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        fecha = self.get_fecha()

        venta_diaria, creada = generar_venta_diaria(
            sucursal=request.sucursal_activa,
            usuario=request.user,
            fecha=fecha,
        )

        if creada:

            messages.success(
                request,
                (
                    "Cierre de caja registrado "
                    "correctamente."
                )
            )

        else:

            messages.success(
                request,
                (
                    "Cierre de caja actualizado "
                    "correctamente."
                )
            )

        return redirect(
            "ventas:cierre_caja"
        )


