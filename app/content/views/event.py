from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.content.filters import EventFilter
from app.content.models import Event
from app.content.serializers import (
    EventCreateAndUpdateSerializer,
    EventListSerializer,
    EventSerializer,
)
from app.util.mail_creator import MailCreator
from app.util.notifier import Notify
from app.util.utils import yesterday


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [BasicViewPermission]
    queryset = Event.objects.filter(start_date__gte=yesterday()).order_by("start_date")
    pagination_class = BasePagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EventFilter
    search_fields = ["title"]

    def get_queryset(self):
        """
            Return all non-expired events by default.
            Filter expired events based on url query parameter.
        """

        if self.kwargs or "expired" in self.request.query_params:
            queryset = Event.objects.all()
        else:
            queryset = Event.objects.filter(start_date__gte=yesterday())

        return queryset.prefetch_related("forms").order_by("start_date")

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
                {"detail": "Fant ikke arrangementet"}, status=status.HTTP_404_NOT_FOUND,
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
                event = serializer.save()
                serializer = EventSerializer(event)
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
        serializer = EventCreateAndUpdateSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            event = serializer.save()
            serializer = EventSerializer(event)
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
        detail=True, methods=["post"], url_path="notify",
    )
    def notifyRegisteredUsers(self, request, *args, **kwargs):
        try:
            title = request.data["title"]
            message = request.data["message"]
            event = self.get_object()
            self.check_object_permissions(self.request, event)

            for registration in event.get_queue():
                Notify(registration.user, title).send_email(
                    MailCreator(title)
                    .add_paragraph(f"Hei {registration.user.first_name}")
                    .add_paragraph(
                        f"Arrangøren av {event.title} har en melding til deg:"
                    )
                    .add_paragraph(message)
                    .add_event_button(event.pk)
                    .generate_string()
                ).send_notification(
                    description=f"Arrangøren av {event.title} har en melding til deg: {message}",
                    link=event.website_url,
                )

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
