from django.db import models
from django.core.exceptions import ValidationError

from app.util.models import BaseModel
from .user import User

class UserEvent(BaseModel):
    """ Model for user registration for an event """
    user_event_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    is_on_wait = models.BooleanField(default=False, verbose_name='waiting list')
    has_attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'event')
        verbose_name = "User event"
        verbose_name_plural = 'User events'

    def save(self, *args, **kwargs):
        if self.user_event_id:
            return self.create(*args, **kwargs)
        return self.update(*args, **kwargs)

    def create(self, *args, **kwargs):
        event = self.event
        is_limit_reached = event.limit <= event.registered_users_list.all().count() and event.limit is not 0
        self.is_on_wait = is_limit_reached

        if event.closed:
            raise ValidationError('The queue for this event is closed')

        return super(UserEvent, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        event = self.event
        is_limit_reached = event.limit <= event.registered_users_list.all().count() and event.limit is not 0

        if not self.is_on_wait and is_limit_reached:
            raise ValidationError('The queue for this event is full')

        allowed_attributes = {'is_on_wait', 'has_attended'}
        for name, value in kwargs.items():
            if name in allowed_attributes:
                self.name = value

        return super(UserEvent, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.email} - is to attend {self.event} and is ' \
               f'{"on the waiting list" if self.is_on_wait else "on the list"}'
