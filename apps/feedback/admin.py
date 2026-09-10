# feedback/admin.py

from django.contrib import admin

from apps.feedback.models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "pagina",
        "usuario",
        "fecha_creacion",
    )

    list_filter = (
        "fecha_creacion",
    )

    search_fields = (
        "descripcion",
        "pagina",
        "usuario__username",
    )

    readonly_fields = (
        "usuario",
       
        "url",
        "fecha_creacion",
        "fecha_actualizacion",
    )

    fieldsets = (

        (
            "Fechas",
            {
                "fields": (
                    "usuario",
                    "descripcion",
                    "pagina",
                    "captura",
                    "fecha_creacion",
                    "fecha_actualizacion",
                )
            },
        ),
    )