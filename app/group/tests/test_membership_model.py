from django.core.exceptions import ValidationError

import pytest

from app.common.enums import MembershipType
from app.group.factories import MembershipFactory
from app.group.factories.group_factory import GroupFactory
from app.group.models import Membership


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
    membership.swap_board(MembershipType.LEADER)
    membership.refresh_from_db()
    membership_leader.refresh_from_db()
    assert membership.membership_type == MembershipType.LEADER
    assert membership_leader.membership_type == MembershipType.MEMBER


@pytest.mark.django_db
def test_swap_board_raises_validation_error(membership_leader):
    """
    Tests that if a leader tries to use swap_leader,
    the function raises a ValidationError
    """
    with pytest.raises(ValidationError):
        membership_leader.swap_board(MembershipType.LEADER)


@pytest.mark.django_db
def test_swap_board_raises_does_not_exist(membership):
    """
    Tests that if a member tries to use swap_leader,
    when there is no leader in the group it raises a DoesNotExist error
    """
    with pytest.raises(Membership.DoesNotExist):
        membership.swap_board(MembershipType.LEADER)
