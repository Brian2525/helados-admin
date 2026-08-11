from django import forms
from apps.core.forms import TailwindModelForm

from .models import Producto


class ProductoForm(TailwindModelForm):

    class Meta:

        model = Producto

        fields = [
            "nombre",
            "descripcion",
            "proveedor",
            "precio_compra",
            "contenido_pzas",
            "activo",
        ]

        widgets = {
            "descripcion": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        if user and not user.is_superuser:

            self.fields["sucursal"].queryset = (
                self.fields["sucursal"]
                .queryset.filter(
                    usuarios=user
                )
            )