from django.db import models

from app.util.models import BaseModel, Gridable, UUIDModel, OptionalImage, OptionalAction


# Create your models here.

class Item(BaseModel, Gridable, UUIDModel):
    pass

class News(Item, OptionalImage):
    title = models.CharField(max_length=200)
    header = models.CharField(max_length=200)
    body = models.TextField()

class EventList(Item):
    """A collection of events to be displayed together"""
    name = models.CharField(max_length=200)

class Event(BaseModel):
    title = models.CharField(max_length=200)
    start = models.DateTimeField()
    location = models.CharField(max_length=200, null=True)
    eventlist = models.ForeignKey(EventList, related_name='events', on_delete=models.CASCADE)

class Poster(Item, OptionalImage, OptionalAction):
    header = models.CharField(max_length=200)
    subheader = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
