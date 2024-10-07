from rest_framework import status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.index.models.feedback import Feedback
from app.index.serializers.feedback import (
    BugCreateSerializer,
    FeedbackListPolymorphicSerializer,
    IdeaCreateSerializer,
    BugUpdateSerializer,
    IdeaUpdateSerializer,
)


class FeedbackViewSet(BaseViewSet):
    serializer_class = FeedbackListPolymorphicSerializer
    queryset = Feedback.objects.select_related("author")
    pagination_class = BasePagination
    permission_classes = [BasicViewPermission]

    def create(self, request, *_args, **_kwargs):
        data = request.data

        feedback_type = data.get("feedback_type")

        if feedback_type == "Idea":
            serializer = IdeaCreateSerializer(data=data)

        elif feedback_type == "Bug":
            serializer = BugCreateSerializer(data=data)

        else:
            return Response(
                {"detail": "Ugyldig type tilbakemelding"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if serializer.is_valid():
            feedback = self.perform_create(serializer)
            data = FeedbackListPolymorphicSerializer(feedback).data
            return Response(
                data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *_args, **_kwargs):
        instance = self.get_object()
        data = request.data

        feedback_type = instance.feedback_type

        if feedback_type == "Idea":
            serializer = IdeaUpdateSerializer(instance, data=data)

        elif feedback_type == "Bug":
            serializer = BugUpdateSerializer(instance, data=data)

        if serializer.is_valid():
            super().perform_update(serializer)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *_args, **_kwargs):
        super().perform_destroy(request, *_args, **_kwargs)
        return Response(
            {"detail": "Tilbakemeldingen ble slettet"},
            status=status.HTTP_200_OK,
        )