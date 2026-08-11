from django.urls import path

from .views import (
    ResumenSemanalListView,
    ResumenSemanalCreateView,
    ResumenSemanalUpdateView,
    ResumenSemanalDeleteView,
    VentaDiariaListView,
    VentaDiariaCreateView,
    VentaDiariaUpdateView,
    VentaDiariaDeleteView,
    VentaDiariaCompletadaView,
)

app_name = "ventas"


urlpatterns = [

    path(
        "",
        ResumenSemanalListView.as_view(),
        name="resumen_list"
    ),

    path(
        "nuevo/",
        ResumenSemanalCreateView.as_view(),
        name="resumen_create"
    ),

    path(
        "<int:pk>/editar/",
        ResumenSemanalUpdateView.as_view(),
        name="resumen_update"
    ),

    path(
        "<int:pk>/eliminar/",
        ResumenSemanalDeleteView.as_view(),
        name="resumen_delete"
    ),






    #Ventas diarios que regitran los ingresos de cada sucursal


    
    path(
        "ventas-diarias/",
        VentaDiariaListView.as_view(),
        name="venta_diaria_list",
    ),

    path(
        "ventas-diarias/nueva/",
        VentaDiariaCreateView.as_view(),
        name="venta_diaria_create",
    ),

    #Venta diaria completada

    path("ventas-diarias/completada/", VentaDiariaCompletadaView.as_view(), name="venta_diaria_completada"),




    path(
        "ventas-diarias/<int:pk>/editar/",
        VentaDiariaUpdateView.as_view(),
        name="venta_diaria_update",
    ),

    path(
        "ventas-diarias/<int:pk>/eliminar/",
        VentaDiariaDeleteView.as_view(),
        name="venta_diaria_delete",
    ),


]