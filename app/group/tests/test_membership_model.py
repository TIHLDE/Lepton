import pytest

from app.common.enums import MembershipType
from app.group.factories import MembershipFactory
from app.group.factories.group_factory import GroupFactory
from app.group.models.membership import MembershipHistory


@pytest.fixture()
def membership():
    return MembershipFactory(membership_type=MembershipType.MEMBER)


@pytest.fixture()
def membership_leader():
    return MembershipFactory(membership_type=MembershipType.LEADER)


@pytest.fixture()
def group():
    return GroupFactory()


@pytest.mark.django_db
def test_swap_leader_changes_leader(group):
    """
    Tests that swap leader changes the leader of the group,
    when there is a leader and a member
    """
    membership = MembershipFactory(membership_type=MembershipType.MEMBER, group=group)
    membership_leader = MembershipFactory(
        membership_type=MembershipType.LEADER, group=group
    )
    membership.membership_type = MembershipType.LEADER
    membership.save()
    membership.refresh_from_db()
    membership_leader.refresh_from_db()
    assert membership.membership_type == MembershipType.LEADER
    assert membership_leader.membership_type == MembershipType.MEMBER


@pytest.mark.django_db
def test_swap_leader_if_no_leader(group):
    """
    Tests that swap leader changes the leader of the group,
    when there is no leader and a member
    """
    membership = MembershipFactory(membership_type=MembershipType.MEMBER, group=group)
    membership.membership_type = MembershipType.LEADER
    membership.save()
    membership.refresh_from_db()
    assert membership.membership_type == MembershipType.LEADER


@pytest.mark.django_db
def test_create_leader(group):
    """
    Tests that creates a leader to a group
    """
    membership = MembershipFactory(membership_type=MembershipType.LEADER, group=group)
    membership.refresh_from_db()
    assert membership.membership_type == MembershipType.LEADER


@pytest.mark.django_db
def test_swap_leader_does_not_create_two_leaders(group):
    """
    Tests that swap leader changes the leader of the group,
    when there is a leader and a member
    """
    membership = MembershipFactory(membership_type=MembershipType.LEADER, group=group)
    membership_leader = MembershipFactory(
        membership_type=MembershipType.LEADER, group=group
    )
    membership.refresh_from_db()
    membership_leader.refresh_from_db()
    assert membership.membership_type == MembershipType.MEMBER
    assert membership_leader.membership_type == MembershipType.LEADER


@pytest.mark.django_db
def test_on_delete_membership_history_is_created(membership):
    membership.delete()
    assert MembershipHistory.objects.get(start_date=membership.created_at)
