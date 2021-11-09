from rest_framework import viewsets

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.content.models.content_request import ContentRequest
from app.content.serializers.content_request import (
    ContentRequestCreateSerializer,
    ContentRequestSerializer,
)


class ContentRequestViewSet(viewsets.ModelViewSet):
    queryset = ContentRequest.objects.all()
    serializer_class = ContentRequestSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def get_serializer_class(self):
        if hasattr(self, "action") and self.action == "create":
            return ContentRequestCreateSerializer
        return super().get_serializer_class()
