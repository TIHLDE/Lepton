from rest_framework import viewsets

from ..models import News
from ..serializers import NewsSerializer
from ..permissions import IsNoK


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all().order_by('-created_at')
    serializer_class = NewsSerializer
    permission_classes = [IsNoK]
