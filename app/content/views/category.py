from rest_framework import status
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models import Category
from app.content.serializers import CategorySerializer


class CategoryViewSet(BaseViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [BasicViewPermission]

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            { "details": "Kategorien ble slettet" },
            status=status.HTTP_200_OK
        )
