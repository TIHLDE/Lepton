from datetime import time
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission, IsMember
from app.common.viewsets import BaseViewSet
from app.communication.enums import UserNotificationSettingType
from app.communication.events import (
    EventGiftCardAmountMismatchError,
    send_gift_cards_by_email,
)
from app.communication.notifier import Notify
from app.constants import MAIL_INDEX
from app.content.filters import EventFilter
from app.content.models import Event, User
from app.content.serializers import (
    EventCreateAndUpdateSerializer,
    EventListSerializer,
    EventSerializer,
    EventStatisticsSerializer,
    PublicRegistrationSerializer,
)
from app.group.models.group import Group
from app.util.utils import midday, now, yesterday


class EventViewSet(BaseViewSet, ActionMixin):
    serializer_class = EventSerializer
    permission_classes = [BasicViewPermission]
    queryset = Event.objects.select_related("organizer")
    pagination_class = BasePagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EventFilter
    search_fields = ["title"]

    def get_queryset(self):
        if hasattr(self, "action") and self.action in [
            "list",
            "get_events_where_is_admin",
        ]:
            return self._list_queryset()
        return super().get_queryset()

    def _list_queryset(self):
        midday_yesterday = midday(yesterday())
        midday_today = midday(now())
        time = midday_today if midday_today < now() else midday_yesterday
        if (
            "end_range" in self.request.query_params
            or "start_range" in self.request.query_params
        ):
            return self.queryset
        expired = self.request.query_params.get("expired", "false").lower() == "true"
        if expired:
            return self.queryset.filter(end_date__lt=time).order_by("-start_date")
        return self.queryset.filter(end_date__gte=time)

    def get_serializer_class(self):
        if hasattr(self, "action") and self.action == "list":
            return EventListSerializer
        return super().get_serializer_class()

    def retrieve(self, request, pk):
        """Return detailed information about the event with the specified pk."""
        try:
            event = self.get_object()
            serializer = EventSerializer(
                event, context={"request": request}, many=False
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist as event_not_exist:
            capture_exception(event_not_exist)
            return Response(
                {"detail": "Fant ikke arrangementet"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def update(self, request, pk):
        """Update the event with the specified pk."""
        try:
            event = self.get_object()
            self.check_object_permissions(self.request, event)
            serializer = EventCreateAndUpdateSerializer(
                event, data=request.data, partial=True, context={"request": request}
            )

            if serializer.is_valid():
                event = super().perform_update(serializer)
                serializer = EventSerializer(event, context={"request": request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "Kunne ikke utføre oppdatering av arrangementet"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Event.DoesNotExist as event_not_exist:
            capture_exception(event_not_exist)
            return Response(
                {"detail": "Fant ikke arrangementet"}, status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        if "is_paid_event" in request.data and request.data["is_paid_event"] and "paid_information" not in request.data:
            request.data["paid_information"] = {}
            request.data["paid_information"]["price"] = 0.00
            request.data["paid_information"]["paytime"] = time(second=0)

        serializer = EventCreateAndUpdateSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            event = super().perform_create(serializer)
            serializer = EventSerializer(event, context={"request": request})

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": ("Arrangementet ble slettet")}, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["get", "put"],
        url_path="favorite",
        permission_classes=(IsMember,),
    )
    def user_favorite(self, request, pk, *args, **kwargs):
        event = get_object_or_404(Event, id=pk)

        if request.method == "PUT":
            if request.data["is_favorite"]:
                event.favorite_users.add(request.user)
            else:
                event.favorite_users.remove(request.user)

        return Response(
            {
                "is_favorite": event.favorite_users.filter(
                    user_id=request.user.user_id
                ).exists()
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="public_registrations",
    )
    def get_public_event_registrations(self, request, pk, *args, **kwargs):
        event = get_object_or_404(Event, id=pk)
        registrations = event.get_participants()
        return self.paginate_response(
            data=registrations,
            serializer=PublicRegistrationSerializer,
            context={"request": request},
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="notify",
    )
    def notify_registered_users(self, request, *args, **kwargs):
        try:
            title = request.data["title"]
            message = request.data["message"]
            event = self.get_object()
            self.check_object_permissions(self.request, event)

            users = User.objects.filter(registrations__in=event.get_participants())
            Notify(users, title, UserNotificationSettingType.OTHER).add_paragraph(
                f"Arrangøren av {event.title} har en melding til deg: {message}"
            ).add_event_link(event.pk).send()

            return Response(
                {
                    "detail": "Meldingen ble sendt ut til alle som er påmeldt og har plass på arrangementet"
                },
                status=status.HTTP_200_OK,
            )

        except Event.DoesNotExist as event_not_exist:
            capture_exception(event_not_exist)
            return Response(
                {"detail": "Fant ikke arrangementet"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["get"], url_path="admin")
    def get_events_where_is_admin(self, request, *args, **kwargs):
        if not self.request.user:
            return Response(
                {"detail": "Du har ikke tilgang til å opprette/redigere arrangementer"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if Event.has_write_all_permission(self.request):
            events = self.get_queryset()
        else:
            allowed_organizers = Group.objects.filter(
                memberships__in=self.request.user.memberships_with_events_access
            )
            if allowed_organizers.exists():
                events = self.get_queryset().filter(
                    Q(organizer__in=allowed_organizers) | Q(organizer=None)
                )
            else:
                return Response(
                    {
                        "detail": "Du har ikke tilgang til å opprette/redigere arrangementer"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        return self.paginate_response(
            data=events, serializer=EventListSerializer, context={"request": request}
        )

    @action(detail=True, methods=["get"], url_path="statistics")
    def statistics(self, request, *args, **kwargs):
        event = self.get_object()
        serializer = EventStatisticsSerializer(event, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="mail-gift-cards",
        parser_classes=(
            MultiPartParser,
            FormParser,
        ),
    )
    def mail_gift_cards(self, request, *args, **kwargs):

        event = self.get_object()
        dispatcher = request.user
        files = request.FILES.getlist("file")

        try:
            send_gift_cards_by_email(event, files, dispatcher)
            return Response(
                {
                    "detail": "Gavekortene er sendt! Vi vil sende deg en mer utfyllende oversikt til din epost."
                },
                status=status.HTTP_200_OK,
            )
        except EventGiftCardAmountMismatchError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            capture_exception(e)
            return Response(
                {
                    "detail": f"Noe gikk galt da vi prøvde å sende ut gavekortene. Gi det et nytt forsøk senere eller "
                    f"kontakt Index på {MAIL_INDEX} eller slack."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
