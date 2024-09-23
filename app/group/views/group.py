from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from sentry_sdk import capture_exception

from app.common.mixins import ActionMixin
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.group.filters.group import GroupFilter
from app.group.models import Group
from app.group.serializers import GroupSerializer, GroupStatisticsSerializer
from app.group.serializers.group import GroupListSerializer, GroupCreateSerializer, SimpleGroupSerializer
from app.group.mixins import APIGroupErrorsMixin


class GroupViewSet(APIGroupErrorsMixin, BaseViewSet, ActionMixin):
    serializer_class = GroupSerializer
    permission_classes = [BasicViewPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = GroupFilter
    queryset = Group.objects.all()
    lookup_field = "slug"

    def get_serializer_class(self):
        if hasattr(self, "action") and self.action == "list":
            return GroupListSerializer
        return super().get_serializer_class()

    def retrieve(self, request, slug):
        """Returns a specific group by slug"""
        try:
            group = self.get_object()
            serializer = GroupSerializer(
                group, context={"request": request}, many=False
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response(
                {"detail": "Gruppen eksisterer ikke"},
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
                {"detail": "Gruppen eksisterer ikke"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        """Creates a group if it does not exist"""
        serializer = GroupCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            group = super().perform_create(serializer)
            return_serializer = SimpleGroupSerializer(group)
            return Response(data=return_serializer.data, status=HTTP_201_CREATED)
        return Response(
            {"detail": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["get"], url_path="statistics")
    def statistics(self, request, *args, **kwargs):
        group = self.get_object()
        serializer = GroupStatisticsSerializer(group, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
