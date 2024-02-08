from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from app.common.enums import AdminGroup, Groups, GroupType, MembershipType
from app.common.permissions import check_has_access
from app.util.models import BaseModel, OptionalImage
from app.util.utils import disable_for_loaddata, now


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, user_id, password, **extra_fields):
        user = self.model(user_id=user_id, **extra_fields)
        user.set_password(make_password(password))
        user.save(using=self._db)
        return user

    def create_staffuser(self, user_id, password):
        user = self.create_user(
            user_id=user_id,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, password):
        user = self.create_user(
            user_id=user_id,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


GENDER = (
    (1, "Mann"),
    (2, "Kvinne"),
    (3, "Annet"),
)


class User(AbstractBaseUser, PermissionsMixin, BaseModel, OptionalImage):
    write_access = AdminGroup.admin()
    read_access = [Groups.TIHLDE]

    user_id = models.CharField(max_length=15, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    email = models.EmailField(max_length=254)

    gender = models.IntegerField(default=2, choices=GENDER, null=True, blank=True)

    allergy = models.CharField(max_length=250, blank=True)

    public_event_registrations = models.BooleanField(default=True)

    tool = models.CharField(max_length=100, blank=True)

    slack_user_id = models.CharField(max_length=20, blank=True, default="")

    allows_photo_by_default = models.BooleanField(default=True)

    accepts_event_rules = models.BooleanField(default=False)

    USERNAME_FIELD = "user_id"
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = (
            "first_name",
            "last_name",
        )

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.user_id}"

    @property
    def is_TIHLDE_member(self):
        return self.memberships.filter(group__slug=Groups.TIHLDE).exists()

    @property
    def is_HS_or_Index_member(self):
        return self.memberships.filter(
            group__slug__in=[AdminGroup.HS, AdminGroup.INDEX]
        ).exists()

    @property
    def memberships_with_events_access(self):
        return self.memberships.filter(
            (
                Q(membership_type=MembershipType.LEADER)
                & (
                    Q(group__type=GroupType.COMMITTEE)
                    | Q(group__type=GroupType.INTERESTGROUP)
                )
            )
            | Q(group__type=GroupType.SUBGROUP)
            | Q(group__type=GroupType.BOARD)
        )

    @property
    def memberships_with_group_form_access(self):
        return self.memberships_with_events_access

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def number_of_strikes(self):
        return self.strikes.sum_active()

    @property
    def study(self):
        return self.memberships.filter(group__type=GroupType.STUDY).first()

    @property
    def studyyear(self):
        return self.memberships.filter(group__type=GroupType.STUDYYEAR).first()

    objects = UserManager()

    @property
    def forms(self):
        from app.forms.models.forms import Form

        return Form.objects.filter(submissions__user=self)

    def is_member_of(self, group):
        return self.memberships.filter(group=group).exists()

    def is_leader_of(self, group):
        return self.memberships.filter(
            group=group, membership_type=MembershipType.LEADER
        ).exists()

    def has_unanswered_evaluations(self):
        return self.get_unanswered_evaluations().exists()

    def has_unanswered_evaluations_for(self, event):
        return self.get_unanswered_evaluations().filter(event=event).exists()

    def get_unanswered_evaluations(self):
        from app.forms.models.forms import EventForm, EventFormType

        date_30_days_ago = now() - timedelta(days=30)
        registrations = self.registrations.filter(has_attended=True)
        return EventForm.objects.filter(
            event__registrations__in=registrations,
            type=EventFormType.EVALUATION,
            event__end_date__gte=date_30_days_ago,
        ).exclude(submissions__user=self)

    @classmethod
    def has_read_permission(cls, request):
        return check_has_access(
            cls.read_access,
            request,
        )
    
    @classmethod
    def has_retrieve_permission(cls, request):
        return check_has_access(
            cls.read_access,
            request,
        )

    @classmethod
    def has_write_permission(cls, request):
        return cls.has_write_permissions(cls, request)

    @classmethod
    def has_update_permission(cls, request):
        return cls.has_write_permissions(cls, request)

    @classmethod
    def has_destroy_permission(cls, request):
        return cls.has_write_permissions(cls, request)

    @classmethod
    def has_create_permission(cls, request):
        return True

    @classmethod
    def has_get_user_detail_strikes_permission(cls, request):
        return check_has_access(
            [AdminGroup.NOK, AdminGroup.INDEX, AdminGroup.HS, AdminGroup.SOSIALEN],
            request,
        )

    def has_object_write_permission(self, request):
        return self == request.user or check_has_access(
            self.write_access,
            request,
        )

    def has_object_retrieve_permission(self, request):
        return self == request.user or check_has_access(
            self.read_access,
            request,
        )

    def has_object_read_permission(self, request):
        return self.has_object_retrieve_permission(request)

    def has_write_permissions(self, request):
        if not request.user:
            return False
        user_id = request.parser_context.get("kwargs", {}).get("pk", None)
        if user_id == "me":
            return bool(request.user)
        if user_id:
            return request.user.user_id == user_id or check_has_access(
                self.write_access,
                request,
            )
        return check_has_access(
            self.write_access,
            request,
        )


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
@disable_for_loaddata
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Generate token at creation of user"""
    if created:
        Token.objects.create(user=instance)
