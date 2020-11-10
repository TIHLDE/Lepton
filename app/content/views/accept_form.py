import os

from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from sentry_sdk import capture_exception


@csrf_exempt
@api_view(["POST"])
def accept_form(request):
    """ Method for accepting company interest forms from the company page """
    try:
        # Get body from request
        body = request.data
        # Define mail content
        sent_from = os.environ.get("EMAIL_USER")
        to = os.environ.get("EMAIL_RECEIVER") or "orakel@tihlde.org"
        subject = (
            body["info"]["bedrift"]
            + " vil ha "
            + ", ".join(body["type"][:-2] + [" og ".join(body["type"][-2:])])
            + " i "
            + ", ".join(body["time"][:-2] + [" og ".join(body["time"][-2:])])
        )
        email_body = """\
            Bedrift-navn:
            %s

            Kontaktperson:
            navn: %s
            epost: %s

            Valgt semester:
            %s

            Valg arrangement:
            %s

            Kommentar:
            %s
        """ % (
            body["info"]["bedrift"],
            body["info"]["kontaktperson"],
            body["info"]["epost"],
            ", ".join(body["time"]),
            ", ".join(body["type"]),
            body["comment"],
        )

        numOfSentMails = send_mail(
            subject, email_body, sent_from, [to], fail_silently=False
        )
        return Response({"detail": ""}, status=200 if numOfSentMails > 0 else 400)

    except Exception as accept_form_fail:
        capture_exception(accept_form_fail)
        raise
