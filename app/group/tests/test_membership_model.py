import pytest

from app.common.enums import (
    AdminGroup,
    NativeGroupType as GroupType,
    MembershipType
)
from app.group.factories import MembershipFactory
from app.group.factories.group_factory import GroupFactory
from app.group.models.membership import Membership, MembershipHistory


@pytest.fixture()
def membership():
    return MembershipFactory(membership_type=MembershipType.MEMBER)


@pytest.fixture()
def membership_leader():
    return MembershipFactory(membership_type=MembershipType.LEADER)


@pytest.fixture()
def group():
    return GroupFactory()


@pytest.fixture()
def hs():
    return GroupFactory(name=AdminGroup.HS, slug=AdminGroup.HS)


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
    assert MembershipHistory.objects.filter(start_date=membership.created_at).exists()


@pytest.mark.django_db
def test_on_swap_creates_hs_membership_with_no_leader(hs):
    """ "
    Tests that if you promote as user to leader of a subgroup with no leader,
    the user is automaticly added to the HS group
    """
    group = GroupFactory(type=GroupType.SUBGROUP)
    membership = MembershipFactory(membership_type=MembershipType.MEMBER, group=group)
    membership.membership_type = MembershipType.LEADER
    membership.save()
    membership.refresh_from_db()
    assert membership.membership_type == MembershipType.LEADER
    assert Membership.objects.filter(user=membership.user, group=hs).exists()


@pytest.mark.django_db
def test_on_swap_creates_hs_membership_with_leader(hs):
    """
    Tests that if you promote as user to leader of a subgroup,
    the user is automaticly added to the HS group
    """
    group = GroupFactory(type=GroupType.SUBGROUP)
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
    assert Membership.objects.filter(user=membership.user, group=hs).exists()


@pytest.mark.django_db
def test_on_remove_leader_without_swap_removes_hs(hs):
    """
    Tests that if you demote as user from leader to member of a subgroup,
    the user is automaticly removed from the HS group
    """
    group = GroupFactory(type=GroupType.SUBGROUP)
    membership = MembershipFactory(membership_type=MembershipType.LEADER, group=group)
    membership.membership_type = MembershipType.MEMBER
    membership.save()
    membership.refresh_from_db()
    assert membership.membership_type == MembershipType.MEMBER
    assert not Membership.objects.filter(user=membership.user, group=hs).exists()


@pytest.mark.django_db
def test_on_swap_leader_with_non_subgroup_group(hs):
    """
    Tests that if you promote a user to leader of a non subgroup group a hs membership vil not me created
    """
    group = GroupFactory(type=GroupType.COMMITTEE)
    membership = MembershipFactory(membership_type=MembershipType.LEADER, group=group)
    membership.membership_type = MembershipType.MEMBER
    membership.save()
    membership.refresh_from_db()
    assert membership.membership_type == MembershipType.MEMBER
    assert not Membership.objects.filter(user=membership.user, group=hs).exists()
