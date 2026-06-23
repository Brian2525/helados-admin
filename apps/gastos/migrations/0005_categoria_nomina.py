from django.db import migrations


def crear_categoria_nomina(apps, schema_editor):

    CategoriaGasto = apps.get_model(
        "gastos",
        "CategoriaGasto"
    )

    CategoriaGasto.objects.get_or_create(
        nombre="Nómina",
        defaults={
            "descripcion": "Categoría reservada para pagos de nómina",
            "activa": True
        }
    )


class Migration(migrations.Migration):

    dependencies = [
        ("gastos", "0004_gasto_pago_nomina"),
    ]

    operations = [
        migrations.RunPython(
            crear_categoria_nomina
        ),
    ]