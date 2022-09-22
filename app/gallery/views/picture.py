from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from app.common.azure_file_handler import AzureFileHandler
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.gallery.models.album import Album
from app.gallery.models.picture import Picture
from app.gallery.serializers.picture import PictureSerializer


class PictureViewSet(BaseViewSet):
    serializer_class = PictureSerializer
    queryset = Picture.objects.all()
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def get_queryset(self):
        album_id = self.kwargs.get("id", None)
        return Picture.objects.filter(album__id=album_id)

    def create(self, request, *args, **kwargs):

        album_id = self.kwargs.get("id", None)
        album = get_object_or_404(Album, id=album_id)

        files = request.FILES.getlist("file")
        if len(files) < 1:
            return Response(
                {"detail": "Du må laste opp minst 1 bilde"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        errors = 0
        for file in files:
            try:
                url = AzureFileHandler(file).uploadBlob()
                Picture.objects.create(image=url, album=album)
            except Exception:
                errors += 1

        if errors == 0:
            return Response(
                {"detail": "Alle bildene ble lastet opp og lagt til i albumet"},
                status=status.HTTP_201_CREATED,
            )
        if errors == len(files):
            return Response(
                {"detail": f"Noe gikk galt, ingen bilder ble lagt til i albumet"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "detail": f"Noe gikk galt, {errors} av {len(files)} bilder ble kunne ikke bli lagt til i albumet"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "Bildet ble fjernet fra galleriet"}, status=status.HTTP_200_OK
        )
