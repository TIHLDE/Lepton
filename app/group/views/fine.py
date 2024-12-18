from django.db.models import Subquery
from django.db.models.aggregates import Coalesce, Sum
from django.db.models.expressions import OuterRef
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.communication.enums import UserNotificationSettingType
from app.content.models.user import User
from app.group.filters.fine import FineFilter
from app.group.mixins import APIFineErrorsMixin
from app.group.models.fine import Fine
from app.group.models.group import Group
from app.group.serializers.fine import (
    FineNoUserSerializer,
    FineSerializer,
    FineStatisticsSerializer,
    FineUpdateCreateSerializer,
    FineUpdateDefenseSerializer,
    UserFineSerializer,
)


class FineViewSet(APIFineErrorsMixin, BaseViewSet, ActionMixin):
    serializer_class = FineSerializer
    permission_classes = [BasicViewPermission]
    queryset = Fine.objects.select_related(
        "created_by",
        "user",
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = FineFilter
    pagination_class = BasePagination

    def get_queryset(self):
        return self.filter_queryset(self.queryset).filter(
            group__slug=self.kwargs["slug"], group__fines_activated=True
        )

    # noinspection PyShadowingNames
    def create(self, request, *args, **kwargs):
        context = {
            "group_slug": kwargs["slug"],
            "created_by": request.id,
            "user_ids": request.data["user"],
            "request": request,
        }

        serializer = FineUpdateCreateSerializer(
            many=True, partial=True, data=[request.data], context=context
        )

        if serializer.is_valid():
            fines = super().perform_create(serializer)

            if len(fines):
                fine = fines[0]
                users = list(map(lambda fine: fine.user, fines))

                from app.communication.notifier import Notify

                Notify(
                    users,
                    f'Du har fått en bot i "{fine.group.name}"',
                    UserNotificationSettingType.FINE,
                ).add_paragraph(
                    f'{fine.created_by.first_name} {fine.created_by.last_name} har gitt deg {fine.amount} bøter for å ha brutt paragraf "{fine.description}" i gruppen {fine.group.name}'
                ).add_link(
                    "Gå til bøter",
                    f"{fine.group.website_url}boter/",
                ).send()

            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"detail": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": ("Boten ble slettet")}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path=r"users/(?P<user_id>[^/.]+)")
    def get_user_fines(self, _request, *_args, **kwargs):
        """Get the fines of a specific user in a group"""

        fines = (
            self.get_queryset()
            .select_related("created_by")
            .filter(user__user_id=kwargs["user_id"])
        )
        return self.paginate_response(data=fines, serializer=FineNoUserSerializer)

    @action(detail=False, methods=["get"], url_path="users")
    def get_fine_users(self, _request, *_args, **_kwargs):
        """Get the users in a group which has fines and how many"""
        users = self.get_fine_filter_query()
        return self.paginate_response(data=users, serializer=UserFineSerializer)

    def get_fine_filter_query(self):
        fines_amount = (
            self.get_queryset()
            .filter(
                user=OuterRef("pk"),
                group=self.kwargs["slug"],
                group__fines_activated=True,
            )
            .order_by()
            .values("user")
            .annotate(count=Sum("amount"))
            .values("count")
        )
        return User.objects.filter(memberships__group=self.kwargs["slug"]).annotate(
            fines_amount=Coalesce(Subquery(fines_amount), 0)
        )

    @action(detail=False, methods=["put"], url_path="batch-update")
    def batch_update_fines(self, request, *_args, **_kwargs):
        """Update a batch of fines at once"""
        assert request.data["data"]
        fines = self.get_queryset().filter(id__in=request.data["fine_ids"])
        serializer = FineUpdateCreateSerializer(
            instance=fines,
            data=[],
            context={"request": request, "data": request.data["data"]},
            many=True,
        )
        if serializer.is_valid():
            super().perform_update(serializer)
            return Response(
                {"detail": "Alle bøtene ble oppdatert"}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["put"], url_path=r"batch-update/(?P<user_id>[^/.]+)")
    def batch_update_user_fines(self, request, *_args, **kwargs):
        """Update all the fines of a user in a specific group"""
        fines = self.get_queryset().filter(user__user_id=kwargs["user_id"])
        serializer = FineUpdateCreateSerializer(
            instance=fines,
            data=[],
            context={"request": request, "data": request.data},
            many=True,
        )
        if serializer.is_valid():
            super().perform_update(serializer)
            return Response(
                {"detail": "Alle bøtene ble oppdatert"}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"], url_path="statistics")
    def get_group_fine_statistics(self, _request, *_args, **kwargs):
        group = Group.objects.get(slug=kwargs["slug"])
        return Response(FineStatisticsSerializer(group).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"], url_path="defense")
    def update_defense(self, request, *_args, **_kwargs):
        fine = self.get_object()
        serializer = FineUpdateDefenseSerializer(
            fine, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            fine = super().perform_update(serializer)
            return Response(FineSerializer(fine).data, status=status.HTTP_200_OK)
        return Response(
            {"detail": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
