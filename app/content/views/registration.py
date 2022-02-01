from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission, is_admin_user
from app.common.viewsets import BaseViewSet
from app.content.exceptions import APIUserAlreadyAttendedEvent
from app.content.mixins import APIRegistrationErrorsMixin
from app.content.models import Event, Registration
from app.content.serializers import RegistrationSerializer


class RegistrationViewSet(APIRegistrationErrorsMixin, BaseViewSet):

    serializer_class = RegistrationSerializer
    permission_classes = [BasicViewPermission]
    lookup_field = "user_id"

    def get_queryset(self):
        event_id = self.kwargs.get("event_id", None)
        return Registration.objects.filter(event__pk=event_id).prefetch_related("user")

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

        registration = super().perform_create(
            serializer, event=event, user=request.user
        )
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

        return super().update(request, *args, **kwargs)

    def _user_has_already_attended_event(self, registration):
        return registration.has_attended and self.request.data["has_attended"]

    def destroy(self, request, *args, **kwargs):
        registration = self.get_object()

        if is_admin_user(request) and self._is_own_registration():
            return self._unregister(registration)

        if is_admin_user(request):
            return self._admin_unregister(registration)

        if self._is_not_own_registration():
            raise PermissionDenied("Du kan kun melde av deg selv")

        return self._unregister(registration)

    def _unregister(self, registration):
        self._log_on_destroy(registration)
        registration.delete()
        return Response(
            {"detail": "Du har blitt meldt av arrangementet"}, status=status.HTTP_200_OK
        )

    def _admin_unregister(self, registration):
        self._log_on_destroy(registration)
        registration.admin_unregister()
        return Response(
            {"detail": "Brukeren har blitt meldt av arrangement"},
            status=status.HTTP_200_OK,
        )
