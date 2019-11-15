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
        self.clean()
        return super(UserEvent, self).save(*args, **kwargs)

    def clean(self):
        """
        Validates models fields.
        Determines whether user is on the waiting list or not when the instance is created and if the user
        is allowed to be moved up from the waiting list.

        :raises ValidationError if the user is moved up from the waiting list and the event limit has been reached.
        :raises ValidationError if the event is closed upon creation. If so, the object will not be created

        """
        event = self.event
        is_limit_reached = event.limit <= event.registered_users_list.all().count() and event.limit is not 0

        # Object is being updated
        if self.user_event_id:
            if not self.is_on_wait and is_limit_reached:
                raise ValidationError('The queue for this event is full')
            return None

        # Object is being created
        self.is_on_wait = is_limit_reached

        if event.closed:
            raise ValidationError('The queue for this event is closed')

    def __str__(self):
        return f'{self.user.email} - is to attend {self.event} and is ' \
               f'{"on the waiting list" if self.is_on_wait else "on the list"}'
