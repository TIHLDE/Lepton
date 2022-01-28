import tempfile
import zipfile

from django.contrib.admin.models import LogEntry
from rest_framework.renderers import JSONRenderer

from sentry_sdk import capture_exception

from app.communication.notifier import send_html_email
from app.content.models import Notification
from app.content.serializers import (
    NotificationSerializer,
    RegistrationSerializer,
    ShortLinkSerializer,
    StrikeSerializer,
    UserBadgeSerializer,
    UserSerializer,
)
from app.forms.serializers import SubmissionGDPRSerializer
from app.group.serializers import (
    FineNoUserSerializer,
    MembershipHistorySerializer,
    MembershipSerializer,
)
from app.util.mail_creator import MailCreator


def export_user_data(request, user):
    """
    Finds all data a user is related to, creates a JSON-file for each model with serialized data,
    zips the files into one zipfile and sends the file to the user's email.

    Must be updated whenever a new model with a relation to User is created.

    Returns a boolean indicating whether the email was successfully sent
    """

    try:
        data = {}

        data["bruker"] = UserSerializer(user, context={"request": request}).data

        data["aktivitet"] = LogEntry.objects.filter(user=user).values()

        notifications = NotificationSerializer(
            # Todo: refactor to use `user.notifications`
            Notification.objects.filter(user=user),
            many=True,
            context={"request": request},
        )
        data["varsler"] = notifications.data

        registrations = RegistrationSerializer(
            user.registrations, many=True, context={"request": request}
        )
        data["paameldinger"] = registrations.data

        memberships = MembershipSerializer(
            user.memberships, many=True, context={"request": request}
        )
        data["medlemskap"] = memberships.data

        membership_histories = MembershipHistorySerializer(
            user.membership_histories, many=True, context={"request": request}
        )
        data["tidligere_medlemskap"] = membership_histories.data

        short_links = ShortLinkSerializer(
            user.short_links, many=True, context={"request": request}
        )
        data["korte_linker"] = short_links.data

        user_badges = UserBadgeSerializer(
            user.user_badges, many=True, context={"request": request}
        )
        data["badges"] = user_badges.data

        strikes = StrikeSerializer(
            user.strikes, many=True, context={"request": request}
        )
        data["prikker"] = strikes.data

        fines = FineNoUserSerializer(
            user.fines, many=True, context={"request": request}
        )
        data["boter"] = fines.data

        submissions = SubmissionGDPRSerializer(
            user.submissions, many=True, context={"request": request}
        )
        data["skjema_svar"] = submissions.data

        is_success = False

        with tempfile.NamedTemporaryFile() as tmp:
            with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as archive:
                for model, json in data.items():
                    archive.writestr(f"{model}.json", JSONRenderer().render(json))

            # Reset file pointer
            tmp.seek(0)

            is_success = send_html_email(
                [user.email],
                MailCreator("Dataeksport")
                .add_paragraph(
                    "Vi har samlet alle dataene som er knyttet til din bruker på TIHLDE.org og samlet dem i den vedlagte zip-filen. Dataene ligger kategorisert i hver sin JSON-fil."
                )
                .add_paragraph(
                    "Om noe av innholdet er uklart eller du ønsker med informasjon kan du ta kontakt med Index, kontaktinfo finner du på nettsiden."
                )
                .add_paragraph(
                    "Hvis du ønsker å slette din profil og alle dine brukerdata så kan du gjøre det i profilen din på nettsiden."
                )
                .generate_string(),
                "Dataeksport",
                [("data.zip", tmp.read(), "application/x-zip-compressed",)],
            )

        return is_success
    except Exception as e:
        capture_exception(e)
        return False
