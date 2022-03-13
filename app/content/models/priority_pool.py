from django.db import models

from app.content.models import Event
from app.group.models import Group
from app.util.models import BaseModel


class PriorityPool(BaseModel):

    groups = models.ManyToManyField(Group, related_name="event_priority_pools")
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="priority_pools"
    )

    class Meta:
        verbose_name_plural = "Priority Pools"

    def __str__(self):
        return "Priority Pool: " + ", ".join(self.groups.values_list("name", flat=True))
