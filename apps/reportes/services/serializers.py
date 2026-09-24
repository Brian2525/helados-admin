from datetime import date, datetime, timezone   
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone as django_timezone


TWO_PLACES = Decimal("0.01")


def decimal_to_str(value: Decimal | int | float | None, places: Decimal = TWO_PLACES) -> str | None:
    if value is None:
        return None

    if not isinstance(value, Decimal):
        value = Decimal(str(value))

    value = value.quantize(places, rounding=ROUND_HALF_UP)
    return format(value, "f")


def date_to_str(value: date | None) -> str | None:
    if value is None:
        return None

    return value.isoformat()


def datetime_to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None

    if django_timezone.is_naive(value):
        value = django_timezone.make_aware(value, django_timezone.get_current_timezone())

    value = value.astimezone(timezone.utc)
    iso = value.isoformat()

    if iso.endswith("+00:00"):
        iso = iso.replace("+00:00", "Z")

    return iso


def serialize_value(value):
    if isinstance(value, Decimal):
        return decimal_to_str(value)

    if isinstance(value, datetime):
        return datetime_to_iso(value)

    if isinstance(value, date):
        return date_to_str(value)

    if isinstance(value, dict):
        return {
            key: serialize_value(subvalue)
            for key, subvalue in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            serialize_value(item)
            for item in value
        ]

    return value