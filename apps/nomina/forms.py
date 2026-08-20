from django import forms
from apps.core.forms import TailwindModelForm
from .models import Empleado, PagoNomina


class EmpleadoForm(TailwindModelForm):

    class Meta:
        model = Empleado

        fields = [
            "nombre",
            "sucursal",
            "tipo_nomina",
            "puesto",
            "salario_periodo",
            "fecha_ingreso",
            "activo",
        ]

        widgets = {
            "fecha_ingreso": forms.DateInput(
                attrs={"type": "date"}
            )
        }

    

class PagoNominaForm(forms.ModelForm):

    class Meta:

        model = PagoNomina

        fields = [
            "fecha_pago",
            "monto",
            "observaciones",
        ]

        widgets = {
            "fecha_pago": forms.DateInput(
                attrs={"type": "date"}
            ),
            "fecha_inicio": forms.DateInput(
                attrs={"type": "date"}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"type": "date"}
            ),
            "observaciones": forms.Textarea(
                attrs={"rows": 3}
            ),
        }