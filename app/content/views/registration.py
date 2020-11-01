from django.utils.translation import gettext as _
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from app.content.exceptions import APIUserAlreadyAttendedEvent
from app.content.mixins import APIRegistrationErrorsMixin
from app.content.models import Event, Registration
from app.content.permissions import RegistrationPermission, is_admin_user
from app.content.serializers import RegistrationSerializer
from app.util.mailer import send_registration_mail


class RegistrationViewSet(APIRegistrationErrorsMixin, viewsets.ModelViewSet):

    serializer_class = RegistrationSerializer
    permission_classes = [RegistrationPermission]
    lookup_field = "user_id"

    def get_queryset(self):
        event_id = self.kwargs.get("event_id", None)
        return Registration.objects.filter(event__pk=event_id).prefetch_related("user")

    def retrieve(self, request, *args, **kwargs):
        """Return own registration for members and any registration for admins."""
        if self._non_admin_tries_to_access_another_registration():
            raise PermissionDenied(_("Du har ikke tilgang til denne påmeldingen"))

        return super().retrieve(request, *args, **kwargs)

    def _non_admin_tries_to_access_another_registration(self):
        return self._is_not_own_registration() and not is_admin_user(self.request)

    def _is_own_registration(self):
        user_id = self.kwargs.get("user_id", None)
        return self.request.id == user_id

    def _is_not_own_registration(self):
        return not self._is_own_registration()

    def create(self, request, *args, **kwargs):
        """Register the current user for the given event."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event_id = self.kwargs.get("event_id", None)
        event = Event.objects.get(pk=event_id)

        current_user = request.user

        registration = Registration.objects.get_or_create(
            user=current_user, event=event
        )[0]
        registration_serializer = RegistrationSerializer(
            registration, context={"user": registration.user}
        )
        return Response(registration_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        registration = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if self._user_has_already_attended_event(registration):
            # Prevent other registrations from using the same QR-code
            raise APIUserAlreadyAttendedEvent()

        self._send_registration_mail_if_user_has_not_attended(registration)

        return super().update(request, *args, **kwargs)

    def _user_has_already_attended_event(self, registration):
        return registration.has_attended and self.request.data["has_attended"]

    def _send_registration_mail_if_user_has_not_attended(self, registration):
        if not self.request.data.get("has_attended"):
            send_registration_mail(
                self.request.data.get("is_on_wait"),
                registration.event.title,
                [registration.user.email],
            )

    def destroy(self, request, *args, **kwargs):
        registration = self.get_object()
        if is_admin_user(request):
            return self._admin_unregister(registration)

        if self._is_not_own_registration():
            raise PermissionDenied(_("Du kan kun melde av deg selv"))

        return self._unregister(registration)

    def _unregister(self, registration):
        registration.delete()
        return Response(
            {"detail": _("Påmeldingen har blitt slettet")}, status=status.HTTP_200_OK
        )

    def _admin_unregister(self, registration):
        registration.admin_unregister()
        return Response(
            {"detail": _("Påmeldingen har blitt slettet")}, status=status.HTTP_200_OK
        )
