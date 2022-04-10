from rest_framework import status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models import Toddel
from app.content.serializers import ToddelSerializer


class ToddelViewSet(BaseViewSet):

    queryset = Toddel.objects.all()
    serializer_class = ToddelSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "Utgaven av Töddel ble slettet"}, status=status.HTTP_200_OK
        )
