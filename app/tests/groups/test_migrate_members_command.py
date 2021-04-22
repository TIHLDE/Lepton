from django.core.management import call_command

import pytest

from app.content.factories import UserFactory
from app.content.models import User
from app.group.factories import GroupFactory
from app.group.management.commands.migrate_members import GROUPS_TIHLDE_SLUG
from app.group.models import Membership

pytestmark = pytest.mark.django_db

MIGRATE_COMMAND = "migrate_members"


@pytest.fixture(autouse=True)
def tihlde_group():
    return GroupFactory(name=GROUPS_TIHLDE_SLUG)


def test_migrate_groups_command_migrates_tihlde_members_to_tihlde_group():
    """Test that all TIHLDE members are successfully migrated to the TIHLDE group."""
    batch_size = 10
    UserFactory.create_batch(batch_size, is_TIHLDE_member=True)

    call_command(MIGRATE_COMMAND)

    tihlde_members = User.objects.all()

    assert (
        user.membership.filter(group__slug=GROUPS_TIHLDE_SLUG).exists()
        for user in tihlde_members
    )
    assert Membership.objects.count() == batch_size


def test_migrate_groups_command_does_not_migrates_non_tihlde_members_to_tihlde_group():
    """Test that non-TIHLDE members are not migrated to the TIHLDE group."""
    batch_size = 10
    UserFactory.create_batch(batch_size, is_TIHLDE_member=True)
    UserFactory.create_batch(batch_size, is_TIHLDE_member=False)

    call_command(MIGRATE_COMMAND)

    non_tihlde_members = User.objects.filter(is_TIHLDE_member=False)

    assert (
        not user.membership.filter(group__slug=GROUPS_TIHLDE_SLUG).exists()
        for user in non_tihlde_members
    )


def test_migrate_groups_command_does_not_create_memberships_for_non_tihlde_members():
    """Test that no memberships are created for non-TIHLDE members upon migration."""
    batch_size = 10
    UserFactory.create_batch(batch_size, is_TIHLDE_member=True)
    UserFactory.create_batch(batch_size, is_TIHLDE_member=False)

    call_command(MIGRATE_COMMAND)

    assert Membership.objects.count() == batch_size
