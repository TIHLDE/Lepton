from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins
from rest_framework.viewsets import GenericViewSet

from app.badge.filters.badge import (
    UserWithBadgesFilter,
    UserWithSpecificBadgeFilter,
)
from app.badge.models import UserBadge
from app.badge.serializers import (
    LeaderboardForBadgeSerializer,
    LeaderboardSerializer,
)
from app.common.pagination import BasePagination
from app.common.permissions import IsMember
from app.content.models import User


class LeaderboardViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = LeaderboardSerializer
    permission_classes = [IsMember]
    pagination_class = BasePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UserWithBadgesFilter
    search_fields = [
        "user_id",
        "first_name",
        "last_name",
    ]

    def get_queryset(self):
        number_of_badges = Count("user_badges", distinct=True)
        category = self.request.query_params.get("category", None)
        if category:
            number_of_badges = Count(
                "user_badges",
                filter=Q(user_badges__badge__badge_category=category),
                distinct=True,
            )

        return (
            User.objects.annotate(number_of_badges=number_of_badges)
            .filter(number_of_badges__gt=0)
            .order_by("-number_of_badges", "first_name")
        )


class LeaderboardForBadgeViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = UserBadge.objects.select_related("user").order_by("created_at")
    serializer_class = LeaderboardForBadgeSerializer
    permission_classes = [IsMember]
    pagination_class = BasePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UserWithSpecificBadgeFilter
    search_fields = [
        "user__user_id",
        "user__first_name",
        "user__last_name",
    ]

    def get_queryset(self):
        return self.queryset.filter(badge__id=self.kwargs["id"])
