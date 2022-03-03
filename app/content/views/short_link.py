from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models import ShortLink, User
from app.content.serializers import ShortLinkSerializer


class ShortLinkViewSet(BaseViewSet):
    serializer_class = ShortLinkSerializer
    queryset = ShortLink.objects.all()
    permission_classes = [BasicViewPermission]

    def get_queryset(self):
        if hasattr(self, "action") and self.action == "retrieve":
            return super().get_queryset()
        user = get_object_or_404(User, user_id=self.request.id)
        return super().get_queryset().filter(user=user)

    def create(self, request):
        user = get_object_or_404(User, user_id=request.id)
        serializer = ShortLinkSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            try:
                super().perform_create(serializer, user=user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response(
                    {"detail": "Dette navnet er allerede i bruk"},
                    status=status.HTTP_409_CONFLICT,
                )
            except ValidationError:
                pass
        return Response(
            {"detail": serializer.errors},
            status=status.HTTP_409_CONFLICT,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "Linken ble slettet"},
            status=status.HTTP_200_OK,
        )
