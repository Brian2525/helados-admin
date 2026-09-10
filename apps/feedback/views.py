# feedback/views.py

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from  apps.feedback.forms import FeedbackForm 


@login_required
def crear_feedback(request):

    if request.method == "POST":

        form = FeedbackForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            feedback = form.save(commit=False)

            feedback.usuario = request.user

            feedback.url = request.POST.get(
                "url",
                request.META.get("HTTP_REFERER", ""),
            )

            feedback.pagina = request.POST.get(
                "pagina",
                "",
            )

            feedback.navegador = request.META.get(
                "HTTP_USER_AGENT",
                "",
            )


            feedback.save()

            return JsonResponse({
                "success": True,
                "message": "Gracias por ayudarnos a mejorar el sistema.",
            })

        return JsonResponse(
            {
                "success": False,
                "errors": form.errors,
            },
            status=400,
        )

    return JsonResponse(
        {
            "success": False,
            "message": "Método no permitido.",
        },
        status=405,
    )