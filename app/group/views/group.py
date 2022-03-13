from django_filters import MultipleChoiceFilter
from django_filters.rest_framework import (
    BooleanFilter,
    DjangoFilterBackend,
    FilterSet,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.common.enums import GroupType
from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission, is_admin_user
from app.common.viewsets import BaseViewSet
from app.group.models import Group
from app.group.serializers import GroupSerializer
from app.group.serializers.membership import MembershipHistorySerializer

"""
filtrering for:
- hente ut klasser og trinn ved brukeropprettelse
     - kan løses med filtrering på alle grupper
- hente ut offentlige grupper til gruppeoversikten
    - admins skal kunne hente ut alle
    - vanlige brukere skal kun hente ut offentlig

noen grupper skal kun vises i gruppeoversikten
kun noen grupper skal kunne filtreres basert på type

By default skal man kun hente ut offentlige grupper men utvidet filtrering skal være mulig
"""


class GroupFilter(FilterSet):
    type = MultipleChoiceFilter(choices=GroupType.all())
    public = BooleanFilter(label="Offentlige")

    class Meta:
        model: Group
        fields = ["type", "public"]

    def filter_type(self, queryset, name, value):
        print(value)
        return queryset.filter(type__in=value)

    def filter_public(self, queryset, name, value):
        if is_admin_user(self.request):
            return queryset
        return queryset.filter(type__in=GroupType.public_groups())


class GroupViewSet(BaseViewSet, ActionMixin):
    """API endpoint for Groups"""

    serializer_class = GroupSerializer
    permission_classes = [BasicViewPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = GroupFilter
    queryset = Group.objects.all()
    lookup_field = "slug"

    def retrieve(self, request, slug):
        """Returns a spesific group by slug"""
        try:
            super().retrieve(request, slug)
        except Group.DoesNotExist:
            return Response(
                {"detail": ("Gruppen eksisterer ikke")},
                status=status.HTTP_404_NOT_FOUND,
            )

    def update(self, request, *args, **kwargs):
        """Updates a spesific group by slug"""
        try:
            group = self.get_object()
            serializer = GroupSerializer(
                group, data=request.data, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                super().perform_update(serializer)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Group.DoesNotExist:
            return Response(
                {"detail": ("Gruppen eksisterer ikke")},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        """Creates a group if it does not exist"""
        try:
            slug = request.data["slug"]
            group, _ = Group.objects.get_or_create(slug=slug)
            serializer = GroupSerializer(
                group, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                super().perform_create(serializer)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )
        except Group.DoesNotExist:
            return Response(
                {"detail": ("Gruppen eksisterer ikke")},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["get"], url_path="membership-histories")
    def get_group_history(self, request, *args, **kwargs):
        group = self.get_object()
        self.pagination_class = BasePagination
        membership_history = group.membership_histories.order_by("-end_date")
        return self.paginate_response(
            data=membership_history, serializer=MembershipHistorySerializer
        )
