from django.contrib.auth.models import Group
from rest_framework.test import force_authenticate

import pytest

from app.common.enums import AdminGroup
from app.content.views import EventViewSet


def add_user_to_group_with_name(user, group_name):
    group = Group.objects.create(name=group_name)
    user.groups.add(group)


def get_response(request, user=None, event=None):
    """
    Converts a request to a response.

    :param request: the desired HTTP-request.
    :param user: the user performing the request. None represents an anonymous user
    :param event: the desired event. None represents all events.
    :return: the HTTP-response from Django.
    """

    force_authenticate(request, user=user)

    if event:
        view = EventViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        )
        return view(request, pk=event.pk)
    else:
        view = EventViewSet.as_view(
            {"get": "list", "put": "update", "delete": "destroy"}
        )
        return view(request)


@pytest.mark.django_db
def test_list_as_anonymous_user(request_factory):
    """An anonymous user should be able to list all events."""

    request = request_factory.get("/events/")
    response = get_response(request=request)

    assert response.status_code == 200


@pytest.mark.django_db
def test_retrieve_as_anonymous_user(request_factory, event):
    """An anonymous user should be able to retrieve an event."""

    request = request_factory.get(f"/events/{event.pk}/")
    response = get_response(request=request, event=event)

    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [(AdminGroup.HS, 200), (AdminGroup.INDEX, 200),],
)
def test_retrieve_as_admin_user(
    request_factory, event, user, token, group_name, expected_status_code
):
    """An admin user should be able to retrieve an event with more data."""

    add_user_to_group_with_name(user, group_name)

    request = request_factory.get(f"/events/{event.pk}/", HTTP_X_CSRF_TOKEN=token.key)
    response = get_response(request=request, user=user, event=event)

    assert response.status_code == expected_status_code
    assert "evaluate_link" in response.data.keys()


@pytest.mark.django_db
def test_update_as_anonymous_user(request_factory, event):
    """An anonymous user should not be able to update an event entity."""

    data = {"title": "new_title", "location": "new_location"}

    request = request_factory.put(f"/events/{event.pk}/", data=data)
    response = get_response(request=request, event=event)

    assert response.status_code == 403


@pytest.mark.django_db
def test_update_as_user(request_factory, event, user):
    """A user should not be able to update an event entity."""

    data = {"title": "new_title", "location": "new_location"}

    request = request_factory.put(f"/events/{event.pk}/", data=data)
    response = get_response(request=request, user=user, event=event)

    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code", "new_title"),
    [
        (AdminGroup.HS, 200, "New Title"),
        (AdminGroup.INDEX, 200, "New Title"),
        (AdminGroup.NOK, 200, "New Title"),
        (AdminGroup.PROMO, 200, "New Title"),
        ("Non_admin_group", 403, None),
    ],
)
def test_update_as_admin_user(
    request_factory, event, user, token, group_name, expected_status_code, new_title
):
    """Only users in an admin group should be able to update an event entity."""

    add_user_to_group_with_name(user, group_name)
    expected_title = new_title if new_title else event.title

    data = {
        "id": event.pk,
        "title": "New Title",
        "location": "New Location",
        "registration_priorities": [{"user_class": 1, "user_study": 1}],
    }

    request = request_factory.put(
        f"/events/{event.pk}/", data=data, format="json", HTTP_X_CSRF_TOKEN=token.key
    )
    response = get_response(request=request, user=user, event=event)
    event.refresh_from_db()

    assert response.status_code == expected_status_code
    assert event.title == expected_title


@pytest.mark.django_db
def test_delete_as_anonymous_user(request_factory, event):
    """An anonymous user should not be able to delete an event entity."""

    request = request_factory.delete(f"/events/{event.pk}/")
    response = get_response(request=request, event=event)

    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_as_user(request_factory, user, event):
    """A user should not be able to to delete an event entity."""

    request = request_factory.delete(f"/events/{event.pk}/")
    response = get_response(request=request, user=user, event=event)

    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, 200),
        (AdminGroup.INDEX, 200),
        (AdminGroup.NOK, 200),
        (AdminGroup.PROMO, 200),
        ("Non_admin_group", 403),
    ],
)
def test_delete_as_group_members(
    request_factory, event, user, token, group_name, expected_status_code
):
    """Only users in an admin group should be able to delete an event entity."""

    add_user_to_group_with_name(user, group_name)

    request = request_factory.delete(
        f"/events/{event.pk}/", HTTP_X_CSRF_TOKEN=token.key
    )
    response = get_response(request=request, user=user, event=event)

    assert response.status_code == expected_status_code
