from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from app.common.pagination import BasePagination
from app.common.permissions import IsMember
from app.content.filters.leaderboard import LeaderBoardFilter
from app.content.models.badge import Badge
from app.content.models.user import User
from app.content.models.user_badge import UserBadge
from app.content.serializers.badge import BadgeSerializer, LeaderboardSerializer
from app.content.serializers.user_badge import UserBadgeLeaderboardSerializer


class BadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [IsMember]
    http_method_names = ["get"]
    pagination_class = BasePagination


class LeaderboardViewSet(viewsets.ModelViewSet):
    queryset = (
        User.objects.annotate(number_of_badges=Count("user_badges"))
        .filter(number_of_badges__gt=0)
        .order_by("-number_of_badges")
    )
    serializer_class = LeaderboardSerializer
    permission_classes = [IsMember]
    http_method_names = ["get"]
    pagination_class = BasePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = LeaderBoardFilter
    search_fields = [
        "user_id",
        "first_name",
        "last_name",
        "user_badges__badge__title",
    ]


class LeaderboardForBadgeViewSet(viewsets.ModelViewSet):
    queryset = UserBadge.objects.all().order_by(
        "created_at"
    )  # TODO best å se hvem som fikk en badge først?
    serializer_class = UserBadgeLeaderboardSerializer
    permission_classes = [IsMember]
    http_method_names = ["get"]
    pagination_class = BasePagination

    def get_queryset(self):
        return self.queryset.filter(badge__id=self.kwargs["id"])
