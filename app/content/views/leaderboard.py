from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission

from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.common.permissions import IsMember
from app.content.filters.leaderboard import LeaderBoardFilter
from app.content.models.user import User
from app.content.models.user_badge import UserBadge
from app.content.serializers.badge import BadgeSerializer
from app.content.serializers.user_badge import LeaderboardSerializer


class LeaderboardViewSet(viewsets.ModelViewSet):
    queryset = (
        User.objects.all()
        .annotate(number_of_badges=Count("user_badges"))
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


class LeaderboardBadgesViewSet(viewsets.ModelViewSet, ActionMixin):
    queryset = User.objects.all()
    serializer_class = LeaderboardSerializer
    permission_classes = [BasePermission]
    http_method_names = ["get"]
    pagination_class = BasePagination

    @action(detail=True, methods=["get"], url_path="badges")
    def get_user_badges(self, request, *args, **kwargs):
        user_badges = UserBadge.objects.filter(user__user_id=kwargs["pk"])
        badges = [user_badge.badge for user_badge in user_badges]
        return self.paginate_response(data=badges, serializer=BadgeSerializer)
