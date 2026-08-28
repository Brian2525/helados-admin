from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.compras.models import CuentaPorPagar, PagoCuentaPorPagar


class Command(BaseCommand):

    help = "Marca cuentas por pagar como pagadas para pruebas"

    def add_arguments(self, parser):

        parser.add_argument(
            "cantidad",
            type=int,
            help="Cantidad de cuentas a marcar como pagadas"
        )

    def handle(self, *args, **options):

        cantidad = options["cantidad"]

        cuentas = []

        # Obtenemos cuentas y filtramos el estatus en Python
        for cuenta in CuentaPorPagar.objects.all():

            if cuenta.estatus != "pagado":
                cuentas.append(cuenta)

            if len(cuentas) >= cantidad:
                break

        total = 0

        for cuenta in cuentas:

            saldo = cuenta.saldo

            if saldo <= 0:
                continue

            PagoCuentaPorPagar.objects.create(
                cuenta=cuenta,
                programacion=None,
                fecha=timezone.localdate(),
                monto=saldo,
                observaciones="Pago generado automáticamente para pruebas."
            )

            total += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Se marcaron {total} cuentas como pagadas."
            )
        )