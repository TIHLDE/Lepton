from django.utils.translation import gettext as _
from rest_framework import status, viewsets
from rest_framework.response import Response

from ..models import News
from ..permissions import IsDev, IsNoK
from ..serializers import NewsSerializer


class NewsViewSet(viewsets.ModelViewSet):
    """ Display all news """

    queryset = News.objects.all().order_by("-created_at")
    serializer_class = NewsSerializer
    permission_classes = [IsDev | IsNoK]

    def destroy(self, request, *args, **kwargs):
        """ Delete the news """
        super().destroy(request, *args, **kwargs)
        return Response({"detail": _("Nyheten ble slettet")}, status=status.HTTP_200_OK)
