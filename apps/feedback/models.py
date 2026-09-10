# feedback/models.py

from django.conf import settings
from django.db import models


class Feedback(models.Model):


    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedbacks",
    )


    descripcion = models.TextField()

    captura = models.ImageField(
        upload_to="feedback/%Y/%m/",
        blank=True,
        null=True,
    )

    # Contexto automático
    url = models.URLField(
        max_length=500,
        blank=True,
    )

    pagina = models.CharField(
        max_length=200,
        blank=True,
    )


    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.pagina}"