from django.db import models

from app.util.models import BaseModel, OptionalImage

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
    cell = models.CharField(max_length=8, blank=True)

    em_nr = models.CharField(max_length=12, blank=True)
    home_busstop = models.IntegerField(null=True, blank=True)

    GENDER = (
        (1, 'Mann'),
        (2, 'Kvinne'),
        (3, 'Annet'),
    )
    gender = models.IntegerField(default=0, choices=GENDER, null=True, blank=True)
    CLASS = (
        (1, '1. Klasse'),
        (2, '2. Klasse'),
        (3, '3. Klasse'),
        (4, '4. Klasse'),
        (5, '5. Klasse'),
    )
    user_class = models.IntegerField(default=1, choices=CLASS, null=True, blank=True)

    STUDY = (
        (1, 'Dataing'),
        (2, 'DigFor'),
        (3, 'DigInc'),
        (4, 'DigSam'),
    )
    user_study = models.IntegerField(default=1, choices=STUDY, null=True, blank=True)
    allergy = models.TextField(blank=True)

    tool = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'User - {self.user_id}: {self.first_name} {self.last_name}'

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

    category = models.ForeignKey(Category, blank=True,
                                    null=True, default=None,
                                    on_delete=models.SET_NULL)

    sign_up = models.BooleanField(default=False)
    limit = models.IntegerField(default=0) 
    closed = models.BooleanField(default=False) # improve name?
    # just registered_users?
    registered_users_list = models.ManyToManyField(User, through='UserEvent', through_fields=('event', 'user'), blank=True, default=None) 

    def add_registration_list(self):
        self.signup = True  

    @property
    def expired(self):
        return self.start <= datetime.now(tz=timezone.utc)-timedelta(days=1)

    def __str__(self):
        return f'{self.title} - starting {self.start} at {self.location}'

class UserEvent(BaseModel):
    """
    UserEvent
        A RegistrationList can have 0 or many UserEvents. 
        UserId (your school id) and regListId have to be primary keys in the UserEvents.
    """
    user = models.ForeignKey(User, primary_key=True, on_delete=models.CASCADE) 
    event = models.ForeignKey(Event, on_delete=models.CASCADE) #-> event_id
    is_on_wait = models.BooleanField(default=False) # if event limit reached set this to true
    has_attended = models.BooleanField(default=False)

    def set_user_on_wait(self):
        # self.limit = self.event.limit is not 0 and self.event.registered_users_list > self.event.limit
        # self.save()
        pass

    def set_has_attended(self):
        # trenger annen logikk hvis bruker møtte opp og tok plassen til noen som 
        # ikke møtte opp
        # if event.expired() and not is_on_wait:
        #     self.has_attended = False
        pass

    def __str__(self):
        return f'{self.user.email} - is to attend {self.event} and is { "on the waitinglist" if self.is_on_wait else "on the list"}'
