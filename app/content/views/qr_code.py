from rest_framework import status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models import QRCode
from app.content.serializers.qr_code import (
    QRCodeCreateSerializer,
    QRCodeSerializer,
)


class QRCodeViewSet(BaseViewSet):
    serializer_class = QRCodeSerializer
    queryset = QRCode.objects.all()
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def get_queryset(self):
        if hasattr(self, "action") and self.action == "retrieve":
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        serializer = QRCodeCreateSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            qr_code = super().perform_create(serializer, user=user)
            serializer = QRCodeSerializer(qr_code, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({"detail": "QR-koden ble oppdatert"}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "QR-koden ble slettet"}, status=status.HTTP_200_OK)
