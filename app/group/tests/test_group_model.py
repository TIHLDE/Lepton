import pytest

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
