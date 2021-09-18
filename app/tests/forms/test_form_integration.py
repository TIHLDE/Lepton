from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.content.factories import EventFactory, RegistrationFactory
from app.forms.enums import EventFormType
from app.forms.models.forms import Field
from app.forms.tests.form_factories import EventFormFactory, FormFactory
from app.util.test_utils import get_api_client

pytestmark = pytest.mark.django_db


def _get_forms_url():
    return "/api/v1/forms/"


def _get_form_detail_url(form):
    return f"{_get_forms_url()}{form.id}/"


def _get_form_post_data(form):
    return {
        "resource_type": "Form",
        "title": form.title,
        "fields": [
            {
                "title": "string",
                "options": [{"title": "string"}],
                "type": "SINGLE_SELECT",
                "required": True,
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
        "title": form.title,
        "fields": [
            {
                "title": "another string",
                "options": [{"title": "another string"}],
                "type": "SINGLE_SELECT",
                "required": True,
            }
        ],
    }


def test_list_forms_data(admin_user):
    """Should return the correct fields about the forms."""
    form = EventFormFactory()
    field = form.fields.first()
    option = field.options.first()

    client = get_api_client(user=admin_user)
    url = _get_forms_url()
    response = client.get(url)
    response = response.json()

    assert response[0] == {
        "id": str(form.id),
        "resource_type": "EventForm",
        "title": form.title,
        "event": form.event.id,
        "type": form.type.name,
        "viewer_has_answered": False,
        "fields": [
            {
                "id": str(field.id),
                "title": field.title,
                "options": [{"id": str(option.id), "title": option.title}],
                "type": field.type.name,
                "required": field.required,
            }
        ],
    }


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
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.NOK, status.HTTP_200_OK),
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
    ],
)
def test_list_forms_as_member_of_nok_hs_or_index(
    member, group_name, expected_status_code
):
    """A user in NOK, HS or Index should be able to list forms."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_forms_url()
    response = client.get(url)

    assert response.status_code == expected_status_code


def test_retrieve_form_as_anonymous_user_is_not_permitted(default_client, form):
    """An anonymous user should not be able to retrieve forms."""
    url = _get_form_detail_url(form)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_retrieve_form_as_member(member, form):
    client = get_api_client(user=member)
    url = _get_form_detail_url(form)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()


def test_retrieve_evaluation_event_form_as_member_when_has_attended_event(member):
    """
    A member should be able to retrieve an event form of type evaluation if
    they has attended the event.
    """
    event = EventFactory(limit=1)
    registration = RegistrationFactory(
        user=member, event=event, is_on_wait=False, has_attended=True
    )
    form = EventFormFactory(event=registration.event, type=EventFormType.EVALUATION)

    client = get_api_client(user=member)
    url = _get_form_detail_url(form)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()


def test_retrieve_evaluation_event_form_as_member_when_has_not_attended_event(member):
    """A member should not be able to retrieve an event evaluation form if they have not attended the event."""
    event = EventFactory(limit=1)
    registration = RegistrationFactory(
        user=member, event=event, is_on_wait=False, has_attended=False
    )
    form = EventFormFactory(event=registration.event, type=EventFormType.EVALUATION)

    client = get_api_client(user=member)
    url = _get_form_detail_url(form)
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_retrieve_form_as_member_returns_form(member, form):
    """Test that the correct form is retrieved."""
    client = get_api_client(user=member)
    url = _get_form_detail_url(form)
    response = client.get(url)

    actual_form = response.json()

    assert actual_form.get("id") == str(form.id)


@pytest.mark.parametrize(
    "group_name", list(AdminGroup),
)
def test_retrieve_form_as_part_of_admin_group(member, group_name, form):
    """A member as a part of an admin group should be able to retrieve a form."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_form_detail_url(form)

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()


def test_create_forms_as_anonymous_is_not_permitted(form):
    """An anonymous user should not be able to create forms."""
    client = get_api_client()
    url = _get_forms_url()
    data = _get_form_post_data(form)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_forms_as_member_is_not_permitted(form, member):
    """A member should not be able to create forms."""
    client = get_api_client(user=member)
    url = _get_forms_url()
    response = client.post(url, _get_form_post_data(form))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "group_name", [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.NOK]
)
def test_create_forms_as_admin_is_permitted(form, member, group_name):
    """An admin should be able to create forms."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_forms_url()
    response = client.post(url, _get_form_post_data(form))

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
    data = _get_event_form_post_data(form, event)
    client.post(url, data)

    assert event.forms.filter(title=form.title).exists()


def test_update_form_as_anonymous_is_not_permitted(form, default_client):
    """An anonymous user should not be allowed to update forms."""
    url = _get_form_detail_url(form)
    response = default_client.put(url, _get_form_update_data(form))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_form_as_member_is_not_permitted(member, form):
    """A member should not be allowed to update forms."""
    client = get_api_client(user=member)
    url = _get_form_detail_url(form)
    response = client.put(url, _get_form_update_data(form))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.NOK, status.HTTP_200_OK),
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
    ],
)
def test_admin_update_form_permissions(form, member, group_name, expected_status_code):
    """HS, Index and NoK is allowed to update form, while Sosialen and Promo is not."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_form_detail_url(form)
    response = client.put(url, _get_form_update_data(form))

    assert response.status_code == expected_status_code


