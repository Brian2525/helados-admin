from django.urls import path

from .views import (
    CategoriaGastoListView,
    CategoriaGastoCreateView,
    CategoriaGastoUpdateView,
    CategoriaGastoDeleteView,
)

app_name = "gastos"

urlpatterns = [

    path(
        "categorias/",
        CategoriaGastoListView.as_view(),
        name="categoria_list"
    ),

    path(
        "categorias/crear/",
        CategoriaGastoCreateView.as_view(),
        name="categoria_create"
    ),

    path(
        "categorias/<int:pk>/editar/",
        CategoriaGastoUpdateView.as_view(),
        name="categoria_update"
    ),

    path(
        "categorias/<int:pk>/eliminar/",
        CategoriaGastoDeleteView.as_view(),
        name="categoria_delete"
    ),

]


from .views import (
    GastoListView,
    GastoCreateView,
    GastoUpdateView,
    GastoDeleteView,
)

urlpatterns += [

    path(
        "",
        GastoListView.as_view(),
        name="list"
    ),

    path(
        "crear/",
        GastoCreateView.as_view(),
        name="create"
    ),

    path(
        "<int:pk>/editar/",
        GastoUpdateView.as_view(),
        name="update"
    ),

    path(
        "<int:pk>/eliminar/",
        GastoDeleteView.as_view(),
        name="delete"
    ),
]