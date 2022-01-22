import os

from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.util.mail_creator import MailCreator
from app.communication.notifier import send_html_email


@csrf_exempt
@api_view(["POST"])
def accept_form(request):
    """ Method for accepting company interest forms from the company page """
    try:
        body = request.data
        title = f"{body['info']['bedrift']} vil ha {', '.join(body['type'][:-2])} og {', '.join(body['type'][-2:])} i {', '.join(body['time'][:-2])} og {', '.join(body['time'][-2:])}"
        is_success = send_html_email(
            to_mails=[os.environ.get("EMAIL_RECEIVER") or "orakel@tihlde.org"],
            html=MailCreator(title)
            .add_paragraph(f"Bedrift: {body['info']['bedrift']}")
            .add_paragraph(
                f"Kontaktperson: {body['info']['kontaktperson']}, epost: {body['info']['epost']}"
            )
            .add_paragraph(f"Valgt semester: {', '.join(body['time'])}")
            .add_paragraph(f"Valgt arrangement: {', '.join(body['type'])}")
            .add_paragraph(f"Kommentar: {body['comment']}")
            .generate_string(),
            subject=title,
        )
        
        if is_success:
            return Response(
                {"detail": "Vi har mottatt din forespørsel"}, status=status.HTTP_200_OK
            )

        return Response(
            {
                "detail": "Ops, det oppsto en feil. Prøv å sende en mail til hs@tihlde.org"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as accept_form_fail:
        capture_exception(accept_form_fail)
        return Response(
            {
                "detail": "Ops, det oppsto en feil. Prøv å sende en mail til hs@tihlde.org"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
