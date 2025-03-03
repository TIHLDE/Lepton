from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.feedback.filters.feedback import FeedbackFilter
from app.feedback.models.feedback import Feedback
from app.feedback.serializers import (
    BugCreateSerializer,
    BugUpdateSerializer,
    FeedbackListPolymorphicSerializer,
    IdeaCreateSerializer,
    IdeaUpdateSerializer,
)


class FeedbackViewSet(BaseViewSet):
    serializer_class = FeedbackListPolymorphicSerializer
    queryset = Feedback.objects.select_related("author")
    pagination_class = BasePagination
    permission_classes = [BasicViewPermission]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = FeedbackFilter
    search_fields = [
        "title",
        "author__first_name",
        "author__last_name",
    ]

    def get_queryset(self):
        return Feedback.objects.select_related("author").annotate(
            upvotes=Count("reactions", filter=Q(reactions__emoji=":thumbs-up:")),
            downvotes=Count("reactions", filter=Q(reactions__emoji=":thumbs-down:")),
        )

    def retrieve(self, request, *_args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        data["upvotes"] = instance.upvotes
        data["downvotes"] = instance.downvotes

        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *_args, **_kwargs):
        data = request.data

        feedback_type = data.get("feedback_type")

        if feedback_type == "Idea":
            serializer = IdeaCreateSerializer(data=data, context={"request": request})

        elif feedback_type == "Bug":
            serializer = BugCreateSerializer(data=data, context={"request": request})

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
        super().destroy(request, *_args, **_kwargs)
        return Response(
            {"detail": "Tilbakemeldingen ble slettet"},
            status=status.HTTP_200_OK,
        )
