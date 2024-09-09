from app.common.viewsets import BaseViewSet
from app.common.permissions import BasicViewPermission
from app.kontresv2.serializers import BookableItemSerializer


class BookableItem(BaseViewSet):
    serializer_class = BookableItemSerializer
    permission_classes = [BasicViewPermission]

    def get_queryset(self):
        return None

    def create(self, request, *args, **kwargs):
        return None

    def update(self, request, *args, **kwargs):
        return None

    def destroy(self, request, *args, **kwargs):
        return None

    def list(self, request, *args, **kwargs):
        return None

    def retrieve(self, request, *args, **kwargs):
        return None
