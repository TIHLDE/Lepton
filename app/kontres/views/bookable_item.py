from rest_framework import status
from app.common.viewsets import BaseViewSet
from rest_framework.response import Response
from app.common.permissions import BasicViewPermission
from app.kontres.serializer import BookableItemSerializer, BookableItemCreateSerializer 
from app.common.pagination import BasePagination
from app.kontres.filters import BookableItemListFilter
    
class BookableItemViewSet(BaseViewSet):
    serializer_class = BookableItemSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination
    filter_class = BookableItemListFilter

    def get_queryset(self):
        return None

    def create(self, request, *args, **kwargs):
        try:
            # Set up the create serializer for handling create requests
            data = request.data
            serializer = BookableItemCreateSerializer(data=data, context={"request": request})            

            # If the request is formatted correctly, with all required fields, create the item
            if serializer.is_valid():
                item = super().perform_create(serializer)

                # Create a new serializer for returning the created item
                serializer = BookableItemSerializer(item) 
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            # If the request is invalid, return the missing fields (or errors)
            return Response(
                {"detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {"detail": "Det oppstod en intern serverfeil"},
                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def update(self, request, *args, **kwargs):
        return None

    def destroy(self, request, *args, **kwargs):
        return None

    def retrieve(self, request, *args, **kwargs):
        return None
