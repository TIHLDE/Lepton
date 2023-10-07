from rest_framework import status
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.viewsets import BaseViewSet
from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.content.serializers.comment import CommentSerializer, CommentCreateSerializer, CommentUpdateSerializer
from app.content.models.comment import Comment
from app.common.permissions import BasicViewPermission


class CommentViewSet(BaseViewSet, ActionMixin):
    serializer_class = CommentSerializer
    permission_classes = [BasicViewPermission]
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
        if (
            "allow_comments" not in data or
            (
                "allow_comments" in data and 
                not data["allow_comments"]
            )
        ):
            return Response(
                {"detail": "Det er ikke tillatt med kommentarer her."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CommentCreateSerializer(
            data=data, context={"request": request}
        )

        if serializer.is_valid():
            try:
                comment = super().perform_create(serializer)
                serializer = CommentSerializer(comment, context={"request": request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as oversized_thread:
                capture_exception(oversized_thread)
                return Response(
                    {"detail": "Denne kommentartråden er for lang."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"detail": serializer.error}, status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, pk):
        try:
        
            data = request.data

            comment = self.get_object()
            serializer = CommentUpdateSerializer(
                comment, data=data, context={"request": request}
            )

            if serializer.is_valid():
                comment = super().perform_update(serializer)
                serializer = CommentSerializer(comment, context={"request": request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(
                {"detail": "Kunne ikke utføre oppdateringen av kommentaren."},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Comment.DoesNotExist as comment_not_exist:
            capture_exception(comment_not_exist)
            return Response(
                {"detail": "Fant ikke kommentaren."},
                status=status.HTTP_404_NOT_FOUND
            )