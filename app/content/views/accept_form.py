from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.communication.notifier import send_html_email
from app.constants import MAIL_NOK_ADS, MAIL_NOK_LEADER
from app.util.mail_creator import MailCreator


@csrf_exempt
@api_view(["POST"])
def accept_form(request):
    """ Method for accepting company interest forms from the company page """
    try:
        body = request.data
        types = [i.lower() for i in body["type"]]
        times = [i.lower() for i in body["time"]]
        to_mail = (
            MAIL_NOK_ADS
            if len(types) == 1 and types[0].lower() == "annonse"
            else MAIL_NOK_LEADER
        )
        title = f"{body['info']['bedrift']} vil ha {', '.join(types[:-1])}{' og ' if len(types) > 1 else ''}{', '.join(types[-1:])}, {', '.join(times[:-1])}{' og ' if len(times) > 1 else ''}{', '.join(times[-1:])}"

        is_success = send_html_email(
            to_mails=[to_mail],
            html=MailCreator(title)
            .add_paragraph(f"Bedrift: {body['info']['bedrift']}")
            .add_paragraph(
                f"Kontaktperson: {body['info']['kontaktperson']}, epost: {body['info']['epost']}"
            )
            .add_paragraph(f"Valgt semester: {', '.join(times)}")
            .add_paragraph(f"Valgt arrangement: {', '.join(types)}")
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
                "detail": f"Ops, det oppsto en feil. Prøv å sende en mail til {MAIL_NOK_LEADER}"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as accept_form_fail:
        capture_exception(accept_form_fail)
        return Response(
            {
                "detail": f"Ops, det oppsto en feil. Prøv å sende en mail til {MAIL_NOK_LEADER}"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
