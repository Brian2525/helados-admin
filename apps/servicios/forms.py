from django import forms
from apps.core.forms import TailwindModelForm


from .models import ServicioRecurrente, PagoServicio


class ServicioRecurrenteForm(TailwindModelForm):

    class Meta:
        model = ServicioRecurrente

        fields = [
            "sucursal",
            "categoria",
            "nombre",
            "proveedor",
            "monto_estimado",
            "dia_pago",
            "activo",
            "observaciones",
        ]

        widgets = {

            "monto_estimado": forms.NumberInput(
                attrs={
                    "step": "0.01"
                }
            ),

            "dia_pago": forms.NumberInput(
                attrs={
                    "min": "1",
                    "max": "31"
                }
            ),

            "observaciones": forms.Textarea(
                attrs={
                    "rows": 3
                }
            )

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
            "servicio": forms.HiddenInput(),
            "fecha_pago": forms.DateInput(
                attrs={"type": "date"}
            ),
        }