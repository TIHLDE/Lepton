from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from rest_framework import status, viewsets
from rest_framework.response import Response

from app.content.models import Event, Registration, User
from app.content.permissions import RegistrationPermission, is_admin_user
from app.content.serializers import RegistrationSerializer
from app.util.mailer import send_registration_mail
from app.util.utils import today


class RegistrationViewSet(viewsets.ModelViewSet):
    """ Administrates registration, waiting lists and attendance for events """

    serializer_class = RegistrationSerializer
    permission_classes = [RegistrationPermission]
    queryset = Registration.objects.all()
    lookup_field = "user_id"

    def get_queryset(self):
        event_id = self.kwargs.get("event_id", None)
        return Registration.objects.filter(event=event_id).prefetch_related("user")

    def list(self, request, event_id):
        """ Returns all registered users for a given events """
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response(
                {"detail": _("Arrangementet eksisterer ikke")},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(self.request, event)
        registration = self.queryset.filter(event__pk=event_id)

        serializer = RegistrationSerializer(
            registration, context={"request": request}, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, event_id, user_id):
        """ Returns a registered user for the specified event """
        if user_id != request.id and not is_admin_user(request):
            return Response(
                {"detail": _("Du har ikke tilgang til denne påmeldingen")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            registration = Registration.objects.get(
                event__pk=event_id, user__user_id=user_id
            )
            serializer = RegistrationSerializer(
                registration, context={"request": request}, many=False
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Registration.DoesNotExist:
            return Response(
                {"detail": _("Kunne ikke finne denne påmeldingen")},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, event_id):
        """ Registers a user with the specified event_id and user_id """
        try:
            event = Event.objects.get(pk=event_id)
            user = User.objects.get(user_id=request.id)
            serializer = RegistrationSerializer(data=request.data)
            if serializer.is_valid():
                registration = Registration.objects.create(user=user, event=event)
                registration.save()
                registration.refresh_from_db()
                registration_serializer = RegistrationSerializer(
                    registration, context={"user": registration.user}
                )
                return Response(
                    registration_serializer.data, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )
        except Event.DoesNotExist:
            return Response(
                {"detail": _("Dette arrangementet eksisterer ikke")},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, event_id, user_id, *args, **kwargs):
        """ Updates fields passed in request """
        try:
            registration = self.get_object()
            self.check_object_permissions(self.request, registration)
            serializer = RegistrationSerializer(
                registration, data=request.data, partial=True, many=False
            )
            if serializer.is_valid():
                if registration.has_attended and request.data["has_attended"]:
                    return Response(
                        {"detail": _("Brukeren har allerede ankommet")},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if not request.data.get("has_attended"):
                    send_registration_mail(
                        request.data.get("is_on_wait"),
                        Event.objects.get(pk=event_id).title,
                        [User.objects.get(user_id=user_id).email],
                    )
                return super().update(request, *args, **kwargs)
            else:
                return Response(
                    {"detail": _("Kunne ikke oppdatere")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Registration.DoesNotExist:
            return Response(
                {"detail": _("Kunne ikke finne påmeldingen")},
                status=status.HTTP_404_NOT_FOUND,
            )

        except ValidationError as e:
            return Response({"detail": _(e.message)}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, event_id, user_id):
        """ Unregisters the user specified with provided event_id and user_id """
        try:
            registration = Registration.objects.get(
                event__pk=event_id, user__user_id=user_id
            )

            if is_admin_user(request):
                super().destroy(registration)
                return Response(
                    {"detail": "Påmelding har blitt slettet"}, status=status.HTTP_200_OK
                )

            event = registration.event
            if event.sign_off_deadline < today():
                return Response(
                    {"detail": "Du kan ikke melde deg av etter avmeldingsfristen"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if request.id == user_id:
                super().destroy(registration)
                return Response(
                    {"detail": "Påmelding har blitt slettet"}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": _("Du kan bare melde deg selv av")},
                    status=status.HTTP_403_FORBIDDEN,
                )

        except Registration.DoesNotExist:
            return Response(
                {"detail": _("Kunne ikke slette arrangement-påmeldingen")},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Event.DoesNotExist:
            return Response(
                {"detail": _("Dette arrangementet eksisterer ikke")},
                status=status.HTTP_404_NOT_FOUND,
            )
