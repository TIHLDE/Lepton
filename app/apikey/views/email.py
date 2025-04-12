from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.apikey.util import (
    check_api_key,
    struct_attachments,
    struct_email,
    validate_email,
)
from app.communication.notifier import send_html_email


@api_view(["POST"])
@check_api_key
def send(request):
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
        emails = request.data.get("emails")
        paragraphs = request.data.get("paragraphs")
        buttons = request.data.get("buttons") if request.data.get("buttons") else []
        title = request.data.get("title")
        notification_type = request.data.get("notification_type")
        attachments = request.data.get("attachments")

        error = validate_email(
            emails=emails,
            paragraphs=paragraphs,
            title=title,
            notification_type=notification_type,
        )

        if error:
            return error

        email_body = struct_email(
            title=title,
            notification_type=notification_type,
            paragraphs=paragraphs,
            buttons=buttons,
        )

        send_html_email(
            to_mails=emails,
            html=email_body,
            subject=title,
            attachments=struct_attachments(attachments),
        )

        return Response(
            {"detail": f"Det ble sendt ut epost til {(len(emails))} eposter"},
            status=status.HTTP_201_CREATED,
        )
    except Exception:
        return Response(
            {"detail": "Det oppstod en feil under sending av e-post"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
