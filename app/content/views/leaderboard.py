from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from app.common.permissions import IsMember
from app.common.pagination import BasePagination
from app.content.filters.leaderboard import LeaderBoardFilter
from app.content.models.user import User
from app.content.serializers.user_badge import LeaderboardSerializer



class LeaderboardViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().annotate(number_of_badges=Count("user_badges")).order_by('-number_of_badges')
    serializer_class = LeaderboardSerializer
    permission_classes = [IsMember]
    http_method_names = ["get"]
    pagination_class = BasePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = LeaderBoardFilter
    search_fields = ["user_id", "first_name", "last_name", "user_badges__badge__title",]