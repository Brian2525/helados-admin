from django.urls import path

from .views import (
    ResumenSemanalListView,
    ResumenSemanalCreateView,
    ResumenSemanalUpdateView,
    ResumenSemanalDeleteView,
    VentaDiariaListView,
    VentaDiariaCreateView,
    VentaDiariaUpdateView,
    VentaDiariaDeleteView,
    VentaDiariaCompletadaView,
    #Ventas 
    VentaAnularView, 
    VentaCreateView, 
    VentaDetailView, 
    VentaListView, 
    VentaUpdateView,
    #POS - Punto de venta
    POSNuevaVentaView,
    POSCobroView,
    POSVentaExitosaView,
    POSMasView,
    POSTransaccionesView,
    POSResumenDiaView,
   
)

app_name = "ventas"


urlpatterns = [

    path("lista",ResumenSemanalListView.as_view(),name="resumen_list"),
    path("nuevo/",ResumenSemanalCreateView.as_view(),name="resumen_create"),
    path("<int:pk>/editar/",ResumenSemanalUpdateView.as_view(),name="resumen_update"),
    path("<int:pk>/eliminar/",ResumenSemanalDeleteView.as_view(),name="resumen_delete"),
    #Ventas diarios que regitran los ingresos de cada sucursal
    path("ventas-diarias/",VentaDiariaListView.as_view(),name="venta_diaria_list",),
    path("ventas-diarias/nueva/",VentaDiariaCreateView.as_view(),name="venta_diaria_create",),
    #Venta diaria completada
    path("ventas-diarias/completada/", VentaDiariaCompletadaView.as_view(), name="venta_diaria_completada"),
    path("ventas-diarias/<int:pk>/editar/",VentaDiariaUpdateView.as_view(),name="venta_diaria_update",),
    path("ventas-diarias/<int:pk>/eliminar/",VentaDiariaDeleteView.as_view(),name="venta_diaria_delete",),

    #Ventas

    path("", VentaListView.as_view(), name="venta_list"),
    path("nueva/", VentaCreateView.as_view(), name="venta_create"),
    path("<int:pk>/", VentaDetailView.as_view(), name="venta_detail"),
    path("<int:pk>/editar/", VentaUpdateView.as_view(), name="venta_update"),
    path("<int:pk>/anular/", VentaAnularView.as_view(), name="venta_anular"),

    #POS 
    path("pos/", POSNuevaVentaView.as_view(), name="pos_nueva_venta"),
    path("pos/cobro/", POSCobroView.as_view(), name="pos_cobro"),
    path("pos/exito/<int:venta_id>/", POSVentaExitosaView.as_view(), name="pos_exito"),
    path("pos/transacciones/",POSTransaccionesView.as_view(),name="pos_transacciones"),
    path("pos/mas/",POSMasView.as_view(),name="pos_mas"),
    path("pos/resumen-dia/",POSResumenDiaView.as_view(),name="pos_resumen_dia"),
    


 

]