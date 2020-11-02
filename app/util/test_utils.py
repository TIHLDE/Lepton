from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


def get_api_client(user=None, group_name=None):
    client = APIClient()
    if user:
        if group_name:
            add_user_to_group_with_name(user, group_name)
        client.force_authenticate(user=user)
        token = Token.objects.get(user_id=user.user_id)
        client.credentials(HTTP_X_CSRF_TOKEN=token)

    return client


def add_user_to_group_with_name(user, group_name):
    # should be changed to our groups later
    group = Group.objects.create(name=group_name)
    user.groups.add(group)
    return user
