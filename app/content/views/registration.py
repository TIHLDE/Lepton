import os
import uuid
from datetime import datetime
from app.payment.tasks import check_if_has_paid

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission, is_admin_user
from app.common.viewsets import BaseViewSet
from app.content.exceptions import APIUserAlreadyAttendedEvent
from app.content.filters.registration import RegistrationFilter
from app.content.mixins import APIRegistrationErrorsMixin
from app.content.models import Event, Registration
from app.content.serializers import RegistrationSerializer
from app.payment.models.order import Order
from app.payment.util.payment_utils import (
    get_new_access_token,
    initiate_payment,
)


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

        # Create order if event is a paid event
        # Check if we have access token
        # If not fetch access token
        # Inlcude payment link in Serializer

        if event.is_paid_event:
            access_token = os.environ.get("PAYMENT_ACCESS_TOKEN")
            expires_at = os.environ.get("PAYMENT_ACCESS_TOKEN_EXPIRES_AT")
            if not access_token or datetime.now() >= datetime.fromtimestamp(expires_at):
                (expires_at, access_token) = get_new_access_token()
                os.environ.update({"PAYMENT_ACCESS_TOKEN": access_token})
                os.environ.update({"PAYMENT_ACCESS_TOKEN_EXPIRES_AT": str(expires_at)})

            paytime = event.paid_information.paytime
            
            # Create Order
            order_id = uuid.uuid4()
            amount = int(event.paid_information.price * 100)
            res = initiate_payment(amount, str(order_id), event.title, access_token)
            payment_link = res["url"]
            order = Order.objects.create(
                order_id=order_id,
                user=request.user,
                event=event,
                payment_link=payment_link,
            )
            order.save()
            
            check_if_has_paid.apply_async(args=(order.order_id, registration.registration_id), countdown=paytime)

            
            # except:
            #     return Response(
            #     {
            #         "detail": "Noe gikk galt med betalingen. Vennligst prøv igjen senere."
            #     },
            #     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            # )

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
