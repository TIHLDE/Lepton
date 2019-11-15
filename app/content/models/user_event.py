from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

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
        """ Determines whether the object is being created or updated """
        if not self.user_event_id:
            return self.create(*args, **kwargs)
        return self.update(*args, **kwargs)

    def create(self, *args, **kwargs): 
        """
        Validates model fields upon creation.
        Determines whether user is on the waiting list or not when the instance is created
        :raises ValidationError if the event is closed. If so, the object will not be created
        """
        event = self.event
        is_limit_reached = event.limit <= event.registered_users_list.all().count() and event.limit is not 0
        self.is_on_wait = is_limit_reached

        if event.closed:
            raise ValidationError(_('is_on_wait: The queue for this event is closed'))

        return super(UserEvent, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        """
        Validates model fields upon update.
        Determines is if the user is allowed to be moved up from the waiting list.
        :raises ValidationError if the user is moved up from the waiting list and the event limit has been reached.
                If so, the object will not be updated.
        """
        event = self.event
        is_limit_reached = event.limit <= event.registered_users_list.all().count() and event.limit is not 0

        if not self.is_on_wait and is_limit_reached:
            raise ValidationError(_('is_on_wait: The queue for this event is full'))

        return super(UserEvent, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.email} - is to attend {self.event} and is ' \
               f'{"on the waiting list" if self.is_on_wait else "on the list"}'
