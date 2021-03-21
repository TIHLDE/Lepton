from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from app.common.permissions import IsMember, get_user_id
from app.content.models import ShortLink, User
from app.content.serializers import ShortLinkSerializer


class ShortLinkViewSet(viewsets.ModelViewSet):
    serializer_class = ShortLinkSerializer
    queryset = ShortLink.objects.all()

    def get_queryset(self):
        if hasattr(self, "action") and self.action == "retrieve":
            return self.queryset
        else:
            user = get_object_or_404(User, user_id=get_user_id(self.request))
            return self.queryset.filter(user=user)

    def get_permissions(self):
        if self.request.method in ["POST"]:
            self.permission_classes = [IsMember]
        return super().get_permissions()

    def create(self, request):
        user = get_object_or_404(User, user_id=request.id)
        serializer = ShortLinkSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            try:
                serializer.save(user=user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response(
                    {"detail": "Dette navnet er allerede i bruk"},
                    status=status.HTTP_409_CONFLICT,
                )
            except ValidationError:
                pass
        return Response({"detail": serializer.errors}, status=status.HTTP_409_CONFLICT,)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Linken ble slettet"}, status=status.HTTP_200_OK,)
