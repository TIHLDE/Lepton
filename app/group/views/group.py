from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from app.common.enums import GroupType
from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission, is_admin_user
from app.group.models import Group
from app.group.serializers import GroupSerializer
from app.group.serializers.membership import MembershipHistorySerializer


class GroupViewSet(viewsets.ModelViewSet, ActionMixin):
    """API endpoint for Groups"""

    serializer_class = GroupSerializer
    permission_classes = [BasicViewPermission]
    queryset = Group.objects.all()
    lookup_field = "slug"

    def get_queryset(self):
        if is_admin_user(self.request):
            return self.queryset
        return self.queryset.filter(type__in=GroupType.public_groups())

    def retrieve(self, request, slug):
        """Returns a spesific group by slug"""
        try:
            group = self.get_object()
            serializer = GroupSerializer(
                group, context={"request": request}, many=False
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)
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
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST,
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
            group = Group.objects.get_or_create(slug=slug)
            serializer = GroupSerializer(
                group[0], data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
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
