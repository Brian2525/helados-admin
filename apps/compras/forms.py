from django import forms
from apps.core.forms import TailwindModelForm

from .models import Proveedor, CuentaPorPagar, PagoCuentaPorPagar


class ProveedorForm(TailwindModelForm):

    class Meta:

        model = Proveedor

        fields = "nombre","descripcion", "telefono", "correo", "direccion", "activo"

        widgets = {

            "nombre": forms.TextInput(
                attrs={
                    "class": "tw-input",
                    "placeholder": "Nombre del proveedor",
                    "autocomplete": "organization"
                }
            ),

            "descripcion": forms.Textarea(
                attrs={
                    "class": "tw-textarea",
                    "rows": 2,
                    "placeholder": "Descripción breve"
                }
            ),

            "telefono": forms.TextInput(
                attrs={
                    "class": "tw-input",
                    "placeholder": "Teléfono",
                    "type": "tel",
                    "autocomplete": "tel"
                }
            ),

            "correo": forms.EmailInput(
                attrs={
                    "class": "tw-input",
                    "placeholder": "Correo electrónico",
                    "autocomplete": "email"
                }
            ),

            "direccion": forms.Textarea(
                attrs={
                    "class": "tw-textarea",
                    "rows": 2,
                    "placeholder": "Dirección"
                }
            ),

            "activo": forms.CheckboxInput(
                attrs={
                    "class": "tw-checkbox",
                }
            ),

        }


class CuentaPorPagarForm(TailwindModelForm):

    meses = forms.IntegerField(
        required=False,
        initial=1,
        min_value=1,
        label="Número de mensualidades",
        help_text="1 = pago único"
    )

    class Meta:

        model = CuentaPorPagar

        fields = [
            "sucursal",
            "proveedor",
            "categoria",
            "fecha",
            "fecha_vencimiento",
            "descripcion",
            "monto_total",
            "observaciones",
        ]

        widgets = {

            "fecha": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "fecha_vencimiento": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "descripcion": forms.TextInput(
                attrs={
                    "placeholder": "Ej. Compra de refrigerador, Amazon, Equipo..."
                }
            ),

            "monto_total": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0"
                }
            ),

            "observaciones": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Notas opcionales..."
                }
            ),

        }

class PagoCuentaForm(TailwindModelForm):


    class Meta:
        model = PagoCuentaPorPagar
        fields = ["fecha", "monto", "observaciones"]

        widgets = {
            "fecha": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full rounded-lg border-gray-300 focus:ring-indigo-500 focus:border-indigo-500",
                }
            ),
            "monto": forms.NumberInput(
                attrs={
                    "class": "w-full rounded-lg border-gray-300 focus:ring-indigo-500 focus:border-indigo-500",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "w-full rounded-lg border-gray-300 focus:ring-indigo-500 focus:border-indigo-500",
                }
            ),
        }


class ProgramacionPagoForm(forms.Form):

    meses = forms.IntegerField(
        min_value=2,
        max_value=60,
        initial=3,
        label="Número de mensualidades"
    )