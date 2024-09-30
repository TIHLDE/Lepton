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

    def create(self,request, *_args, **_kwargs):
        data = request.data

        feedback_type = data.get("feedback_type")

        if feedback_type == "Idea" :
            serializer = IdeaCreateSerializer(data=data)

        elif feedback_type == "Bug":
            serializer = BugCreateSerializer(data=data)

        if serializer.is_valid():
            feedback = self.perform_create(serializer)
            return Response(
                FeedbackListPolymorphicSerializer(feedback).data,
                status=status.HTTP_201_CREATED,
            )
        
        return Response(
            {"detail": "Ugyldig type tilbakemelding"},
            status=status.HTTP_400_BAD_REQUEST,
        )


