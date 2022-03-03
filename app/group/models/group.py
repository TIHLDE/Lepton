from django.conf import settings
from django.db import models
from django.utils.text import slugify

from enumchoicefield import EnumChoiceField

from app.common.enums import AdminGroup, GroupType
from app.common.permissions import BasePermissionModel, set_user_id
from app.content.models.user import User
from app.util.models import BaseModel, OptionalImage


class Group(OptionalImage, BaseModel, BasePermissionModel):

    write_access = AdminGroup.admin()

    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, primary_key=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    contact_email = models.EmailField(max_length=200, null=True, blank=True)
    fine_info = models.TextField(default="", blank=True)
    type = EnumChoiceField(GroupType, default=GroupType.OTHER)
    fines_activated = models.BooleanField(default=False)
    members = models.ManyToManyField(
        User,
        through="Membership",
        through_fields=("group", "user"),
        blank=True,
        default=None,
        related_name="group_members",
        verbose_name="Group members",
    )
    members_history = models.ManyToManyField(
        User,
        through="MembershipHistory",
        through_fields=("group", "user"),
        blank=True,
        default=None,
        related_name="group_members_history",
        verbose_name="Group membership history",
    )
    fines_admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="fine_master_groups",
        null=True,
        blank=True,
        default=None,
    )

    class Meta:
        verbose_name_plural = "Groups"

    def __str__(self):
        return f"{self.name}"

    def notify_fines_admin(self):
        from app.communication.notifier import Notify
        from app.util.mail_creator import MailCreator

        description = [
            f"Hei! Lederen av {self.name} har gjort deg til botsjef i gruppen. I botsystemet i gruppen kan alle medlemmer melde inn bøter på en eller flere andre medlemmer. Gruppen kan selv velge hvor mye en bot er verdt og hvordan bøter skal godkjennes og betales.",
            "Som botsjef kan du, sammen med leder av gruppen, redigere lovverket og bøter (godkjenne, markere som betalt, endre antall og slette). Medlemmene kan ikke opprette bøter før det er minst én lov i lovverket. Du og alle medlemmene kan se en oversikt over alle bøter, samt filtrere på om boten er godkjent, betalt og per medlem.",
            "Lykke til!",
        ]
        Notify(
            [self.fines_admin], f"Du har blitt botsjef for gruppen {self.name}"
        ).send_email(
            MailCreator(f"Du har blitt botsjef for gruppen {self.name}")
            .add_paragraph(description[0])
            .add_paragraph(description[1])
            .add_paragraph(description[2])
            .add_button("Gå til gruppesiden", self.website_url)
            .generate_string()
        ).send_notification(
            description=" \n".join(description),
            link=f"/grupper/{self.slug}/boter/",
        )

    def check_fine_admin(self):
        return (
            self.fines_admin is not None
            and not Group.objects.filter(
                slug=self.slug, fines_admin=self.fines_admin
            ).exists()
        )

    def save(self, *args, **kwargs):
        if self.check_fine_admin():
            self.notify_fines_admin()
        if self.slug == "":
            self.slug = slugify(self.name)
        else:
            self.slug = slugify(self.slug)

        super().save(*args, **kwargs)

    @classmethod
    def check_context(cls, request):
        return request.parser_context.get("kwargs", {}).get("slug", None) is not None

    @property
    def website_url(self):
        return f"{settings.WEBSITE_URL}/grupper/{self.slug}/"

    @classmethod
    def check_request_user_is_leader(cls, request):
        if request.id is None:
            set_user_id(request)
        group_slug = request.parser_context["kwargs"]["slug"]
        group = cls.objects.get(slug=group_slug)
        membership = group.memberships.filter(
            group__slug=group_slug, user__user_id=request.id
        )
        return len(membership) == 1 and membership[0].is_leader()

    @classmethod
    def check_user_is_fine_master(cls, request):
        group = cls.get_group_from_permission_context(request)
        return (
            group.fines_admin
            and request.user
            and request.user.user_id == group.fines_admin.user_id
        )

    @classmethod
    def get_group_from_permission_context(cls, request):
        group_slug = request.parser_context["kwargs"]["slug"]
        return cls.objects.get(slug=group_slug)

    @classmethod
    def has_write_permission(cls, request):
        from app.group.models import Membership

        try:
            return cls.check_request_user_is_leader(
                request
            ) or super().has_write_permission(request)
        except (Membership.DoesNotExist, KeyError, AssertionError):
            return super().has_write_permission(request)

    def has_object_write_permission(self, request):
        from app.group.models import Membership

        if request.id is None:
            set_user_id(request)
        try:
            return self.memberships.get(
                group__slug=self.slug, user__user_id=request.id
            ).is_leader() or super().has_object_write_permission(request)
        except Membership.DoesNotExist:
            return super().has_object_write_permission(request)
