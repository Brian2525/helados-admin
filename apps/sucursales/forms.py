from django import forms
from .models import Sucursal
from apps.core.forms import TailwindModelForm



class SucursalForm(TailwindModelForm):

    class Meta:
        model = Sucursal
        fields = [
            "nombre",
            "direccion",
            "telefono",
            "responsable",
            "fecha_apertura",
            "activa",
            "notas",
        ]

        widgets = {
            "fecha_apertura": forms.DateInput(
                attrs={"type": "date"}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for nombre, field in self.fields.items():

            if nombre == "activa":
                continue

            field.widget.attrs.update({
                "class": (
                    "w-full rounded-lg border border-gray-300 "
                    "bg-gray-50 px-3 py-2 "
                    "focus:outline-none focus:ring-2 "
                    "focus:ring-blue-500 focus:border-blue-500"
                )
            })