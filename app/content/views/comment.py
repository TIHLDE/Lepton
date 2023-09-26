from app.common.viewsets import BaseViewSet
from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.content.serializers.comment import CommentSerializer, CommentCreateAndUpdateSerializer
from app.content.models.comment import Comment
from app.common.permissions import BasicViewPermission


class CommentViewSet(BaseViewSet, ActionMixin):
    serializer_class = CommentSerializer
    # permission_classes = [BasicViewPermission]
    queryset = Comment.objects.all()
    pagination_class = BasePagination

    def retrieve(self, request, pk):
        try:
            comment = self.get_object()
            print(comment)
        except Exception as e:
            print(e)
    
    def create(self, request, *args, **kwargs):
        data = request.data
        print(data)

        serializer = CommentCreateAndUpdateSerializer(
            data=data, context={"request": request}
        )

        if serializer.is_valid():
            print("valid")
            comment = super().perform_create(serializer)
            print("perform create good")
            print(comment)