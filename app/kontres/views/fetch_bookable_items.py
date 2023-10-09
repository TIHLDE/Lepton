from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.kontres.models.bookable_item import BookableItem
from app.kontres.serializer.bookable_item_serializer import BookableItemSerializer


@api_view(['GET'])
def bookable_item_view(request):
    if request.method == 'GET':
        bookable_items = BookableItem.objects.all()
        serializer = BookableItemSerializer(bookable_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
