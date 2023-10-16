from rest_framework import viewsets, status
from rest_framework.response import Response
from app.kontres.models.bookable_item import BookableItem
from app.kontres.serializer.bookable_item_serializer import BookableItemSerializer


class BookableItemViewSet(viewsets.ViewSet):

    # GET: Retrieve a list of all bookable items
    def list(self, request):
        queryset = BookableItem.objects.all()
        serializer = BookableItemSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
