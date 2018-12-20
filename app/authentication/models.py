from app.util.models import BaseModel
from django.db import models

# This model defines the different 'undergrupper' and 'komitéer' i TIHLDE
class Group(BaseModel):

    name = models.CharField(max_length=200, null=False, blank=False, unique=True)

    # A shorter version of the name, and will be the name used in the permissions
    abbr = models.CharField(max_length=200, null=False, blank=False, unique=True)

    def __str__(self):
        return f"{self.name}"


# This model defines which member is conencted to which group ("undergruppe/komité")
class Connection(BaseModel):

    user_id = models.CharField(max_length=200)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user_id', 'group'),) # Instead of two primary-keys

    def __str__(self):
        return f'"{self.user_id}" is in "{self.group}"'

    



