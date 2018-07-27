from django.db import models

from app.util.models import BaseModel, GridItem

# Create your models here.



class News(BaseModel, GridItem):
    header = models.CharField(max_length=200)
    body = models.TextField()

class Event(BaseModel, GridItem):
    name = models.CharField(max_length=200)
    start = models.DateTimeField()
