from django.db import models

from app.util.models import BaseModel, Gridable, OptionalImage, OptionalAction

import importlib # RecentFirstGrid
from datetime import datetime, timezone, timedelta

class Item(BaseModel, Gridable):
    def __str__(self):
        return '{} [{},{} - {}, {}]'.format(self.__class__.__name__, self.height, self.width, self.created_at, self.updated_at)
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

class Category(BaseModel):
    text = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f'{self.text}'

class Event(BaseModel, OptionalImage):
    title = models.CharField(max_length=200)
    start = models.DateTimeField()
    location = models.CharField(max_length=200, null=True)
    eventlist = models.ForeignKey(EventList,
                                  related_name='events',
                                  on_delete=models.CASCADE)
    description = models.TextField(default='', blank=True)
    sign_up = models.BooleanField(default=False)

    PRIORITIES = (
        (0, 'Low'),
        (1, 'Normal'),
        (2, 'High'),
    )
    priority = models.IntegerField(default=0, choices=PRIORITIES, null=True)

    category = models.ForeignKey(Category, related_name='category',blank=True, null=True, on_delete=models.CASCADE)

    @property
    def expired(self):
        return self.start <= datetime.now(tz=timezone.utc)-timedelta(days=1)

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


class Grid(BaseModel):
    """An ordered list of items with a given name."""
    # The name of the grid. e.g. frontpage, news, ...
    name = models.CharField(max_length=200)

    def __str__(self):
        return '{}'.format(self.name)


class ManualGridItem(BaseModel):
    """
    Extra fields on the many-to-many relation between
    Grid and Item.
    """
    grid = models.ForeignKey('ManualGrid', on_delete='CASCADE')
    item = models.ForeignKey(Item, on_delete='CASCADE')

    # The item with the hightest priority will
    # be placed at the top of the grid.
    priority = models.IntegerField()

    class Meta:
        ordering = ['-priority']


class ManualGrid(Grid):
    """A manually ordered grid"""
    items = models.ManyToManyField(Item, through='ManualGridItem')

    def __str__(self):
        return '{} [{} items]'.format(self.name, self.items.all().count())


class RecentFirstGrid(Grid):
    """
    A grid which orders and generates itself automatically based upon the
    creation_time of the item.
    """
    # e.g. 'app.content.Models.News' (subclass of BareModel)
    item_class = models.CharField(max_length=200)

    @property
    def items(self):
        return self.objects.all()

    @property
    def objects(self):
        module_str, class_str = self.item_class.rsplit('.', 1)
        class_ = getattr(importlib.import_module(module_str), class_str)
        return class_.objects

    def __str__(self):
        return '{} [{} - {}]'.format(self.name, self.item_class,
                                     len(self.items))

    class Meta:
        ordering = ['-created_at']


class ImageGallery(Item):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Image(BaseModel):
    image = models.URLField(max_length=400, null=True)
    image_alt = models.CharField(max_length=200, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    gallery = models.ForeignKey(ImageGallery,
                                related_name='images',
                                on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.image} - Created at: {self.created_at}'


class Warning(BaseModel):
    text = models.CharField(max_length=400, null=True)
    TYPES = (
        (0, 'Error'),
        (1, 'Warning'),
        (2, 'Message'),
    )
    type = models.IntegerField(default=0, choices=TYPES, null=True)

    def __str__(self):
        return f'Warning: {self.type} - Text: {self.text}'
