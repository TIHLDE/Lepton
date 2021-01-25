import json

from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

import pytest

from app.common.enums import AdminGroup
from app.content.factories.event_factory import EventFactory
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


def _event_url():
    return "/api/v1/events/"


def _event_detail_url(event):
    return f"{_event_url()}{event.id}/"


def _forms_url():
    return "/api/v1/forms/"


def _form_detail_url(form):
    return f"{_forms_url()}{form.id}/"


def _get_form_post_data(form):
    return {
        # "event": event.pk,
        "allow_photo": False,
    }


# def _get_registration_put_data(user, event):
#    return {
#        **_get_registration_post_data(user, event),
#        "is_on_wait": False,
#        "has_attended": False,
#    }


# GET /events
# Send med formet (read_only)
@pytest.mark.django_db
def test_retrieve_events_does_not_contain_forms():
    event = EventFactory()
    client = _create_user_client(AdminGroup.INDEX)

    response = client.get(_event_url())
    event = response.json()

    assert "forms" not in event


# GET /events/<id>/
# Send med formet (read_only)
# Er brukeren admin?
# Send med all info fra den over (retrieve) pluss brukerens ubesvarte forms
# Dette feltet ligger på brukeren som "request.user.unanswered_forms()"
@pytest.mark.django_db
def test_retrieve_event_detail_has_form_id_equal_to_the_one_provided():
    event = EventFactory()
    client = _create_user_client(AdminGroup.INDEX)

    response = client.get(_event_detail_url(event))
    retrieved_event = response.json()

    form = retrieved_event.get("forms")[0]
    assert form == str(event.forms.get().id)


# PUT /events/<id>/
# Oppdaterer ikke formet (sendes ikke med fra frontend)
@pytest.mark.django_db
def test_update_event_detail_does_not_update_form_ids():
    event = EventFactory()
    client = _create_user_client(AdminGroup.INDEX)

    response = client.put(_event_detail_url(event), {"forms": []}, format="json")
    updated_event = response.json()

    assert updated_event.get("forms") != []


# POST /events/
# Oppdaterer/lager ikke formet (sendes ikke med fra frontend)
@pytest.mark.django_db
def test_create_event():
    raise NotImplementedError()


@pytest.mark.django_db
def test_get_forms():
    raise NotImplementedError()
    form1 = None  # _create_form("foo")
    form2 = None  # _create_form("bar")
    client = _create_user_client(AdminGroup.INDEX)
    response = client.get(_forms_url())
    forms = response.json()
    print(forms)
    assert forms == [
        {
            "id": form1.id,
            "title": form1.title,
            "event": form1.event,
            "type": form1.type,
            "hidden": form1.hidden,
            "fields": form1.fields,
        },
        {
            "id": form2.id,
            "title": form2.title,
            "event": form2.event,
            "type": form2.type,
            "hidden": form2.hidden,
            "fields": form2.fields,
        },
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
