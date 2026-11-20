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
            "comprobante",
          
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



class GastoCajaChicaForm(forms.ModelForm):

    class Meta:
        model = Gasto

        fields = [
            "categoria",
            "descripcion",
            "monto",
            "comprobante",
        ]

        widgets = {
            "descripcion": forms.TextInput(
                attrs={
                    "placeholder": "¿En qué se gastó?",
                }
            ),
            "monto": forms.NumberInput(
                attrs={
                    "min": "0.01",
                    "step": "0.01",
                    "placeholder": "0.00",
                }
            ),
            "comprobante": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*,application/pdf",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["categoria"].queryset = (
            CategoriaGasto.objects.filter(
                activa=True
            ).exclude(
                nombre__iexact="nómina"
            ).order_by("nombre")
        )

        self.fields["descripcion"].required = True

    def clean_monto(self):
        monto = self.cleaned_data["monto"]

        if monto <= 0:
            raise forms.ValidationError(
                "El importe debe ser mayor a cero."
            )

        return monto
