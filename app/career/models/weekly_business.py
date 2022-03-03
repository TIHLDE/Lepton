import uuid

from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.util import now
from app.util.models import BaseModel, OptionalImage


class WeeklyBusiness(BaseModel, OptionalImage, BasePermissionModel):
    write_access = [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.NOK]

    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        default=uuid.uuid4,
        serialize=False,
    )

    business_name = models.CharField(max_length=200)
    body = models.TextField()

    year = models.PositiveSmallIntegerField()
    week = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("year", "week")
        verbose_name = "Weekly business"
        verbose_name_plural = "Weekly businesses"
        ordering = ["-year", "-week"]

    def __str__(self):
        return f"{self.business_name} - {self.year} - {self.week}"

    def save(self, *args, **kwargs):
        if self.week < 1 or self.week > 52:
            raise ValueError("Uke må være mellom 1 og 52")
        if self.year < now().year:
            raise ValueError("Ukens bedrift kan ikke opprettes i fortiden")
        try:
            if WeeklyBusiness.objects.get(week=self.week, year=self.year).id != self.id:
                raise ValueError("Finnes allerede en ukens bedrift for denne uken")
        except WeeklyBusiness.DoesNotExist:
            pass
        super().save(*args, **kwargs)
