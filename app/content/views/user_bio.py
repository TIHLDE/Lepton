from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response

from app.common.viewsets import BaseViewSet
from app.content.models.user_bio import UserBio
from app.content.serializers.user_bio import UserBioSerializer


class UserBioViewset(BaseViewSet):
    queryset = (
        UserBio.objects.all()
    )  # Queryset = all data som tilhører denne klassen (alle objekter i userbio)
    serializer_class = UserBioSerializer

    def create(self, request, *args, **kwargs):

        # Intiate base serializer from request data
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create instance of user_bio
        user_bio = super().perform_create(serializer, user=request.user)

        user_bio_serializer = UserBioSerializer(
            user_bio, context={"user": user_bio.user}
        )

        return Response(user_bio_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        bio = self.get_object()
        serializer = UserBioSerializer(
            bio, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            bio = super().perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)


# todo
# create update retrieve
# test (post, put, get)
# autentisering - bruker kan kun oppdatere sin egen bio
# Kun admin kan endre andre bios + test
# test alt
