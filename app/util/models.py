from django.db import models

# Create your models here.
class Gridable(models.Model):
    """
    Abstract model representing a item which contains
    information required to place it in a grid.
    """
    height = models.IntegerField()
    width = models.IntegerField()
    order = models.IntegerField(unique=False) # Make unique?
    hide_on_mobile = models.BooleanField(default=False)

    class Meta:
        abstract = True

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True

class OptionalImage(models.Model):
    """Abstract model for models containing an image"""
    # Should the image file be stored on this server (ImageField),
    # or as an URL to another service?
    image = models.URLField(max_length=400, null=True, blank=True)
    image_alt = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        abstract = True

class OptionalAction(models.Model):
    """Abstract model for models with an action"""
    action = models.URLField(null=True, blank=True)
    action_text = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        abstract = True
