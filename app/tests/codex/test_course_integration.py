import pytest

from rest_framework import status

from datetime import timedelta

from django.utils import timezone

from app.codex.enums import CodexGroups
from app.codex.factories import CourseFactory
from app.util.test_utils import add_user_to_group_with_name, get_api_client
from app.common.enums import MembershipType


CODEX_COURSE_BASE_URL = "/codex/courses/"

def get_course_data(
    title: str = "Test Course",
    description: str = "Test Description",
    organizer: str = None,
    lecturer: str = None,
): 
    start_date = timezone.now() + timedelta(days=10)
    end_date = timezone.now() + timedelta(days=11)
    registration_start_at = timezone.now() - timedelta(days=1)
    registration_end_at = timezone.now() + timedelta(days=9)
    sign_off_deadline = timezone.now() + timedelta(days=8)

    data = {
        "title": title,
        "description": description,
        "start_date": start_date,
        "end_date": end_date,
        "start_registration_at": registration_start_at,
        "end_registration_at": registration_end_at,
        "sign_off_deadline": sign_off_deadline,
        "location": "Test Location",
        "maxemap_link": "https://example.com",
    }

    if organizer:
        data["organizer"] = organizer
    if lecturer:
        data["lecturer"] = lecturer
    
    return data


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_list_codex_courses_as_codex_member(
    member,
    codex_group
):
    """A codex member should be able to list all codex courses"""
    add_user_to_group_with_name(member, codex_group)

    CourseFactory.create_batch(5)

    url = CODEX_COURSE_BASE_URL
    client = get_api_client(user=member)
    response = client.get(url)

    count = response.data["count"]
    
    assert response.status_code == status.HTTP_200_OK
    assert count == 5


@pytest.mark.django_db
def test_list_codex_course_as_member(member):
    """A member should not be able to list codex courses"""
    url = CODEX_COURSE_BASE_URL
    client = get_api_client(user=member)
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_retrieve_codex_course_as_member(member, codex_course):
    """A member should not be able to retrieve a codex course"""
    url = f"{CODEX_COURSE_BASE_URL}{codex_course.id}/"
    client = get_api_client(user=member)
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_retrieve_codex_course_as_codex_member(member, codex_group, codex_course):
    """A codex member should be able to retrieve a codex course"""
    add_user_to_group_with_name(member, codex_group)

    url = f"{CODEX_COURSE_BASE_URL}{codex_course.id}/"
    client = get_api_client(user=member)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == codex_course.id


@pytest.mark.django_db
def test_create_codex_course_as_member(member):
    """A member should not be able to create a codex course"""
    url = CODEX_COURSE_BASE_URL
    data = get_course_data()
    client = get_api_client(user=member)
    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_create_codex_course_as_codex_member(member, codex_group):
    """A normal codex member should not be able to create a codex course"""
    add_user_to_group_with_name(member, codex_group)

    url = CODEX_COURSE_BASE_URL
    data = get_course_data(
        organizer=codex_group,
        lecturer=member.user_id
    )
    client = get_api_client(user=member)
    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_create_codex_course_as_codex_group_leader(member, codex_group):
    """A codex group leader should be able to create a codex course"""
    add_user_to_group_with_name(
        member,
        codex_group,
        membership_type=MembershipType.LEADER
    )

    url = CODEX_COURSE_BASE_URL
    data = get_course_data(
        organizer=codex_group,
        lecturer=member.user_id
    )
    client = get_api_client(user=member)
    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_update_codex_course_as_member(member, codex_course):
    """A member should not be able to update a codex course"""
    url = f"{CODEX_COURSE_BASE_URL}{codex_course.id}/"
    data = get_course_data()
    client = get_api_client(user=member)
    response = client.put(url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_update_codex_course_as_codex_member(member, codex_group, codex_course):
    """A codex member should not be able to update a codex course"""
    add_user_to_group_with_name(member, codex_group)

    url = f"{CODEX_COURSE_BASE_URL}{codex_course.id}/"
    data = get_course_data()
    client = get_api_client(user=member)
    response = client.put(url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_update_codex_course_as_codex_group_leader(member, codex_group, codex_course):
    """A codex group leader should be able to update a codex course"""
    add_user_to_group_with_name(
        member,
        codex_group,
        membership_type=MembershipType.LEADER
    )

    url = f"{CODEX_COURSE_BASE_URL}{codex_course.id}/"
    data = get_course_data()
    client = get_api_client(user=member)
    response = client.put(url, data=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == data["title"]


@pytest.mark.django_db
def test_destroy_codex_course_as_member(member, codex_course):
    """A member should not be able to destroy a codex course"""
    url = f"{CODEX_COURSE_BASE_URL}{codex_course.id}/"
    client = get_api_client(user=member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_destroy_codex_course_as_codex_member(member, codex_group, codex_course):
    """A codex member should not be able to destroy a codex course"""
    add_user_to_group_with_name(member, codex_group)

    url = f"{CODEX_COURSE_BASE_URL}{codex_course.id}/"
    client = get_api_client(user=member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_destroy_codex_course_as_codex_group_leader(member, codex_group, codex_course):
    """A codex group leader should be able to destroy a codex course"""
    add_user_to_group_with_name(
        member,
        codex_group,
        membership_type=MembershipType.LEADER
    )

    url = f"{CODEX_COURSE_BASE_URL}{codex_course.id}/"
    client = get_api_client(user=member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK