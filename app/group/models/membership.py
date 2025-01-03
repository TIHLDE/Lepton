from django.db import models
from django.db.transaction import atomic

from app.common.enums import AdminGroup
from app.common.enums import NativeGroupType as GroupType
from app.common.enums import NativeMembershipType as MembershipType
from app.common.permissions import BasePermissionModel
from app.content.models.user import User
from app.group.models.group import Group
from app.util.models import BaseModel
from app.util.utils import now


class MembershipHistory(BaseModel):
    """Model for a Group Membership History"""

    write_access = AdminGroup.admin()

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="membership_histories"
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="membership_histories"
    )
    membership_type = models.CharField(
        max_length=50, choices=MembershipType.choices, default=MembershipType.MEMBER
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        ordering = ("-end_date", "-start_date")
        unique_together = ("user", "group", "end_date")
        verbose_name = "Membership History"
        verbose_name_plural = "Membership Histories"

    def __str__(self):
        return f"{self.user} - {self.group} - {self.membership_type} - {self.end_date}"

    @staticmethod
    def from_membership(membership):
        """Creates a Membership History object from a Membership object"""
        MembershipHistory.objects.create(
            user=membership.user,
            group=membership.group,
            membership_type=membership.membership_type,
            start_date=membership.created_at,
            end_date=now(),
        )

    @classmethod
    def has_read_permission(cls, request):
        return Membership.has_read_permission(request)

    @classmethod
    def has_write_permission(cls, request):
        return Membership.has_write_permission(request)

    def has_object_read_permission(self, request):
        return Membership.has_read_permission(request)

    def has_object_write_permission(self, request):
        return Membership.has_write_permission(request)


class Membership(BaseModel, BasePermissionModel):
    """Model for a Group Membership"""

    write_access = AdminGroup.admin()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="memberships"
    )
    membership_type = models.CharField(
        max_length=50, choices=MembershipType.choices, default=MembershipType.MEMBER
    )
    expiration_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "group")
        ordering = ["user__first_name", "user__last_name"]

    @classmethod
    def _check_request_user_is_leader(cls, request):
        assert request.id
        assert request.parser_context["kwargs"]["slug"]

        group_slug = request.parser_context["kwargs"]["slug"]
        return Membership.objects.get(
            user__user_id=request.id, group__slug=group_slug
        ).is_leader()

    @classmethod
    def has_read_permission(cls, request):
        return request.user is not None

    @classmethod
    def has_write_permission(cls, request):
        try:
            return cls._check_request_user_is_leader(
                request
            ) or super().has_write_permission(request)
        except (Membership.DoesNotExist, KeyError, AssertionError):
            return super().has_write_permission(request)

    def has_object_write_permission(self, request):
        return Membership.has_write_permission(request)

    def __str__(self):
        return f"{self.user} - {self.group} - {self.membership_type}"

    def is_leader(self):
        return self.membership_type == MembershipType.LEADER

    def is_board_member(self):
        return self.membership_type in MembershipType.board_members()

    def clean(self):
        if (
            self.membership_type == MembershipType.MEMBER
            and self.group.type == GroupType.SUBGROUP
        ):
            self.delete_hs_membership()

        if self.membership_type in MembershipType.board_members():
            self.swap_board()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Membership, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        MembershipHistory.from_membership(self)
        return super().delete(*args, **kwargs)

    @atomic
    def delete_hs_membership(self):
        seat_to_delete = (
            Membership.objects.select_for_update()
            .filter(group__slug=AdminGroup.HS, user=self.user)
            .first()
        )
        if seat_to_delete:
            seat_to_delete.delete()

    @atomic
    def swap_hs_seat(self, previous_seat):
        seat_to_delete = None
        if previous_seat:
            seat_to_delete = (
                Membership.objects.select_for_update()
                .filter(group__slug=AdminGroup.HS, user=previous_seat.user)
                .first()
            )

        if seat_to_delete:
            MembershipHistory.from_membership(membership=seat_to_delete)
            seat_to_delete.delete()
        group = Group.objects.filter(slug=AdminGroup.HS).first()

        if group and self:
            membership = Membership.objects.get_or_create(user=self.user, group=group)[
                0
            ]
            membership.save()

    @atomic
    def swap_board(self):
        previous_board_member = (
            Membership.objects.select_for_update()
            .filter(group=self.group, membership_type=self.membership_type)
            .first()
        )
        if previous_board_member and previous_board_member.user != self.user:
            MembershipHistory.from_membership(membership=previous_board_member)
            previous_board_member.membership_type = MembershipType.MEMBER
            previous_board_member.save()

        current_membership = (
            Membership.objects.select_for_update()
            .filter(group=self.group, user=self.user)
            .first()
        )
        if (
            current_membership
            and self.group.type == GroupType.SUBGROUP
            and self.membership_type == MembershipType.LEADER
        ):
            self.swap_hs_seat(previous_board_member)

        if current_membership:
            MembershipHistory.from_membership(membership=current_membership)
