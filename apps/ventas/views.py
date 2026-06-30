from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import ResumenSemanal
from .forms import ResumenSemanalForm
from django.contrib.auth.mixins import LoginRequiredMixin


class ResumenSemanalListView(LoginRequiredMixin,ListView):
    model = ResumenSemanal
    template_name = "ventas/list.html"
    context_object_name = "resumenes"


class ResumenSemanalCreateView(LoginRequiredMixin, CreateView):
    model = ResumenSemanal
    form_class = ResumenSemanalForm
    template_name = "ventas/create.html"
    success_url = reverse_lazy("resumen_list")


class ResumenSemanalUpdateView(LoginRequiredMixin, UpdateView):
    model = ResumenSemanal
    form_class = ResumenSemanalForm
    template_name = "ventas/update.html"
    success_url = reverse_lazy("resumen_list")


class ResumenSemanalDeleteView(LoginRequiredMixin, DeleteView):
    model = ResumenSemanal
    template_name = "ventas/delete.html"
    success_url = reverse_lazy("resumen_list")