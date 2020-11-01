from rest_framework import viewsets

from app.content.models import Category
from app.content.permissions import IsNoKorPromo
from app.content.serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsNoKorPromo]
