from rest_framework import status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models import News
from app.content.serializers import NewsSerializer, SimpleNewsSerializer
from app.emoji.serializers.news_emojis import NewsEmojisSerializer


class NewsViewSet(BaseViewSet):

    queryset = News.objects.all().order_by("-created_at")
    serializer_class = NewsSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def get_serializer_class(self):
        if hasattr(self, "action") and self.action == "list":
            return SimpleNewsSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        data = request.data
        emojis_allowed = data.get("allowEmojis")
        data.pop("allowEmojis", None)

        serializer = NewsSerializer(data=data, context={"request": request})
        try:
            if serializer.is_valid():
                news = super().perform_create(serializer)
                res = self.allow_emojis(
                    data={"news": news.id, "emojis_allowed": emojis_allowed}
                )

                if res.status == status.HTTP_400_BAD_REQUEST:
                    return res
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError:
            return Response(
                {"detail": "Nyhet ble ikke laget fordi noe gikk galt"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def allow_emojis(self, data):
        serializer = NewsEmojisSerializer(data=data)
        try:
            if serializer.is_valid():
                super().perform_create(serializer)
                return Response(
                    {"detail": "Emoji ble tillatt for nyhet"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"detail": "Emoji ble ikke tillatt fordi noe gikk galt"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError:
            return Response(
                {"detail": "Emoji ble ikke tillatt fordi noe gikk galt"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Nyheten ble slettet"}, status=status.HTTP_200_OK)
