from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def inicio(request):

    user = request.user

    if user.is_superuser:
        return redirect("dashboard:home")

    perfil = user.perfil

    if perfil.ventas:
        return redirect(
            "ventas:venta_diaria_create"
        )

    if perfil.gastos:
        return redirect(
            "gastos:create"
        )

    if perfil.inventario:
        return redirect(
            "inventario:producto_list"
        )

    if perfil.nomina:
        return redirect(
            "nomina:historial"
        )

    return redirect("dashboard:home")
# Create your views here.
