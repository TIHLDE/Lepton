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
        self.clean()
        return super(UserEvent, self).save(*args, **kwargs)

    def clean(self):
        """
        Is called when the instance is saved
        Determines whether user is on the waiting list or not when the instance is created.

        :raises ValidationError if the event is closed. If so, the UserEvent will not be created

        """
        event = self.event
        if event.closed:
            raise ValidationError({'detail': _('The queue for this event is closed')})
        if not self.user_event_id:
            self.is_on_wait = event.limit <= event.registered_users_list.all().count() and event.limit is not 0

    def __str__(self):
        return f'{self.user.email} - is to attend {self.event} and is ' \
               f'{"on the waiting list" if self.is_on_wait else "on the list"}'
