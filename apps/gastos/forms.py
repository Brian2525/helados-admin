from django import forms
from .models import CategoriaGasto, Gasto
from apps.servicios.models import PagoServicio


class CategoriaGastoForm(forms.ModelForm):

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






class GastoForm(forms.ModelForm):

    class Meta:
        model = Gasto
        fields = [
            "sucursal",
            "fecha",
            "categoria",
            "monto",
          
        ]

        widgets = {
           
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

class PagoServicioForm(forms.ModelForm):

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