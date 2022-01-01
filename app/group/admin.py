from django.contrib import admin

from app.group import models

admin.site.register(models.Group)
admin.site.register(models.Membership)
admin.site.register(models.MembershipHistory)
admin.site.register(models.Law)
admin.site.register(models.Fine)
