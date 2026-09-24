from django.shortcuts import render
# apps/reportes/views.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, ListView



from apps.core.mixins import ModulePermissionMixin, SucursalPermissionMixin
from apps.reportes.forms import ReporteMensualGenerarForm, ReporteMensualFiltroForm
from apps.reportes.models import ReporteMensual
from apps.reportes.services.mensual import generar_reporte_mensual


class ReporteMensualAccessMixin:
    """
    Controla qué reportes guardados puede consultar/regenerar el usuario.

    Regla:
    - superuser: todos
    - propietario: sus reportes
    - usuario asignado a sucursal: solo reportes de esa sucursal
      (NO consolidados ajenos)
    """

    def get_queryset(self):
        qs = ReporteMensual.objects.select_related(
            "propietario",
            "sucursal",
            "generado_por",
        )

        if self.request.user.is_superuser:
            return qs

        return qs.filter(
            Q(propietario=self.request.user) |
            Q(sucursal__usuarios=self.request.user)
        ).distinct()


class ReporteMensualGenerarView(
    LoginRequiredMixin,
    ModulePermissionMixin,
    SucursalPermissionMixin,
    FormView,
):
    template_name = "reportes/reporte_mensual_generar.html"
    form_class = ReporteMensualGenerarForm
    module_permission = "administracion"

    def get_initial(self):
        initial = super().get_initial()

        anio = self.request.GET.get("anio")
        mes = self.request.GET.get("mes")
        sucursal_id = self.request.GET.get("sucursal")

        if anio:
            initial["anio"] = anio
        if mes:
            initial["mes"] = mes
        if sucursal_id:
            initial["sucursal"] = sucursal_id

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        kwargs["sucursales_qs"] = self.get_sucursales_usuario()
        return kwargs

    def form_valid(self, form):
        sucursal = form.cleaned_data.get("sucursal")

        propietario = None
        if "propietario" in form.cleaned_data:
            propietario = form.cleaned_data.get("propietario")

        reporte = generar_reporte_mensual(
            usuario=self.request.user,
            anio=form.cleaned_data["anio"],
            mes=form.cleaned_data["mes"],
            sucursal_id=sucursal.id if sucursal else None,
            propietario_id=propietario.id if propietario else None,
        )

        messages.success(
            self.request,
            "El reporte mensual fue generado/regenerado correctamente.",
        )

        return redirect("reportes:reporte_mensual_json", pk=reporte.pk)


class ReporteMensualRegenerarView(
    LoginRequiredMixin,
    ModulePermissionMixin,
    ReporteMensualAccessMixin,
    View,
):
    module_permission = "administracion"

    def post(self, request, *args, **kwargs):
        reporte = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])

        propietario_id = None
        if request.user.is_superuser and reporte.sucursal_id is None:
            propietario_id = reporte.propietario_id

        reporte_actualizado = generar_reporte_mensual(
            usuario=request.user,
            anio=reporte.anio,
            mes=reporte.mes,
            sucursal_id=reporte.sucursal_id,
            propietario_id=propietario_id,
        )

        messages.success(
            request,
            "El reporte mensual fue regenerado correctamente.",
        )

        return redirect(
            "reportes:reporte_mensual_json",
            pk=reporte_actualizado.pk,
        )

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])


class ReporteMensualJSONView(
    LoginRequiredMixin,
    ModulePermissionMixin,
    ReporteMensualAccessMixin,
    View,
):
    module_permission = "administracion"

    def get(self, request, *args, **kwargs):
        reporte = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])

        return JsonResponse(
            reporte.datos,
            safe=True,
            json_dumps_params={
                "indent": 2,
                "ensure_ascii": False,
            },
        )


class ReporteMensualListView(LoginRequiredMixin,ModulePermissionMixin,ReporteMensualAccessMixin,SucursalPermissionMixin,ListView,):
    model = ReporteMensual
    template_name = "reportes/reporte_mensual_list.html"
    context_object_name = "reportes"
    paginate_by = 20
    module_permission = "administracion"

    def get_filter_form(self):
        if not hasattr(self, "_filter_form"):
            self._filter_form = ReporteMensualFiltroForm(
                data=self.request.GET or None,
                usuario=self.request.user,
                sucursales_qs=self.get_sucursales_usuario(),
            )
        return self._filter_form

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            "propietario",
            "sucursal",
            "generado_por",
        )

        form = self.get_filter_form()

        if form.is_valid():
            anio = form.cleaned_data.get("anio")
            mes = form.cleaned_data.get("mes")
            sucursal = form.cleaned_data.get("sucursal")
            consolidado = form.cleaned_data.get("consolidado")
            propietario = form.cleaned_data.get("propietario")

            if anio:
                qs = qs.filter(anio=anio)

            if mes:
                qs = qs.filter(mes=mes)

            if sucursal:
                qs = qs.filter(sucursal=sucursal)

            if consolidado == "si":
                qs = qs.filter(sucursal__isnull=True)
            elif consolidado == "no":
                qs = qs.filter(sucursal__isnull=False)

            if self.request.user.is_superuser and propietario:
                qs = qs.filter(propietario=propietario)

        return qs.order_by("-anio", "-mes", "sucursal__nombre", "id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.get_filter_form()
        return context



