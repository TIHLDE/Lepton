from django.core.management import call_command

import pytest

from app.common.enums import GroupType
from app.content.factories import UserFactory
from app.group.models import Group, Membership

pytestmark = pytest.mark.django_db


MIGRATE_COMMAND = "migrate_users"


@pytest.mark.parametrize(
    ("user_class", "group_name"),
    [(-1, "Alumni"), (1, "2021"), (2, "2020"), (3, "2019"), (4, "2018"), (5, "2017"),],
)
def test_that_users_are_migrated_to_correct_study_year_group(user_class, group_name):
    batch_size = 10
    users = UserFactory.create_batch(batch_size, user_class=user_class)

    call_command(MIGRATE_COMMAND)

    assert (user.membership.filter(group__slug=group_name).exists() for user in users)
    assert (
        Membership.objects.filter(group__type=GroupType.STUDYYEAR).count() == batch_size
    )


@pytest.mark.parametrize(
    ("user_class", "group_name"),
    [(-1, "Alumni"), (1, "2021"), (2, "2020"), (3, "2019"), (4, "2018"), (5, "2017"),],
)
def test_that_study_year_groups_are_created_with_correct_name_and_type(
    user_class, group_name
):
    batch_size = 10
    UserFactory.create_batch(batch_size, user_class=user_class)

    call_command(MIGRATE_COMMAND)

    group = Group.objects.filter(name=group_name).first()

    assert group
    assert group.type == GroupType.STUDYYEAR


@pytest.mark.parametrize(
    ("user_study", "group_name"),
    [
        (1, "Dataingeniør"),
        (2, "Digital forretningsutvikling"),
        (3, "Digital infrastruktur og cybersikkerhet"),
        (4, "Digital samhandling"),
        (5, "Drift"),
        (6, "Informasjonsbehandling"),
    ],
)
def test_that_users_are_migrated_to_correct_study_group(user_study, group_name):
    batch_size = 10
    users = UserFactory.create_batch(batch_size, user_study=user_study)

    call_command(MIGRATE_COMMAND)

    assert (user.membership.filter(group__slug=group_name).exists() for user in users)
    assert Membership.objects.filter(group__type=GroupType.STUDY).count() == batch_size


@pytest.mark.parametrize(
    ("user_study", "group_name"),
    [
        (1, "Dataingeniør"),
        (2, "Digital forretningsutvikling"),
        (3, "Digital infrastruktur og cybersikkerhet"),
        (4, "Digital samhandling"),
        (5, "Drift"),
        (6, "Informasjonsbehandling"),
    ],
)
def test_that_study_groups_are_created_with_correct_name_and_type(
    user_study, group_name
):
    batch_size = 10
    UserFactory.create_batch(batch_size, user_study=user_study)

    call_command(MIGRATE_COMMAND)

    group = Group.objects.filter(name=group_name).first()

    assert group
    assert group.type == GroupType.STUDY


def test_that_memberships_are_created_for_both_year_and_study():
    batch_size = 10
    UserFactory.create_batch(batch_size)

    call_command(MIGRATE_COMMAND)

    assert Membership.objects.count() == batch_size * 2