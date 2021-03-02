from rest_framework import viewsets

from dry_rest_permissions.generics import DRYPermissions

from app.content.models import Category
from app.content.serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [DRYPermissions]
