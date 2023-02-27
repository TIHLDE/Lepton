from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.emoji.models.user_news_reaction import UserNewsReaction
from app.emoji.serializers.user_news_reaction import UserNewsReactionSerializer
from rest_framework import status
from rest_framework.response import Response


class UserNewsReactionViewSet(BaseViewSet): 

    serializer_class = UserNewsReactionSerializer
    queryset = UserNewsReaction.objects.all()
    permission_classes = [BasicViewPermission]
    #filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        print("Running destroy")
        return Response({"detail": "Reaksjonen ble slettet"}, status=status.HTTP_200_OK)
    