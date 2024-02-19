from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models.user_bio import UserBio
from app.content.serializers.user_bio import (
    UserBioCreateSerializer,
    UserBioSerializer,
    UserBioUpdateSerializer,
)


class UserBioViewset(BaseViewSet):
    queryset = UserBio.objects.all()
    serializer_class = UserBioSerializer
    permission_classes = [BasicViewPermission]

    def create(self, request, *args, **kwargs):
        data = request.data

        serializer = UserBioCreateSerializer(data=data, context={"request": request})

        if not serializer.is_valid():
            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        user_bio = super().perform_create(serializer, user=request.user)

        user_bio_serializer = UserBioSerializer(
            user_bio, context={"user": user_bio.user}
        )

        return Response(user_bio_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        bio = self.get_object()
        serializer = UserBioUpdateSerializer(
            bio, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            bio = super().perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": ("Brukerbio ble slettet")}, status=status.HTTP_200_OK
        )
