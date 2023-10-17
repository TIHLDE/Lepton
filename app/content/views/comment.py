from rest_framework import status
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from app.common.mixins import ActionMixin
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models import Comment, User
from app.content.serializers import CommentCreateSerializer, CommentSerializer


class CommentViewSet(BaseViewSet, ActionMixin):
    permission_classes = [BasicViewPermission]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def create(self, request):
        data = request.data

        user = get_object_or_404(User, user_id=request.id)

        print(user)

        create_serizalier = CommentCreateSerializer(data=data, context={"request": request})

        if create_serizalier.is_valid():
            print("Valid")
            comment = super().perform_create(create_serizalier, user=user)
            serializer = CommentSerializer(comment, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
'''
    def update(self, request):
        """Update the event with the specified pk."""
        try:
            data = request.data

            if not data["is_paid_event"]:
                data["paid_information"] = {}

            event = self.get_object()
            self.check_object_permissions(self.request, event)
            serializer = EventCreateAndUpdateSerializer(
                event, data=data, partial=True, context={"request": request}
            )

            if serializer.is_valid():
                event = super().perform_update(serializer)
                serializer = EventSerializer(event, context={"request": request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "Kunne ikke utføre oppdatering av arrangementet"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Event.DoesNotExist as event_not_exist:
            capture_exception(event_not_exist)
            return Response(
                {"detail": "Fant ikke arrangementet"}, status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, *args, **kwargs):
        event = Event.objects.get(pk=kwargs["pk"])
        if event.is_paid_event:
            paid_event = PaidEvent.objects.get(event=kwargs["pk"])
            paid_event.delete()

        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": ("Arrangementet ble slettet")}, status=status.HTTP_200_OK
        )
    '''