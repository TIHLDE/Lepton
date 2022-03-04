from django.conf import settings
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response

from app.common.enums import MembershipType
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission, IsLeader, is_admin_user
from app.common.viewsets import BaseViewSet
from app.communication.notifier import Notify
from app.content.models import User
from app.group.filters.membership import MembershipFilter
from app.group.models import Group, Membership
from app.group.serializers import MembershipSerializer
from app.group.serializers.membership import (
    MembershipLeaderSerializer,
    UpdateMembershipSerializer,
)
from app.util.mail_creator import MailCreator


class MembershipViewSet(BaseViewSet):

    serializer_class = MembershipSerializer
    queryset = Membership.objects.all()
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = MembershipFilter
    lookup_field = "user_id"

    def get_queryset(self):
        return super().get_queryset().filter(group__slug=self.kwargs["slug"])

    def get_serializer_class(self):
        if is_admin_user(self.request):
            return MembershipLeaderSerializer
        if IsLeader().has_permission(request=self.request, view=self):
            return MembershipLeaderSerializer
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        try:
            membership = self.get_object()
            serializer = UpdateMembershipSerializer(
                membership, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            if (
                str(request.data.get("membership_type")).lower()
                == str(MembershipType.LEADER).lower()
            ):
                title = f"Du er nå leder i gruppen {membership.group.name}"
                description = f"Du har blitt gjort til leder i gruppen {membership.group.name}. Gratulerer så mye og lykke til!"
                Notify([membership.user], title).send_email(
                    MailCreator(title)
                    .add_paragraph(f"Hei {membership.user.first_name}!")
                    .add_paragraph(description)
                    .add_button(
                        "Se gruppen",
                        membership.group.website_url,
                    )
                    .generate_string()
                ).send_notification(
                    description=description,
                    link=f"/grupper/{membership.group.slug}/",
                )
            return super().update(request, *args, **kwargs)
        except Membership.DoesNotExist:
            return Response(
                {"detail": "Medlemskapet eksisterer ikke"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        try:
            user = get_object_or_404(User, user_id=request.data["user"]["user_id"])
            group = get_object_or_404(Group, slug=kwargs["slug"])
            membership = Membership.objects.create(user=user, group=group)
            serializer = MembershipSerializer(
                membership, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            self._log_on_create(serializer)
            title = f"Du er nå med i gruppen {membership.group.name}"
            description = f"Du har blitt lagt til som medlem i gruppen {membership.group.name}. Gratulerer så mye og lykke til!"
            Notify([membership.user], title).send_email(
                MailCreator(title)
                .add_paragraph(f"Hei {membership.user.first_name}!")
                .add_paragraph(description)
                .add_button(
                    "Se gruppen",
                    f"{settings.WEBSITE_URL}/grupper/{membership.group.slug}/",
                )
                .generate_string()
            ).send_notification(
                description=description,
                link=f"/grupper/{membership.group.slug}/",
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Membership.DoesNotExist:
            return Response(
                {"detail": "Medlemskapet eksisterer ikke"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError:
            return Response(
                {"detail": "Medlemskapet eksisterer allerede "},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "Medlemskapet ble slettet"},
            status=status.HTTP_200_OK,
        )
