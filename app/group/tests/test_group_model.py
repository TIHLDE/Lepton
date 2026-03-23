import pytest
from django.core.exceptions import ValidationError

from app.common.enums import NativeGroupType as GroupType
from app.common.enums import NativeInterestGroupType as InterestGroupType
from app.content.factories.user_factory import UserFactory
from app.group.factories.group_factory import GroupFactory


@pytest.fixture()
def user():
    return UserFactory()


@pytest.fixture()
def group():
    return GroupFactory()


@pytest.mark.django_db
def test_check_fines_admin_does_not_send_mail_if_no_update(group):
    assert not group.check_fine_admin()


@pytest.mark.django_db
def test_check_fines_admin_does_sends_mail_if_update(group, user):
    group.fines_admin = user
    assert group.check_fine_admin()


@pytest.mark.django_db
def test_check_fines_admin_does_not_send_mail_if_admin_is_none(group):
    group.fines_admin = None
    assert not group.check_fine_admin()


@pytest.mark.django_db
def test_clean_raises_validation_error_if_subtype_set_for_non_interest_group():
    group = GroupFactory.build(
        type=GroupType.SUBGROUP,
        subtype=InterestGroupType.GRUPPE,
    )
    with pytest.raises(ValidationError) as exc_info:
        group.clean()
    assert "subtype" in exc_info.value.message_dict


@pytest.mark.django_db
def test_clean_does_not_raise_if_subtype_set_for_interest_group():
    group = GroupFactory.build(
        type=GroupType.INTERESTGROUP,
        subtype=InterestGroupType.GRUPPE,
    )
    group.clean()  # Should not raise


@pytest.mark.django_db
def test_clean_does_not_raise_if_subtype_is_none_for_non_interest_group():
    group = GroupFactory.build(
        type=GroupType.SUBGROUP,
        subtype=None,
    )
    group.clean()  # Should not raise


@pytest.mark.django_db
def test_save_raises_validation_error_if_subtype_set_for_non_interest_group():
    group = GroupFactory.build(
        type=GroupType.SUBGROUP,
        subtype=InterestGroupType.GRUPPE,
    )
    with pytest.raises(ValidationError):
        group.save()

