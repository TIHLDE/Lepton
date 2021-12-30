from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from app.common.pagination import BasePagination
from app.common.permissions import IsHS, IsMember
from app.content.filters.badge import (
    UserWithBadgesFilter,
    UserWithSpecificBadgeFilter,
)
from app.content.models import Badge, User, UserBadge
from app.content.serializers import (
    BadgeSerializer,
    LeaderboardForBadgeSerializer,
    LeaderboardSerializer,
)


class BadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [IsHS]
    http_method_names = ["get", "post"]
    pagination_class = BasePagination


class LeaderboardViewSet(viewsets.ModelViewSet):
    serializer_class = LeaderboardSerializer
    permission_classes = [IsMember]
    http_method_names = ["get"]
    pagination_class = BasePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UserWithBadgesFilter
    search_fields = [
        "user_id",
        "first_name",
        "last_name",
    ]

    def get_queryset(self):
        return (
            User.objects.annotate(number_of_badges=Count("user_badges"))
            .filter(number_of_badges__gt=0)
            .order_by("-number_of_badges", "first_name")
        )


class LeaderboardForBadgeViewSet(viewsets.ModelViewSet):
    queryset = UserBadge.objects.all().order_by("created_at")
    serializer_class = LeaderboardForBadgeSerializer
    permission_classes = [IsMember]
    http_method_names = ["get"]
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
