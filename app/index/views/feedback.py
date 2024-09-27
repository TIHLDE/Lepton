from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.index.models.feedback import Feedback
from app.index.serializers.feedback import FeedbackListPolymorphicSerializer


class FeedbackViewSet(BaseViewSet):
    serializer_class = FeedbackListPolymorphicSerializer
    queryset = Feedback.objects.select_related("author")
    pagination_class = BasePagination
    permission_classes = [BasicViewPermission]
