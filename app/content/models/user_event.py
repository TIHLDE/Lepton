from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
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

        if self.is_on_wait and self.event.has_priorities() and self.is_user_prioritized() \
                and self.event.is_full():
            self.swap_users()

        return super(UserEvent, self).save(*args, **kwargs)

    def is_user_prioritized(self):
        user_class = UserClass(int(self.user.user_class))
        user_study = UserStudy(int(self.user.user_study))

        return self.event.registration_priorities.filter(user_class=user_class, user_study=user_study).exists()

    def swap_users(self):
        """ Swaps a user with a spot with a prioritized user, if such user exists """
        event = self.event
        class_priorities = [int(priority.user_class.value) for priority in event.registration_priorities.all()]
        priorities = [(int(priority.user_class.value), int(priority.user_study.value))
                      for priority in event.registration_priorities.all()]
        other_user = None

        for user_event in UserEvent.objects.filter(event=event, is_on_wait=False):
            user = user_event.user
            if (user.user_class, user.user_study) in priorities:
                other_user = user_event


        # other_user = UserEvent.objects.filter(event=event) \
        #     .exclude(
        #     user__user_class__in=class_priorities,
        #     user__user_study__in=study_priorities,
        #     is_on_wait=True
        # ).first()

        print('--------\n', self, '\n Other:', other_user, '\n')
        if other_user is None:
            return

        other_user.is_on_wait = True
        other_user.save()

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
