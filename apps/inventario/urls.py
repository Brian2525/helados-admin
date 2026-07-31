from django.urls import path

from .views import (
    ProductoListView,
    ProductoCreateView,
    ProductoUpdateView,
    ProductoDeleteView,
)

app_name = "inventario"


urlpatterns = [

    path(
        "productos/",
        ProductoListView.as_view(),
        name="producto_list",
    ),

    path(
        "productos/nuevo/",
        ProductoCreateView.as_view(),
        name="producto_create",
    ),

    path(
        "productos/<int:pk>/editar/",
        ProductoUpdateView.as_view(),
        name="producto_update",
    ),

    path(
        "productos/<int:pk>/eliminar/",
        ProductoDeleteView.as_view(),
        name="producto_delete",
    ),

]