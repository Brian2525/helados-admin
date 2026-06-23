from django.urls import path

from .views import (
    EmpleadoListView,
    EmpleadoCreateView,
    EmpleadoUpdateView,
    EmpleadoDeleteView,
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
]