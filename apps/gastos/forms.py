from django import forms
from .models import CategoriaGasto, Gasto
from apps.core.forms import TailwindModelForm
from apps.servicios.models import PagoServicio


class CategoriaGastoForm(TailwindModelForm):

    class Meta:
        model = CategoriaGasto
        fields = [
            "nombre",
            "descripcion",
            "activa",
        ]

        widgets = {
            "descripcion": forms.Textarea(
                attrs={
                    "rows": 3
                }
            )
        }






class GastoForm(TailwindModelForm):

    class Meta:
        model = Gasto
        fields = [
            "sucursal",
            "fecha",
            "categoria",
            "monto",
            "descripcion",
          
        ]

        widgets = {
            "descripcion": forms.Textarea(
                attrs={
                    "rows": 3
                }
            ),
            "monto": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01"
                }
            ),
            "fecha": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),
            "sucursal": forms.Select(
                attrs={"class": "form-select"}
            ),
            "categoria": forms.Select(
                attrs={"class": "form-select"}
            ),
        }

class PagoServicioForm(TailwindModelForm):

    class Meta:

        model = PagoServicio

        fields = [
            "servicio",
            "fecha_pago",
            "monto",
            "observaciones",
        ]

        widgets = {

            "fecha_pago": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "observaciones": forms.Textarea(
                attrs={
                    "rows": 3
                }
            )
        }