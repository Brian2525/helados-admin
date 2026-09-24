# apps/reportes/urls.py

from django.urls import path

from apps.reportes.views import (
    ReporteMensualGenerarView,
    ReporteMensualJSONView,
    ReporteMensualListView,
    ReporteMensualRegenerarView,
)

app_name = "reportes"

urlpatterns = [
    path(
        "mensual/",
        ReporteMensualListView.as_view(),
        name="reporte_mensual_list",
    ),

    path(
        "mensual/generar/",
        ReporteMensualGenerarView.as_view(),
        name="reporte_mensual_generar",
    ),
    path(
        "mensual/<int:pk>/json/",
        ReporteMensualJSONView.as_view(),
        name="reporte_mensual_json",
    ),
    path(
        "mensual/<int:pk>/regenerar/",
        ReporteMensualRegenerarView.as_view(),
        name="reporte_mensual_regenerar",
    ),
]