
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.nomina.services import generar_nominas




class Command(BaseCommand):

    help = "Genera las nóminas del periodo correspondiente."

    def handle(self, *args, **options):

        hoy = timezone.localdate()
        weekday = hoy.weekday()

        # Miércoles
        if weekday == 2:

            nominas = generar_nominas("SEMANA")

            self.stdout.write(
                self.style.SUCCESS(
                    f"Se generaron {len(nominas)} nóminas SEMANA."
                )
            )

        # Sábado
        elif weekday == 5:

            nominas = generar_nominas("FIN_SEMANA")

            self.stdout.write(
                self.style.SUCCESS(
                    f"Se generaron {len(nominas)} nóminas FIN_SEMANA."
                )
            )

        else:

            self.stdout.write(
                "Hoy no corresponde generar nóminas."
            )