from django.db import models
from django.db import models

from datetime import datetime

class Jodel(models.Model):
    text = models.TextField()
    creation_time = models.DateTimeField()
    votes = models.IntegerField()

    # NOTE: Not currently implemented as it is not
    # clarified how this will be determined
    #voted = models.BooleanField() # has the current user upvoted this jodel

    def __str__(self):
        return "%s %d %s" % (self.text, self.votes, self.creation_time)
