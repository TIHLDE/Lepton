from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.content.factories import EventFactory
from app.forms.tests.form_factories import FormFactory
from app.util.test_utils import get_api_client

pytestmark = pytest.mark.django_db


def _get_forms_url():
    return "/api/v1/forms/"


def _get_form_detail_url(form):
    return f"{_get_forms_url()}{form.id}/"


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


def _get_event_form_post_data(form, event):
    return {
        "resource_type": "EventForm",
        "title": form.title,
        "event": event.pk,
        "fields": [],
    }


def _get_form_update_data(form):
    return {
        "resource_type": "Form",
        "title": "another string",
        "fields": [
            {
                "title": "another string",
                "options": [{"title": "another string"}],
                "type": "SINGLE_SELECT",
                "required": True,
            }
        ],
    }


def test_list_forms_data(user):
    """Should return the correct fields about the forms."""
    form = FormFactory()
    other_form = FormFactory()
    client = get_api_client(user=user)
    response = client.get(_get_form_detail_url())
    forms = response.json()

    assert forms == [
        {
            "id": form.id,
            "title": form.title,
            "event": form.event,
            "type": form.type,
            "fields": form.fields,
        },
        {
            "id": other_form.id,
            "title": other_form.title,
            "event": other_form.event,
            "type": other_form.type,
            "fields": other_form.fields,
        },
    ]


def test_list_forms_as_anonymous_user_is_not_permitted(default_client):
    """An anonymous user should not be able to list forms."""
    url = _get_forms_url()
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_forms_as_member_is_not_permitted(member):
    """A member should not be able to list forms."""
    client = get_api_client(user=member)
    url = _get_forms_url()
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "group_name",
    [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.NOK],
)
def test_list_forms_as_member_of_nok_hs_or_index(member, group_name):
    """A user in NOK, HS or Index should be able to list forms."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_forms_url()
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()


@pytest.mark.parametrize(
    "group_name",
    [AdminGroup.SOSIALEN, AdminGroup.PROMO],
)
def test_list_forms_as_member_of_sosialen_or_promo(member, group_name):
    """A user in sosialen or promo should be able to list forms."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_forms_url()
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()


def test_retrieve_form_as_anonymous_user_is_not_permitted(default_client, form):
    """An anomymous user should not be able to retrieve forms."""
    url = _get_form_detail_url(form)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_retrieve_form_as_member(member, form):
    client = get_api_client(user=member)
    url = _get_form_detail_url(form)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()


def test_retrieve_form_as_member_returns_form(member, form):
    """Test that the correct form is retrieved."""
    client = get_api_client(user=member)
    url = _get_form_detail_url(form)
    response = client.get(url)

    actual_form = response.json().get("data").get("form")

    assert actual_form.get("id") == form.form_id


@pytest.mark.parametrize(
    "group_name",
    list(AdminGroup),
)
def test_retrieve_form_as_part_of_admin_group(member, group_name, form):
    """A member as a part of an admin group should be able to retrieve a form."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_form_detail_url(form)

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()


def test_create_forms_as_anonymous_is_not_permitted(member):
    """An anonymous user should not be able to create forms."""
    client = get_api_client(user=member)
    url = _get_forms_url()
    response = client.post(url, _get_form_post_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_forms_as_member_is_not_permitted(member):
    """A member should not be able to create forms."""
    client = get_api_client(user=member)
    url = _get_forms_url()
    response = client.post(url, _get_form_post_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "group_name", [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.NOK]
)
def test_create_forms_as_admin_is_permitted(member, group_name):
    """An admin should be able to create forms."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_forms_url()
    response = client.post(url, _get_form_post_data())

    assert response.status_code == status.HTTP_201_CREATED


def test_create_event_form_as_admin(admin_user):
    """An admin should be able to create an event form."""
    form = FormFactory.build()
    event = EventFactory()

    client = get_api_client(user=admin_user)
    url = _get_forms_url()
    response = client.post(url, _get_event_form_post_data(form, event))

    assert response.status_code == status.HTTP_201_CREATED


