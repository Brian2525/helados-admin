from decimal import Decimal

from django.db.models import (
    Case,
    CharField,
    DecimalField,
    ExpressionWrapper,
    F,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.utils import timezone


def con_resumen_financiero(queryset):
    cero = Decimal("0.00")

    campo_monetario = DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    return (
        queryset
        .annotate(
            total_pagado_db=Coalesce(
                Sum("pagos__monto"),
                Value(cero),
                output_field=campo_monetario,
            ),
        )
        .annotate(
            saldo_db=ExpressionWrapper(
                F("monto_total") - F("total_pagado_db"),
                output_field=campo_monetario,
            ),
        )
        .annotate(
            estado_filtro=Case(
                # Sin saldo pendiente, incluso si hubo sobrepago.
                When(
                    saldo_db__lte=cero,
                    then=Value("pagado"),
                ),

                # Vencido tiene prioridad sobre parcial.
                When(
                    saldo_db__gt=cero,
                    fecha_vencimiento__lt=timezone.localdate(),
                    then=Value("vencido"),
                ),

                # Hay pagos efectivos y todavía existe saldo.
                When(
                    saldo_db__gt=cero,
                    total_pagado_db__gt=cero,
                    then=Value("parcial"),
                ),

                default=Value("pendiente"),
                output_field=CharField(),
            ),
        )
    )