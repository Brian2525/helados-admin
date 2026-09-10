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




class FiltroCuentasPorPagarForm(forms.Form):
    ESTADOS = [
        ("abiertas", "Abiertas"),
        ("pagadas", "Pagadas"),
        ("pendientes", "Pendientes"),
        ("parciales", "Parciales"),
        ("vencidas", "Vencidas"),
        ("todas", "Todas"),
    ]

    q = forms.CharField(
        required=False,
        max_length=200,
        strip=True,
    )

    categoria = forms.IntegerField(
        required=False,
        min_value=1,
    )

    proveedor = forms.IntegerField(
        required=False,
        min_value=1,
    )

    estado = forms.ChoiceField(
        required=False,
        choices=ESTADOS,
    )

    fecha_desde = forms.DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    fecha_hasta = forms.DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def clean(self):
        cleaned_data = super().clean()

        fecha_desde = cleaned_data.get("fecha_desde")
        fecha_hasta = cleaned_data.get("fecha_hasta")

        if (
            fecha_desde
            and fecha_hasta
            and fecha_desde > fecha_hasta
        ):
            self.add_error(
                "fecha_hasta",
                "La fecha final no puede ser anterior a la inicial.",
            )

        return cleaned_data