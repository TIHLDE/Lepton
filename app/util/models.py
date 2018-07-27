from django.db import models

# Create your models here.


class Gridable(models.Model):
    height = models.IntegerField()
    width = models.IntegerField()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)


class Content(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField() 

    text = models.TextField()

