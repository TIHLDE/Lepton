from rest_framework import status, viewsets
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.gallery.models.picture import Picture
from app.gallery.serializers.picture import PictureSerializer


class PictureViewSet(viewsets.ModelViewSet):
    serializer_class = PictureSerializer
    queryset = Picture.objects.all()
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def get_queryset(self):
        album_id = self.kwargs.get("slug", None)
        return Picture.objects.filter(album__slug=album_id)

    def create(self, request, *args, **kwargs):

        album_id = self.kwargs.get("slug", None)

        serializer = PictureSerializer(
            data=request.data, partial=True, many=True, context={"slug": album_id}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
