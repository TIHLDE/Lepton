from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from app.blitzed.models.user_wasted_level import UserWastedLevel
from app.blitzed.serializers.user_wasted_level import UserWastedLevelSerializer
from app.common.permissions import BasicViewPermission


class UserWastedLevelViewset(ModelViewSet):
    queryset = UserWastedLevel.objects.all().order_by("-timestamp")
    serializer_class = UserWastedLevelSerializer
    permission_classes = [BasicViewPermission]

    def destroy(self, request, *args, **kwargs):
        print("Debugging - Before calling super().destroy()")

        super().destroy(request, *args, **kwargs)

        print("Debugging - After calling super().destroy()")

        return Response(
            {"detail": "The wasted level was deleted"}, status=status.HTTP_200_OK
        )
