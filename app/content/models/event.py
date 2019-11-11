from django.db import models

from app.util.models import BaseModel, OptionalImage
from app.util.utils import yesterday
from .category import Category
from .user import User


class Event(BaseModel, OptionalImage):
    title = models.CharField(max_length=200)
    start = models.DateTimeField()
    location = models.CharField(max_length=200, null=True)
    description = models.TextField(default='', blank=True)

    PRIORITIES = (
        (0, 'Low'),
        (1, 'Normal'),
        (2, 'High'),
    )
    priority = models.IntegerField(default=0, choices=PRIORITIES, null=True)
    category = models.ForeignKey(Category, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    sign_up = models.BooleanField(default=False)
    limit = models.IntegerField(default=0)
    closed = models.BooleanField(default=False)
    registered_users_list = models.ManyToManyField(User, through='UserEvent', through_fields=('event', 'user'),
                                                   blank=True, default=None)

    @property
    def expired(self):
        return self.start <= yesterday()

    def __str__(self):
        return f'{self.title} - starting {self.start} at {self.location}'
