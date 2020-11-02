from django.contrib import admin
from django.contrib.auth.models import Group

from app.group import models

admin.site.register(models.Group)
admin.site.unregister(Group)
