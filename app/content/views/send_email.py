import os

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.communication.enums import UserNotificationSettingType
from app.communication.notifier import Notify
from app.content.models import User


@api_view(["POST"])
def send_email(request):
    """
    Endpoint for sending a notification and email to a user.

    Body should contain:
    - 'user_id_list': A list of user ids to send the email to.
    - 'notification_type': KONTRES or BLITZED.
    - 'title': The title of the notification.
    - 'paragraphs': A list of paragraphs to include in the notification.

    The header should contain:
    - 'api_key': A key for validating access.

    """
    try:
        EMAIL_API_KEY = os.environ.get("EMAIL_API_KEY")
        api_key = request.META.get("api_key")
        if api_key != EMAIL_API_KEY:
            return Response(
                {"detail": "Feil API nøkkel"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_id_list = request.data.get("user_id_list")
        paragraphs = request.data.get("paragraphs")
        title = request.data.get("title")
        notification_type = request.data.get("notification_type")

        if not isinstance(user_id_list, list) or not user_id_list:
            return Response(
                {"detail": "En ikke-tom liste med bruker id-er må inkluderes"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(paragraphs, list) or not paragraphs:
            return Response(
                {"detail": "En ikke-tom liste med paragrafer må inkluderes"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not notification_type or not title:
            return Response(
                {
                    "detail": "Notifikasjonstype (KONTRES/BLITZED) og tittel må være satt"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        users = list(User.objects.filter(user_id__in=user_id_list))
        if not users or len(users) != len(user_id_list):
            return Response(
                {"detail": "En eller flere brukere ble ikke funnet"},
                status=status.HTTP_404_NOT_FOUND,
            )

        email = Notify(
            users,
            f"{title}",
            UserNotificationSettingType(notification_type),
        )

        for paragraph in paragraphs:
            email.add_paragraph(paragraph)

        email.send()
        return Response({"detail": "Emailen ble sendt"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
        return Response(
            {"detail": "Det oppsto en feil under sending av email"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
