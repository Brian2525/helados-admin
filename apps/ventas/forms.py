from django import forms
from .models import ResumenSemanal


class ResumenSemanalForm(forms.ModelForm):

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