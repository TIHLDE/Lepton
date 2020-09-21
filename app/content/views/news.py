from rest_framework import viewsets

from ..models import News
from ..permissions import IsDev, IsNoK
from ..serializers import NewsSerializer


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all().order_by("-created_at")
    serializer_class = NewsSerializer
    permission_classes = [IsDev | IsNoK]
