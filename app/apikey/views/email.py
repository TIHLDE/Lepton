from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import requests
from sentry_sdk import capture_exception

from app.apikey.models.key import ApiKey
from app.apikey.util import is_valid_uuid
from app.communication.enums import UserNotificationSettingType
from app.communication.notifier import Notify, send_html_email


@api_view(["POST"])
def send_email(request):
    """
    Endpoint for sending a notification and email to a list of emails.

    Body should contain:
    - 'emails': A list of emails.
    - 'notification_type': UserNotificationSettingType.
    - 'title': The title of the notification.
    - 'paragraphs': A list of paragraphs to include in the notification.
    - 'buttons': A list of buttons to include in the notification, each button is a object with a text and a link.
    - 'attachments': A list of file urls to include in the notification.

    The header should contain:
    - 'x-api_key': A key for validating access.
    """

    try:
        api_key = request.headers.get("x-api-key")
        if not api_key:
            return Response(
                {"detail": "API nøkkel mangler"},
                status=status.HTTP_403_FORBIDDEN,
            )

        is_valid_api_key = is_valid_uuid(api_key)
        if not is_valid_api_key:
            return Response(
                {"detail": "API nøkkel er ikke riktig format. Den må være UUID"},
                status=status.HTTP_403_FORBIDDEN,
            )

        valid_api_key = ApiKey.objects.filter(key=api_key).first()

        if not valid_api_key:
            return Response(
                {"detail": "Ugyldig API nøkkel"},
                status=status.HTTP_403_FORBIDDEN,
            )

        emails = request.data.get("emails")
        paragraphs = request.data.get("paragraphs")
        buttons = request.data.get("buttons")
        title = request.data.get("title")
        notification_type = request.data.get("notification_type")
        attachments = request.data.get("attachments")

        if not isinstance(emails, list) or not emails:
            return Response(
                {"detail": "En liste med eposter må inkluderes"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(paragraphs, list) or not paragraphs:
            return Response(
                {"detail": "En liste med avsnitt må inkluderes"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not notification_type or not title:
            return Response(
                {"detail": "Notifikasjonstype og tittel må være satt"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = Notify(
            [],
            f"{title}",
            UserNotificationSettingType(notification_type),
        )

        for paragraph in paragraphs:
            email.add_paragraph(paragraph)

        for button in buttons if buttons else []:
            email.add_link(button.get("text"), button.get("link"))

        email_attachments = []
        for attachment in attachments if attachments else []:
            try:
                response = requests.get(attachment)
                response.raise_for_status()
                email_attachments.append(
                    (
                        attachment.split("/")[-1],
                        response.content,
                        response.headers["Content-Type"],
                    )
                )
            except Exception as e:
                capture_exception(e)
                continue

        email_body = email.mail.generate_string()

        send_html_email(
            to_mails=emails,
            html=email_body,
            subject=email.title,
            attachments=email_attachments,
        )

        return Response(
            {"detail": f"Det ble sendt ut epost til {(len(emails))} eposter"},
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return Response(
            {"detail": "Det oppstod en feil under sending av e-post"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
