from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.azure_file_handler import AzureFileHandler
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models import QRCode, User
from app.content.serializers.qr_code import (
    QRCodeCreateSerializer,
    QRCodeSerializer,
)


class QRCodeViewSet(BaseViewSet):
    serializer_class = QRCodeSerializer
    queryset = QRCode.objects.all()
    permission_classes = [BasicViewPermission]

    def get_queryset(self):
        if hasattr(self, "action") and self.action == "retrieve":
            return super().get_queryset()
        user = get_object_or_404(User, user_id=self.request.id)
        return super().get_queryset().filter(user=user)

    def create(self, request, *args, **kwargs):
        user = get_object_or_404(User, user_id=request.id)
        data = request.data

        serializer = QRCodeCreateSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            qr_code = super().perform_create(serializer, user=user)
            serializer = QRCodeSerializer(qr_code, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = get_object_or_404(QRCode, id=kwargs["pk"])
            AzureFileHandler(url=instance.image).deleteBlob()
        except Exception as blob_not_found:
            capture_exception(blob_not_found)
            super().destroy(request, *args, **kwargs)
            return Response(
                {
                    "detail": "Kunne ikke finne blob i Azure Storage. QR-koden ble slettet"
                },
                status=status.HTTP_200_OK,
            )

        super().destroy(request, *args, **kwargs)
        return Response({"detail": "QR-koden ble slettet"}, status=status.HTTP_200_OK)
