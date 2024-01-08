from django.db import models
from app.content.models.user import User
from app.util.models import BaseModel
import datetime


"""
# Create your models here.
class Statistics(BaseModel):
    id = models.ForeignKey(TimestampedEntry, primary_key=True, on_delete=models.CASCADE)
    fines_received = models.PositiveIntegerField(default=models.SET_NULL)
    badges_unlocked = models.PositiveIntegerField(default=models.SET_NULL)
    events_attended = models.PositiveIntegerField(default=models.SET_NULL)
    fines_percentile = models.FloatField(default=models.SET_NULL)
    badges_percentile = models.FloatField(default=models.SET_NULL)
    events_percentile = models.FloatField(default=models.SET_NULL)
"""


def set_year():
    year = datetime.date.today().year
    return year


class DataDistributions(BaseModel):
    year = models.CharField(primary_key=True, default=set_year, max_length=5)
    events_distribution = models.JSONField(null=False, blank=False)
    fines_distribution = models.JSONField(null=False, blank=False)
    badges_distribution = models.JSONField(null=False, blank=False)
