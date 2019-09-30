from django.db import models

from app.util.models import BaseModel, OptionalImage, OptionalAction

import importlib # RecentFirstGrid
from datetime import datetime, timezone, timedelta

class News(BaseModel, OptionalImage):
    title = models.CharField(max_length=200)
    header = models.CharField(max_length=200)
    body = models.TextField()

    def __str__(self):
        return '{} - {} [{} characters]'.format(self.title,
                                                self.header, len(self.body))

class Category(BaseModel):
    text = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f'{self.text}'

class Event(BaseModel, OptionalImage):
    title = models.CharField(max_length=200)
    start = models.DateTimeField()
    location = models.CharField(max_length=200, null=True)

    description = models.TextField(default='', blank=True)
    sign_up = models.BooleanField(default=False)

    PRIORITIES = (
        (0, 'Low'),
        (1, 'Normal'),
        (2, 'High'),
    )
    priority = models.IntegerField(default=0, choices=PRIORITIES, null=True)

    category = models.ForeignKey(Category, blank=True,
                                    null=True, default=None,
                                    on_delete=models.SET_NULL)
    @property
    def expired(self):
        return self.start <= datetime.now(tz=timezone.utc)-timedelta(days=1)

    def __str__(self):
        return f'{self.title} - starting {self.start} at {self.location}'

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


class JobPost(BaseModel, OptionalImage):
    title = models.CharField(max_length=200)
    ingress = models.CharField(max_length=800)
    body = models.TextField(blank=True, default='')
    location = models.CharField(max_length=200)

    deadline = models.DateTimeField(null=True, blank=True)

    company = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    link = models.URLField(max_length=300, blank=True, null=True)

    @property
    def expired(self):
        return self.deadline <= datetime.now(tz=timezone.utc)-timedelta(days=1)

    def __str__(self):
        return f'JobPost: {self.company}  - {self.title}'


class User(BaseModel, OptionalImage):
    user_id = models.CharField(max_length=15, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    email = models.EmailField(max_length=254)
    cell = models.CharField(max_length=8)

    em_nr = models.CharField(max_length=12)
    home_busstop = models.IntegerField()

    GENDER = (
        (1, 'Mann'),
        (2, 'Kvinne'),
        (3, 'Annet'),
    )
    gender = models.IntegerField(default=0, choices=GENDER, null=True)
    CLASS = (
        (1, 'Første'),
        (2, 'Andre'),
        (3, 'Tredje'),
        (4, 'Fjerde'),
        (5, 'Femte'),
    )
    user_class = models.IntegerField(default=0, choices=CLASS, null=True)

    STUDY = (
        (1, 'Data'),
        (2, 'DigFor'),
        (3, 'Cyber'),
        (4, 'Master'),
    )
    user_study = models.IntegerField(default=0, choices=STUDY, null=True)
    allergy = models.TextField()

    tool = models.CharField(max_length=100)
