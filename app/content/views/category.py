from rest_framework import viewsets

from ..models import Category
from ..permissions import IsNoKorPromo
from ..serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsNoKorPromo]
