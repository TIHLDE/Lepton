from django.shortcuts import render
from models import Statistics, TimestampedEntry


# Create your views here.
def get_statistics(request, user_id):
    timestamp_id_key = TimestampedEntry.objects.filter(user=user_id).order_by("-year")
    statistics = Statistics.objects.get(id=timestamp_id_key.first())
    print(statistics)
