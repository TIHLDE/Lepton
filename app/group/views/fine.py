from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.content.models.user import User
from app.group.models.fine import Fine
from app.group.models.group import Group
from app.group.serializers.fine import FineSerializer


class FineViewSet(viewsets.ModelViewSet):
    serializer_class = FineSerializer
    permission_classes = [BasicViewPermission]
    queryset = Fine.objects.all()

    def get_queryset(self):
        return self.queryset.filter(group__slug=self.kwargs["slug"])

    def create(self, request, *args, **kwargs):
        user = get_object_or_404(User, user_id=request.data["user_id"])
        group = get_object_or_404(Group, slug=kwargs["slug"])
        fine = Fine.objects.create(group=group, user=user)
        serializer = FineSerializer(
            fine, data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"detail": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
