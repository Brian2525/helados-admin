from django.urls import path

from .views import (
    ResumenSemanalListView,
    ResumenSemanalCreateView,
    ResumenSemanalUpdateView,
    ResumenSemanalDeleteView,
)



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

]