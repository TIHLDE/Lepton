from rest_framework import viewsets

from app.common.permissions import IsNoKorPromo
from app.content.models import Category
from app.content.serializers import CategorySerializer
from dry_rest_permissions.generics import DRYPermissions


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [DRYPermissions]
