from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response

from app.common.enums import NativeStrikeEnum as StrikeEnum
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.filters.strike import StrikeFilter
from app.content.models import (
    Event,
    Strike,
    User,
    get_strike_description,
    get_strike_strike_size,
)
from app.content.serializers import StrikeSerializer


class StrikeViewSet(BaseViewSet):
    serializer_class = StrikeSerializer
    queryset = Strike.objects.active()
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = StrikeFilter
    search_fields = [
        "user__user_id",
        "user__first_name",
        "user__last_name",
        "user__email",
    ]

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Endepunktet ikke støttet"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )

    def create(self, request):
        if "enum" in request.data:
            enum = request.data["enum"]
            if enum not in StrikeEnum.all():
                return Response(
                    {"detail": "Fant ikke Enum"}, status=status.HTTP_404_NOT_FOUND
                )
            request.data["description"] = get_strike_description(enum)
            request.data["strike_size"] = get_strike_strike_size(enum)

        serializer = StrikeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, user_id=request.data["user_id"])
        if "event_id" in request.data:
            event = get_object_or_404(Event, id=request.data["event_id"])
            super().perform_create(
                serializer, user=user, event=event, creator=request.user
            )
        else:
            super().perform_create(serializer, user=user, creator=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, args, kwargs)
        return Response({"detail": "Prikken ble slettet"}, status=status.HTTP_200_OK)
