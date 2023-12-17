import uuid
from datetime import datetime

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.pagination import BasePagination
from app.common.permissions import (
    BasicViewPermission,
    is_admin_group_user,
    is_admin_user,
)
from app.common.viewsets import BaseViewSet
from app.content.exceptions import APIUserAlreadyAttendedEvent
from app.content.filters.registration import RegistrationFilter
from app.content.mixins import APIRegistrationErrorsMixin
from app.content.models import Event, Registration, User
from app.content.serializers import RegistrationSerializer
from app.content.util.event_utils import start_payment_countdown
from app.payment.models.order import Order
from app.payment.views.vipps_callback import vipps_callback


class RegistrationViewSet(APIRegistrationErrorsMixin, BaseViewSet):

    serializer_class = RegistrationSerializer
    permission_classes = [BasicViewPermission]
    lookup_field = "user_id"
    pagination_class = BasePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = RegistrationFilter
    search_fields = ["user__first_name", "user__last_name"]

    def get_queryset(self):
        event_id = self.kwargs.get("event_id", None)
        return Registration.objects.filter(event__pk=event_id).select_related("user")

    def _is_own_registration(self):
        user_id = self.kwargs.get("user_id", None)
        return self.request.id == user_id

    def _is_not_own_registration(self):
        return not self._is_own_registration()

    def create(self, request, *args, **kwargs):
        """Register the current user for the given event."""

        if not request.user.accepts_event_rules:
            return Response(
                {
                    "detail": "Du må akseptere arrangementreglene i profilen din for å melde deg på."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Autofill allow_photo from user to avoid checkbox when registering for event

        request.data["allow_photo"] = request.user.allows_photo_by_default

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        event_id = self.kwargs.get("event_id", None)
        event = Event.objects.get(pk=event_id)

        registration = super().perform_create(
            serializer, event=event, user=request.user
        )

        try:
            start_payment_countdown(event, registration)
        except Exception as countdown_error:
            capture_exception(countdown_error)
            registration.delete()
            return Response(
                {
                    "detail": "Det skjedde en feil med oppstart av betalingsfrist. Påmeldingen ble ikke fullført."
                },
                status=status.HTTP_400_BAD_REQUEST,
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

        if is_admin_group_user(request):
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

    @action(detail=False, methods=["post"], url_path="add")
    def add_registration(self, request, *args, **kwargs):
        """Add registration to event for admins"""

        if not is_admin_group_user(request):
            return Response(
                {
                    "detail": "Du har ikke tillatelse til å opprette en påmelding på dette arrangementet"
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        event_id = self.kwargs.get("event_id", None)
        user_id = request.data["user"]

        event = get_object_or_404(Event, id=event_id)
        user = get_object_or_404(User, user_id=user_id)

        if not user.accepts_event_rules:
            return Response(
                {
                    "detail": "Brukeren må akseptere arrangementreglene i profilen sin først."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if event.user_is_participant(user):
            return Response(
                {"detail": "Brukeren er allerede påmeldt arrangementet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if event.is_paid_event and not event.is_full:
                Order.objects.create(
                    order_id=uuid.uuid4(),
                    user=user,
                    event=event,
                    payment_link=f"https://tihlde.org/arrangementer/{event_id}/",
                    expire_date=datetime.now(),
                    status=OrderStatus.SALE,
                )
        except Exception as e:
            capture_exception(e)
            return Response(
                {
                    "detail": "Det skjedde en feil med opprettelse av betalingsordre. Påmeldingen ble ikke fullført"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["allow_photo"] = user.allows_photo_by_default
        request.data["created_by_admin"] = True

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        registration = super().perform_create(serializer, event=event, user=user)

        registration_serializer = RegistrationSerializer(
            registration, context={"user": registration.user}
        )

        return Response(registration_serializer.data, status=status.HTTP_201_CREATED)
