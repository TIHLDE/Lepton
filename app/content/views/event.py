from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.response import Response

from app.util import yesterday

from ..filters import EventFilter
from ..models import Event
from ..pagination import BasePagination
from ..permissions import IsNoKorPromo, is_admin_user
from ..serializers import (
    EventAdminSerializer,
    EventCreateAndUpdateSerializer,
    EventSerializer,
)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsNoKorPromo]
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
            return Event.objects.all().order_by("start_date")
        return Event.objects.filter(start_date__gte=yesterday()).order_by("start_date")

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
            return Response(serializer.data)
        except Event.DoesNotExist:
            return Response({"detail": _("Registration not found.")}, status=404)

    def update(self, request, pk):
        """Update the event with the specified pk."""
        try:
            event = Event.objects.get(pk=pk)
            self.check_object_permissions(self.request, event)
            serializer = EventCreateAndUpdateSerializer(
                event, data=request.data, partial=True
            )

            if serializer.is_valid():
                save = serializer.save()
                return Response(
                    {"detail": _("Event successfully updated."), "id": save.id},
                    status=200,
                )
            else:
                return Response({"detail": _("Could not perform update")}, status=400)

        except Event.DoesNotExist:
            return Response({"detail": "Could not find event"}, status=404)

    def create(self, request, *args, **kwargs):
        """Create an event."""
        serializer = EventCreateAndUpdateSerializer(data=request.data)

        if serializer.is_valid():
            save = serializer.save()
            return Response({"detail": "Event created", "id": save.id}, status=201)

        return Response({"detail": serializer.errors}, status=400)
