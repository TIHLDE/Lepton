from rest_framework import status

import pytest

from app.common.enums import (
    AdminGroup,
    NativeGroupType as GroupType,
    MembershipType
)
from app.content.factories import EventFactory, RegistrationFactory
from app.content.serializers import EventListSerializer
from app.forms.enums import NativeEventFormType as EventFormType
from app.forms.tests.form_factories import EventFormFactory
from app.group.factories import GroupFactory
from app.util.test_utils import add_user_to_group_with_name, get_api_client

pytestmark = pytest.mark.django_db

# "event_organizer" should have one of 3 different values:
# - None -> The event has no connected organizer
# - "same" -> The event is connected to same organizer as user is member of
# - "other" -> The event is connected to another organizer as user i member of
permission_params = pytest.mark.parametrize(
    (
        "organizer_name",
        "organizer_type",
        "membership_type",
        "expected_create_status_code",
        "expected_update_delete_status_code",
        "event_organizer",
    ),
    (
        [AdminGroup.HS, GroupType.BOARD, MembershipType.MEMBER, 201, 200, "same"],
        [AdminGroup.HS, GroupType.BOARD, MembershipType.MEMBER, 201, 200, "other"],
        [AdminGroup.HS, GroupType.BOARD, MembershipType.MEMBER, 201, 200, None],
        [AdminGroup.INDEX, GroupType.SUBGROUP, MembershipType.MEMBER, 201, 200, "same"],
        [
            AdminGroup.INDEX,
            GroupType.SUBGROUP,
            MembershipType.MEMBER,
            201,
            200,
            "other",
        ],
        [AdminGroup.INDEX, GroupType.SUBGROUP, MembershipType.MEMBER, 201, 200, None],
        [AdminGroup.NOK, GroupType.SUBGROUP, MembershipType.MEMBER, 201, 200, "same"],
        [AdminGroup.NOK, GroupType.SUBGROUP, MembershipType.MEMBER, 403, 403, "other"],
        [AdminGroup.NOK, GroupType.SUBGROUP, MembershipType.MEMBER, 201, 200, None],
        ["KontKom", GroupType.COMMITTEE, MembershipType.LEADER, 201, 200, "same"],
        ["Pythons", GroupType.INTERESTGROUP, MembershipType.LEADER, 201, 200, "same"],
        ["KontKom", GroupType.COMMITTEE, MembershipType.LEADER, 201, 200, None],
        ["Pythons", GroupType.INTERESTGROUP, MembershipType.LEADER, 201, 200, None],
        ["KontKom", GroupType.COMMITTEE, MembershipType.LEADER, 403, 403, "other"],
        ["Pythons", GroupType.INTERESTGROUP, MembershipType.LEADER, 403, 403, "other"],
        ["KontKom", GroupType.COMMITTEE, MembershipType.MEMBER, 403, 403, "same"],
        ["Pythons", GroupType.INTERESTGROUP, MembershipType.MEMBER, 403, 403, "same"],
    ),
)


@pytest.fixture
@permission_params
def permission_test_util(
    member,
    organizer_name,
    organizer_type,
    membership_type,
    expected_create_status_code,
    expected_update_delete_status_code,
    event_organizer,
):
    organizer = add_user_to_group_with_name(
        member, organizer_name, organizer_type, membership_type
    )
    if event_organizer == "same":
        event_organizer = organizer
    elif event_organizer == "other":
        event_organizer = GroupFactory()
    event = EventFactory(organizer=event_organizer)
    return (
        member,
        event,
        expected_create_status_code,
        expected_update_delete_status_code,
    )


def _get_forms_url():
    return "/forms/"


def _get_form_detail_url(form):
    return f"{_get_forms_url()}{form.id}/"


def _get_event_form_post_data(form, event):
    return {
        "resource_type": "EventForm",
        "title": form.title,
        "event": event.pk,
        "fields": [],
        "type": "SURVEY",
    }


def _get_event_form_update_data(form, title="New EventForm Title"):
    return {
        "resource_type": "EventForm",
        "title": title,
        "event": form.event.pk,
        "type": "SURVEY",
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
    url = _get_forms_url() + "?all"
    response = client.get(url)
    response = response.json()

    assert (
        response[0]
        | {
            "id": str(form.id),
            "resource_type": "EventForm",
            "title": form.title,
            "event": EventListSerializer(form.event).data,
            "type": form.type,
            "viewer_has_answered": False,
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
                    "type": field.type,
                    "required": field.required,
                    "order": field.order,
                }
            ],
            "template": False,
        }
        == response[0]
    )


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


@permission_params
def test_create_event_form_as_admin(permission_test_util):
    """An admin should be able to create an event form."""
    (
        member,
        event,
        expected_create_status_code,
        expected_update_delete_status_code,
    ) = permission_test_util
    form = EventFormFactory.build()

    client = get_api_client(user=member)
    url = _get_forms_url()
    response = client.post(url, _get_event_form_post_data(form, event))

    assert response.status_code == expected_create_status_code

    if expected_create_status_code == status.HTTP_201_CREATED:
        assert event.forms.filter(title=form.title).exists()


@permission_params
def test_update_event_form_as_admin(permission_test_util):
    """An admin should be able to update an event form."""
    member, event, _, expected_update_delete_status_code = permission_test_util
    form = EventFormFactory(event=event)

    client = get_api_client(user=member)
    url = _get_form_detail_url(form)
    new_title = "New form title"
    response = client.put(url, _get_event_form_update_data(form, new_title))

    assert response.status_code == expected_update_delete_status_code

    if expected_update_delete_status_code == status.HTTP_200_OK:
        assert event.forms.filter(title=new_title).exists()


@permission_params
def test_delete_event_form_as_admin(permission_test_util):
    """An admin should be able to delete an event form."""
    member, event, _, expected_update_delete_status_code = permission_test_util
    form = EventFormFactory(event=event)

    client = get_api_client(user=member)
    url = _get_form_detail_url(form)
    response = client.delete(url)

    assert response.status_code == expected_update_delete_status_code

    if expected_update_delete_status_code == status.HTTP_200_OK:
        assert not event.forms.filter(title=form.title).exists()
