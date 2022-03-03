from rest_framework import status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models import News
from app.content.serializers import NewsSerializer


class NewsViewSet(BaseViewSet):

    queryset = News.objects.all().order_by("-created_at")
    serializer_class = NewsSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def create(self, request, *args, **kwargs):
        serializer = NewsSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            news = super().perform_create(serializer)
            serializer = NewsSerializer(news, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Nyheten ble slettet"}, status=status.HTTP_200_OK)
