from django.urls import path

from .views import (
    ProductoListView,
    ProductoCreateView,
    ProductoUpdateView,
    ProductoDeleteView,
    VarianteProductoListView,
    VarianteProductoCreateView,
    VarianteProductoUpdateView,
    VarianteProductoDeleteView, 
    InventarioDiarioView,
    InventarioDiarioListView,
    InventarioDiarioDetailView,
    InventarioDiarioUpdateView,
    InventarioDiarioCompletadoView,
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

    path(
        "productos/<int:producto_id>/variantes/",
        VarianteProductoListView.as_view(),
        name="variante_list",
    ),

    path(
        "productos/<int:producto_id>/variantes/nueva/",
        VarianteProductoCreateView.as_view(),
        name="variante_create",
    ),

    path(
        "productos/<int:producto_id>/variantes/<int:pk>/editar/",
        VarianteProductoUpdateView.as_view(),
        name="variante_update",
    ),

    path(
        "productos/<int:producto_id>/variantes/<int:pk>/eliminar/",
        VarianteProductoDeleteView.as_view(),
        name="variante_delete",
    ),

    path(
        "inventario-diario/",
        InventarioDiarioView.as_view(),
        name="inventario_diario",
    ),

    path(
        "inventario-diario/historico/",
        InventarioDiarioListView.as_view(),
        name="inventario_list"
    ),

    path(
        "inventario-diario/"
        "<int:sucursal_id>/"
        "<str:fecha>/",
        InventarioDiarioDetailView.as_view(),
        name="inventario_detail"
    ),

    path(
    "inventario-diario/<int:sucursal_id>/<str:fecha>/editar/",
    InventarioDiarioUpdateView.as_view(),
    name="inventario_update",
),


    path("inventario-diario/completado/<int:sucursal_id>/<str:fecha>/",
         InventarioDiarioCompletadoView.as_view(),name="inventario_diario_completado"),












]