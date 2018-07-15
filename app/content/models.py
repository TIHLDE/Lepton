from django.db import models

# Create your models here.


class Item(models.Model):
    '''
    Is a grid item
    '''
    height = models.IntegerField()
    width = models.IntegerField()

class News(Item):
    header = models.CharField(max_length=200)
    body = models.TextField()


class Event(Item):
    name = models.CharField(max_length=200)
    start = models.DateTimeField()

