from rest_framework import status
from rest_framework.response import Response

import requests
from sentry_sdk import capture_exception

from app.communication.notifier import Notify


def validate_email(
    emails,
    paragraphs,
    title,
    notification_type,
) -> Response | None:
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


def struct_email(
    title: str,
    notification_type: str,
    paragraphs: list[str],
    buttons: list[object],
):
    email = Notify(
        [],
        f"{title}",
        notification_type,
    )

    for paragraph in paragraphs:
        email.add_paragraph(paragraph)

    for button in buttons:
        email.add_link(button["text"], button["link"])

    return email.mail.generate_string()


def struct_attachments(attachments: list[str]) -> list[tuple[str, bytes, str]]:
    email_attachments = []
    for attachment in attachments if attachments else []:
        try:
            if ".blob.core.windows.net" not in attachment:
                continue
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

    return email_attachments
