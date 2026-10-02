from django import forms
from .models import ResumenSemanal, VentaDiaria, Venta, VentaDetalle
from django.forms import inlineformset_factory
from apps.inventario.models import VarianteProducto

from django.utils import timezone
from decimal import Decimal 


from apps.core.forms import TailwindModelForm


class ResumenSemanalForm(TailwindModelForm):

    class Meta:
        model = ResumenSemanal
        fields = [
            "sucursal",
            "fecha_inicio",
            "fecha_fin",
            "efectivo",
            "tarjeta",
            "observaciones",
        ]

        widgets = {
            "fecha_inicio": forms.DateInput(
                attrs={"type": "date"}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"type": "date"}
            ),
            "observaciones": forms.Textarea(
                attrs={"rows": 4}
            ),
        }
    
    def clean(self):

        cleaned_data = super().clean()

        sucursal = cleaned_data.get("sucursal")
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if fecha_inicio and fecha_fin:

            if fecha_fin < fecha_inicio:

                raise forms.ValidationError(
                    "La fecha final no puede ser menor a la fecha inicial."
                )
            
        if sucursal and fecha_inicio and fecha_fin:

            traslape = ResumenSemanal.objects.filter(
                sucursal=sucursal
            ).filter(
                fecha_inicio__lte=fecha_fin,
                fecha_fin__gte=fecha_inicio
            )

            if self.instance.pk:
                traslape = traslape.exclude(pk=self.instance.pk)

            if traslape.exists():

                raise forms.ValidationError(
                    "Ya existe un resumen para esa sucursal en ese rango de fechas."
                )


        return cleaned_data




class VentaDiariaForm(TailwindModelForm):

    class Meta:
        model = VentaDiaria
        fields = [
            "sucursal",
            "fecha",
            "efectivo",
            "tarjeta",
            "observaciones",
        ]

        widgets = {
            "fecha": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Solo para registros nuevos
        if not self.instance.pk:
            self.fields["fecha"].initial = timezone.now().date()




class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = [
            "sucursal",
            "fecha_hora",
            "descuento",
            "efectivo",
            "tarjeta",
            "observaciones",
        ]
        widgets = {
            "fecha_hora": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "observaciones": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        efectivo = cleaned_data.get("efectivo") or 0
        tarjeta = cleaned_data.get("tarjeta") or 0

        if efectivo == 0 and tarjeta == 0:
            raise forms.ValidationError(
                "Debes registrar al menos un monto de pago."
            )

        return cleaned_data


class VentaDetalleForm(forms.ModelForm):
    class Meta:
        model = VentaDetalle
        fields = [
            "variante",
            "cantidad",
            "precio_unitario",
        ]

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


VentaDetalleFormSet = inlineformset_factory(
    Venta,
    VentaDetalle,
    form=VentaDetalleForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)




class POSCobroForm(forms.Form):
    FORMA_PAGO_CHOICES = [
        ("efectivo", "Efectivo"),
        ("tarjeta", "Tarjeta"),
        ("otro", "Otro"),
    ]

    forma_pago = forms.ChoiceField(
        choices=FORMA_PAGO_CHOICES,
        widget=forms.RadioSelect
    )

    monto_recibido = forms.DecimalField(
        required=False,
        min_value=Decimal("0.00"),
        decimal_places=2,
        max_digits=12
    )

    def __init__(self, *args, total=None, **kwargs):
        self.total = total or Decimal("0.00")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        forma_pago = cleaned_data.get("forma_pago")
        monto_recibido = cleaned_data.get("monto_recibido")

        if forma_pago == "efectivo":
            if monto_recibido is None:
                raise forms.ValidationError(
                    "Debes indicar el monto recibido en efectivo."
                )
            if monto_recibido < self.total:
                raise forms.ValidationError(
                    "El monto recibido no puede ser menor al total."
                )

        return cleaned_data



