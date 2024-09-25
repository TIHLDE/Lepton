from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.communication.enums import UserNotificationSettingType
from app.communication.notifier import Notify
from app.content.models import User

# Temporary fake api key, will be changed to a proper api key in prod
API_KEY = "your_api_key"


@api_view(["POST"])
def send_email(request):
    """
    Endpoint for sending a notification and email to a user.

    Body should contain:
    - 'user_id': The ID of the user to notify.
    - 'notification_type': KONTRES or BLITZED.
    - 'title': The title of the notification.
    - 'paragraphs': A list of paragraphs to include in the notification.

    The header should contain:
    - 'api_key': A key for validating access.

    """
    try:
        # Validate API key
        api_key = request.META.get("EMAIL_API_KEY")
        if api_key != API_KEY:
            return Response(
                {"detail": "Invalid API key"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Validate request data
        user_id = request.data.get("user_id")
        paragraphs = request.data.get("paragraphs")
        title = request.data.get("title")
        notification_type = request.data.get("notification_type")

        if not user_id or not notification_type or not paragraphs or not title:
            return Response(
                {
                    "detail": "user_id, event_id, paragraphs and title are required fields."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        email = Notify(
            [user],
            f"{title}",
            UserNotificationSettingType(notification_type),
        ).add_paragraph(f"Hei, {user.first_name}!")

        for paragraph in paragraphs:
            email.add_paragraph(paragraph)

        email.send()
        return Response(
            {"detail": "Email sent successfully."},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"detail": f"An unknown error {e} has occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
