from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response

from app.codex.filters import CodexEventFilter
from app.codex.mixins import APICodexEventErrorsMixin
from app.codex.models.event import CodexEvent
from app.codex.serializers import (
    CodexEventCreateSerializer,
    CodexEventUpdateSerializer,
    CodexEventListSerializer,
    CodexEventSerializer
) 
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class CodexEventViewSet(APICodexEventErrorsMixin, BaseViewSet):
    serializer_class = CodexEventSerializer
    permission_classes = [BasicViewPermission]
    queryset = CodexEvent.objects.all()
    pagination_class = BasePagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = CodexEventFilter
    search_fields = ["title"]

    def get_serializer_class(self):
        if hasattr(self, "action") and self.action == "list":
            return CodexEventListSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        try:
            event = self.get_object()
            serializer = CodexEventSerializer(
                event, context={"request": request}, many=False
            )
            return Response(serializer.data)
        except CodexEvent.DoesNotExist:
            return Response(
                {"detail": "Fant ikke arrangementet"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = CodexEventCreateSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            event = super().perform_create(serializer)
            serializer = CodexEventSerializer(
                event, context={"request": request}, many=False
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {"detail": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        event = self.get_object()
        serializer = CodexEventUpdateSerializer(
            event, data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            event = super().perform_update(serializer)
            serializer = CodexEventSerializer(
                event, context={"request": request}, many=False
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Arrangementet ble slettet"}, status=status.HTTP_200_OK)
