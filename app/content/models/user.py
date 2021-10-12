from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from app.common.enums import AdminGroup, Groups, MembershipType
from app.common.permissions import check_has_access
from app.content.models.strike import Strike
from app.util.models import BaseModel, OptionalImage
from app.util.utils import disable_for_loaddata


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, user_id, password):
        user = self.model(user_id=user_id,)
        user.set_password(make_password(password))
        user.save(using=self._db)
        return user

    def create_staffuser(self, user_id, password):
        user = self.create_user(user_id=user_id, password=password,)
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, password):
        user = self.create_user(user_id=user_id, password=password,)
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                has_active_strikes=models.Exists(
                    Strike.objects.active(user__user_id=models.OuterRef("user_id"))
                )
            )
        )


CLASS = (
    (-1, "Alumni"),
    (1, "1. Klasse"),
    (2, "2. Klasse"),
    (3, "3. Klasse"),
    (4, "4. Klasse"),
    (5, "5. Klasse"),
)

STUDY = (
    (1, "Dataing"),
    (2, "DigFor"),
    (3, "DigInc"),
    (4, "DigSam"),
    (5, "Drift"),
)

GENDER = (
    (1, "Mann"),
    (2, "Kvinne"),
    (3, "Annet"),
)


class User(AbstractBaseUser, PermissionsMixin, BaseModel, OptionalImage):
    has_access = [AdminGroup.HS, AdminGroup.INDEX]
    user_id = models.CharField(max_length=15, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    email = models.EmailField(max_length=254)
    cell = models.CharField(max_length=8, blank=True)

    gender = models.IntegerField(default=2, choices=GENDER, null=True, blank=True)

    user_class = models.IntegerField(default=1, choices=CLASS, null=True, blank=True)
    user_study = models.IntegerField(default=1, choices=STUDY, null=True, blank=True)
    allergy = models.CharField(max_length=250, blank=True)

    tool = models.CharField(max_length=100, blank=True)

    USERNAME_FIELD = "user_id"
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.user_id}"

    @property
    def is_TIHLDE_member(self):
        return self.memberships.filter(group__slug=Groups.TIHLDE).exists()

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def number_of_strikes(self):
        return self.strikes.sum_active()

    objects = UserManager()

    @property
    def forms(self):
        from app.forms.models.forms import Form

        return Form.objects.filter(submissions__user=self)

    def has_unanswered_evaluations(self):
        return self.get_unanswered_evaluations().exists()

    def has_unanswered_evaluations_for(self, event):
        return self.get_unanswered_evaluations().filter(event=event).exists()

    def get_unanswered_evaluations(self):
        from app.forms.models.forms import EventForm, EventFormType

        registrations = self.registrations.filter(has_attended=True)
        return EventForm.objects.filter(
            event__registrations__in=registrations, type=EventFormType.EVALUATION
        ).exclude(submissions__user=self)

    @classmethod
    def has_retrieve_permission(cls, request):
        if request.user:
            return request.id == request._user.user_id or check_has_access(
                cls.has_access, request,
            )
        return check_has_access(cls.has_access, request,)

    @classmethod
    def has_list_permission(cls, request):
        try:
            return check_has_access(cls.has_access, request) or len(
                request.user.memberships.filter(membership_type=MembershipType.LEADER)
            )
        except AttributeError:
            return check_has_access(cls.has_access, request)

    @staticmethod
    def has_read_permission(request):
        return User.has_list_permission(request) or User.has_retrieve_permission(
            request
        )

    @classmethod
    def has_write_permission(cls, request):
        return check_has_access(cls.has_access, request,)

    @classmethod
    def has_update_permission(cls, request):
        try:
            if request.user:
                return request.user.user_id == request.parser_context["kwargs"][
                    "pk"
                ] or check_has_access(cls.has_access, request,)
        except (AssertionError, KeyError):
            return check_has_access(cls.has_access, request,)

    @classmethod
    def has_create_permission(cls, request):
        return True

    def has_object_write_permission(self, request):
        if request.method == "DELETE":
            return check_has_access(self.has_access, request,)
        return self == request.user or check_has_access(self.has_access, request,)

    def has_object_retrieve_permission(self, request):
        return self == request.user or check_has_access(self.has_access, request,)

    def has_object_get_user_detail_strikes_permission(self, request):
        return check_has_access(
            [AdminGroup.NOK, AdminGroup.INDEX, AdminGroup.HS, AdminGroup.SOSIALEN],
            request,
        )


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
@disable_for_loaddata
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Generate token at creation of user"""
    if created:
        Token.objects.create(user=instance)
