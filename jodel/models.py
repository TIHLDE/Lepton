from django.db import models
from django.utils import timezone


class AbstractJodelPost(models.Model):
    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    votes = models.IntegerField(default=0)

    @property
    def voteState(self):
        # TODO:
        return 0;

    def __str__(self):
        return "%s [votes %d] [created %s]" % (self.text, self.votes, self.time)

    class Meta:
        abstract = True

class Jodel(AbstractJodelPost):
    @property
    def comments(self):
        #return Comment.objects.filter(parent=self)
        return self.comment_set.all()
        #return Comment.objects.all()

class Comment(AbstractJodelPost):
    parent = models.ForeignKey('Jodel', related_name='comments', on_delete=models.CASCADE, null=False)

    def replies(self):
        return Comment.objects.filter(parent=self)