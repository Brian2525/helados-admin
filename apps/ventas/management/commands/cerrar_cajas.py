from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from apps.sucursales.models import Sucursal
from apps.ventas.models import VentaDiaria
from django.contrib.auth import get_user_model



# Ajusta el import a la ubicación real de tu servicio
from apps.ventas.services import generar_venta_diaria


class Command(BaseCommand):

    help = "Genera cierres de caja faltantes del día anterior"

    def handle(self, *args, **options):

        fecha = timezone.localdate() - timedelta(days=1)

        User = get_user_model()

        usuario_sistema = User.objects.get(
            username="sistema_cierres"
        )

        sucursales = Sucursal.objects.filter(
            activa=True
        )

        creados = 0
        existentes = 0

        for sucursal in sucursales:

            try:
                venta_diaria, creada = generar_venta_diaria(
                    sucursal=sucursal,
                    usuario=usuario_sistema,
                    fecha=fecha,
                    efectivo_contado=None,
                    tipo_registro=VentaDiaria.TipoRegistro.AUTOMATICO,
                )

                if creada:

                    creados += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Cierre creado: {sucursal.nombre} - {fecha}"
                        )
                    )

                else:

                    existentes += 1

                    self.stdout.write(
                        f"Cierre existente: {sucursal.nombre} - {fecha}"
                    )

            except Exception as error:

                self.stderr.write(
                    self.style.ERROR(
                        f"Error en {sucursal.nombre}: {error}"
                    )
                )

        self.stdout.write(
            f"Cierres creados: {creados} | "
            f"Existentes: {existentes}"
        )