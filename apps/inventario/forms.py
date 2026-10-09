from django import forms
from apps.core.forms import TailwindModelForm
from django.forms import modelformset_factory, formset_factory


from apps.sucursales.models import Sucursal
from .models import Producto, VarianteProducto, InventarioDiario, Receta , MovimientoInventario









class VarianteProductoForm(TailwindModelForm):

    class Meta:
        model = VarianteProducto
        fields = [
            "nombre",
            "precio_venta",
            "activo",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-gray-300 "
                        "px-3 py-2 focus:outline-none focus:ring-2 "
                        "focus:ring-blue-500"
                    ),
                    "placeholder": "Nombre de la variante",
                }
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "rounded border-gray-300 text-blue-600 "
                           "focus:ring-blue-500"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["nombre"].label = "Nombre"
        self.fields["activo"].label = "Activo"


        

class ProductoForm(TailwindModelForm):

    class Meta:

        model = Producto

        fields = [
            "nombre",
            "descripcion",
            "registrar_venta_diaria",
            "activo",
            "tipo",
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





class InventarioDiarioItemForm(forms.ModelForm):
    

    class Meta:
        model = InventarioDiario
        fields = [
            "cantidad",
        ]

        widgets = {
            "cantidad": forms.NumberInput(
                attrs={
                    "class": (
                        "w-28 rounded-lg border border-gray-300 "
                        "px-3 py-2 text-center font-semibold "
                        "focus:outline-none focus:ring-2 "
                        "focus:ring-blue-500"
                    ),
                    "min": "0",
                    "step": "0.0001",
                    "inputmode": "decimal",
                }
            ),
        }



InventarioDiarioFormSet = modelformset_factory(
    InventarioDiario,
    form=InventarioDiarioItemForm,
    extra=0,
)






class CierreInventarioItemForm(forms.Form):

    variante_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    cantidad = forms.DecimalField(
        label="Físico",
        min_value=0,
        max_digits=10,
        decimal_places=4,
        widget=forms.NumberInput(
            attrs={
                "class": (
                    "cantidad-fisica "
                    "w-full "
                    "text-center "
                    "text-xl "
                    "font-bold "
                    "border border-gray-300 "
                    "rounded-xl "
                    "px-3 py-3 "
                    "focus:ring-2 "
                    "focus:ring-blue-500 "
                    "focus:border-blue-500"
                ),
                "min": "0",
                "step": "0.0001",
                "inputmode": "decimal",
                "placeholder": "0",
            }
        ),
    )



CierreInventarioFormSet = formset_factory(
    CierreInventarioItemForm,
    extra=0,
)


#Formulario para el inventario diario, con un campo adicional para mostrar el inventario inicial de cada variante de producto.



class InventarioSucursalForm(forms.Form):

    sucursal = forms.ModelChoiceField(
        queryset=Sucursal.objects.none(),
        empty_label="Selecciona una sucursal",
        widget=forms.Select(
            attrs={
                "class": (
                    "w-full rounded-lg border border-gray-300 "
                    "px-3 py-2 "
                    "focus:outline-none focus:ring-2 "
                    "focus:ring-blue-500"
                )
            }
        )
    )

    def __init__(
        self,
        *args,
        sucursales=None,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.fields[
            "sucursal"
        ].queryset = sucursales



class InventarioCapturaItemForm(forms.Form):

    variante_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    

    cantidad = forms.DecimalField(
        min_value=0,
        max_digits=12,
        decimal_places=4,
        label="Cantidad física",
        widget=forms.NumberInput(
            attrs={
                "class": (
                    "w-28 rounded-lg border border-gray-300 "
                    "px-3 py-2 text-center font-semibold "
                    "focus:outline-none focus:ring-2 "
                    "focus:ring-blue-500"
                ),
                "step": "0.0001",
                "inputmode": "decimal",
                "placeholder": "0",
            }
        )
    )
   

InventarioCapturaFormSet = forms.formset_factory(
    InventarioCapturaItemForm,
    extra=0,
)






class PreparacionForm(forms.Form):

    cantidad = forms.IntegerField(
        label="Cantidad preparada",
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": (
                    "w-full text-center text-4xl font-bold "
                    "border border-gray-300 rounded-2xl "
                    "px-4 py-5 "
                    "focus:ring-2 focus:ring-blue-500 "
                    "focus:border-blue-500"
                ),
                "min": "1",
                "step": "1",
                "inputmode": "numeric",
                "placeholder": "0",
                "autofocus": True,
            }
        ),
    )



class RecepcionMercanciaForm(forms.Form):

    cantidad = forms.DecimalField(
        label="Cantidad recibida",
        min_value=0.0001,
        max_digits=12,
        decimal_places=4,
        widget=forms.NumberInput(
            attrs={
                "class": (
                    "w-full text-center text-4xl font-bold "
                    "border border-gray-300 rounded-2xl "
                    "px-4 py-5 "
                    "focus:ring-2 focus:ring-blue-500 "
                    "focus:border-blue-500"
                ),
                "min": "0.0001",
                "step": "0.0001",
                "inputmode": "decimal",
                "placeholder": "0",
                "autofocus": True,
            }
        ),
    )

    observaciones = forms.CharField(
        label="Observaciones",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": (
                    "w-full border border-gray-300 "
                    "rounded-xl px-4 py-3 "
                    "focus:ring-2 focus:ring-blue-500"
                ),
                "rows": 3,
                "placeholder": (
                    "Opcional. Ej. Entrega semanal"
                ),
            }
        ),
    )


class MermaForm(forms.Form):

    cantidad = forms.DecimalField(
        label="Cantidad perdida",
        min_value=0.0001,
        max_digits=12,
        decimal_places=4,
        widget=forms.NumberInput(
            attrs={
                "class": (
                    "w-full text-center text-4xl font-bold "
                    "border border-gray-300 rounded-2xl "
                    "px-4 py-5 "
                    "focus:ring-2 focus:ring-red-500 "
                    "focus:border-red-500"
                ),
                "min": "0.0001",
                "step": "0.0001",
                "inputmode": "decimal",
                "placeholder": "0",
                "autofocus": True,
            }
        ),
    )

    motivo = forms.ChoiceField(
        label="Motivo",
        choices=MovimientoInventario.MotivoMerma.choices,
        initial=MovimientoInventario.MotivoMerma.ROTO,
        widget=forms.Select(
            attrs={
                "class": (
                    "w-full border border-gray-300 "
                    "rounded-xl px-4 py-3 bg-white"
                )
            }
        ),
    )

    observaciones = forms.CharField(
        label="Observaciones",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": (
                    "w-full border border-gray-300 "
                    "rounded-xl px-4 py-3"
                ),
                "rows": 2,
                "placeholder": "Opcional",
            }
        ),
    )

    def clean(self):

        cleaned_data = super().clean()

        motivo = cleaned_data.get("motivo")
        observaciones = cleaned_data.get("observaciones")

        if (
            motivo == MovimientoInventario.MotivoMerma.OTRO
            and not observaciones
        ):
            self.add_error(
                "observaciones",
                "Describe el motivo de la merma."
            )

        return cleaned_data