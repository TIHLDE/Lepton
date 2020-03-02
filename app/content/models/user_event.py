from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from app.util.utils import today
from app.util.models import BaseModel
from app.content.enums import UserClass, UserStudy
from .user import User


class UserEvent(BaseModel):
    """ Model for user registration for an event """
    user_event_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)

    is_on_wait = models.BooleanField(default=False, verbose_name='waiting list')
    has_attended = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Signed up on')

    class Meta:
        ordering = ('event', 'is_on_wait', 'created_at')
        unique_together = ('user', 'event')
        verbose_name = "User event"
        verbose_name_plural = 'User events'

    def __str__(self):
        return f'{self.user.email} - is to attend {self.event} and is ' \
               f'{"on the waiting list" if self.is_on_wait else "on the list"}'

    def save(self, *args, **kwargs):
        """ Determines whether the object is being created or updated and acts accordingly """
        if not self.user_event_id:
            return self.create(*args, **kwargs)

        return super(UserEvent, self).save(*args, **kwargs)

    def create(self, *args, **kwargs):
        """ Determines whether user is on the waiting list or not when the instance is created. """
        self.clean()

        self.is_on_wait = self.event.has_waiting_list()

        if self.should_be_swapped_with_not_prioritized_user():
            self.swap_users()

        return super(UserEvent, self).save(*args, **kwargs)

    def should_be_swapped_with_not_prioritized_user(self):
        return self.is_on_wait and self.is_prioritized() and self.event.has_priorities() and self.event.is_full()

    def is_prioritized(self):
        user_class = UserClass(int(self.user.user_class))
        user_study = UserStudy(int(self.user.user_study))

        return self.event.registration_priorities.filter(user_class=user_class, user_study=user_study).exists()

    def swap_users(self):
        """ Swaps a user with a spot with a prioritized user, if such user exists """
        for user_event in UserEvent.objects.filter(event=self.event, is_on_wait=False):
            if not user_event.is_prioritized():
                return self.swap_not_prioritized_user(user_event)

    def swap_not_prioritized_user(self, other_user_event):
        """ Puts own self on the list and other_user_event on wait """
        other_user_event.is_on_wait = True
        other_user_event.save()
        self.is_on_wait = False

    def clean(self):
        """
        Validates model fields. Is called upon instance save.

        :raises ValidationError if the event or queue is closed.
        """
        if self.event.closed:
            raise ValidationError(_('The queue for this event is closed'))
        if not self.event.sign_up:
            raise ValidationError(_('Sign up is not possible'))

        self.validate_start_and_end_registration_time()

    def validate_start_and_end_registration_time(self):
        self.check_registration_has_started()
        self.check_registration_has_ended()

    def check_registration_has_started(self):
        if self.event.start_registration_at > today():
            raise ValidationError(_('The registration for this event has not started yet.'))

    def check_registration_has_ended(self):
        if self.event.end_registration_at < today():
            raise ValidationError(_('The registration for this event has ended.'))