def test_create_event_form_as_admin_adds_the_form_to_the_event(admin_user, event):
    """The form created should be connected to the event."""
    form = FormFactory.build()

    client = get_api_client(user=admin_user)
    url = _get_forms_url()
    client.post(url, _get_event_form_post_data(form, event))

    assert event.forms.count() == 1
    assert event.forms.first().title == form.title


def test_update_form_as_anonymous_is_not_permitted(default_client):
    """An anonymous user should not be allowed to update forms."""
    url = _get_forms_url()
    response = default_client.put(url, _get_form_update_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_form_as_member_is_not_permitted(member):
    """A member should not be allowed to update forms."""
    client = get_api_client(user=member)
    url = _get_forms_url()
    response = client.put(url, _get_form_update_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "group_name",
    [AdminGroup.SOSIALEN, AdminGroup.PROMO],
)
def test_update_form_as_sosialen_or_promo_is_not_permitted(member, group_name):
    """A member of sosialen or promo should not be allowed to update forms."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_forms_url()
    response = client.put(url, _get_form_update_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "group_name", [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.NOK]
)
def test_update_form_as_hs_index_or_nok_is_permitted(member, group_name):
    """An admin from HS, Index or NoK should not be allowed to update forms."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_forms_url()
    response = client.put(url, _get_form_update_data())

    assert response.status_code == status.HTTP_200_OK


def test_update_form_as_admin_changes_form(admin_user, form):
    """The form should update if an admin updates it."""
    client = get_api_client(user=admin_user)
    url = _get_form_detail_url(form)
    put_data = _get_form_update_data()
    client.put(url, put_data)

    form.refresh_from_db()

    assert put_data.title == form.title


def test_update_fields_when_existing_field_is_not_included_in_request_removes_field_from_form(
    admin_user, form
):
    """Thest that field that are not included in the request data are removed from the form."""
    client = get_api_client(user=admin_user)
    url = _get_form_detail_url(form)
    data = {
        "resource_type": "Form",
        "title": "test",
        "fields": [],
    }
    client.put(url, data)

    form.refresh_from_db()

    assert not form.fields.exists()


def test_update_fields_when_id_is_passed_in_field_request_data_updates_the_field():
    """Test that the field is updated when the field id is not included in the request data."""
    raise NotImplementedError()


def test_update_field_when_id_is_not_passed_in_field_request_data_adds_new_field():
    """Test that new fields are added when the field id is not included in the request data."""
    raise NotImplementedError()


def test_update_options_when_previous_option_is_not_included_in_request_removes_option_from_field():
    """Options that are not included in the request data are removed from the form fields."""
    raise NotImplementedError()


def test_update_options_when_id_is_passed_in_options_request_data_updates_the_option():
    """Test that the option is updated when the option id is not included in the request data."""
    raise NotImplementedError()


def test_update_option_when_id_is_not_passed_in_options_request_data_adds_new_option():
    """Test that new options are added when the option id is not included in the request data."""
    raise NotImplementedError()


def test_delete_form_as_anonymous_is_not_permitted(default_client):
    """Anonymous users should not be allowed to delete forms."""
    url = _get_forms_url()
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_form_as_member_is_not_permitted(member):
    """Members should not be allowed to delete forms."""
    client = get_api_client(user=member)
    url = _get_forms_url()
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "group_name",
    [AdminGroup.SOSIALEN, AdminGroup.PROMO],
)
def test_delete_form_as_sosialen_or_promo_is_not_permitted(member, group_name):
    """Admins in Sosialen and Promo should not be allowed to delete forms."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_forms_url()
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "group_name", [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.NOK]
)
def test_delete_form_as_hs_index_or_nok_is_permitted(member, group_name):
    """Admins in HS, Index or NoK should be allowed to delete forms."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_forms_url()
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK
