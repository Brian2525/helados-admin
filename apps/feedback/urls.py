# feedback/urls.py

from django.urls import path

from  apps.feedback import views

app_name = "feedback"

urlpatterns = [
    path(
        "crear/",
        views.crear_feedback,
        name="crear",
    ),
]