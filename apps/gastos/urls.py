from django.urls import path

from .views import (
    CategoriaGastoListView,
    CategoriaGastoCreateView,
    CategoriaGastoUpdateView,
    CategoriaGastoDeleteView,
    GastoListView,
    GastoCreateView,
    GastoUpdateView,
    GastoDeleteView,
    CompromisosListView,
    CajaChicaView, 
    ReponerCajaChicaView,
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
    path(
            "compromisos_pago/",
            CompromisosListView.as_view(),
            name="compromisos_pago"
        ),

    path(
        "caja-chica/",
        CajaChicaView.as_view(),
        name="caja_chica",
    ),

    path(
        "caja-chica/reponer/",
        ReponerCajaChicaView.as_view(),
        name="caja_chica_reponer",
    ),

    


]

