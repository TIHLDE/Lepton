from django.core.exceptions import ValidationError
from django.db import models
from django.db.transaction import atomic

from enumchoicefield import EnumChoiceField

from app.common.enums import MembershipType
from app.content.models import User
from app.group.models import Group
from app.util.models import BaseModel
from app.util.utils import today


class MembershipHistory(BaseModel):
    """Model for a Group Membership History"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    membership_type = EnumChoiceField(MembershipType, default=MembershipType.MEMBER)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ("user", "group", "end_date")
        verbose_name = "Membership History"
        verbose_name_plural = "Membership Histories"

    def __str__(self):
        return f"{self.user} - {self.group} - {self.membership_type} - {self.end_date}"

    @staticmethod
    def from_membership(Membership):
        """Creates a Membership History object from a Membership object"""
        MembershipHistory.objects.create(
            user=Membership.user,
            group=Membership.group,
            membership_type=Membership.membership_type,
            start_date=Membership.created_at,
            end_date=today(),
        )


class Membership(BaseModel):
    """Model for a Group Membership"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    membership_type = EnumChoiceField(MembershipType, default=MembershipType.MEMBER)
    expiration_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "group")

    def __str__(self):
        return f"{self.user} - {self.group} - {self.membership_type}"

    @atomic
    def swap_leader(self):
        """Swaps leader of a group and creates a Membership History for each membership"""
        previous_leader = Membership.objects.select_for_update().get(
            group=self.group, membership_type=self.membership_type
        )
        if previous_leader.user == self.user:
            raise ValidationError("The user is the current leader")
        MembershipHistory.membership(Membership=previous_leader)
        previous_leader.membership_type = MembershipType.MEMBER
        previous_leader.save()
        MembershipHistory.from_membership(Membership=self)
        self.membership_type = MembershipType.LEADER
        self.save()
