from rest_framework import status
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from app.common.mixins import ActionMixin
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models import Comment, User
from app.content.serializers import CommentCreateSerializer, CommentSerializer, CommentUpdateSerializer


class CommentViewSet(BaseViewSet, ActionMixin):
    permission_classes = [BasicViewPermission]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def create(self, request):
        data = request.data

        user = get_object_or_404(User, user_id=request.id)

        create_serizalier = CommentCreateSerializer(data=data, context={"request": request})

        if create_serizalier.is_valid():
            comment = super().perform_create(create_serizalier, user=user)
            serializer = CommentSerializer(comment, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {"detail": create_serizalier.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, pk):
        data = request.data

        comment = self.get_object()

        update_serializer = CommentUpdateSerializer(comment, data=data, context={"request": request})

        if update_serializer.is_valid():
            super().perform_update(update_serializer)
            serializer = CommentSerializer(comment, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": update_serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
            

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": ("Kommentaren ble slettet")}, status=status.HTTP_200_OK
        )