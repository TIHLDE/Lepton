from django.db import models

from app.util.models import BaseModel, Gridable, OptionalImage, OptionalAction

class Item(BaseModel, Gridable):
    pass

class News(Item, OptionalImage):
    title = models.CharField(max_length=200)
    header = models.CharField(max_length=200)
    body = models.TextField()

    def __str__(self):
        return '{} - {} [{} characters]'.format(self.title,
                                                self.header, len(self.body))

class EventList(Item):
    """A collection of events to be displayed together"""
    name = models.CharField(max_length=200)

    def __str__(self):
        num_events = len(Event.objects.all().filter(eventlist=self))
        return '{} [{} events]'.format(self.name, num_events)

class Event(BaseModel):
    title = models.CharField(max_length=200)
    start = models.DateTimeField()
    location = models.CharField(max_length=200, null=True)
    eventlist = models.ForeignKey(EventList,
                                  related_name='events',
                                  on_delete=models.CASCADE)

    def __str__(self):
        fmt_str = '{} - starting {} at {} [{}]'
        return fmt_str.format(self.title, self.start,
                              self.location, self.eventlist.name)


class Poster(Item, OptionalImage, OptionalAction):
    header = models.CharField(max_length=200, blank=True)
    subheader = models.CharField(max_length=200, blank=True)
    color = models.CharField(max_length=7, blank=True)

    def __str__(self):
        fmt_str = '{} - {} - [color {}]'
        return fmt_str.format(self.header, self.subheader, self.color)

