# apps/reportes/forms.py

from django import forms
from django.contrib.auth.models import User

from apps.sucursales.models import Sucursal


class ReporteMensualGenerarForm(forms.Form):
    anio = forms.IntegerField(
        min_value=2000,
        max_value=2100,
        label="Año",
    )

    mes = forms.IntegerField(
        min_value=1,
        max_value=12,
        label="Mes",
    )

    sucursal = forms.ModelChoiceField(
        queryset=Sucursal.objects.none(),
        required=False,
        empty_label="Todas las sucursales permitidas",
        label="Sucursal",
    )

    propietario = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        required=False,
        label="Propietario",
        help_text="Solo aplica para consolidado cuando el usuario es superusuario.",
    )

    def __init__(self, *args, usuario=None, sucursales_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

        self.fields["sucursal"].queryset = sucursales_qs or Sucursal.objects.none()

        if not usuario or not usuario.is_superuser:
            self.fields.pop("propietario", None)

    def clean(self):
        cleaned_data = super().clean()

        sucursal = cleaned_data.get("sucursal")

        if self.usuario and self.usuario.is_superuser:
            propietario = cleaned_data.get("propietario")

            # Si es consolidado y superuser, debe indicar propietario.
            if sucursal is None and propietario is None:
                self.add_error(
                    "propietario",
                    "Debes seleccionar un propietario para generar un consolidado como superusuario.",
                )

        return cleaned_data





class ReporteMensualFiltroForm(forms.Form):
    anio = forms.IntegerField(
        required=False,
        min_value=2000,
        max_value=2100,
        label="Año",
    )

    mes = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=12,
        label="Mes",
    )

    sucursal = forms.ModelChoiceField(
        queryset=Sucursal.objects.none(),
        required=False,
        empty_label="Todas",
        label="Sucursal",
    )

    consolidado = forms.ChoiceField(
        required=False,
        label="Alcance",
        choices=[
            ("", "Todos"),
            ("si", "Solo consolidados"),
            ("no", "Solo por sucursal"),
        ],
    )

    propietario = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        required=False,
        label="Propietario",
    )

    def __init__(self, *args, usuario=None, sucursales_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

        self.fields["sucursal"].queryset = sucursales_qs or Sucursal.objects.none()

        if not usuario or not usuario.is_superuser:
            self.fields.pop("propietario", None)

    def clean(self):
        cleaned_data = super().clean()

        sucursal = cleaned_data.get("sucursal")
        consolidado = cleaned_data.get("consolidado")

        if sucursal and consolidado == "si":
            self.add_error(
                "consolidado",
                "No puedes filtrar por sucursal específica y consolidado al mismo tiempo.",
            )

        return cleaned_data