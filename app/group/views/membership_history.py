from rest_framework import status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.group.models import MembershipHistory
from app.group.serializers import MembershipHistorySerializer


class MembershipHistoryViewSet(BaseViewSet):

    serializer_class = MembershipHistorySerializer
    queryset = MembershipHistory.objects.all()
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def get_queryset(self):
        return super().get_queryset().filter(group__slug=self.kwargs["slug"])

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "Medlemskapshistorikken ble slettet"},
            status=status.HTTP_200_OK,
        )
