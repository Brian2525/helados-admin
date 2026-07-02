from django.urls import path

from .views import (
    EmpleadoListView,
    EmpleadoCreateView,
    EmpleadoUpdateView,
    EmpleadoDeleteView,
    NominaPendienteListView,
    PagoNominaListView,
    registrar_todos,
    registrar_pago,
)

app_name = "nomina"

urlpatterns = [

    path(
        "empleados/",
        EmpleadoListView.as_view(),
        name="empleado_list"
    ),

    path(
        "empleados/nuevo/",
        EmpleadoCreateView.as_view(),
        name="empleado_create"
    ),

    path(
        "empleados/<int:pk>/editar/",
        EmpleadoUpdateView.as_view(),
        name="empleado_update"
    ),

    path(
        "empleados/<int:pk>/eliminar/",
        EmpleadoDeleteView.as_view(),
        name="empleado_delete"
    ),

    path(
        "",
        NominaPendienteListView.as_view(),
        name="pendientes"
    ),

    path(
        "historial/",
        PagoNominaListView.as_view(),
        name="historial"
    ),

    path(
        "pagar/<int:empleado_id>/",
        registrar_pago,
        name="pagar"
    ),

    path(
        "pagar-todo/",
        registrar_todos,
        name="pagar_todo"
    ),
]
