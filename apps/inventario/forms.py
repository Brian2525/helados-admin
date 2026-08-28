from django import forms
from apps.core.forms import TailwindModelForm
from django.forms import modelformset_factory

from apps.sucursales.models import Sucursal
from .models import Producto, VarianteProducto, InventarioDiario


class VarianteProductoForm(TailwindModelForm):

    class Meta:
        model = VarianteProducto
        fields = [
            "nombre",
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




class InventarioDiarioFormSet(
    forms.BaseModelFormSet
):

    def add_fields(
        self,
        form,
        index
    ):

        super().add_fields(
            form,
            index
        )

        inventario = form.instance

        fecha = inventario.fecha
        sucursal = inventario.sucursal
        variante = inventario.variante

        inventario_anterior = (
            InventarioDiario.objects
            .filter(
                sucursal=sucursal,
                variante=variante,
                fecha__lt=fecha
            )
            .order_by("-fecha")
            .first()
        )

        cantidad_inicial = (
            inventario_anterior.cantidad
            if inventario_anterior
            else 0
        )

        form.fields[
            "inventario_inicial"
        ].initial = cantidad_inicial





class InventarioDiarioItemForm(forms.ModelForm):

    inventario_inicial = forms.DecimalField(
        required=False,
        disabled=True,
        label="Inventario inicial",
        widget=forms.NumberInput(
            attrs={
                "class": (
                    "w-24 rounded-lg border border-gray-200 "
                    "bg-gray-100 px-3 py-2 text-center "
                    "text-gray-500"
                )
            }
        )
    )

    class Meta:
        model = InventarioDiario
        fields = [
            "cantidad",
        ]

        widgets = {
            "cantidad": forms.NumberInput(
                attrs={
                    "class": (
                        "w-24 rounded-lg border border-gray-300 "
                        "px-3 py-2 text-center "
                        "focus:outline-none focus:ring-2 "
                        "focus:ring-blue-500"
                    ),
                    "min": "0",
                    "step": "0.01",
                }
            ),
        }



InventarioDiarioFormSet = modelformset_factory(
    InventarioDiario,
    form=InventarioDiarioItemForm,
    formset=InventarioDiarioFormSet,
    extra=0,
)






#Inventario diario inicial 


class InventarioDiarioBaseFormSet(
    forms.BaseModelFormSet
):

    def add_fields(
        self,
        form,
        index
    ):

        super().add_fields(
            form,
            index
        )

        inventario = form.instance

        inventario_anterior = (
            InventarioDiario.objects
            .filter(
                sucursal=inventario.sucursal,
                variante=inventario.variante,
                fecha__lt=inventario.fecha
            )
            .order_by("-fecha")
            .first()
        )

        form.fields[
            "inventario_inicial"
        ].initial = (
            inventario_anterior.cantidad
            if inventario_anterior
            else 0
        )


InventarioDiarioFormSet = modelformset_factory(
    InventarioDiario,
    form=InventarioDiarioItemForm,
    formset=InventarioDiarioBaseFormSet,
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