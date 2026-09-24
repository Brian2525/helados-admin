from datetime import date, datetime
from decimal import Decimal

from django.test import SimpleTestCase
from django.utils import timezone

from apps.reportes.services.serializers import (
    date_to_str,
    datetime_to_iso,
    decimal_to_str,
    serialize_value,
)


class SerializersServiceTests(SimpleTestCase):

    def test_decimal_to_str(self):
        self.assertEqual(decimal_to_str(Decimal("123.4")), "123.40")
        self.assertEqual(decimal_to_str(Decimal("8.425")), "8.43")
        self.assertEqual(decimal_to_str(Decimal("0")), "0.00")

    def test_date_to_str(self):
        self.assertEqual(date_to_str(date(2026, 8, 1)), "2026-08-01")

    def test_datetime_to_iso(self):
        dt = timezone.make_aware(datetime(2026, 8, 1, 10, 30, 0))
        value = datetime_to_iso(dt)

        self.assertIn("2026-08-01T", value)
        self.assertTrue(value.endswith("Z"))

    def test_serialize_value(self):
        dt = timezone.make_aware(datetime(2026, 8, 1, 10, 30, 0))

        data = {
            "monto": Decimal("123.45"),
            "fecha": date(2026, 8, 1),
            "datetime": dt,
            "nested": {
                "porcentaje": Decimal("8.425"),
            },
            "items": [Decimal("1.5"), date(2026, 8, 2)],
        }

        serialized = serialize_value(data)

        self.assertEqual(serialized["monto"], "123.45")
        self.assertEqual(serialized["fecha"], "2026-08-01")
        self.assertEqual(serialized["nested"]["porcentaje"], "8.43")
        self.assertEqual(serialized["items"][0], "1.50")
        self.assertEqual(serialized["items"][1], "2026-08-02")
        self.assertTrue(serialized["datetime"].endswith("Z"))