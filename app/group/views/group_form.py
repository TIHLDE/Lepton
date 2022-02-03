from django.shortcuts import get_object_or_404
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.common.permissions import BasicViewPermission, is_admin_user
from app.forms.mixins import APIFormErrorsMixin
from app.forms.models.forms import GroupForm
from app.forms.serializers.forms import GroupFormSerializer
from app.group.models.group import Group


class GroupFormViewSet(APIFormErrorsMixin, mixins.ListModelMixin, GenericViewSet):

    serializer_class = GroupFormSerializer
    permission_classes = [BasicViewPermission]
    queryset = GroupForm.objects.all()

    def get_queryset(self):
        group = get_object_or_404(Group, slug=self.kwargs.get("slug"))
        if self.request.user.is_leader_of(group) or is_admin_user(self.request):
            return super().get_queryset().filter(group=group)

        if self.request.user.is_member_of(group):
            return (
                super().get_queryset().filter(group=group, is_open_for_submissions=True)
            )

        return (
            super()
            .get_queryset()
            .filter(
                group=group, is_open_for_submissions=True, only_for_group_members=False
            )
        )
