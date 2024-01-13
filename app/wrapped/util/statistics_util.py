from django.shortcuts import render
from app.content.models.registration import Registration
from app.group.models.fine import Fine
from django.db.models import Sum, Avg, Count, Case, When, IntegerField, Q
from django.db.models.functions import Coalesce
from app.wrapped.models import DataDistributions
from app.badge.models.user_badge import UserBadge
from rest_framework.authtoken.models import Token
from app.content.models.user import User
from app.badge.models.user_badge import UserBadge
import numpy as np
from scipy import stats
import traceback


"""
    Calculates the statistics for a single user. This function references the DataDistributions
    model.
"""


def calculate_statistics(user, year):
    try:
        calculate_distributions(year)
        events_count = Registration.objects.filter(
            user=user, event__start_date__year=year, has_attended=True
        ).count()

        fines_count = Fine.objects.filter(user=user, created_at__year=year).count()

        badges_count = UserBadge.objects.filter(
            user=user, created_at__year=year
        ).count()

        events_dist = (
            DataDistributions.objects.filter(year=year)
            .values_list("events_distribution", flat=True)
            .first()
        )

        fines_dist = (
            DataDistributions.objects.filter(year=year)
            .values_list("fines_distribution", flat=True)
            .first()
        )

        badges_dist = (
            DataDistributions.objects.filter(year=year)
            .values_list("badges_distribution", flat=True)
            .first()
        )
    except e:
        print("An exception occured: {e}")
        raise Exception(e)

    statistics = None

    try:
        statistics = {
            "events_attended": events_count,
            "badges_unlocked": badges_count,
            "fines_received": fines_count,
            "events_percentile": None
            if events_dist["std_dev"] == 0
            else round(
                stats.norm.cdf(
                    events_count, events_dist["mean"], events_dist["std_dev"]
                ),
                2,
            ),
            "badges_percentile": None
            if badges_dist["std_dev"] == 0
            else round(
                stats.norm.cdf(
                    badges_count, badges_dist["mean"], badges_dist["std_dev"]
                ),
                2,
            ),
            "fines_percentile": None
            if fines_dist["std_dev"] == 0
            else round(
                stats.norm.cdf(fines_count, fines_dist["mean"], fines_dist["std_dev"]),
                2,
            ),
        }
    except Exception as e:
        traceback.print_exception(e)
        raise Exception(e)

    return statistics


"""
    This method should in theory only be run ONCE per year!
    It calculates standard distributions for several attributes,
    and saves them to the DataDistributions table.
"""


def calculate_distributions(year):
    # Fetch total amount of users in database
    user_count = User.objects.filter(is_active=True).count()

    mean_event_no = mean_events(year, user_count)
    print("Mean number of events this year per user: ", mean_event_no["mean_value"])
    mean_fines_no = mean_fines(year, user_count)
    print("Mean number of fines this year per user: ", mean_fines_no["mean_value"])
    mean_badges_no = mean_badges(year, user_count)
    print("Mean number of badges this year per user: ", mean_badges_no["mean_value"])
    print(mean_fines_no["distributions"])

    event_dev = std_dev(
        [dist["number_of_events"] for dist in mean_event_no["distributions"]]
    )
    fines_dev = std_dev(
        [dist["number_of_fines"] for dist in mean_fines_no["distributions"]]
    )
    badges_dev = std_dev(
        [dist["number_of_badges"] for dist in mean_badges_no["distributions"]]
    )

    DataDistributions.objects.update_or_create(
        year=year,
        defaults={
            "events_distribution": {
                "std_dev": event_dev,
                "mean": mean_event_no["mean_value"],
            },
            "fines_distribution": {
                "std_dev": fines_dev,
                "mean": mean_fines_no["mean_value"],
            },
            "badges_distribution": {
                "std_dev": badges_dev,
                "mean": mean_badges_no["mean_value"],
            },
        },
    )


"""
    Calculates the standard deviation for a given series of numbers.
"""


def std_dev(values):
    # Use numpy to calculate std devitation
    std_dev = np.std(values, ddof=1)
    return std_dev


"""
    Calculates the mean amount of events for all users, and returns the data points as well as the mean
    value in a dictionary
"""


def mean_events(year, user_count):
    result = User.objects.annotate(
        number_of_events=Sum(
            Case(
                When(
                    Q(registrations__event__start_date__year=year)
                    & Q(registrations__has_attended=True),
                    then=1,
                ),
                default=0,
                output_field=IntegerField(),
            )
        )
    ).values("user_id", "number_of_events")

    if user_count == 0:
        return 0

    # return total_events_attended / user_count
    total_events = 0
    for entry in result:
        number_of_events = entry["number_of_events"]
        total_events += number_of_events

    return {"distributions": result, "mean_value": total_events / user_count}


def mean_fines(year, user_count):
    result = User.objects.annotate(
        number_of_fines=Sum(
            Case(
                When(fines__created_at__year=year, then="fines__amount"),
                default=0,
                output_field=IntegerField(),
            )
        )
    ).values("user_id", "number_of_fines")

    total_fines = 0
    for entry in result:
        number_of_fines = entry["number_of_fines"]
        total_fines += number_of_fines

    if user_count == 0:
        return 0

    return {"distributions": result, "mean_value": total_fines / user_count}


"""
    Calculates the mean amount of badges for all users, and returns the data points as well as the mean
    value in a dictionary
"""


def mean_badges(year, user_count):
    result = User.objects.annotate(
        number_of_badges=Sum(
            Case(
                When(
                    user_badges__created_at__year=year,
                    then=1,
                ),
                default=0,
                output_field=IntegerField(),
            )
        )
    ).values("user_id", "number_of_badges")

    total_badges = 0
    for entry in result:
        number_of_events = entry["number_of_badges"]
        total_badges += number_of_events

    if user_count == 0:
        return 0

    return {"distributions": result, "mean_value": total_badges / user_count}
