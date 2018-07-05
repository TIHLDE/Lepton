from django.db import models
from django.db import models

class Jodel(models.Model):
    text = models.TextField()     # the contents of the jodel
    time = models.DateTimeField() # creation_date
    votes = models.IntegerField() # total number of posts

    # NOTE: Not currently implemented as it is not
    # clarified how this will be determined
    #voted = models.BooleanField() # has the current user upvoted this jodel
    
    def __str__(self):
        return "%s %d %s" % (self,text, self.votes, self.time)
