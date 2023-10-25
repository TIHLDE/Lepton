from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.kontres.models.bookable_item import BookableItem
from app.kontres.serializer.bookable_item_serializer import (
    BookableItemSerializer,
)


class BookableItemViewSet(BaseViewSet):
    queryset = BookableItem.objects.all()
    serializer_class = BookableItemSerializer
    permission_classes = [BasicViewPermission]
