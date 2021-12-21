from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.common.permissions import BasicViewPermission
from app.forms.models.forms import GroupForm
from app.forms.serializers.forms import GroupFormSerializer


class GroupFormViewSet(mixins.ListModelMixin, GenericViewSet):

    serializer_class = GroupFormSerializer
    permission_classes = [BasicViewPermission]
    queryset = GroupForm.objects.all()

    def get_queryset(self):
        # TODO: Limit listed forms based on "is_open_for_submissions" and "only_for_group_members"
        return self.queryset.filter(group=self.kwargs.get("slug"))
