from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

import pytest

from app.common.enums import AdminGroup
from app.content.factories.user_factory import UserFactory
from app.forms.models.forms import Form


def _create_user_client(user_group):
    test_user = UserFactory(
        user_id="dev", password="123", first_name="member", last_name="user"
    )
    test_user.groups.add(Group.objects.create(name=user_group))
    token = Token.objects.get(user_id=test_user.user_id)
    client = APIClient()
    client.credentials(HTTP_X_CSRF_TOKEN=token)
    return client


def _create_form(title, event):
    form = Event(title=title)
    form.save()
    return form


def _forms_url():
    return "/api/v1/forms/"


def _form_detail_url(form):
    return f"{_forms_url()}{form.id}/"


def _get_form_post_data(form):
    return {
        "event": event.pk,
        "allow_photo": False,
    }


def _get_registration_put_data(user, event):
    return {
        **_get_registration_post_data(user, event),
        "is_on_wait": False,
        "has_attended": False,
    }


@pytest.mark.django_db
def test_get_forms():
    form1 = _create_form("foo")
    form2 = _create_form("bar")
    client = _create_user_client(AdminGroup.INDEX)
    response = client.get(_forms_url())
    forms = response.json()
    assert forms == [
        {
            "id": "",
            "title": "",
            "event": "",
            "type": "",
            "hidden": "",
            "fields": "",
        }
    ]
    raise NotImplementedError()


@pytest.mark.django_db
def test_get_forms_permissions(user_group):
    raise NotImplementedError()


@pytest.mark.django_db
def test_get_form():
    raise NotImplementedError()


@pytest.mark.django_db
def test_create_forms():
    raise NotImplementedError()


@pytest.mark.django_db
def test_update_form():
    raise NotImplementedError()
