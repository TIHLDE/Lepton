from django.db import models


class BookableItem(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
