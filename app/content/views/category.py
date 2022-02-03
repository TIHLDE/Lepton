from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models import Category
from app.content.serializers import CategorySerializer


class CategoryViewSet(BaseViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [BasicViewPermission]
