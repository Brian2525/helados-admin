from django import forms
from apps.core.forms import TailwindModelForm
from .models import Empleado


class EmpleadoForm(TailwindModelForm):

    class Meta:
        model = Empleado

        fields = [
            "nombre",
            "sucursal",
            "puesto",
            "sueldo_semanal",
            "fecha_ingreso",
            "activo",
        ]

        widgets = {
            "fecha_ingreso": forms.DateInput(
                attrs={"type": "date"}
            )
        }