from django.urls import path

from .views import (
    ProveedorListView,
    ProveedorCreateView,
    ProveedorUpdateView,
    ProveedorDeleteView,
    CuentaPorPagarListView,
    CuentaPorPagarCreateView,
    CuentaPorPagarDeleteView,
    RegistrarPagoCuentaView,
    CuentaPorPagarDetailView,
)

app_name = "compras"

urlpatterns = [

    path(
        "proveedores/",
        ProveedorListView.as_view(),
        name="proveedor_list",
    ),

    path(
        "proveedores/nuevo/",
        ProveedorCreateView.as_view(),
        name="proveedor_create",
    ),

    path(
        "proveedores/<int:pk>/editar/",
        ProveedorUpdateView.as_view(),
        name="proveedor_update",
    ),

    path(
        "proveedores/<int:pk>/eliminar/",
        ProveedorDeleteView.as_view(),
        name="proveedor_delete",
    ),

    path(
    "cuentas/",
    CuentaPorPagarListView.as_view(),
    name="cuenta_list",
    ),

    path(
        "cuentas/nueva/",
        CuentaPorPagarCreateView.as_view(),
        name="cuenta_create",
    ),

    path(
    "cuentas/<int:pk>/",
    CuentaPorPagarDetailView.as_view(),
    name="cuenta_detail",
    ),


    path(
        "cuentas/<int:pk>/eliminar/",
        CuentaPorPagarDeleteView.as_view(),
        name="cuenta_delete",
    ),

    path(
    "cuentas/<int:pk>/pagar/",
    RegistrarPagoCuentaView.as_view(),
    name="cuenta_pagar",
),






]