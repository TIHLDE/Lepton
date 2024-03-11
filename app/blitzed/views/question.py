from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from app.blitzed.models.question import Question
from app.blitzed.serializers.question import QuestionSerializer
from app.common.permissions import BasicViewPermission


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all().order_by("-created_at")
    serializer_class = QuestionSerializer
    permission_classes = [BasicViewPermission]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "The question was deleted"}, status=status.HTTP_200_OK
        )
