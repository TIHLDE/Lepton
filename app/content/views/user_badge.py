from rest_framework import viewsets
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
                return Response({"detail": "Badge already completed."}, status=400)

            serializer = UserBadgeSerializer(data=request.data)
            if serializer.is_valid():
                UserBadge(user=user, badge=badge).save()
                return Response({"detail": "Badge completed."}, status=201)
            else:
                return Response({"detail": serializer.errors}, status=400)

        except User.DoesNotExist:
            return Response({"detail": "Could not find User"}, status=404)
        except Badge.DoesNotExist:
            return Response({"detail": "Could not find badge"}, status=404)
        except Exception:
            return Response({"detail": "The badge could not be created"}, status=404)
