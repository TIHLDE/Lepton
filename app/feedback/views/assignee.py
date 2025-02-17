from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.feedback.models.assignee import Assignee
from app.feedback.serializers import (
    AssigneeCreateUpdateDeleteSerializer,
    AssigneeSerializer,
)


class AssigneeViewSet(BaseViewSet):
    serializer_class = AssigneeSerializer
    queryset = Assignee.objects.select_related("user", "feedback")
    pagination_class = BasePagination
    permission_classes = [BasicViewPermission]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["user__first_name", "user__last_name", "feedback__title"]

    def create(self, request, *_args, **_kwargs):
        data = request.data
        data["user_id"] = request.user.id

        serializer = AssigneeCreateUpdateDeleteSerializer(
            data=data, context={"request": request}
        )

        if serializer.is_valid():
            assignee = serializer.save()
            return Response(
                AssigneeSerializer(assignee).data, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *_args, **_kwargs):
        instance = self.get_object()

        if instance.user != request.user:
            return Response(
                {"detail": "Du kan bare oppdatere dine egne tildelinger."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssigneeCreateUpdateDeleteSerializer(
            instance, data=request.data, partial=True
        )

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *_args, **_kwargs):
        super.destroy(request, *_args, **_kwargs)
        return Response(
            {"detail": "Oppdragstakeren har blitt slettet."}, status=status.HTTP_200_OK
        )
