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


class ServicioRecurrenteListView(ListView):

    model = ServicioRecurrente

    template_name = "servicios/list.html"

    context_object_name = "servicios"

    paginate_by = 20


class ServicioRecurrenteCreateView(CreateView):

    model = ServicioRecurrente

    form_class = ServicioRecurrenteForm

    template_name = "servicios/form.html"

    success_url = reverse_lazy(
        "servicios:list"
    )


class ServicioRecurrenteUpdateView(UpdateView):

    model = ServicioRecurrente

    form_class = ServicioRecurrenteForm

    template_name = "servicios/form.html"

    success_url = reverse_lazy(
        "servicios:list"
    )


class ServicioRecurrenteDeleteView(DeleteView):

    model = ServicioRecurrente

    template_name = "servicios/delete.html"

    success_url = reverse_lazy(
        "servicios:list"
    )

class ServiciosPendientesView(TemplateView):

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


class RegistrarPagoServicioView(CreateView):

    model = PagoServicio

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