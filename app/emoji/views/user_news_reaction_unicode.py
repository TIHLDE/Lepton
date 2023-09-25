from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models.news import News
from app.emoji.models.news_emojis import NewsEmojis
from app.emoji.models.user_news_reaction_unicode import UserNewsReactionUnicode
from app.emoji.serializers.user_news_reaction_unicode import (
    UserNewsReactionUnicodeSerializer,
)


class UserNewsReactionUnicodeViewSet(BaseViewSet):

    serializer_class = UserNewsReactionUnicodeSerializer
    queryset = UserNewsReactionUnicode.objects.all()
    permission_classes = [BasicViewPermission]

    def create(self, request, *args, **kwargs):
        news = get_object_or_404(News, id=request.data["news"])

        try:
            news_emojis = NewsEmojis.objects.get(news=news)
            emojis_allowed = news_emojis.emojis_allowed

            if not emojis_allowed:
                return Response(
                    {"detail": "Ulovlig emoji for denne nyheten"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = UserNewsReactionUnicodeSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                super().perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError:
            return Response(
                {"detail": "Noe gikk galt"}, status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        news = get_object_or_404(News, id=request.data["news"])

        try:
            news_emojis = NewsEmojis.objects.get(news=news)
            emojis_allowed = news_emojis.emojis_allowed

            if not emojis_allowed:
                return Response(
                    {"detail": "Ulovlig emoji for denne nyheten"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            reaction = self.get_object()
            serializer = UserNewsReactionUnicodeSerializer(
                reaction, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                super().perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"detail": "Du har ikke tillatelse til å oppdatere med den emojien"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except UserNewsReactionUnicode.DoesNotExist as reaction_not_exist:
            capture_exception(reaction_not_exist)
            return Response(
                {"details": "Reaksjonen ble ikke funnet"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Reaksjonen ble slettet"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def get_reactions_by_news(self, request):
        try:
            news_id = request.query_params.get("news")
            if not news_id:
                return Response(
                    {"detail": "Vennligst send med id-en til nyheten."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            reactions = UserNewsReactionUnicode.objects.filter(news=news_id)
            serializer = UserNewsReactionUnicodeSerializer(reactions, many=True)

            if reactions.exists():
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(
                {"detail": "Ingen reaksjoner funnet for den angitte nyheten."},
                status=status.HTTP_200_OK,
            )
        except ValueError:
            return Response(
                {"detail": "Noe gikk galt ved henting av reaksjoner"},
                status=status.HTTP_400_BAD_REQUEST,
            )
