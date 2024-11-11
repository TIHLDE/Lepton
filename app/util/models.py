from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class OptionalImage(models.Model):
    """Abstract model for models containing an image"""

    image = models.URLField(max_length=600, null=True, blank=True)
    image_alt = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        abstract = True


class OptionalFile(models.Model):
    """Abstract model for models containing a file"""

    file = models.URLField(max_length=600, null=True, blank=True)

    class Meta:
        abstract = True
