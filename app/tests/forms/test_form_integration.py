from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.forms.models.forms import Field
from app.forms.tests.form_factories import FieldFactory, FormFactory
from app.util.test_utils import get_api_client

pytestmark = pytest.mark.django_db


def _get_forms_url():
    return "/forms/"


def _get_form_detail_url(form):
    return f"{_get_forms_url()}{form.id}/"


def _get_form_post_data(form):
    return {
        "resource_type": "Form",
        "title": form.title,
        "fields": [
            {
                "title": "string",
                "options": [{"title": "string", "order": 0}],
                "type": "SINGLE_SELECT",
                "required": True,
            }
        ],
    }


def _get_form_template_post_data():
    return {
        "resource_type": "Form",
        "title": "form",
        "fields": [
            {
                "title": "string",
                "options": [{"title": "string", "order": 0}],
                "type": "SINGLE_SELECT",
                "required": True,
                "order": 0,
            }
        ],
        "template": True,
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


def test_create_template_form(admin_user):
    client = get_api_client(user=admin_user)
    form = client.post(_get_forms_url(), _get_form_template_post_data()).json()
    response = client.get(_get_forms_url() + str(form.get("id")) + "/").json()

    assert response == form


def test_list_form_templates_data(admin_user):
    """Should return the correct fields about the forms."""
    form = FormFactory(template=True)
    field = form.fields.first()
    option = field.options.first()

    client = get_api_client(user=admin_user)
    url = _get_forms_url()
    response = client.get(url)
    response = response.json()

    assert (
        response[0]
        | {
            "id": str(form.id),
            "title": form.title,
            "fields": [
                {
                    "id": str(field.id),
                    "title": field.title,
                    "options": [
                        {
                            "id": str(option.id),
                            "title": option.title,
                            "order": option.order,
                        }
                    ],
                    "type": field.type.name,
                    "required": field.required,
                    "order": field.order,
                }
            ],
            "template": True,
            "resource_type": form._meta.object_name,
            "viewer_has_answered": False,
        }
        == response[0]
    )


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
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN),
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
    ],
)
def test_list_forms_as_member_of_board_or_sub_group(
    member, group_name, expected_status_code
):
    """A member of the board or a subgroup should be able to list forms."""
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


def test_retrieve_form_as_member_returns_form(member, form):
    """Test that the correct form is retrieved."""
    client = get_api_client(user=member)
    url = _get_form_detail_url(form)
    response = client.get(url)

    actual_form = response.json()

    assert actual_form.get("id") == str(form.id)


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


@pytest.mark.parametrize("group_name", [AdminGroup.HS, AdminGroup.INDEX])
def test_create_forms_as_admin_is_permitted(form, member, group_name):
    """An admin should be able to create forms."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_forms_url()
    response = client.post(url, _get_form_post_data(form))

    assert response.status_code == status.HTTP_201_CREATED


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
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN),
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
    ],
)
def test_admin_update_form_permissions(form, member, group_name, expected_status_code):
    """HS and Index are allowed to update form, while NoK, Sosialen and Promo are not."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_form_detail_url(form)
    response = client.put(url, _get_form_update_data(form))

    assert response.status_code == expected_status_code


def test_update_form_when_invalid_returns_detail(admin_user, form):
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
        "fields": [
            {
                "id": str(field.id),
                "options": [],
            }
        ],
    }
    client = get_api_client(user=admin_user)
    url = _get_form_detail_url(form)

    client.patch(url, data)
    field.refresh_from_db()

    assert not field.options.exists()


@pytest.mark.django_db
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
                "options": [
                    {
                        "id": str(option.id),
                        "title": updated_title,
                        "order": option.order,
                    },
                ],
                "order": field.order,
            }
        ],
    }
    client = get_api_client(user=admin_user)
    url = _get_form_detail_url(form)
    client.put(url, data)

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
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN),
    ],
)
def test_delete_form_as_member_of_admin_group(
    member, group_name, expected_status_code, form
):
    """Only admins in HS and Index should be allowed to delete forms."""
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


def test_update_form_field_ordering_reorders_fields(api_client, admin_user, form):
    """Test that updating fields work, by flipping order of fields"""
    FieldFactory(form=form)

    client = api_client(user=admin_user)
    url = _get_form_detail_url(form)

    first_in_order, second_in_order = 0, 1
    first_field_in_order, second_field_in_order = form.fields.all()

    expected_field_data = [
        {
            "id": str(first_field_in_order.id),
            "title": "i love this field <3",
            "type": "SINGLE_SELECT",
            "options": [],
            "required": False,
            "order": second_in_order,
        },
        {
            "id": str(second_field_in_order.id),
            "title": "i love this field <3",
            "type": "SINGLE_SELECT",
            "options": [],
            "required": False,
            "order": first_in_order,
        },
    ]
    data = {
        "resource_type": "Form",
        "title": "testform",
        "fields": expected_field_data,
    }

    client.put(url, data)

    first_field_in_order.refresh_from_db()
    second_field_in_order.refresh_from_db()

    assert first_field_in_order.order == second_in_order
    assert second_field_in_order.order == first_in_order
