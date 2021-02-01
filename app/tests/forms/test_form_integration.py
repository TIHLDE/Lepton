from datetime import timedelta

from django.utils import timezone
from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.content.factories.event_factory import EventFactory
from app.util.test_utils import get_api_client

pytestmark = pytest.mark.django_db


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
        "resource_type": "Form",
        "title": "string",
        "fields": [
            {
                "title": "string",
                "options": [{"title": "string"}],
                "type": "SINGLE_SELECT",
                "required": False,
            }
        ],
    }


# def _get_registration_put_data(user, event):
#    return {
#        **_get_registration_post_data(user, event),
#        "is_on_wait": False,
#        "has_attended": False,
#    }


# GET /events
# Send med formet (read_only)
def test_retrieve_events_does_not_contain_forms():
    event = EventFactory()
    client = get_api_client(AdminGroup.INDEX)

    response = client.get(_event_url())
    event = response.json()

    assert "forms" not in event


# GET /events/<id>/
# Send med formet (read_only)
# Er brukeren admin?
# Send med all info fra den over (retrieve) pluss brukerens ubesvarte forms
# Dette feltet ligger på brukeren som "request.user.unanswered_forms()"
def test_retrieve_event_detail_has_form_id_equal_to_the_one_provided():
    event = EventFactory()
    client = get_api_client(AdminGroup.INDEX)

    response = client.get(_event_detail_url(event))
    retrieved_event = response.json()

    form = retrieved_event.get("forms")[0]
    assert form == str(event.forms.get().id)


# PUT /events/<id>/
# Oppdaterer ikke formet (sendes ikke med fra frontend)
def test_update_event_detail_does_not_update_form_ids():
    event = EventFactory()
    client = get_api_client(AdminGroup.INDEX)

    response = client.put(_event_detail_url(event), {"forms": []}, format="json")
    updated_event = response.json()

    assert updated_event.get("forms") != []


# POST /events/
# Oppdaterer/lager ikke formet (sendes ikke med fra frontend)
def test_create_event():
    client = get_api_client(AdminGroup.INDEX)

    print(
        client.post(
            _event_url(),
            {
                "title": "title",
                "start_date": timezone.now() + timedelta(days=10),
                "end_date": timezone.now() + timedelta(days=11),
                "forms": [],
            },
            format="json",
        ).json()
    )
    raise NotImplementedError()


def test_get_forms():
    raise NotImplementedError()
    form1 = None  # _create_form("foo")
    form2 = None  # _create_form("bar")
    client = get_api_client(AdminGroup.INDEX)
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


def test_list_forms_as_anonymous_user(default_client):
    """An anonymous user should not be able to list forms."""
    url = _forms_url()
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_forms_as_member_is_not_permitted(member):
    """A member should not be able to list forms."""
    client = get_api_client(user=member)
    url = _forms_url()
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "group_name",
    [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.NOK],
)
def test_list_forms_as_member_of_nok_hs_or_index(member, group_name):
    """A user in NOK, HS or Index should be able to list forms."""
    client = get_api_client(user=member, group_name=group_name)
    url = _forms_url()
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "group_name",
    [AdminGroup.SOSIALEN, AdminGroup.PROMO],
)
def test_list_forms_as_member_of_sosialen_or_promo(member, group_name):
    """A user in sosialen or promo should be able to list forms."""
    client = get_api_client(user=member, group_name=group_name)
    url = _forms_url()
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_retrieve_form_as_anonymous_user_is_not_permitted(default_client, form):
    url = _form_detail_url(form)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_retrieve_form_as_member(member, form):
    client = get_api_client(user=member)
    url = _form_detail_url(form)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


def test_retrieve_form_as_member_returns_form(member, form):
    client = get_api_client(user=member)
    url = _form_detail_url(form)
    response = client.get(url)

    actual_form = response.json().get("data").get("form")

    assert actual_form.get("id") == form.form_id


@pytest.mark.parametrize(
    "group_name",
    list(AdminGroup),
)
def test_retrieve_form_as_part_of_admin_group(member, group_name):
    client = get_api_client(user=member, group_name=group_name)
    url = _forms_url()

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


def test_create_forms_as_anonymous_is_not_permitted():
    """An anonymous user should not be able to create forms."""
    raise NotImplementedError()


def test_create_forms_as_member_is_not_permitted(member):
    """A member should not be able to create forms."""
    client = get_api_client(user=member)
    url = _forms_url()
    response = client.post(url, _get_form_post_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "group_name", [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.NOK]
)
def test_create_forms_as_admin_is_permitted(member, group_name):
    """An admin should be able to create forms."""
    client = get_api_client(user=member, group_name=group_name)
    url = _forms_url()
    response = client.post(url, _get_form_post_data())

    assert response.status_code == status.HTTP_201_CREATED


def test_update_form():
    raise NotImplementedError()
