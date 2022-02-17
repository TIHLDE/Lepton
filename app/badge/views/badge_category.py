from app.badge.models import Badge, BadgeCategory
from app.badge.serializers import BadgeCategorySerializer, BadgeSerializer
from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.common.permissions import IsMember, is_admin_user
from app.common.viewsets import BaseViewSet


class BadgeCategoryViewSet(BaseViewSet, ActionMixin):
    queryset = BadgeCategory.objects.all()
    serializer_class = BadgeCategorySerializer
    permission_classes = [IsMember]
    http_method_names = ["get", "post"]
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
