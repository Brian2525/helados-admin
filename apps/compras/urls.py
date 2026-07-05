from django.urls import path

from .views import (
    ProveedorListView,
    ProveedorCreateView,
    ProveedorUpdateView,
    ProveedorDeleteView,
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

]