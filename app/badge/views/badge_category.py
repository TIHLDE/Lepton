from rest_framework import mixins, viewsets

from app.badge.models import Badge, BadgeCategory
from app.badge.serializers import BadgeCategorySerializer, BadgeSerializer
from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.common.permissions import IsMember, is_admin_user


class BadgeCategoryViewSet(
    viewsets.GenericViewSet, ActionMixin, mixins.ListModelMixin, mixins.CreateModelMixin
):
    queryset = BadgeCategory.objects.all()
    serializer_class = BadgeCategorySerializer
    permission_classes = [IsMember]
    pagination_class = BasePagination

    def retrieve(self, request, *args, **kwargs):
        if is_admin_user(request):
            badges = Badge.objects.all()
        else:
            badges = Badge.objects.public()

        badges_in_category = badges.filter(badge_category__id=kwargs["pk"])
        return self.paginate_response(
            data=badges_in_category, serializer=BadgeSerializer
        )
