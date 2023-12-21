from django.shortcuts import render
from models import Statistics, TimestampedEntry
from content.models.event import Event
from group.models.fine import Fine
import numpy as np
from scipy import stats
from django.db.models import Sum, Avg


# Create your views here.
def get_statistics_for_user(user_id, year):
    statistics = None

    try:
        timestamp_id_key = TimestampedEntry.objects.filter(user=user_id).order_by(
            "-year"
        )
        statistics = Statistics.objects.get(id=timestamp_id_key.first())
    except Statistics.DoesNotExist:
        pass

    if not statistics:
        # Run a request to the distributions table
        statistics = calculate_statistics(user_id, year)
        statistics.save()

    return statistics


"""
    Calculates the statistics for a single user. This method references the DataDistributions
    model.
"""


def calculate_statistics(user_id, year):
    events_count = Event.objects.filter(user=user_id, created_at__year=year).count()

    fines_count = Event.objects.filter(user=user_id, created_at__year=year).count()

    badges_count = Event.objects.filter(user=user_id, created_at__year=year).count()

    timestamp_id_key = TimestampedEntry.objects.filter(user=user_id).order_by("-year")
    statistics = Statistics.objects.get_or_create(id=timestamp_id_key.first())
    statistics.events_attended = events_count
    statistics.fines_received = fines_count
    statistics.badges_unlocked = badges_count

    statistics.save()
    return statistics


"""
    This method should in theory only be run ONCE per year!
    It calculates standard distributions for several attributes,
    and saves them to the DataDistributions table.
"""


def calculate_distributions(year):
    # Select all fines
    a = 0


def calculate_fine_stats(year):
    # Select all relevant rows
    fines = Fine.objects.filter(created_at__year=year)

    # Group fines by receiving user
    grouped_fines = fines.values("user").annotate(
        total_fines=Sum("amount"), average_fines=Avg("amount")
    )

    print(grouped_fines)
