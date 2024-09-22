from rest_framework import status
from rest_framework.response import Response

from app.codex.models.registration import CodexEventRegistration
from app.codex.serializers import (
    RegistrationCreateSerializer,
    RegistrationListSerializer,
)
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class RegistrationViewSet(BaseViewSet):
    serializer_class = RegistrationListSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def get_queryset(self):
        event_id = self.kwargs.get("event_id")
        return CodexEventRegistration.objects.filter(event__pk=event_id).select_related(
            "user"
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            registration = self.get_object()
            serializer = RegistrationListSerializer(
                registration, context={"request": request}, many=False
            )
            return Response(serializer.data)
        except CodexEventRegistration.DoesNotExist:
            return Response(
                {"detail": "Fant ikke påmeldingen for arrangementet"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = RegistrationCreateSerializer(
            data=data, context={"request": request}
        )

        if serializer.is_valid():
            registration = super().perform_create(serializer, user=request.user)
            serializer = RegistrationListSerializer(
                registration, context={"request": request}, many=False
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {"detail": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "Påmeldingen for arrangementet ble slettet"}, status=status.HTTP_200_OK
        )
