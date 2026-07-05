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
                    "type": "date"
                }
            ),

            "fecha_vencimiento": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "observaciones": forms.Textarea(
                attrs={
                    "rows": 3
                }
            ),

        }

class PagoCuentaForm(TailwindModelForm):

    class Meta:

        model = PagoCuentaPorPagar

        fields = [

            "fecha",

            "monto",

            "observaciones",

        ]