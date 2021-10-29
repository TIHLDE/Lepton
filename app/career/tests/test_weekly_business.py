import pytest

from app.career.factories import WeeklyBusinessFactory
from app.util import now


@pytest.fixture()
def weekly_business():
    return WeeklyBusinessFactory(week=5)


@pytest.mark.django_db
def test_update_weekly_business(weekly_business):
    """
    Test if possible to update weekly_business
    """
    weekly_business.business_name = "Index"
    weekly_business.save()

    assert weekly_business.business_name == "Index"
    assert weekly_business.week == 5


@pytest.mark.django_db
def test_create_weekly_business_on_free_week(weekly_business):
    """
    Test if possible to create weekly_business object on a free week
    """
    second_weekly_business = WeeklyBusinessFactory(week=6)

    assert weekly_business.week == 5
    assert second_weekly_business.week == 6


@pytest.mark.django_db
def test_create_weekly_business_on_taken_week(weekly_business):
    """
    Test if possible to create weekly_business object on a taken week
    """
    with pytest.raises(ValueError) as v_err:
        WeeklyBusinessFactory(week=5)

    assert "Finnes allerede en ukens bedrift for denne uken" == str(v_err.value)


@pytest.mark.django_db
def test_update_weekly_business_to_free_week(weekly_business):
    """
    Test if possible to update weekly_business object to a free week
    """
    second_weekly_business = WeeklyBusinessFactory(week=6)
    second_weekly_business.week = 7
    second_weekly_business.save()

    assert weekly_business.week == 5
    assert second_weekly_business.week == 7


@pytest.mark.django_db
def test_update_weekly_business_to_taken_week(weekly_business):
    """
    Test if possible to update weekly_business object to a taken week
    """
    with pytest.raises(ValueError) as v_err:
        second_weekly_business = WeeklyBusinessFactory(week=6)
        second_weekly_business.week = 5
        second_weekly_business.save()

    assert "Finnes allerede en ukens bedrift for denne uken" == str(v_err.value)


@pytest.mark.django_db
def test_create_weekly_business_on_edge_week_number():
    """
    Test if possible to create weekly_business object on week 1 and 52
    """
    weekly_business = WeeklyBusinessFactory(week=1)
    second_weekly_business = WeeklyBusinessFactory(week=52)

    assert weekly_business.week == 1
    assert second_weekly_business.week == 52


@pytest.mark.django_db
def test_create_weekly_business_non_existing_week_number():
    """
    Test if possible to create weekly_business object on non existing week numbers
    """
    with pytest.raises(ValueError) as v_err_lt:
        WeeklyBusinessFactory(week=0)
    with pytest.raises(ValueError) as v_err_gt:
        WeeklyBusinessFactory(week=53)

    assert "Uke må være mellom 1 og 52" == str(v_err_lt.value)
    assert "Uke må være mellom 1 og 52" == str(v_err_gt.value)


@pytest.mark.django_db
def test_update_weekly_business_to_non_existing_week_number():
    """
    Test if possible to update weekly_business object to non existing week numbers
    """
    with pytest.raises(ValueError) as v_err_lt:
        weekly_business = WeeklyBusinessFactory(week=7)
        weekly_business.week = 0
        weekly_business.save()
    with pytest.raises(ValueError) as v_err_gt:
        weekly_business = WeeklyBusinessFactory(week=6)
        weekly_business.week = 53
        weekly_business.save()

    assert "Uke må være mellom 1 og 52" == str(v_err_lt.value)
    assert "Uke må være mellom 1 og 52" == str(v_err_gt.value)


@pytest.mark.django_db
def test_create_weekly_business_this_year(weekly_business):
    """
    Test if possible to create weekly_business object this year
    """
    assert weekly_business.year == now().year + 1


@pytest.mark.django_db
def test_create_weekly_business_next_year():
    """
    Test if possible to create weekly_business object next year
    """
    weekly_business = WeeklyBusinessFactory(year=(now().year) + 1)
    assert weekly_business.year == (now().year) + 1


@pytest.mark.django_db
def test_create_weekly_business_last_year():
    """
    Test if possible to create weekly_business object last year
    """
    with pytest.raises(ValueError) as v_err:
        WeeklyBusinessFactory(year=(now().year) - 1)
    assert "Ukens bedrift kan ikke opprettes i fortiden" == str(v_err.value)
