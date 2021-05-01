from django.db.transaction import atomic
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from app.group.models import Group, Membership


def get_api_client(user=None, group_name=None):
    client = APIClient()
    if user:
        if group_name:
            add_user_to_group_with_name(user, group_name)
        client.force_authenticate(user=user)
        token = Token.objects.get(user_id=user.user_id)
        client.credentials(HTTP_X_CSRF_TOKEN=token)

    return client


@atomic
def add_user_to_group_with_name(user, group_name):
    # should be changed to our groups later
    group = Group.objects.get_or_create(name=group_name)[0]
    Membership.objects.create(group=group, user=user)
    return user
