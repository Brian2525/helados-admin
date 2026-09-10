# feedback/forms.py

from django import forms
from apps.core.forms import TailwindModelForm

from apps.feedback.models import Feedback


class FeedbackForm(TailwindModelForm):

    class Meta:
        model = Feedback
        fields = [
            "descripcion",
            "captura",
        ]

        widgets = {
            

            "descripcion": forms.Textarea(
                attrs={
                    "class": "w-full rounded-lg border-gray-300",
                    "rows": 5,
                    "placeholder": (
                        "Describe qué ocurrió y qué esperabas que sucediera..."
                    ),
                }
            ),

            "captura": forms.ClearableFileInput(
                attrs={
                    "class": "w-full"
                }
            ),
        }