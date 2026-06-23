from django import forms

from .models import Empleado


class EmpleadoForm(forms.ModelForm):

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