from django import forms
from apps.core.forms import TailwindModelForm
from django.forms import modelformset_factory, formset_factory
from django.core.exceptions import ValidationError
from decimal import Decimal




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








class MovimientoInventarioPOSForm(forms.ModelForm):

    TIPOS_MANUALES = [
        (
            MovimientoInventario.TipoMovimiento.AJUSTE_ENTRADA,
            "Ajuste de entrada (+)",
        ),
        (
            MovimientoInventario.TipoMovimiento.AJUSTE_SALIDA,
            "Ajuste de salida (-)",
        ),
        (
            MovimientoInventario.TipoMovimiento.MERMA,
            "Merma (-)",
        ),
    ]

    tipo = forms.ChoiceField(
        choices=[("", "Selecciona un movimiento")] + TIPOS_MANUALES,
        widget=forms.Select(attrs={
            "class": "w-full rounded-xl border border-gray-300 p-3",
        }),
    )

    class Meta:
        model = MovimientoInventario

        fields = [
            "tipo",
            "variante",
            "cantidad",
            "motivo_merma",
            "observaciones",
        ]

        widgets = {
            "variante": forms.Select(attrs={
                "class": "w-full rounded-xl border border-gray-300 p-3",
            }),
            "cantidad": forms.NumberInput(attrs={
                "class": "w-full rounded-xl border border-gray-300 p-3",
                "min": "0.0001",
                "step": "0.0001",
                "placeholder": "0.0000",
            }),
            "motivo_merma": forms.Select(attrs={
                "class": "w-full rounded-xl border border-gray-300 p-3",
            }),
            "observaciones": forms.Textarea(attrs={
                "class": "w-full rounded-xl border border-gray-300 p-3",
                "rows": 3,
                "placeholder": "Describe el motivo del movimiento",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["variante"].queryset = (
            VarianteProducto.objects
            .filter(
                activo=True,
                producto__activo=True,
            )
            .select_related("producto")
            .order_by("producto__nombre", "nombre")
        )

        self.fields["variante"].empty_label = (
            "Selecciona un producto"
        )

        self.fields["motivo_merma"].required = False

        # Exigimos una justificación para los ajustes y mermas.
        self.fields["observaciones"].required = True

    def clean_tipo(self):
        tipo = self.cleaned_data["tipo"]

        tipos_permitidos = {
            valor for valor, _ in self.TIPOS_MANUALES
        }

        if tipo not in tipos_permitidos:
            raise ValidationError(
                "Este tipo de movimiento no está permitido."
            )

        return tipo

    def clean(self):
        cleaned_data = super().clean()

        tipo = cleaned_data.get("tipo")
        motivo_merma = cleaned_data.get("motivo_merma")

        if tipo == MovimientoInventario.TipoMovimiento.MERMA:
            if not motivo_merma:
                self.add_error(
                    "motivo_merma",
                    "Selecciona el motivo de la merma.",
                )
        else:
            cleaned_data["motivo_merma"] = None

        return cleaned_data




class InventarioInicialAutorizacionForm(forms.Form):
    """Un campo obligatorio por variante; cero es un valor válido."""

    confirmar_corte = forms.BooleanField(
        required=True,
        label="Confirmo que la sucursal está sin ventas ni operaciones pendientes y que las cantidades corresponden al momento de autorizar.",
        error_messages={
            "required": "Debes confirmar el corte antes de autorizar."
        },
    )

    def __init__(self, *args, variantes, **kwargs):
        super().__init__(*args, **kwargs)
        self.variantes = list(variantes)
        self.filas = []

        for variante in self.variantes:
            field_name = f"cantidad_{variante.pk}"
            self.fields[field_name] = forms.DecimalField(
                label="Cantidad física",
                required=True,
                min_value=Decimal("0"),
                max_digits=12,
                decimal_places=4,
                widget=forms.NumberInput(attrs={
                    "min": "0",
                    "step": "0.0001",
                    "inputmode": "decimal",
                    "placeholder": "0.0000",
                    "class": "w-full rounded-xl border border-gray-300 px-3 py-3 text-lg font-semibold focus:border-blue-500 focus:ring-blue-500",
                }),
                error_messages={
                    "required": "Captura la cantidad, aunque sea cero.",
                    "invalid": "Introduce una cantidad numérica válida.",
                },
            )
            self.filas.append({
                "variante": variante,
                "campo": self[field_name],
            })
