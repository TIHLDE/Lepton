from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.filters.news import NewsFilter
from app.content.models import News
from app.content.serializers import NewsSerializer, SimpleNewsSerializer


class NewsViewSet(BaseViewSet):

    queryset = News.objects.all().order_by("-created_at")
    serializer_class = NewsSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = NewsFilter
    search_fields = ["title", "body", "header"]

    def get_serializer_class(self):
        if hasattr(self, "action") and self.action == "list":
            return SimpleNewsSerializer
        return super().get_serializer_class()

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Nyheten ble slettet"}, status=status.HTTP_200_OK)
