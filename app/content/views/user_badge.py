from rest_framework import status
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models import Badge, User, UserBadge
from app.content.serializers import UserBadgeSerializer


class UserBadgeViewSet(BaseViewSet):
    serializer_class = UserBadgeSerializer
    permission_classes = [BasicViewPermission]
    queryset = UserBadge.objects.all()
    http_method_names = ["post"]

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
                super().perform_create(serializer, user=user, badge=badge)
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
