from django.urls import path

from .views import (
    ServicioRecurrenteListView,
    ServicioRecurrenteCreateView,
    ServicioRecurrenteUpdateView,
    ServicioRecurrenteDeleteView,
    ServiciosPendientesView,
    RegistrarPagoServicioView,
)

app_name = "servicios"

urlpatterns = [

    path(
        "",
        ServicioRecurrenteListView.as_view(),
        name="list"
    ),

    path(
        "crear/",
        ServicioRecurrenteCreateView.as_view(),
        name="create"
    ),

    path(
        "<int:pk>/editar/",
        ServicioRecurrenteUpdateView.as_view(),
        name="update"
    ),

    path(
        "<int:pk>/eliminar/",
        ServicioRecurrenteDeleteView.as_view(),
        name="delete"
    ),
    
    path("pendientes/", ServiciosPendientesView.as_view(), name="pendientes"),

    path(
    "pagar/<int:pk>/",
    RegistrarPagoServicioView.as_view(),
    name="registrar_pago"
),

]