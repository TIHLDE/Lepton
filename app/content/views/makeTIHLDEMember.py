from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from app.common.enums import Groups
from app.common.permissions import IsDev, IsHS
from app.content.models import User
from app.group.models import Group, Membership


@api_view(["POST"])
@permission_classes((IsHS|IsDev,))
def makeTIHLDEMember(request):
    TIHLDE = Group.objects.get(slug=Groups.TIHLDE)
    user_id = request.data["user_id"]
    user = get_object_or_404(User, user_id=user_id)
    Membership.objects.get_or_create(user=user, group=TIHLDE)
    return Response(
        {"detail": "Brukeren ble lagt til som TIHLDE medlem"},
        status=status.HTTP_200_OK,
    )
