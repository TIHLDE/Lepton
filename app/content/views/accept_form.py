import os
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view


# TODO: MOVE TO TEMPLATE
from django.core.mail import send_mail


@csrf_exempt
@api_view(['POST'])
def accept_form(request):
    """ Method for accepting company interest forms from the company page """
    try:
        # Get body from request
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        # Define mail content
        sent_from = 'no-reply@tihlde.org'
        to = os.environ.get('EMAIL_RECEIVER') or 'orakel@tihlde.org'
        subject = body["info"]['bedrift'] + " vil ha " + ", ".join(body["type"][:-2] + [" og ".join(body["type"][-2:])]) + " i " + ", ".join(body["time"][:-2] + [" og ".join(body["time"][-2:])])
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
        """ % (body["info"]["bedrift"], body["info"]["kontaktperson"], body["info"]["epost"], ", ".join(body["time"]), ", ".join(body["type"]), body["comment"])

        numOfSentMails = send_mail(
            subject,
            email_body,
            sent_from,
            [to],
            fail_silently = False
        )
        return JsonResponse({}, status= 200 if numOfSentMails > 0 else 500)

    except:
        print('Something went wrong...')
        raise

