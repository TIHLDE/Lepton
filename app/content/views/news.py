from django.utils.translation import gettext as _
from rest_framework import status, viewsets
from rest_framework.response import Response

from dry_rest_permissions.generics import DRYPermissions

from app.common.pagination import BasePagination
from app.content.models import News
from app.content.serializers import NewsSerializer


class NewsViewSet(viewsets.ModelViewSet):

    queryset = News.objects.all().order_by("-created_at")
    serializer_class = NewsSerializer
    permission_classes = [DRYPermissions]
    pagination_class = BasePagination

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": _("Nyheten ble slettet")}, status=status.HTTP_200_OK)
