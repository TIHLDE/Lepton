from rest_framework import status, viewsets
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.permissions import IsDev, IsMember

from ..models import Badge, User, UserBadge
from ..serializers import UserBadgeSerializer


class UserBadgeViewSet(viewsets.ModelViewSet):
    serializer_class = UserBadgeSerializer
    permission_classes = [IsDev]
    queryset = UserBadge.objects.all()

    def get_permissions(self):
        if self.request.method in ["POST"]:
            self.permission_classes = [IsMember]
        return super(UserBadgeViewSet, self).get_permissions()

    def create(self, request):
        try:
            user = User.objects.get(user_id=request.id)
            badge = Badge.objects.get(id=request.data.get("badge_id"))

            if UserBadge.objects.filter(user=user, badge=badge).exists():
                return Response(
                    {"detail": "Dette badgen er allerede fullført"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = UserBadgeSerializer(data=request.data)
            if serializer.is_valid():
                UserBadge(user=user, badge=badge).save()
                return Response(
                    {"detail": "Badge fullført!"}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "Badgen kunne ikke ble opprettet"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except User.DoesNotExist as user_not_exist:
            capture_exception(user_not_exist)
            return Response(
                {"detail": "Kunne ikke finne brukeren"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Badge.DoesNotExist as badge_not_exist:
            capture_exception(badge_not_exist)
            return Response(
                {"detail": "Kunne ikke finne badgen"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as badge_create_fail:
            capture_exception(badge_create_fail)
            return Response(
                {"detail": "Badgen kunne ikke ble opprettet"},
                status=status.HTTP_404_NOT_FOUND,
            )