def test_update_form_whhen_invalid_returns_detail(admin_user, form):
    """Should return a detail message in the response."""
    client = get_api_client(user=admin_user)
    url = _get_form_detail_url(form)

    response = client.put(url, {})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json().get("detail")


def test_update_form_as_admin_changes_form(admin_user, form):
    """The form should update if an admin updates it."""
    client = get_api_client(user=admin_user)
    url = _get_form_detail_url(form)
    put_data = _get_form_update_data(form)
    client.put(url, put_data)

    form.refresh_from_db()

    assert put_data.get("title") == form.title


def test_update_fields_when_existing_field_is_not_included_in_request_removes_field_from_form(
    admin_user, form
):
    """Test that field that are not included in the request data are removed from the form."""
    client = get_api_client(user=admin_user)
    url = _get_form_detail_url(form)
    data = {
        "resource_type": "Form",
        "id": str(form.id),
        "title": "test",
        "fields": [],
    }
    client.patch(url, data)

    form.refresh_from_db()

    assert not form.fields.exists()


def test_update_fields_when_id_is_passed_in_field_request_data_updates_the_field(
    admin_user, form
):
    """Test that the field is updated when the field id is not included in the request data."""
    client = get_api_client(user=admin_user)
    url = _get_form_detail_url(form)
    field = Field.objects.get(form=form.id)
    expected_field_data = {
        "id": str(field.id),
        "title": "i love this field <3",
        "type": "SINGLE_SELECT",
        "options": [],
        "required": False,
    }
    data = {
        "resource_type": "Form",
        "title": "testform",
        "fields": [{**expected_field_data}],
    }

    response = client.patch(url, data)
    response = response.json()
    field_resp = response["fields"][0]

    actual_field_data = {key: field_resp[key] for key in expected_field_data.keys()}

    assert actual_field_data == expected_field_data


def test_update_field_when_id_is_not_passed_in_field_request_data_adds_new_field(
    admin_user, form
):
    """Test that new fields are added when the field id is not included in the request data."""
    form.fields.all().delete()

    client = get_api_client(user=admin_user)
    url = _get_form_detail_url(form)
    data = {
        "resource_type": "Form",
        "title": "test",
        "fields": [
            {
                "title": "string",
                "options": [{"title": "string"}],
                "type": "SINGLE_SELECT",
                "required": False,
            }
        ],
    }

    client.patch(url, data)
    form.refresh_from_db()

    assert form.fields.count() == 1


def test_update_options_when_previous_option_is_not_included_in_request_removes_option_from_field(
    admin_user, form
):
    """Options that are not included in the request data are removed from the form fields."""
    field = form.fields.first()
    data = {
        "resource_type": "Form",
        "fields": [{"id": str(field.id), "options": [],}],
    }
    client = get_api_client(user=admin_user)
    url = _get_form_detail_url(form)

    client.patch(url, data)
    field.refresh_from_db()

    assert not field.options.exists()


def test_update_options_when_id_is_passed_in_options_request_data_updates_the_option(
    admin_user, form
):
    """Test that the option is updated when the option id is included in the request data."""
    field = form.fields.first()
    option = field.options.first()
    updated_title = "Test"

    data = {
        "resource_type": "Form",
        "fields": [
            {
                "id": str(field.id),
                "options": [{"id": str(option.id), "title": updated_title,},],
            }
        ],
    }
    client = get_api_client(user=admin_user)
    url = _get_form_detail_url(form)
    client.patch(url, data)

    option.refresh_from_db()

    assert option.title == updated_title


def test_update_option_when_id_is_not_passed_in_options_request_data_adds_new_option(
    admin_user, form
):
    """Test that new options are added when the option id is not included in the request data."""
    field = form.fields.first()
    field.options.all().delete()

    client = get_api_client(user=admin_user)
    url = _get_form_detail_url(form)
    data = {
        "resource_type": "Form",
        "fields": [
            {
                "id": field.id,
                "title": "string",
                "options": [{"title": "string"}],
                "type": "SINGLE_SELECT",
                "required": False,
            }
        ],
    }

    client.patch(url, data)
    field.refresh_from_db()

    assert field.options.count() == 1


def test_delete_form_as_anonymous_is_not_permitted(default_client, form):
    """Anonymous users should not be allowed to delete forms."""
    url = _get_form_detail_url(form)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_form_as_member_is_not_permitted(member, form):
    """Members should not be allowed to delete forms."""
    client = get_api_client(user=member)
    url = _get_form_detail_url(form)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.NOK, status.HTTP_200_OK),
    ],
)
def test_delete_form_as_member_of_admin_group(
    member, group_name, expected_status_code, form
):
    """Only admins in HS, Index and Nok should be allowed to delete forms."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_form_detail_url(form)
    response = client.delete(url)

    assert response.status_code == expected_status_code


def test_delete_form_returns_detail(admin_user, form):
    """Test that deleting a forms returns a response detail."""
    client = get_api_client(user=admin_user)
    url = _get_form_detail_url(form)
    response = client.delete(url)

    assert response.data.get("detail")
