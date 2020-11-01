from rest_framework import status, viewsets
from rest_framework.response import Response

from ..models import Badge, User, UserBadge
from ..permissions import IsDev, IsMember
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

            if UserBadge.objects.get(user=user, badge=badge).exists():
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
                    {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )

        except User.DoesNotExist:
            return Response(
                {"detail": "Kunne ikke finne brukeren"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Badge.DoesNotExist:
            return Response(
                {"detail": "Kunne ikke finne badgen"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception:
            return Response(
                {"detail": "Badgen kunne ikke ble opprettet"},
                status=status.HTTP_404_NOT_FOUND,
            )
