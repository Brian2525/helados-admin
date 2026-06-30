from django.urls import reverse_lazy
from datetime import date

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)

from .models import ServicioRecurrente, PagoServicio
from .forms import ServicioRecurrenteForm, PagoServicioForm
from django.contrib.auth.mixins import LoginRequiredMixin


class ServicioRecurrenteListView(LoginRequiredMixin, ListView):
    model = ServicioRecurrente
    template_name = "servicios/list.html"
    context_object_name = "servicios"
    paginate_by = 20

    def get_queryset(self):
        hoy = date.today()

        queryset = super().get_queryset().filter(activo=True)

        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                sucursal__usuarios=self.request.user
            )

        for servicio in queryset:
            servicio.pagado = PagoServicio.objects.filter(
                servicio=servicio,
                fecha_pago__year=hoy.year,
                fecha_pago__month=hoy.month
            ).exists()

            servicio.dias_restantes = servicio.dia_pago - hoy.day

        return queryset


class ServicioRecurrenteCreateView(LoginRequiredMixin, CreateView):

    model = ServicioRecurrente
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )

    form_class = ServicioRecurrenteForm

    template_name = "servicios/form.html"

    success_url = reverse_lazy(
        "servicios:list"
    )


class ServicioRecurrenteUpdateView(LoginRequiredMixin, UpdateView):

    model = ServicioRecurrente
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )

    form_class = ServicioRecurrenteForm

    template_name = "servicios/form.html"

    success_url = reverse_lazy(
        "servicios:list"
    )


class ServicioRecurrenteDeleteView(LoginRequiredMixin, DeleteView):

    model = ServicioRecurrente
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )

    template_name = "servicios/delete.html"

    success_url = reverse_lazy(
        "servicios:list"
    )

class ServiciosPendientesView(LoginRequiredMixin, TemplateView):

    template_name = "servicios/pendientes.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        hoy = date.today()

        servicios = []

        for servicio in ServicioRecurrente.objects.filter(
            activo=True
        ):
            
            pagado = PagoServicio.objects.filter(
            servicio=servicio,
            fecha_pago__year=hoy.year,
            fecha_pago__month=hoy.month,
        ).exists()
            
            if pagado:
                continue

            dias_restantes = servicio.dia_pago - hoy.day

            servicios.append({
                "servicio": servicio,
                "dias_restantes": dias_restantes,
            })

        servicios.sort(
            key=lambda x: x["dias_restantes"]
        )

        context["servicios"] = servicios

        return context


class RegistrarPagoServicioView(LoginRequiredMixin, CreateView):

    model = PagoServicio

    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            sucursal__usuarios=self.request.user
        )

    form_class = PagoServicioForm

    template_name = "servicios/pago_form.html"

    success_url = reverse_lazy(
        "servicios:pendientes"
    )

    def get_initial(self):

        initial = super().get_initial()

        servicio = ServicioRecurrente.objects.get(
            pk=self.kwargs["pk"]
        )

        initial["servicio"] = servicio
        initial["monto"] = servicio.monto_estimado
        initial["fecha_pago"] = date.today()

        return initial