from django.core.management.base import BaseCommand
from faker import Faker
from decimal import Decimal
from datetime import timedelta
from random import choice, randint

from apps.compras.models import CuentaPorPagar, Proveedor
from apps.sucursales.models import Sucursal
from apps.gastos.models import CategoriaGasto


class Command(BaseCommand):

    help = "Genera cuentas por pagar de prueba"

    def add_arguments(self, parser):
        parser.add_argument(
            "cantidad",
            type=int,
            help="Cantidad de cuentas por pagar a generar"
        )

    def handle(self, *args, **options):

        cantidad = options["cantidad"]

        fake = Faker("es_MX")

        proveedores = list(Proveedor.objects.all())
        sucursales = list(Sucursal.objects.all())
        categorias = list(CategoriaGasto.objects.all())

        if not proveedores:
            self.stdout.write(
                self.style.ERROR("No existen proveedores.")
            )
            return

        if not sucursales:
            self.stdout.write(
                self.style.ERROR("No existen sucursales.")
            )
            return

        if not categorias:
            self.stdout.write(
                self.style.ERROR("No existen categorías de gasto.")
            )
            return

        for i in range(cantidad):

            fecha = fake.date_between(
                start_date="-180d",
                end_date="today"
            )

            CuentaPorPagar.objects.create(
                sucursal=choice(sucursales),
                proveedor=choice(proveedores),
                fecha=fecha,
                fecha_vencimiento=fecha + timedelta(
                    days=randint(7, 60)
                ),
                descripcion=fake.sentence(nb_words=5),
                monto_total=Decimal(randint(500, 20000)),
                categoria=choice(categorias),
                observaciones=fake.text(max_nb_chars=100),
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Se generaron {cantidad} cuentas por pagar."
            )
        )