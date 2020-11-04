from django.contrib import admin

from app.group import models

# from django.contrib.auth.models import Group as auth_group


admin.site.register(models.Group)
# admin.site.unregister(auth_group)
