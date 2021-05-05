from django.contrib import admin
#from django.contrib.auth.models import Group as auth_group

from app.group import models

admin.site.register(models.Group)
admin.site.register(models.Membership)
admin.site.register(models.MembershipHistory)
#admin.site.unregister(auth_group)
