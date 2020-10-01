from rest_framework import viewsets
from rest_framework.response import Response

from ..models import Challenge, User, UserChallenge
from ..permissions import IsDev, IsMember
from ..serializers import UserChallengeSerializer


class UserChallengeViewSet(viewsets.ModelViewSet):
    serializer_class = UserChallengeSerializer
    permission_classes = [IsDev]
    queryset = UserChallenge.objects.all()

    def get_permissions(self):
        if self.request.method in ["POST"]:
            self.permission_classes = [IsMember]
        return super(UserChallengeViewSet, self).get_permissions()

    def create(self, request):
        try:
            user = User.objects.get(user_id=request.id)
            challenge = Challenge.objects.get(id=request.data.get("challenge_id"))

            if UserChallenge.objects.filter(user=user, challenge=challenge).exists():
                return Response({"detail": "Challenge already completed."}, status=400)

            serializer = UserChallengeSerializer(data=request.data)
            if serializer.is_valid():
                UserChallenge(user=user, challenge=challenge).save()
                return Response({"detail": "Challenge Completed."}, status=200)
            else:
                return Response({"detail": serializer.errors}, status=400)

        except User.DoesNotExist:
            return Response({"detail": "Could not find User"}, status=400)
        except Challenge.DoesNotExist:
            return Response({"detail": "Could not find challenge"}, status=400)
        except Exception as e:
            return Response({"Error": e}, status=404)
