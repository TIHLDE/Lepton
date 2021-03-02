from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.pagination import BasePagination
from app.common.permissions import IsNoKorPromo, is_admin_user
from app.content.filters import EventFilter
from app.content.models import Event
from app.content.serializers import (
    EventAdminSerializer,
    EventCreateAndUpdateSerializer,
    EventListSerializer,
    EventSerializer,
)
from app.util.utils import yesterday
from dry_rest_permissions.generics import DRYPermissions


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [DRYPermissions]
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
            event = Event.objects.get(pk=pk)
            if is_admin_user(request):
                serializer = EventAdminSerializer(
                    event, context={"request": request}, many=False
                )
            else:
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
            event = Event.objects.get(pk=pk)
            self.check_object_permissions(self.request, event)
            serializer = EventCreateAndUpdateSerializer(
                event, data=request.data, partial=True
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
        """Create an event."""
        serializer = EventCreateAndUpdateSerializer(data=request.data)

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
