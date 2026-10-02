from django.urls import path

from .views import (
    SucursalListView,
    SucursalCreateView,
    SucursalUpdateView,
    SucursalDeleteView,
    SeleccionarSucursalView,
    ConfirmarCambioSucursalView
)

app_name = "sucursales"

urlpatterns = [
    path( "",SucursalListView.as_view(),name="list"),

    path("crear/",SucursalCreateView.as_view(),name="create"),

    path("<int:pk>/editar/",SucursalUpdateView.as_view(),name="update"),

    path("<int:pk>/eliminar/",SucursalDeleteView.as_view(),name="delete"),
       #sucursales 
    path("seleccionar/",SeleccionarSucursalView.as_view(),name="seleccionar_sucursal"),
    path("cambiar/",ConfirmarCambioSucursalView.as_view(),name="confirmar_cambio_sucursal"),
    
    
]