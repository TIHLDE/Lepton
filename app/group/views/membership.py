from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.response import Response

from app.common.permissions import IsDev, IsHS, IsLeader, is_admin_user
from app.content.models import User
from app.group.models import Group, Membership
from app.group.serializers import MembershipSerializer
from app.group.serializers.membership import (
    MembershipLeaderSerializer,
    UpdateMembershipSerializer,
)


class MembershipViewSet(viewsets.ModelViewSet):

    serializer_class = MembershipSerializer
    queryset = Membership.objects.all()
    permission_classes = [IsDev | IsHS | IsLeader]
    lookup_field = "user_id"

    def get_queryset(self):
        return self.queryset.filter(group__slug=self.kwargs["slug"])

    def get_serializer_class(self):
        if is_admin_user(self.request):
            return MembershipLeaderSerializer
        if IsLeader().has_permission(request=self.request, view=self):
            return MembershipLeaderSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = []
        return super(MembershipViewSet, self).get_permissions()

    def update(self, request, *args, **kwargs):
        try:
            membership = self.get_object()
            serializer = UpdateMembershipSerializer(
                membership, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            return super().update(request, *args, **kwargs)
        except Membership.DoesNotExist:
            return Response(
                {"detail": "Medlemskapet eksisterer ikke"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        try:
            user = User.objects.get(user_id=request.data["user"]["user_id"])
            group = Group.objects.get(slug=kwargs["slug"])
            membership = Membership.objects.create(user=user, group=group)
            serializer = MembershipSerializer(membership, data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Membership.DoesNotExist:
            return Response(
                {"detail": "Medlemskapet eksisterer ikke"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "Bruker eksisterer ikke"}, status=status.HTTP_404_NOT_FOUND,
            )
        except Group.DoesNotExist:
            return Response(
                {"detail": "Gruppen eksisterer ikke"}, status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError:
            return Response(
                {"detail": "Medlemskapet eksisterer allerede "},
                status=status.HTTP_400_BAD_REQUEST,
            )
